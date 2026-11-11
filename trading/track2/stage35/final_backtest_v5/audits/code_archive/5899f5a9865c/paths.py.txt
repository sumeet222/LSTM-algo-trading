"""Portable V5 output namespace; original V4 sources stay read-only."""

from pathlib import Path

from ..final_backtest_v4.paths import V2, V3, canonical, digest, publish

ROOT = Path("trading/track2/stage35/final_backtest_v5")
V4 = Path("trading/track2/stage35/final_backtest_v4")

__all__ = ["ROOT", "V2", "V3", "V4", "canonical", "digest", "publish"]
