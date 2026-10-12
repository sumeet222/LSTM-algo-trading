"""Reproducible oracles and independent ledger reconstruction, no raw input."""

from decimal import Decimal as D

import pytest

from lstm_data.p3_audit import evidence, reconstruct, toy_engine
from lstm_data.p3_domain import UniverseSpec


def test_audit_oracles_and_distinct_24_paths():
    u = UniverseSpec("audit-fixture", ("ONE", "TWO", "THREE", "FOUR", "FIVE"))
    result = evidence(u)
    assert all(row["status"] == "PASS" for row in result["expected_vs_actual"])
    assert len(result["matrix"]) == 24
    assert len({row["trace_id"] for row in result["matrix"]}) == 24
    assert result["traces"]["OVERNIGHT"]["events"][-1]["payload"]["NAV"] is None


def test_reconstruction_detects_broken_cash_sequence():
    u = UniverseSpec("audit-fixture", ("ONE", "TWO", "THREE", "FOUR", "FIVE"))
    e = toy_engine(u)
    e.book.debit(D(2), e.book.as_of, "SYN:BORROW_FIXTURE", {})
    trace = e.ledger.export()
    assert reconstruct(trace, u)["cash"] == 9998
    trace[-1]["payload"]["cash_before"] = "9999"
    with pytest.raises(AssertionError):
        reconstruct(trace, u)
