"""Past-only same-slot peer donors and complete-panel provenance; never load donor labels."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import fingerprint
from .hf1m_action_audit import REVISION, SYMBOLS
from .hf1m_ft16_source import COMMON, ORDER, checked
from .peer_screen_spec import CONTRACT, ROLES, SCIENCE


def validate_metadata(
    symbols: tuple[str, ...], channels: tuple[str, ...], scale: float, expected: float
) -> None:
    if symbols != SYMBOLS or channels != ORDER or scale != expected:
        raise ValueError("P027_PANEL_ORDER_OR_PHASE_SCALE")


def validate_clock(own: dict, donor: dict) -> None:
    for row in (own, donor):
        if (
            str(row["session_date_et"]) >= "2026-01-01"
            or int(row["entry_index"]) - int(row["first_step"]) != 47
        ):
            raise ValueError("P027_PROTECTED_OR_MISALIGNED_PEER_BEFORE_NUMERIC_IO")
        end, issuance = pd.Timestamp(row["entry_end_utc"]), pd.Timestamp(row["issuance_utc"])
        if end.tzinfo is None or issuance.tzinfo is None or end > issuance:
            raise ValueError("P027_FUTURE_OR_NAIVE_PEER_CLOCK")
    if pd.Timestamp(donor["entry_end_utc"]) >= pd.Timestamp(own["entry_end_utc"]):
        raise ValueError("P027_FUTURE_PEER_DONOR")
    a = pd.Timestamp(own["entry_end_utc"]).tz_convert("America/New_York")
    b = pd.Timestamp(donor["entry_end_utc"]).tz_convert("America/New_York")
    if (a.hour, a.minute) != (b.hour, b.minute) or a.hour not in (10, 11) or a.minute != 30:
        raise ValueError("P027_PEER_SAME_SLOT_REQUIRED")


def donor_map(own: pd.DataFrame, pool: pd.DataFrame) -> pd.DataFrame:
    """Shift by10 previous distinct source-input-eligible sessions; never use outcomes."""
    if (
        own.session_date_et.ge("2026-01-01").any()
        or pool.session_date_et.ge("2026-01-01").any()
        or own.origin_id.duplicated().any()
        or pool.origin_id.duplicated().any()
    ):
        raise ValueError("P027_PROTECTED_OR_DUPLICATE_DONOR_POOL")
    dates = sorted(set(pool.session_date_et))
    date_index = {d: i for i, d in enumerate(dates)}
    slots = pd.to_datetime(pool.entry_end_utc, utc=True).dt.tz_convert("America/New_York").dt.hour
    keys = {(d, int(slot)): i for i, (d, slot) in enumerate(zip(pool.session_date_et, slots))}
    if len(keys) != len(pool):
        raise ValueError("P027_DUPLICATE_DONOR_SLOT")
    result = []
    for i, row in enumerate(own.to_dict("records")):
        position = date_index.get(row["session_date_et"])
        reason = "NO_TEN_PRIOR_ELIGIBLE_SESSIONS"
        donor = None
        if position is not None and position >= 10:
            date = dates[position - 10]
            slot = pd.Timestamp(row["entry_end_utc"]).tz_convert("America/New_York").hour
            candidate = keys.get((date, slot))
            if candidate is None:
                reason = "SAME_SLOT_MISSING_ON_EXACT_DONOR_SESSION"
            else:
                donor = pool.iloc[candidate].to_dict()
                validate_clock(row, donor)
                reason = "MATCHED"
        result.append(
            dict(
                position=i,
                origin_id=row["origin_id"],
                session_date_et=row["session_date_et"],
                donor_position=candidate if donor is not None else -1,
                donor_origin_id=donor["origin_id"] if donor is not None else None,
                donor_session=donor["session_date_et"] if donor is not None else None,
                status=reason,
            )
        )
    return pd.DataFrame(result)


def pool_for(study, view) -> pd.DataFrame:
    if view.split not in ROLES:
        raise ValueError("P027_PROTECTED_PEER_POOL_BEFORE_FILE_LOOKUP")
    last = str(view.source.rows.session_date_et.max())
    if last >= "2026-01-01":
        raise ValueError("P027_PROTECTED_PEER_POOL_BEFORE_FILE_LOOKUP")
    # Project only historical input metadata; neither labels nor future quality choose donors.
    columns = [
        "origin_id",
        "session_date_et",
        "entry_index",
        "first_step",
        "entry_end_utc",
        "issuance_utc",
    ]
    return pd.read_parquet(
        checked(study.contract["files"]["origins"]),
        columns=columns,
        filters=[("source_input_eligible", "=", True), ("session_date_et", "<=", last)],
    ).reset_index(drop=True)


def panel_from_rows(view, rows: pd.DataFrame) -> np.ndarray:
    if view.split not in ROLES or rows.session_date_et.ge("2026-01-01").any():
        raise ValueError("P027_PROTECTED_PEER_INPUT_BEFORE_ARRAY_LOOKUP")
    if (rows.entry_index - rows.first_step).ne(47).any() or rows.first_step.lt(0).any():
        raise ValueError("P027_PEER_WINDOW")
    if int(rows.entry_index.max()) >= len(view.source.common):
        raise ValueError("P027_PEER_PREFIX_RANGE")
    history = rows.first_step.to_numpy(dtype=np.int64)[:, None] + np.arange(48)
    slots = (
        pd.to_datetime(rows.entry_end_utc, utc=True)
        .dt.tz_convert("America/New_York")
        .dt.hour.to_numpy()
        - 10
    )
    if not np.isin(slots, (0, 1)).all():
        raise ValueError("P027_PEER_SLOT")
    common = view.source.common[history].transpose(0, 2, 1, 3)
    m2 = view.source.m2[history, :, slots[:, None]].transpose(0, 2, 1)
    x = np.empty((len(rows), 20, 48, 16), dtype=np.float32)
    for j, name in enumerate(ORDER):
        x[..., j] = m2 if name == "M2" else common[..., COMMON.index(name)]
    if not np.isfinite(x).all():
        raise ValueError("P027_NONFINITE_DONOR_INPUT")
    return x


def cache_key(view, mapping: pd.DataFrame) -> str:
    return fingerprint(
        dict(
            revision=REVISION,
            contract=CONTRACT,
            role=view.split,
            phase=view.source.fit_version,
            recipe=fingerprint(view.source.fit),
            tickers=SYMBOLS,
            channels=ORDER,
            peer_recipe=SCIENCE["A4"],
            negative_control=SCIENCE["negative_control"],
            donors=mapping.to_dict("records"),
        )
    )
