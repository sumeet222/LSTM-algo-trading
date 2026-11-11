"""Read-only risk re-aggregation entrypoint; never import a backtest engine."""

import argparse
import platform
import resource
import time
from pathlib import Path

from . import io
from .analysis import build
from .io import CODE, ROOT, digest, publish, verify_inputs
from .saved import load_saved


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-root", type=Path, default=ROOT)
    parser.add_argument("--prepare", action="store_true")
    args = parser.parse_args()
    if Path(args.run_id).name != args.run_id or not args.run_id:
        raise ValueError("INVALID_RUN_ID")
    io.ROOT = args.output_root
    if args.prepare:
        io.prepare()
    out = args.output_root / "runs" / args.run_id
    # Exclusive creation: a disconnected or already complete analysis is never overwritten.
    out.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    publish(
        out / "START.json",
        {
            "run_id": args.run_id,
            "scope": "READ_ONLY_SAVED_ACCOUNT_ANALYSIS",
            "code": {str(p): digest(p) for p in sorted(CODE.glob("*.py"))},
        },
    )
    try:
        data = load_saved()
        publish(
            out / "ACCOUNT_BINDINGS.json",
            {
                "accounts": data.accounts,
                "join": "sealed RESULTS strategy_id + variant; cohort arm/population not trusted",
            },
        )
        result = build(data, out)
        verified = verify_inputs()
        publish(
            out / "ANALYSIS_RECEIPT.json",
            {
                "status": "PARTIAL_WITH_EXPLICIT_MISSING_FIELDS",
                "all_available_account_and_daily_metrics": "COMPLETE_DESCRIPTIVE",
                "accounts": 12,
                "sessions_per_account": 1005,
                "paired_comparisons": 9,
                "cohort_rows": result["cohort_rows"],
                "physical_fill_rows": result["physical_rows"],
                "maximum_daily_and_terminal_residual_USD": result[
                    "max_daily_and_terminal_residual_USD"
                ],
                "immutable_inputs_after": verified,
                "elapsed_seconds": time.perf_counter() - started,
                "peak_RSS_bytes_macOS": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                "python": platform.python_version(),
                "new_trading_or_neural_runs": 0,
                "missing": [
                    "per-stock marked exposure",
                    "physical gross/long-short exposure",
                    "name/vintage utilization",
                    "exact RTH invested time",
                    "complete daily action journal",
                    "exact source mark receipt timestamps",
                    "daily live buying power after all reservations",
                ],
                "output_bytes_at_receipt": sum(
                    p.stat().st_size for p in out.rglob("*") if p.is_file()
                ),
            },
        )
    except Exception as exc:
        publish(
            out / "HOLD_WITNESS.json",
            {
                "status": "HOLD_SOURCE_OR_ACCOUNT_RECONCILIATION",
                "error": str(exc),
                "elapsed_seconds": time.perf_counter() - started,
            },
        )
        raise
    print(out)


if __name__ == "__main__":
    main()
