"""Once-per-session/slot features with explicit prior-session support masks."""

import json
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from lstm_data.hf20_s4_clock import endpoint

from ..stage012.calendar_schedule import MarketClock
from ..stage012.model_registry import SYMBOLS
from ..stage35.final_backtest_v4.market import minute
from .paths import PACKAGE, ROOT, canonical, digest, publish
from .scheduler import weekly_scan_dates
from .sources import RawDay, RawMarket

PAIRS = ((11, 5), (14, 8), (2, 15))


def statistic(a: np.ndarray, kind: str, minimum: int, axis: int = 0) -> np.ndarray:
    count = np.isfinite(a).sum(axis=axis)
    safe = np.where(np.isfinite(a), a, 0)
    mean = safe.sum(axis=axis) / np.maximum(count, 1)
    if kind == "mean":
        value = mean
    elif kind == "std":
        delta = np.where(np.isfinite(a), a - np.expand_dims(mean, axis), 0)
        value = np.sqrt((delta * delta).sum(axis=axis) / np.maximum(count - 1, 1))
    else:
        raise ValueError("STATISTIC_KIND")
    return np.where(count >= minimum, value, np.nan)


def divide(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.divide(
        a,
        b,
        out=np.full_like(a, np.nan, dtype=float),
        where=np.isfinite(a) & np.isfinite(b) & (b > 0),
    )


def logratio(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    ratio = divide(a, b)
    return np.log(ratio, out=np.full_like(ratio, np.nan), where=ratio > 0)


@dataclass(frozen=True)
class FeatureFrame:
    session: str
    slot: int
    origin: int
    decision: int
    endpoint: int
    latest_observation_end: int
    prior_available: int
    weekly_scan: bool
    values: dict[str, np.ndarray]
    pair_parameters: np.ndarray
    lineage: str

    def require_causal(self) -> None:
        if self.latest_observation_end + 2 > self.decision or self.prior_available > self.decision:
            raise ValueError("FEATURE_NOT_RECEIVED")


class FeatureBuilder:
    def __init__(self, clock: MarketClock):
        self.clock = clock
        self.weekly = weekly_scan_dates(clock)
        self.history: list[dict[str, np.ndarray]] = []
        self.factor = np.ones(20)
        self.history_hash = "RAW2020_GENESIS"
        self.prior_available = -1
        facts = json.loads(Path("configs/hf1m_p019_verified_event_facts_v1.json").read_text())
        self.splits: dict[str, list[tuple[int, float]]] = {}
        for row in facts["events"]:
            if row["kind"] == "SPLIT" and "2020-01-01" <= row["date"] <= "2024-12-31":
                self.splits.setdefault(row["date"], []).append(
                    (SYMBOLS.index(row["ticker"]), float(row["factor_denominator"]))
                )

    def history_array(self, key: str, n: int) -> np.ndarray:
        if len(self.history) < n:
            shape = (7, 20) if key.endswith("_slots") else (20,)
            return np.full((n, *shape), np.nan)
        return np.asarray([r[key] for r in self.history[-n:]])

    def begin(self, day: RawDay) -> None:
        for j, ratio in self.splits.get(day.date, []):
            self.factor[j] *= ratio

    def references(self) -> tuple[dict[str, np.ndarray], np.ndarray]:
        close = self.history_array("close", 126)
        ret = self.history_array("ret", 60)
        v20 = statistic(ret[-20:], "std", 16)
        v60 = statistic(ret, "std", 48)
        lo = self.history_array("low", 20)
        hi = self.history_array("high", 20)
        # An incomplete daily range is unknown, never a fabricated full-day extreme.
        h20 = np.where(np.isfinite(hi).all(axis=0), np.max(hi, axis=0), np.nan)
        l20 = np.where(np.isfinite(lo).all(axis=0), np.min(lo, axis=0), np.nan)
        refs = {
            "v20": v20,
            "v60": v60,
            "adv20": statistic(self.history_array("volume", 20), "mean", 16) * self.factor,
            "previous_close": close[-1],
            "j6minus1": logratio(close[-22], close[-126]),
            "j5": logratio(close[-1], close[-6]),
            "h20": h20,
            "l20": l20,
            "trend": divide(
                np.log(
                    divide(statistic(close[-20:], "mean", 16), statistic(close[-60:], "mean", 48))
                ),
                v60 * np.sqrt(20),
            ),
            "on10": statistic(self.history_array("overnight", 10), "mean", 10) * 10,
            "intra10": statistic(self.history_array("intraday", 10), "mean", 10) * 10,
            "on_scale": statistic(self.history_array("overnight", 60), "std", 48) * np.sqrt(10),
            "intra_scale": statistic(self.history_array("intraday", 60), "std", 48) * np.sqrt(10),
            "volume_rank": statistic(self.history_array("volume_z", 5), "mean", 5),
        }
        rv = self.history_array("rv10", 61)
        q = np.full(20, np.nan)
        for j in range(20):
            a = rv[:-1, j]
            a = a[np.isfinite(a)]
            if len(a) >= 48:
                q[j] = np.quantile(a, 0.2)
        refs["compression"] = np.where(
            np.isfinite(q) & np.isfinite(rv[-1]), (rv[-1] < q).astype(float), np.nan
        )
        refs["residual5"] = np.full(20, np.nan)
        for j in range(20):
            peers = np.delete(ret, j, axis=1)
            factor = statistic(peers, "mean", 11, axis=1)
            good = np.isfinite(ret[:, j]) & np.isfinite(factor)
            if good.sum() < 50 or not good[-5:].all():
                continue
            x, y = factor[good], ret[good, j]
            variance = np.var(x, ddof=1)
            if variance <= 1e-12:
                continue
            beta = np.cov(x, y, ddof=1)[0, 1] / variance
            residual = y - beta * x
            scale = np.std(residual, ddof=1) * np.sqrt(5)
            if scale > 1e-12:
                refs["residual5"][j] = (ret[-5:, j] - beta * factor[-5:]).sum() / scale
        pairs = np.full((3, 4), np.nan)
        for n, (i, j) in enumerate(PAIRS):
            x, y = np.log(close[-60:, j]), np.log(close[-60:, i])
            if not (np.isfinite(x).all() and np.isfinite(y).all()) or np.var(x) < 1e-12:
                continue
            beta = np.cov(x, y, ddof=1)[0, 1] / np.var(x, ddof=1)
            residual = y - beta * x
            scale = np.std(residual, ddof=1)
            r2 = float(np.corrcoef(x, y)[0, 1] ** 2)
            if 0.25 <= beta <= 4 and scale > 1e-4 and r2 >= 0.3:
                pairs[n] = beta, np.mean(residual), scale, r2
        return refs, pairs

    def frame(
        self, day: RawDay, slot: int, refs: dict[str, np.ndarray], pairs: np.ndarray
    ) -> FeatureFrame:
        offset = slot * 60
        end = 0 if slot == 0 else offset - 1
        if end >= len(day.starts):
            raise ValueError("CALENDAR_EXCLUDED_ORIGIN")
        # Every reference below is a slice of the completed/received prefix only.
        valid = day.valid[: end + 1]
        cl = np.where(valid, day.closes[: end + 1], np.nan) * self.factor
        op = np.where(valid[0], day.opens[0], np.nan) * self.factor
        current = cl[-1]
        r60 = logratio(
            current, op if offset == 60 else cl[-61] if offset >= 120 else np.full(20, np.nan)
        )
        r30 = logratio(current, cl[-31]) if offset >= 60 else np.full(20, np.nan)
        gap = logratio(op, refs["previous_close"])
        opening = logratio(cl[59], op) if offset >= 60 else np.full(20, np.nan)
        intra = logratio(current, op)
        sigma = statistic(self.history_array("r60_slots", 20)[:, slot, :], "std", 16)
        intra_sigma = statistic(self.history_array("intra_slots", 20)[:, slot, :], "std", 16)
        gap_sigma = statistic(self.history_array("gap", 20), "std", 16)
        recent = (
            np.where(
                valid[-60:].all(axis=0),
                np.nansum(
                    np.where(valid[-60:], day.volumes[max(0, end - 59) : end + 1], np.nan), axis=0
                )
                / self.factor,
                np.nan,
            )
            if offset >= 60
            else np.full(20, np.nan)
        )
        pastvol = self.history_array("volume_slots", 20)[:, slot, :]
        vz = np.full(20, np.nan)
        vmean = np.full(20, np.nan)
        for j in range(20):
            p = pastvol[:, j]
            p = p[np.isfinite(p)]
            if len(p) >= 16:
                vmean[j] = np.mean(p)
                med = np.median(np.log1p(p))
                mad = np.median(np.abs(np.log1p(p) - med)) * 1.4826
                if mad > 1e-12 and np.isfinite(recent[j]):
                    vz[j] = (np.log1p(recent[j]) - med) / mad
        # Avoid NaN diagonal arithmetic contaminating off-diagonal entries.
        peer_matrix = np.tile(r60, (20, 1))
        np.fill_diagonal(peer_matrix, np.nan)
        peers = statistic(peer_matrix, "mean", 11, axis=1)
        residual = r60 - peers
        residual_sigma = statistic(self.history_array("residual_slots", 20)[:, slot, :], "std", 16)
        hist_half = self.history_array("half_slots", 20)[:, slot, :]
        half_mean = statistic(hist_half, "mean", 16)
        half_se = statistic(hist_half, "std", 16) / np.sqrt(
            np.isfinite(hist_half).sum(axis=0).clip(1)
        )
        or_hi = np.full(20, np.nan)
        or_lo = np.full(20, np.nan)
        if offset >= 60:
            complete = valid[:30].all(axis=0)
            or_hi = np.where(complete, np.max(day.highs[:30], axis=0) * self.factor, np.nan)
            or_lo = np.where(complete, np.min(day.lows[:30], axis=0) * self.factor, np.nan)
        cumulative = np.where(
            valid.all(axis=0),
            np.where(valid, day.volumes[: end + 1], 0).sum(axis=0) / self.factor,
            np.nan,
        )
        cumulative_mean = statistic(
            self.history_array("cumulative_slots", 20)[:, slot, :], "mean", 16
        )
        values = {
            **refs,
            "price": current,
            "raw_price": np.where(valid[-1], day.closes[end], np.nan),
            "factor": self.factor.copy(),
            "r60": r60,
            "r30": r30,
            "r60_z": divide(r60, sigma),
            "gap": gap,
            "gap_z": divide(gap, gap_sigma),
            "first_hour": opening,
            "first_hour_z": divide(
                opening, statistic(self.history_array("first_hour", 20), "std", 16)
            ),
            "volume_ratio": divide(recent, vmean),
            "volume_z": vz,
            "recent_volume_genesis": recent,
            "residual": residual,
            "residual_z": divide(residual, residual_sigma),
            "cumulative_volume_genesis": cumulative,
            "cumulative_volume_ratio": divide(cumulative, cumulative_mean),
            "same_clock_z": divide(half_mean, half_se),
            "intraday": intra,
            "intraday_z": divide(intra, intra_sigma),
            "or_high": or_hi,
            "or_low": or_lo,
            "peer_count": np.full(20, np.isfinite(r60).sum()),
            "legacy_sign": np.sign(refs["j5"]),
        }
        origin = int(day.starts[0]) + offset
        observed_end = int(day.starts[end]) + 1
        origin_stamp = pd.Timestamp(origin * 60, unit="s", tz="UTC")
        if not isinstance(origin_stamp, pd.Timestamp):
            raise ValueError("INVALID_ORIGIN_TIMESTAMP")
        frame = FeatureFrame(
            day.date,
            slot,
            origin,
            observed_end + 2,
            minute(
                endpoint(
                    origin_stamp,
                    self.clock.calendar.loc[day.date :],
                )
            ),
            observed_end,
            self.prior_available,
            day.date in self.weekly,
            values,
            pairs.copy(),
            canonical((self.history_hash, day.source_hash, observed_end)),
        )
        frame.require_causal()
        return frame

    def finish(self, day: RawDay, frames: list[FeatureFrame]) -> None:
        op = np.where(day.valid[0], day.opens[0], np.nan) * self.factor
        close = np.where(day.valid[-1], day.closes[-1], np.nan) * self.factor
        previous = self.history[-1]["close"] if self.history else np.full(20, np.nan)
        ret = logratio(close, previous)
        coverage = day.valid.mean(axis=0)
        volume = np.where(
            coverage >= 0.98, np.where(day.valid, day.volumes, 0).sum(axis=0) / self.factor, np.nan
        )
        volume_z = np.full(20, np.nan)
        pv = self.history_array("volume", 60)
        for j in range(20):
            a = np.log1p(pv[:, j])
            a = a[np.isfinite(a)]
            if len(a) >= 48:
                med = np.median(a)
                mad = 1.4826 * np.median(np.abs(a - med))
                if mad > 1e-12 and np.isfinite(volume[j]):
                    volume_z[j] = (np.log1p(volume[j]) - med) / mad
        row = {
            "open": op,
            "close": close,
            "ret": ret,
            "gap": logratio(op, previous),
            "overnight": logratio(op, previous),
            "intraday": logratio(close, op),
            "high": np.where(
                day.valid.all(axis=0), np.max(day.highs, axis=0) * self.factor, np.nan
            ),
            "low": np.where(day.valid.all(axis=0), np.min(day.lows, axis=0) * self.factor, np.nan),
            "volume": volume,
            "volume_z": volume_z,
            "rv10": statistic(np.vstack([self.history_array("ret", 9), ret]), "std", 10),
            "first_hour": frames[1].values["first_hour"]
            if len(frames) > 1
            else np.full(20, np.nan),
        }
        for key, field in [
            ("r60_slots", "r60"),
            ("intra_slots", "intraday"),
            ("volume_slots", "recent_volume_genesis"),
            ("cumulative_slots", "cumulative_volume_genesis"),
        ]:
            a = np.full((7, 20), np.nan)
            for f in frames:
                a[f.slot] = f.values[field]
            row[key] = a
        res = np.full((7, 20), np.nan)
        half = np.full((7, 20), np.nan)
        for f in frames:
            a = f.values["r60"]
            peer = np.tile(a, (20, 1))
            np.fill_diagonal(peer, np.nan)
            res[f.slot] = a - statistic(peer, "mean", 11, axis=1)
            i = f.slot * 60
            k = i + 29
            if k < len(day.starts):
                half[f.slot] = logratio(
                    np.where(day.valid[k], day.closes[k], np.nan),
                    np.where(day.valid[i], day.opens[i], np.nan),
                )
        row["residual_slots"], row["half_slots"] = res, half
        self.history.append(row)
        self.history_hash = canonical((self.history_hash, day.source_hash))
        self.prior_available = int(day.starts[-1]) + 3


def build_cache() -> Path:
    from .registry import verify_registry

    registry = verify_registry()
    started = time.monotonic()
    market = RawMarket()
    builder = FeatureBuilder(market.clock)
    saved: list[FeatureFrame] = []
    for day in market.days():
        builder.begin(day)
        refs, pairs = builder.references()
        frames = [
            builder.frame(day, k, refs, pairs) for k in range(len(market.clock.origins(day.date)))
        ]
        if day.date >= "2021-01-01":
            saved.extend(frames)
        builder.finish(day, frames)
    sessions = len({f.session for f in saved})
    valid_prices = sum(np.isfinite(f.values["raw_price"]).sum() for f in saved)
    if len(saved) != 7014 or sessions != 1005 or valid_prices < len(saved) * 18:
        raise ValueError("INCOMPLETE_CALENDAR_OR_RECEIVED_PRICE_COVERAGE")
    names = sorted(saved[0].values)
    feature_code = {
        str(PACKAGE / name): digest(PACKAGE / name)
        for name in ("shared_features.py", "sources.py", "scheduler.py")
    }
    identity = canonical(
        {
            "feature_code": feature_code,
            "support_policy": digest(ROOT / "SOURCE_AND_SUPPORT_DEFAULTS_V1.json"),
            "sources": market.reads,
            "feature_version": "rapid-v1",
        }
    )
    root = ROOT / "cache" / identity
    root.mkdir(parents=True, exist_ok=False)
    np.savez_compressed(
        root / "features.npz",
        dates=np.asarray([f.session for f in saved]),
        slots=np.asarray([f.slot for f in saved], dtype=np.int8),
        origins=np.asarray([f.origin for f in saved]),
        decisions=np.asarray([f.decision for f in saved]),
        endpoints=np.asarray([f.endpoint for f in saved]),
        prior_available=np.asarray([f.prior_available for f in saved]),
        weekly=np.asarray([f.weekly_scan for f in saved]),
        values=np.stack([np.stack([f.values[k] for k in names]) for f in saved]),
        pairs=np.stack([f.pair_parameters for f in saved]),
        lineage=np.asarray([f.lineage for f in saved]),
    )
    size = (root / "features.npz").stat().st_size
    if size > 80 * 2**20:
        raise ValueError("SHARED_FEATURE_CACHE_HARD_LIMIT")
    publish(
        root / "manifest.json",
        {
            "identity": identity,
            "fields": names,
            "registry": registry["identity"],
            "feature_code": feature_code,
            "support_policy_sha256": digest(ROOT / "SOURCE_AND_SUPPORT_DEFAULTS_V1.json"),
            "source_reads": market.reads,
            "rows": len(saved),
            "bytes": size,
            "sessions": sessions,
            "calendar_opportunities": len(saved) * 20,
            "received_price_cells": int(valid_prices),
            "wall_seconds": time.monotonic() - started,
            "data_sha256": digest(root / "features.npz"),
            "last_market_date": "2024-12-31",
            "source_pass": "one shared feature preparation; no strategy outcomes/funding",
        },
    )
    return root


class FeatureCache:
    def __init__(self, root: Path):
        self.root = root
        self.manifest = json.loads((root / "manifest.json").read_text())
        if digest(root / "features.npz") != self.manifest["data_sha256"]:
            raise ValueError("FEATURE_CACHE_HASH")
        if (
            any(digest(Path(p)) != h for p, h in self.manifest["feature_code"].items())
            or digest(ROOT / "SOURCE_AND_SUPPORT_DEFAULTS_V1.json")
            != self.manifest["support_policy_sha256"]
        ):
            raise ValueError("FEATURE_LOGIC_DRIFT")
        with np.load(root / "features.npz", allow_pickle=False) as archive:
            self.data = {key: archive[key] for key in archive.files}
        self.by_date: dict[str, list[int]] = {}
        for i, day in enumerate(self.data["dates"]):
            self.by_date.setdefault(str(day), []).append(i)

    def frames(self, day: str) -> list[FeatureFrame]:
        frames = []
        for i in self.by_date.get(day, []):
            decision = int(self.data["decisions"][i])
            v = self.data["values"][i]
            values = {name: v[k] for k, name in enumerate(self.manifest["fields"])}
            for array in values.values():
                array.setflags(write=False)
            frames.append(
                FeatureFrame(
                    day,
                    int(self.data["slots"][i]),
                    int(self.data["origins"][i]),
                    decision,
                    int(self.data["endpoints"][i]),
                    decision - 2,
                    int(self.data["prior_available"][i]),
                    bool(self.data["weekly"][i]),
                    values,
                    self.data["pairs"][i],
                    str(self.data["lineage"][i]),
                )
            )
        return frames
