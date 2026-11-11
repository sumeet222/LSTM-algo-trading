"""Small live checks and immutable evidence; no financial-signature ceremony."""

import json
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from ..stage35.final_backtest_v4.book import Account as FrozenAccount
from ..stage35.final_backtest_v4.market import minute
from ..stage35.final_backtest_v4.protocol import Scenario
from ..stage35.final_backtest_v5.execution import disposition
from .costs import CostReference
from .paths import ROOT, canonical, digest, publish
from .portfolio import FastAccount, Lot, Order, Request
from .sources import RawMarket

D = Decimal


def preserve_check(path: Path) -> dict:
    baseline = json.loads((ROOT / "audits/FROZEN_BOUNDARY_BASELINE.json").read_text())

    def check(row):
        p = Path(row["path"])
        s = p.stat()
        h = digest(p)
        return (
            None
            if h == row["sha256"] and s.st_mtime_ns == row["mtime_ns"]
            else {
                "path": str(p),
                "sha256_before": row["sha256"],
                "sha256_after": h,
                "mtime_before": row["mtime_ns"],
                "mtime_after": s.st_mtime_ns,
                "Finder_metadata_only": p.name == ".DS_Store",
            }
        )

    t = time.monotonic()
    with ThreadPoolExecutor(max_workers=4) as pool:
        changes = [r for r in pool.map(check, baseline["files"]) if r]
    material = [r for r in changes if not r["Finder_metadata_only"]]
    result = {
        "status": "HOLD" if material else "PASS_RESEARCH_BYTES_WITH_DISCLOSED_FINDER_METADATA",
        "files_checked": baseline["file_count"],
        "changes_since_rapid_start": changes,
        "preexisting_V5_metadata_drift": baseline["preexisting_differences"],
        "material_changes": material,
        "elapsed_seconds": time.monotonic() - t,
    }
    publish(path, result)
    if material:
        raise ValueError("FROZEN_MATERIAL_DRIFT")
    return result


def source_kernel_parity(path: Path) -> dict:
    """Actual AVGO source, identical seeded intents, exact tested V5 accountant.

    This is kernel parity, not whole-portfolio or new-frequency-policy parity.
    The tiny legacy requests intentionally do not represent retail $2000 entries.
    """
    market = RawMarket("2021-06-09", "2021-06-09")
    day = next(market.days())
    j = 16
    effective = minute("2021-06-09T16:33:00Z")
    later = effective + 1
    first = int(effective - day.starts[0])
    second = first + 1
    if day.valid[first, j] or not day.valid[second, j]:
        raise ValueError("AVGO_SOURCE_WITNESS_CHANGED")
    rows = []
    for strategy, amount, old in [("LEGACY_EQUAL", 2, 8), ("LEGACY_S2C", 3, 10)]:
        frozen = FrozenAccount(strategy, "kernel", Scenario())
        fast = FastAccount(strategy, "RETAIL_CONSERVATIVE", Scenario())
        for account in (frozen, fast):
            seed_origin = minute("2021-06-09T15:30:00Z")
            seed_prior = int(seed_origin - 1 - day.starts[0])
            if not day.valid[seed_prior, j]:
                raise ValueError("PARITY_SEED_REFERENCE_MISSING")
            account.prices[j] = D(str(day.closes[seed_prior, j]))
            account.marks_at[j] = seed_origin
            seed_end = minute(
                market.clock.endpoint(datetime.fromtimestamp(seed_origin * 60, timezone.utc))
            )
            seed = Lot(
                "old", j, seed_origin, seed_end, seed_origin + 10, -1, -old, D(1), pending=D(-old)
            )
            account.lots[seed.key] = seed
            account.refresh()
            order = Order(
                "seed",
                j,
                seed_origin + 2,
                seed_origin + 3,
                (Request("old", D(-old), "ENTRY"),),
                D(-old),
                seed_origin + 1,
                seed_origin + 10,
            )
            if isinstance(account, FastAccount):
                account.cost_references[order.key] = CostReference(
                    "RETAIL_CONSERVATIVE", available_at=order.decision
                )
            seed_index = int(seed_origin + 3 - day.starts[0])
            if not day.valid[seed_index, j]:
                raise ValueError("PARITY_SEED_BAR_MISSING")
            account.fill(order, D(str(day.opens[seed_index, j])), seed_origin + 6, seed_origin + 3)
            account.prices[j] = D(str(day.closes[first - 4, j]))
            account.marks_at[j] = effective - 3
            new_end = minute(
                market.clock.endpoint(datetime.fromtimestamp((effective - 3) * 60, timezone.utc))
            )
            account.lots["new"] = Lot(
                "new",
                j,
                effective - 3,
                new_end,
                effective + 7,
                -1,
                -amount,
                D(1),
                pending=D(-amount),
            )
            account.refresh()
        order_args = (
            "pending",
            j,
            effective - 1,
            effective,
            (Request("new", D(-amount), "ENTRY"),),
            D(-amount),
            effective - 2,
            effective + 7,
        )
        one, two = Order(*order_args), Order(*order_args)
        fast.cost_references[two.key] = CostReference(
            "RETAIL_CONSERVATIVE", available_at=two.decision
        )
        if disposition(one, effective, effective + 3, 2, False) != "WAIT":
            raise ValueError("EXACT_MISSING_BAR_NOT_PENDING")
        before = (fast.cash, fast.restricted(), int(fast.quantity[j]))
        price = D(str(day.opens[second, j]))
        frozen.fill(one, price, later + 3, later)
        fast.fill(two, price, later + 3, later)
        for attr in (
            "cash",
            "commission",
            "friction",
            "physical_basis",
            "physical_realized",
            "claims",
            "abs_virtual",
            "quantity",
        ):
            a, b = getattr(frozen, attr), getattr(fast, attr)
            if hasattr(a, "tolist"):
                a, b = a.tolist(), b.tolist()
            if a != b:
                raise ValueError("FROZEN_KERNEL_PARITY:" + attr)
        if {k: asdict(v) for k, v in frozen.lots.items()} != {
            k: asdict(v) for k, v in fast.lots.items()
        }:
            raise ValueError("VIRTUAL_LOT_PARITY")
        rows.append(
            {
                "label": strategy,
                "signed_request": -amount,
                "missing_minute_UTC": "2021-06-09T16:33:00Z",
                "actual_effective_UTC": "2021-06-09T16:34:00Z",
                "available_posted_UTC": "2021-06-09T16:37:00Z",
                "raw_price": str(price),
                "external_price": str(fast.stats.physical_rows[-1]["external_price"]),
                "commission": str(two.paid_fee),
                "physical_before": before[2],
                "physical_after": int(fast.quantity[j]),
                "cash_delta": str(fast.cash - before[0]),
                "restricted_delta": str(fast.restricted() - before[1]),
                "source": day.source_hash,
                "scope": (
                    "Identical-intent kernel parity; "
                    "V5 portfolio and default $2000 retail selection differ."
                ),
            }
        )
    result = {
        "status": "PASS",
        "cases": rows,
        "source_reads": market.reads,
        "sha256": canonical(rows),
    }
    publish(path, result)
    return result
