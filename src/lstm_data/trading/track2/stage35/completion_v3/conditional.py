"""Scenario populations and standalone yield-proxy schedule; never factual cash events."""

from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from .acquire import ROOT, write_once
from .actions import Action, Truth
from .fallback import complete_ordinary, yield_proxy_adjustment
from .inventory import write_jsonl
from .tapes import load_actions, midnight

D = Decimal


def conditional_population(actions: tuple[Action, ...], scenario: str) -> tuple[Action, ...]:
    lags = {
        "OBSERVED_ACTION_BASE": None,
        "CONDITIONAL_ORDINARY_IMPUTED": 30,
        "LOW_DIVIDEND_SENSITIVITY": 14,
        "HIGH_DIVIDEND_SENSITIVITY": 45,
    }
    if scenario not in lags:
        raise ValueError("SCENARIO_NOT_FROZEN")
    result = []
    for action in actions:
        if (
            action.action_type == "CASH_DIVIDEND"
            and action.status not in (Truth.CONFLICTED_HOLD, Truth.SPECIAL_ACTION_HOLD)
            and not action.special
        ):
            lag = lags[scenario]
            shift = (
                -1
                if scenario == "LOW_DIVIDEND_SENSITIVITY"
                else (1 if scenario == "HIGH_DIVIDEND_SENSITIVITY" else 0)
            )
            result.append(complete_ordinary(action, pay_lag=lag, ex_shift=shift) if lag else action)
        else:
            result.append(action)
    return tuple(result)


@dataclass(frozen=True)
class ProxyPeriod:
    symbol: str
    start: datetime
    end: datetime
    kind: str = "UNVERIFIED_DIVIDEND_YIELD_PROXY_STANDALONE_ONLY"
    baseline: Decimal = D(".015")
    low: Decimal = D(0)
    high: Decimal = D(".03")
    truth: str = "ASSUMED_YIELD_PROXY"
    cash_action: bool = False
    pretrade_NAV_input: bool = False


def proxy_schedule(
    symbol: str, year: int, actions: tuple[Action, ...], coverage_status: str
) -> tuple[ProxyPeriod, ...]:
    if coverage_status != "UNKNOWN":
        return ()
    if any(
        a.symbol == symbol
        and (
            a.action_type == "CASH_DIVIDEND"
            and a.ex_date
            and a.ex_date.year == year
            or a.status == Truth.NO_EVENT_VERIFIED
            and a.effective_date
            and a.effective_date.year == year
        )
        for a in actions
    ):
        return ()
    # This is a separate ex-post sensitivity population. Annual suppression never
    # enters runtime features, trading eligibility, size, raw prices or cash books.
    result = []
    at = date(year, 1, 1)
    while at.year == year:
        result.append(ProxyPeriod(symbol, midnight(at), midnight(at + timedelta(days=1))))
        at += timedelta(days=1)
    return tuple(result)


def standalone_adjustment(
    period: ProxyPeriod, signed_exposure: Decimal, exposure_available: datetime, rate: Decimal
) -> Decimal:
    if exposure_available > period.start:
        raise ValueError("FUTURE_EXPOSURE_IN_STANDALONE_PROXY")
    seconds = D(str((period.end - period.start).total_seconds()))
    return yield_proxy_adjustment(signed_exposure, seconds, annual_rate=rate)


def publish(root: Path = ROOT) -> None:
    import json

    from .inventory import digest

    actions = load_actions(root)
    coverage = json.loads((root / "ACTION_COVERAGE_V3.json").read_text())["ticker_years"]
    periods = tuple(
        p
        for row in coverage
        for p in proxy_schedule(row["symbol"], row["year"], actions, row["coverage_status"])
    )
    write_jsonl(root / "STANDALONE_PROXY_SCHEDULE_V3.jsonl", [asdict(p) for p in periods])
    write_once(
        root / "CONDITIONAL_POPULATIONS_V3.json",
        {
            "populations": {
                name: {
                    "actions": len(conditional_population(actions, name)),
                    "field_imputations": sum(
                        bool(a.inferred_fields) for a in conditional_population(actions, name)
                    ),
                    "supported_fields_preserved": True,
                }
                for name in (
                    "OBSERVED_ACTION_BASE",
                    "CONDITIONAL_ORDINARY_IMPUTED",
                    "LOW_DIVIDEND_SENSITIVITY",
                    "HIGH_DIVIDEND_SENSITIVITY",
                )
            },
            "unresolved_special_events": [
                a.event_id for a in actions if a.status == Truth.SPECIAL_ACTION_HOLD
            ],
            "proxy_daily_templates": len(periods),
            "proxy_amounts_computed": False,
            "proxy_schedule_sha256": digest(root / "STANDALONE_PROXY_SCHEDULE_V3.jsonl"),
            "proxy_security_years": 8,
            "suppression": "all supported cash and verified zero security-years",
            "historical_financial_backtest_run": False,
        },
    )
    write_jsonl(
        root / "CURRENCY_UNIT_ASSUMPTIONS_V3.jsonl",
        [
            {
                "event_id": a.event_id,
                "symbol": a.symbol,
                "currency": "USD",
                "status": "CONDITIONAL_US_COMMON_SHARE_DENOMINATION_NOT_PROVIDER_FIELD",
                "source_rate_basis": "Alpaca rate;raw contemporaneous share,not adjustedAmount",
                "reason": "provider has no explicit currency field;US common-stock scope",
                "source_refs": [s.source_id for s in a.sources],
                "review_required": True,
            }
            for a in actions
            if a.action_type == "CASH_DIVIDEND" and a.status == Truth.OBSERVED_UNCORROBORATED
        ],
    )


if __name__ == "__main__":
    publish()
