"""Approved S3 adapter: independent horizon keys, shared targets, M2-only intervention."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .hf20_horizon_math import (
    endpoints,
    historical_m2,
    horizon_roles,
    m2_parameters,
    returns_at,
    target_parameters,
    target_support,
)
from .hf20_ranking_data import FoldData, assemble, year_guard
from .hf20_ranking_run import sha, write
from .hf20_recent_linear import PRIOR

PREPARATION = Path("reports/experiments/hf20_s3_horizons_2026-10-26_000127_preparation")
DESIGN_SHA = "bf12ae80cdd5a7c4418ffb7735e80eb93b7e720a90ba942518195839b2a266c3"
ROLES = ("inner_train", "inner_validation", "refit", "oos")


def relative_output(path: Path) -> Path:
    """Canonical portable receipt paths for relative and tempfile absolute spellings."""
    return path.resolve().relative_to(Path.cwd().resolve())


def source_matrix(base: FoldData, name: str) -> np.ndarray:
    return (
        base.components.hours.pivot(index="hour_start_utc", columns="ticker", values=name)
        .reindex(index=base.grid.hour_start_utc, columns=base.symbols)
        .to_numpy()
    )


class HorizonData(FoldData):
    """Reuse one source object and all original 15-channel arrays; never refit FT16."""

    def __init__(self, base: FoldData, horizon: int, stage: str):
        if horizon not in (1, 2) or stage not in ("A", "B"):
            raise ValueError("S3_ONLY_AUTHORIZED_NEW_CONDITIONS")
        self.__dict__.update(base.__dict__)
        self.base, self.horizon, self.stage = base, horizon, stage
        entry = base.rows.entry_index.to_numpy(int)
        exit_ = endpoints(base.grid, entry, horizon)
        basis = source_matrix(base, "price_basis_id")
        genuine = source_matrix(base, "genuine_close").astype(bool)
        self.valid = target_support(base.grid, entry, genuine, basis, horizon).all(1)
        self.returns = returns_at(base.components.source["close"], entry, exit_)
        self.returns[~self.valid] = np.nan
        self.rows = base.rows.copy()
        self.rows["exit_index"] = exit_
        self.rows["exit_end_utc"] = base.grid.hour_end_utc.to_numpy()[exit_]
        self.rows["label_maturity_utc"] = (
            pd.to_datetime(self.rows.exit_end_utc, utc=True) + pd.Timedelta(minutes=2)
        ).astype(str)
        # Membership still uses the approved conservative four-hour clock from base.rows.
        self.plans = {}
        membership = json.loads(
            (PREPARATION / "eligibility_amendment_v2/S3_ROLE_MEMBERSHIP.json").read_text()
        )
        for year, (plan, _) in base.plans.items():
            masks = horizon_roles(base.rows, base.grid, plan, self.valid)
            for role, mask in masks.items():
                expected = membership["canonical_row_positions"][f"F{year % 100}/H{horizon}/{role}"]
                np.testing.assert_array_equal(np.flatnonzero(mask), expected)
            v = self.rows.loc[masks["inner_validation"]]
            slot = (
                pd.to_datetime(v.entry_end_utc, utc=True).dt.tz_convert("America/New_York").dt.hour
            )
            if v.session_date_et.nunique() < 50 or min(slot.eq(10).sum(), slot.eq(11).sum()) < 25:
                raise ValueError("S3_UNCHANGED_VALIDATION_SUPPORT_GATE")
            self.plans[year] = (plan, masks)
        self.cache_key = None
        self.mean = self.rms = np.empty(0)
        self.references = np.empty(0, dtype=int)
        if stage == "B":
            self.mean, self.rms, self.references, _ = historical_m2(
                base.grid,
                base.components.source["close"],
                basis,
                source_matrix(base, "cop_dependency").astype(bool),
                horizon,
            )

    def phase(self, year: int, phase: str, out: Path) -> dict:
        out = relative_output(out)
        year_guard(year)
        if phase not in ("inner", "refit"):
            raise ValueError("S3_UNKNOWN_PHASE")
        if self.cache_key == (year, phase):
            return self.recipe
        original = self.base.phase(year, phase, PRIOR)
        self.common = self.base.common
        self.fallback_common = self.base.fallback_common
        stop = original["fit_stop_inclusive"]
        path = out / f"F{year % 100}_{phase}_recipe.json"
        target_path = out.parents[1] / "targets" / f"F{year % 100}_H{self.horizon}_{phase}.json"
        if target_path.exists():
            target = json.loads(target_path.read_text())
        else:
            if self.stage != "A":
                raise ValueError("B_MUST_REUSE_A_TARGET_PARAMETERS")
            prefix = self.rows.session_date_et.le(stop).to_numpy() & self.valid
            limit = pd.Timestamp(stop, tz="America/New_York") + pd.Timedelta(days=1)
            prefix &= (
                pd.to_datetime(self.base.rows.label_maturity_utc, utc=True).lt(limit).to_numpy()
            )
            admitted = prefix & self.rows.source_input_eligible.to_numpy(bool)
            target = dict(
                **target_parameters(self.returns, prefix, admitted),
                fit_stop_inclusive=stop,
                horizon=self.horizon,
                epsilon_origin_count=int(prefix.sum()),
                scale_origin_count=int(admitted.sum()),
                epsilon_positions_sha256=sha_array(np.flatnonzero(prefix)),
                scale_positions_sha256=sha_array(np.flatnonzero(admitted)),
            )
            write(target_path, target)
        if target["fit_stop_inclusive"] != stop or target["horizon"] != self.horizon:
            raise ValueError("TARGET_PREFIX_OR_HORIZON_MISMATCH")
        recipe = dict(original)
        recipe.update(
            epsilon=target["epsilon"],
            t2_scale=target["t2_scale"],
            horizon=self.horizon,
            stage=self.stage,
            original_recipe_path=str(PRIOR / path.name),
            original_recipe_sha256=sha(PRIOR / path.name),
            shared_target_path=str(target_path),
            shared_target_sha256=sha(target_path),
        )
        self.m2, self.fallback_m2 = self.base.m2, self.base.fallback_m2
        if self.stage == "B":
            fit_hours = np.array(original["fit_hour_indices"], dtype=int)
            unique = (
                self.grid.iloc[fit_hours].drop_duplicates("session_date_et").index.to_numpy(int)
            )
            floor, scale, self.m2 = m2_parameters(self.mean, self.rms, unique)
            self.fallback_m2 = ~np.isfinite(self.mean / np.maximum(self.rms, floor[None, :, None]))
            recipe["S3_M2"] = dict(
                floors=floor.tolist(),
                scaler=scale,
                unique_day_indices=unique.tolist(),
                fit_input_indices_sha256=sha_array(fit_hours),
                fallback_cells=int(self.fallback_m2.sum()),
            )
        if path.exists():
            stored = json.loads(path.read_text())
            if stored != recipe:
                differing = [
                    k for k in stored.keys() | recipe.keys() if stored.get(k) != recipe.get(k)
                ]
                raise ValueError("IMMUTABLE_S3_RECIPE_CHANGED:" + str(path) + ":" + str(differing))
        else:
            write(path, recipe)
        self.recipe, self.cache_key = recipe, (year, phase)
        return recipe

    def arrays(self, positions: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        if self.cache_key is None or not len(positions):
            raise ValueError("S3_PHASE_AND_NONEMPTY_POSITIONS_REQUIRED")
        year, phase = self.cache_key
        _, masks = self.plans[year]
        allowed = (
            masks["inner_train"] | masks["inner_validation"]
            if phase == "inner"
            else masks["refit"] | masks["oos"]
        )
        if not allowed[positions].all():
            raise ValueError("S3_WRONG_ROLE_OR_PHASE")
        x = assemble(self.rows.iloc[positions], self.common, self.m2)
        r = self.returns[positions]
        med = np.median(r, axis=1)
        mad = np.median(abs(r - med[:, None]), axis=1)
        y = (r - med[:, None]) / (mad[:, None] + self.recipe["epsilon"])
        if not np.isfinite(y).all():
            raise ValueError("S3_NONFINITE_LABEL")
        return x, r, y


def sha_array(values: np.ndarray) -> str:
    import hashlib

    return hashlib.sha256(np.ascontiguousarray(values).tobytes()).hexdigest()
