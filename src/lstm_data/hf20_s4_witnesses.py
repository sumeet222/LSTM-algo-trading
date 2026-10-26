"""Independent real-candle checks for S4's unchanged channels and expanded M2."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .hf1m_action_audit import SYMBOLS, digest
from .hf1m_ft16_fit import native
from .hf1m_ft16_math import Components
from .hf1m_ft16_oracles import average, manual
from .hf1m_ft16_source import COMMON, ORDER
from .hf20_rank_visuals import PRIOR


def scaled(c: Components, recipe: dict) -> tuple[np.ndarray, np.ndarray]:
    """Apply an already sealed recipe, without estimating any new parameter."""
    raw, m2 = native(c, recipe["floors"])
    common = np.empty_like(raw, dtype=np.float32)
    for k, name in enumerate(COMMON):
        sc = recipe["scalers"][name]
        common[:, :, k] = (
            np.where(np.isfinite(raw[:, :, k]), raw[:, :, k], recipe["fallbacks"][name])
            - sc["center"]
        ) / sc["scale"]
    sc = recipe["scalers"]["M2"]
    return common, (
        (np.where(np.isfinite(m2), m2, recipe["fallbacks"]["M2"]) - sc["center"]) / sc["scale"]
    ).astype(np.float32)


def assemble(rows: pd.DataFrame, common: np.ndarray, m2: np.ndarray) -> np.ndarray:
    """Exactly48 shifted full-hour steps; origin context held fixed throughout sequence."""
    if rows.session_date_et.ge("2025-01-01").any() or rows.first_step.lt(0).any():
        raise ValueError("S4_INPUT_SCOPE")
    if (
        not rows.context.between(0, 6).all()
        or not (rows.entry_index - rows.first_step).eq(47).all()
    ):
        raise ValueError("S4_FULL_HOUR_CONTEXT48_REQUIRED")
    history = rows.first_step.to_numpy(int)[:, None] + np.arange(48)
    context = rows.context.to_numpy(int)
    x = np.empty((len(rows), 20, 48, 16), dtype=np.float32)
    for k, name in enumerate(ORDER):
        a = (
            m2[history, :, context[:, None]]
            if name == "M2"
            else common[history, :, COMMON.index(name)]
        )
        x[:, :, :, k] = a.transpose(0, 2, 1)
    if not np.isfinite(x).all():
        raise ValueError("S4_NONFINITE_INPUT")
    return x


def verify(c: Components, clock: pd.DataFrame, returns: np.ndarray, out: Path) -> None:
    """Saved exact old tensors, then independent scalar operands for all seven contexts."""
    keys = pd.read_csv(PRIOR / "shared_source_case_keys.csv")
    replays = []
    for year in range(2021, 2025):
        path = PRIOR / f"F{year % 100}_refit_recipe.json"
        recipe = json.loads(path.read_text())
        common, m2 = scaled(c, recipe)
        saved = np.load(PRIOR / f"F{year % 100}_refit_source_case_inputs.npz")
        chosen = keys.set_index("case_id").loc[saved["case_id"]].reset_index()
        rows = clock.set_index("origin_id").loc[chosen.origin_id].reset_index()
        x = assemble(rows, common, m2)
        sample = np.stack([x[k, SYMBOLS.index(str(t))] for k, t in enumerate(chosen.ticker)])
        np.testing.assert_array_equal(sample, saved["inputs"])
        np.testing.assert_allclose(
            returns[rows.row_index.to_numpy(int)], saved["returns20"], atol=1e-12, rtol=1e-11
        )
        replays.append(
            dict(
                year=year,
                events=len(chosen),
                features16_steps48_exact=True,
                recipe_sha256=digest(path),
                source_saved_sha256=digest(PRIOR / f"F{year % 100}_refit_source_case_inputs.npz"),
            )
        )
    pd.DataFrame(replays).to_csv(out / "S4_ARCHIVED_ALL16_TENSOR_IDENTITY.csv", index=False)
    recipe = json.loads((PRIOR / "F24_refit_recipe.json").read_text())
    raw, m2 = native(c, recipe["floors"])
    frame = c.hours.copy()
    frame["step"] = frame.hour_start_utc.map(pd.Series(c.grid.index, index=c.grid.hour_start_utc))
    frame["volume_usable_for_feature"] = frame.hour_id.map(
        c.volume.set_index("hour_id").volume_usable_for_feature
    )
    checks, operands = [], []
    for context in range(7):
        # Fixed date, independent of return values or predictive performance.
        row = clock.loc[clock.session_date_et.eq("2024-06-18") & clock.context.eq(context)].iloc[0]
        i = int(row.entry_index)
        j = SYMBOLS.index("AAPL")
        expected, source = manual(frame, "AAPL", i, 0, recipe["floors"][j])
        input_day = str(c.grid.session_date_et.iloc[i])
        past = clock.loc[
            clock.regular_session & clock.context.eq(context) & clock.session_date_et.lt(input_day)
        ].tail(60)
        values = returns[past.row_index.to_numpy(int), j].copy()
        immature = past.label_maturity_utc.ge(
            pd.Timestamp(input_day + " 09:30", tz="America/New_York")
        ).to_numpy()
        values[immature] = np.nan
        mean = average(values.tolist(), 20, 19)
        rms = average(values.tolist(), 60, 57, True)
        expected["M2"] = mean / max(rms, recipe["floors"][j]["m2_floor"])
        for name in ORDER:
            actual = float(m2[i, j, context] if name == "M2" else raw[i, j, COMMON.index(name)])
            scalar = float(expected[name])
            np.testing.assert_allclose(actual, scalar, rtol=1e-11, atol=1e-11, equal_nan=True)
            checks.append(
                dict(
                    origin_id=row.origin_id,
                    slot=row.slot,
                    category=row.category,
                    ticker="AAPL",
                    feature=name,
                    native_available=bool(np.isfinite(actual)),
                    vector=actual,
                    scalar=scalar,
                    tolerance="rtol=atol=1e-11",
                    status="PASS",
                )
            )
        operands.append(
            dict(
                origin_id=row.origin_id,
                ticker="AAPL",
                last_input_end=str(c.grid.hour_end_utc.iloc[i]),
                M2_session_lock=str(pd.Timestamp(input_day + " 09:30", tz="America/New_York")),
                M2_past60_origin_ids=past.origin_id.tolist(),
                M2_immature_mask=immature.tolist(),
                M2_mean=mean,
                M2_rms=rms,
                canonical_scalar_operands=source,
            )
        )
    # Q2 is legitimately unavailable in the fixed AAPL examples. Select the first
    # source-native Q2 witness per context, never by a return or forecast value.
    for context in range(7):
        candidates = clock.loc[
            clock.context.eq(context) & clock.eligible & clock.session_date_et.ge("2013-01-01")
        ]
        indices = candidates.entry_index.to_numpy(int)
        available = np.isfinite(raw[indices, :, COMMON.index("Q2")])
        found = np.argwhere(available)
        if not len(found):
            raise ValueError("NO_NATIVE_Q2_WITNESS_IN_CONTEXT")
        k, j = map(int, found[0])
        row = candidates.iloc[k]
        i = int(row.entry_index)
        expected, source = manual(frame, SYMBOLS[j], i, 0, recipe["floors"][j])
        actual = float(raw[i, j, COMMON.index("Q2")])
        np.testing.assert_allclose(actual, expected["Q2"], rtol=1e-11, atol=1e-11)
        checks.append(
            dict(
                origin_id=row.origin_id,
                slot=row.slot,
                category=row.category,
                ticker=SYMBOLS[j],
                feature="Q2",
                native_available=True,
                vector=actual,
                scalar=expected["Q2"],
                tolerance="rtol=atol=1e-11",
                status="PASS_FIRST_SOURCE_NATIVE_Q2_WITNESS",
            )
        )
        operands.append(
            dict(
                origin_id=row.origin_id,
                ticker=SYMBOLS[j],
                selection="first native Q2 after2013; source availability only",
                canonical_scalar_operands=source,
            )
        )
    pd.DataFrame(checks).to_csv(out / "S4_ALL16_SCALAR_SOURCE_WITNESSES.csv", index=False)
    (out / "S4_SCALAR_OPERANDS.json").write_text(json.dumps(operands, indent=2, default=str) + "\n")
    if set(pd.DataFrame(checks).loc[pd.DataFrame(checks).native_available, "feature"]) != set(
        ORDER
    ):
        raise ValueError("ALL16_NATIVE_REAL_WITNESSES_REQUIRED")
