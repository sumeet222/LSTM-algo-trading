"""Coverage-driven amendment and equal-year uncertainty, without empirical fits."""

import numpy as np
import pandas as pd
import pytest

from lstm_data.hf20_mag_designa import limit, role_mask
from lstm_data.hf20_mag_designa_continue import bootstrap_equal_year, choose_candidate


def test_latest_qualifying_month_is_counts_only() -> None:
    options = [
        dict(month=7, sessions=57, slot_min=46),
        dict(month=6, sessions=80, slot_min=50),
        dict(month=5, sessions=100, slot_min=60),
    ]
    assert choose_candidate(options)["month"] == 7
    options[0]["sessions"] = 35
    options[1]["sessions"] = 42
    assert choose_candidate(options)["month"] == 5
    options[1]["sessions"] = 59
    options[1]["slot_min"] = 38
    assert choose_candidate(options)["month"] == 6


def test_may_failure_does_not_extend_to_april() -> None:
    options = [dict(month=m, sessions=49, slot_min=25) for m in (7, 6, 5)]
    with pytest.raises(ValueError, match="no July/June/May"):
        choose_candidate(options)
    options = [dict(month=m, sessions=50, slot_min=24) for m in (7, 6, 5)]
    with pytest.raises(ValueError):
        choose_candidate(options)


def test_earlier_initial_cutoff_keeps_selector_and_tail_separate() -> None:
    rows = pd.DataFrame(
        dict(
            session_date_et=["2021-04-30", "2021-05-14", "2021-10-12"],
            eligible=[True, True, True],
            label_maturity_utc=pd.to_datetime(
                ["2021-04-30T19:00Z", "2021-05-14T19:00Z", "2021-10-12T19:00Z"]
            ),
        )
    )
    first = np.array(["2021-04-19", "2021-05-03", "2021-10-01"])
    train = role_mask(rows, first, "2011-04-01", "2021-04-30")
    selector = role_mask(rows, first, "2021-05-01", "2021-09-30", "2021-04-30")
    cal = role_mask(rows, first, "2021-10-01", "2021-12-31", "2021-09-30")
    assert train.tolist() == [True, False, False]
    assert selector.tolist() == [False, True, False]
    assert cal.tolist() == [False, False, True]
    assert not (train & selector | selector & cal | train & cal).any()
    assert limit("2021-09-30") == pd.Timestamp("2021-10-01T00:00Z")


def test_equal_year_bootstrap_does_not_pool_unequal_session_counts() -> None:
    daily = {
        year: pd.Series(
            np.full(n, value), index=pd.date_range(f"{year}-01-01", periods=n).strftime("%Y-%m-%d")
        )
        for year, n, value in [(2021, 3, 1.0), (2022, 6, 2.0), (2023, 9, 3.0), (2024, 12, 4.0)]
    }
    result = bootstrap_equal_year(daily)
    assert result == dict(mean=2.5, low=2.5, high=2.5)
    assert result == bootstrap_equal_year(daily)
    with pytest.raises(ValueError, match="FOUR_VALID_YEARS"):
        bootstrap_equal_year({2021: daily[2021]})
