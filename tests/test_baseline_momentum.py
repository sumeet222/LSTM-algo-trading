"""Own latest scaled M1, causal masks, universe and shared trading bridge."""

from dataclasses import replace
from decimal import Decimal as D

import pandas as pd
import pytest

from lstm_data.baseline_fixtures import feature_input, proxy_offers
from lstm_data.baseline_inputs import forecast_adapter, momentum
from lstm_data.p3_domain import MODE, Frictions, Permission, UniverseSpec
from lstm_data.p3_engine import PortfolioEngine
from lstm_data.p3_policy import Policy


@pytest.mark.parametrize(
    "names", [("AAPL", "JPM", "JNJ", "WMT", "CAT"), ("FOX", "ZEN", "MAP", "ORB", "TIN")]
)
@pytest.mark.parametrize(
    "scores,pair,constant",
    [
        ((2.0, 1.0, 0.0, -1.0, -2.0), (0, 4), False),
        ((-1.0, -2.0, -3.0, -4.0, -5.0), (0, 4), False),
        ((1.0, 1.0, 0.0, 0.0, 0.0), (0, 4), False),
        ((3.0,) * 5, (0, 4), True),
    ],
)
def test_hand_ranked_m1_and_both_policies(names, scores, pair, constant):
    u = UniverseSpec("SYN:m1-v1", names)
    row = feature_input(u, latest=scores)
    p = momentum(row, Permission(MODE), allow_synthetic=True)
    f = forecast_adapter(p, Permission(MODE), allow_synthetic=True)
    assert p.scores == scores and f.pair == (names[pair[0]], names[pair[1]])
    assert (p.ranking_status == "CONSTANT_PREDICTION") is constant
    assert row.plan.entry is not None and row.plan.cutoff is not None
    offers = proxy_offers(u, row.plan.entry, row.plan.cutoff)
    for policy in ("A", "B"):
        e = PortfolioEngine(
            u, Permission(MODE), Policy(u, policy), Frictions(u), D(10000), row.plan.cutoff
        )
        assert e.enter(f, row.plan.entry, offers, tuple(o.reference for o in offers))
        assert e.book.quantity(f.pair[0]) == D("24.75")


def test_explicit_synthetic_context_shape_order_publication_scaler_guard():
    u = UniverseSpec("SYN:v1", ("ONE", "TWO", "THREE", "FOUR", "FIVE"))
    row = feature_input(u)
    with pytest.raises(ValueError):
        momentum(row, Permission(MODE))
    bads = [
        replace(row, basis="DOCUMENTED"),
        replace(row, stock=replace(row.stock, symbols=u.symbols[::-1])),
        replace(row, stock=replace(row.stock, values=row.stock.values[:-1])),
        replace(row, stock=replace(row.stock, application_context="HISTORICAL_TRAINING")),
        replace(row, stock=replace(row.stock, scaler_ref="wrong")),
    ]
    mask = row.stock.mask[0][:-1] + ((False,) + (True,) * 15,)
    bads.append(replace(row, stock=replace(row.stock, mask=(mask,) + row.stock.mask[1:])))
    clocks = row.available_at[0][:-1] + ((None,) + row.available_at[0][-1][1:],)
    bads.append(replace(row, available_at=(clocks,) + row.available_at[1:]))
    clocks2 = row.available_at[0][:-1] + (
        (row.stock.steps[-1].end + pd.Timedelta(minutes=1),) + row.available_at[0][-1][1:],
    )
    bads.append(replace(row, available_at=(clocks2,) + row.available_at[1:]))
    for bad in bads:
        with pytest.raises(ValueError):
            momentum(bad, Permission(MODE), allow_synthetic=True)
    with pytest.raises(ValueError):
        momentum(row, Permission("EMPIRICAL"), allow_synthetic=True)


def test_input_ordered_steps_cannot_compact_missing_bar():
    row = feature_input(UniverseSpec("SYN:v1", ("ONE", "TWO", "THREE", "FOUR", "FIVE")))
    changed = replace(row.stock, steps=row.stock.steps[1:] + (row.stock.steps[-1],))
    with pytest.raises(ValueError, match="SCHEDULED"):
        momentum(replace(row, stock=changed), Permission(MODE), allow_synthetic=True)
