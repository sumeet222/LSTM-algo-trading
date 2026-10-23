"""Hash-bound P022 readers with role/date guards before numeric paths or caches."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import digest
from ..hf1m_action_audit import SYMBOLS
from ..hf1m_ft16_source import COMMON, ORDER
from ..objective_screen_source import prefix_array
from .hf1m_long import LongStudy, dates, role

CONFIG = "configs/track_a_p022_visualization_v1.json"
MODELS = ("H2", "W1", "E1", "R1", "T2_42", "T2_123", "ZERO")


@dataclass(frozen=True)
class Screen:
    root: Path
    files: dict[str, dict]
    token: str
    config: dict

    @classmethod
    def discover(cls, root: Path) -> Screen:
        config = json.loads((root / CONFIG).read_text())
        manifest = config["manifest"]
        path = root / manifest["path"]
        if digest(path) != manifest["sha256"]:
            raise ValueError("P022 manifest changed")
        value = json.loads(path.read_text())
        if value["status"] != "PASS_COLLECTIVE_DIAGNOSTICS" or value["ledger"] != 41:
            raise ValueError("P022 diagnostics unavailable")
        return cls(root, value["files"], manifest["sha256"], config)

    def file(self, key: str) -> Path:
        if key not in self.files:
            raise ValueError("P022 artifact not allowlisted")
        item = self.files[key]
        path = self.root / item["path"]
        if path.stat().st_size != item["bytes"] or digest(path) != item["sha256"]:
            raise ValueError("P022 artifact changed")
        return path

    def table(self, key: str) -> pd.DataFrame:
        path = self.file(key)
        f = pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path)
        if "session_date_et" in f and f.session_date_et.ge("2026-01-01").any():
            raise ValueError("P022 protected dates denied")
        return f

    def population(self, model: str, split: str) -> pd.DataFrame:
        role(split)
        if model not in MODELS:
            raise ValueError("P022 model denied")
        return self.table(f"{model}/{split}/population.parquet")

    def filtered(self, model: str, split: str, ticker: str, start: str, end: str) -> pd.DataFrame:
        dates(start, end)
        role(split)
        if ticker not in SYMBOLS:
            raise ValueError("P022 ticker denied")
        f = self.population(model, split)
        return f.loc[f.ticker.eq(ticker) & f.session_date_et.between(start, end)].copy()


def safe_features(
    study: LongStudy, ticker: str, start: str, end: str, version: str, origin: int
) -> pd.DataFrame:
    """Decode only the requested date prefix of the immutable P020 component arrays."""
    dates(start, end)
    if ticker not in SYMBOLS or origin not in (1, 2) or version not in ("inner", "refit"):
        raise ValueError("P022 feature request denied")
    grid = study.table("grid")
    positions = np.flatnonzero(grid.session_date_et.between(start, end).to_numpy())
    if not len(positions):
        return pd.DataFrame()
    stop = int(positions.max()) + 1
    path = study.file(Path(study.contract["files"]["components"]["path"]).name)
    j = SYMBOLS.index(ticker)
    arrays = {
        (kind, suffix): prefix_array(path, f"{version}_{kind}_{suffix}", stop)[positions, j]
        for kind in ("native", "scaled", "fallback")
        for suffix in ("common", "m2")
    }
    recipe = study.recipe(version)
    frames = []
    for name in ORDER:
        suffix = "m2" if name == "M2" else "common"
        index = origin - 1 if name == "M2" else COMMON.index(name)
        native = arrays["native", suffix][:, index]
        scaled = arrays["scaled", suffix][:, index]
        center, scale = recipe["scalers"][name]["center"], recipe["scalers"][name]["scale"]
        filled = np.where(np.isfinite(native), native, recipe["fallbacks"][name])
        np.testing.assert_allclose((filled - center) / scale, scaled, rtol=2e-6, atol=2e-7)
        frames.append(
            pd.DataFrame(
                dict(
                    hour_end_utc=grid.hour_end_utc.iloc[positions].to_numpy(),
                    step=positions,
                    feature=name,
                    native=native,
                    scaled=scaled,
                    fallback=arrays["fallback", suffix][:, index],
                    center=center,
                    scale=scale,
                )
            )
        )
    return pd.concat(frames, ignore_index=True)
