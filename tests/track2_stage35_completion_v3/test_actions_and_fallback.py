"""Source normalization and all approved ordinary fallback branches; no economics."""

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from lstm_data.trading.track2.stage35.completion_v3.acquire import classify
from lstm_data.trading.track2.stage35.completion_v3.actions import (
    Action,
    Evidence,
    Truth,
    normalize_alpaca,
    normalize_nasdaq,
    reconcile,
)
from lstm_data.trading.track2.stage35.completion_v3.fallback import (
    assumed_pay,
    carry_amount,
    complete_ordinary,
    ex_from_record,
    recurring_candidates,
    yield_proxy_adjustment,
)

D = Decimal
E = Evidence("PRIMARY:one", "https://issuer.invalid/declaration", "a" * 64, "event", "2026-11-09")


def event(**fields) -> Action:
    return replace(
        Action(
            "e",
            "AAPL",
            "CASH_DIVIDEND",
            date(2024, 5, 10),
            date(2024, 5, 13),
            date(2024, 5, 16),
            D(".25"),
            Truth.VERIFIED_PRIMARY,
            (E,),
        ),
        **fields,
    )


@pytest.mark.parametrize(
    "http,data,expected",
    [
        (429, {}, "RATE_LIMITED"),
        (401, {}, "ACCESS_DENIED"),
        (403, {}, "ACCESS_DENIED"),
        (0, {}, "SOURCE_UNAVAILABLE"),
        (200, {"Information": "premium subscription required"}, "NOT_AVAILABLE_FREE"),
        (200, {"error": "api key required"}, "ACCESS_DENIED"),
        (
            200,
            {"non_json_body": "legal footer api key premium stocks"},
            "RESPONSE_RECEIVED_NOT_COMPLETENESS_PROOF",
        ),
    ],
)
def test_provider_status_not_html_marketing(http, data, expected):
    assert classify(http, data) == expected


@pytest.mark.parametrize(
    "record,ex",
    [
        ("2024-05-13", "2024-05-10"),
        ("2024-05-24", "2024-05-23"),
        ("2024-05-28", "2024-05-24"),
        ("2024-05-29", "2024-05-29"),
    ],
)
def test_settlement_transition(record, ex):
    assert ex_from_record(date.fromisoformat(record)) == date.fromisoformat(ex)


@pytest.mark.parametrize("record,special", [("2024-05-27", False), ("2024-05-29", True)])
def test_nonbusiness_and_special_not_inferred(record, special):
    with pytest.raises(ValueError):
        ex_from_record(date.fromisoformat(record), ordinary=not special)


def test_supported_apple_fields_immutable_in_all_pay_stresses():
    for lag in (14, 30, 45):
        assert complete_ordinary(event(), pay_lag=lag) is not None
        assert complete_ordinary(event(), pay_lag=lag) == event()


def test_missing_ex_and_pay_explicit_assumed_not_verified():
    inferred = complete_ordinary(event(ex_date=None, payable_date=None))
    assert inferred.ex_date == date(2024, 5, 10)
    assert inferred.payable_date == date(2024, 6, 10)
    assert inferred.status == Truth.ASSUMED_ORDINARY
    assert set(inferred.inferred_fields) == {"ex_date", "payable_date"}


def test_payment_next_bank_day_and_past_terminal_without_prices():
    assert assumed_pay(date(2024, 12, 6)) == date(2025, 1, 6)
    assert assumed_pay(date(2024, 3, 15), 14) == date(2024, 3, 29)  # Good Friday bank day


def test_empty_feed_is_not_nonpayer():
    with pytest.raises(ValueError, match="EMPTY_FEED"):
        event(status=Truth.NO_EVENT_VERIFIED).validate()
    assert normalize_alpaca({"corporate_actions": {"cash_dividends": []}}, E, ("AAPL",)) == ()


def test_provider_schema_change_and_empty_nasdaq():
    with pytest.raises(ValueError):
        normalize_alpaca({"corporate_actions": {"cash_dividends": {}}}, E, ("AAPL",))
    with pytest.raises(ValueError):
        normalize_nasdaq({}, E, "AAPL")
    assert normalize_nasdaq({"data": {"dividends": {"rows": None}}}, E, "AAPL") == ()


def test_split_pay_before_ex_is_not_cash_dividend():
    rows = {
        "corporate_actions": {
            "forward_splits": [
                {
                    "symbol": "AMZN",
                    "ex_date": "2022-06-06",
                    "payable_date": "2022-06-03",
                    "old_rate": 1,
                    "new_rate": 20,
                }
            ]
        }
    }
    assert normalize_alpaca(rows, E, ("AMZN",))[0].split_ratio_new_old == 20


def test_acquirer_does_not_receive_acquiree_merger_cash():
    rows = {
        "corporate_actions": {
            "cash_mergers": [
                {
                    "acquirer_symbol": "CSCO",
                    "acquiree_symbol": "ACIA",
                    "effective_date": "2021-03-01",
                    "rate": 115,
                }
            ]
        }
    }
    info = normalize_alpaca(rows, E, ("CSCO",))[0]
    assert info.amount is None
    assert info.effect_on_books == "NO_DIRECT_COMMON_HOLDER_ENTITLEMENT"


def test_repeated_page_deduplicates_not_two_sources():
    source = replace(E, source_id="ALPACA:page1")
    a = event(status=Truth.OBSERVED_UNCORROBORATED, sources=(source,))
    out = reconcile((a, a))
    assert len(out) == 1 and len(out[0].sources) == 1
    assert out[0].status == Truth.OBSERVED_UNCORROBORATED


def test_cross_source_conflict_is_hold_never_sum():
    a = event(status=Truth.OBSERVED_UNCORROBORATED)
    b = replace(a, amount=D(".3"), sources=(replace(E, source_id="SECOND:one"),))
    assert all(e.status == Truth.CONFLICTED_HOLD for e in reconcile((a, b)))
    b = replace(a, ex_date=date(2024, 5, 9), sources=(replace(E, source_id="SECOND:one"),))
    assert reconcile((a, b))[0].status == Truth.CONFLICTED_HOLD


def test_legitimate_two_component_cop_cash_not_blindly_merged():
    a = event(symbol="COP", status=Truth.OBSERVED_UNCORROBORATED)
    b = replace(a, amount=D(".5"), event_id="other")
    assert len(reconcile((a, b))) == 2


def test_inferred_cannot_be_upgraded_to_verified():
    with pytest.raises(ValueError):
        event(inferred_fields=("ex_date",)).validate()
    with pytest.raises(ValueError):
        event(economic_basis="TOTAL_RETURN_ADJUSTED").validate()


def test_amount_carry_only_past_and_splits_raw_units():
    prior = event(ex_date=date(2020, 8, 7), declared_at=date(2020, 7, 30), amount=D(".82"))
    missing = event(ex_date=date(2020, 11, 6), amount=None)
    split = event(
        action_type="SPLIT", ex_date=date(2020, 8, 31), split_ratio_new_old=D(4), amount=None
    )
    out = carry_amount(
        missing,
        (prior,),
        date(2020, 11, 6),
        interval_months=3,
        regular_series_evidence="verified regular series",
        known_splits=(split,),
    )
    assert out.amount == D(".205") and out.status == Truth.ASSUMED_ORDINARY
    future = replace(prior, ex_date=date(2021, 1, 1), amount=D(100))
    assert carry_amount(
        missing,
        (prior, future),
        date(2020, 11, 6),
        interval_months=3,
        regular_series_evidence="verified regular series",
        known_splits=(split,),
    ).amount == D(".205")


def test_amount_stale_and_special_hold():
    prior = event(ex_date=date(2023, 1, 1))
    with pytest.raises(ValueError, match="STALE"):
        carry_amount(
            event(amount=None),
            (prior,),
            date(2024, 5, 10),
            interval_months=3,
            regular_series_evidence="verified regular series",
        )
    with pytest.raises(ValueError):
        complete_ordinary(event(special=True))


@pytest.mark.parametrize("factor", [D(0), D(1), D("1.5")])
def test_amount_stresses_not_optimized(factor):
    prior = event(ex_date=date(2024, 2, 9))
    out = carry_amount(
        event(amount=None),
        (prior,),
        date(2024, 5, 10),
        interval_months=3,
        regular_series_evidence="verified regular series",
        factor=factor,
    )
    assert out.amount == D(".25") * factor


def test_recurrence_requires_payer_and_prior_support_and_respects_suspension():
    a = event(ex_date=date(2023, 11, 10), event_id="old")
    b = event(ex_date=date(2024, 2, 9), event_id="new")
    out = recurring_candidates(
        "AAPL",
        (a, b),
        date(2024, 5, 1),
        date(2024, 11, 30),
        interval_months=3,
        payer_evidence="two issuer declarations",
    )
    assert out and len(out) <= 2
    assert all(e.status == Truth.ASSUMED_ORDINARY for e in out)
    with pytest.raises(ValueError):
        recurring_candidates(
            "AAPL", (b,), date(2024, 5, 1), date(2024, 11, 30), interval_months=3, payer_evidence=""
        )
    assert (
        recurring_candidates(
            "AAPL",
            (a, b),
            date(2024, 5, 1),
            date(2024, 11, 30),
            interval_months=3,
            payer_evidence="issuer",
            suspension_known_at=date(2024, 5, 1),
        )
        == ()
    )


def test_proxy_standalone_and_no_overlap_or_verified_zero():
    assert yield_proxy_adjustment(D(1000), D(365 * 86400)) == 15
    assert yield_proxy_adjustment(D(-1000), D(365 * 86400)) == -15
    assert yield_proxy_adjustment(D(1000), D(1000), verified_distribution_overlap=True) == 0
    assert yield_proxy_adjustment(D(1000), D(1000), verified_nonpayer=True) == 0


def test_recurring_assumption_keeps_payer_reference_and_pay_rule():
    a = event(ex_date=date(2023, 11, 10), event_id="a")
    b = event(ex_date=date(2024, 2, 9), event_id="b")
    output = recurring_candidates(
        "AAPL",
        (a, b),
        date(2024, 5, 1),
        date(2024, 8, 31),
        interval_months=3,
        payer_evidence="issuer regular-series history",
    )
    assert output
    params = dict(output[0].assumption_params)
    assert params["reference_event"] == "b" and params["calendar_lag"] == "30"
    assert params["payer_evidence"] == "issuer regular-series history"


def test_proxy_daily_templates_never_cash_actions_and_dst_elapsed_time():
    from lstm_data.trading.track2.stage35.completion_v3.conditional import (
        proxy_schedule,
        standalone_adjustment,
    )

    unknown = proxy_schedule("AMD", 2024, (), "UNKNOWN")
    assert len(unknown) == 366
    assert not any(p.cash_action or p.pretrade_NAV_input for p in unknown)
    assert sum((p.end - p.start).total_seconds() for p in unknown) == 366 * 86400
    assert proxy_schedule("AAPL", 2024, (event(),), "UNKNOWN") == ()
    assert proxy_schedule("TSLA", 2024, (), "NO_EVENT_VERIFIED") == ()
    p = unknown[0]
    assert standalone_adjustment(p, D(1000), p.start, D(".015")) == D(1000) * D(".015") / 365
    with pytest.raises(ValueError, match="FUTURE_EXPOSURE"):
        standalone_adjustment(p, D(1000), p.end, D(".015"))


def test_wrong_issuer_and_prefix_cop_special_not_ordinary():
    import json
    from pathlib import Path

    facts = json.loads(Path("configs/hf1m_p019_verified_event_facts_v1.json").read_text())
    cop = next(r for r in facts["events"] if r["ticker"] == "COP" and r["kind"] == "SPINOFF")
    assert cop["date"] == "2012-05-01" and cop["factor_denominator"] is None
    with pytest.raises(ValueError, match="ISSUER"):
        event(action_type="SPINOFF", symbol="AAPL", sub_type="OGN_PER_MRK_0.1").validate()
    with pytest.raises(ValueError, match="EXCLUDES_SPECIAL"):
        complete_ordinary(event(symbol="COP", action_type="SPINOFF", special=True))


@pytest.mark.parametrize(
    "shift,expected", [(-1, "2024-05-09"), (0, "2024-05-10"), (1, "2024-05-13")]
)
def test_only_inferred_exdate_stressed(shift, expected):
    inferred = complete_ordinary(event(ex_date=None), ex_shift=shift)
    assert inferred.ex_date == date.fromisoformat(expected)
    assert complete_ordinary(event(), ex_shift=shift) == event()
