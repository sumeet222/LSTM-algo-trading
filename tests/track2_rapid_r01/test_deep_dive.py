from dataclasses import replace
from decimal import Decimal as D

import numpy as np
import pandas as pd
import pytest

from lstm_data.trading.track2.rapid_r01_deep_dive import (
    DEFAULT,
    csv_at,
    dollars,
    drawdown,
    entry_units,
    infer_ticket,
    json_at,
    near,
)
from lstm_data.trading.track2.rapid_v1.shared_features import FeatureCache
from lstm_data.trading.track2.rapid_v1.strategies import evaluate
from lstm_data.trading.track2.rapid_v3_dynamic.policy import scores


def test_money_subtracts_raw_to_execution_concession_once():
    row = {
        "gross_signed_price_PnL_USD": "120.50",
        "gross_action_value_USD": "-3.25",
        "commission_USD": "2",
        "assumed_spread_USD": "1.10",
        "assumed_impact_USD": "1.10",
        "borrow_USD": "0.40",
        "funding_USD": "0.00",
    }
    assert dollars(row) == (D("112.65"), D("4.60"))
    with pytest.raises(ValueError, match="BROKEN"):
        near(D("120.50"), D("120.49"), "BROKEN")


def test_ticket_sides_and_fractional_old_unit_after_split():
    assert infer_ticket(20, D(100)) == (D("100.10"), D("1.00"), D("2.00"))
    assert infer_ticket(-20, D(100)) == (D("99.90"), D("1.00"), D("2.00"))
    assert infer_ticket(250, D(100))[1] == D("1.25")
    splits = [(17, "2022-08-25", 3)]
    old = [entry_units(q, 17, "2022-08-23", "2022-08-26", splits) for q in (-10, -5)]
    assert sum(old) == -5
    assert entry_units(-10, 17, "2022-08-25", "2022-08-26", splits) == -10


def test_drawdown_recovers_from_seed_and_does_not_reset():
    result = drawdown(
        pd.Series([102, 97, 98, 102, 96, 94]),
        pd.Series(["a", "b", "c", "d", "e", "f"]),
        100.0,
    )
    assert result["max_drawdown"] == pytest.approx(94 / 102 - 1)
    assert result["dd_peak"] == "d"
    assert result["dd_trough"] == "f"
    assert result["dd_recovery"] == "UNRECOVERED"
    assert result["underwater_sessions"] == 2


def test_frozen_r01_rank_and_signal_ignore_outcomes():
    from pathlib import Path

    seal = json_at(DEFAULT / "R01_INPUT_SEAL.json")
    cache = FeatureCache(Path(seal["cache"]))
    f = cache.frames("2021-01-04")[1]
    original = evaluate("R01", f)
    assert original.scheduled and len(original.intents) == 4
    assert f.prior_available < f.decision and f.latest_observation_end + 2 == f.decision
    signed, ranked = scores("R01", f)
    for intent in original.intents:
        j, side = intent.tickers[0], intent.signs[0]
        assert side * ranked[j] > 0 and intent.strength == pytest.approx(abs(signed[j]))
        assert np.sum(ranked * side > ranked[j] * side) <= 1
    perturbed = replace(f, values={**f.values, "future_return": np.full(20, 1000.0)})
    assert evaluate("R01", perturbed) == original
    with pytest.raises(ValueError, match="FEATURE_NOT_RECEIVED"):
        evaluate("R01", replace(f, prior_available=f.decision + 1))


def test_saved_match_and_risk_count_definitions():
    root = DEFAULT / "extraction_02"
    opportunity = csv_at(root / "R01_OPPORTUNITY_MATCH.csv")
    keys = {(r["origin"], r["ticker"], r["side"], r["lineage"]) for r in opportunity}
    assert len(keys) == len(opportunity) == 832
    assert sum(r["membership"] == "CONSERVATIVE+STANDARD+HIGH_RISK" for r in opportunity) == 438
    for row in csv_at(root / "R01_RECONCILIATION.csv"):
        assert int(row["scheduled_final_exits"]) + int(row["risk_final_exits"]) == int(
            row["closed_cohorts"]
        )
        assert (
            0
            == int(row["early_exits"])
            < int(row["risk_before_240"])
            < int(row["risk_closed_cohorts"])
        )
        assert int(row["risk_closed_cohorts"]) == int(row["cohorts_with_risk_fill"])
