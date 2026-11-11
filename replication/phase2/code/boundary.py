"""Procedural clean-room boundary for the independent modeling replication."""
from __future__ import annotations

import atexit
import hashlib
import importlib.abc
import json
import os
from pathlib import Path
import sys
import time

PHASE = Path(__file__).resolve().parents[1]
ROOT = PHASE.parents[1]
SPEC = ROOT / "replication/EXPERIMENT_SPEC.md"
MONTHS = tuple(f"{year:04d}-{month:02d}" for year in range(2010, 2025)
               for month in range(1, 13) if (year, month) >= (2010, 7))
FAMILIES = {
    "hourly": ROOT / "data/processed/hf20_hf1m_long_v1_action_qa_v1/ta019b_action_qa_2026-10-22_201224/hourly",
    "canonical": ROOT / "data/processed/hf20_hf1m_long_v1/776328445b7ac6e7815ef3a483e9c8ded1eb6d56/qa_v2/canonical_observed",
    "raw": ROOT / "data/raw/hf20_hf1m_long_v1/776328445b7ac6e7815ef3a483e9c8ded1eb6d56/raw_1m_selected",
}
ALLOWED_DATA = {str(directory / f"{month}.parquet") for directory in FAMILIES.values() for month in MONTHS}
_events: dict[tuple[str, str], int] = {}
_installed = False


class OriginalPackageBlocker(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] == "lstm_data":
            raise ImportError("Clean-room boundary forbids original lstm_data imports")
        return None


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _audit(event, args):
    if event not in {"open", "os.listdir", "os.scandir"} or not args:
        return
    raw = args[0]
    if not isinstance(raw, (str, bytes, os.PathLike)):
        return
    path = Path(os.fsdecode(raw)).absolute()
    value = str(path)
    if path == ROOT or ROOT in path.parents:
        permitted = (PHASE == path or PHASE in path.parents or path == SPEC or
                     value in ALLOWED_DATA or ROOT / ".venv" in path.parents)
        if not permitted:
            _events[("DENIED:" + event, value)] = _events.get(("DENIED:" + event, value), 0) + 1
            raise PermissionError(f"Clean-room denied project path: {path}")
        _events[(event, value)] = _events.get((event, value), 0) + 1


def receipt() -> None:
    modules = {}
    for name, module in sorted(sys.modules.items()):
        value = getattr(module, "__file__", None)
        if value:
            path = Path(value).absolute()
            if ROOT in path.parents and not (PHASE in path.parents or ROOT / ".venv" in path.parents):
                raise RuntimeError(f"Forbidden imported origin: {name}: {path}")
            modules[name] = str(path)
    result = {"procedural_not_sandbox_isolation": True, "pid": os.getpid(),
              "cwd": str(Path.cwd()), "sys_path": sys.path, "modules": modules,
              "file_events": [{"event": e, "path": p, "count": n} for (e, p), n in sorted(_events.items())]}
    (PHASE / "audit" / f"provenance_{os.getpid()}.json").write_text(json.dumps(result, indent=2))


def install() -> None:
    global _installed
    if _installed:
        return
    os.chdir(PHASE)
    sys.dont_write_bytecode = True
    sys.path[:] = [str(PHASE / "code")] + [p for p in sys.path if p and not (Path(p).absolute() == ROOT or str(ROOT / "src") in p)]
    sys.meta_path.insert(0, OriginalPackageBlocker())
    sys.addaudithook(_audit)
    atexit.register(receipt)
    _installed = True


def data_path(family: str, month: str) -> Path:
    if month not in MONTHS or family not in FAMILIES:
        raise PermissionError("Input outside literal month/family allowlist")
    path=FAMILIES[family] / f"{month}.parquet"
    _events[("admitted_data_request",str(path))]=_events.get(("admitted_data_request",str(path)),0)+1
    return path
