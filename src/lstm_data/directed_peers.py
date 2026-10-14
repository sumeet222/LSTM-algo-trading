"""D8 synthetic formation and clock-bound directed signals; real H/L on HOLD.

No source loader, fitted transform, empirical authority or LL neural family.
The extra predecessor is explicit: missing lag48 can never be padded.
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from .baseline_cache import canonical_apply
from .baseline_fit import Preparation
from .baseline_inputs import BaselineInput
from .baseline_ridge import LAGS
from .calendar import schedule
from .clocks import utc
from .config import digest
from .ft0_transforms import Context, identity
from .m2 import ScheduledCalendar, ScheduledStep
from .neural_market import MarketEvidence
from .p3_domain import MODE, Permission, UniverseSpec, synthetic_id
from .peer_inputs import M1_INDEX, peer_input, peer_summaries
from .ridge_extension import metadata_identity

SIGNAL_ORDER = ("H_TO_L_0", "H_TO_L_1", "L_TO_H_0", "L_TO_H_1", "PEER_MEAN_1")
FLAG_ORDER = ("TARGET_IS_H", "TARGET_IS_L")
VERSION = "SYN:D8_DIRECTED:1"

if TYPE_CHECKING:
    from .baseline_fit import FitData
    from .baseline_ridge import Stage
    from .directed_ridge import DirectedArchive, MatchedFits


def _finite(value: float | None) -> float:
    if value is None or not math.isfinite(value):
        raise ValueError("FINITE_ORIGINAL_M1_REQUIRED")
    return value


def _published(at: pd.Timestamp | None) -> pd.Timestamp:
    if at is None:
        raise ValueError("M1_PUBLICATION_REQUIRED")
    return utc(at)


@dataclass(frozen=True)
class FormationRow:
    symbol: str
    session: str
    close: float
    volume: float
    available_at: pd.Timestamp
    source_id: str
    units_verified: bool = True


@dataclass(frozen=True)
class FormationPair:
    """Qualified fictional identities; hash the full60×5 table, not just its rank."""

    universe: UniverseSpec
    highest: str
    lowest: str
    means: tuple[float, ...]
    table_sha: str
    decision_at: pd.Timestamp
    qualification: str = "SYNTHETIC_FORMATION_ONLY"

    def validate(self) -> None:
        synthetic_id(self.universe.version)
        if (
            self.qualification != "SYNTHETIC_FORMATION_ONLY"
            or len(self.means) != 5
            or len(self.table_sha) != 64
            or not all(math.isfinite(x) and x > 0 for x in self.means)
            or self.highest not in self.universe.symbols
            or self.lowest not in self.universe.symbols
            or self.highest == self.lowest
            or self.means.count(max(self.means)) != 1
            or self.means.count(min(self.means)) != 1
            or self.universe.symbols[self.means.index(max(self.means))] != self.highest
            or self.universe.symbols[self.means.index(min(self.means))] != self.lowest
            or utc(self.decision_at) != pd.Timestamp("2020-07-01", tz="America/New_York")
        ):
            raise ValueError("UNIQUE_SYNTHETIC_PREFORMATION_HL_REQUIRED")

    @property
    def pair_id(self) -> str:
        self.validate()
        return identity([VERSION, self, digest(Path(__file__))])


def formation_pair(
    universe: UniverseSpec,
    rows: tuple[FormationRow, ...],
    permission: Permission,
) -> FormationPair:
    """Exact preceding60 actual XNYS sessions; daily-close×volume proxy, fake only."""
    permission.ensure()
    synthetic_id(universe.version)
    decision = pd.Timestamp("2020-07-01", tz="America/New_York").tz_convert("UTC")
    prior = schedule("2020-01-01", "2020-06-30").iloc[-60:]
    days = tuple(pd.Timestamp(d).date().isoformat() for d in prior.index)
    keys = {(r.symbol, r.session) for r in rows}
    if len(rows) != 300 or keys != {(s, d) for s in universe.symbols for d in days}:
        raise ValueError("EXACT_UNIQUE_FIVE_NAME_FORMATION60_REQUIRED")
    lookup = {}
    for d, r in prior.iterrows():
        if not isinstance(d, pd.Timestamp):
            raise ValueError("XNYS_TIMESTAMP_INDEX_REQUIRED")
        lookup[d.date().isoformat()] = utc(r.close)
    for row in rows:
        synthetic_id(row.source_id)
        if (
            not row.units_verified
            or isinstance(row.close, bool)
            or isinstance(row.volume, bool)
            or not math.isfinite(row.close)
            or not math.isfinite(row.volume)
            or row.close <= 0
            or row.volume <= 0
            or not lookup[row.session] <= utc(row.available_at) < decision
        ):
            raise ValueError("CAUSAL_SYNTHETIC_FORMATION_PRICE_VOLUME_REQUIRED")
    means = tuple(
        math.fsum(r.close * r.volume for r in rows if r.symbol == s) / 60 for s in universe.symbols
    )
    if means.count(max(means)) != 1 or means.count(min(means)) != 1:
        raise ValueError("HL_TIE_UNRESOLVED")
    # Canonical ordered table is stable when callers merely reorder input records.
    ordered = tuple(sorted(rows, key=lambda r: (universe.symbols.index(r.symbol), r.session)))
    result = FormationPair(
        universe,
        universe.symbols[means.index(max(means))],
        universe.symbols[means.index(min(means))],
        means,
        identity(ordered),
        decision,
    )
    result.validate()
    return result


def target_flags(pair: FormationPair) -> np.ndarray:
    pair.validate()
    return np.asarray(
        [(float(s == pair.highest), float(s == pair.lowest)) for s in pair.universe.symbols]
    )


@dataclass(frozen=True)
class Antecedent:
    """One extra original full-hour M1 vector, before the earliest48-step input.

    Values are upstream raw feature M1, transformed once by the existing FT0
    certificate. No new return computation or independently fitted peer scaler.
    """

    universe: UniverseSpec
    step: ScheduledStep
    raw_m1: tuple[float, ...]
    available_at: tuple[pd.Timestamp, ...]
    source_ids: tuple[str, ...]
    source_binding: str
    action_binding: str
    scaler_ref: str
    unit_evidence: str
    units_verified: bool = True
    basis: str = "SYNTHETIC"


@dataclass(frozen=True)
class CompletedM1:
    """Already-scaled synthetic table entry, with own-step publication and fit identity."""

    universe: UniverseSpec
    step: ScheduledStep
    z: tuple[float, ...]
    available_at: tuple[pd.Timestamp, ...]
    source_ids: tuple[str, ...]
    source_binding: str
    action_binding: str
    scaler_ref: str
    unit_evidence: str
    units_verified: bool = True
    basis: str = "SYNTHETIC"

    def validate(self, calendar: ScheduledCalendar) -> None:
        synthetic_id(self.universe.version)
        synthetic_id(self.unit_evidence)
        calendar.validate_step(self.step)
        if (
            self.basis != "SYNTHETIC"
            or not self.units_verified
            or len(self.z) != 5
            or not all(math.isfinite(v) for v in self.z)
            or len(self.source_ids) != 5
            or len(set(self.source_ids)) != 5
            or len(self.available_at) != 5
            or not self.source_binding
            or not self.action_binding
            or not self.scaler_ref
            or any(
                not self.step.end <= utc(t) <= self.step.information_cutoff
                for t in self.available_at
            )
        ):
            raise ValueError("CAUSAL_FIVE_ORIGINAL_FULL_HOUR_M1_REQUIRED")
        for source in self.source_ids:
            synthetic_id(source)
            if any(token in source.lower() for token in ("label", "outcome", "exit", "target")):
                raise ValueError("M1_FEATURE_EVIDENCE_CANNOT_BE_AN_OUTCOME")

    @property
    def binding(self) -> tuple:
        return (
            self.universe,
            self.source_binding,
            self.action_binding,
            self.scaler_ref,
            self.unit_evidence,
            self.units_verified,
            self.basis,
        )


def _signals(current: np.ndarray, previous: np.ndarray, pair: FormationPair) -> np.ndarray:
    """Only fixed H/L targets have directional channels; fifth is prior four-peer mean."""
    flags = target_flags(pair)
    h, low = pair.universe.symbols.index(pair.highest), pair.universe.symbols.index(pair.lowest)
    # Reuse frozen peer arithmetic, even for the additive single antecedent.
    fake = np.zeros((5, 48, 16))
    fake[:, :, M1_INDEX] = previous[:, None]
    mean = peer_summaries(fake)[:, 0, 0]
    return np.stack(
        (
            flags[:, 1] * current[h],
            flags[:, 1] * previous[h],
            flags[:, 0] * current[low],
            flags[:, 0] * previous[low],
            mean,
        ),
        axis=-1,
    )


@dataclass(frozen=True)
class DirectedWindow:
    """No labels: unchanged processed E5 controls,49 original clocks and five signals."""

    processed: BaselineInput
    peer_values: np.ndarray
    flags: np.ndarray
    signals: np.ndarray
    samples: tuple[CompletedM1, ...]
    pair: FormationPair
    peer_trace: str
    content_sha: str

    def content(self) -> str:
        return metadata_identity(
            [
                VERSION,
                self.processed,
                self.peer_values.tolist(),
                self.flags.tolist(),
                self.signals.tolist(),
                self.samples,
                self.pair.pair_id,
                self.peer_trace,
                digest(Path(__file__)),
            ]
        )

    def validate(self, calendar: ScheduledCalendar) -> None:
        self.pair.validate()
        if (
            self.pair.universe != self.processed.universe
            or len(self.samples) != 49
            or self.peer_values.shape != (5, 48, 2)
            or self.flags.shape != (5, 2)
            or self.signals.shape != (5, 48, 5)
            or self.content() != self.content_sha
        ):
            raise ValueError("DIRECTED_SOURCE_PAIR_ORDER_CODE_CONTENT_CHANGED")
        for a, b in zip(self.samples, self.samples[1:]):
            a.validate(calendar)
            b.validate(calendar)
            if (
                a.binding != b.binding
                or calendar.steps.index(b.step) != calendar.steps.index(a.step) + 1
            ):
                raise ValueError("CONTIGUOUS_CAUSAL_49_STEP_BINDING_REQUIRED")
        if tuple(s.step for s in self.samples[1:]) != self.processed.stock.steps:
            raise ValueError("EXACT_48_INPUT_CLOCKS_REQUIRED")
        for j, sample in enumerate(self.samples[1:]):
            if sample.z != tuple(_finite(v[j][M1_INDEX]) for v in self.processed.stock.values):
                raise ValueError("M1_VALUES_MUST_MATCH_FROZEN_SCALED_INPUT")
        expected = np.stack(
            [
                _signals(np.asarray(b.z), np.asarray(a.z), self.pair)
                for a, b in zip(self.samples, self.samples[1:])
            ],
            axis=1,
        )
        if not np.array_equal(expected, self.signals) or not np.array_equal(
            target_flags(self.pair), self.flags
        ):
            raise ValueError("FROZEN_DIRECTION_AND_IDENTITY_FORMULA_REQUIRED")

    def trace(self, calendar: ScheduledCalendar, index: int = 47) -> dict:
        """T1 single-step source/value/lag/flag trace, no full window or outcome dump."""
        self.validate(calendar)
        if not 0 <= index < 48:
            raise ValueError("BOUNDED_DIRECTED_TRACE_INDEX_REQUIRED")
        a, b = self.samples[index : index + 2]
        return {
            "scope": MODE,
            "HL": [self.pair.highest, self.pair.lowest],
            "pair_sha": self.pair.pair_id,
            "current": b.step.end.isoformat(),
            "previous": a.step.end.isoformat(),
            "wall_lag_minutes": (b.step.end - a.step.end).total_seconds() / 60,
            "cross_session": a.step.session != b.step.session,
            "flags": self.flags.tolist(),
            "signal_order": SIGNAL_ORDER,
            "signals": self.signals[:, index].tolist(),
            "source_ids": [a.source_ids, b.source_ids],
            "available_at": [[t.isoformat() for t in s.available_at] for s in (a, b)],
            "binding": self.content_sha,
            "ridge": "SYNTHETIC_FLAGS_ONCE_APPROVED_REAL_HOLD",
        }


def directed_window(
    row: BaselineInput,
    prep: Preparation,
    history: MarketEvidence,
    permission: Permission,
    calendar: ScheduledCalendar,
    pair: FormationPair,
    antecedent: Antecedent,
    context: Context = "ASOF",
) -> DirectedWindow:
    processed, peers, trace = peer_input(row, prep, history, permission, context)
    pair.validate()
    if pair.universe != row.universe or antecedent.universe != row.universe:
        raise ValueError("EXACT_HL_ANTECEDENT_UNIVERSE_REQUIRED")
    first = calendar.steps.index(processed.stock.steps[0])
    if (
        first == 0
        or antecedent.step != calendar.steps[first - 1]
        or antecedent.source_binding != processed.stock.source_binding
        or antecedent.action_binding != processed.stock.action_binding
        or antecedent.scaler_ref != processed.stock.scaler_ref
        or len(antecedent.raw_m1) != 5
    ):
        raise ValueError("EXACT_CAUSAL_LAG48_ANTECEDENT_REQUIRED")
    transformed = tuple(
        _finite(
            canonical_apply(
                prep.stock_scaler,
                "M1",
                v,
                antecedent.step.end,
                source_binding=antecedent.source_binding,
                action_binding=antecedent.action_binding,
                context=context,
                training_origin=row.plan.cutoff,
            )[0]
        )
        for v in antecedent.raw_m1
    )
    first_sample = CompletedM1(
        antecedent.universe,
        antecedent.step,
        transformed,
        antecedent.available_at,
        antecedent.source_ids,
        antecedent.source_binding,
        antecedent.action_binding,
        antecedent.scaler_ref,
        antecedent.unit_evidence,
        antecedent.units_verified,
        antecedent.basis,
    )
    first_sample.validate(calendar)
    samples = [first_sample]
    for j, step in enumerate(processed.stock.steps):
        values = tuple(_finite(stock[j][M1_INDEX]) for stock in processed.stock.values)
        # peer_input already rejects missing/NaT clocks; keep explicit numeric-type narrowing.
        stamps = tuple(_published(stock[j][M1_INDEX]) for stock in row.available_at)
        source_ids = tuple(stock[j][M1_INDEX] for stock in processed.stock.lineage)
        if any(s is None for s in source_ids):
            raise ValueError("ORIGINAL_M1_SOURCE_ID_REQUIRED")
        samples.append(
            CompletedM1(
                row.universe,
                step,
                values,
                stamps,
                tuple(str(s) for s in source_ids),
                antecedent.source_binding,
                antecedent.action_binding,
                antecedent.scaler_ref,
                antecedent.unit_evidence,
            )
        )
    signals = np.stack(
        [_signals(np.asarray(b.z), np.asarray(a.z), pair) for a, b in zip(samples, samples[1:])],
        axis=1,
    )
    from dataclasses import replace

    result = DirectedWindow(
        processed, peers, target_flags(pair), signals, tuple(samples), pair, trace, ""
    )
    result = replace(result, content_sha=result.content())
    result.validate(calendar)
    return result


@dataclass(frozen=True)
class ShamResult:
    """All three arms share this origin mask; no separate arm drops or invented rows."""

    matched: bool
    shifted_signals: np.ndarray | None
    exclusions: dict[str, int]
    timestamp_pairs: tuple[tuple[str, str], ...]
    binding: str
    limitation: str = "TIMING_DESTRUCTION_SHAM_NOT_FORMAL_PERMUTATION"


def timing_destroy(
    window: DirectedWindow,
    history: tuple[CompletedM1, ...],
    eligible_sessions: tuple[str, ...],
    calendar: ScheduledCalendar,
) -> ShamResult:
    """Same stock/slot exactly ten earlier eligible trading sessions, controls untouched."""
    window.validate(calendar)
    if (
        len(set(eligible_sessions)) != len(eligible_sessions)
        or tuple(sorted(eligible_sessions)) != eligible_sessions
    ):
        raise ValueError("ORDERED_UNIQUE_ELIGIBLE_SESSION_COHORT_REQUIRED")
    for d in eligible_sessions:
        calendar.clock(d)
    table = {}
    for sample in history:
        sample.validate(calendar)
        key = sample.step.session, sample.step.slot
        if key in table or sample.binding != window.samples[0].binding:
            raise ValueError("EXACT_UNIQUE_SHAM_SOURCE_FIT_BINDING_REQUIRED")
        table[key] = sample
    shifted, failures, pairs = [], Counter(), []
    for sample in window.samples:
        if sample.step.session not in eligible_sessions:
            failures["CURRENT_SESSION_NOT_ELIGIBLE"] += 1
            continue
        pos = eligible_sessions.index(sample.step.session)
        if pos < 10:
            failures["TEN_PRIOR_ELIGIBLE_SESSIONS_ABSENT"] += 1
            continue
        day = eligible_sessions[pos - 10]
        earlier = table.get((day, sample.step.slot))
        if earlier is None:
            failures["SAME_SLOT_SOURCE_ABSENT"] += 1
            continue
        if earlier.step.end >= sample.step.end:
            raise ValueError("SHAM_FUTURE_SOURCE_FORBIDDEN")
        shifted.append(earlier)
        pairs.append((sample.step.end.isoformat(), earlier.step.end.isoformat()))
    values = None
    if not failures:
        values = np.stack(
            [
                _signals(np.asarray(b.z), np.asarray(a.z), window.pair)
                for a, b in zip(shifted, shifted[1:])
            ],
            axis=1,
        )
    return ShamResult(
        not failures,
        values,
        dict(failures),
        tuple(pairs),
        metadata_identity(
            [window.content_sha, eligible_sessions, shifted, dict(failures), digest(Path(__file__))]
        ),
    )


def ridge_layout_status() -> dict:
    """Additive human-approved synthetic choice; repeated flags remain unapproved."""
    return {
        "status": "SYNTHETIC_FLAGS_ONCE_APPROVED_REAL_HOLD",
        "lags": LAGS,
        "approved_prefix": 161,
        "flags_once": {"LL0_R": 163, "LL1_R": 198},
        "flags_each_lag": {"LL0_R": 175, "LL1_R": 210},
        "effect": "Repeating7 equal flag columns changes effective penalty to lambda/7",
        "authority": "D8-RIDGE-FLAGS-ONCE-v1 additive human decision 2026-10-13",
        "real_HL": "HL_REAL_UNRESOLVED",
        "LL_neural": "NOT_IMPLEMENTED_NOT_AUTHORIZED",
    }


def directed_ridge_fit(
    data: FitData | None = None,
    stage: Stage = "WF1",
    history: MarketEvidence | None = None,
    archive: DirectedArchive | None = None,
    pair: FormationPair | None = None,
    permission: Permission | None = None,
    decision_path: Path | None = None,
    *,
    allow_synthetic: bool = False,
) -> MatchedFits:
    """Only an explicitly bound synthetic decision may enter the shared fit kernel."""
    if any(v is None for v in (data, history, archive, pair, permission, decision_path)):
        raise ValueError("LL_RIDGE_FLAG_LAYOUT_REQUIRES_HUMAN_DECISION_BINDING")
    assert data is not None and history is not None and archive is not None
    assert pair is not None and permission is not None and decision_path is not None
    from .directed_ridge import fit_directed

    return fit_directed(
        data,
        stage,
        history,
        archive,
        pair,
        permission,
        decision_path,
        allow_synthetic=allow_synthetic,
    )
