"""Package008 T0/T1: immutable candidate diagnostics, no fitting or journal writer."""

from __future__ import annotations

import argparse
import csv
import json
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .config import digest, write_json
from .ft0_transforms import ORDER, identity
from .market_features import MarketMeasures
from .neural_engine import SharedLSTM
from .neural_health import g6_summary
from .neural_models import EndpointGatedLSTM, gate_diagnostics
from .peer_inputs import peer_summaries
from .pilot_postrun import summarize, target_array
from .pretraining_market import conditional_vector
from .pretraining_policy import CANDIDATE
from .pretraining_tables import target_moments, tg0
from .pretraining_transforms import raw_features
from .real_batch_authority import journal_rows_v2, load_plan
from .real_batch_data import load_batch_inputs
from .real_bridge_data import tensor_hash
from .real_bridge_run import rank_ic

GRADE = "ASSUMPTION_CONDITIONAL_RETROSPECTIVE_IDEAL_CLOCK_HOURLY_PROXY"
MODELS = ("TM0", "MC0", "MC1", "E5")
PAIRS = (
    ("TM0", "ZERO"),
    ("MC0", "TM0"),
    ("MC1", "MC0"),
    ("E5", "MC0"),
    ("E5", "TM0"),
    ("MC0", "RIDGE_MARKET_147"),
)


def read(path: Path) -> dict:
    return json.loads(path.read_text())


def csv_table(path: Path, rows: list[dict]) -> None:
    """New report only; absent values use NOT_RECORDED rather than fabricated zero."""
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("x", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, restval="NOT_RECORDED")
        writer.writeheader()
        writer.writerows(rows)


def legal_key(day: str, origin: int) -> None:
    if not "2020-07-01" <= day < "2024-01-01" or origin not in (1, 2):
        raise ValueError("DIAGNOSTIC_WF1_OR_EARLIER_ONLY_NO_CONFIRMATION")


def quantiles(values: np.ndarray) -> dict:
    a = np.asarray(values, dtype=float).reshape(-1)
    if not len(a) or not np.isfinite(a).all():
        raise ValueError("FINITE_NONEMPTY_DIAGNOSTIC_REQUIRED")
    return {str(q): float(np.quantile(a, q)) for q in (0, 0.01, 0.05, 0.5, 0.95, 0.99, 1)}


def session_concentration(days: list[str], origin_mse: np.ndarray) -> dict:
    """Mean origins per session, then top ceil(p*N) sessions; no stock-row ranking."""
    if len(days) != len(origin_mse) or not np.isfinite(origin_mse).all():
        raise ValueError("MATCHED_FINITE_SESSION_ERRORS_REQUIRED")
    losses = {
        d: float(np.mean([v for day, v in zip(days, origin_mse) if day == d]))
        for d in sorted(set(days))
    }
    ordered = sorted(losses.items(), key=lambda r: (-r[1], r[0]))
    total = sum(losses.values())
    return {
        "sessions": len(losses),
        "equal_day_MSE": float(np.mean(list(losses.values()))),
        "shares": {
            str(p): {
                "k": max(1, math.ceil(p * len(losses))),
                "share": sum(v for _, v in ordered[: max(1, math.ceil(p * len(losses)))]) / total
                if total
                else 0.0,
            }
            for p in (0.01, 0.05, 0.1)
        },
        "worst_sessions": ordered[:5],
    }


def pairwise_accuracy(scores: np.ndarray, target: np.ndarray) -> float:
    """Target ties omitted; a forecast tie receives half credit among ten pairs."""
    values = []
    for i in range(5):
        for j in range(i + 1, 5):
            a, b = float(scores[i] - scores[j]), float(target[i] - target[j])
            if b:
                values.append(0.5 if not a else float(a * b > 0))
    return float(np.mean(values)) if values else float("nan")


def rank_difference(a: np.ndarray, b: np.ndarray, target: np.ndarray) -> float | None:
    left, _ = rank_ic(tuple(a), tuple(target))
    right, _ = rank_ic(tuple(b), tuple(target))
    return left - right if left is not None and right is not None else None


def paired_blocks(
    values: np.ndarray,
    calendar_positions: np.ndarray,
    length: int,
    *,
    seed: int = 8008,
    samples: int = 5000,
) -> dict:
    """Exploratory moving blocks never bridge an omitted exchange session."""
    n = len(values)
    starts = [
        i for i in range(n - length + 1) if np.all(np.diff(calendar_positions[i : i + length]) == 1)
    ]
    if not starts:
        return {"status": "NO_CONTIGUOUS_BLOCKS"}
    rng = np.random.default_rng(seed)
    chosen = rng.choice(starts, (samples, math.ceil(n / length)))
    indices = (chosen[:, :, None] + np.arange(length)).reshape(samples, -1)[:, :n]
    means = values[indices].mean(axis=1)
    return {
        "status": "EXPLORATORY_NOT_FULL_G8",
        "block_sessions": length,
        "eligible_starts": len(starts),
        "samples": samples,
        "seed": seed,
        "percentile95": np.quantile(means, [0.025, 0.975]).tolist(),
        "limitations": "Post-screen one seed/fold; no selection adjustment or HAC. "
        "Blocks obey exchange chronology; blocks cross only at resample joins.",
    }


def safe_model(path: Path, manifest: dict, contract: dict, pair_key: str):
    """Verify bytes, preparation, stage and contract before safe frozen-weight inference."""
    if digest(path) != manifest["sha256"]:
        raise ValueError("DIAGNOSTIC_CHECKPOINT_HASH_MISMATCH")
    obj = torch.load(path, map_location="cpu", weights_only=True)
    if (
        obj["contract"] != contract
        or obj["pair_key"] != pair_key
        or obj["preparation_id"] != manifest["preparation_id"]
        or obj["stage"] != manifest["stage"]
        or obj["epoch"] != manifest["epoch"]
    ):
        raise ValueError("DIAGNOSTIC_CHECKPOINT_IDENTITY_MISMATCH")
    model = (
        EndpointGatedLSTM()
        if contract["architecture"] == "MC1"
        else SharedLSTM(contract["channels"])
    )
    model.load_state_dict(obj["model"], strict=True)
    if sum(p.numel() for p in model.parameters()) != contract["parameters"]:
        raise ValueError("DIAGNOSTIC_CHECKPOINT_PARAMETER_COUNT_MISMATCH")
    if not all(bool(torch.isfinite(p).all()) for p in model.parameters()):
        raise ValueError("NONFINITE_FROZEN_WEIGHTS")
    return model.eval().requires_grad_(False)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--previous", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out, previous = args.output, args.previous
    started = time.monotonic()
    torch.set_num_threads(1)
    if not out.is_dir() or (out / "diagnostic_summary.json").exists():
        raise ValueError("NEW_PREFLIGHT_PACKET_REQUIRED")
    plan_path = previous / "batch_plan.json"
    plan, review = load_plan(Path.cwd(), {"path": str(plan_path), "sha256": digest(plan_path)})
    binding = read(Path(plan["dataset"]["path"]))
    inputs = load_batch_inputs(review, binding)
    views = {k: inputs.stock_view(k) for k in ("inner", "validation", "refit", "WF1")}
    feature_rows = []
    for partition in ("refit", "WF1"):
        values = views[partition].values.numpy()
        for j, channel in enumerate(ORDER):
            vector = values[:, j]
            feature_rows.append(
                {
                    "partition": partition,
                    "channel": channel,
                    "unique_input_rows_including_lookback_context": len(vector),
                    "quantiles": json.dumps(quantiles(vector)),
                    "abs_gt10_share": float(np.mean(np.abs(vector) > 10)),
                    "abs_gt100_share": float(np.mean(np.abs(vector) > 100)),
                    "grade": GRADE,
                }
            )
    csv_table(out / "input_channel_distribution.csv", feature_rows)
    market_view = inputs.view("WF1", 21)
    keys = [(r.session, r.origin) for r in views["WF1"].rows]
    if len(keys) != 232 or len(views["WF1"].sessions) != 116 or len(set(keys)) != 232:
        raise ValueError("EXPECTED_MATCHED_WF1_KEYS_REQUIRED")
    for key in keys:
        legal_key(*key)
    # Freeze error-blind temporal and market-state representatives before reading any scores.
    days = views["WF1"].sessions
    representative = [
        (days[round(q * (len(days) - 1))], o) for q in (0, 0.25, 0.5, 0.75, 1) for o in (1, 2)
    ]
    endpoints = np.asarray(
        [market_view.market[idx[-1]].numpy() for _, idx in market_view.market_indices]
    )
    for index in (int(np.argmin(endpoints[:, 1])), int(np.argmax(endpoints[:, 1]))):
        if keys[index] not in representative:
            representative.append(keys[index])
    write_json(
        out / "representative_keys.json",
        {
            "selection": "ERROR_BLIND_FROZEN_BEFORE_SCORE_FILES_READ",
            "rule": "Both origins at first/quarter/mid/three-quarter/last eligible sessions "
            "+ endpoint standardized U2 minimum/maximum origins, deduplicated; all five stocks",
            "keys": representative,
            "outcomes_or_model_errors_used": False,
            "stock_order": list(CANDIDATE),
            "grades": GRADE,
        },
    )
    load_seconds = time.monotonic() - started
    snapshot = pd.read_csv(plan["baseline_snapshot"]["path"], float_precision="round_trip")
    wf = snapshot.loc[snapshot.partition == "WF1"]
    expected = [(d, o, s) for d, o in keys for s in CANDIDATE]
    if list(zip(wf.session, wf.origin, wf.symbol)) != expected:
        raise ValueError("BASELINE_ONE_TO_ONE_KEYS_REQUIRED")
    y = target_array(views["WF1"]).astype(float)
    if not np.array_equal(y, wf.TG0.to_numpy().reshape(-1, 5)):
        raise ValueError("BASELINE_TARGET_MISMATCH")
    scores = {
        "TM0": wf.TM0.to_numpy().reshape(-1, 5),
        "ZERO": np.zeros_like(y),
        "M1": wf.M1.to_numpy().reshape(-1, 5),
        "RIDGE_OWN_112": wf.RIDGE_OWN_112.to_numpy().reshape(-1, 5),
    }
    results = {"TM0": read(Path(plan["tm0_result"]["path"]))}
    folders = {"TM0": Path(plan["tm0_result"]["path"]).parent}
    for name in MODELS[1:]:
        folders[name] = previous / name
        results[name] = read(folders[name] / f"seed42_{name.lower()}_pair_result.json")
        descriptor = next(r for r in plan["runs"] if r["architecture"] == name)
        if (
            results[name]["contract"] != descriptor["contract"]
            or results[name]["input_id"] != descriptor["input_id"]
        ):
            raise ValueError("HISTORICAL_RUN_CONTRACT_OR_INPUT_MISMATCH")
        records = results[name]["development"]["origin_records"]
        if [(r["session"], r["origin"]) for r in records] != keys:
            raise ValueError("MODEL_KEY_MISMATCH")
        if not np.array_equal(y, np.asarray([r["targets"] for r in records])):
            raise ValueError("MODEL_TARGET_MISMATCH")
        scores[name] = np.asarray([r["scores"] for r in records])
    ridge = read(previous / "RIDGE_MARKET_147/result.json")
    if [tuple(k) for k in ridge["origin_keys"]] != keys:
        raise ValueError("RIDGE_KEY_MISMATCH")
    scores["RIDGE_MARKET_147"] = np.asarray(ridge["scores"])
    metrics = {name: summarize(views["WF1"], score) for name, score in scores.items()}
    prior = {
        r["model"]: r
        for r in csv.DictReader((previous / "matched_wf1_model_comparison.csv").open())
    }
    for name, m in metrics.items():
        if (
            abs(m["MSE"] - float(prior[name]["MSE"])) > 1e-12
            or abs(m["daily_Rank_IC"] - float(prior[name]["daily_Rank_IC"])) > 1e-12
        ):
            raise ValueError("FROZEN_WF1_METRIC_MISMATCH")
    # Saved dropout-on telemetry only. Never label a final-weight eval replay training.
    epoch_rows, health, losses, associations = [], {}, [], {}
    for name in MODELS:
        result, folder = results[name], folders[name]
        cal = [read(p) for p in sorted(folder.glob("calibration_epoch_*.json"))]
        refit = [read(p) for p in sorted(folder.glob("refit_epoch_*.json"))]
        h = g6_summary(
            tuple(r["training"] for r in cal),
            tuple(refit),
            result["development"]["score_std"],
            result["selector"]["status"],
        )
        health[name] = {
            **h,
            "selector": result["selector"],
            "calibration_epochs": len(cal),
            "refit_epochs": len(refit),
            "historical_G6": result["G6"],
        }
        for phase, records in (
            ("CALIBRATION_DROPOUT_ON", [r["training"] for r in cal]),
            ("FRESH_REFIT_DROPOUT_ON", refit),
        ):
            for i, r in enumerate(records):
                g = r.get("gradients") or {}
                epoch_rows.append(
                    {
                        "model": name,
                        "pass": phase,
                        "epoch": r["epoch"],
                        "train_MSE": r["mse"],
                        "train_score_std_dropout_on": r.get("score_std", "NOT_RECORDED"),
                        "validation_score_std_eval": cal[i]["validation"].get(
                            "score_std", "NOT_RECORDED"
                        )
                        if phase.startswith("CAL")
                        else "NOT_RECORDED",
                        "inner_validation_MSE": cal[i]["validation"]["mse"]
                        if phase.startswith("CAL")
                        else "NOT_RECORDED",
                        "updates": r["steps"],
                        "selected_epoch": result["selector"]["selected"],
                        "gradient_missing": not bool(g),
                        **g,
                        "G6": h["status"],
                        "selected_checkpoint_sha": result["selected_checkpoint"]["sha256"],
                        "grade": GRADE,
                    }
                )
        c = np.asarray(
            [
                [
                    r["training"]["gradients"]["median"],
                    r["training"]["gradients"]["clipped_fraction"],
                    r["training"]["mse"],
                    r["validation"]["mse"],
                    r["training"]["score_std"],
                    r["validation"]["score_std"],
                ]
                for r in cal
            ]
        )
        associations[name] = {
            "columns": [
                "norm_median",
                "clipped_fraction",
                "train_MSE",
                "inner_MSE",
                "train_score_std_dropout_on",
                "validation_score_std_eval",
            ],
            "epoch_Pearson_descriptive": np.corrcoef(c.T).tolist(),
            "selected_validation": result["selector"]["best"],
            "last_validation": cal[-1]["validation"]["mse"],
            "validation_last_minus_selected": cal[-1]["validation"]["mse"]
            - result["selector"]["best"],
            "historical_batch_loss_gradient_link": (
                "CLIPPING_CAUSE_NOT_IDENTIFIABLE_FROM_SAVED_BATCH_LOGS"
            ),
        }
        for partition in ("validation", "refit", "WF1"):
            if name == "TM0":
                s = snapshot.loc[snapshot.partition == partition]
                error = (s.TM0.to_numpy() - s.TG0.to_numpy()) ** 2
                group = (
                    pd.DataFrame({"session": s.session, "origin": s.origin, "error": error})
                    .groupby(["session", "origin"])
                    .error.mean()
                )
                d, e = [k[0] for k in group.index], group.to_numpy()
            else:
                rec = (
                    cal[result["selector"]["selected"] - 1]["validation"]["origin_records"]
                    if partition == "validation"
                    else result[
                        "refit_train_evaluation" if partition == "refit" else "development"
                    ]["origin_records"]
                )
                d = [r["session"] for r in rec]
                e = np.asarray(
                    [
                        np.mean((np.asarray(r["scores"]) - np.asarray(r["targets"])) ** 2)
                        for r in rec
                    ]
                )
            conc = session_concentration(d, e)
            for p, v in conc["shares"].items():
                losses.append(
                    {
                        "model": name,
                        "partition": partition,
                        "mode": "SELECTED_CALIBRATION_EVAL"
                        if partition == "validation"
                        else "FINAL_REFIT_EVAL",
                        "top_fraction": p,
                        **v,
                        "sessions": conc["sessions"],
                        "MSE": conc["equal_day_MSE"],
                        "grade": GRADE,
                    }
                )
    csv_table(out / "g6_four_model_epochs.csv", epoch_rows)
    csv_table(out / "loss_concentration.csv", losses)
    write_json(out / "epoch_associations.json", associations)
    write_json(out / "g6_summary.json", health)
    # Reuse the exact raw-return -> median/unscaled MAD -> existing epsilon target code.
    tails, details = [], {}
    for partition, view in views.items():
        recipe = inputs.candidates[
            "WF1_INNER_TRAIN" if partition in ("inner", "validation") else "WF1_REFIT"
        ].preparation
        decomposed = []
        for row in view.rows:
            panel = inputs.base.panels[row.session, row.origin]
            returns = tuple(v for v in panel.returns if v is not None)
            center, mad = target_moments(returns)
            target = np.asarray(tg0(returns, recipe.target_epsilon))
            if not np.array_equal(
                target.astype(np.float32), np.asarray(row.targets, dtype=np.float32)
            ):
                raise ValueError("CANONICAL_TG0_DECOMPOSITION_MISMATCH")
            decomposed.append(
                {
                    "session": row.session,
                    "origin": row.origin,
                    "returns": returns,
                    "median": center,
                    "MAD": mad,
                    "epsilon": recipe.target_epsilon,
                    "denominator": mad + recipe.target_epsilon,
                    "TG0": target.tolist(),
                }
            )
        details[partition] = decomposed
        data = np.asarray([r["TG0"] for r in decomposed])
        raw = np.asarray([r["returns"] for r in decomposed])
        mad = np.asarray([r["MAD"] for r in decomposed])
        e = recipe.target_epsilon
        tails.append(
            {
                "partition": partition,
                "origins": len(data),
                "sessions": len(view.sessions),
                "epsilon": e,
                "zero_MAD_origins": int(np.sum(mad == 0)),
                "floor_ge_MAD_origins": int(np.sum(mad <= e)),
                "MAD_lt_epsilon_div10": int(np.sum(mad < e / 10)),
                "abs_TG0_gt10_rows": int(np.sum(np.abs(data) > 10)),
                "abs_TG0_gt20_rows": int(np.sum(np.abs(data) > 20)),
                "raw_log_return_quantiles": json.dumps(quantiles(raw)),
                "MAD_quantiles": json.dumps(quantiles(mad)),
                "TG0_signed_quantiles": json.dumps(quantiles(data)),
                "grade": GRADE,
            }
        )
        for j, symbol in enumerate(CANDIDATE):
            tails.append(
                {
                    "partition": partition,
                    "stock": symbol,
                    "TG0_signed_quantiles": json.dumps(quantiles(data[:, j])),
                    "grade": GRADE,
                }
            )
        for label, groups in (
            ("origin", [str(r.origin) for r in view.rows]),
            ("month", [r.session[:7] for r in view.rows]),
        ):
            for group in sorted(set(groups)):
                mask = np.asarray([v == group for v in groups], dtype=np.bool_)
                tails.append(
                    {
                        "partition": partition,
                        label: group,
                        "origins": int(mask.sum()),
                        "TG0_signed_quantiles": json.dumps(quantiles(data[mask])),
                        "floor_ge_MAD_origins": int(np.sum(mad[mask] <= e)),
                        "grade": GRADE,
                    }
                )
    csv_table(out / "tg0_denominator_and_tail_audit.csv", tails)
    # Aggregated diagnostics only; no full target/feature dataset is persisted.
    severe = sorted(details["WF1"], key=lambda r: -max(abs(v) for v in r["TG0"]))[:3]
    mse_daily = np.asarray([r["MSE"] for r in metrics["TM0"]["daily"]])
    worst_days = [days[i] for i in np.argsort(-mse_daily)[:3]]
    rank0 = pd.DataFrame(scores["MC0"]).rank(axis=1, method="average").to_numpy()
    rank1 = pd.DataFrame(scores["MC1"]).rank(axis=1, method="average").to_numpy()
    different = np.any(rank0 != rank1, axis=1)
    anomaly = {
        "designation": "POST_HOC_DIAGNOSTIC_NOT_REPRESENTATIVE",
        "extreme_TG0": [(r["session"], r["origin"]) for r in severe],
        "high_loss_TM0_sessions": [(d, 1) for d in worst_days],
        "MC0_MC1_rank_disagreement": [keys[i] for i in np.flatnonzero(different)[:3]],
        "MC0_MC1_rank_equality": [keys[i] for i in np.flatnonzero(~different)[:3]],
    }
    for label, column in (("market_state_extreme", 1),):
        anomaly[label] = [
            keys[int(np.argmin(endpoints[:, column]))],
            keys[int(np.argmax(endpoints[:, column]))],
        ]
    write_json(out / "posthoc_anomaly_keys.json", anomaly)
    write_json(
        out / "severe_target_examples.json",
        {
            "designation": "POST_HOC_DIAGNOSTIC",
            "WF1": severe,
            "refit": sorted(details["refit"], key=lambda r: -max(abs(v) for v in r["TG0"]))[:5],
        },
    )
    daily_rows, origin_rows, stock_rows, contrast_rows = [], [], [], []
    for i, day in enumerate(days):
        r = {"session": day, "origins": 2, "grade": GRADE}
        for name, m in metrics.items():
            r.update({name + "_MSE": m["daily"][i]["MSE"], name + "_IC": m["daily"][i]["IC"]})
        daily_rows.append(r)
    daily = pd.DataFrame(daily_rows)
    calendar_lookup = {d: i for i, d in enumerate(inputs.base.history.calendar.days)}
    positions = np.asarray([calendar_lookup[d] for d in days])
    for a, b in PAIRS:
        contrast = a + "-" + b
        for metric in ("MSE", "IC"):
            delta = daily[a + "_" + metric].to_numpy() - daily[b + "_" + metric].to_numpy()
            daily[contrast + "_delta_" + metric] = delta
            contrast_rows.append(
                {
                    "contrast": contrast,
                    "metric": metric,
                    "days": len(delta),
                    "mean": float(delta.mean()),
                    "median": float(np.median(delta)),
                    "positive_day_share": float(np.mean(delta > 1e-12)),
                    "negative_day_share": float(np.mean(delta < -1e-12)),
                    "zero_day_share_atol1e12": float(np.mean(np.abs(delta) <= 1e-12)),
                    "quantiles": quantiles(delta),
                    "grade": GRADE,
                    "uncertainty": [paired_blocks(delta, positions, n) for n in (5, 10, 20)],
                }
            )
    csv_table(out / "matched_wf1_daily_model_comparison.csv", daily.to_dict("records"))
    delta_columns = [c for c in daily.columns if "_delta_" in c]
    monthly_delta = daily.assign(month=daily.session.str[:7]).groupby("month")[delta_columns].mean()
    csv_table(out / "monthly_paired_deltas.csv", monthly_delta.reset_index().to_dict("records"))
    write_json(
        out / "paired_contrasts_and_exploratory_uncertainty.json",
        {
            "signs": "A-B; lower delta_MSE better; higher delta_IC better",
            "contrasts": contrast_rows,
        },
    )
    monthly = []
    for name, m in metrics.items():
        for month, values in m["monthly"].items():
            monthly.append({"model": name, "month": month, **values, "grade": GRADE})
        for origin, values in m["by_origin"].items():
            mask = np.asarray([r.origin == int(origin) for r in views["WF1"].rows], dtype=bool)
            cohort = scores[name][mask]
            origin_rows.append(
                {
                    "model": name,
                    "origin": origin,
                    **values,
                    "grade": GRADE,
                    "score_mean": float(cohort.mean()),
                    "score_std": float(cohort.std()),
                    "score_min": float(cohort.min()),
                    "score_max": float(cohort.max()),
                }
            )
        for j, symbol in enumerate(CANDIDATE):
            a = scores[name][:, j]
            residual = a - y[:, j]
            stock_rows.append(
                {
                    "model": name,
                    "symbol": symbol,
                    "mean": float(a.mean()),
                    "std": float(a.std()),
                    "min": float(a.min()),
                    "max": float(a.max()),
                    "residual_mean": float(residual.mean()),
                    "residual_std": float(residual.std()),
                    "MSE": float(np.mean(residual**2)),
                    "grade": GRADE,
                }
            )
    csv_table(out / "monthly_model_diagnostics.csv", monthly)
    csv_table(out / "origin_model_diagnostics.csv", origin_rows)
    csv_table(out / "stock_score_residual_diagnostics.csv", stock_rows)
    score_health = {
        name: {
            "pooled_MSE": float(np.mean((score - y) ** 2)),
            "equal_day_MSE": metrics[name]["MSE"],
            "cross_sectional_SD": quantiles(np.std(score, axis=1)),
            "pairwise_accuracy": float(
                np.nanmean([pairwise_accuracy(a, b) for a, b in zip(score, y)])
            ),
            "tied_origins": metrics[name]["tied_score_origins"],
            "constant_origins": metrics[name]["constant_forecast_origins"],
        }
        for name, score in scores.items()
    }
    dIC = daily["MC1_IC"] - daily["MC0_IC"]
    equivalence = {
        "exact_score_equal_origins": int(np.all(scores["MC0"] == scores["MC1"], axis=1).sum()),
        "literal_rank_equal_origins": int((~different).sum()),
        "rank_different_origins": int(different.sum()),
        "max_abs_score_difference": float(np.max(np.abs(scores["MC0"] - scores["MC1"]))),
        "daily_IC_positive": int((dIC > 1e-12).sum()),
        "daily_IC_negative": int((dIC < -1e-12).sum()),
        "daily_IC_equal_atol1e12": int((abs(dIC) <= 1e-12).sum()),
        "mean_delta_IC": float(dIC.mean()),
    }
    write_json(out / "score_health.json", {"models": score_health, "MC0_MC1": equivalence})
    # Representative and anomaly sample only: source boundaries, transforms, hidden/output.
    trace_keys = list(
        dict.fromkeys(
            representative
            + [tuple(k) for label, ks in anomaly.items() if label != "designation" for k in ks]
        )
    )
    models = {
        name: safe_model(
            folders[name] / "refit_final.pt",
            results[name]["final_checkpoint"],
            results[name]["contract"],
            results[name]["pair_key"],
        )
        for name in MODELS
    }
    state_hashes = {
        name: identity({k: v.tolist() for k, v in model.state_dict().items()})
        for name, model in models.items()
    }
    replays, gates, counterfactuals = [], [], []
    market_measures = {pd.Timestamp(r["timestamp"]): r for r in inputs.market_store["measures"]}
    for day, origin in trace_keys:
        legal_key(day, origin)
        index = keys.index((day, origin))
        pos = views["WF1"].sessions.index(day)
        sample = {
            16: views["WF1"].batch((pos,)).inputs[0, origin - 1],
            21: inputs.view("WF1", 21).batch((pos,)).inputs[0, origin - 1],
            23: inputs.view("WF1", 23).batch((pos,)).inputs[0, origin - 1],
        }
        if not torch.equal(sample[16], sample[21][..., :16]) or not torch.equal(
            sample[21], sample[23][..., :21]
        ):
            raise ValueError("REPLAY_ARCHITECTURE_INPUT_PREFIX_MISMATCH")
        peer = torch.tensor(peer_summaries(sample[16].numpy()), dtype=torch.float32)
        if not torch.equal(peer, sample[23][..., 21:]):
            raise ValueError("PEER_REPLAY_MISMATCH")
        for j in range(5):
            other = sample[16][[k for k in range(5) if k != j], :, 0].double().numpy()
            oracle = np.stack((other.mean(0), other.std(0, ddof=0)), axis=-1).astype(np.float32)
            if not np.array_equal(oracle, peer[j].numpy()):
                raise ValueError("INDEPENDENT_FOUR_PEER_ORACLE_MISMATCH")
        panel = inputs.base.panels[day, origin]
        end_pos = inputs.base.origin_steps[day, origin][-1]
        step = inputs.base.history.calendar.steps[end_pos]
        prep = inputs.candidates["WF1_REFIT"].preparation
        component = inputs.base.components[CANDIDATE[0], day, step.slot]
        raw, flags = raw_features(inputs.base, CANDIDATE[0], end_pos, origin, prep.floors[0])
        scaled_endpoint = prep.scaler.apply(tuple(v for v in raw if v is not None))
        if not np.array_equal(
            np.asarray(scaled_endpoint, dtype=np.float32), sample[16][0, -1].numpy()
        ):
            raise ValueError("ENDPOINT_RAW_TO_FITTED_SCALER_REPLAY_MISMATCH")
        measure = dict(market_measures[step.end])
        measure["timestamp"] = step.end
        measure["evidence_ids"] = tuple(measure["evidence_ids"])
        recipe = inputs.market_store["preparations"]["WF1_REFIT"]
        raw_market = conditional_vector(
            MarketMeasures(**measure), recipe["hourly_floor"], recipe["daily_floor"]
        )
        trace = {
            "key": [day, origin],
            "selection": "REPRESENTATIVE"
            if (day, origin) in representative
            else "POST_HOC_DIAGNOSTIC",
            "B0": {
                "component_store": review.manifest["canonical_store"],
                "source_binding": inputs.base.history.binding,
                "action_binding": inputs.base.history.action_binding,
                "component_lineage": component.lineage_id,
                "endpoint_source_ids": component.source_ids,
                "price_reference_ids": panel.reference_ids,
                "retrospective_entry_close": panel.entry_prices,
                "retrospective_exit_close": panel.exit_prices,
                "unadjusted_OHLC_action_vintage": "NOT_RECORDED_IN_COMPONENT_STORE_NOT_CERTIFIED",
            },
            "B1": {
                "own_step_end": str(step.end),
                "cutoff": str(panel.cutoff),
                "issuance": str(panel.issuance),
                "nominal_entry_event": str(panel.entry_event),
                "nominal_exit_event": str(panel.exit_event),
                "maturity": str(panel.maturity),
                "actual_publication": "UNKNOWN",
                "available_at": "IDEALIZED_PERIOD_END_ASSUMPTION",
                "window_first": str(inputs.base.history.calendar.steps[end_pos - 47].end),
                "market_valid_steps": sum(
                    v >= 0
                    for _, idx in market_view.market_indices
                    if _ == (day, origin)
                    for v in idx
                ),
            },
            "B2": next(r for r in details["WF1"] if (r["session"], r["origin"]) == (day, origin)),
            "B3": {
                "preparation_id": prep.preparation_id,
                "stock_order": list(CANDIDATE),
                "channel_order": list(ORDER),
                "AAPL_endpoint_prescaled": raw,
                "scaler_centers": prep.scaler.centers,
                "scaler_scales": prep.scaler.scales,
                "scaler_methods": prep.scaler.methods,
                "scaler_channel_note": "13 fitted channels; B2/T2/T5 native bounded passthrough",
                "flags": flags,
                "market_recipe_id": market_view.recipe_id,
                "raw_market_U1_U5": raw_market,
                "endpoint_scaled_market": endpoints[index].tolist(),
                "tensors": {
                    str(d): {
                        "shape": list(x.shape),
                        "sha256": tensor_hash(x),
                        "endpoint_AAPL": x[0, -1].tolist(),
                        "absolute_max": float(x.abs().max()),
                    }
                    for d, x in sample.items()
                },
                "peer_endpoint_by_stock": peer[:, -1].tolist(),
                "four_peer_oracle": True,
            },
            "B4_B5": {},
        }
        for name, model in models.items():
            x = sample[results[name]["contract"]["channels"]]
            with torch.inference_mode():
                if isinstance(model, EndpointGatedLSTM):
                    transformed, alpha = model.compose(x)
                    hidden = model.core.encode(transformed)
                    gate = gate_diagnostics(alpha)
                    gates.append(alpha[0].numpy())
                    gate["weights"] = alpha[0].tolist()
                else:
                    hidden = model.encode(x)
                    gate = None
                prediction = model(x).numpy()
            max_error = float(np.max(np.abs(prediction - scores[name][index])))
            if max_error > 2e-6:
                raise ValueError("REPRODUCIBILITY_DEFECT_FROZEN_CHECKPOINT_FORWARD")
            trace["B4_B5"][name] = {
                "checkpoint_sha": results[name]["final_checkpoint"]["sha256"],
                "eval_dropout_off": True,
                "max_abs_stored_prediction_difference": max_error,
                "hidden_norm_by_stock": hidden.norm(dim=1).tolist(),
                "hidden_cross_stock_SD_mean": float(hidden.std(0, unbiased=False).mean()),
                "scores": prediction.tolist(),
                "midranks": pd.Series(prediction).rank().tolist(),
                "residuals": (prediction - y[index]).tolist(),
                "gate": gate,
            }
        if (day, origin) in representative[:3]:
            with torch.inference_mode():
                x = sample[23].clone()
                x[..., 21:] = 0
                e5_delta = (models["E5"](x) - models["E5"](sample[23])).tolist()
                z = sample[21].clone()
                z[..., 16:] = 0
                mc_delta = (models["MC0"](z) - models["MC0"](sample[21])).tolist()
            counterfactuals.append(
                {
                    "key": [day, origin],
                    "designation": "DIAGNOSTIC_COUNTERFACTUAL_NOT_OBSERVED",
                    "E5_zero_peer_channel_score_change": e5_delta,
                    "MC0_zero_market_channel_score_change": mc_delta,
                    "historical_metric_or_selection_use": False,
                }
            )
        replays.append(trace)
    assert all(
        state_hashes[name] == identity({k: v.tolist() for k, v in model.state_dict().items()})
        for name, model in models.items()
    )
    write_json(
        out / "boundary_replay_compact.json",
        {
            "grade": GRADE,
            "cases": replays,
            "counterfactuals": counterfactuals,
            "weights_unchanged": True,
            "tolerance_absolute": 2e-6,
            "no_optimizer_or_gradients": True,
        },
    )
    gate_array = np.asarray(gates)
    write_json(
        out / "gate_sample_summary.json",
        {
            "shared_across_five_stocks_by_construction": True,
            "channel_std_across_sample": gate_array.std(0).tolist(),
            "zero_logit_identity": bool(
                torch.equal(16 * torch.softmax(torch.zeros(1, 16), -1), torch.ones(1, 16))
            ),
            "fitted_sample": gate_diagnostics(torch.tensor(gate_array)),
            "sample_is_representative_plus_posthoc_not_population": True,
        },
    )
    # Compare low denominators with large relative moves without pretending to identify clipping.
    raw_examples = details["refit"]
    max_target = np.asarray([max(abs(v) for v in r["TG0"]) for r in raw_examples])
    relative = np.asarray([max(abs(v - r["median"]) for v in r["returns"]) for r in raw_examples])
    denominator = np.asarray([r["denominator"] for r in raw_examples])
    target_association = {
        "training_origin_count": len(max_target),
        "max_abs_target": float(max_target.max()),
        "top_target_1pct_mean_denominator": float(
            denominator[np.argsort(-max_target)[: math.ceil(0.01 * len(max_target))]].mean()
        ),
        "all_mean_denominator": float(denominator.mean()),
        "log_abs_target_vs_log_relative_numerator_corr": float(
            np.corrcoef(np.log(max_target), np.log(relative))[0, 1]
        ),
        "log_abs_target_vs_log_denominator_corr": float(
            np.corrcoef(np.log(max_target), np.log(denominator))[0, 1]
        ),
        "CLIPPING_CAUSAL_LINK": "UNRESOLVED",
        "historical_batch_loss_gradient_link": (
            "CLIPPING_CAUSE_NOT_IDENTIFIABLE_FROM_SAVED_BATCH_LOGS"
        ),
    }
    write_json(out / "target_association_summary.json", target_association)
    # State reporting uses the existing standardized U5 sign; no fitted diagnostic threshold.
    state = []
    for sign in (False, True):
        ix = endpoints[:, 4] >= 0 if sign else endpoints[:, 4] < 0
        selected_days = sorted({keys[i][0] for i in np.flatnonzero(ix)})
        first_state = {d: bool(endpoints[keys.index((d, 1)), 4] >= 0) for d in days}
        anchor_days = [d for d in days if first_state[d] == sign]
        episode_count = sum(
            i == 0 or positions[i] - positions[i - 1] != 1 or first_state[days[i - 1]] != sign
            for i, d in enumerate(days)
            if first_state[d] == sign
        )
        state.append(
            {
                "state": "standardized_U5_nonnegative" if sign else "standardized_U5_negative",
                "origins": int(ix.sum()),
                "sessions": len(selected_days),
                "first_origin_anchor_sessions": len(anchor_days),
                "contiguous_anchor_episodes": int(episode_count),
                "support": "SPARSE_EXPLORATORY_ONLY"
                if len(anchor_days) < 30 or episode_count < 3
                else "DESCRIPTIVE_SUPPORTED_OCCUPANCY",
                "qualification": "Sign of standardized U5, not raw U5 bull/bear. No regime fit.",
                "MC1_minus_MC0_origin_IC": float(
                    np.mean(
                        [
                            value
                            for i in np.flatnonzero(ix)
                            if (value := rank_difference(scores["MC1"][i], scores["MC0"][i], y[i]))
                            is not None
                        ]
                    )
                ),
            }
        )
    write_json(
        out / "market_state_diagnostic.json",
        {"slices": state, "no_new_threshold_or_regime_fit": True},
    )
    write_json(
        out / "diagnostic_summary.json",
        {
            "status": "TA008_DIAGNOSIS_COMPLETE",
            "grade": GRADE,
            "load_views_seconds": load_seconds,
            "read_only_analysis_seconds": time.monotonic() - started,
            "ledger_count": 1
            + sum(
                r["status"] == "STARTED"
                for r in journal_rows_v2(Path("reports/audit/track_a_real_pairs_v2.jsonl"))
            ),
            "models": {
                name: {"MSE": m["MSE"], "daily_IC": m["daily_Rank_IC"]}
                for name, m in metrics.items()
            },
            "health": health,
            "score_equivalence": equivalence,
            "trace_cases": len(replays),
            "CLIPPING_CAUSAL_LINK": "UNRESOLVED",
            "target_association": target_association,
            "next_disposition": "NO_HYPERPARAMETER_CHANGE_YET",
            "new_neural_pairs": 0,
        },
    )
    print(
        json.dumps(
            {
                "status": "TA008_DIAGNOSIS_COMPLETE",
                "seconds": time.monotonic() - started,
                "trace_cases": len(replays),
                "ledger": "4/40",
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
