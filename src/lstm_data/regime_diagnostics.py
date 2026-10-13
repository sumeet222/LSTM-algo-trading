"""Synthetic RS1/MC2 arithmetic only; no historical activation or fitting executor."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .baseline_fit import Preparation
from .baseline_inputs import BaselineInput
from .calendar import schedule
from .clocks import utc
from .config import digest
from .ft0_transforms import identity
from .market_features import MarketScaler, MarketWindow
from .neural_market import MarketEvidence, MarketStamp, market_input
from .p3_domain import Permission, synthetic_id


def diagnostic_code_identity() -> str:
    """Code changes require new evidence, independently of a source version label."""
    return identity(
        [
            digest(Path(__file__)),
            digest(Path(__file__).with_name("neural_market.py")),
            digest(Path(__file__).with_name("market_features.py")),
            digest(Path(__file__).with_name("ft0_transforms.py")),
            digest(Path(__file__).with_name("m2.py")),
        ]
    )


@dataclass(frozen=True)
class U2Threshold:
    """Median of standardized, unique training times under an existing SYN scaler."""

    value: float
    scaler_id: str
    source_version: str
    fitted_at: pd.Timestamp
    training_trace: str

    def __post_init__(self) -> None:
        if not math.isfinite(self.value) or not self.training_trace or not self.scaler_id:
            raise ValueError("BOUND_FINITE_TRAINING_U2_MEDIAN_REQUIRED")
        synthetic_id(self.source_version)
        utc(self.fitted_at)

    @property
    def threshold_id(self) -> str:
        return identity([diagnostic_code_identity(), self])


def training_threshold(
    history: MarketEvidence, scaler: MarketScaler, permission: Permission
) -> U2Threshold:
    """No new scaler fit; summarize precisely its already fitted timestamp population."""
    permission.ensure()
    history.validate()
    if scaler.basis != "SYNTHETIC" or scaler.window.phase not in {"INNER_TRAIN", "REFIT"}:
        raise ValueError("SYNTHETIC_TRAINING_THRESHOLD_ONLY")
    if utc(scaler.window.fitted_at) < utc(scaler.window.stop):
        raise ValueError("THRESHOLD_FIT_BEFORE_TRAINING_STOP")
    lookup = {v.timestamp: v for v in history.vectors}
    values = []
    for at in sorted(scaler.timestamps):
        raw = lookup.get(at)
        if (
            raw is None
            or raw.values is None
            or raw.reason != "VECTOR_VALID"
            or not scaler.window.contains(at)
        ):
            raise ValueError("EXACT_TRAINING_THRESHOLD_POPULATION_REQUIRED")
        values.append(scaler.transform(raw.values)[0][1])
    return U2Threshold(
        float(np.median(values)),
        identity(scaler),
        history.version,
        utc(scaler.window.fitted_at),
        identity([scaler.window, sorted(scaler.timestamps), values, history.evidence_id]),
    )


@dataclass(frozen=True)
class DiagnosticWindow:
    """Bound already-standardized 48-step synthetic input, never raw prices or labels.

    Production-facing callers use diagnostic_window(), which reuses all P2/P4
    stock, fit and publication checks. Direct construction is a synthetic oracle.
    """

    session: str
    origin: int
    market: MarketWindow
    stamps: tuple[MarketStamp, ...]
    source_version: str
    input_trace: str
    phase: str

    def __post_init__(self) -> None:
        synthetic_id(self.source_version)
        day = pd.Timestamp(self.session, tz="America/New_York")
        if day < pd.Timestamp("2020-07-01", tz="America/New_York") or day >= pd.Timestamp(
            "2024-07-01", tz="America/New_York"
        ):
            raise ValueError("CONFIRMATION_OR_PRETRAINING_DIAGNOSTIC_NOT_AUTHORIZED")
        if self.phase == "TRAINING" and day >= pd.Timestamp("2023-07-01", tz="America/New_York"):
            raise ValueError("MC2_TRAINING_POPULATION_REQUIRED")
        m = self.market
        if (
            self.origin not in (1, 2)
            or self.phase not in {"TRAINING", "DISCLOSURE"}
            or not self.input_trace
            or m.research_ready
            or m.values is None
            or len(m.values) != 48
            or len(m.valid_mask) != 48
            or len(m.scheduled_ends) != 48
            or len(m.source_ids) != 48
            or len(self.stamps) != 48
            or not m.valid_mask[-1]
            or sum(m.valid_mask) < 46
            or not m.scaler_ref
            or not m.floor_ref
            or len(set(m.scheduled_ends)) != 48
        ):
            raise ValueError("ADMITTED_48_STEP_D7_DIAGNOSTIC_REQUIRED")
        from .m2 import ScheduledCalendar, scheduled_window

        first = utc(m.scheduled_ends[0]).tz_convert("America/New_York").date().isoformat()
        steps = scheduled_window(ScheduledCalendar(first, self.session), self.session, self.origin)
        if m.scheduled_ends != tuple(s.end for s in steps):
            raise ValueError("DIAGNOSTIC_EXACT_SCHEDULED_KEYS_REQUIRED")
        for at, vector, valid, source, stamp in zip(
            m.scheduled_ends, m.values, m.valid_mask, m.source_ids, self.stamps
        ):
            if (
                type(valid) is not bool
                or len(vector) != 5
                or not all(math.isfinite(v) for v in vector)
                or utc(stamp.timestamp) != utc(at)
                or stamp.evidence_ids != source
            ):
                raise ValueError("DIAGNOSTIC_VECTOR_MASK_SOURCE_REQUIRED")
            if valid:
                if stamp.period_end is None or stamp.available_at is None or not source:
                    raise ValueError("DIAGNOSTIC_PUBLICATION_UNKNOWN")
                end, available = utc(stamp.period_end), utc(stamp.available_at)
                if (
                    not end <= available <= utc(at)
                    or not 0 <= (utc(at) - end).total_seconds() <= 5400
                ):
                    raise ValueError("DIAGNOSTIC_FUTURE_OR_STALE_PUBLICATION")
                for source_id in source:
                    synthetic_id(source_id)
            elif vector != (0.0,) * 5 or source:
                raise ValueError("INVALID_MARKET_STEP_MUST_REMAIN_NEUTRAL_MASKED")

    @property
    def key(self) -> tuple[str, int]:
        return self.session, self.origin

    @property
    def window_id(self) -> str:
        return identity(["SYN:RS1_MC2:1", diagnostic_code_identity(), self])


def diagnostic_window(
    row: BaselineInput,
    prep: Preparation,
    history: MarketEvidence,
    permission: Permission,
    *,
    phase: str,
    context: str = "ASOF",
) -> DiagnosticWindow:
    processed, trace = market_input(row, prep, history, permission, context)
    assert processed.market is not None
    lookup = {s.timestamp: s for s in history.stamps}
    return DiagnosticWindow(
        row.plan.session,
        row.plan.origin,
        processed.market,
        tuple(lookup[s.end] for s in row.stock.steps),
        history.version,
        trace,
        phase,
    )


@dataclass(frozen=True)
class Regime:
    key: tuple[str, int]
    trend: str
    volatility: str
    window_id: str
    threshold_id: str
    cutoff: pd.Timestamp | None = None

    def __post_init__(self) -> None:
        if (
            self.key[1] not in (1, 2)
            or self.trend not in {"BULL", "BEAR", "NEUTRAL"}
            or self.volatility not in {"HIGH", "LOW"}
            or not self.window_id
            or not self.threshold_id
        ):
            raise ValueError("BOUND_CAUSAL_REGIME_STATE_REQUIRED")
        if self.cutoff is not None:
            utc(self.cutoff)


def classify(window: DiagnosticWindow, threshold: U2Threshold) -> Regime:
    if (
        window.market.scaler_ref != threshold.scaler_id
        or window.source_version != threshold.source_version
        or utc(threshold.fitted_at) > utc(window.market.scheduled_ends[-1])
    ):
        raise ValueError("REGIME_TRAINING_THRESHOLD_ASOF_BINDING_REQUIRED")
    assert window.market.values is not None
    u2, u5 = window.market.values[-1][1], window.market.values[-1][4]
    trend = "BULL" if u5 > 0 else "BEAR" if u5 < 0 else "NEUTRAL"
    return Regime(
        window.key,
        trend,
        "HIGH" if u2 > threshold.value else "LOW",
        window.window_id,
        threshold.threshold_id,
        utc(window.market.scheduled_ends[-1]),
    )


def occupancy(states: tuple[Regime, ...], scheduled_sessions: tuple[str, ...]) -> dict:
    """First eligible origin anchors a session; missing scheduled days break episodes."""
    if (
        not scheduled_sessions
        or len(set(scheduled_sessions)) != len(scheduled_sessions)
        or scheduled_sessions != tuple(sorted(scheduled_sessions))
        or scheduled_sessions
        != tuple(
            str(d.date()) for d in schedule(scheduled_sessions[0], scheduled_sessions[-1]).index
        )
    ):
        raise ValueError("EXACT_CONTIGUOUS_XNYS_SESSION_DENOMINATOR_REQUIRED")
    if (
        len({s.key for s in states}) != len(states)
        or any(s.key[0] not in scheduled_sessions or s.key[1] not in (1, 2) for s in states)
        or len({s.threshold_id for s in states}) > 1
    ):
        raise ValueError("UNIQUE_MATCHED_REGIME_ORIGINS_REQUIRED")
    by_day: dict[str, list[Regime]] = {}
    for state in sorted(states, key=lambda s: s.key):
        by_day.setdefault(state.key[0], []).append(state)
    anchors = {day: rows[0] for day, rows in by_day.items()}
    summary = {}
    for family, labels in (
        ("trend", ("BULL", "BEAR", "NEUTRAL")),
        ("volatility", ("HIGH", "LOW")),
        ("joint", ("BULL_HIGH", "BULL_LOW", "BEAR_HIGH", "BEAR_LOW")),
    ):
        for label in labels:
            count = episodes = 0
            previous = False
            for day in scheduled_sessions:
                state = anchors.get(day)
                current = (
                    None
                    if state is None
                    else (
                        state.trend
                        if family == "trend"
                        else state.volatility
                        if family == "volatility"
                        else state.trend + "_" + state.volatility
                    )
                )
                hit = current == label
                count += int(hit)
                episodes += int(hit and not previous)
                previous = hit
            summary[family + ":" + label] = {
                "sessions": count,
                "episodes": episodes,
                "support": "SUPPORTED_DESCRIPTIVE_ONLY"
                if count >= 30 and episodes >= 3
                else "SPARSE_EXPLORATORY_ONLY",
                "inference": "NO_INFERENCE",
            }
    return {
        "scheduled_sessions": len(scheduled_sessions),
        "eligible_sessions": len(anchors),
        "unavailable_sessions": len(scheduled_sessions) - len(anchors),
        "origin_observations": len(states),
        "states": summary,
        "per_origin": {
            str(o): {
                "observations": sum(s.key[1] == o for s in states),
                "trend": {
                    v: sum(s.key[1] == o and s.trend == v for s in states)
                    for v in ("BULL", "BEAR", "NEUTRAL")
                },
                "volatility": {
                    v: sum(s.key[1] == o and s.volatility == v for s in states)
                    for v in ("HIGH", "LOW")
                },
            }
            for o in (1, 2)
        },
        "anchors": {d: s.key[1] for d, s in anchors.items()},
        "within_day_changes": [
            d for d, rows in by_day.items() if len({(s.trend, s.volatility) for s in rows}) > 1
        ],
    }


def variation(window: DiagnosticWindow) -> dict:
    assert window.market.values is not None
    endpoint = window.market.values[-1]
    changes = sum(
        valid and max(abs(v[k] - endpoint[k]) for k in (1, 2, 3, 4)) >= 1
        for v, valid in zip(window.market.values, window.market.valid_mask)
    )
    n = sum(window.market.valid_mask)
    return {
        "key": window.key,
        "window_id": window.window_id,
        "valid_steps": n,
        "changed_steps": changes,
        "A_t": changes / n,
        "qualifies": changes / n >= 0.25,
    }


def mc2_readiness(windows: tuple[DiagnosticWindow, ...]) -> dict:
    if (
        not windows
        or len({w.key for w in windows}) != len(windows)
        or any(w.phase != "TRAINING" for w in windows)
        or len({(w.source_version, w.market.scaler_ref, w.market.floor_ref) for w in windows}) != 1
    ):
        raise ValueError("UNIQUE_MATCHED_TRAINING_WINDOWS_REQUIRED")
    results = [variation(w) for w in sorted(windows, key=lambda w: w.key)]
    selected = [r for r in results if r["qualifies"]]
    sessions = sorted({r["key"][0] for r in selected})
    return {
        "eligible_windows": len(results),
        "qualifying_windows": len(selected),
        "qualifying_sessions": sessions,
        "fraction": len(selected) / len(results),
        "synthetic_structural_condition": 5 * len(selected) >= len(results) and len(sessions) >= 20,
        "windows": results,
        "scientific_status": "SCIENTIFIC_NOT_ASSESSED",
        "activation": "MC2_NOT_ACTIVATED",
    }


@dataclass(frozen=True)
class PairedRecord:
    """Already issued fabricated scores and separately matured fabricated outcomes."""

    architecture: str
    state: Regime
    scores: tuple[float, ...]
    labels: tuple[float, ...]
    source_id: str
    target_id: str
    fit_id: str
    fitted_at: pd.Timestamp
    cutoff: pd.Timestamp
    issued_at: pd.Timestamp
    maturity: pd.Timestamp
    evaluated_at: pd.Timestamp
    gate_weights: tuple[float, ...] | None = None

    def validate(self) -> None:
        if (
            self.architecture not in {"MC0", "MC1"}
            or len(self.scores) != 5
            or len(self.labels) != 5
            or not all(math.isfinite(v) for v in self.scores + self.labels)
        ):
            raise ValueError("FIVE_FINITE_SYNTHETIC_PAIRED_VALUES_REQUIRED")
        if self.gate_weights is not None and (
            self.architecture != "MC1"
            or len(self.gate_weights) != 16
            or not all(math.isfinite(v) and v > 0 for v in self.gate_weights)
            or abs(sum(self.gate_weights) - 16) > 2e-6
        ):
            raise ValueError("VALID_EXISTING_MC1_GATE_REQUIRED")
        for ref in (self.source_id, self.target_id, self.fit_id):
            synthetic_id(ref)
        if self.state.cutoff is None or utc(self.state.cutoff) != utc(self.cutoff):
            raise ValueError("PAIRED_STATE_CUTOFF_MISMATCH")
        if not (
            utc(self.fitted_at)
            <= utc(self.cutoff)
            <= utc(self.issued_at)
            < utc(self.maturity)
            <= utc(self.evaluated_at)
        ):
            raise ValueError("PAIRED_ISSUANCE_MATURITY_NO_FUTURE_OUTCOME_ACCESS_REQUIRED")


def paired_report(records: tuple[PairedRecord, ...]) -> dict:
    """MSE arithmetic oracle only; shared approved rank/economic metrics are deferred."""
    rows: dict[tuple[str, int], dict[str, PairedRecord]] = {}
    for record in records:
        record.validate()
        pair = rows.setdefault(record.state.key, {})
        if record.architecture in pair:
            raise ValueError("DUPLICATE_PAIRED_DIAGNOSTIC")
        pair[record.architecture] = record
    output = []
    for key, pair in sorted(rows.items()):
        if set(pair) != {"MC0", "MC1"}:
            raise ValueError("MISSING_PAIRED_DIAGNOSTIC")
        a, b = pair["MC0"], pair["MC1"]

        def binding(r: PairedRecord) -> tuple:
            return (
                r.state,
                r.labels,
                r.source_id,
                r.target_id,
                r.fit_id,
                utc(r.fitted_at),
                utc(r.cutoff),
                utc(r.issued_at),
                utc(r.maturity),
                utc(r.evaluated_at),
            )

        if binding(a) != binding(b):
            raise ValueError("PAIRED_SOURCE_LABEL_FIT_CLOCK_STATE_MISMATCH")
        mse = [sum((s - y) ** 2 for s, y in zip(r.scores, r.labels)) / 5 for r in (a, b)]
        output.append(
            {"key": key, "MC0_MSE": mse[0], "MC1_MSE": mse[1], "delta_MSE": mse[1] - mse[0]}
        )
    slices = {}
    for family in ("trend", "volatility"):
        labels = ("BULL", "BEAR", "NEUTRAL") if family == "trend" else ("HIGH", "LOW")
        for label in labels:
            selected = [r for r in output if getattr(rows[r["key"]]["MC0"].state, family) == label]
            slice_days = sorted({r["key"][0] for r in selected})
            slices[family + ":" + label] = {
                "origins": len(selected),
                "sessions": len(slice_days),
                "delta_MSE": float(
                    np.mean(
                        [
                            np.mean([r["delta_MSE"] for r in selected if r["key"][0] == d])
                            for d in slice_days
                        ]
                    )
                )
                if slice_days
                else None,
                "inference": "NO_INFERENCE",
            }
    gates = [r.gate_weights for r in records if r.gate_weights is not None]
    gate_summary = None
    if gates:
        import torch

        from .neural_models import gate_diagnostics

        gate_summary = gate_diagnostics(torch.tensor(gates, dtype=torch.float32))
    days = sorted({r["key"][0] for r in output})
    daily = [
        sum(r["delta_MSE"] for r in output if r["key"][0] == day)
        / sum(r["key"][0] == day for r in output)
        for day in days
    ]
    return {
        "origins": output,
        "daily_mean_delta_MSE": float(np.mean(daily)) if daily else None,
        "rank_IC": "APPROVED_IMPLEMENTATION_ABSENT_DEFERRED",
        "top_bottom_accuracy": "APPROVED_IMPLEMENTATION_ABSENT_DEFERRED",
        "slices": slices,
        "gate_summary": gate_summary if gate_summary else "NOT_AVAILABLE",
        "net_cost": "NOT_AVAILABLE",
        "inference": "NO_INFERENCE",
    }
