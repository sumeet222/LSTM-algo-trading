"""S4 seven-context adapter with explicit prefix authority and unchanged16 channels."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .hf1m_ft16_fit import native
from .hf1m_ft16_math import Components
from .hf20_ranking_data import FoldData, metadata, year_guard
from .hf20_s4_fit import fit_expanded
from .hf20_s4_witnesses import assemble, scaled

ROLES = ("inner_train", "inner_validation", "refit", "oos")


class S4Data(FoldData):
    """No parent constructor: it hashes protected partitions, forbidden in this package."""

    def __init__(self, c: Components, rows: pd.DataFrame, returns: np.ndarray):
        self.components = c
        self.rows = rows.copy()
        self.grid = c.grid
        self.returns = returns
        self.target_components: pd.DataFrame | None = None
        self.contract = metadata(2021)[0]
        self.symbols = tuple(self.contract["symbols"])
        self.plans = {}
        days = sorted(set(c.grid.session_date_et))
        first = np.full(len(rows), "0000", dtype=object)
        has = rows.first_step.ge(0)
        first[has] = c.grid.session_date_et.to_numpy()[rows.loc[has, "first_step"].to_numpy(int)]
        for year in range(2021, 2025):
            stop = max(d for d in days if d < str(year))
            anchor = (pd.Timestamp(stop).to_period("M") - 5).start_time.strftime("%Y-%m-%d")
            inner = max(d for d in days if d < anchor)
            day = rows.session_date_et
            nominal = dict(
                inner_train=day.between("2011-04-01", inner),
                inner_validation=day.between(anchor, stop),
                refit=day.between("2011-04-01", stop),
                oos=day.str.startswith(str(year)),
            )
            masks = {}
            for role, n in nominal.items():
                cutoff = (
                    inner
                    if role == "inner_train"
                    else str(year) + "-12-31"
                    if role == "oos"
                    else stop
                )
                boundary = (
                    inner if role == "inner_validation" else stop if role == "oos" else "0000"
                )
                limit = (
                    pd.Timestamp(cutoff, tz="America/New_York")
                    + pd.Timedelta(days=1)
                    - pd.Timedelta(hours=4)
                )
                masks[role] = (
                    n & rows.eligible & (first > boundary) & rows.label_maturity_utc.lt(limit)
                ).to_numpy(bool)
            v = rows.loc[masks["inner_validation"]]
            if (
                v.session_date_et.nunique() < 50
                or v.groupby("context").size().reindex(range(7), fill_value=0).min() < 25
            ):
                raise ValueError("S4_FROZEN_VALIDATION_SUPPORT")
            self.plans[year] = (
                dict(year=year, inner_stop=inner, selection_start=anchor, refit_stop=stop),
                masks,
            )
        self.common = self.m2 = np.empty(0)
        self.recipe = {}
        self.cache_key = None
        self.fallback_common = self.fallback_m2 = np.empty(0, dtype=bool)
        h = c.hours.copy()
        h["age"] = (
            h.hour_end_utc - h.last_minute - pd.Timedelta(minutes=1)
        ).dt.total_seconds() / 60
        ages = h.pivot(index="hour_start_utc", columns="ticker", values="age").reindex(
            index=c.grid.hour_start_utc, columns=self.symbols
        )
        self.age_max48 = ages.rolling(48, min_periods=1).max().to_numpy(float)

    def apply_recipe(self, year: int, phase: str, recipe: dict) -> None:
        year_guard(year)
        if phase not in ("inner", "refit"):
            raise ValueError("S4_PHASE")
        plan, _ = self.plans[year]
        stop = plan["inner_stop"] if phase == "inner" else plan["refit_stop"]
        if recipe["fit_stop_inclusive"] != stop:
            raise ValueError("S4_PREFIX_RECIPE_CUTOFF")
        self.common, self.m2 = scaled(self.components, recipe)
        a, b = native(self.components, recipe["floors"])
        self.fallback_common = ~np.isfinite(a)
        self.fallback_m2 = ~np.isfinite(b)
        self.recipe = recipe
        self.cache_key = (year, phase)

    def phase(self, year: int, phase: str, out: Path) -> dict:
        from .hf20_s4_authority import authorize

        authorize(out)
        year_guard(year)
        if phase not in ("inner", "refit"):
            raise ValueError("S4_PHASE")
        if self.cache_key == (year, phase):
            return self.recipe
        path = out / f"F{year % 100}_{phase}_recipe.json"
        plan, _ = self.plans[year]
        stop = plan["inner_stop"] if phase == "inner" else plan["refit_stop"]
        if path.exists():
            recipe = json.loads(path.read_text())
        else:
            fh = np.zeros(len(self.grid), bool)
            selected = self.rows.loc[
                self.rows.source_input_eligible
                & self.rows.session_date_et.between("2011-04-01", stop)
            ]
            for a, b in selected[["first_step", "entry_index"]].to_numpy(int):
                fh[a : b + 1] = True
            fh &= self.grid.session_date_et.between("2011-04-01", stop).to_numpy()
            recipe, _ = fit_expanded(self.components, fh, stop, approved=True)
            limit = (
                pd.Timestamp(stop, tz="America/New_York")
                + pd.Timedelta(days=1)
                - pd.Timedelta(hours=4)
            )
            prefix = (
                self.rows.label_eligible
                & self.rows.session_date_et.between("2011-04-01", stop)
                & self.rows.label_maturity_utc.lt(limit)
            )
            r = self.returns[prefix.to_numpy()]
            med = np.median(r, axis=1)
            mad = np.median(abs(r - med[:, None]), axis=1)
            epsilon = max(1e-4, 0.1 * float(np.median(mad)))
            r = self.returns[(prefix & self.rows.source_input_eligible).to_numpy()]
            med = np.median(r, axis=1)
            mad = np.median(abs(r - med[:, None]), axis=1)
            y = (r - med[:, None]) / (mad[:, None] + epsilon)
            recipe.update(
                epsilon=epsilon,
                t2_scale=max(float(np.median(abs(y))), 1e-6),
                s4_contexts=7,
                task="S4A",
                target_minutes=240,
            )
            with path.open("x") as stream:
                json.dump(recipe, stream, indent=2)
        self.apply_recipe(year, phase, recipe)
        return recipe

    def arrays(self, positions: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        if self.cache_key is None:
            raise ValueError("S4_PHASE_NOT_LOADED")
        year, phase = self.cache_key
        _, masks = self.plans[year]
        allowed = (
            (masks["inner_train"] | masks["inner_validation"])
            if phase == "inner"
            else (masks["refit"] | masks["oos"])
        )
        if not allowed[positions].all():
            raise ValueError("S4_FOLD_PHASE_LEAKAGE")
        x = assemble(self.rows.iloc[positions], self.common, self.m2)
        r = self.returns[positions]
        m = np.median(r, axis=1)
        mad = np.median(abs(r - m[:, None]), axis=1)
        y = (r - m[:, None]) / (mad[:, None] + self.recipe["epsilon"])
        if not np.isfinite(y).all():
            raise ValueError("S4_NONFINITE_TARGET")
        return x, r, y

    def quality_fields(self, positions: np.ndarray) -> dict[str, np.ndarray]:
        rows = self.rows.iloc[positions]
        starts, ends = rows.first_step.to_numpy(int), rows.entry_index.to_numpy(int)
        result = {}
        for name, values in (
            ("assumed_zero_minute_count", self.components.source["missing_count"]),
            ("price_proxy_minute_count", self.components.source["proxy_count"]),
            ("feature_fallback_cells", self.fallback_common.sum(2)),
        ):
            if not np.isfinite(values).all():
                raise ValueError("S4_UNKNOWN_SOURCE_COUNT")
            prefix = np.vstack([np.zeros((1, 20)), values.cumsum(0)])
            result[name] = (prefix[ends + 1] - prefix[starts]).reshape(-1)
        counts = np.zeros((len(rows), 20))
        for context in range(7):
            prefix = np.vstack([np.zeros((1, 20)), self.fallback_m2[:, :, context].cumsum(0)])
            own = rows.context.eq(context).to_numpy()
            counts[own] = prefix[ends[own] + 1] - prefix[starts[own]]
        result["feature_fallback_cells"] += counts.reshape(-1)
        result["max_terminal_price_age_minutes"] = self.age_max48[ends].reshape(-1)
        return result
