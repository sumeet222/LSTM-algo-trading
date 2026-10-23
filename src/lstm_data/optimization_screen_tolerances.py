"""Read-only P024 audit of existing numerical tolerances; never relaxes a comparison."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .config import write_json
from .hf1m_ft16_source import ref
from .optimization_screen import RUNS as ORIGINAL_RUNS
from .optimization_screen_recovery_authority import RUNS, VARIANTS


def comparison(
    name: str, actual: np.ndarray, expected: np.ndarray, rtol: float, atol: float
) -> dict:
    """Measure error against the unchanged original acceptance budget."""
    error = np.abs(np.asarray(actual, dtype=float) - np.asarray(expected, dtype=float))
    budget = atol + rtol * np.abs(np.asarray(expected, dtype=float))
    np.testing.assert_allclose(actual, expected, rtol=rtol, atol=atol)
    return dict(
        quantity=name,
        rtol=rtol,
        atol=atol,
        max_abs_error=float(error.max()),
        max_budget_fraction=float(np.max(error / budget)),
    )


def audit(workflow: Path, out: Path) -> None:
    receipt = json.loads((workflow / "workflow_rehearsal_receipt.json").read_text())
    if receipt["status"] != "PASS_COMPLETE_ZERO_STEP_WORKFLOW":
        raise ValueError("P024_COMPLETE_WORKFLOW_REHEARSAL_REQUIRED")
    rows = []
    roots = [
        (v.arm, workflow / (v.arm + "_diagnostics"), workflow / run_id)
        for v, run_id in zip(VARIANTS, RUNS, strict=True)
    ]
    original = Path("reports/experiments/ta024_hf1m_long_optimization_2026-10-23_preparation_v3")
    roots.append(("LRLOW", original / "LRLOW_diagnostics_v1", original / ORIGINAL_RUNS[0]))
    for arm, root, run in roots:
        for role in ("inner_train", "inner_validation", "refit", "development"):
            path = root / role / "population.parquet"
            f = pd.read_parquet(path)
            if f.session_date_et.ge("2026-01-01").any():
                raise ValueError("P024_PROTECTED_NUMERICS_DENIED")
            y = f.TG20.to_numpy(dtype=float)
            s = float(f.t2_scale.iloc[0])
            if not f.t2_scale.eq(s).all():
                raise ValueError("P024_MIXED_RECIPE_SCALE")
            target = f.numerator.to_numpy(dtype=float) / (
                f.cross_section_mad.to_numpy(dtype=float) + f.epsilon.to_numpy(dtype=float)
            )
            pred = s * np.sinh(f.z_hat.to_numpy(dtype=float))
            z32 = np.arcsinh(y.astype(np.float32) / np.float32(s)).astype(float)
            loss = (z32 - f.raw_0.to_numpy(dtype=float)) ** 2
            fixed = json.loads((run / (role + "_checkpoint_metrics.json")).read_text())
            checks = [
                comparison("TG20 numerator/(MAD+epsilon)", y, target, 1e-10, 1e-11),
                comparison("once-only inverse", f.y_hat.to_numpy(dtype=float), pred, 7e-7, 1e-7),
                comparison(
                    "float32 supervised point loss", f.raw.to_numpy(dtype=float), loss, 3e-5, 2e-6
                ),
                comparison(
                    "weighted checkpoint zMSE",
                    np.array([f.total.sum()]),
                    np.array([fixed["objective"]]),
                    5e-7,
                    1e-8,
                ),
            ]
            # A meaningful wrong prediction must be rejected, not hidden by these tolerances.
            try:
                np.testing.assert_allclose(
                    f.y_hat.to_numpy(dtype=float) + 0.01, pred, rtol=7e-7, atol=1e-7
                )
            except AssertionError:
                negative = True
            else:
                raise ValueError("P024_TOLERANCE_HIDES_MEANINGFUL_ERROR")
            rows.append(
                dict(
                    arm=arm,
                    role=role,
                    source=ref(path),
                    checks=checks,
                    injected_prediction_error_rejected=negative,
                )
            )
    write_json(
        out,
        dict(
            status="PASS_UNCHANGED_TOLERANCES",
            checks=rows,
            hyperparameter_tolerance=0,
            checkpoint_reload_tolerance=0,
            selector_comparator="strict <; no tolerance or epsilon added",
            tolerances_relaxed=False,
            protected_numeric_access=False,
            optimizer_updates=0,
        ),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workflow", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    a = parser.parse_args()
    audit(a.workflow, a.out)
