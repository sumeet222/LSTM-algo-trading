"""Portable paths and immutable content identities."""

import hashlib
import json
from pathlib import Path

ROOT = Path("trading/track2/stage35/final_backtest_v4")
V2 = Path("trading/track2/stage35/completion_v2")
V3 = Path("trading/track2/stage35/completion_v3")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, default=str, separators=(",", ":")).encode()
    ).hexdigest()


def publish(path: Path, value: object) -> None:
    text = json.dumps(value, indent=2, sort_keys=True, default=str) + "\n"
    if path.exists():
        if path.read_text() != text:
            raise ValueError("IMMUTABLE_OUTPUT:" + str(path))
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(text)
    temp.replace(path)
