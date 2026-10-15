"""Read-only G6 aggregation across both passes; never changes model fitting."""

from __future__ import annotations

import math


def g6_summary(
    calibration: tuple[dict, ...],
    refit: tuple[dict, ...],
    score_std: float,
    selection_status: str,
) -> dict:
    """Fail on missing/nonfinite telemetry, and retain warnings from either pass."""
    warnings = {}
    nonfinite = 0
    for name, records in (("calibration", calibration), ("refit", refit)):
        if not records or any(
            not isinstance(r.get("gradients"), dict)
            or not {"nonfinite_count", "sustained_clipping_warning"} <= r["gradients"].keys()
            or r.get("epoch") != i
            for i, r in enumerate(records, 1)
        ):
            raise ValueError("G6_COMPLETE_SEQUENTIAL_BOTH_PASS_TELEMETRY_REQUIRED")
        nonfinite += sum(r["gradients"]["nonfinite_count"] for r in records)
        warnings[name] = [
            r["epoch"] for r in records if r["gradients"]["sustained_clipping_warning"]
        ]
    reasons = []
    if warnings["calibration"] or warnings["refit"]:
        reasons.append("SUSTAINED_CLIPPING")
    if score_std == 0:
        reasons.append("CONSTANT_FORECAST")
    if selection_status == "MAX_EPOCHS_REACHED":
        reasons.append("MAX_EPOCHS_REACHED")
    if nonfinite or not math.isfinite(score_std):
        reasons.append("NONFINITE_TELEMETRY")
        status = "FAIL_NONFINITE_TELEMETRY"
    else:
        status = "WARN_INVESTIGATE" if reasons else "PASS_PER_RUN_TELEMETRY"
    return {
        "status": status,
        "reasons": reasons,
        "warning_epochs": warnings,
        "nonfinite_gradient_count": nonfinite,
        "scope": "BOTH_CALIBRATION_AND_REFIT",
    }
