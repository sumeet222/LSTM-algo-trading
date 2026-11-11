"""Independent year-end marks and action attribution from sealed case states."""

import argparse
import csv
import gzip
import json
from decimal import Decimal
from pathlib import Path

from lstm_data.trading.track2.rapid_v1.paths import canonical, digest, publish
from lstm_data.trading.track2.rapid_v1.state import decode
from lstm_data.trading.track2.rapid_v2_diagnostics.report import GROSS_BASIS, csv_write
from lstm_data.trading.track2.stage35.final_backtest_v5.special import Distribution

D = Decimal
ZERO = D(0)
TOL = D("1e-7")


def annual(run: Path, output: Path) -> None:
    completion = json.loads((run / "RUN_COMPLETION.json").read_text())
    results = Path(completion["results"])
    manifest = results / "MANIFEST.json"
    if digest(manifest) != completion["result_manifest_sha256"]:
        raise ValueError("RESULT_MANIFEST_DRIFT")
    files = json.loads(manifest.read_text())["result_files"]
    if any(digest(results / p) != h for p, h in files.items()):
        raise ValueError("RESULT_OUTPUT_DRIFT")
    observed = {}
    for file in ("HEADROOM_RESULTS.csv", "HORIZON_RESULTS.csv"):
        with (results / file).open() as stream:
            for r in csv.DictReader(stream):
                observed[r["strategy_id"] + "_" + r["variant"]] = r
    if len(observed) != 108:
        raise ValueError("SUMMARY_CASE_CENSUS")
    accounts = {}
    last_year = {}
    rows = []
    checks = {}
    states = sorted((run / "states").glob("*.json.gz"))
    if len(states) != 4:
        raise ValueError("ANNUAL_STATE_CENSUS")
    for path in states:
        envelope = json.loads(gzip.decompress(path.read_bytes()))
        body = envelope["body"]
        if envelope["sha256"] != canonical(body):
            raise ValueError("INVALID_ANNUAL_CHECKPOINT")
        state = decode(body["state"])
        decoded = decode(body["accounts"])
        if not isinstance(state, dict) or not isinstance(decoded, list):
            raise ValueError("CHECKPOINT_SCHEMA")
        if len(decoded) != 108:
            raise ValueError("CHECKPOINT_CASE_CENSUS")
        daily, distributions = state["daily_rows"], state["special"]
        if not isinstance(daily, dict) or not isinstance(distributions, dict):
            raise ValueError("CHECKPOINT_DAILY_OR_ACTION_SCHEMA")
        for n, a in enumerate(decoded):
            if not isinstance(a, dict):
                raise ValueError("CHECKPOINT_ACCOUNT_SCHEMA")
            key = a["arm"]
            row = observed[key]
            series = daily[key]
            if not isinstance(series, list) or not series or not isinstance(series[-1], dict):
                raise ValueError("CHECKPOINT_DAILY_ACCOUNT_SCHEMA")
            end = series[-1]
            if end["date"] != path.name[:10]:
                raise ValueError("ANNUAL_NAV_MARK_DATE")
            actions = a["dividend_cash"] + a["special_cash"] + end["claims"] + end["special"]
            special = distributions.get(n)
            if special is not None:
                if not isinstance(special, Distribution):
                    raise ValueError("CHECKPOINT_DISTRIBUTION_SCHEMA")
                actions += sum((v for _, v in special.cost_allocations), ZERO)
            commission = end["commission"]
            friction = end["friction"]
            borrow = end["borrow"]
            funding = end["funding"]
            cost = commission + friction + borrow + funding
            nav = end["nav"]
            start = last_year.get(key, (D(100000), ZERO, ZERO, ZERO, ZERO, ZERO, ZERO))
            (
                prior_nav,
                prior_gross,
                prior_action,
                prior_fee,
                prior_price,
                prior_borrow,
                prior_fund,
            ) = start
            status = row["status"]
            valid = nav is not None and end["status"] == "OBSERVED" and status != "HOLD"
            gross = nav - a["initial"] + cost - actions if valid else None
            gross_delta = (
                gross - prior_gross if gross is not None and prior_gross is not None else None
            )
            net = nav - prior_nav if valid and prior_nav is not None else None
            parts = {
                "annual_net_NAV_change_USD": net,
                "annual_gross_raw_price_PnL_USD": gross_delta,
                "annual_gross_action_value_USD": actions - prior_action,
                "annual_physical_commission_USD": commission - prior_fee,
                "annual_assumed_price_concession_USD": friction - prior_price,
                "annual_borrow_USD": borrow - prior_borrow,
                "annual_funding_USD": funding - prior_fund,
            }
            rows.append(
                {
                    "strategy_id": row["strategy_id"],
                    "variant": row["variant"],
                    "mode": row["mode"],
                    "status": status,
                    "year": end["date"][:4],
                    "last_market_session": end["date"],
                    "starting_NAV_USD": prior_nav,
                    "ending_NAV_USD": nav,
                    "gross_basis": GROSS_BASIS,
                    **parts,
                }
            )
            if gross_delta is not None and net is not None:
                bridge = gross_delta + actions - prior_action
                bridge -= (
                    commission
                    - prior_fee
                    + friction
                    - prior_price
                    + borrow
                    - prior_borrow
                    + funding
                    - prior_fund
                )
                if abs(bridge - net) > TOL:
                    raise ValueError("ANNUAL_MARKED_BRIDGE")
            last_year[key] = (nav, gross, actions, commission, friction, borrow, funding)
            if path == states[-1] and valid:
                if gross is None:
                    raise ValueError("MISSING_TERMINAL_GROSS")
                errors = [
                    abs(gross - D(row["gross_signed_price_PnL_USD"])),
                    abs(actions - D(row["gross_action_value_USD"])),
                ]
                if max(errors) > TOL:
                    raise ValueError(f"ANNUAL_VS_LOT_ATTRIBUTION:{key}:{errors}")
                accounts[key] = max(errors)
        checks[path.name] = {"sha256": digest(path), "cursor": state["last_completed"]}
    output.mkdir(exist_ok=False)
    csv_write(output / "ANNUAL_MARKED_BRIDGE.csv", rows)
    publish(
        output / "ANNUAL_MARKED_BRIDGE_RECEIPT.json",
        {
            "status": "PASS",
            "year_rows": len(rows),
            "terminal_accounts_compared": len(accounts),
            "maximum_terminal_lot_bridge_residual_USD": max(accounts.values(), default=ZERO),
            "state_files": checks,
            "result_manifest_sha256": digest(manifest),
            "code_sha256": digest(Path(__file__)),
            "annual_output_sha256": digest(output / "ANNUAL_MARKED_BRIDGE.csv"),
        },
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("run", type=Path)
    p.add_argument("output", type=Path)
    a = p.parse_args()
    annual(a.run, a.output)
