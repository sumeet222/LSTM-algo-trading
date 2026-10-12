"""Portable synthetic baseline/benchmark evidence; never loads historical panels."""

from __future__ import annotations

import argparse
from decimal import Decimal
from pathlib import Path

import pandas as pd

from .baseline_authority import verify
from .baseline_benchmarks import BuyAndHold, CashControl, OpeningOffer
from .baseline_fit import select_and_refit
from .baseline_fixtures import feature_input, proxy_offers, random_fixture, ridge_data
from .baseline_inputs import forecast_adapter, momentum
from .baseline_random import path_script, replay_scenario
from .config import write_json
from .labels import UNIVERSE
from .p3_audit import reconstruct
from .p3_domain import MODE, Frictions, Permission, PriceReference, UniverseSpec
from .p3_events import json_value
from .p3_execution import ExecutionOffer

D = Decimal


def opening_rows(benchmark: BuyAndHold, at, price=D(100)):
    return tuple(
        OpeningOffer(
            benchmark.universe,
            ExecutionOffer(
                benchmark.universe,
                PriceReference(
                    benchmark.universe,
                    s,
                    price,
                    at,
                    at,
                    "SYN:OPEN:" + s + at.isoformat(),
                    "SYNTHETIC_MINUTE_EVENT",
                    benchmark.engine.book.share_basis(s),
                ),
            ),
            "open",
            "SYNTHETIC",
        )
        for s in benchmark.universe.symbols
    )


def engineering_evidence(universe: UniverseSpec, permission: Permission) -> dict:
    proof = verify(permission)
    data = ridge_data(universe)
    own = select_and_refit(data, "WF1", permission, market=False, allow_synthetic=True)
    market = select_and_refit(data, "WF1", permission, market=True, allow_synthetic=True)
    row = feature_input(universe, day="2023-07-20", latest=(2.0, 1.0, 0.0, -1.0, -2.0))
    from .market_features import MarketVector

    asof_market = tuple(
        MarketVector(
            step.end,
            (0.0, 0.0, 0.0, 0.0, 0.0),
            "VECTOR_VALID",
            ("SYN:ASOF_MARKET:" + step.end.isoformat(),),
            "SYNTHETIC",
        )
        for step in row.stock.steps
    )
    market_prep = market.preparation.with_market_history(
        asof_market, permission, allow_synthetic=True
    )
    processed = own.preparation.apply(row, "ASOF")
    predictions = (
        momentum(processed, permission, allow_synthetic=True),
        own.model.predict(processed, permission, allow_synthetic=True),
        market.model.predict(market_prep.apply(row, "ASOF"), permission, allow_synthetic=True),
    )
    integrated = []
    from .p3_domain import Forecast
    from .p3_replay import ReplayFrame, replay

    for pred in predictions:
        f: Forecast = forecast_adapter(pred, permission, allow_synthetic=True)
        assert f.plan.entry is not None and f.plan.cutoff is not None and f.plan.exit is not None
        entries = proxy_offers(universe, f.plan.entry, f.plan.cutoff)
        exits = proxy_offers(universe, f.plan.exit, f.plan.cutoff + pd.Timedelta(hours=4))
        frames = (
            ReplayFrame(
                universe,
                "SYN:INTEGRATION_ENTRY",
                f.plan.entry,
                tuple(o.reference for o in entries),
                entries,
                f,
            ),
            ReplayFrame(
                universe,
                "SYN:INTEGRATION_EXIT",
                f.plan.exit,
                tuple(o.reference for o in exits),
                exits,
            ),
        )
        for policy in ("A", "B"):
            e = replay(
                permission, universe, frames, policy, Frictions(universe), D(10000), f.plan.cutoff
            )
            recovered = reconstruct(e.ledger.export(), universe)
            assert recovered["cash"] == e.book.cash and recovered["shares"] == e.book.balances
            integrated.append(
                {
                    "method": pred.method,
                    "policy": policy,
                    "prediction": json_value(pred),
                    "forecast_id": f.forecast_id,
                    "events": e.ledger.export(),
                    "trace_id": e.ledger.trace_id,
                    "reconstructed": json_value(recovered),
                }
            )
    assert row.plan.cutoff is not None
    cash = CashControl(universe, permission, D(10000), row.plan.cutoff, allow_synthetic=True)
    benches = []
    for cost, capital in ((0, 10000), (5, 10005), (10, 10010)):
        bh = BuyAndHold(
            universe,
            permission,
            Frictions(universe, D(cost)),
            D(capital),
            f"SYN:BENCH:{cost}",
            "2020-08-03",
            "2020-08-03",
            allow_synthetic=True,
        )
        assert bh.attempt_entry(bh.start, opening_rows(bh, bh.start))
        entry_cash = bh.engine.book.cash
        entry_fee = bh.engine.book.execution_fees
        assert bh.attempt_terminal(bh.terminal, opening_rows(bh, bh.terminal))
        actual = reconstruct(bh.engine.ledger.export(), universe)
        assert actual["cash"] == bh.engine.book.cash
        benches.append(
            {
                "cost": cost,
                "initial_equity": capital,
                "shares_each": 20,
                "entry_cash": str(entry_cash),
                "entry_fee": str(entry_fee),
                "ending_cash": str(bh.engine.book.cash),
                "expected_cash": str(D(10000 - cost)),
                "events": bh.engine.ledger.export(),
                "trace_id": bh.engine.ledger.trace_id,
                "status": "PASS" if bh.engine.book.cash == D(10000 - cost) else "CORRECT",
            }
        )
    opportunities, template, start = random_fixture(universe)
    random_examples = []
    for path in (0, 499, 999):
        script, path_draws = path_script(universe, opportunities, template, path, permission)
        traces = []
        for policy in ("A", "B"):
            for cost in (0, 2, 5, 10):
                for borrow in (D(0), D(".005"), D(".03")):
                    e = replay_scenario(
                        permission, universe, script, policy, cost, borrow, D(10000), start
                    )
                    actual = reconstruct(e.ledger.export(), universe)
                    assert actual["cash"] == e.book.cash and actual["shares"] == e.book.balances
                    traces.append(
                        {
                            "policy": policy,
                            "cost": cost,
                            "borrow": str(borrow),
                            "hash": e.ledger.trace_id,
                            "cash": str(e.book.cash),
                            "fees": str(e.book.execution_fees),
                            "reconstruction": "PASS",
                        }
                    )
        random_examples.append(
            {"path_id": path, "draws": json_value(path_draws), "scenarios": traces}
        )
    return {
        "scope": "SYNTHETIC_ONLY",
        "universe": json_value(universe),
        "authority": proof,
        "ridge_own": {
            "solution": json_value(own.model.solution),
            "selection": own.evidence,
            "candidates": own.candidates,
            "model_id": own.model.model_id,
        },
        "ridge_market": {
            "solution": json_value(market.model.solution),
            "selection": market.evidence,
            "candidates": market.candidates,
            "model_id": market.model.model_id,
        },
        "integrated": integrated,
        "cash_control": json_value(cash.valuation(row.plan.cutoff)),
        "buy_hold": benches,
        "random_examples": random_examples,
        "scientific_status": "HOLD",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=[MODE], required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    permission = Permission(args.mode)
    verify(permission)
    if (args.out / "baseline_evidence.json").exists():
        raise ValueError("EVIDENCE_EXISTS_USE_NEW_DIRECTORY")
    u = UniverseSpec("SYN:PRIMARY_BASELINES:v1", UNIVERSE)
    payload = engineering_evidence(u, permission)
    write_json(args.out / "baseline_evidence.json", payload)
    print("SYNTHETIC_ONLY: momentum/ridge/benchmark handoff; scientific activation HOLD")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
