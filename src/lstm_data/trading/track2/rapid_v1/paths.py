"""Portable paths, atomic immutable publications and content identities."""

import hashlib
import json
from pathlib import Path

ROOT = Path("trading/track2/rapid_v1")
V5 = Path("trading/track2/stage35/final_backtest_v5")
V4 = Path("trading/track2/stage35/final_backtest_v4")
V2 = Path("trading/track2/stage35/completion_v2")
MENU = Path("HF20_Track2_Directional_Strategy_Research_Menu_Micro_and_Retail_2026-11-10.md")
PACKAGE = Path("src/lstm_data/trading/track2/rapid_v1")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(2**20), b""):
            h.update(block)
    return h.hexdigest()


def canonical(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()


def publish(path: Path, value: object) -> None:
    """Never replace an already published research artifact."""
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    if temporary.exists():
        raise FileExistsError(temporary)
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n")
    temporary.replace(path)


def code_identity() -> dict[str, str]:
    return {str(p): digest(p) for p in sorted(PACKAGE.glob("*.py"))}
