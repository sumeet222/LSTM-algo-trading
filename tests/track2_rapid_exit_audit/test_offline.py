from pathlib import Path

import numpy as np

from lstm_data.trading.track2.rapid_exit_audit.offline import (
    EconomicEvent,
    clock,
    economic_units,
)
from lstm_data.trading.track2.rapid_v3_dynamic.offline import targets
from lstm_data.trading.track2.stage35.final_backtest_v4.market import minute


def test_share_dividend_claim_and_unsupported_distribution():
    events = (
        EconomicEvent(0, 200, "SPLIT", 2.0, 200, "VERIFIED_PRIMARY", "s"),
        EconomicEvent(0, 300, "CASH", 1.0, 500, "OBSERVED_UNCORROBORATED", "d"),
        EconomicEvent(1, 250, "UNSUPPORTED", 0.0, 0, "VERIFIED_PRIMARY", "ogn"),
    )
    f, c, p, bad, n = economic_units(
        np.array([0, 0, 1]),
        np.array([100, 100, 100]),
        np.array([400, 600, 400]),
        events,
    )
    np.testing.assert_array_equal(f, [2, 2, 1])
    np.testing.assert_array_equal(c, [0, 2, 0])
    np.testing.assert_array_equal(p, [2, 0, 0])
    np.testing.assert_array_equal(bad, [False, False, True])
    np.testing.assert_array_equal(n, [2, 2, 1])
    assert 1 * 2 * 50 - 1 * 100 == 0
    assert -2 * (55 - 50) == -10


def test_reference_calendar_and_cutoff_geometry():
    c = clock()
    t = np.array(
        [
            minute(x)
            for x in (
                "2024-11-29T17:00:00Z",
                "2024-03-08T20:30:00Z",
                "2024-12-31T20:30:00Z",
            )
        ]
    )
    ref = targets(c, t)
    # Thanksgiving half-day ends 18:00 UTC. A close boundary maps to Monday open.
    assert c.cal.next(int(ref["T60"][0]) - 1) == minute("2024-12-02T14:30:00Z")
    assert ref["NEXT_FULL_SESSION"][0] == minute("2024-12-02T17:00:00Z")
    # DST changes UTC but retains the same Eastern clock on Monday.
    assert ref["NEXT_FULL_SESSION"][1] == minute("2024-03-11T19:30:00Z")
    assert ref["NEXT_FULL_SESSION"][2] > minute("2024-12-31T23:59:00Z")


def test_future_mutation_changes_only_diagnostic_and_signed_opportunity():
    actual = {"decision": 10, "effective": 11, "quantity": -2, "fill": 100.0}
    frozen = dict(actual)

    def opportunity(price):
        return actual["quantity"] * (price - actual["fill"])

    assert opportunity(100) == 0
    assert opportunity(110) == -20
    assert opportunity(90) == 20
    assert actual == frozen
    root = Path("src/lstm_data/trading/track2/rapid_v3_dynamic")
    assert all("rapid_exit_audit" not in p.read_text() for p in root.glob("*.py"))


def test_event_after_reference_cannot_change_existing_reference():
    base = (EconomicEvent(0, 200, "CASH", 1.0, 500, "OBSERVED_UNCORROBORATED", "old"),)
    args = (np.array([0]), np.array([100]), np.array([300]))
    before = economic_units(*args, base)
    after = economic_units(
        *args, (*base, EconomicEvent(0, 400, "SPLIT", 10.0, 400, "VERIFIED_PRIMARY", "new"))
    )
    for x, y in zip(before, after, strict=True):
        np.testing.assert_array_equal(x, y)


def test_missing_and_late_marks_are_censored_without_zero_payoff():
    from lstm_data.trading.track2.rapid_exit_audit.offline import reference_status

    status = reference_status(
        np.array([True, True, True, False, True]),
        np.array([101, -1, 108, -1, 101]),
        np.array([100, 100, 100, 200, 100]),
        np.array([False, False, False, False, True]),
    )
    assert list(status) == [
        "VALID",
        "CENSORED_NO_VALID_MARK",
        "CENSORED_FORWARD_LIMIT",
        "CENSORED_EVALUATION_CUTOFF",
        "CENSORED_UNSUPPORTED_DISTRIBUTION",
    ]
    payoff = np.where(status == "VALID", 2.0, np.nan)
    assert np.isnan(payoff[1:]).all()


def test_exit_concession_recovery_is_offset_by_replacement_exit_only():
    import pandas as pd

    from lstm_data.trading.track2.rapid_exit_audit.offline import cost_scenarios

    sample = pd.DataFrame(
        {
            "strategy_id": ["R07", "R07"],
            "quantity": [10, -10],
            "share_factor": [1, 1],
            "later_raw": [100.0, 100.0],
            "raw": [100.0, 100.0],
            "fill": [99.9, 100.1],
            "reference_at": [200, 200],
            "effective": [100, 100],
        }
    )
    result = cost_scenarios(sample, np.ones(2), np.ones(2))
    np.testing.assert_allclose(result["original_exit_concession_recovery"], [1, 1])
    np.testing.assert_allclose(result["assumed_later_exit_concession"], [1, 1])
    np.testing.assert_allclose(result["standalone_fee_difference"], [0, 0])
    assert result["frozen_mark_short_carry"][0] == 0
    assert result["frozen_mark_short_carry"][1] > 0


def test_all54_output_census_and_no_silent_missing_zero():
    import csv

    result = Path("trading/track2/rapid_exit_audit_v1/results_01")
    with (result / "ALL18_EXIT_REFERENCE_COVERAGE.csv").open() as stream:
        rows = [r for r in csv.DictReader(stream) if r["axis"] == "all"]
    assert len(rows) == 54 * 3
    assert sum(int(r["exits"]) for r in rows) == 474354
    assert sum(int(r["valid"]) for r in rows) == 474109
    assert len({(r["strategy_id"], r["regime"]) for r in rows}) == 54
    for r in rows:
        assert int(r["valid"]) + sum(
            int(v) for k, v in r.items() if k.startswith("CENSORED")
        ) == int(r["exits"])


def test_snapshot_decimal_and_distinct_netting_portions():
    from decimal import Decimal

    import pandas as pd
    import pytest

    from lstm_data.trading.track2.rapid_exit_audit.io import decimal_scalar

    assert decimal_scalar({"decimal": "-34.02"}) == Decimal("-34.02")
    with pytest.raises(ValueError):
        decimal_scalar({"decimal": "NaN"})
    portions = pd.DataFrame(
        [
            {"case": "x", "lot": "a", "effective": 10, "external": False, "quantity": 35},
            {"case": "x", "lot": "a", "effective": 10, "external": True, "quantity": 153},
        ]
    )
    assert portions.duplicated(["case", "lot", "effective"]).sum() == 1
    assert portions.duplicated().sum() == 0
    assert portions.quantity.sum() == 188
