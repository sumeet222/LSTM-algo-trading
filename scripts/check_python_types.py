"""Reproduce basic Pyright checks with the editor's explicitly selected Pylance stubs.

Run using .venv/bin/python and pass --pylance-dist <extension>/dist. Missing
checker/stubs or interpreter mismatch is HOLD, never an excuse to lower severity.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pylance-dist", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    binary = root / ".venv" / ("Scripts" if os.name == "nt" else "bin")
    interpreter = binary / ("python.exe" if os.name == "nt" else "python")
    checker = binary / ("pyright.exe" if os.name == "nt" else "pyright")
    dist = args.pylance_dist.resolve()
    if (Path(sys.executable).resolve() != interpreter.resolve() or not checker.is_file()
            or not (dist / "bundled/stubs").is_dir()
            or not (dist / "typeshed-fallback").is_dir()):
        raise SystemExit("HOLD: repository interpreter/checker/Pylance stubs must match")
    names = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard",
                            "-z", "*.py"], cwd=root, check=True, capture_output=True,
                           text=True).stdout.split("\0")
    with tempfile.TemporaryDirectory(prefix="lstm-types-") as temporary:
        folder = Path(temporary)
        config = {
            "include": [os.path.relpath(root / p, folder) for p in names if p],
            "typeCheckingMode": "basic", "pythonVersion":
                f"{sys.version_info.major}.{sys.version_info.minor}",
            "venvPath": str(root), "venv": ".venv", "extraPaths": [str(root / "src")],
            "stubPath": str(dist / "bundled/stubs"),
            "typeshedPath": str(dist / "typeshed-fallback"),
            "executionEnvironments": [{"root": str(root), "extraPaths": [str(root / "src")]}],
        }
        path = folder / "pyright.json"
        path.write_text(json.dumps(config))
        result = subprocess.run([str(checker), "--project", str(path), "--outputjson"],
                                cwd=root, capture_output=True, text=True)
    payload = json.loads(result.stdout)
    for item in payload.get("generalDiagnostics", []):
        item["file"] = str(Path(item["file"]).relative_to(root))
    payload["validation_profile"] = {"mode": "basic", "interpreter": ".venv",
                                     "pylance_dist_version": dist.parent.name,
                                     "owned_files": [p for p in names if p]}
    print(json.dumps(payload, indent=2))
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
