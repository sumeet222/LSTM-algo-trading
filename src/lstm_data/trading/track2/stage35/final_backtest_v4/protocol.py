"""Owner-approved, non-optimized protocol frozen before financial outputs."""

from dataclasses import dataclass, replace
from decimal import Decimal
from numbers import Real

from ...stage012.model_registry import SYMBOLS
from .paths import ROOT, canonical

D = Decimal
ARMS = ("EQUAL", "ROLLING_RISK", "EWMA_RISK", "S2C_RISK")


@dataclass(frozen=True)
class Scenario:
    name: str = "baseline"
    lag: int = 2
    spread: Decimal = D(5)
    impact: Decimal = D(5)
    fee: Decimal = D(".005")
    minimum: Decimal = D(1)
    borrow: Decimal = D(".02")
    funding: Decimal = D(0)
    unknown_yield: Decimal = D(0)
    cil_postclose: Decimal | None = None
    cil_sessions: int = 5
    prohibit_mrk_cross: bool = False
    borrow_stress: bool = False


def scenarios() -> tuple[Scenario, ...]:
    base = Scenario()
    rows = [base]
    for key, values in (
        ("lag", (1, 5)),
        ("spread", (D(1), D(15))),
        ("impact", (D(1), D(15))),
        ("fee", (D(0), D(".01"))),
        ("minimum", (D(0), D(2))),
        ("borrow", (D(".01"), D(".05"))),
        ("funding", (D(".05"), D(".10"))),
        ("unknown_yield", (D(".015"), D(".03"))),
        ("cil_postclose", (D("33.30"), D("40.70"))),
        ("cil_sessions", (1, 10)),
    ):
        rows.extend(replace(base, name=f"{key}_{value}", **{key: value}) for value in values)
    rows.extend(
        (
            replace(base, name="known_mrk_cross_prohibition", prohibit_mrk_cross=True),
            replace(base, name="fixed_borrow_reject_recall", borrow_stress=True),
            replace(
                base,
                name="joint_adverse",
                lag=5,
                spread=D(15),
                impact=D(15),
                fee=D(".01"),
                minimum=D(2),
                borrow=D(".05"),
                funding=D(".10"),
                unknown_yield=D(".03"),
                cil_postclose=D("40.70"),
                cil_sessions=10,
                borrow_stress=True,
            ),
        )
    )
    return tuple(rows)


def freeze() -> dict:
    """Validate the already preregistered immutable protocol, never rewrite it."""
    import json

    value = json.loads((ROOT / "FINAL_CONSOLIDATED_PROTOCOL.json").read_text())
    seal = json.loads((ROOT / "FINAL_CONSOLIDATED_PROTOCOL.seal.json").read_text())
    if canonical(value) != seal["sha256"]:
        raise ValueError("PREREGISTERED_PROTOCOL_CHANGED")
    if value["symbols"] != list(SYMBOLS) or value["arms"] != list(ARMS):
        raise ValueError("RESEARCH_AXIS_CHANGED")
    return value


if __name__ == "__main__":
    freeze()


def valid_multiplier(value: object) -> bool:
    """Nullable source controls abstain; neither strings nor booleans are sizes."""
    if isinstance(value, bool) or not isinstance(value, (Real, Decimal)):
        return False
    number = Decimal(str(value))
    return number.is_finite() and number > 0
