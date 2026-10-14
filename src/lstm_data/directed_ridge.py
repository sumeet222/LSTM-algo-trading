"""Synthetic once-only D8 ridge adapters over the unchanged P3 fit kernel.

Source publications retain their original clocks. The sham's older raw M1 is
transformed with the bound preparation at the current input step, never asserted
to have been transformed before that preparation existed.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, replace
from pathlib import Path

import pandas as pd

from .baseline_cache import canonical_apply
from .baseline_fit import FitData, Preparation, SelectionFit, selection_fit
from .baseline_inputs import BaselineInput
from .baseline_ridge import LAGS, Stage
from .config import digest
from .directed_peers import (
    Antecedent,
    CompletedM1,
    DirectedWindow,
    FormationPair,
    ShamResult,
    directed_window,
    timing_destroy,
)
from .ft0_transforms import Context, identity
from .m2 import ScheduledCalendar, ScheduledStep
from .neural_market import MarketEvidence, market_preparation_identity
from .p3_domain import MODE, Permission, UniverseSpec, synthetic_id
from .peer_inputs import M1_INDEX
from .ridge_extension import DECISION_SHA, LAYOUT, Arm, DirectedExtension, metadata_identity


def _scaled(value: float | None) -> float:
    if value is None or not math.isfinite(value):
        raise ValueError("FINITE_CANONICAL_M1_REQUIRED")
    return value


def approved_decision(path: Path) -> str:
    """Require the explicit human decision, not merely a caller's width claim."""
    if digest(path) != DECISION_SHA or json.loads(path.read_text()).get("decision_id") != LAYOUT:
        raise ValueError("APPROVED_FLAGS_ONCE_DECISION_SHA_REQUIRED")
    return DECISION_SHA


@dataclass(frozen=True)
class RawM1:
    step: ScheduledStep
    values: tuple[float, ...]
    source_ids: tuple[str, ...]
    available_at: tuple[pd.Timestamp, ...]


@dataclass(frozen=True)
class DirectedArchive:
    """One immutable fabricated upstream-M1 namespace, not a source loader."""

    universe: UniverseSpec
    version: str
    rows: tuple[RawM1, ...]
    source_binding: str
    action_binding: str
    unit_evidence: str
    units_verified: bool = True
    basis: str = "SYNTHETIC"

    def validate(self, calendar: ScheduledCalendar) -> None:
        synthetic_id(self.version)
        if not self.rows or len({r.step.end for r in self.rows}) != len(self.rows):
            raise ValueError("UNIQUE_COMPLETE_M1_ARCHIVE_REQUIRED")
        for row in self.rows:
            CompletedM1(
                self.universe,
                row.step,
                row.values,
                row.available_at,
                row.source_ids,
                self.source_binding,
                self.action_binding,
                "SYN:RAW_VALIDATION",
                self.unit_evidence,
                self.units_verified,
                self.basis,
            ).validate(calendar)

    @property
    def archive_id(self) -> str:
        return metadata_identity(self)


def extension(
    window: DirectedWindow,
    sham: ShamResult,
    prep: Preparation,
    context: str,
    arm: Arm,
    decision_sha: str,
) -> DirectedExtension:
    """Lag-major peer14, once-only flags2, then directed35; no new scaler."""
    if decision_sha != DECISION_SHA or not sham.matched or sham.shifted_signals is None:
        raise ValueError("APPROVED_LAYOUT_AND_COMMON_SHAM_MASK_REQUIRED")
    tails = []
    signals = sham.shifted_signals if arm == "SHAM_LL1_R" else window.signals
    for i in range(5):
        peer = tuple(float(v) for lag in LAGS for v in window.peer_values[i, 47 - lag])
        flags = tuple(float(v) for v in window.flags[i])
        directed = tuple(float(v) for lag in LAGS for v in signals[i, 47 - lag])
        tails.append(peer + flags + (() if arm == "LL0_R" else directed))
    value = DirectedExtension(
        tuple(tails),
        arm,
        window.processed.input_id,
        window.processed.universe.universe_id,
        market_preparation_identity(prep),
        context,
        decision_sha,
        identity([window.content_sha, sham.binding]),
        "",
    )
    return replace(value, content_id=value.content())


class MatchedDesign:
    """Shared per-origin preparation cache; each arm rejects exactly the same mask."""

    def __init__(
        self,
        archive: DirectedArchive,
        history: MarketEvidence,
        pair: FormationPair,
        calendar: ScheduledCalendar,
        decision_sha: str,
    ) -> None:
        archive.validate(calendar)
        history.validate()
        pair.validate()
        if archive.universe != pair.universe or decision_sha != DECISION_SHA:
            raise ValueError("EXACT_SYNTHETIC_PAIR_DECISION_REQUIRED")
        self.archive, self.history, self.pair, self.calendar = archive, history, pair, calendar
        self.decision_sha = decision_sha
        self.archive_id = archive.archive_id
        self.lookup = {r.step.end: r for r in archive.rows}
        self.sessions = tuple(sorted({s.session for s in calendar.steps}))
        self.slots = {(s.session, s.slot): s for s in calendar.steps}
        self.positions = {s.end: i for i, s in enumerate(calendar.steps)}
        self.cache: dict[tuple[str, str, str], tuple[DirectedWindow, ShamResult, str]] = {}

    def prepare(
        self,
        row: BaselineInput,
        prep: Preparation,
        permission: Permission,
        context: str,
    ) -> tuple[DirectedWindow, ShamResult, str]:
        permission.ensure()
        if context not in {"ASOF", "HISTORICAL_TRAINING"}:
            raise ValueError("EXPLICIT_PREPROCESS_CONTEXT_REQUIRED")
        ctx: Context = "ASOF" if context == "ASOF" else "HISTORICAL_TRAINING"
        if (
            row.universe != self.archive.universe
            or row.stock.source_binding != self.archive.source_binding
            or row.stock.action_binding != self.archive.action_binding
        ):
            raise ValueError("M1_ARCHIVE_SOURCE_ACTION_ORDER_CHANGED")
        key = row.input_id, market_preparation_identity(prep), context
        # Hash row content as well: a reused ID cannot conceal an input mutation.
        row_sha = metadata_identity(row)
        cached = self.cache.get(key)
        if cached is not None:
            if cached[2] != row_sha:
                raise ValueError("INPUT_ID_CONTENT_CONFLICT")
            return cached
        for j, step in enumerate(row.stock.steps):
            source = self.lookup.get(step.end)
            if source is None or any(
                row.stock.raw_values[i][j][M1_INDEX] != source.values[i]
                or row.stock.lineage[i][j][M1_INDEX] != source.source_ids[i]
                or row.available_at[i][j][M1_INDEX] != source.available_at[i]
                for i in range(5)
            ):
                raise ValueError("EXACT_UPSTREAM_M1_SOURCE_VALUES_CLOCKS_REQUIRED")
        first = self.positions[row.stock.steps[0].end]
        if first == 0:
            raise ValueError("EXACT_CAUSAL_LAG48_ANTECEDENT_REQUIRED")
        previous = self.lookup.get(self.calendar.steps[first - 1].end)
        if previous is None:
            raise ValueError("MISSING_ORIGINAL_LAG48_SOURCE")
        a = Antecedent(
            row.universe,
            previous.step,
            previous.values,
            previous.available_at,
            previous.source_ids,
            self.archive.source_binding,
            self.archive.action_binding,
            prep.stock_scaler.certificate_id,
            self.archive.unit_evidence,
            self.archive.units_verified,
            self.archive.basis,
        )
        window = directed_window(
            row,
            prep,
            self.history,
            permission,
            self.calendar,
            self.pair,
            a,
            ctx,
        )
        shifted, applications = [], []
        for sample in window.samples:
            pos = self.sessions.index(sample.step.session)
            if pos < 10:
                raise ValueError("TEN_PRIOR_ELIGIBLE_SESSIONS_ABSENT")
            step = self.slots.get((self.sessions[pos - 10], sample.step.slot))
            raw = self.lookup.get(step.end) if step is not None else None
            if raw is None:
                raise ValueError("SAME_SLOT_SOURCE_ABSENT")
            # Already-known older feature, transformed NOW by this bound fit.
            z = tuple(
                _scaled(
                    canonical_apply(
                        prep.stock_scaler,
                        "M1",
                        v,
                        sample.step.end,
                        source_binding=self.archive.source_binding,
                        action_binding=self.archive.action_binding,
                        context=ctx,
                        training_origin=row.plan.cutoff,
                    )[0]
                )
                for v in raw.values
            )
            shifted.append(
                CompletedM1(
                    row.universe,
                    raw.step,
                    z,
                    raw.available_at,
                    raw.source_ids,
                    self.archive.source_binding,
                    self.archive.action_binding,
                    prep.stock_scaler.certificate_id,
                    self.archive.unit_evidence,
                )
            )
            applications.append((raw.step.end, sample.step.end, prep.window.fitted_at, ctx))
        sham = timing_destroy(window, tuple(shifted), self.sessions, self.calendar)
        if not sham.matched:
            raise ValueError("COMMON_SHAM_MASK:" + str(sham.exclusions))
        sham = replace(
            sham, binding=metadata_identity([sham.binding, applications, self.archive_id])
        )
        result = window, sham, row_sha
        self.cache[key] = result
        return result

    def adapter(self, arm: Arm):
        def apply(row: BaselineInput, prep: Preparation, permission: Permission, context: str):
            window, sham, _ = self.prepare(row, prep, permission, context)
            return window.processed, extension(
                window,
                sham,
                prep,
                context,
                arm,
                self.decision_sha,
            )

        return apply


@dataclass(frozen=True)
class MatchedFits:
    ll0: SelectionFit
    ll1: SelectionFit
    sham: SelectionFit
    evidence: dict


def fit_directed(
    data: FitData,
    stage: Stage,
    history: MarketEvidence,
    archive: DirectedArchive,
    pair: FormationPair,
    permission: Permission,
    decision_path: Path,
    *,
    allow_synthetic: bool = False,
) -> MatchedFits:
    """Three actual candidate/refit arms; never confers empirical forecast authority."""
    data.validate(permission, allow_synthetic)
    from .neural_data import validate_label_clocks

    validate_label_clocks(data)
    if len({r.inputs.input_id for r in data.origins}) != len(data.origins):
        raise ValueError("UNIQUE_RIDGE_INPUT_IDENTITIES_REQUIRED")
    if history.vectors != data.market_vectors or data.universe != archive.universe:
        raise ValueError("EXACT_SYNTHETIC_FIT_SOURCE_REQUIRED")
    stop = {"WF1": "2023-06-30", "WF2": "2023-12-31", "PRECONFIRMATION": "2024-06-30"}[stage]
    calendar = ScheduledCalendar("2020-07-01", stop)
    design = MatchedDesign(archive, history, pair, calendar, approved_decision(decision_path))
    fits = tuple(
        selection_fit(
            data,
            stage,
            permission,
            market=True,
            allow_synthetic=True,
            adapter=design.adapter(arm),
        )
        for arm in ("LL0_R", "LL1_R", "SHAM_LL1_R")
    )
    matched_fields = (
        "fit_keys",
        "validation_keys",
        "train_exclusions",
        "validation_exclusions",
        "refit_exclusions",
        "effective_train_weights",
        "effective_refit_weights",
        "candidate_scaler",
        "candidate_tg0_floor",
        "refit_scaler",
        "refit_tg0_floor",
    )
    if any(f.evidence[k] != fits[0].evidence[k] for f in fits for k in matched_fields):
        raise ValueError("EXACT_THREE_ARM_COHORT_PREPARATION_REQUIRED")
    if tuple(len(f.solution.coefficients) for f in fits) != (163, 198, 198):
        raise ValueError("EXACT_APPROVED_ONCE_FLAG_DIMENSIONS_REQUIRED")
    evidence = {
        "scope": MODE,
        "layout": LAYOUT,
        "decision_sha": DECISION_SHA,
        "archive_id": archive.archive_id,
        "formation_pair": pair.pair_id,
        "universe": data.universe.universe_id,
        "order": data.universe.symbols,
        "code_sha": digest(Path(__file__)),
        "code_dependencies": {
            name: digest(Path(__file__).with_name(name))
            for name in (
                "baseline_fit.py",
                "baseline_ridge.py",
                "peer_inputs.py",
                "directed_peers.py",
                "ridge_extension.py",
                "ft0_transforms.py",
                "neural_market.py",
                "hourly_proxy.py",
            )
        },
        "market_evidence": history.evidence_id,
        "preparations": tuple(market_preparation_identity(f.preparation) for f in fits),
        "matched_fields": matched_fields,
        "fit_ids": tuple(
            identity([f.input_hash, f.solution, pair.pair_id, DECISION_SHA]) for f in fits
        ),
        "sham": "TEN_ELIGIBLE_SESSIONS_SAME_STOCK_SLOT_WEAK_DIAGNOSTIC",
        "source_clock": "ORIGINAL_PUBLICATION; TRANSFORM_AT_CURRENT_INPUT_STEP",
        "real_HL": "HL_REAL_UNRESOLVED",
        "scientific_status": "HOLD",
        "science_pairs_consumed": 0,
    }
    return MatchedFits(fits[0], fits[1], fits[2], evidence)
