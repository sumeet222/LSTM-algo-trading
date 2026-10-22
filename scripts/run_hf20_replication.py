"""Sequential Package017 supervisor; each consumed slot is never retried."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd

from lstm_data.config import write_json
from lstm_data.hf20_replication_authority import IDS, append, ensure, read_rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--approval", type=Path, required=True)
    args = parser.parse_args()
    plan = args.out / "experiment_design.json"
    tick = time.monotonic()
    records = []
    for name in IDS:
        p = ensure(plan, args.approval, name)
        if any(r["run_id"] == name for r in read_rows()):
            raise ValueError("P017_ALREADY_STARTED_NO_RETRY")
        remaining = (pd.Timestamp(p["fit_deadline"]) - pd.Timestamp.now(tz="UTC")).total_seconds()
        if remaining < p["minimum_pair_reserve_seconds"]:
            raise TimeoutError("P017_NO_WHOLE_PAIR_RESERVE")
        command = [
            sys.executable,
            "-u",
            "-m",
            "lstm_data.hf20_replication_run",
            "--plan",
            str(plan),
            "--approval",
            str(args.approval),
            "--run-id",
            name,
            "--out",
            str(args.out / name),
        ]
        pair_tick = time.monotonic()
        try:
            with (args.out / (name + "_worker_stdout.txt")).open("x") as stream:
                result = subprocess.run(
                    command, stdout=stream, stderr=subprocess.STDOUT, timeout=remaining, check=False
                ).returncode
        except subprocess.TimeoutExpired:
            result = 124
        record = dict(
            run_id=name,
            command=command,
            return_code=result,
            supervisor_wall_seconds=time.monotonic() - pair_tick,
        )
        records.append(record)
        write_json(args.out / (name + "_supervisor_runtime.json"), record)
        if result == 0:
            from lstm_data.hf20_replication_review import audit_run

            audit_run(args.out, name)
        if result:
            own = [r for r in read_rows() if r["run_id"] == name]
            if own and own[-1]["status"] not in ("COMPLETED", "FAILED"):
                append(
                    plan,
                    args.approval,
                    name,
                    "FAILED",
                    dict(reason="SUPERVISOR_EXIT", return_code=result),
                )
            break
    write_json(
        args.out / "queue_actual_runtime.json",
        dict(pairs=records, queue_supervisor_wall_seconds=time.monotonic() - tick),
    )
    return int(any(r["return_code"] for r in records))


if __name__ == "__main__":
    raise SystemExit(main())
