"""Exactly 28 authorized recent36 ridge attempts; frozen recipes, no neural calls."""

from __future__ import annotations

import argparse
import csv
import json
import resource
import time
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import torch

from .hf20_ranking import (
    GRID,
    YEARS,
    daily_ic,
    origin_weights,
    rank_targets,
    ranks,
    ridge_solution,
    ridge_system,
)
from .hf20_ranking_data import FoldData, year_guard
from .hf20_ranking_run import sha, write
from .hf20_recent_analysis import cohorts, collective, origin_panel, saved_monthly
from .neural_engine import SharedLSTM

PRIOR = Path("reports/experiments/hf20_s1_s2_continuation_2026-10-25_204117")
OLD = Path("reports/experiments/hf20_s1_s2_ranking_2026-10-25_225152_preparation_v1")
POINTER = Path("configs/CURRENT_EXPERIMENT_REGISTRY.json")


def lower_bound(stop: str) -> str:
    """Inclusive 36-calendar-month span ending at the inherited cutoff date."""
    return ((pd.Timestamp(stop) + pd.Timedelta(days=1)) - pd.DateOffset(months=36)).strftime(
        "%Y-%m-%d"
    )


def recent_positions(data: FoldData, year: int, role: str) -> np.ndarray:
    year_guard(year)
    if role not in ("inner_train", "refit"):
        raise ValueError("FIT_ROLE_ONLY")
    plan, _ = data.plans[year]
    stop = plan["inner_stop"] if role == "inner_train" else plan["refit_stop"]
    pos = data.positions(year, role)
    pos = pos[data.rows.iloc[pos].session_date_et.ge(lower_bound(stop)).to_numpy()]
    rows = data.rows.iloc[pos]
    if rows.session_date_et.nunique() < 100 or len(rows) < 200:
        raise ValueError("INSUFFICIENT_RECENT_CHRONOLOGICAL_SUPPORT")
    limit = pd.Timestamp(stop, tz="America/New_York") + pd.Timedelta(days=1)
    if not pd.to_datetime(rows.label_maturity_utc, utc=True).lt(limit).all():
        raise ValueError("UNMATURED_RECENT_FIT_LABEL")
    return pos


def forecast(data: FoldData, pos: np.ndarray, coef: np.ndarray) -> np.ndarray:
    """Pure NumPy linear prediction, never a recurrent checkpoint or Torch forward."""
    if coef.shape != (769,):
        raise ValueError("EXACT768_PLUS_INTERCEPT_REQUIRED")
    values = []
    for start in range(0, len(pos), 16):
        x, _, _ = data.arrays(pos[start : start + 16])
        values.append(x.reshape(-1, 20, 768) @ coef[:-1] + coef[-1])
    result = np.concatenate(values)
    if not np.isfinite(result).all():
        raise ValueError("NONFINITE_LINEAR_SCORES")
    return result


def old_score_path(year: int, role: str) -> Path:
    dest = PRIOR / f"F{year % 100}_S1_LR"
    if year == 2021 and role.startswith("inner"):
        dest = OLD / dest.name
    return dest / f"{role}_scores.parquet"


def support(data: FoldData, year: int, role: str, pos: np.ndarray) -> dict:
    rows = data.rows.iloc[pos]
    first = data.grid.iloc[rows.first_step.to_numpy(int)].hour_end_utc
    end = pd.to_datetime(rows.entry_end_utc, utc=True)
    # Label maturity is inherited endpoint+2 minutes; historical publication remains unverified.
    plan, _ = data.plans[year]
    phase = "inner" if role.startswith("inner") else "refit"
    stop = plan["inner_stop"] if phase == "inner" else plan["refit_stop"]
    return dict(
        year=year,
        role=role,
        phase=phase,
        cutoff=stop,
        requested_recent_start=lower_bound(stop),
        origins=len(pos),
        stock_rows=20 * len(pos),
        sessions=rows.session_date_et.nunique(),
        first_session=str(rows.session_date_et.min()),
        last_session=str(rows.session_date_et.max()),
        feature_first=str(first.min()),
        feature_last=str(end.max()),
        maturity_first=str(rows.label_maturity_utc.min()),
        maturity_last=str(rows.label_maturity_utc.max()),
        phase_recipe_path=str(PRIOR / f"F{year % 100}_{phase}_recipe.json"),
        phase_recipe_sha256=sha(PRIOR / f"F{year % 100}_{phase}_recipe.json"),
        available_at="UNKNOWN; inherited end+2 minute issuance assumption",
    )


def preservation(out: Path, *, final: bool = False) -> dict:
    """Byte checks only, including any protected references; never numerical decoding."""
    receipt = out / "INPUT_PRESERVATION.json"
    if final:
        refs = json.loads(receipt.read_text())["files"]
    else:
        refs = {}
        for row in csv.DictReader((PRIOR / "artifact_inventory.csv").open()):
            refs[row["path"]] = row["sha256"]
        # Older manifests bind historical registry pointers; bind the live pointer now.
        for name in (
            "CONTINUATION_AUTHORITY_AND_RUN_MANIFEST.json",
            "PAIR_GUARD_PROSPECTIVE_AMENDMENT.json",
        ):
            for ref in json.loads((PRIOR / name).read_text())["preserve_refs"]:
                if ref["path"] != str(POINTER):
                    prior = refs.setdefault(ref["path"], ref["sha256"])
                    if prior != ref["sha256"]:
                        raise ValueError("CONFLICTING_PRIOR_PRESERVATION_BINDINGS")
        refs[str(POINTER)] = sha(POINTER)
        for p in PRIOR.iterdir():
            if p.is_file():
                refs.setdefault(str(p), sha(p))
    for name, expected in refs.items():
        if sha(Path(name)) != expected:
            raise ValueError("PRIOR_BYTES_CHANGED: " + name)
    result = dict(status="PASS", count=len(refs), protected_files="BYTE_HASH_ONLY", files=refs)
    if not final:
        write(receipt, result)
    return dict(status="PASS", count=len(refs), live_pointer_sha256=refs[str(POINTER)])


def preflight(data: FoldData, out: Path) -> None:
    if not (out / "GATE_B.json").exists():
        raise ValueError("SAVED_OUTPUT_MONTHLY_GATE_REQUIRED")
    saved = json.loads((PRIOR / "folds.json").read_text())
    if [data.plans[y][0] for y in YEARS] != saved:
        raise ValueError("FOLD_PLAN_CHANGED")
    rows = []
    replay = []
    for year in YEARS:
        for phase in ("inner", "refit"):
            recipe_path = PRIOR / f"F{year % 100}_{phase}_recipe.json"
            if not recipe_path.is_file():
                raise ValueError("FROZEN_RECIPE_MISSING_NO_REFIT_ALLOWED")
            data.phase(year, phase, PRIOR)
            fitrole = "inner_train" if phase == "inner" else "refit"
            rows.append(support(data, year, fitrole, recent_positions(data, year, fitrole)))
            coefpath = PRIOR / f"F{year % 100}_S1_LR/refit_coefficients.npy"
            if phase == "inner":
                base = OLD if year == 2021 else PRIOR
                selection = json.loads((base / f"F{year % 100}_S1_LR/selection.json").read_text())[
                    "selected"
                ]
                coefpath = base / f"F{year % 100}_S1_LR/inner_{selection['penalty']}.npy"
            for role in (
                ("inner_train", "inner_validation") if phase == "inner" else ("refit", "oos")
            ):
                pos = data.positions(year, role)
                index = pd.read_csv(PRIOR / f"F{year % 100}_{role}_indices.csv")
                actual = data.rows.iloc[pos]
                for key in ("origin_id", "session_date_et", "entry_index", "first_step"):
                    np.testing.assert_array_equal(index[key].to_numpy(), actual[key].to_numpy())
                template = pd.read_parquet(old_score_path(year, role))
                np.testing.assert_array_equal(
                    template.origin_id.to_numpy()[::20], actual.origin_id.to_numpy()
                )
                np.testing.assert_array_equal(template.ticker.to_numpy()[:20], data.symbols)
                # Replay every OOS key and three deterministic origins in other roles.
                chosen = (
                    np.arange(len(pos))
                    if role == "oos"
                    else np.unique([0, len(pos) // 2, len(pos) - 1])
                )
                score = forecast(data, pos[chosen], np.load(coefpath))
                expected = template.score.to_numpy().reshape(-1, 20)[chosen]
                np.testing.assert_allclose(score, expected, rtol=1e-13, atol=1e-14)
                _, r, y = data.arrays(pos[chosen])
                np.testing.assert_allclose(
                    r, template.return_4h.to_numpy().reshape(-1, 20)[chosen], rtol=1e-13, atol=1e-15
                )
                np.testing.assert_allclose(
                    y, template.TG20.to_numpy().reshape(-1, 20)[chosen], rtol=1e-13, atol=1e-15
                )
                replay.append(
                    dict(
                        year=year,
                        role=role,
                        origins_replayed=len(chosen),
                        coefficient=str(coefpath),
                        status="PASS",
                    )
                )
    pd.DataFrame(rows).to_csv(out / "FOLD_SOURCE_RECIPE_MANIFEST.csv", index=False)
    pd.DataFrame(replay).to_csv(out / "PREFLIGHT_LINEAR_REPLAY.csv", index=False)
    write(
        out / "GATE_A.json",
        dict(
            status="PASS",
            folds=4,
            matched_roles=16,
            neural_calls=0,
            recipes_reused=8,
            recipe_fits=0,
            feature_flattening="48 chronological steps; frozen ORDER16 inside each; free intercept",
            window="[(cutoff+1day)-36calendar months, cutoff] inclusive; source warmup unchanged",
            scalers="expanding-prefix statistics intentionally retained for both estimators",
        ),
    )


class Attempts:
    """Separate write-once baseline journal; a STARTED attempt can never be retried."""

    def __init__(self, out: Path):
        self.path = out / "nonneural_attempts.jsonl"
        if self.path.exists():
            raise ValueError("EXISTING_ATTEMPTS_NO_RESTART")
        self.started: list[str] = []

    def event(self, key: str, status: str, details: dict) -> None:
        if status == "STARTED":
            if key in self.started or len(self.started) >= 28:
                raise ValueError("RETRY_OR_BUDGET_EXCEEDED")
            self.started.append(key)
        record = dict(
            key=key,
            status=status,
            attempt=self.started.index(key) + 1,
            at=pd.Timestamp.now(tz="America/New_York").isoformat(),
            **details,
        )
        with self.path.open("a") as f:
            f.write(json.dumps(record, allow_nan=False) + "\n")
            f.flush()


def fit_attempt(
    log: Attempts, key: str, system: tuple[np.ndarray, np.ndarray], penalty: float, path: Path
) -> tuple[np.ndarray, dict] | None:
    log.event(key, "STARTED", dict(penalty=penalty))
    began = time.monotonic()
    try:
        coef = ridge_solution(*system, penalty)
        matrix = system[0] + np.diag(np.r_[np.full(768, penalty), 0.0])
        residual = matrix @ coef - system[1]
        np.testing.assert_allclose(residual, 0, rtol=0, atol=1e-9)
        np.save(path, coef)
        np.testing.assert_array_equal(coef, np.load(path))
        info = dict(
            penalty=penalty,
            seconds=time.monotonic() - began,
            coefficient_path=str(path),
            sha256=sha(path),
            slope_norm=float(np.linalg.norm(coef[:-1])),
            intercept=float(coef[-1]),
            normal_equation_max_abs_residual=float(abs(residual).max()),
            penalty_term=float(penalty * (coef[:-1] @ coef[:-1])),
        )
        log.event(key, "COMPLETED", info)
        return coef, info
    except np.linalg.LinAlgError as e:
        log.event(key, "FAILED", dict(error=str(e), isolated_numerical_failure=True))
        return None
    except BaseException as e:
        log.event(key, "FAILED", dict(error=str(e), isolated_numerical_failure=False))
        raise


def score_table(
    data: FoldData, year: int, role: str, pos: np.ndarray, coef: np.ndarray, coefpath: Path
) -> pd.DataFrame:
    """Copy existing source-key operands, replacing only new scores and their derived fields."""
    template = pd.read_parquet(old_score_path(year, role))
    ids = data.rows.iloc[pos].origin_id.to_numpy()
    f = template.loc[template.origin_id.isin(ids)].copy().reset_index(drop=True)
    np.testing.assert_array_equal(f.origin_id.to_numpy()[::20], ids)
    np.testing.assert_array_equal(f.ticker.to_numpy()[:20], data.symbols)
    score = forecast(data, pos, coef)
    _, r, y = data.arrays(pos)
    np.testing.assert_array_equal(r, f.return_4h.to_numpy().reshape(-1, 20))
    np.testing.assert_array_equal(y, f.TG20.to_numpy().reshape(-1, 20))
    np.testing.assert_array_equal(rank_targets(r).reshape(-1), f.q.to_numpy())
    f["model"] = "RECENT36_LR"
    f["score"] = score.reshape(-1)
    f["prediction_rank"] = ranks(score).reshape(-1)
    f["actual_row_allocation"] = (score.reshape(-1) - f.q.to_numpy()) ** 2 / 20
    f["weight"] = np.repeat(origin_weights(data.rows.iloc[pos].session_date_et.to_numpy()) / 20, 20)
    f["relative_side_hit"] = (
        np.sign(score - np.median(score, axis=1)[:, None])
        == np.sign(r - np.median(r, axis=1)[:, None])
    ).reshape(-1)
    f["coefficient_sha256"] = sha(coefpath)
    f["execution_sha256"] = sha(Path(__file__))
    return f


def run(data: FoldData, out: Path) -> None:
    if json.loads((out / "GATE_A.json").read_text())["status"] != "PASS":
        raise ValueError("PREFLIGHT_GATE_REQUIRED")
    log = Attempts(out)
    selections = []
    supports = []
    for year in YEARS:
        dest = out / f"F{year % 100}_RECENT36_LR"
        dest.mkdir()
        data.phase(year, "inner", PRIOR)
        fitpos = recent_positions(data, year, "inner_train")
        valpos = data.positions(year, "inner_validation")
        system = ridge_system(data.linear_stream(fitpos))
        candidates = []
        for penalty in GRID:
            result = fit_attempt(
                log,
                f"F{year % 100}/inner/{penalty}",
                system,
                penalty,
                dest / f"inner_{penalty}.npy",
            )
            if result is None:
                continue
            coef, info = result
            score = forecast(data, valpos, coef)
            ic = daily_ic(
                data.returns[valpos], score, data.rows.iloc[valpos].session_date_et.to_numpy()
            )

            def objective(pos: np.ndarray) -> float:
                s = forecast(data, pos, coef)
                q = rank_targets(data.returns[pos])
                w = origin_weights(data.rows.iloc[pos].session_date_et.to_numpy())
                return float(w @ ((s - q) ** 2).mean(1))

            train_loss = objective(fitpos)
            # Independent direct streamed prediction objective reconciles sufficient statistics.
            w = origin_weights(data.rows.iloc[fitpos].session_date_et.to_numpy())
            q2 = float(w @ (rank_targets(data.returns[fitpos]).astype(float) ** 2).mean(1))
            np.testing.assert_allclose(
                train_loss,
                q2 - 2 * coef @ system[1] + coef @ system[0] @ coef,
                rtol=1e-10,
                atol=1e-12,
            )
            row = dict(
                year=year,
                **info,
                inner_ic=ic,
                inner_train_loss=train_loss,
                inner_validation_loss=objective(valpos),
                fit_objective=train_loss + info["penalty_term"],
                status="COMPLETED",
            )
            selections.append(row)
            candidates.append(row)
        finite = [r for r in candidates if np.isfinite(r["inner_ic"])]
        if not finite:
            write(
                dest / "UNAVAILABLE.json", dict(status="NO_FINITE_INNER_CANDIDATE", no_retry=True)
            )
            continue
        selected = max(finite, key=lambda r: (r["inner_ic"], r["penalty"]))
        write(
            dest / "selection.json",
            dict(
                candidates=candidates,
                selected=selected,
                rule="maximum validation equal-session IC; exact ties prefer larger penalty",
            ),
        )
        coefpath = Path(selected["coefficient_path"])
        coef = np.load(coefpath)
        for role, pos in (("inner_train", fitpos), ("inner_validation", valpos)):
            score_table(data, year, role, pos, coef, coefpath).to_parquet(
                dest / f"{role}_scores.parquet", index=False
            )
            supports.append(support(data, year, role, pos))
        data.phase(year, "refit", PRIOR)
        refit = recent_positions(data, year, "refit")
        result = fit_attempt(
            log,
            f"F{year % 100}/refit",
            ridge_system(data.linear_stream(refit)),
            selected["penalty"],
            dest / "refit_coefficients.npy",
        )
        if result is None:
            write(dest / "UNAVAILABLE.json", dict(status="ISOLATED_REFIT_FAILURE", no_retry=True))
            continue
        coef, info = result
        checks = []
        for role, pos in (("refit", refit), ("oos", data.positions(year, "oos"))):
            table = score_table(data, year, role, pos, coef, dest / "refit_coefficients.npy")
            path = dest / f"{role}_scores.parquet"
            table.to_parquet(path, index=False)
            reloaded = pd.read_parquet(path)
            pd.testing.assert_frame_equal(table, reloaded, check_exact=True)
            panel = origin_panel(reloaded)
            d = panel.groupby("session_date_et").ic.mean().mean()
            checks.append(
                dict(
                    role=role,
                    daily_ic=float(d),
                    origins=len(panel),
                    sessions=panel.session_date_et.nunique(),
                    sha256=sha(path),
                )
            )
            supports.append(support(data, year, role, pos))
        # Check all four roles' exact objectives and cohorts before accepting the fold.
        cohort_rows = []
        for role in ("inner_train", "inner_validation", "refit", "oos"):
            f = pd.read_parquet(dest / f"{role}_scores.parquet")
            p = origin_panel(f)
            base = old_score_path(year, role)
            th = json.loads(base.with_name(role + "_thresholds.json").read_text())
            cohort_rows.append(cohorts(f, th))
            saved = float(
                np.repeat(origin_weights(f.session_date_et.to_numpy()[::20]), 20)
                @ f.actual_row_allocation.to_numpy()
            )
            direct = float(p.groupby("session_date_et").actual_loss.mean().mean())
            np.testing.assert_allclose(saved, direct, rtol=1e-12, atol=1e-14)
        pd.concat(cohort_rows, ignore_index=True).to_csv(
            dest / "objective_cohorts.csv", index=False
        )
        write(
            dest / "GATE_C.json",
            dict(
                status="PASS",
                year=year,
                selected_penalty=selected["penalty"],
                refit=info,
                checks=checks,
                coefficient_exact_reload=True,
                rank_objective_and_cohort_conservation=True,
                OOS_keys_exact=True,
                no_neural_calls=True,
                thresholds="reused expanding-prefix train-frozen definitions; matched cohorts",
            ),
        )
        print(
            f"F{year % 100} PASS lambda={selected['penalty']} OOS_IC={checks[-1]['daily_ic']:.8f}",
            flush=True,
        )
    pd.DataFrame(selections).to_csv(out / "RECENT36_INNER_SELECTION.csv", index=False)
    pd.DataFrame(supports).to_csv(out / "RECENT36_ROLE_SUPPORT.csv", index=False)
    records = [json.loads(s) for s in log.path.read_text().splitlines()]
    write(
        out / "FIT_COMPLETION.json",
        dict(
            status="ALL_AUTHORIZED_ATTEMPTS_FINISHED",
            starts=sum(r["status"] == "STARTED" for r in records),
            completed=sum(r["status"] == "COMPLETED" for r in records),
            failed=sum(r["status"] == "FAILED" for r in records),
            neural_ledger=74,
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--saved-monthly", action="store_true")
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--collect", action="store_true")
    args = parser.parse_args()
    if sum((args.saved_monthly, args.preflight, args.run, args.collect)) != 1:
        parser.error("Choose exactly one stage")
    out = args.out
    if not (out / "submitted_instruction.txt").exists():
        raise ValueError("DIRECT_TASK_AUTHORITY_MISSING")
    began = time.monotonic()
    with ExitStack() as stack:
        step = stack.enter_context(
            patch.object(
                torch.optim.AdamW, "step", side_effect=AssertionError("NEURAL_STEP_FORBIDDEN")
            )
        )
        forward = stack.enter_context(
            patch.object(
                SharedLSTM, "forward", side_effect=AssertionError("NEURAL_INFERENCE_FORBIDDEN")
            )
        )
        fit = stack.enter_context(
            patch(
                "lstm_data.hf20_ranking_data.fit",
                side_effect=AssertionError("SCALER_REFIT_FORBIDDEN"),
            )
        )
        if args.saved_monthly:
            preservation(out, final=(out / "INPUT_PRESERVATION.json").exists())
            saved_monthly(PRIOR, out)
            stage = "saved_monthly"
        elif args.collect:
            collective(PRIOR, out)
            stage = "collective_analysis"
        else:
            if args.run:
                plan = json.loads((out / "AUTHORIZED_LINEAR_PLAN.json").read_text())
                if (
                    plan["instruction_sha256"] != sha(out / "submitted_instruction.txt")
                    or plan["max_attempts"] != 28
                    or plan["grid"] != list(GRID)
                    or plan["neural_starts"] != 0
                    or plan["window_months"] != 36
                ):
                    raise ValueError("EXACT_LINEAR_AUTHORITY_REQUIRED")
                for ref in plan["code"]:
                    if sha(Path(ref["path"])) != ref["sha256"]:
                        raise ValueError("SEALED_EXECUTION_CHANGED")
                preservation(out, final=True)
            data = FoldData(live_approved=True)
            if args.preflight:
                preflight(data, out)
                stage = "preflight"
            else:
                run(data, out)
                stage = "linear_fitting"
        assert step.call_count == forward.call_count == fit.call_count == 0
        preserve = preservation(out, final=True)
        write(
            out / f"{stage}_RECEIPT.json",
            dict(
                status="PASS",
                seconds=time.monotonic() - began,
                peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                neural_step_calls=step.call_count,
                neural_forward_calls=forward.call_count,
                scaler_fit_calls=fit.call_count,
                prior_preservation=preserve,
            ),
        )


if __name__ == "__main__":
    main()
