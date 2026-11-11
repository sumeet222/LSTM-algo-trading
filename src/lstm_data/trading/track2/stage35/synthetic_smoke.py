"""Golden tiny synthetic ledger. Never reads market source/forecasts or broker state."""

import argparse
import json
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from ..stage012.cohort_state import Cohort
from .accounting import Book
from .borrow_financing import BorrowEvidence, BorrowState
from .common import RAW, D, Price


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("APPEND_ONLY_SYNTHETIC_RECEIPT")
    t = datetime(2024, 1, 8, 15, 33, tzinfo=timezone.utc)

    def quote(at: datetime, value: str) -> Price:
        return Price(at, at, D(value), "SYNTHETIC_GOLDEN_NOT_MARKET_DATA")

    evidence = BorrowEvidence(
        BorrowState.CONDITIONAL_SCENARIO,
        t - timedelta(days=1),
        "SYNTHETIC_ONLY",
        D(".1"),
        "SYNTHETIC_FIXTURE",
    )
    cohorts = tuple(
        Cohort(
            key,
            "AAPL",
            q,
            abs(q) * 100,
            t - timedelta(minutes=3),
            t + timedelta(hours=3, minutes=57),
            t + timedelta(minutes=2),
            RAW,
            ("SYNTHETIC_ONLY",),
        )
        for key, q in (("old", 10.0), ("new", -6.0))
    )
    book = Book.funded(D(100000))
    mark = quote(t - timedelta(seconds=2), "100")
    book = book.mark("mark", "AAPL", mark, mark.at)
    p = quote(t - timedelta(seconds=1), "100")
    book = book.reserve("reserve", cohorts, p, p.at, evidence)
    book = book.execute(
        "cross",
        "AAPL",
        (("old", D(10)), ("new", D(-6))),
        quote(t, "100"),
        t,
        D(100),
        D(4),
        D(1),
        evidence,
    )
    first = {
        "cash": str(book.cash),
        "nav": str(book.nav()),
        "physical_shares": str(book.positions[0].quantity),
        "virtual_gross": str(book.capacity(t).gross),
    }
    end = t + timedelta(hours=4)
    book = book.execute(
        "old_exit",
        "AAPL",
        (("old", D(-10)),),
        quote(end, "110"),
        end,
        D(110),
        D(-10),
        borrow=evidence,
    )
    book.reconcile()
    assert book.nav() == D(100039) and book.positions[0].quantity == -6
    payload = {
        "kind": "PURE_SYNTHETIC_ACCOUNTING_ONLY",
        "market_source_reads": 0,
        "first": first,
        "final_cash": str(book.cash),
        "final_nav": str(book.nav()),
        "restricted_proceeds": str(book.restricted()),
        "book": asdict(book),
        "state_checksum": book.digest(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, default=str) + "\n")


if __name__ == "__main__":
    main()
