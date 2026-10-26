"""Exact P020 source contract, annual calendar proposal and prefix-only FT16 adapter."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .hf1m_action_audit import REVISION, SYMBOLS, digest
from .hf1m_ft16_fit import fit, native
from .hf1m_ft16_math import Components, build
from .hf1m_ft16_source import COMMON, ORDER, checked, configuration, read_hourly
from .hf1m_training_data import CONTRACT
from .hf20_ranking import YEARS, origin_weights


def year_guard(year: int) -> None:
    if year not in YEARS:
        raise ValueError("S1S2_PROTECTED_OR_UNAPPROVED_YEAR_BEFORE_IO")


def assemble(rows: pd.DataFrame, common: np.ndarray, m2: np.ndarray) -> np.ndarray:
    """One bounded chronological gather shared by linear and recurrent adapters."""
    if rows.session_date_et.ge("2025-01-01").any():
        raise ValueError("S1S2_DATE_BEFORE_COMPONENT_LOOKUP")
    if (rows.entry_index - rows.first_step).ne(47).any() or rows.first_step.lt(0).any():
        raise ValueError("EXACT48_SCHEDULED_STEPS")
    history = rows.first_step.to_numpy(int)[:, None] + np.arange(48)
    slot = (
        pd.to_datetime(rows.entry_end_utc, utc=True)
        .dt.tz_convert("America/New_York")
        .dt.hour.to_numpy()
        - 10
    )
    if not np.isin(slot, (0, 1)).all():
        raise ValueError("ORIGINAL_TWO_SLOTS_ONLY")
    x = np.empty((len(rows), 20, 48, 16), dtype=np.float32)
    for j, name in enumerate(ORDER):
        v = (
            m2[history, :, slot[:, None]].transpose(0, 2, 1)
            if name == "M2"
            else common[history, :, COMMON.index(name)].transpose(0, 2, 1)
        )
        x[:, :, :, j] = v
    if not np.isfinite(x).all():
        raise ValueError("NONFINITE_FT16")
    return x


def metadata(year: int) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    year_guard(year)
    d = json.loads(CONTRACT.read_text())
    if (
        digest(CONTRACT) != "7adfec916b7eb74fead83ef1fe6082ff0fcee9ff0b6ebae5722077e2a82c01a5"
        or d["revision"] != REVISION
        or tuple(d["symbols"]) != SYMBOLS
        or tuple(d["feature_order"]) != ORDER
    ):
        raise ValueError("EXACT_P020_SOURCE_IDENTITY_REQUIRED")
    if d["maximum_numeric_date"] != "2025-12-31" or d["protected_numeric_access"] is not False:
        raise ValueError("P020_HISTORICAL_CONTRACT_REQUIRED")
    f = pd.read_parquet(
        checked(d["files"]["origins"]), filters=[("session_date_et", "<=", "2024-12-31")]
    )
    g = pd.read_parquet(
        checked(d["files"]["grid"]), filters=[("session_date_et", "<=", "2024-12-31")]
    )
    if f.session_date_et.ge("2025-01-01").any() or g.session_date_et.ge("2025-01-01").any():
        raise ValueError("S1S2_OUTSIDE_APPROVED_HISTORICAL_READ")
    return d, f, g


def fold_masks(year: int, f: pd.DataFrame, g: pd.DataFrame) -> tuple[dict, dict[str, np.ndarray]]:
    year_guard(year)
    sessions = sorted(set(g.session_date_et))
    before = [s for s in sessions if s < str(year)]
    if not before:
        raise ValueError("EMPTY_PREFIX")
    stop = before[-1]
    anchor = (pd.Timestamp(stop).to_period("M") - 5).start_time.strftime("%Y-%m-%d")
    selection_start = min(s for s in before if s >= anchor)
    inner_stop = max(s for s in before if s < selection_start)
    if f.first_step.lt(0).any():
        raise ValueError("UNEXPECTED_NEGATIVE_P020_INDEX")
    first_dates = np.asarray(g.session_date_et)[f.first_step.to_numpy(int)]
    day = f.session_date_et.to_numpy()
    nominal = dict(
        inner_train=day <= inner_stop,
        inner_validation=(day >= selection_start) & (day <= stop),
        refit=day <= stop,
        oos=f.session_date_et.str.startswith(str(year)).to_numpy(),
    )
    temporal = dict(
        inner_train=np.ones(len(f), bool),
        refit=np.ones(len(f), bool),
        inner_validation=first_dates > inner_stop,
        oos=first_dates > stop,
    )
    joint = (f.source_input_eligible & f.label_eligible).to_numpy()
    masks = {role: n & temporal[role] & joint for role, n in nominal.items()}
    counts = {}
    for role, m in masks.items():
        rows = f.loc[m]
        if rows.empty or rows.origin_id.duplicated().any():
            raise ValueError("EMPTY_OR_DUPLICATE_FOLD")
        cutoff = (
            inner_stop if role == "inner_train" else stop if role != "oos" else str(year) + "-12-31"
        )
        maturity = pd.to_datetime(rows.label_maturity_utc, utc=True)
        limit = pd.Timestamp(cutoff, tz="America/New_York") + pd.Timedelta(days=1)
        if not maturity.lt(limit).all():
            raise ValueError("UNMATURED_LABEL_AT_CUTOFF")
        slot = (
            pd.to_datetime(rows.entry_end_utc, utc=True).dt.tz_convert("America/New_York").dt.hour
        )
        counts[role] = dict(
            origins=len(rows),
            sessions=rows.session_date_et.nunique(),
            rows=20 * len(rows),
            first=str(rows.session_date_et.min()),
            last=str(rows.session_date_et.max()),
            origin1=int(slot.eq(10).sum()),
            origin2=int(slot.eq(11).sum()),
            scheduled_candidates=int(nominal[role].sum()),
            embargo_candidates=int((nominal[role] & ~temporal[role]).sum()),
            joint_source_label_rejected=int((nominal[role] & temporal[role] & ~joint).sum()),
        )
    validation = counts["inner_validation"]
    if validation["sessions"] < 50 or min(validation["origin1"], validation["origin2"]) < 25:
        raise ValueError("INHERITED_INNER_SUPPORT_INADEQUATE")
    return dict(
        year=year,
        inner_stop=inner_stop,
        selection_start=selection_start,
        refit_stop=stop,
        input_embargo=48,
        counts=counts,
    ), masks


class FoldData:
    """One shared source/components object; one temporary normalized phase, no window store."""

    def __init__(self, *, live_approved: bool):
        if live_approved is not True:
            raise ValueError("LIVE_APPROVAL_REQUIRED_BEFORE_PREFIX_FITS")
        self.contract, self.rows, self.grid = metadata(2021)
        self.plans = {year: fold_masks(year, self.rows, self.grid) for year in YEARS}
        config = configuration()
        hours = read_hourly(config, stop="2024-12-31")
        field_ref = json.loads(
            (Path(config["upstream_packet"]) / "hour_field_mask_manifest.json").read_text()
        )["file"]
        fields = pd.read_parquet(
            checked(field_ref), filters=[("session_date_et", "<=", "2024-12-31")]
        )
        self.components: Components = build(hours, fields, config["volume_max_absent_minutes"])
        pd.testing.assert_frame_equal(
            self.components.grid[self.grid.columns], self.grid, check_exact=True
        )
        self.symbols = tuple(self.contract["symbols"])
        source = self.components.source["close"]
        entry = self.rows.entry_index.to_numpy(int)
        exit_ = self.rows.exit_index.to_numpy(int)
        self.returns = np.log(source[exit_] / source[entry])
        self.returns[~self.rows.label_eligible.to_numpy()] = np.nan
        self.cache_key: tuple[int, str] | None = None
        self.common = np.empty(0)
        self.m2 = np.empty(0)
        self.recipe: dict = {}
        self.fallback_common = np.empty(0, dtype=bool)
        self.fallback_m2 = np.empty(0, dtype=bool)
        overlay_ref = json.loads(
            (CONTRACT.parent / "provenance_overlay_manifest.json").read_text()
        )["file"]
        age = pd.read_parquet(
            checked(overlay_ref),
            filters=[("session_date_et", "<=", "2024-12-31")],
            columns=["ticker", "hour_end_utc", "terminal_input_price_age_minutes"],
        )
        ages = age.pivot(
            index="hour_end_utc", columns="ticker", values="terminal_input_price_age_minutes"
        )
        ages = ages.reindex(index=self.grid.hour_end_utc, columns=self.symbols)
        self.age_max48 = ages.rolling(48, min_periods=1).max().to_numpy(float)

    def phase(self, year: int, phase: str, out: Path) -> dict:
        year_guard(year)
        if phase not in ("inner", "refit"):
            raise ValueError("UNKNOWN_PHASE_BEFORE_IO")
        if self.cache_key == (year, phase):
            return self.recipe
        plan, _ = self.plans[year]
        stop = plan["inner_stop"] if phase == "inner" else plan["refit_stop"]
        path = out / f"F{year % 100}_{phase}_recipe.json"
        if path.exists():
            recipe = json.loads(path.read_text())
            if recipe["fit_stop_inclusive"] != stop:
                raise ValueError("RECIPE_CUTOFF_CHANGED")
            raw, m2 = native(self.components, recipe["floors"])
            fallback_common = ~np.isfinite(raw)
            fallback_m2 = ~np.isfinite(m2)
            common = np.empty_like(raw, dtype=np.float32)
            for j, name in enumerate(COMMON):
                sc = recipe["scalers"][name]
                common[:, :, j] = (
                    np.where(np.isfinite(raw[:, :, j]), raw[:, :, j], recipe["fallbacks"][name])
                    - sc["center"]
                ) / sc["scale"]
            sc = recipe["scalers"]["M2"]
            m2 = (
                (np.where(np.isfinite(m2), m2, recipe["fallbacks"]["M2"]) - sc["center"])
                / sc["scale"]
            ).astype(np.float32)
        else:
            fh = np.zeros(len(self.grid), bool)
            selected = self.rows.loc[
                self.rows.source_input_eligible & self.rows.session_date_et.le(stop)
            ]
            for a, b in selected[["first_step", "entry_index"]].to_numpy(int):
                fh[a : b + 1] = True
            fh &= self.grid.session_date_et.between("2011-04-01", stop).to_numpy()
            recipe, a = fit(self.components, fh, stop)
            eligible = (self.rows.label_eligible & self.rows.session_date_et.le(stop)).to_numpy()
            rr = self.returns[eligible]
            med = np.median(rr, axis=1)
            mad = np.median(abs(rr - med[:, None]), axis=1)
            epsilon = max(1e-4, 0.1 * float(np.median(mad)))
            admitted = eligible & self.rows.source_input_eligible.to_numpy()
            r = self.returns[admitted]
            m = np.median(r, axis=1)
            d = np.median(abs(r - m[:, None]), axis=1)
            y = (r - m[:, None]) / (d[:, None] + epsilon)
            recipe.update(epsilon=epsilon, t2_scale=max(float(np.median(abs(y))), 1e-6))
            path.write_text(json.dumps(recipe, indent=2) + "\n")
            common, m2 = a["scaled_common"], a["scaled_m2"]
            fallback_common, fallback_m2 = a["fallback_common"], a["fallback_m2"]
        self.common, self.m2, self.recipe = common, m2, recipe
        self.fallback_common, self.fallback_m2 = fallback_common, fallback_m2
        self.cache_key = (year, phase)
        return recipe

    def positions(self, year: int, role: str) -> np.ndarray:
        if role not in ("inner_train", "inner_validation", "refit", "oos"):
            raise ValueError("PROTECTED_OR_UNKNOWN_ROLE_BEFORE_IO")
        year_guard(year)
        _, masks = self.plans[year]
        return np.flatnonzero(masks[role])

    def arrays(self, positions: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        rows = self.rows.iloc[positions]
        if rows.session_date_et.ge("2025-01-01").any() or self.cache_key is None:
            raise ValueError("PHASE_OR_DATE_GUARD")
        year, phase = self.cache_key
        plan, masks = self.plans[year]
        permitted = (
            masks["inner_train"] | masks["inner_validation"]
            if phase == "inner"
            else masks["refit"] | masks["oos"]
        )
        expected = plan["inner_stop"] if phase == "inner" else plan["refit_stop"]
        if not permitted[positions].all() or self.recipe["fit_stop_inclusive"] != expected:
            raise ValueError("S1S2_WRONG_FOLD_OR_FUTURE_FITTED_RECIPE")
        x = assemble(rows, self.common, self.m2)
        r = self.returns[positions]
        m = np.median(r, axis=1)
        mad = np.median(abs(r - m[:, None]), axis=1)
        y = (r - m[:, None]) / (mad[:, None] + self.recipe["epsilon"])
        if not np.isfinite(x).all() or not np.isfinite(y).all():
            raise ValueError("NONFINITE_FOLD")
        return x, r, y

    def linear_stream(self, positions: np.ndarray):
        w = origin_weights(self.rows.iloc[positions].session_date_et.to_numpy())

        def stream():
            for start in range(0, len(positions), 16):
                p = positions[start : start + 16]
                x, r, _ = self.arrays(p)
                yield x.reshape(len(p), 20, 768).astype(float), r, w[start : start + 16]

        return stream

    def quality_fields(self, positions: np.ndarray) -> dict[str, np.ndarray]:
        """Descriptive masks only; never additional model channels or eligibility filters."""
        rows = self.rows.iloc[positions]
        starts, ends = rows.first_step.to_numpy(int), rows.entry_index.to_numpy(int)
        slot = (
            pd.to_datetime(rows.entry_end_utc, utc=True)
            .dt.tz_convert("America/New_York")
            .dt.hour.to_numpy()
            - 10
        )
        result = {}
        for name, values in (
            ("assumed_zero_minute_count", self.components.source["missing_count"]),
            ("price_proxy_minute_count", self.components.source["proxy_count"]),
            ("feature_fallback_cells", self.fallback_common.sum(2)),
        ):
            if not np.isfinite(values).all():
                raise ValueError("UNKNOWN_SOURCE_COUNT_NOT_ZERO")
            prefix = np.vstack([np.zeros((1, 20)), values.cumsum(0)])
            result[name] = (prefix[ends + 1] - prefix[starts]).reshape(-1)
        m2_counts = np.zeros((len(rows), 20))
        for s in (0, 1):
            prefix = np.vstack([np.zeros((1, 20)), self.fallback_m2[:, :, s].cumsum(0)])
            choice = slot == s
            m2_counts[choice] = prefix[ends[choice] + 1] - prefix[starts[choice]]
        result["feature_fallback_cells"] += m2_counts.reshape(-1)
        result["max_terminal_price_age_minutes"] = self.age_max48[ends].reshape(-1)
        return result
