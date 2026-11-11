"""Frozen rank mechanics and explicit non-hybrid policy identities."""

import pytest

from lstm_data.trading.track2.final_directional_slate.common import POLICIES, WEIGHTS
from lstm_data.trading.track2.final_directional_slate.comparison import percentile


def test_exact_ids_and_family_dependency():
    assert set(POLICIES) == {"F1", "F2", "F3", "F4", "F5"}
    assert POLICIES["F1"]["family"] == POLICIES["F2"]["family"] == "R01"
    assert POLICIES["F2"]["headroom"] == "1"
    assert POLICIES["F3"]["engine"] == "V2_FIXED" and POLICIES["F3"]["horizon"] == 480
    assert POLICIES["F4"]["engine"] == "V3_DYNAMIC" and POLICIES["F4"]["horizon"] == 10
    assert POLICIES["F5"]["change"] == "TWO_DISTINCT_VALID_EVENT_CHECKS"


def test_percentile_exact_ties_and_weight_total():
    assert percentile([1.0, 2.0, 3.0]) == [0.0, 0.5, 1.0]
    assert percentile([1.0, 1.0, 3.0]) == [0.25, 0.25, 1.0]
    assert percentile([1.0, 1.0, 1.0]) == [0.5, 0.5, 0.5]
    assert percentile([9.0]) == [0.5]
    assert sum(WEIGHTS.values()) == 1
    with pytest.raises(ValueError, match="RANKING_HOLD"):
        percentile([1.0, float("nan")])
