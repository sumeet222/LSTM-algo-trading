"""Opt-in historical candle geometry; never an empirical P2/P3/P4 permission."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .candle_cleanup import MODE, POLICY, CleanupView, PriceUnitSegment, cleanup
from .config import digest, fingerprint
from .fast_screen import verified_frame
from .p3_domain import UniverseSpec


@dataclass(frozen=True)
class EngineeringSelection:
    """Universe-injected P3/P4 geometry with a quarantined candle-only payload."""

    universe: UniverseSpec
    view: CleanupView
    profile_sha256: str
    source_manifest_sha256: str

    def cache_binding(
        self,
        *,
        floor_id: str | None = None,
        target_id: str | None = None,
        preparation_id: str | None = None,
    ) -> str:
        """Any profile/source/policy/order/fit identity change invalidates later caches."""
        return fingerprint(
            [
                self.profile_sha256,
                self.source_manifest_sha256,
                self.universe.universe_id,
                self.view.content_id,
                POLICY,
                floor_id,
                target_id,
                preparation_id,
            ]
        )

    def for_activity(self, activity: str) -> pd.DataFrame:
        if activity not in {"CANDLE_QA", "DATA_SHAPE"}:
            self.view.require_scientific(activity)
        return self.view.materialize_engineering(mode=MODE)


def load_engineering_profile(path: Path, *, mode: str) -> EngineeringSelection:
    """Load immutable references and sparse overlay binding without touching canonical defaults."""
    profile = json.loads(path.read_text())
    if (
        mode != MODE
        or profile["mode"] != MODE
        or profile["policy_id"] != POLICY
        or profile["scientific_activation"] is not False
        or not profile["universe_version"].startswith("ENG:")
        or not profile["code_bindings"]
    ):
        raise ValueError("EXPLICIT_QUARANTINED_ENGINEERING_PROFILE_REQUIRED")
    manifest_path = Path(profile["source_manifest"])
    if manifest_path.is_absolute() or ".." in manifest_path.parts:
        raise ValueError("PORTABLE_ENGINEERING_SOURCE_REFERENCE_REQUIRED")
    if digest(manifest_path) != profile["source_manifest_sha256"]:
        raise ValueError("ENGINEERING_SOURCE_MANIFEST_CHANGED")
    for entry in profile["code_bindings"]:
        code = Path(entry["path"])
        if code.is_absolute() or ".." in code.parts or digest(code) != entry["sha256"]:
            raise ValueError("ENGINEERING_PROFILE_CODE_CHANGED_REBUILD_REQUIRED")
    source = json.loads(manifest_path.read_text())
    universe = UniverseSpec(
        profile["universe_version"],
        tuple(profile["symbols"]),
        tuple((r["symbol"], r["sector"]) for r in profile["sectors"]),
    )
    if tuple(source["ordered_universe"]) != universe.symbols:
        raise ValueError("ENGINEERING_ORDERED_SOURCE_POPULATION_REQUIRED")
    frames = {}
    for rows in source["source_by_stock"].values():
        for ref in rows:
            if ref["data"] not in frames:
                frames[ref["data"]] = verified_frame(ref)
    stocks = []
    for symbol in universe.symbols:
        per = [
            frames[r["data"]][frames[r["data"]].symbol == symbol]
            for r in source["source_by_stock"][symbol]
        ]
        stocks.append(pd.concat(per, ignore_index=True).sort_values("timestamp"))
    native = pd.concat(stocks, ignore_index=True)
    segments = tuple(
        PriceUnitSegment(
            r["symbol"],
            pd.Timestamp(r["start"]),
            pd.Timestamp(r["stop"]),
            r["unit_id"],
            r["verified"],
            r["evidence_ref"],
        )
        for r in profile["price_unit_segments"]
    )
    view = cleanup(
        native,
        universe.symbols,
        profile["start"],
        profile["stop"],
        profile_id=profile["universe_version"],
        source_binding=profile["source_manifest_sha256"],
        segments=segments,
    )
    return EngineeringSelection(universe, view, digest(path), digest(manifest_path))
