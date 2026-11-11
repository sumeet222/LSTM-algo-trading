"""Export a verified V3 terminal checkpoint after a report-only amendment."""

import argparse
import fcntl
import time
from pathlib import Path

from lstm_data.trading.track2.rapid_v1.cli import peak_memory_bytes, unique
from lstm_data.trading.track2.rapid_v1.paths import canonical, digest, publish
from lstm_data.trading.track2.rapid_v1.verification import preserve_check
from lstm_data.trading.track2.rapid_v2_diagnostics.variants import FIRST, LAST
from lstm_data.trading.track2.rapid_v3_dynamic.cli import (
    CODE,
    LIMIT,
    ROOT,
    build,
    code_hashes,
    load,
    registry,
    require_pilot,
    run_size,
    verify_parents,
)
from lstm_data.trading.track2.rapid_v3_dynamic.report import emit
from lstm_data.trading.track2.rapid_v3_dynamic.state import restore


def recover(run: Path, original_registry: Path) -> None:
    started = time.monotonic()
    current = registry()
    old = load(original_registry)
    identity = old.pop("registry_identity")
    if (
        digest(original_registry) != load(original_registry.with_suffix(".seal.json"))["sha256"]
        or canonical(old) != identity
    ):
        raise ValueError("RECOVERY_ORIGINAL_REGISTRY_DRIFT")
    historical = {**old, "registry_identity": identity}
    before, after = old["code_and_test_hashes"], code_hashes()
    changed = {p for p in before.keys() | after.keys() if before.get(p) != after.get(p)}
    if changed != {str(CODE / "report.py")}:
        raise ValueError("RECOVERY_REQUIRES_REPORT_ONLY_CHANGE")
    with (ROOT / "engine.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        parents = verify_parents()
        start_path = run / "START.json"
        start = load(start_path)
        if (
            start["registry"] != identity
            or start["pilot_sha256"] != digest(require_pilot(historical))
            or (run / "V3_RUN_STATUS.json").exists()
        ):
            raise ValueError("RECOVERY_RUN_BINDING")
        partials = sorted(run.glob("funded_*"))
        if not partials or any((p / "FUNDED_OUTPUT_MANIFEST.json").exists() for p in partials):
            raise ValueError("RECOVERY_EXPORT_CENSUS")
        failed = {str(p): digest(p) for d in partials for p in d.iterdir() if p.is_file()}
        checkpoint = run / "states" / f"{LAST}.json.gz"
        engine = build(historical, FIRST, LAST)
        restore(checkpoint, engine)
        if engine.last_completed != LAST or engine.days_completed != 1005:
            raise ValueError("RECOVERY_NONTERMINAL_CHECKPOINT")
        sources = [
            {"path": r["path"], "sha256": r["sha256"]}
            for month, r in sorted(engine.market.parts.items())
            if FIRST[:7] <= month <= LAST[:7]
        ]
        if len(sources) != 48 or engine.market.reads:
            raise ValueError("RECOVERY_SOURCE_SCOPE")
        elapsed = (checkpoint.stat().st_mtime_ns - start_path.stat().st_mtime_ns) / 1e9
        if elapsed <= 0:
            raise ValueError("RECOVERY_NONMONOTONE_FILE_TIMES")
        funded = run / ("funded_" + unique())
        result = emit(engine, funded, parents)
        protection = run / ("PARENT_PROTECTED_AFTER_" + unique() + ".json")
        preserve_check(protection)
        verify_parents()
        size = run_size(run)
        if size > LIMIT:
            raise ValueError("V3_STORAGE_LIMIT")
        receipt = {
            "original_registry": str(original_registry),
            "original_registry_sha256": digest(original_registry),
            "export_registry": current["registry_identity"],
            "export_registry_path": current["registry_path"],
            "checkpoint": str(checkpoint),
            "checkpoint_sha256": digest(checkpoint),
            "previous_unsealed_exports": failed,
            "previous_export_exception": "TypeError: float divided by Decimal in exit_share",
            "previous_exit_code": 1,
            "trading_replayed": False,
            "market_months_read_in_export": len(engine.market.reads),
            "report_only_changed": sorted(changed),
            "progress_1000_session_seconds": 343.8,
        }
        recovery = run / ("REPORT_RECOVERY_" + unique() + ".json")
        publish(recovery, receipt)
        publish(
            run / "V3_RUN_STATUS.json",
            {
                "status": "PARTIAL" if result["status_counts"].get("HOLD") else "COMPLETE",
                "cases": 54,
                "status_counts": result["status_counts"],
                "registry": identity,
                "export_registry": current["registry_identity"],
                "source_months": sources,
                "source_month_receipt_basis": "Frozen traversal through terminal checkpoint",
                "period": [FIRST, LAST],
                "sessions": engine.days_completed,
                "last_session": engine.last_completed,
                "funded_directory": str(funded),
                "funded_manifest_sha256": digest(funded / "FUNDED_OUTPUT_MANIFEST.json"),
                "wall_seconds": elapsed,
                "elapsed": elapsed,
                "measurement_scope": "START to terminal checkpoint filesystem timestamps",
                "peak_RSS_bytes": None,
                "export_peak_RSS_bytes": peak_memory_bytes(),
                "export_seconds": time.monotonic() - started,
                "new_bytes": size,
                "protection_sha256": digest(protection),
                "ledger_residual_USD": result["maximum_ledger_residual_USD"],
                "report_recovery_sha256": digest(recovery),
            },
        )
        print(run, result["status_counts"], flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("executed_registry", type=Path)
    args = parser.parse_args()
    recover(args.run, args.executed_registry)
