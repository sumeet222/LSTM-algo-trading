"""Original cached magnitudes and sign-independent strictly matured controls.

No torch, auxiliary sign, F09, outcome-completeness filter or neural inference.
"""

import time
from decimal import Decimal

import numpy as np
import pandas as pd

from ..rapid_exit_audit.io import as_rows, column
from ..rapid_v1.paths import canonical, digest, publish
from ..stage012.model_registry import SYMBOLS
from .common import BUNDLES, CACHE, COVERAGE, RISK, ROOT, load, verify_inputs

ARMS = ("EQUAL", "ROLLING_RISK", "EWMA_RISK", "S2C_RISK")


def control(sample: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    count = np.isfinite(sample).sum(axis=0)
    med, rms = np.full(sample.shape[1], np.nan), np.full(sample.shape[1], np.nan)
    valid = (count == len(sample)) & (count >= 40)
    if np.any(valid):
        x = abs(sample[:, valid])
        med[valid] = np.median(x, axis=0)
        v = x[0] ** 2
        for r in x[1:]:
            v = 0.94 * v + 0.06 * r**2
        rms[valid] = np.sqrt(v)
    return med, rms, count


def factor(b: np.ndarray, floor: np.ndarray, scale: np.ndarray) -> np.ndarray:
    ready = (
        np.isfinite(b)
        & np.isfinite(floor)
        & np.isfinite(scale)
        & (b > 0)
        & (floor > 0)
        & (scale >= 0)
    )
    g = np.full(len(b), np.nan)
    g[ready] = np.clip(b[ready] / np.maximum(scale[ready], floor[ready]), 0.5, 1.5)
    return g


def build() -> None:
    verify_inputs()
    start = time.monotonic()
    report = load(COVERAGE)
    ref = load(RISK)
    actual = canonical(ref["payload"])
    # This payload's historical SHA uses compact JSON, unlike the generic helper.
    import hashlib
    import json

    exact = hashlib.sha256(
        json.dumps(ref["payload"], sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if exact != "5c453193572a2e428c561249c842c90a3d36041736183195f3e1dc6a350b6681":
        raise ValueError("ORIGINAL_PREFIX_REFERENCE_IDENTITY")
    refs = {(r["fold"], r["ticker"], r["slot"]): r for r in ref["payload"]["records"]}
    bundle = load(BUNDLES)["bundles"]
    cols = [
        "origin",
        "ticker",
        "fold",
        "input_eligible",
        "magnitude_c3",
        "issued_at",
        "source_latest_completed",
        "checkpoint_hash",
        "recipe_hash",
        "c3_hash",
    ]
    parts = []
    for item in report["partitions"]:
        p = item["path"]
        if digest(__import__("pathlib").Path(p)) != item["sha256"]:
            raise ValueError("ORIGINAL_SIGNAL_HASH")
        d = pd.read_parquet(p, columns=cols)
        fold = str(d["fold"].iloc[0])
        year = str(2000 + int(fold[1:]))
        for field, expected in zip(
            ("checkpoint_hash", "recipe_hash", "c3_hash"), bundle[year]["sha256"][:3], strict=True
        ):
            if set(column(d, field)) != {expected}:
                raise ValueError("ORIGINAL_BUNDLE_SIGNAL_BINDING")
        parts.append(d)
    frame = pd.concat(parts, ignore_index=True)
    if len(frame) != 140280 or int(column(frame, "input_eligible").sum()) != 131111:
        raise ValueError("ORIGINAL_INPUT_FORECAST_CENSUS")
    origin = pd.DatetimeIndex(column(frame, "origin")).as_unit("ns").asi8 // 60_000_000_000
    issued = pd.DatetimeIndex(column(frame, "issued_at")).as_unit("ns").asi8 // 60_000_000_000
    observed = (
        pd.DatetimeIndex(column(frame, "source_latest_completed")).as_unit("ns").asi8
        // 60_000_000_000
    )
    unique = np.unique(origin)
    index = {int(x): n for n, x in enumerate(unique)}
    size = (len(unique), 20)
    magnitude = np.full(size, np.nan)
    available = np.full(size, -1, dtype=np.int64)
    b = np.full(size, np.nan)
    floor = np.full(size, np.nan)
    from datetime import datetime, timezone

    for n, r in enumerate(as_rows(frame)):
        i = index[int(origin[n])]
        j = SYMBOLS.index(r.ticker)
        slot = (
            datetime.fromtimestamp(int(origin[n]) * 60, timezone.utc)
            .astimezone(__import__("zoneinfo").ZoneInfo("America/New_York"))
            .strftime("%H:%M")
        )
        rr = refs[(r.fold, r.ticker, slot)]
        if rr["status"] == "READY":
            b[i, j], floor[i, j] = rr["b"], rr["m_floor"]
        if r.input_eligible:
            value = float(r.magnitude_c3)
            if not np.isfinite(value) or value < 0:
                raise ValueError("INVALID_ORIGINAL_MAGNITUDE")
            magnitude[i, j] = value
            available[i, j] = max(int(issued[n]), int(observed[n]) + 2)
    geo = pd.read_parquet(CACHE / "movement_geometry.parquet")
    end = (pd.DatetimeIndex(column(geo, "exit_end_utc")).as_unit("ns").asi8 // 60_000_000_000) + 2
    moves = np.load(CACHE / "matured_source_moves.npy", mmap_mode="r")
    slots = column(geo, "slot").to_numpy(str)
    rolling = np.full(size, np.nan)
    ewma = np.full(size, np.nan)
    counts = np.zeros(size, np.int16)
    latest = np.full(len(unique), -1, np.int64)
    windows = np.zeros(len(unique), np.int16)
    for i, t in enumerate(unique):
        slot = (
            datetime.fromtimestamp(int(t) * 60, timezone.utc)
            .astimezone(__import__("zoneinfo").ZoneInfo("America/New_York"))
            .strftime("%H:%M")
        )
        decision = int(t) + 2 if slot != "09:30" else int(t) + 3
        eligible = np.flatnonzero((slots == slot) & (end < decision))[-60:]
        windows[i] = len(eligible)
        if len(eligible):
            rolling[i], ewma[i], counts[i] = control(np.asarray(moves[eligible]))
            latest[i] = int(end[eligible[-1]])
            if latest[i] >= decision:
                raise ValueError("UNMATURED_CONTROL")
    g = np.ones((*size, 4))
    g[:, :, 1] = factor(b.ravel(), floor.ravel(), rolling.ravel()).reshape(size)
    g[:, :, 2] = factor(b.ravel(), floor.ravel(), ewma.ravel()).reshape(size)
    g[:, :, 3] = factor(b.ravel(), floor.ravel(), magnitude.ravel()).reshape(size)
    path = ROOT / "SIGN_INDEPENDENT_RISK_INPUTS.npz"
    with path.open("xb") as f:
        np.savez_compressed(
            f,
            origin=unique,
            g=g,
            magnitude=magnitude,
            b=b,
            floor=floor,
            available=available,
            control_latest=latest,
            control_count=counts,
            control_window=windows,
            rolling=rolling,
            ewma=ewma,
        )
    publish(
        ROOT / "RISK_INPUT_READINESS.json",
        {
            "status": "PASS",
            "rows": len(frame),
            "original_forecasts": int(np.isfinite(magnitude).sum()),
            "origins": len(unique),
            "counts": {arm: int(np.isfinite(g[:, :, j]).sum()) for j, arm in enumerate(ARMS)},
            "cache_sha256": digest(path),
            "cache_bytes": path.stat().st_size,
            "prefix_payload_hash": exact,
            "prefix_canonical_hash": actual,
            "original_source_manifest_sha256": digest(COVERAGE),
            "sign_mask_used": False,
            "future_endpoint_eligibility_filter": False,
            "classical_source": "strictly matured original move tape; no missing pooling",
            "wall_seconds": time.monotonic() - start,
        },
    )


class RiskInputs:
    def __init__(self):
        path = ROOT / "SIGN_INDEPENDENT_RISK_INPUTS.npz"
        if digest(path) != load(ROOT / "RISK_INPUT_READINESS.json")["cache_sha256"]:
            raise ValueError("RISK_CACHE_HASH")
        self.data = dict(np.load(path, allow_pickle=False))
        self.index = {int(t): i for i, t in enumerate(self.data["origin"])}

    def values(self, origin: int, decision: int) -> np.ndarray:
        i = self.index.get(origin)
        if i is None:
            return np.full((20, 4), np.nan)
        values = self.data["g"][i].copy()
        values[self.data["available"][i] > decision, 3] = np.nan
        if self.data["control_latest"][i] >= decision:
            values[:, 1:3] = np.nan
        return values

    def multiplier(
        self, origin: int, decision: int, ticker: int, arm: str, population: str
    ) -> Decimal | None:
        g = self.values(origin, decision)
        if population == "MATCHED" and not np.isfinite(g[ticker]).all():
            return None
        value = g[ticker, ARMS.index(arm)]
        return Decimal(str(float(value))) if np.isfinite(value) else None


if __name__ == "__main__":
    build()
