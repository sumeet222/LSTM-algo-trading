"""Supervise the two sealed HF20 workers sequentially, never retrying a started pair."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd

from lstm_data.config import write_json
from lstm_data.hf20_training_authority import IDS, ensure, read_rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--approval", type=Path, required=True)
    args = parser.parse_args()
    plan = args.out / "experiment_design.json"
    started = time.monotonic()
    records = []
    for name in IDS:
        p = ensure(plan, args.approval, name)
        if any(r["run_id"] == name for r in read_rows()):
            raise ValueError("HF20_ALREADY_STARTED_NO_RETRY")
        remaining = (pd.Timestamp(p["fit_deadline"]) - pd.Timestamp.now(tz="UTC")).total_seconds()
        projected = max(
            [p["historical_runtime_estimate_NOT_MEASURED_HF20"]["cautious_pair_projection_seconds"]]
            + [r["supervisor_wall_seconds"] * 2 for r in records]
        )
        if remaining < projected:
            write_json(
                args.out / "prefix_stop.json",
                dict(
                    reason="INSUFFICIENT_WHOLE_PAIR_TIME",
                    next=name,
                    remaining_seconds=remaining,
                    projection_NOT_MEASUREMENT=projected,
                ),
            )
            break
        command = [
            sys.executable,
            "-u",
            "-m",
            "lstm_data.hf20_training_run",
            "--plan",
            str(plan),
            "--approval",
            str(args.approval),
            "--run-id",
            name,
            "--out",
            str(args.out / name),
        ]
        tick = time.monotonic()
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
            supervisor_wall_seconds=time.monotonic() - tick,
            return_code=result,
        )
        records.append(record)
        write_json(args.out / (name + "_supervisor_runtime.json"), record)
        print(json.dumps(record), flush=True)
        if result:
            # An abruptly terminated started worker still permanently consumes its slot.
            own = [r for r in read_rows() if r["run_id"] == name]
            if own and own[-1]["status"] not in ("FAILED", "COMPLETED"):
                from lstm_data.hf20_training_authority import append

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
        dict(pairs=records, queue_supervisor_wall_seconds=time.monotonic() - started),
    )
    return int(any(r["return_code"] for r in records))


if __name__ == "__main__":
    raise SystemExit(main())
