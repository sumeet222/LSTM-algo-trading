"""Matched synthetic147/161 diagnostics through the original P3 selection kernel."""

from __future__ import annotations

from .baseline_fit import FitData, Preparation, SelectionFit, selection_fit
from .baseline_inputs import BaselineInput
from .baseline_ridge import LAGS, Stage
from .ft0_transforms import identity
from .neural_market import MarketEvidence, market_preparation_identity
from .p3_domain import Permission
from .peer_inputs import peer_code_identity, peer_input


def matched_peer_ridge(
    data: FitData,
    stage: Stage,
    history: MarketEvidence,
    permission: Permission,
    *,
    allow_synthetic: bool = False,
) -> tuple[SelectionFit, SelectionFit, dict]:
    """Same strict causal adapter/labels/63-tail/weights; no model forecast authority."""
    data.validate(permission, allow_synthetic)
    history.validate()
    from .neural_data import data_identity, validate_label_clocks

    validate_label_clocks(data)
    if len({r.inputs.input_id for r in data.origins}) != len(data.origins):
        raise ValueError("UNIQUE_RIDGE_INPUT_IDENTITIES_REQUIRED")
    if data.market_vectors != history.vectors:
        raise ValueError("EXACT_RIDGE_D7_HISTORY_REQUIRED")
    # Shared temporary normalized inputs. No second feature formulas/solver/loss,
    # no persistent tensors and no outcome-based cohort choice.
    cache: dict[tuple[str, str, str], tuple[BaselineInput, tuple[tuple[float, ...], ...]]] = {}

    def adapter(peers: bool):
        def apply(
            row: BaselineInput, prep: Preparation, permission: Permission, context: str
        ) -> tuple[BaselineInput, tuple[tuple[float, ...], ...]]:
            key = row.input_id, market_preparation_identity(prep), context
            if key not in cache:
                processed, summaries, _ = peer_input(row, prep, history, permission, context)
                extra = tuple(
                    tuple(float(v) for lag in LAGS for v in summaries[i, 47 - lag])
                    for i in range(5)
                )
                cache[key] = processed, extra
            processed, extra = cache[key]
            return processed, extra if peers else tuple(() for _ in range(5))

        return apply

    control = selection_fit(
        data, stage, permission, market=True, allow_synthetic=True, adapter=adapter(False)
    )
    peer = selection_fit(
        data, stage, permission, market=True, allow_synthetic=True, adapter=adapter(True)
    )
    for name in (
        "fit_keys",
        "validation_keys",
        "candidate_scaler",
        "candidate_tg0_floor",
        "refit_scaler",
        "refit_tg0_floor",
        "effective_train_weights",
        "effective_refit_weights",
        "train_exclusions",
        "validation_exclusions",
        "refit_exclusions",
    ):
        if control.evidence[name] != peer.evidence[name]:
            raise ValueError("MATCHED_RIDGE_POPULATION_FIT_IDENTITY_REQUIRED")
    if len(control.solution.coefficients) != 147 or len(peer.solution.coefficients) != 161:
        raise ValueError("MATCHED_RIDGE147_PEER161_REQUIRED")
    return (
        control,
        peer,
        {
            "scope": "ENGINEERING_SYNTHETIC_ONLY",
            "widths": (147, 161),
            "matched": identity(
                [control.evidence["fit_keys"], control.evidence["validation_keys"]]
            ),
            "code": peer_code_identity(),
            "source": identity([data_identity(data), history.evidence_id]),
            "neural_pairs": 0,
            "scientific_status": "NOT_ASSESSED_SCIENTIFIC",
        },
    )
