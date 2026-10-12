"""Candidate-only source screen; no production universe activation or empirical fitting."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from lstm_data.alpaca import DataAccessError
from lstm_data.config import fingerprint, write_json
from lstm_data.universe_screen import gate_a
from lstm_data.universe_screen_audit import analyze_pilot
from lstm_data.universe_screen_source import acquire_requests, pilot_plan


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=["attribution", "pilot", "analysis"], required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    args = parser.parse_args()
    if args.phase == "analysis":
        print(analyze_pilot(args.report))
        return 0
    if args.phase == "attribution":
        if (args.report / "original_gap_attribution.json").exists():
            raise ValueError("ATTRIBUTION_EXISTS_USE_NEW_REPORT")
        result = gate_a(args.report)
        print({"original": result["original"], "warmup": result["warmup"], "denominator": 1502})
        return 0
    gate = json.loads((args.report / "original_gap_attribution.json").read_text())
    if (gate["original"], gate["warmup"], gate["denominator"]) != (919, 1183, 1502):
        raise ValueError("GATE_A_REQUIRED_BEFORE_NETWORK")
    plan = json.loads((args.report / "backup_pilot_plan.json").read_text())
    if fingerprint(plan) != fingerprint(pilot_plan()):
        raise ValueError("PILOT_PLAN_CHANGED")
    result = acquire_requests(args.report, plan, env_file=args.env_file)
    output = args.report / "backup_pilot_results.json"
    if output.exists():
        print({"status": "VERIFIED_ZERO_GET_RESUME", "attempts": result["attempts"]})
    else:
        write_json(output, result)
        print(
            {
                "status": "CANDIDATE_PILOT_COMPLETE",
                "attempts": result["attempts"],
                "bytes": result["bytes"],
            }
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except DataAccessError as exc:
        print({"status": "SOURCE_BLOCKED", "reason": str(exc)})
        raise SystemExit(2) from None
