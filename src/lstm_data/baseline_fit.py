"""Synthetic chronological candidate preprocessing, five lambda fits, one refit."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Protocol

import numpy as np
import pandas as pd

from .baseline_authority import verify
from .baseline_cache import canonical_apply
from .baseline_inputs import BaselineInput
from .baseline_ridge import (
    PENALTIES,
    RidgeModel,
    RidgeOrigin,
    Solution,
    Stage,
    adequacy,
    bind_model,
    choose_penalty,
    fitting_origins,
    lag_vectors,
    session_weights,
    solve_weighted,
    windows,
)
from .ft0_transforms import (
    FitObservation,
    FloorCertificate,
    ScalerCertificate,
    check_window,
    fit_floors,
    fit_scaler,
    identity,
)
from .hourly_proxy import ProxyFloor, apply_proxy_floor, fit_proxy_floor
from .labels import FitWindow
from .market_features import (
    DailyScaleSample,
    MarketFitWindow,
    MarketFloors,
    MarketMeasures,
    MarketScaler,
    MarketVector,
    MarketWindow,
    fit_synthetic_floors,
    fit_synthetic_scaler,
)
from .p3_domain import Permission, UniverseSpec


@dataclass(frozen=True)
class FitData:
    universe: UniverseSpec
    origins: tuple[RidgeOrigin, ...]
    stock_records: tuple[FitObservation, ...]
    floor_records: tuple[FitObservation, ...]
    market_vectors: tuple[MarketVector, ...]
    market_measures: tuple[MarketMeasures, ...]
    daily_scales: tuple[DailyScaleSample, ...]
    basis: str

    def validate(self, permission: Permission, allow_synthetic: bool) -> None:
        verify(permission)
        if not allow_synthetic or self.basis != "SYNTHETIC" or not self.origins:
            raise ValueError("EMPIRICAL_RIDGE_FITTING_HOLD")
        for row in self.origins:
            row.validate(self.universe)
        if any(r.basis != "SYNTHETIC" for r in self.stock_records + self.floor_records):
            raise ValueError("EMPIRICAL_SCALER_FLOOR_FITTING_HOLD")
        if any(
            r.basis != "SYNTHETIC"
            for r in self.market_vectors + self.market_measures + self.daily_scales
        ):
            raise ValueError("EMPIRICAL_D7_FITTING_HOLD")


@dataclass(frozen=True)
class Preparation:
    universe: UniverseSpec
    window: FitWindow
    stock_scaler: ScalerCertificate
    stock_floors: FloorCertificate
    tg0_floor: ProxyFloor
    market_scaler: MarketScaler | None
    market_floors: MarketFloors | None
    market_vectors: tuple[MarketVector, ...]

    def with_market_history(
        self,
        vectors: tuple[MarketVector, ...],
        permission: Permission,
        *,
        allow_synthetic: bool = False,
    ) -> Preparation:
        verify(permission)
        if (
            not allow_synthetic
            or self.market_scaler is None
            or any(
                v.basis != "SYNTHETIC" or v.source_version != self.market_scaler.source_version
                for v in vectors
            )
        ):
            raise ValueError("SYNTHETIC_ASOF_D7_HISTORY_REQUIRED")
        lookup = {v.timestamp: v for v in self.market_vectors}
        for value in vectors:
            previous = lookup.get(value.timestamp)
            if previous is not None and previous != value:
                raise ValueError("CONFLICTING_D7_HISTORY_REPLACEMENT")
            lookup[value.timestamp] = value
        return replace(self, market_vectors=tuple(lookup[t] for t in sorted(lookup)))

    def apply(self, row: BaselineInput, context: str) -> BaselineInput:
        if context not in {"ASOF", "HISTORICAL_TRAINING"}:
            raise ValueError("EXPLICIT_PREPROCESS_CONTEXT_REQUIRED")
        if row.universe != self.universe or row.basis != "SYNTHETIC":
            raise ValueError("PREPROCESS_UNIVERSE_SYNTHETIC_BINDING_REQUIRED")
        if self.stock_floors.values != row.stock_floors.values:
            raise ValueError("UPSTREAM_RAW_FEATURE_FLOOR_REBUILD_REQUIRED")
        scaler = self.stock_scaler
        values = []
        for stock in row.stock.raw_values:
            rows = []
            for step, original in zip(row.stock.steps, stock):
                rows.append(
                    tuple(
                        canonical_apply(
                            scaler,
                            f,
                            value,
                            step.end,
                            source_binding=row.stock.source_binding,
                            action_binding=row.stock.action_binding,
                            context="ASOF" if context == "ASOF" else "HISTORICAL_TRAINING",
                            training_origin=row.plan.cutoff,
                        )[0]
                        if value is not None
                        else None
                        for f, value in zip(row.stock.channels, original)
                    )
                )
            values.append(tuple(rows))
        stock = replace(
            row.stock,
            values=tuple(values),
            scaler_ref=scaler.certificate_id,
            floor_ref=self.stock_floors.certificate_id,
            application_context="ASOF" if context == "ASOF" else "HISTORICAL_TRAINING",
        )
        market = None
        if self.market_scaler is not None and self.market_floors is not None:
            lookup = {v.timestamp: v for v in self.market_vectors}
            output, mask, ids = [], [], []
            for step in stock.steps:
                v = lookup.get(step.end)
                valid = v is not None and v.values is not None and v.reason == "VECTOR_VALID"
                mask.append(valid)
                if valid and v is not None and v.values is not None:
                    output.append(self.market_scaler.transform(v.values)[0])
                    ids.append(v.evidence_ids)
                else:
                    output.append((0.0,) * 5)
                    ids.append(())
            market = MarketWindow(
                tuple(output),
                tuple(mask),
                "SYNTHETIC_PREPARED",
                (),
                scheduled_ends=tuple(s.end for s in stock.steps),
                source_ids=tuple(ids),
                floor_ref=identity(self.market_floors),
                scaler_ref=identity(self.market_scaler),
                application_context=stock.application_context,
                source_ages_seconds=tuple(0.0 if v else None for v in mask),
            )
        return replace(
            row,
            stock=stock,
            stock_scaler=scaler,
            stock_floors=self.stock_floors,
            market=market,
            market_scaler=self.market_scaler,
        )


@dataclass(frozen=True)
class RidgeMarketFitWindow(MarketFitWindow):
    """The P2 helper's INNER cap is WF1-specific; bind all approved P3 fold windows.

    This synthetic adapter requires the exact frozen stock fitting-window bounds
    and phase. No arbitrary later training or empirical source becomes permitted.
    """

    parent: FitWindow

    def __post_init__(self) -> None:
        check_window(self.parent)
        if (
            not self.parent.window_id.startswith(("WF1:", "WF2:", "PRECONFIRMATION:"))
            or self.parent.phase not in {"INNER_TRAIN", "REFIT"}
            or (self.start, self.stop, self.fitted_at, self.phase)
            != (self.parent.start, self.parent.stop, self.parent.fitted_at, self.parent.phase)
        ):
            raise ValueError("EXACT_FROZEN_RIDGE_MARKET_WINDOW_REQUIRED")


def prepare(
    data: FitData,
    window: FitWindow,
    rows: tuple[RidgeOrigin, ...],
    *,
    market: bool,
    permission: Permission,
    allow_synthetic: bool = False,
) -> Preparation:
    data.validate(permission, allow_synthetic)
    for row in rows:
        row.validate(data.universe)
    if window.phase not in {"INNER_TRAIN", "REFIT"}:
        raise ValueError("TRAINING_PREPROCESS_ONLY")
    # Same authoritative bounds/phase, explicitly synthetic certificate namespace.
    # Avoid reconstructing the exchange calendar for every one of3840 cell applies.
    synthetic_window = replace(window, window_id="SYNTHETIC:" + window.window_id)
    scaler = fit_scaler(
        data.stock_records,
        synthetic_window,
        "SYN:RIDGE:SCALER:" + window.window_id,
        allow_synthetic=True,
    )
    floors = fit_floors(
        data.floor_records,
        synthetic_window,
        "SYN:RIDGE:FLOORS:" + window.window_id,
        allow_synthetic=True,
    )
    tg0 = fit_proxy_floor(tuple(r.label for r in rows), window, test_scenario=True)
    market_scaler = market_floors = None
    if market:
        phase = "INNER_TRAIN" if window.phase == "INNER_TRAIN" else "REFIT"
        mw = RidgeMarketFitWindow(window.start, window.stop, window.fitted_at, phase, window)
        vectors = tuple(v for v in data.market_vectors if mw.contains(v.timestamp))
        measures = tuple(v for v in data.market_measures if mw.contains(v.timestamp))
        daily = tuple(v for v in data.daily_scales if mw.contains(v.timestamp))
        market_scaler = fit_synthetic_scaler(
            vectors, mw, "SYN:RIDGE:D7_SCALER", allow_synthetic=True
        )
        market_floors = fit_synthetic_floors(
            measures, daily, mw, "SYN:RIDGE:D7_FLOOR", allow_synthetic=True
        )
    return Preparation(
        data.universe,
        window,
        scaler,
        floors,
        tg0,
        market_scaler,
        market_floors,
        data.market_vectors,
    )


class DesignAdapter(Protocol):
    """Synthetic diagnostic adapter; canonical transformed input plus extra columns."""

    def __call__(
        self, row: BaselineInput, prep: Preparation, permission: Permission, context: str
    ) -> tuple[BaselineInput, tuple[tuple[float, ...], ...]]: ...


def design(
    rows: tuple[RidgeOrigin, ...],
    prep: Preparation,
    permission: Permission,
    *,
    market: bool,
    context: str,
    matched_market: bool,
    adapter: DesignAdapter | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, tuple, tuple]:
    features, targets, keys, accepted, failures = [], [], [], [], []
    for row in rows:
        try:
            extra = None
            if adapter is None:
                transformed = prep.apply(row.inputs, context)
            else:
                transformed, extra = adapter(row.inputs, prep, permission, context)
            x = lag_vectors(
                transformed, permission, market=market, allow_synthetic=True, context=context
            )
            if matched_market:
                transformed.validate_market(permission, allow_synthetic=True)
            if extra is not None:
                if (
                    not market
                    or len(extra) != 5
                    or len({len(r) for r in extra}) != 1
                    or len(extra[0]) not in {0, 14}
                ):
                    raise ValueError("EXACT_SYNTHETIC_PEER14_EXTENSION_REQUIRED")
                x = tuple(base + tail for base, tail in zip(x, extra))
        except ValueError as exc:
            failures.append((row.label.key, str(exc)))
            continue
        y = apply_proxy_floor(row.label, prep.tg0_floor, test_scenario=True).scores
        features.extend(x)
        targets.extend(y)
        keys.extend(
            (row.label.plan.session, row.label.plan.origin, s) for s in prep.universe.symbols
        )
        accepted.append(row)
    if not accepted:
        raise ValueError("NO_ELIGIBLE_RIDGE_DESIGN")
    return (
        np.asarray(features),
        np.asarray(targets),
        session_weights(tuple(keys)),
        tuple(accepted),
        tuple(failures),
    )


@dataclass(frozen=True)
class Selection:
    model: RidgeModel
    preparation: Preparation
    candidates: tuple[dict, ...]
    selected_penalty: float
    evidence: dict


def selection_fit(
    data: FitData,
    stage: Stage,
    permission: Permission,
    *,
    market: bool,
    allow_synthetic: bool = False,
    matched_market: bool = True,
    adapter: DesignAdapter | None = None,
) -> SelectionFit:
    data.validate(permission, allow_synthetic)
    # The authoritative constructors determine each cutoff; fit after the exclusive stop.
    provisional = {"WF1": "2023-07-01", "WF2": "2024-01-01", "PRECONFIRMATION": "2024-07-01"}[stage]
    refit_at = pd.Timestamp(provisional, tz="America/New_York").tz_convert("UTC")
    inner, validation, refit = windows(stage, refit_at)
    inner = replace(inner, fitted_at=inner.stop)
    train, train_ex = fitting_origins(data.origins, data.universe, inner)
    val, val_ex = fitting_origins(data.origins, data.universe, validation)
    prep = prepare(
        data,
        inner,
        train,
        market=market or matched_market,
        permission=permission,
        allow_synthetic=True,
    )
    x, y, w, trained, train_bad = design(
        train,
        prep,
        permission,
        market=market,
        context="HISTORICAL_TRAINING",
        matched_market=matched_market,
        adapter=adapter,
    )
    vx, vy, vw, evaluated, val_bad = design(
        val,
        prep,
        permission,
        market=market,
        context="ASOF",
        matched_market=matched_market,
        adapter=adapter,
    )
    guard = adequacy(evaluated)
    candidates = []
    for penalty in PENALTIES:
        solution = solve_weighted(x, y, w, penalty)
        loss = float(
            np.sum(vw * (vy - solution.intercept - vx @ np.asarray(solution.coefficients)) ** 2)
        )
        candidates.append(
            {
                "penalty": penalty,
                "validation_session_TG0_MSE": loss,
                "solution": identity(solution),
                "condition": solution.condition,
                "residual": solution.residual_norm,
                "objective": solution.objective,
                "fit_stop": inner.stop.isoformat(),
                "fitted_at": inner.fitted_at.isoformat(),
            }
        )
    chosen = choose_penalty(
        tuple((c["penalty"], c["validation_session_TG0_MSE"]) for c in candidates)
    )
    full, full_ex = fitting_origins(data.origins, data.universe, refit)
    final_prep = prepare(
        data,
        refit,
        full,
        market=market or matched_market,
        permission=permission,
        allow_synthetic=True,
    )
    fx, fy, fw, refitted, refit_bad = design(
        full,
        final_prep,
        permission,
        market=market,
        context="HISTORICAL_TRAINING",
        matched_market=matched_market,
        adapter=adapter,
    )
    final = solve_weighted(fx, fy, fw, chosen)
    input_hash = identity(
        [
            [(r.label.key, r.inputs.input_id) for r in refitted],
            fx.tolist(),
            fy.tolist(),
            fw.tolist(),
        ]
    )
    evidence = {
        "scope": "SYNTHETIC_ONLY",
        "stage": stage,
        "training_origins": len(trained),
        "validation_origins": len(evaluated),
        "refit_origins": len(refitted),
        "adequacy": guard,
        "candidate_scaler": prep.stock_scaler.certificate_id,
        "candidate_tg0_floor": prep.tg0_floor.floor_id,
        "refit_scaler": final_prep.stock_scaler.certificate_id,
        "refit_tg0_floor": final_prep.tg0_floor.floor_id,
        "train_exclusions": train_ex + train_bad,
        "validation_exclusions": val_ex + val_bad,
        "refit_exclusions": full_ex + refit_bad,
        "refit_count": 1,
        "candidate_count": 5,
        "effective_train_weights": tuple(float(v) for v in w),
        "effective_refit_weights": tuple(float(v) for v in fw),
        "validation_keys": tuple(r.label.key for r in evaluated),
        "fit_keys": tuple(r.label.key for r in trained),
        "criterion": "SESSION_WEIGHTED_TG0_MSE_EXACT_TIE_LARGER_LAMBDA",
        "scientific_status": "HOLD",
    }
    return SelectionFit(final, final_prep, tuple(candidates), chosen, evidence, refit, input_hash)


@dataclass(frozen=True)
class SelectionFit:
    """Shared synthetic selection/refit kernel; does not confer forecast authority."""

    solution: Solution
    preparation: Preparation
    candidates: tuple[dict, ...]
    selected_penalty: float
    evidence: dict
    window: FitWindow
    input_hash: str


def select_and_refit(
    data: FitData,
    stage: Stage,
    permission: Permission,
    *,
    market: bool,
    allow_synthetic: bool = False,
    matched_market: bool = True,
) -> Selection:
    """Original public112/147 model contract; delegates to unchanged selection math."""
    fitted = selection_fit(
        data,
        stage,
        permission,
        market=market,
        allow_synthetic=allow_synthetic,
        matched_market=matched_market,
    )
    prep = fitted.preparation
    model = bind_model(
        data.universe,
        fitted.solution,
        market,
        fitted.window,
        prep.stock_scaler.certificate_id,
        identity(prep.market_scaler) if market else None,
        prep.tg0_floor.floor_id,
        fitted.input_hash,
    )
    return Selection(model, prep, fitted.candidates, fitted.selected_penalty, fitted.evidence)
