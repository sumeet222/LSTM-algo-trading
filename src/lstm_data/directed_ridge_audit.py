"""Compact synthetic fit evidence; no raw archive reads or portfolio replay."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np

from .baseline_ridge import LAGS, lag_vectors
from .config import write_json
from .directed_peers import SIGNAL_ORDER
from .directed_ridge import DECISION_SHA, MatchedDesign, extension, fit_directed
from .directed_ridge_fixture import Case, fixture
from .ft0_transforms import ORDER, identity
from .m2 import ScheduledCalendar
from .neural_audit import peak_memory
from .p3_domain import MODE
from .p3_events import json_value


def column_names() -> tuple[str, ...]:
    stock = tuple(f"{f}:lag{lag}" for lag in LAGS for f in ORDER)
    market = tuple(f"D7_{i}:lag{lag}" for lag in LAGS for i in range(5))
    peer = tuple(f"PEER_{f}:lag{lag}" for lag in LAGS for f in ("MEAN", "SD"))
    directed = tuple(f"{f}:lag{lag}" for lag in LAGS for f in SIGNAL_ORDER)
    return stock + market + peer + ("TARGET_IS_H", "TARGET_IS_L") + directed


def run_case(case: Case, decision: Path) -> dict:
    start = time.monotonic()
    data, history, archive, pair, permission = fixture(case)
    fitted = fit_directed(
        data, "WF1", history, archive, pair, permission, decision, allow_synthetic=True
    )
    calendar = ScheduledCalendar("2020-07-01", "2023-06-30")
    design = MatchedDesign(archive, history, pair, calendar, DECISION_SHA)
    row = data.origins[-2].inputs
    window, sham, _ = design.prepare(row, fitted.ll1.preparation, permission, "HISTORICAL_TRAINING")
    prefix = np.asarray(
        lag_vectors(
            window.processed,
            permission,
            market=True,
            allow_synthetic=True,
            context="HISTORICAL_TRAINING",
        )
    )
    arms = {}
    for name, fit in zip(("LL0_R", "LL1_R", "SHAM_LL1_R"), (fitted.ll0, fitted.ll1, fitted.sham)):
        extra = extension(window, sham, fit.preparation, "HISTORICAL_TRAINING", name, DECISION_SHA)
        x = np.concatenate((prefix, np.asarray(extra.values)), axis=1)
        arms[name] = {
            "selected_lambda": fit.selected_penalty,
            "heldout_session_TG0_MSE": min(c["validation_session_TG0_MSE"] for c in fit.candidates),
            "candidates": fit.candidates,
            "cohort": fit.evidence,
            "full_prefix_coefficients": fit.solution.coefficients,
            "free_intercept": fit.solution.intercept,
            "solution_sha": identity(fit.solution),
            "input_sha": fit.input_hash,
            "illustrative_five_scores": (
                fit.solution.intercept + x @ fit.solution.coefficients
            ).tolist(),
            "score_context": "HISTORICAL_TRAINING_FABRICATED_ILLUSTRATION_NOT_ASOF_FORECAST",
            "flags": fit.solution.coefficients[161:163],
        }
    low, h = pair.universe.symbols.index(pair.lowest), pair.universe.symbols.index(pair.highest)
    expected = "H_TO_L_1" if case == "FORWARD" else "L_TO_H_1"
    index = 163 + SIGNAL_ORDER.index(expected)
    beta = fitted.ll1.solution.coefficients[index]
    loss = arms["LL1_R"]["heldout_session_TG0_MSE"]
    if case != "NULL":
        assert beta > 0 and loss < arms["LL0_R"]["heldout_session_TG0_MSE"] * 0.1
        assert loss < arms["SHAM_LL1_R"]["heldout_session_TG0_MSE"] * 0.1
    else:
        assert all(f.selected_penalty == 1.0 for f in (fitted.ll0, fitted.ll1, fitted.sham))
        assert all(
            max(abs(v) for v in f.solution.coefficients) == 0
            for f in (fitted.ll0, fitted.ll1, fitted.sham)
        )
    return {
        "case": case,
        "scope": MODE,
        "fixture_seed": 8050,
        "arms": arms,
        "matched": fitted.evidence,
        "formation": pair,
        "planted_target_ordinal": low if case == "FORWARD" else h if case == "REVERSE" else None,
        "expected_prior_channel": expected if case != "NULL" else "NONE",
        "prior_channel_index": index if case != "NULL" else None,
        "prior_channel_coefficient": beta if case != "NULL" else 0,
        "trace_examples": [window.trace(calendar, j) for j in (0, 24, 47)],
        "sham_timestamp_examples": sham.timestamp_pairs[:2] + sham.timestamp_pairs[-1:],
        "sham_binding": sham.binding,
        "seconds": time.monotonic() - start,
        "peak_memory": peak_memory(),
        "predictive_alpha_or_economic_claim": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=("FORWARD", "REVERSE", "NULL"), required=True)
    parser.add_argument("--decision", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.parts[:2] != ("reports", "data_audit"):
        raise ValueError("NEW_SEPARATE_AUDIT_EVIDENCE_ONLY")
    if args.case == "FORWARD":
        case: Case = "FORWARD"
    elif args.case == "REVERSE":
        case = "REVERSE"
    else:
        case = "NULL"
    result = run_case(case, args.decision)
    write_json(args.output, json_value(result))
    print({"case": case, "seconds": result["seconds"], "status": "SYNTHETIC_FIT_PASS"})


if __name__ == "__main__":
    main()
