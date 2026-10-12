"""All score methods share one physical adapter; no label/exit input is consulted."""

from dataclasses import replace
from decimal import Decimal as D

import pandas as pd
import pytest

from lstm_data.baseline_fixtures import feature_input, proxy_offers
from lstm_data.baseline_inputs import forecast_adapter, momentum
from lstm_data.baseline_random import RandomOpportunity, draws, random_predictions
from lstm_data.baseline_ridge import RidgeModel, Solution
from lstm_data.p3_domain import MODE, Frictions, Permission, UniverseSpec
from lstm_data.p3_replay import ReplayFrame, replay


@pytest.mark.parametrize(
    "symbols", [("ONE", "TWO", "THREE", "FOUR", "FIVE"), ("TIN", "MAP", "FOX", "ORB", "ZEN")]
)
def test_typed_methods_physical_bridge_counterfactual_and_model_binding(symbols):
    u = UniverseSpec("SYN:BRIDGE", symbols)
    row = feature_input(u, day="2020-08-20")
    assert row.stock.scaler_ref is not None
    # Hand-specified one-coordinate synthetic model isolates bridge algebra;
    # actual five-candidate TG0 selection/refit has its separate integration proof.
    solution = Solution(0.0, (1.0,) + (0.0,) * 111, 1.0, 1.0, 0.0, 0.0, "SYNTHETIC_HAND_ORACLE")
    model = RidgeModel(
        u,
        solution,
        False,
        row.stock_scaler.window.fitted_at,
        row.stock_scaler.window,
        row.stock.scaler_ref,
        None,
        "SYN:TG0",
        "SYN:DESIGN",
        "SYN:HAND_MODEL",
        "SYNTHETIC",
    )
    momentum_pred = momentum(row, Permission(MODE), allow_synthetic=True)
    ridge_pred = model.predict(row, Permission(MODE), allow_synthetic=True)
    assert ridge_pred.scores == momentum_pred.scores == (2.0, 1.0, 0.0, -1.0, -2.0)
    op = (
        RandomOpportunity(
            u, "SYN:COMMON_OP", row.input_id, row.plan, row.plan.cutoff, True, "SYNTHETIC"
        ),
    )
    random_pred = random_predictions(
        op, draws(u, op, 0, Permission(MODE), allow_synthetic=True), Permission(MODE)
    )[0]
    for pred in (momentum_pred, ridge_pred, random_pred):
        f = forecast_adapter(pred, Permission(MODE), allow_synthetic=True)
        assert f.plan.entry is not None and f.plan.cutoff is not None and f.plan.exit is not None
        entry = proxy_offers(u, f.plan.entry, f.plan.cutoff)
        exit = proxy_offers(u, f.plan.exit, f.plan.cutoff + pd.Timedelta(hours=4))
        first = ReplayFrame(
            u, "SYN:ENTRY", f.plan.entry, tuple(o.reference for o in entry), entry, f
        )
        complete = ReplayFrame(u, "SYN:EXIT", f.plan.exit, tuple(o.reference for o in exit), exit)
        missing = replace(complete, offers=())
        a = replay(
            Permission(MODE), u, (first, complete), "A", Frictions(u), D(10000), f.plan.cutoff
        )
        b = replay(
            Permission(MODE), u, (first, missing), "A", Frictions(u), D(10000), f.plan.cutoff
        )
        assert [e for e in a.ledger.export() if e["at"] == f.plan.entry.isoformat()] == [
            e for e in b.ledger.export() if e["at"] == f.plan.entry.isoformat()
        ]
    with pytest.raises(ValueError):
        model.predict(
            replace(row, universe=UniverseSpec("SYN:WRONG", symbols[::-1])),
            Permission(MODE),
            allow_synthetic=True,
        )
