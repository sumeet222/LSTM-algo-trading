"""Fabricated prices, no real signal/source/market reader. Golden recomputable book."""

import argparse
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from ...stage012.cohort_state import Cohort
from ..borrow_financing import BorrowEvidence, BorrowState
from ..common import RAW, D, Price
from .cache import publish
from .settlement import FinalBar, Request, V2Book, settle, submit


def run(output: Path) -> None:
    at = datetime(2024, 1, 8, 15, 33, tzinfo=timezone.utc)
    known = at - timedelta(minutes=1)
    point = Price(known, known, D(100), "FABRICATED_GOLDEN_V2")
    book = V2Book.funded(D(100000))
    if not isinstance(book, V2Book):
        raise AssertionError("V2_BOOK")
    book = book.mark("mark", "AAPL", point, known)
    cohorts = tuple(
        Cohort(
            key,
            "AAPL",
            qty,
            abs(qty) * 100,
            at - timedelta(minutes=3),
            at + timedelta(hours=4),
            at + timedelta(minutes=7),
            RAW,
            ("FABRICATED_ONLY",),
        )
        for key, qty in (("a", 10), ("b", -6))
    )
    reserved = book.reserve(
        "reserve",
        cohorts,
        point,
        known,
        BorrowEvidence(
            BorrowState.CONDITIONAL_SCENARIO, known, "FABRICATED", D(".02"), "SYNTHETIC_FIXTURE"
        ),
    )
    if not isinstance(reserved, V2Book):
        raise AssertionError("V2_BOOK")
    order = submit(
        "open",
        "account",
        "S2C_RISK",
        "AAPL",
        (Request("a", D(10)), Request("b", D(-6))),
        known,
        known,
        at,
        at + timedelta(minutes=7),
        point,
        D(100000),
        known,
        True,
    )
    bar = FinalBar(
        at,
        at + timedelta(minutes=1),
        at + timedelta(minutes=2),
        D(100),
        "FABRICATED_BAR",
        "ORIGINAL_OBSERVED",
    )
    book = settle(reserved, order, bar, bar.available)
    end = at + timedelta(hours=4, minutes=3)
    prior = end - timedelta(minutes=1)
    order = submit(
        "old_long_close",
        "account",
        "S2C_RISK",
        "AAPL",
        (Request("a", D(-10), "EXIT"),),
        prior,
        prior,
        end,
        None,
        Price(prior, prior, D(110), "FABRICATED_PRIOR"),
        D(100000),
        prior,
        True,
    )
    bar = FinalBar(
        end,
        end + timedelta(minutes=1),
        end + timedelta(minutes=2),
        D(110),
        "FABRICATED_BAR_2",
        "ORIGINAL_OBSERVED",
    )
    book = settle(book, order, bar, bar.available)
    book.reconcile()
    if book.positions[0].quantity != -6:
        raise AssertionError("GOLDEN_SHARES")
    publish(
        output,
        {
            "provenance": "FABRICATED_PRICES_ONLY_NO_HISTORICAL_ECONOMICS",
            "cash": book.cash,
            "restricted_proceeds_subset": book.restricted(),
            "nav": book.nav(),
            "lots": [asdict(lot) for lot in book.lots],
            "physical": [asdict(p) for p in book.positions],
            "journal": [asdict(j) for j in book.journal],
            "digest": book.digest(),
            "adjacent_hashes_pass": all(
                a.after == b.before for a, b in zip(book.journal, book.journal[1:])
            ),
        },
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    run(parser.parse_args().output)
