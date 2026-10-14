"""Bound once-only D8 extra columns, without changing the original ridge solver."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

import numpy as np

from .ft0_transforms import identity
from .p3_domain import MODE, synthetic_id
from .p3_events import json_value

if TYPE_CHECKING:
    from .baseline_fit import Preparation
    from .baseline_inputs import BaselineInput

Arm = Literal["LL0_R", "LL1_R", "SHAM_LL1_R"]
LAYOUT = "D8-RIDGE-FLAGS-ONCE-v1"
DECISION_SHA = "c59c4486271f2d8c465c556272d8ea2fdde9fe08acff3d66bc7bada4819b485d"


def metadata_identity(value: object) -> str:
    """Hash every typed field with ISO clocks, avoiding locale-heavy dataclass repr.

    This new D8 encoding is versioned separately. It changes provenance hashes,
    never numeric inputs, fitting semantics or the protected legacy encodings.
    """
    return identity(["SYN:D8_TYPED_JSON:1", json_value(value)])


@dataclass(frozen=True)
class DirectedExtension:
    """Validated trailing16/51 columns over147 stock/market, explicit synthetic binding."""

    values: tuple[tuple[float, ...], ...]
    arm: Arm
    input_id: str
    universe_id: str
    preparation_id: str
    context: str
    decision_sha: str
    trace_id: str
    content_id: str
    layout: str = LAYOUT
    mode: str = MODE

    def content(self) -> str:
        return identity(
            [
                self.values,
                self.arm,
                self.input_id,
                self.universe_id,
                self.preparation_id,
                self.context,
                self.decision_sha,
                self.trace_id,
                self.layout,
                self.mode,
            ]
        )

    def validate(self, row: BaselineInput, prep: Preparation, context: str) -> None:
        from .neural_market import market_preparation_identity

        synthetic_id(row.input_id)
        if (
            self.mode != MODE
            or self.layout != LAYOUT
            or self.arm not in {"LL0_R", "LL1_R", "SHAM_LL1_R"}
            or self.input_id != row.input_id
            or self.universe_id != row.universe.universe_id
            or self.preparation_id != market_preparation_identity(prep)
            or self.context != context
            or self.context != row.stock.application_context
            or len(self.values) != 5
            or not self.trace_id
            or self.decision_sha != DECISION_SHA
            or any(len(v) != (16 if self.arm == "LL0_R" else 51) for v in self.values)
            or not np.isfinite(np.asarray(self.values)).all()
            or self.content_id != self.content()
        ):
            raise ValueError("EXACT_BOUND_SYNTHETIC_D8_EXTENSION_REQUIRED")
