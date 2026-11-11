"""Risk arithmetic and settled-book boundaries; no market or model access."""

from decimal import Decimal

import numpy as np
import pandas as pd
import pytest

from lstm_data.trading.track2.final3_risk_attribution.analysis import ORIENTATION, cost_summary
from lstm_data.trading.track2.final3_risk_attribution.io import ARMS, POLICIES, col
from lstm_data.trading.track2.final3_risk_attribution.metrics import (
    drawdowns,
    nonexecutable_proxy,
    performance,
    simple_returns,
    tail,
)
from lstm_data.trading.track2.final3_risk_attribution.saved import near, validate_keys


def test_sharpe_sortino_and_annualization():
    r = np.array([0.01, -0.02, 0.03, 0.0])
    nav = 100000 * np.cumprod(1 + r)
    m, _ = performance(nav, ["2021-01-04", "2021-01-05", "2021-01-06", "2021-01-07"])
    assert m["Sharpe"] == pytest.approx(np.sqrt(252) * r.mean() / r.std(ddof=1))
    assert m["Sortino"] == pytest.approx(np.sqrt(252) * r.mean() / 0.01)
    assert m["annual_volatility"] == pytest.approx(np.sqrt(252) * r.std(ddof=1))
    assert m["net_PnL_USD"] == pytest.approx(nav[-1] - 100000)


def test_drawdown_includes_initial_and_recovery_ties():
    nav = np.array([90.0, 80.0, 100.0, 110.0, 99.0, 110.0, 100.0])
    m, e = drawdowns(nav, [str(x) for x in range(7)], 100.0)
    assert m["max_drawdown"] == pytest.approx(-0.2)
    assert m["longest_underwater_sessions"] == 2
    assert m["total_underwater_sessions"] == 4
    assert e[0]["time_to_trough_sessions"] == 2
    assert e[0]["recovery_date"] == "2"
    assert any(not x["recovered"] for x in e)


def test_tail_fixed_count_not_only_strictly_below_quantile():
    r = np.array([-0.1, -0.1, 0.0, 0.2, 0.3])
    t = tail(r, 0.21)
    assert t["tail_count"] == 2
    assert t["ES_loss"] == pytest.approx(0.1)
    assert t["indices"].tolist() == [0, 1]
    with pytest.raises(ValueError):
        tail(np.array([]), 0.05)


@pytest.mark.parametrize("bad", [[], [0.0], [-1.0], [np.nan], [np.inf]])
def test_nonpositive_missing_or_empty_wealth_holds(bad):
    with pytest.raises(ValueError):
        simple_returns(np.array(bad))


def test_zero_risk_denominators_are_not_infinite_scores():
    m, e = performance(np.array([100000.0, 100000.0]), ["2021-01-04", "2021-01-05"])
    assert m["Sharpe"] is None and m["Sortino"] is None
    assert m["max_drawdown"] == 0 and e == []
    assert nonexecutable_proxy(np.array([0.0, 0.0]), ["a", "b"], 0.1, 0.0, "MEAN_RTH_GROSS")[
        "status"
    ].startswith("REFUSED")


def test_partial_fill_fee_order_not_cohort_or_fill_count():
    p = pd.DataFrame(
        {
            "order_id": ["a", "a", "b"],
            "shares": [10, 5, -15],
            "external_price": [100.0, 100.0, 101.0],
            "commission": [1.0, 0.0, 1.0],
        }
    )
    m = cost_summary(p)
    assert m["physical_orders_recomputed"] == 2
    assert m["external_fill_rows"] == 3
    assert m["executed_physical_side_notional"] == 3015
    assert m["fraction_retail_orders_at_one_USD"] == 1


def test_fee_and_restricted_cash_not_double_counted():
    near(Decimal("100"), Decimal("80") + Decimal("20"), "cash_already_restricted")
    near(Decimal("7"), Decimal("10") + Decimal("1") - Decimal("2") - Decimal("2"), "gross_bridge")
    with pytest.raises(ValueError):
        near(Decimal("7"), Decimal("5"), "double_cost")


def test_account_population_join_census_and_duplicate_columns():
    correct = {(p, a) for p in POLICIES for a in ARMS}
    validate_keys(correct)
    with pytest.raises(ValueError):
        validate_keys({(p, "MICRO_PRO") for p in POLICIES})
    with pytest.raises(ValueError):
        col(pd.DataFrame([[1, 2]], columns=["arm", "arm"]), "arm")


def test_improvement_orientation():
    assert ORIENTATION["Sharpe"] * (0.4 - 0.3) > 0
    assert ORIENTATION["ES95_loss"] * (0.02 - 0.03) > 0
    assert ORIENTATION["drawdown_severity"] * (0.2 - 0.1) < 0


def test_future_suffix_cannot_change_earlier_risk_returns():
    original = np.array([100000.0, 99000.0, 101000.0, 102000.0])
    mutated = original.copy()
    mutated[-1] = 90000
    assert np.array_equal(simple_returns(original)[:3], simple_returns(mutated)[:3])
    # Only a report is calculated; neither helper produces orders, scores or fills.
    assert set(
        nonexecutable_proxy(
            simple_returns(original),
            ["2021-01-04", "2021-01-05", "2021-01-06", "2021-01-07"],
            0.2,
            0.1,
            "MEAN_RTH_GROSS",
        )
    ).isdisjoint({"orders", "fills"})


def test_source_fingerprint_refuses_drift_on_synthetic_file(tmp_path, monkeypatch):
    from lstm_data.trading.track2.final3_risk_attribution import io

    source = tmp_path / "synthetic_saved_input.json"
    source.write_text('{"nav": 100}')
    monkeypatch.setattr(io, "ROOT", tmp_path)
    io.publish(
        tmp_path / "SOURCE_REGISTER_BEFORE.json",
        {
            "files": [
                {
                    "path": str(source),
                    "sha256": io.digest(source),
                    "mtime_ns": source.stat().st_mtime_ns,
                }
            ]
        },
    )
    io.verify_inputs()
    source.write_text('{"nav": 101}')
    with pytest.raises(ValueError, match="HOLD_SOURCE_OR_ACCOUNT_RECONCILIATION"):
        io.verify_inputs()


def test_atomic_report_no_overwrite(tmp_path):
    from lstm_data.trading.track2.final3_risk_attribution.io import publish

    path = tmp_path / "receipt.json"
    publish(path, {"status": "FIRST"})
    with pytest.raises(FileExistsError):
        publish(path, {"status": "REPLACEMENT"})
    assert "FIRST" in path.read_text()
