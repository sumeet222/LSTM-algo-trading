"""P020 feature/target preparation only. No torch, checkpoints, or neural fits."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from .hf1m_action_audit import digest
from .hf1m_action_source import publish_json, publish_table
from .hf1m_ft16_fit import fit, target_values
from .hf1m_ft16_math import Components, build
from .hf1m_ft16_source import (
    COMMON,
    CONFIG,
    ORDER,
    checked,
    configuration,
    read_hourly,
    ref,
    source_masks,
)


def origins(c: Components, config: dict) -> tuple[pd.DataFrame, np.ndarray]:
    """Input admission precedes targets and depends on source booleans only."""
    mask, clock = source_masks(config)
    clock = (
        clock.loc[clock.session_date_et.between("2011-04-01", "2025-12-31")]
        .copy()
        .reset_index(drop=True)
    )
    past = (
        mask.pivot(index="origin_id", columns="ticker", values="origin_input_48_cap5")
        .reindex(index=clock.origin_id, columns=config["symbols"])
        .to_numpy(bool)
    )
    future = (
        mask.pivot(index="origin_id", columns="ticker", values="origin_future_4h_eligible")
        .reindex(index=clock.origin_id, columns=config["symbols"])
        .to_numpy(bool)
    )
    close = c.source["close"]
    returns = np.full((len(clock), 20), np.nan)
    records = []
    dates = c.grid.session_date_et.to_numpy()
    for k, row in enumerate(clock.to_dict("records")):
        entry = int(str(row["entry_index"]))
        exit_ = int(str(row["exit_index"]))
        first = entry - 47
        if c.grid.hour_end_utc.iloc[entry] != row["entry_end_utc"] or exit_ - entry != 4:
            raise ValueError("STOP_IDENTITY: source grid index drift")
        input_ok = first >= 0 and bool(past[k].all())
        if input_ok and not np.isfinite(c.source["close_input_cap5"][first : entry + 1]).all():
            raise ValueError("STOP_IDENTITY: source mask/close mismatch")
        value = np.log(close[exit_] / close[entry])
        value[~future[k]] = np.nan
        returns[k] = value
        date = str(row["session_date_et"])
        records.append(
            {
                "Index": k,
                **row,
                "first_step": first,
                "source_input_eligible": input_ok,
                "label_eligible": bool(future[k].all()),
                "label_missing_stocks": "|".join(np.asarray(config["symbols"])[~future[k]]),
                "input_exclusion": "" if input_ok else "SOURCE_CAP5_CONTEXT_OR_WARMUP_OR_COP",
                "inner_train": date <= "2023-01-23",
                "inner_validation": date >= "2023-01-24"
                and date <= "2025-06-30"
                and first >= 0
                and dates[first] > "2023-01-23",
                "refit": date <= "2025-06-30",
                "development": date >= "2025-07-01" and first >= 0 and dates[first] > "2025-06-30",
                "inner_embargo": date >= "2023-01-24"
                and date <= "2025-06-30"
                and (first < 0 or dates[first] <= "2023-01-23"),
                "development_embargo": date >= "2025-07-01"
                and (first < 0 or dates[first] <= "2025-06-30"),
                "issuance_utc": pd.Timestamp(str(row["entry_end_utc"])) + pd.Timedelta(minutes=2),
                "label_maturity_utc": pd.Timestamp(str(row["exit_end_utc"]))
                + pd.Timedelta(minutes=2),
                "source_publication_available_at": "UNKNOWN_ASSUMED_END_PLUS2_ISSUANCE",
            }
        )
    return pd.DataFrame(records), returns


def fitting_hours(c: Components, rows: pd.DataFrame, stop: str) -> np.ndarray:
    selected = np.zeros(len(c.grid), dtype=bool)
    positions = rows.loc[
        rows.source_input_eligible & rows.session_date_et.le(stop), ["first_step", "entry_index"]
    ].to_numpy(dtype=np.int64)
    for first, last in positions:
        selected[int(first) : int(last) + 1] = True
    selected &= c.grid.session_date_et.between("2011-04-01", stop).to_numpy()
    return selected


def run(out: Path) -> None:
    started = time.monotonic()
    config = configuration()
    pre = json.loads((out / "preflight.json").read_text())
    if pre["config_sha256"] != digest(CONFIG):
        raise ValueError("STOP_IDENTITY: frozen config drift")
    if (out / "model_input_contract.json").exists():
        contract = json.loads((out / "model_input_contract.json").read_text())
        for r in contract["files"].values():
            checked(r)
        print("SEALED_P020_VERIFIED_REPLAY")
        return
    hours = read_hourly(config)
    up = Path(config["upstream_packet"])
    fm = json.loads((up / "hour_field_mask_manifest.json").read_text())
    fields = pd.read_parquet(checked(fm["file"]))
    c = build(hours, fields, config["volume_max_absent_minutes"])
    rows, returns = origins(c, config)
    private = Path("data/processed/hf20_hf1m_long_v1_ft16_v1") / out.name
    private.mkdir(parents=True, exist_ok=True)
    arrays = {}
    recipes = {}
    targets = {}
    alltargets = []
    for name, stop in [("inner", config["inner_train_end"]), ("refit", config["train"][1])]:
        fh = fitting_hours(c, rows, stop)
        recipe, a = fit(c, fh, stop)
        eligible_train = rows.label_eligible & rows.session_date_et.le(stop)
        mad = np.median(np.abs(returns - np.median(returns, axis=1)[:, None]), axis=1)
        epsilon = max(1e-4, 0.1 * float(np.median(mad[eligible_train])))
        y, median, mad = target_values(returns, epsilon)
        y[~rows.label_eligible.to_numpy()] = np.nan
        supervised = (
            rows.source_input_eligible & rows.label_eligible & rows.session_date_et.le(stop)
        ).to_numpy()
        scale = max(float(np.median(np.abs(y[supervised]))), 1e-6)
        recipe.update(
            epsilon=epsilon,
            epsilon_origins=int(eligible_train.sum()),
            epsilon_population=(
                "all complete20 genuine training origins in fit prefix, "
                "independent of feature values"
            ),
            t2_scale=scale,
            t2_scale_origins=int(supervised.sum()),
            t2_rule=(
                "pooled unique admissible origin/stock median(abs(TG20)),floor1e-6;"
                "z=asinh(y/s);inverse=s*sinh(z) once"
            ),
        )
        a["targets"] = y.astype(np.float32)
        targets[name] = y
        recipes[name] = recipe
        arrays[name] = a
        for k, feature in enumerate(COMMON):
            if not np.isfinite(a["scaled_common"][:, :, k]).all():
                raise ValueError("NONFINITE_CHANNEL " + feature)
        label = pd.DataFrame(
            {
                "origin_id": np.repeat(rows.origin_id.to_numpy(), 20),
                "ticker": np.tile(config["symbols"], len(rows)),
                "session_date_et": np.repeat(rows.session_date_et.to_numpy(), 20),
                "fit_version": name,
                "return_4h": returns.reshape(-1),
                "cross_section_median": np.repeat(median, 20),
                "cross_section_mad": np.repeat(mad, 20),
                "numerator": (returns - median[:, None]).reshape(-1),
                "epsilon": epsilon,
                "denominator": np.repeat(mad + epsilon, 20),
                "TG20": y.reshape(-1),
                "T2_z": np.arcsinh(y / scale).reshape(-1),
                "label_eligible": np.repeat(rows.label_eligible.to_numpy(), 20),
                "entry_end_utc": np.repeat(rows.entry_end_utc.to_numpy(), 20),
                "exit_end_utc": np.repeat(rows.exit_end_utc.to_numpy(), 20),
                "label_maturity_utc": np.repeat(rows.label_maturity_utc.to_numpy(), 20),
            }
        )
        alltargets.append(label)
    for split in ["inner_train", "inner_validation", "refit", "development"]:
        rows[split + "_admitted"] = rows[split] & rows.source_input_eligible & rows.label_eligible
    publish_json(out / "train_only_fit_recipes.json", recipes)
    component_path = private / "HF20_HF1M_LONG_v1_FT16_v1_components.npz"
    payload = {
        "feature_id": np.asarray(config["feature_id"]),
        "symbols": np.asarray(config["symbols"]),
        "feature_order": np.asarray(ORDER),
        "hour_end_ns": c.grid.hour_end_utc.astype("int64").to_numpy(),
        "m2_reference_end_index": c.m2_reference_end,
    }
    for name, a in arrays.items():
        for key in [
            "native_common",
            "native_m2",
            "scaled_common",
            "scaled_m2",
            "fallback_common",
            "fallback_m2",
        ]:
            payload[name + "_" + key] = a[key]
    if component_path.exists():
        raise ValueError("P020_OUTPUT_ALREADY_EXISTS")
    with component_path.open("xb") as stream:
        np.savez_compressed(stream, **payload)
    source_cols = [
        "ticker",
        "hour_id",
        "source_month",
        "session_date_et",
        "hour_start_utc",
        "hour_end_utc",
        "open",
        "high",
        "low",
        "close",
        "close_input_cap5",
        "observed_volume",
        "expected_minutes",
        "genuine_count",
        "missing_count",
        "conflict_count",
        "quarantine_count",
        "proxy_count",
        "price_basis_id",
        "volume_basis_id",
        "anomaly_event_ids",
        "price_factor",
        "raw_linkage_hash",
        "genuine_open",
        "genuine_close",
        "extrema_complete",
    ]
    source = c.hours[source_cols].copy()
    source["step"] = (
        np.repeat(np.arange(len(c.grid)), 20)
        if source.hour_start_utc.is_monotonic_increasing
        else source.hour_start_utc.map(dict(zip(c.grid.hour_start_utc, range(len(c.grid)))))
    )
    source = source.merge(
        c.volume, on=["hour_id", "ticker", "session_date_et"], validate="one_to_one"
    )
    files = {
        "components": ref(component_path),
        "origins": publish_table(
            private / "HF20_HF1M_LONG_v1_MODEL_INPUT_v1_origins.parquet", rows
        ),
        "targets": publish_table(
            private / "HF20_HF1M_LONG_v1_TG20_4H_v1_targets.parquet",
            pd.concat(alltargets, ignore_index=True),
        ),
        "candles_quality": publish_table(
            private / "HF20_HF1M_LONG_v1_FT16_v1_candles_quality.parquet", source
        ),
    }
    gridref = publish_table(private / "HF20_HF1M_LONG_v1_FT16_v1_grid.parquet", c.grid)
    files["grid"] = gridref
    contract = {
        "schema": 1,
        "source": config["source"],
        "revision": config["revision"],
        "feature_id": config["feature_id"],
        "target_id": config["target_id"],
        "model_input_id": config["model_input_id"],
        "parent_namespace": config["parent_namespace"],
        "symbols": config["symbols"],
        "feature_order": list(ORDER),
        "config": ref(CONFIG),
        "upstream_gate_sha256": config["upstream_gate_sha256"],
        "action_ledger_sha256": digest(up / "unresolved_event_ledger_v3.json"),
        "root_register_sha256": config["root_register_sha256"],
        "fit_recipes": ref(out / "train_only_fit_recipes.json"),
        "files": files,
        "maximum_numeric_date": "2025-12-31",
        "protected_numeric_access": False,
        "lookback": 48,
        "tensor_shape_per_origin": [20, 48, 16],
        "shared_components": (
            "15unique stock/hour common channels plus2session-locked origin-context "
            "M2 channels; materialize16on demand"
        ),
        "split_counts": {
            split: int(rows[split + "_admitted"].sum())
            for split in ["inner_train", "inner_validation", "refit", "development"]
        },
        "model_training_authorized": False,
        "ledger": 32,
        "original_source_unchanged": True,
        "status": "PENDING_INDEPENDENT_QA",
        "code_sha256": {
            str(p): digest(p) for p in sorted(Path("src/lstm_data").glob("hf1m_ft16_*.py"))
        },
    }
    publish_json(out / "model_input_contract.json", contract)
    try:
        import resource

        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    except ImportError:
        rss = None
    publish_json(
        out / "preparation_resource_receipt.json",
        {
            "wall_seconds": time.monotonic() - started,
            "peak_rss_native": rss,
            "native_rss_units": "bytes on macOS,KiB on Linux",
            "private_store_bytes": sum(p.stat().st_size for p in private.iterdir() if p.is_file()),
            "price_download_requests": 0,
            "model_fits": 0,
            "protected_numeric_rows": 0,
        },
    )
    print(json.dumps(contract["split_counts"]))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", required=True, type=Path)
    run(p.parse_args().out)


if __name__ == "__main__":
    main()
