"""Optional, separately approved conditional SPY U1–U5 preparation; never USA500 assent."""
from __future__ import annotations

import json
import math
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from .config import atomic_new, digest, fingerprint, write_json
from .ft0_transforms import robust_parameters
from .labels import FitWindow
from .market_features import (
    MarketHistory,
    MarketMeasures,
    history_from_archive,
    market_values,
    rms,
)
from .market_source import MarketSource, hourly_archive
from .pretraining_policy import PreparationAuthority, verify_ref
from .pretraining_source import BARRIER, COLUMNS
from .pretraining_store import serial
from .pretraining_tables import BaseTables
from .pretraining_transforms import CandidatePreparation


class ConditionalMarketHistory(MarketHistory):
    """Override access on the approved ideal clock; source objects remain UNKNOWN."""

    def _return(self, step) -> float | None:
        row = self.hours.get(step.end)
        if (row is None or row.period_end > step.end or row.period_end >= BARRIER
                or step.end - row.period_end > pd.Timedelta(minutes=90)):
            return None
        return math.log(row.close / row.open)

    def _close(self, day: str, cutoff: pd.Timestamp) -> float | None:
        row = self.closes.get(day)
        if row is None or row.period_end > cutoff or row.period_end >= BARRIER:
            return None
        return row.close


def ensure_annex(authority: PreparationAuthority, annex_ref: dict) -> dict:
    authority.ensure("FEATURE_TARGET_PREPARATION")
    annex = json.loads(verify_ref(authority.root, annex_ref).read_text())
    if (annex.get("decision_id") != "TA-G3-SPY-004-v1"
            or annex.get("status") not in {"APPROVED", "CONDITIONALLY_APPROVED"}
            or annex.get("authority_binding") != authority.binding
            or annex.get("actor_type") != "human"
            or not annex.get("response_text", "").strip()
            or annex.get("mode") != "ASSUMPTION_CONDITIONAL_CANDIDATE_ONLY"
            or annex.get("observed_publication_certified") is not False
            or annex.get("course_substitution_authorized") is not False
            or annex.get("collaborator_assent_verified") is not False
            or annex.get("model_fit_authorized") is not False):
        raise ValueError("SEPARATE_ACTUAL_CONDITIONAL_SPY_APPROVAL_REQUIRED")
    return annex


def load_conditional_spy(
    authority: PreparationAuthority, annex_ref: dict,
) -> tuple[ConditionalMarketHistory, dict]:
    ensure_annex(authority, annex_ref)
    source = MarketSource.load(authority.root / "configs/track_a_market_spy_v3.json")
    refs, frames = [], []
    lower = pd.Timestamp("2020-03-19", tz="America/New_York").tz_convert("UTC")
    for manifest in sorted(source.store.glob("*.manifest.json")):
        meta = json.loads(manifest.read_text())
        params = meta.get("params", {})
        if params.get("timeframe") != "30Min":
            continue
        data = manifest.with_suffix("").with_suffix(".parquet")
        if not data.exists() or digest(data) != meta.get("sha256"):
            raise ValueError("SPY_IMMUTABLE_ARCHIVE_MISMATCH")
        if any(params.get(k) != v for k, v in {"symbols": "SPY", "feed": "sip",
                "adjustment": "raw", "asof": "2025-06-30", "timeframe": "30Min"}.items()):
            raise ValueError("SPY_RAW_PRICE_REQUEST_MISMATCH")
        refs.append({"data": str(data.relative_to(authority.root)), "sha256": digest(data),
                     "manifest": str(manifest.relative_to(authority.root)),
                     "manifest_sha256": digest(manifest), "params": params})
        if pd.Timestamp(params["start"]) >= BARRIER:
            continue
        frame = pq.read_table(data, columns=COLUMNS,
                              filters=[("timestamp", ">=", lower.to_pydatetime()),
                                       ("timestamp", "<", BARRIER.to_pydatetime())]).to_pandas()
        if not frame.empty:
            frames.append(frame)
    if len(refs) != 11 or not frames:
        raise ValueError("EXACT_ELEVEN_EXISTING_SPY_ARCHIVES_REQUIRED")
    frame = pd.concat(frames, ignore_index=True)
    if frame.duplicated(["symbol", "timestamp"]).any() or (frame.timestamp >= BARRIER).any():
        raise ValueError("SPY_DUPLICATE_OR_CONFIRMATION_NUMERIC_ACCESS")
    hourly, qa = hourly_archive(frame, "2020-03-19", "2024-06-30")
    if qa["missing_source_bars"]:
        raise ValueError("SPY_MISSING_NATIVE_NO_IMPUTATION")
    from .m2 import ScheduledCalendar
    cal = ScheduledCalendar("2020-03-19", "2024-06-30")
    strict = history_from_archive(cal, hourly)
    conditional = ConditionalMarketHistory(cal, tuple(strict.hours.values()), strict.closes)
    return conditional, {"refs": refs, "identity": fingerprint(refs), "native_rows": len(frame),
                          "source_publication": "UNKNOWN", "source_action_verification": False,
                          "confirmation_numeric_rows": 0, "annex": annex_ref}


def conditional_vector(row: MarketMeasures, hourly: float, daily: float):
    values = (row.hourly_return, row.rms12, row.rms60, row.daily_rms63,
              row.momentum5, row.momentum20)
    if any(v is None for v in values):
        return None
    r, short, long, d, m5, m20 = values
    if r is None or short is None or long is None or d is None or m5 is None or m20 is None:
        raise AssertionError("UNREACHABLE_MARKET_VALUES")
    return market_values(r, short, long, d, m5, m20, hourly, daily)


def prepare_market(history: ConditionalMarketHistory, measures: tuple[MarketMeasures, ...],
                   window: FitWindow) -> dict:
    selected = [r for r in measures if window.start <= r.timestamp < window.stop]
    hp = [x for r in selected for x in (r.rms12, r.rms60) if x is not None and x > 0]
    # Daily RMS uses actual session-close keys, not six copies at hourly endpoints.
    daily_rows = []
    days = history.days
    for i, day in enumerate(days):
        close = history.closes.get(day)
        if close is None or not window.start <= close.period_end < window.stop:
            continue
        prices = [history._close(d, close.period_end) for d in days[max(0, i - 63):i + 1]]
        returns = tuple(math.log(b / a) if a is not None and b is not None else None
                        for a, b in zip(prices, prices[1:]))
        scale = rms(returns, 63, 60)
        if scale is not None and scale > 0:
            daily_rows.append((str(close.period_end), scale))
    if not hp or not daily_rows:
        raise ValueError("TRAIN_ONLY_POSITIVE_SPY_FLOORS_REQUIRED")
    hourly, daily = float(np.percentile(hp, 5)), float(np.percentile([x[1] for x in daily_rows], 5))
    raw = [conditional_vector(r, hourly, daily) for r in selected]
    valid = [r for r in raw if r is not None]
    if not valid:
        raise ValueError("TRAIN_ONLY_VALID_SPY_VECTORS_REQUIRED")
    a = np.asarray(valid)
    center, scale, method = [], [], []
    for i in range(5):
        c, s, m = robust_parameters(a[:, i])
        center.append(c)
        scale.append(s)
        method.append(m)
    return {"hourly_floor": hourly, "daily_floor": daily, "centers": center, "scales": scale,
            "methods": method, "window": serial(asdict(window)), "unique_market_rows": len(valid),
            "unique_daily_scale_rows": len(daily_rows), "five_stock_replication": False,
            "source_basis": "RAW_SPY_PRICE_ONLY_DISTRIBUTION_GAPS_NOT_TOTAL_RETURN",
            "observed_publication_certified": False, "NOT_FOR_TRAINING": True}


def run_market(base: BaseTables, preparations: dict[str, CandidatePreparation],
               annex_ref: dict, report: Path) -> dict:
    authority = base.history.authority
    history, source = load_conditional_spy(authority, annex_ref)
    measures = tuple(history.measures(s) for s in history.calendar.steps)
    recipes, masks = {}, []
    for key, stock in preparations.items():
        recipe = prepare_market(history, measures, stock.window)
        recipes[key] = recipe
        vectors = {r.timestamp: conditional_vector(r, recipe["hourly_floor"], recipe["daily_floor"])
                   for r in measures}
        for (day, origin), positions in sorted(base.origin_steps.items()):
            steps = [base.history.calendar.steps[p] for p in positions]
            mask = [vectors.get(s.end) is not None for s in steps]
            valid = mask[-1] and sum(mask) >= 46
            masks.append({"preparation": key, "session": day, "origin": origin,
                          "valid_market_steps": sum(mask), "endpoint_valid": mask[-1],
                          "market_input_admissible": valid, "market_mask": mask,
                          "own_step_age_seconds": 0, "designation": "ASSUMPTION_CONDITIONAL"})
    data = {"source": source, "measures": [serial(asdict(r)) for r in measures],
            "preparations": recipes, "masks": masks,
            "course_and_collaborator": "HOLD_EXTERNAL_ACKNOWLEDGMENTS_UNSUPPLIED",
            "MODEL_FIT_FORBIDDEN": True, "designation": "ASSUMPTION_CONDITIONAL_CANDIDATE_ONLY"}
    # One market observation per timestamp, one store. No five-stock source replication.
    import gzip
    path = report / "canonical_market_components.json.gz"
    atomic_new(path, gzip.compress(json.dumps(data, sort_keys=True,
                                               separators=(",", ":")).encode(), mtime=0))
    summary = {"canonical_store": {"path": str(path), "sha256": digest(path)},
               "source": source, "preparations": recipes,
               "matched_masks": {key: {"nominal": sum(r["preparation"] == key for r in masks),
                                          "market_valid": sum(r["preparation"] == key
                                          and r["market_input_admissible"] for r in masks)}
                                 for key in recipes},
               "scientific_training_ready": False, "candidate_preparation_computed": True}
    write_json(report / "conditional_market_retention.json", summary)
    return summary
