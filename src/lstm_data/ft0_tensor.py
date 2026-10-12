"""Guarded stock-only and stock/SPY candidate inputs; no model or execution engine."""

from __future__ import annotations

from dataclasses import dataclass

from .clocks import ExecutionPlan
from .ft0_transforms import (
    ORDER,
    SCALED,
    Context,
    FitObservation,
    FloorCertificate,
    ScalerCertificate,
)
from .labels import UNIVERSE, ForecastEvidence
from .m2 import M2FloorCertificate, ScheduledStep, scheduled_window, window_quality
from .market_features import (
    MarketFloors,
    MarketHistory,
    MarketScaler,
    MarketWindow,
    window_from_history,
)
from .stock_features import FeatureCalculator, FeatureCell
from .stock_source import proxy_reference

Numbers = tuple[tuple[tuple[float | None, ...], ...], ...]
Masks = tuple[tuple[tuple[bool, ...], ...], ...]
Reasons = tuple[tuple[tuple[str, ...], ...], ...]


@dataclass(frozen=True)
class StockTensor:
    symbols: tuple[str, ...]
    steps: tuple[ScheduledStep, ...]
    channels: tuple[str, ...]
    raw_values: Numbers
    values: Numbers
    mask: Masks
    reasons: Reasons
    lineage: tuple[tuple[tuple[str, ...], ...], ...]
    input_eligible: bool
    floor_ref: str | None
    m2_floor_refs: tuple[str | None, ...]
    scaler_ref: str | None
    application_context: Context
    source_binding: str
    action_binding: str
    source_only: bool
    synthetic: bool
    research_ready: bool = False

    @property
    def shape(self) -> tuple[int, int, int]:
        return 5, 48, 16


def stock_window(
    calculator: FeatureCalculator,
    session: str,
    origin: int,
    floors: FloorCertificate | None = None,
    m2_floors: tuple[M2FloorCertificate | None, ...] = (),
    scaler: ScalerCertificate | None = None,
    *,
    context: Context = "ASOF",
    source_only: bool = False,
) -> StockTensor:
    """All 3,840 cells required; invalid values retain positions and never become zeros."""
    history = calculator.history
    steps = scheduled_window(history.calendar, session, origin)
    if not m2_floors:
        m2_floors = (None,) * 5
    if len(m2_floors) != 5:
        raise ValueError("FIVE_ORDERED_STOCK_M2_CERTIFICATES_REQUIRED")
    if scaler is not None and (
        scaler.source_binding != history.binding or scaler.action_binding != history.action_binding
    ):
        raise ValueError("FT0_SCALER_SOURCE_BINDING_MISMATCH")
    raw, values, masks, reasons, lineage = [], [], [], [], []
    for symbol, m2_floor in zip(UNIVERSE, m2_floors):
        if m2_floor is not None and any(key[0] != symbol for key in m2_floor.fitting_keys):
            raise ValueError("M2_CERTIFICATE_STOCK_MISMATCH")
        sr, sv, sm, se, si = [], [], [], [], []
        for step in steps:
            cells = calculator.evaluate(
                symbol,
                step,
                origin,
                floors,
                m2_floor,
                source_only=source_only,
                context=context,
                training_origin=steps[-1].end,
            )
            current_values, current_mask, current_reasons = [], [], []
            for cell in cells:
                value, reason = None, cell.reason
                if cell.valid and cell.value is not None:
                    if cell.feature not in SCALED:
                        value, reason = cell.value, "NATIVE_BOUNDED_VALID"
                    elif scaler is None:
                        reason = "SCALER_CERTIFICATE_REQUIRED"
                    else:
                        value, reason, novel = scaler.apply(
                            cell.feature,
                            cell.value,
                            step.information_cutoff,
                            source_binding=history.binding,
                            action_binding=history.action_binding,
                            context=context,
                            training_origin=steps[-1].end,
                        )
                        if novel:
                            reason += ":NOVEL_CONSTANT_VARIATION"
                current_values.append(value)
                current_mask.append(value is not None)
                current_reasons.append(reason)
            sr.append(tuple(c.value for c in cells))
            sv.append(tuple(current_values))
            sm.append(tuple(current_mask))
            se.append(tuple(current_reasons))
            si.append(tuple(c.lineage_id for c in cells))
        raw.append(tuple(sr))
        values.append(tuple(sv))
        masks.append(tuple(sm))
        reasons.append(tuple(se))
        lineage.append(tuple(si))
    # Reuse the approved close-only window audit as an independent boundary check.
    references = tuple(
        ref
        for symbol in UNIVERSE
        for step in steps
        if (bar := history.bars.get((symbol, step.session, step.slot))) is not None
        and (ref := proxy_reference(bar, 1.0, "EXPLICIT_SYNTHETIC_COMMON_EPOCH")) is not None
        and history.synthetic
    )
    quality = window_quality(history.calendar, steps, references, test_scenario=history.synthetic)
    eligible = all(all(all(row) for row in stock) for stock in masks)
    if history.synthetic and eligible and not quality.raw_window_eligible:
        raise ValueError("FT0_CLOSE_QUALITY_CONTRADICTION")
    return StockTensor(
        UNIVERSE,
        steps,
        ORDER,
        tuple(raw),
        tuple(values),
        tuple(masks),
        tuple(reasons),
        tuple(lineage),
        eligible,
        floors.certificate_id if floors else None,
        tuple(f.floor_id if f else None for f in m2_floors),
        scaler.certificate_id if scaler else None,
        context,
        history.binding,
        history.action_binding,
        source_only,
        history.synthetic,
    )


@dataclass(frozen=True)
class CandidateJoin:
    stock: StockTensor
    market: MarketWindow | None
    stock_only_eligible: bool
    matched_market_eligible: bool
    status: str
    future_mc0_width: int = 21
    model_wiring: str = "NOT_BUILT"
    research_ready: bool = False


def join_market(
    stock: StockTensor,
    history: MarketHistory | None,
    market_floors: MarketFloors | None = None,
    market_scaler: MarketScaler | None = None,
    *,
    origin: int,
) -> CandidateJoin:
    if stock.symbols != UNIVERSE or stock.channels != ORDER or len(stock.steps) != 48:
        raise ValueError("CANONICAL_FT0_TENSOR_REQUIRED")
    market = None
    if history is not None:
        market = window_from_history(
            history,
            stock.steps[-1].session,
            origin,
            market_floors,
            market_scaler,
            allow_synthetic=stock.synthetic and history.allow_synthetic,
        )
        if market.scheduled_ends != tuple(s.end for s in stock.steps):
            raise ValueError("STOCK_SPY_SCHEDULED_KEY_MISMATCH")
    market_valid = market is not None and market.values is not None
    return CandidateJoin(
        stock,
        market,
        stock.input_eligible,
        stock.input_eligible and market_valid,
        "IMPLEMENTATION_PASS_SCIENTIFIC_HOLD" if stock.input_eligible else "INPUT_HOLD",
    )


def forecast_bridge(stock: StockTensor, plan: ExecutionPlan) -> ForecastEvidence:
    """Only input state; exits, labels and fills cannot affect this bridge."""
    if plan.cutoff != stock.steps[-1].end or plan.session != stock.steps[-1].session:
        raise ValueError("FT0_PLAN_ORIGIN_MISMATCH")
    return ForecastEvidence(
        stock.input_eligible and stock.application_context == "ASOF",
        stock.steps[-1].end,
        UNIVERSE,
        "SYNTHETIC" if stock.synthetic else "UNKNOWN",
        stock.source_binding + ":" + (stock.scaler_ref or "SCALER_PENDING"),
    )


def fitting_observations(cells: tuple[FeatureCell, ...]) -> tuple[FitObservation, ...]:
    """Canonical unique feature input records; no label or future-fill filtering."""
    output = []
    for cell in cells:
        if not cell.valid or cell.value is None or cell.feature not in SCALED:
            continue
        if cell.basis != "SYNTHETIC":
            raise ValueError("FIT_PENDING_SOURCE_EVIDENCE")
        output.append(
            FitObservation(
                cell.key[0],
                cell.timestamp,
                cell.feature,
                cell.key,
                cell.value,
                cell.lineage_id,
                cell.source_binding,
                cell.action_binding,
                "SYNTHETIC",
                cell.timestamp,
                cell.key[2] if cell.feature == "M2" else None,
            )
        )
    return tuple(output)
