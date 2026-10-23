"""P024 repair read-only diagnostic routing; identical scientific formulas and source readers."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .config import digest, fingerprint, write_json
from .dm_quantile_cases import exact_cases
from .dm_quantile_diagnostics import allocation
from .hf1m_ft16_source import checked, ref
from .objective_screen_attribution import cohort_masks, cohort_table
from .objective_screen_audit import month_ci
from .objective_screen_diagnostics import canonical, daily_scores
from .objective_screen_metrics import equal_weights, regression
from .objective_screen_source import ordered_targets, scoped_view
from .optimization_screen import ScreenLSTM, ScreenStop
from .optimization_screen_diagnostics import original_identity
from .optimization_screen_recovery_authority import RUNS, VARIANTS, code_binding, rows
from .optimization_screen_supplement import read_updates
from .visualization.hf1m_long import LongStudy


def diagnose(plan_path: Path, arm: str, out: Path) -> None:
    plan = json.loads(plan_path.read_text())
    if plan["code"] != code_binding():
        raise ValueError("P024_FROZEN_EXECUTION_CHANGED")
    index = [v.arm for v in VARIANTS].index(arm)
    v, run_id = VARIANTS[index], RUNS[index]
    history = [r for r in rows() if r["run_id"] == run_id]
    if not history or history[-1]["status"] != "COMPLETED":
        raise ValueError("P024_COMPLETED_FIT_REQUIRED")
    rp = checked(history[-1]["detail"]["result"])
    result = json.loads(rp.read_text())
    selector = ScreenStop(improvement=v.improvement)
    for record in result["epochs"]:
        e = record["training"]["epoch"]
        receipt = rp.parent / "epoch_receipts" / f"{record['phase']}_{e:03d}.json"
        if fingerprint(json.loads(receipt.read_text())) != fingerprint(record):
            raise ValueError("P024_EPOCH_RECEIPT_MISMATCH")
        if record["phase"] == "calibration":
            if (
                selector.observe(record["validation"]["original_mse"]) != record["qualifies"]
                or asdict(selector) != record["selector"]
            ):
                raise ValueError("P024_SELECTOR_REPLAY")
    if (
        asdict(selector) != result["selector"]
        or result["initial_hash"] != result["refit_initial_hash"]
    ):
        raise ValueError("P024_SELECTOR_REFIT_IDENTITY")
    updates = read_updates(checked(result["optimizer_telemetry"]))
    if not len(updates) and result.get("scope") != "REHEARSAL_ONLY":
        raise ValueError("P024_REAL_FIT_REQUIRES_ACTUAL_UPDATES")
    if (
        len(updates) != result["calibration_steps"] + result["refit_steps"]
        or updates.postclip_norm.gt(1.00001).any()
    ):
        raise ValueError("P024_UPDATE_TELEMETRY_COUNT_CLIP")
    out.mkdir(parents=True, exist_ok=False)
    (out / ".gitignore").write_text("*\n!.gitignore\n")
    study = LongStudy.discover(Path.cwd())
    tables, metrics, differences, heterogeneity = [], [], [], []
    training = {}
    for role in ("inner_train", "inner_validation", "refit", "development"):
        view = scoped_view(study, role, stage=7)
        version = view.source.fit_version
        recipe = dict(scale=view.source.fit["t2_scale"])
        rr = next(
            r for r in result["artifacts"] if Path(r["path"]).name == role + "_predictions.parquet"
        )
        f = canonical(pd.read_parquet(checked(rr)), ordered_targets(view))
        original_identity(study, view, f)
        quality = study.targets(role)
        extra = [c for c in quality if c not in f]
        f = f.merge(
            quality[["origin_id", "ticker"] + extra],
            on=["origin_id", "ticker"],
            validate="one_to_one",
        )
        f["raw_0"], f["z_hat"], f["y_hat"] = (
            f.raw_net_output,
            f.raw_net_output,
            f.pred_original_TG20,
        )
        np.testing.assert_allclose(
            f.y_hat, recipe["scale"] * np.sinh(f.z_hat), rtol=7e-7, atol=1e-7
        )
        f = allocation(f, "SS1", recipe)  # Same ordinary z-MSE; no sampler or other head is used.
        if role in ("inner_train", "refit"):
            training[version] = f
        masks, thresholds = cohort_masks(f, training[version])
        table = cohort_table(f, masks, thresholds)
        table["role"] = role
        tables.append(table)
        dest = out / role
        dest.mkdir()
        f.to_parquet(dest / "population.parquet", index=False)
        write_json(dest / "thresholds.json", thresholds)
        fixed = json.loads((rp.parent / (role + "_checkpoint_metrics.json")).read_text())
        np.testing.assert_allclose(f.total.sum(), fixed["objective"], rtol=5e-7, atol=1e-8)
        w = equal_weights(f.session_date_et.to_numpy())
        y, hat = f.TG20.to_numpy(), f.y_hat.to_numpy()
        zero_rhs = float(w @ (hat**2) - 2 * w @ (y * hat))
        np.testing.assert_allclose(
            float(w @ ((y - hat) ** 2) - w @ (y * y)), zero_rhs, rtol=1e-8, atol=1e-12
        )
        event = float(np.quantile(abs(training[version].TG20), 0.95, method="higher"))
        d = daily_scores(f, hat, True).set_index("session_date_et")
        d.to_parquet(dest / "daily.parquet")
        m = regression(y, hat, f.session_date_et.to_numpy())
        m.update(
            model=arm,
            role=role,
            seed=v.seed,
            weighted_z_objective=float(f.total.sum()),
            unweighted_z_mse=float(f.raw.mean()),
            zero_decomposition=zero_rhs,
            event_threshold=event,
            event_observed=int((abs(y) >= event).sum()),
            event_predicted=int((abs(hat) >= event).sum()),
            event_recall=float(
                w @ ((abs(y) >= event) & (abs(hat) >= event)) / w[abs(y) >= event].sum()
            )
            if w[abs(y) >= event].sum()
            else None,
        )
        for band in (0.01, 0.05, 0.10):
            m[f"near_zero_z_{band}"] = float(w @ (abs(f.z_hat.to_numpy()) < band))
            m[f"near_zero_y_{band}"] = float(w @ (abs(hat) < band))
        for name, mask in [("tail", abs(y) >= event), ("nontail", abs(y) < event)]:
            m[name + "_mse"] = (
                float(w[mask] @ ((y[mask] - hat[mask]) ** 2) / w[mask].sum())
                if mask.any()
                else None
            )
        metrics.append(m)
        for baseline in (f"HF1M-LONG-TM0-T2-S{v.seed}-DEV1", "ZERO"):
            bhat = (
                np.zeros(len(f))
                if baseline == "ZERO"
                else canonical(study.prediction(baseline, role), f).pred_original_TG20.to_numpy()
            )
            bm = regression(y, bhat, f.session_date_et.to_numpy())
            metrics.append(dict(model=baseline, role=role, seed=v.seed, **bm))
            b = daily_scores(f, bhat, True).set_index("session_date_et")
            for metric in ("mse", "ic"):
                diff = (d[metric] - b[metric]).dropna()
                for block in (1, 2):
                    low, high = month_ci(diff, block)
                    differences.append(
                        dict(
                            role=role,
                            baseline=baseline,
                            metric=metric,
                            block_months=block,
                            replicates=400,
                            seed=22042,
                            sessions=len(diff),
                            difference=float(diff.mean()),
                            low=low,
                            high=high,
                        )
                    )
        for col, values in [
            ("ticker", f.ticker),
            ("year", f.session_date_et.str[:4]),
            (
                "era",
                np.where(
                    f.session_date_et.lt("2016-01-01"),
                    "2011-2015",
                    np.where(f.session_date_et.lt("2021-01-01"), "2016-2020", "2021-2025"),
                ),
            ),
            ("proxy", f.price_proxy_minute_count.gt(0)),
            ("zero_volume", f.assumed_zero_minute_count.gt(0)),
            ("fallback", f[version + "_feature_fallback_cells"].gt(0)),
        ]:
            for value in pd.unique(values):
                mask = np.asarray(values == value)
                mass = w[mask].sum()
                heterogeneity.append(
                    dict(
                        role=role,
                        dimension=col,
                        group=str(value),
                        rows=int(mask.sum()),
                        weight_mass=float(mass),
                        mse=float(w[mask] @ ((y[mask] - hat[mask]) ** 2) / mass),
                    )
                )
        if role == "refit":
            top = set()
            for ticker in ("AAPL", "AMZN", "TSLA", "SBUX"):
                top.update(
                    f.loc[f.ticker.eq(ticker)]
                    .sort_values(["total", "origin_id"], ascending=[False, True])
                    .head(5)
                    .index
                )
            extras = {}
            for label in ("BOTH_5", "MAD_ONLY_5"):
                eligible = f.loc[masks[label] & ~f.index.isin(top | set(extras))].sort_values(
                    "total", ascending=False
                )
                if len(eligible):
                    extras[int(eligible.index[0])] = label + " mechanism representative"
            case = exact_cases(study, view, f, pd.DataFrame(), arm, recipe, dest, extras)
            write_json(dest / "case_verification.json", case)
        checkpoint = result["calibration"] if role.startswith("inner") else result["refit"]
        model = ScreenLSTM(v)
        model.load_state_dict(torch.load(checked(checkpoint), weights_only=True)["model"])
        model.eval()
        with torch.no_grad():
            x = torch.from_numpy(view.origin_batch(tuple(range(16)))["x"].reshape(-1, 48, 16))
            _, (h, c) = model.lstm(x)
        write_json(
            dest / "recurrent_state_sample.json",
            dict(
                examples=len(x),
                hidden_shape=list(h.shape),
                cell_shape=list(c.shape),
                hidden_norm=float(h.norm()),
                cell_norm=float(c.norm()),
                hidden_min=float(h.min()),
                hidden_max=float(h.max()),
                cell_min=float(c.min()),
                cell_max=float(c.max()),
                interpretation="Sample only; saturation and vanishing gradients unproved",
            ),
        )
    pd.DataFrame(metrics).to_json(out / "metrics.json", orient="records", indent=2)
    pd.concat(tables).to_parquet(out / "cohorts.parquet", index=False)
    pd.DataFrame(differences).to_csv(out / "matched_daily_intervals.csv", index=False)
    pd.DataFrame(heterogeneity).to_csv(out / "heterogeneity.csv", index=False)
    for r in plan["protected_refs"]:
        checked(r)
    evidence = [
        ref(rp),
        ref(out / "metrics.json"),
        ref(out / "cohorts.parquet"),
        ref(out / "matched_daily_intervals.csv"),
        ref(out / "heterogeneity.csv"),
    ]
    write_json(
        plan_path.parent / f"stage_{index + 4}_receipt.json",
        dict(
            status="PASS_" + arm,
            scope=result.get("scope", "RESEARCH"),
            run_id=run_id,
            proposal_sha256=digest(plan_path),
            evidence=evidence,
            diagnostics=str(out),
            all_roles=4,
            all20_endpoint_reconstruction=True,
            selector_replay=True,
            source_preserved=True,
            protected_numeric_access=False,
            optimizer_updates=0,
        ),
    )
    (plan_path.parent / f"stage_{index + 4}_review.md").write_text(
        f"# {arm}: PASS\n\nFit and immediate full-population scientific gate passed. "
        f"Same-seed comparisons, witnesses and actual z-MSE attribution are in `{out}`. "
        "No automatic promotion or new training.\n"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--arm", choices=[v.arm for v in VARIANTS], required=True)
    parser.add_argument("--out", type=Path, required=True)
    a = parser.parse_args()
    diagnose(a.plan, a.arm, a.out)
