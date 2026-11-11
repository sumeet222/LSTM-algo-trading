"""Validate the V5 policy and unchanged predecessor economic scenario grid."""

import json

from ..final_backtest_v4.protocol import ARMS, Scenario, scenarios, valid_multiplier
from .paths import ROOT, V4, canonical, digest

POLICY = "V5_NEXT_VALID_OBSERVED_BAR"


def freeze() -> dict:
    value = json.loads((ROOT / "FINAL_CONSOLIDATED_PROTOCOL_V5.json").read_text())
    seal = json.loads((ROOT / "FINAL_CONSOLIDATED_PROTOCOL_V5.seal.json").read_text())
    if canonical(value) != seal["sha256"]:
        raise ValueError("V5_PROTOCOL_DRIFT")
    if digest(ROOT / "execution_policy_v5.json") != value["execution_policy_sha256"]:
        raise ValueError("V5_EXECUTION_POLICY_DRIFT")
    original = json.loads((V4 / "FINAL_CONSOLIDATED_PROTOCOL.json").read_text())
    if digest(V4 / "FINAL_CONSOLIDATED_PROTOCOL.json") != value["predecessor_protocol_sha256"]:
        raise ValueError("V4_PROTOCOL_DRIFT")
    changed = {"version", "authority", "execution_policy_sha256", "predecessor_protocol_sha256"}
    if any(value[k] != v for k, v in original.items() if k not in changed):
        raise ValueError("UNAPPROVED_ECONOMIC_PROTOCOL_CHANGE")
    if value["arms"] != list(ARMS):
        raise ValueError("ARM_AXIS_DRIFT")
    return value


__all__ = ["ARMS", "POLICY", "Scenario", "freeze", "scenarios", "valid_multiplier"]
