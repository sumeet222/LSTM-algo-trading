"""Actual pre-AVGO checkpoint replay and forensic output, no return analysis."""

import gzip
import hashlib
import json
from pathlib import Path

from ..final_backtest_v4.market import minute, stamp
from .driver import Driver
from .paths import ROOT, V4, digest, publish
from .release import Admission, fingerprint


def lines(path: Path):
    with gzip.open(path, "rt") as stream:
        for line in stream:
            yield line, json.loads(line)


def certify(pilot_folder: Path, admission: Admission) -> dict:
    original = pilot_folder / "2021-06-02"
    restored_folder = pilot_folder / "PRE_AVGO_RESTART"
    checkpoint = original / "checkpoints/2021-06-08.json.gz"
    restored = Driver.restart(checkpoint, restored_folder, admission)
    result = restored.run()
    boundary = minute("2021-06-09T00:00:00Z")
    checks = {}
    output_hashes = {}
    for kind in ("events", "daily", "cohorts"):

        def included(row):
            if kind == "daily":
                return row["date"] >= "2021-06-09"
            return int(row["posted"] if kind == "events" else row["closed_at"]) >= boundary

        first = "".join(
            line for line, row in lines(original / f"baseline/{kind}.jsonl.gz") if included(row)
        )
        second = "".join(
            line
            for line, row in lines(restored_folder / f"baseline/{kind}.jsonl.gz")
            if included(row)
        )
        checks[kind] = first == second
        output_hashes[kind] = hashlib.sha256(first.encode()).hexdigest()
    checks["pending"] = result["terminal_pending_orders"] == 0
    checks["complete"] = not result["unresolved"]
    intended = minute("2021-06-09T16:33:00Z")
    collected = {}
    for _, row in lines(original / "baseline/events.jsonl.gz"):
        if row.get("ticker") != 16 or row["population"] != "attainable":
            continue
        if row["kind"] == "V5_QUALIFIED_BAR" and row["intended_minute"] == intended:
            collected[(row["arm"], row["order"])] = {"qualified_observation": row}
        elif row["kind"] == "FILL" and (row["arm"], row["order"]) in collected:
            collected[(row["arm"], row["order"])]["fill"] = row
    rows = []
    for (arm, order), data in sorted(collected.items()):
        data["arm"] = arm
        data["order_id"] = order
        data["intended_minute_utc"] = stamp(intended)
        data["effective_fill_utc"] = stamp(data["fill"]["effective"])
        data["conditional_bar_open_fill_not_broker_claim"] = True
        rows.append(data)
    expected = {"EQUAL": "-2", "S2C_RISK": "-3"}
    checks["AVGO_expected_signed_requests"] = {
        r["arm"]: str(r["fill"]["external"]) for r in rows
    } == expected
    checks["AVGO_next_minute_actual"] = (
        all(r["fill"]["effective"] == intended + 1 for r in rows) and len(rows) == 2
    )
    record = {
        "checks": checks,
        "all_passed": all(checks.values()),
        "pre_event_checkpoint": str(checkpoint),
        "checkpoint_sha256": digest(checkpoint),
        "restart_window": ["2021-06-09", "2021-06-11"],
        "comparison": "byte-identical uncompressed JSONL suffix; gzip header wall time excluded",
        "uncompressed_output_sha256": output_hashes,
        "receipt": result,
        "V4_blocker_sha256": digest(V4 / "MATERIAL_PRICE_BLOCKER_V4.json"),
        "orders": rows,
        "files": {str(f): digest(f) for f in restored_folder.rglob("*") if f.is_file()},
    }
    publish(ROOT / ("audits/RESTART_CERTIFICATION_V5_" + fingerprint() + ".json"), record)
    publish(
        ROOT / ("audits/AVGO_ORDER_WITNESS_V5_" + fingerprint() + ".json"),
        {"orders": rows, "checks": checks},
    )
    print("PRE_AVGO_RESTART", checks, flush=True)
    return record
