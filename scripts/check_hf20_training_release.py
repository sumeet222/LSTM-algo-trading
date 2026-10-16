"""One focused HF20 release check with actual command/status/time receipts; no fitting."""

from __future__ import annotations

import argparse
import subprocess
import time
from pathlib import Path

from lstm_data.config import now, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--pylance-dist", type=Path, required=True)
    args = parser.parse_args()
    records = []
    commands = [
        (
            "focused_pytest",
            [
                ".venv/bin/python",
                "-m",
                "pytest",
                "tests/test_hf20_training.py",
                "tests/test_hf20_visualization.py",
                "-q",
            ],
        ),
        ("ruff", [".venv/bin/ruff", "check", "."]),
        (
            "pylance",
            [
                ".venv/bin/python",
                "scripts/check_python_types.py",
                "--pylance-dist",
                str(args.pylance_dist),
            ],
        ),
        ("launcher_check", ["./scripts/run_track_a_dashboard.sh", "--check"]),
        ("diff_check", ["git", "diff", "--check"]),
    ]
    for name, command in commands:
        tick = time.monotonic()
        at = now()
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        log = args.out / ("release_" + name + ".txt")
        with log.open("x") as stream:
            stream.write(result.stdout + result.stderr)
        records.append(
            dict(
                name=name,
                command=command,
                started_UTC=at,
                finished_UTC=now(),
                elapsed_seconds=time.monotonic() - tick,
                return_code=result.returncode,
                log=str(log),
            )
        )
        print(name, result.returncode, flush=True)
        if result.returncode:
            break
    write_json(
        args.out / "release_check_receipts.json",
        dict(
            commands=records,
            all_pass=len(records) == len(commands) and all(r["return_code"] == 0 for r in records),
        ),
    )
    return int(len(records) != len(commands) or any(r["return_code"] for r in records))


if __name__ == "__main__":
    raise SystemExit(main())
