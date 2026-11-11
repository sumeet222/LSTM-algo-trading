"""No historical economic runner exists in this delivery. Gate refuses before IO."""

import json
from pathlib import Path

REQUIRED = (
    "G_ACCOUNTING",
    "G_EXECUTION",
    "G_PRICE_BASIS",
    "G_SHORT",
    "G_RISK",
    "G_PROVENANCE",
    "G_HUMAN",
    "G_REPOSITORY",
)


def require_backtest_approval(report: dict) -> None:
    for key in REQUIRED:
        if report.get("gates", {}).get(key, {}).get("status") != "PASS":
            raise PermissionError("BACKTEST_HOLD:" + key)
    human = report["gates"]["G_HUMAN"]
    if (
        human.get("reviewer_kind") != "EXTERNAL_HUMAN"
        or not human.get("external_approval_id")
        or human.get("created_by") in ("codex", "agent", None)
    ):
        raise PermissionError("BACKTEST_HUMAN_NOT_AUTHENTICATED")
    # An actual future versioned financial protocol/runner must be separately built.
    raise PermissionError("HISTORICAL_RUNNER_NOT_ACTIVATED_IN_STAGE35")


def historical_start(gate_path: Path, output: Path) -> None:
    require_backtest_approval(json.loads(gate_path.read_text()))
    raise AssertionError("UNREACHABLE_NO_OUTPUT_CREATED")
