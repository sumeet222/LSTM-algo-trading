"""Read-only P021 allowlisted historical/target explorer. No fitting or legacy fallback."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import digest
from ..hf1m_action_audit import REVISION, SYMBOLS
from ..hf1m_ft16_source import BOUNDED, COMMON, ORDER
from ..hf1m_training_authority import IDS
from ..hf1m_training_data import COUNTS

CONFIG = Path("configs/track_a_hf1m_long_visualization_v1.json")
ROLES = {
    "inner_train": "Inner training · calibration in-sample",
    "inner_validation": "Inner validation · checkpoint selection",
    "refit": "Full-prefix refit training · in-sample, includes historical validation dates",
    "development": "Exploratory development · post-fit chronological assessment",
}


def dates(start: str, end: str) -> None:
    """Validate before filesystem/cache access. All views share this numerical barrier."""
    a, b = pd.Timestamp(start), pd.Timestamp(end)
    if a > b or a < pd.Timestamp("2010-07-01") or b >= pd.Timestamp("2026-01-01"):
        raise ValueError("HF1M protected/out-of-scope numerical date denied")


def role(split: str) -> str:
    if split not in ROLES:
        raise ValueError("HF1M protected/unknown role denied")
    return "inner" if split.startswith("inner") else "refit"


@dataclass
class LongStudy:
    root: Path
    plan: dict
    contract: dict
    packet: Path
    files: dict[str, dict]
    token: str

    @classmethod
    def discover(cls, root: Path) -> LongStudy:
        config = json.loads((root / CONFIG).read_text())
        plan_path = root / config["plan"]["path"]
        if digest(plan_path) != config["plan"]["sha256"]:
            raise ValueError("HF1M sealed experiment changed")
        p = json.loads(plan_path.read_text())
        for reference in p["protected_refs"]:
            path = root / reference["path"]
            if digest(path) != reference["sha256"] or path.stat().st_size != reference["bytes"]:
                raise ValueError("HF1M upstream release/allowlist changed")
        if (
            p["runs"] != list(IDS)
            or tuple(p["symbols"]) != SYMBOLS
            or p["source_revision"] != REVISION
        ):
            raise ValueError("HF1M source/run/order identity denied")
        contract_path = root / p["input_contract"]["path"]
        if digest(contract_path) != p["input_contract"]["sha256"]:
            raise ValueError("HF1M input identity denied")
        d = json.loads(contract_path.read_text())
        if digest(root / d["config"]["path"]) != d["config"]["sha256"]:
            raise ValueError("HF1M source configuration changed")
        if (
            d["maximum_numeric_date"] != "2025-12-31"
            or d["protected_numeric_access"] is not False
            or d["feature_id"] != "HF20_HF1M_LONG_v1_FT16_v1"
            or tuple(d["feature_order"]) != ORDER
        ):
            raise ValueError("HF1M current FT16 release required")
        packet = contract_path.parent
        gate_ref = next(
            r for r in p["protected_refs"] if Path(r["path"]).name == "release_gate.json"
        )
        if digest(packet / "release_gate.json") != gate_ref["sha256"]:
            raise ValueError("HF1M current release hash changed")
        gate = json.loads((packet / "release_gate.json").read_text())
        if (
            gate["status"] != "FEATURE_READY_FOR_TRAINING"
            or gate["evidence"]["model_input_contract.json"]["sha256"]
            != p["input_contract"]["sha256"]
        ):
            raise ValueError("HF1M release not ready")
        # Bind every file path before numerical use; no arbitrary supplied file or directory glob.
        refs = json.loads((packet / "numeric_file_allowlist.json").read_text())["files"]
        files = {Path(r["path"]).name: r for r in refs}
        expected = Path("data/processed/hf20_hf1m_long_v1_ft16_v1") / packet.name
        if len(files) != 10 or any(Path(r["path"]).parent != expected for r in refs):
            raise ValueError("HF1M private allowlist identity")
        return cls(root, p, d, packet, files, config["plan"]["sha256"])

    def file(self, name: str) -> Path:
        if name not in self.files:
            raise ValueError("HF1M file not allowlisted")
        r = self.files[name]
        path = self.root / r["path"]
        if path.stat().st_size != r["bytes"] or digest(path) != r["sha256"]:
            raise ValueError("HF1M immutable numerical artifact changed")
        return path

    def table(self, key: str) -> pd.DataFrame:
        name = (
            Path(self.contract["files"][key]["path"]).name if key in self.contract["files"] else key
        )
        f = pd.read_parquet(self.file(name))
        if "session_date_et" in f and f.session_date_et.ge("2026-01-01").any():
            raise ValueError("HF1M protected rows denied")
        return f

    def recipe(self, version: str) -> dict:
        if version not in ("inner", "refit"):
            raise ValueError("HF1M unknown fit")
        r = self.contract["fit_recipes"]
        path = self.root / r["path"]
        if digest(path) != r["sha256"]:
            raise ValueError("HF1M train-only recipe changed")
        return json.loads(path.read_text())[version]

    def targets(self, split: str) -> pd.DataFrame:
        version = role(split)
        origins = self.table("origins")
        admitted = origins.loc[origins[split + "_admitted"]]
        t = self.table("targets")
        t = t.loc[t.fit_version.eq(version) & t.origin_id.isin(admitted.origin_id)].copy()
        if len(t) != COUNTS[split][0] * 20:
            raise ValueError("HF1M full target population mismatch")
        # Retrospective diagnostic thresholds, always from appropriate fitting prefix.
        fitting = origins.loc[
            origins[("inner_train" if version == "inner" else "refit") + "_admitted"]
        ]
        train = self.table("targets")
        train = train.loc[train.fit_version.eq(version) & train.origin_id.isin(fitting.origin_id)]
        mad = float(train.drop_duplicates("origin_id").cross_section_mad.quantile(0.05))
        numerator = float(train.numerator.abs().quantile(0.95))
        tg = float(train.TG20.abs().quantile(0.99))
        t["large_numerator"] = t.numerator.abs().ge(numerator)
        t["small_mad"] = t.cross_section_mad.le(mad)
        t["target_p99"] = t.TG20.abs().ge(tg)
        t["tail_class"] = np.select(
            [t.large_numerator & t.small_mad, t.large_numerator, t.small_mad],
            ["both", "large numerator", "small MAD"],
            default="neither",
        )
        t["numerator_p95_train"] = numerator
        t["mad_p05_train"] = mad
        t["abs_tg_p99_train"] = tg
        quality = self.table("P020_origin_quality_diagnostics.parquet")
        extra = [
            "origin_id",
            "assumed_zero_minute_count",
            "price_proxy_minute_count",
            "poor_volume_hour_count",
            "inner_feature_fallback_cells",
            "refit_feature_fallback_cells",
        ]
        return t.merge(quality[extra], on="origin_id", validate="many_to_one")

    def history(self, ticker: str, start: str, end: str) -> pd.DataFrame:
        dates(start, end)
        if ticker not in SYMBOLS:
            raise ValueError("HF1M stock denied")
        if (pd.Timestamp(end) - pd.Timestamp(start)).days > 93:
            raise ValueError(
                "Choose at most93 days per candle window; all permitted history is navigable"
            )
        # Use P019B full-hour AND stub rows; never open a protected month.
        cfg = json.loads((self.root / "configs/hf1m_long_ft16_v1.json").read_text())
        parent = self.root / cfg["upstream_packet"]
        manifest = parent / "adjusted_hourly_manifest.json"
        expected = json.loads((parent / "pre_feature_gate.json").read_text())["evidence_sha256"][
            "adjusted_hourly_manifest.json"
        ]
        if digest(manifest) != expected:
            raise ValueError("HF1M source-hour manifest changed")
        frames = []
        for m in json.loads(manifest.read_text())["monthly"]:
            if start[:7] <= m["month"] <= end[:7] and m["month"] < "2026-01":
                r = m["files"]["hourly"]
                path = self.root / r["path"]
                if digest(path) != r["sha256"]:
                    raise ValueError("HF1M adjusted hourly bytes changed")
                frames.append(
                    pd.read_parquet(
                        path,
                        filters=[
                            ("ticker", "==", ticker),
                            ("session_date_et", ">=", start),
                            ("session_date_et", "<=", end),
                        ],
                    )
                )
        if not frames:
            return pd.DataFrame()
        f = pd.concat(frames, ignore_index=True).sort_values("hour_start_utc")
        q = self.table("candles_quality")
        q = q.loc[q.ticker.eq(ticker) & q.session_date_et.between(start, end)]
        volume = [
            "hour_id",
            "volume_for_feature",
            "volume_quality_tier",
            "assumed_zero_missing_count",
            "observed_minute_fraction",
            "hourly_volume_lower_bound",
        ]
        f = f.merge(q[volume], on="hour_id", how="left", validate="one_to_one")
        provenance = self.table("P020_hour_provenance_overlay.parquet")
        provenance = provenance.loc[
            provenance.ticker.eq(ticker) & provenance.session_date_et.between(start, end)
        ]
        return f.merge(
            provenance[["hour_id", "terminal_input_price_age_minutes"]],
            on="hour_id",
            how="left",
            validate="one_to_one",
        )

    def features(
        self, ticker: str, start: str, end: str, version: str, origin: int
    ) -> pd.DataFrame:
        dates(start, end)
        if ticker not in SYMBOLS or origin not in (1, 2):
            raise ValueError("HF1M feature stock/context denied")
        recipe = self.recipe(version)
        grid = self.table("grid")
        mask = grid.session_date_et.between(start, end).to_numpy()
        positions = np.flatnonzero(mask)
        j = SYMBOLS.index(ticker)
        path = self.file(Path(self.contract["files"]["components"]["path"]).name)
        records = []
        with np.load(path, allow_pickle=False) as a:
            # NPZ members are not internally cached. Read each once, immediately narrowing
            # to this stock/date request; keep no dense48-step model windows in the UI.
            values = {
                (kind, suffix): a[version + "_" + kind + "_" + suffix][positions, j, :]
                for kind in ("native", "scaled", "fallback")
                for suffix in ("common", "m2")
            }
            for name in ORDER:
                context = origin - 1 if name == "M2" else COMMON.index(name)
                suffix = "m2" if name == "M2" else "common"
                native = values["native", suffix][:, context]
                scaled = values["scaled", suffix][:, context]
                fallback = values["fallback", suffix][:, context]
                center = recipe["scalers"][name]["center"]
                scale = recipe["scalers"][name]["scale"]
                filled = np.where(np.isfinite(native), native, recipe["fallbacks"][name])
                if not np.allclose((filled - center) / scale, scaled, rtol=2e-6, atol=2e-7):
                    raise ValueError("HF1M displayed normalization reconstruction failed")
                records.append(
                    pd.DataFrame(
                        dict(
                            hour_end_utc=grid.hour_end_utc.iloc[positions].to_numpy(),
                            step=positions,
                            feature=name,
                            native=native,
                            model_scaled=scaled,
                            fallback=fallback,
                            fallback_value=recipe["fallbacks"][name],
                            filled=filled,
                            center=center,
                            scale=scale,
                            method=recipe["scalers"][name]["method"],
                            identity=name in BOUNDED,
                        )
                    )
                )
        f = pd.concat(records, ignore_index=True)
        reason = self.table("P020_component_quality_reason_masks.parquet")
        reason = reason.loc[reason.ticker.eq(ticker) & reason.session_date_et.between(start, end)]
        return f.merge(reason, on=["step", "hour_end_utc"], validate="many_to_one")

    def run_result(self, run_id: str) -> dict:
        if run_id not in IDS:
            raise ValueError("HF1M run denied")
        config = json.loads((self.root / CONFIG).read_text())
        result = self.root / Path(config["plan"]["path"]).parent / run_id / "run_result.json"
        if not result.exists():
            raise ValueError(f"{run_id}: training artifact unavailable; approval/execution pending")
        r = json.loads(result.read_text())
        if r["run_id"] != run_id or r["status"] != "COMPLETED":
            raise ValueError("HF1M completed exact run required")
        for key, stage, version in (
            ("calibration", "CALIBRATION_SELECTED", "inner"),
            ("refit", "REFIT_FINAL", "refit"),
        ):
            binding = r[key]["binding"]
            if (
                binding["input_contract"] != self.plan["input_contract"]
                or binding["source_revision"] != REVISION
                or tuple(binding["symbols"]) != SYMBOLS
                or binding["feature_id"] != self.plan["feature_id"]
                or binding["target_id"] != self.plan["target_id"]
                or binding["stage"] != stage
                or binding["fit_version"] != version
            ):
                raise ValueError("HF1M checkpoint phase/source identity denied")
        return r

    def prediction(self, run_id: str, split: str) -> pd.DataFrame:
        role(split)
        r = self.run_result(run_id)
        reference = r["artifacts"][split + "_predictions.parquet"]
        expected = Path(self.plan["private_root"]) / run_id / (split + "_predictions.parquet")
        permitted = {expected}
        if run_id == IDS[0] and "original_plan" in self.plan:
            permitted.add(expected.parent / "continuation_v1" / expected.name)
        if Path(reference["path"]) not in permitted:
            raise ValueError("HF1M exact prediction path required")
        path = self.root / reference["path"]
        if digest(path) != reference["sha256"]:
            raise ValueError("HF1M prediction bytes changed")
        frame = pd.read_parquet(path)
        if len(frame) != COUNTS[split][0] * 20 or frame.session_date_et.ge("2026-01-01").any():
            raise ValueError("HF1M prediction population denied")
        return frame

    def report_file(self, name: str) -> Path:
        """Small P020 dictionaries/QA are bound by its sealed closeout inventory."""
        if Path(name).name != name:
            raise ValueError("HF1M report path denied")
        close_ref = next(
            r
            for r in self.plan["protected_refs"]
            if Path(r["path"]).name == "final_closeout_receipt.json"
        )
        close_path = self.root / close_ref["path"]
        if digest(close_path) != close_ref["sha256"]:
            raise ValueError("HF1M P020 closeout changed")
        close = json.loads(close_path.read_text())
        inventory = self.packet / "artifact_inventory.csv"
        if digest(inventory) != close["inventory_sha256"]:
            raise ValueError("HF1M report inventory changed")
        rows = pd.read_csv(inventory)
        relative = (self.packet / name).relative_to(self.root).as_posix()
        row = rows.loc[rows.path.eq(relative)]
        path = self.packet / name
        if len(row) != 1 or digest(path) != row.iloc[0].sha256:
            raise ValueError("HF1M report artifact unavailable or changed")
        return path

    def feature_operands(
        self, ticker: str, step: int, version: str, origin: int
    ) -> tuple[dict, dict]:
        """Independent scalar replay of actual causal source operands; no fitting."""
        from ..hf1m_ft16_oracles import manual

        if ticker not in SYMBOLS or origin not in (1, 2):
            raise ValueError("HF1M operand identity denied")
        recipe = self.recipe(version)
        candles = self.table("candles_quality")
        past = candles.loc[candles.ticker.eq(ticker) & candles.step.le(step)].copy()
        if past.empty or past.session_date_et.nunique() < 140:
            return {}, {
                "status": "UNAVAILABLE during startup; insufficient126-session source history"
            }
        floor = next(f for f in recipe["floors"] if f["symbol"] == ticker)
        values, operands = manual(past, ticker, step, origin - 1, floor)
        current = past.loc[past.step.eq(step)].iloc[0]
        operands.update(
            {
                k: current[k]
                for k in (
                    "open",
                    "high",
                    "low",
                    "close_input_cap5",
                    "volume_for_feature",
                    "volume_basis_id",
                    "price_basis_id",
                    "proxy_count",
                    "quarantine_count",
                    "missing_count",
                )
            }
        )
        operands.update(
            hourly_floor=floor["hourly_floor"],
            daily_floor=floor["daily_floor"],
            m2_floor=floor["m2_floor"],
        )
        return values, operands

    def diagnostic(self, name: str) -> pd.DataFrame:
        config = json.loads((self.root / CONFIG).read_text())
        packet = self.root / Path(config["plan"]["path"]).parent
        manifest = json.loads((packet / "diagnostics_manifest.json").read_text())
        if manifest["status"] != "PASS_DIAGNOSTICS" or manifest["plan"] != config["plan"]:
            raise ValueError("HF1M diagnostics require exact study identity")
        if name not in manifest["files"] or Path(name).name != name:
            raise ValueError("HF1M diagnostic name denied")
        r = manifest["files"][name]
        path = self.root / r["path"]
        if digest(path) != r["sha256"]:
            raise ValueError("HF1M saved diagnostic changed")
        return pd.read_csv(path) if path.suffix == ".csv" else pd.read_parquet(path)


def select_events(
    frame: pd.DataFrame,
    mode: str,
    ticker: str = "All",
    search: str = "",
    start: str = "2010-07-01",
    end: str = "2025-12-31",
    tail: str = "All",
    sign: str = "Both",
) -> pd.DataFrame:
    dates(start, end)
    f = frame.loc[frame.session_date_et.between(start, end)].copy()
    if ticker != "All":
        if ticker not in SYMBOLS:
            raise ValueError("HF1M stock denied")
        f = f.loc[f.ticker.eq(ticker)]
    if search:
        keep = (
            f[["ticker", "origin_id", "session_date_et"]]
            .astype(str)
            .apply(lambda s: s.str.contains(search, case=False, regex=False))
            .any(axis=1)
        )
        f = f.loc[keep]
    if tail != "All":
        f = f.loc[f.tail_class.eq(tail)]
    if sign != "Both":
        f = f.loc[f.TG20.gt(0) if sign == "Positive" else f.TG20.lt(0)]
    if mode in ("Smallest raw MAD", "Smallest denominator"):
        field = "cross_section_mad" if mode == "Smallest raw MAD" else "denominator"
        # Rank origins once; each selected origin still exposes all20 stocks in event detail.
        return f.sort_values([field, "origin_id", "ticker"], kind="stable").drop_duplicates(
            "origin_id"
        )
    if mode == "Large numerator AND small MAD":
        f = f.loc[f.large_numerator & f.small_mad]
    if mode == "Training p99 exceedance":
        f = f.loc[f.target_p99]
    field = {"Largest |numerator|": "numerator", "Largest |return|": "return_4h"}.get(mode, "TG20")
    return f.assign(sort_magnitude=f[field].abs()).sort_values(
        ["sort_magnitude", "origin_id", "ticker"], ascending=[False, True, True], kind="stable"
    )
