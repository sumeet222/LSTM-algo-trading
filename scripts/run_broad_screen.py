"""Bounded candidate-only SIP screen; full history and production activation absent."""

from __future__ import annotations

import argparse
from pathlib import Path

from lstm_data.alpaca import DataAccessError
from lstm_data.broad_screen import acquire, analyze, prepare
from lstm_data.config import write_json


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", required=True, choices=("plan", "acquire", "analyze"))
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    args = parser.parse_args()
    if args.phase == "plan":
        plan = prepare(args.report)
        print(
            {
                "requests": len(plan["requests"]),
                "worst_attempts": plan["pilot_worst_page_attempt_envelope"],
            }
        )
    elif args.phase == "acquire":
        result = acquire(args.report, env_file=args.env_file)
        name = (
            "zero_get_resume.json"
            if (args.report / "acquisition_results.json").exists()
            else "acquisition_results.json"
        )
        write_json(args.report / name, result)
        print(
            {
                "attempts": result["attempts"],
                "bytes": result["bytes"],
                "resumed": all(r["resumed"] for r in result["chunks"]),
            }
        )
    else:
        print(analyze(args.report))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except DataAccessError as exc:
        print({"status": "SOURCE_BLOCKED", "reason": str(exc)})
        raise SystemExit(2) from None
