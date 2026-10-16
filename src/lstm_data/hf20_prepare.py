"""Approved HF20 preparation only: unique components, recipes and indexed inputs; no fits."""

from __future__ import annotations

import argparse
import json
import resource
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from .config import digest, fingerprint, now, write_json
from .hf20_features import COMMON, ORDER, build_components
from .hf20_loader import PROPOSALS, V2_PROPOSAL_SHA, require_approval
from .hf20_source import BARRIER, REVISION, SYMBOLS, read_source, verify_source
from .hf20_transforms import admissions, fit_recipe, target_decomposition

CONFIG = Path("configs/hf20_hourly_native_v1.json")


def ref(path: Path) -> dict:
    return dict(path=str(path), sha256=digest(path), bytes=path.stat().st_size)


def code_refs() -> list[dict]:
    return [ref(path) for path in sorted(Path("src/lstm_data").glob("hf20_*.py"))]


def prepare(
    out: Path,
    approval_path: Path,
    config_path: Path = CONFIG,
    amendment_path: Path | None = None,
) -> dict:
    """Stop before numeric reads unless actual live scope and bounded rights are approved."""
    started = time.monotonic()
    started_at = now()
    proposal_sha = digest(config_path)
    if proposal_sha not in PROPOSALS:
        raise ValueError("HF20_PROPOSED_CONTRACT_CHANGED")
    approval = ref(approval_path)
    amendment = ref(amendment_path) if amendment_path else None
    require_approval(Path.cwd(), approval, proposal_sha=proposal_sha, amendment_ref=amendment)
    config = json.loads(config_path.read_text())
    manifest = verify_source()
    out.mkdir(parents=True, exist_ok=False)
    source_refs = [dict(path=row["path"], sha256=row["sha256"]) for row in manifest["files"]]
    code = code_refs()
    prep_id = "HF20_PREP:" + fingerprint([config, source_refs, code, approval, amendment])
    frame = read_source(manifest)
    source_seconds = time.monotonic() - started
    phase = time.monotonic()
    c = build_components(
        frame,
        start="2022-06-01",
        stop="2026-01-06",
        independent_daily_close=proposal_sha == V2_PROPOSAL_SHA,
    )
    component_seconds = time.monotonic() - phase
    training_days = [day for day in c.days if "2022-12-01" <= day <= "2025-03-28"]
    tail_start = training_days[-63]
    inner_stop = training_days[-64]
    recipes, arrays, origins = {}, {}, {}
    phase = time.monotonic()
    for name, stop in (("inner", inner_stop), ("refit", "2025-03-28")):
        recipe, numbers = fit_recipe(c, stop)
        recipe["recipe_id"] = "HF20_RECIPE:" + fingerprint([prep_id, name, recipe])
        recipes[name] = recipe
        arrays[name] = numbers
        table = admissions(c, numbers, fitted_stop=stop)
        table.to_csv(out / (name + "_origins.csv"), index=False)
        origins[name] = table
    recipe_seconds = time.monotonic() - phase
    recipe_path = out / "train_only_scalers_and_floors.json"
    write_json(recipe_path, recipes)
    store_dir = Path("data/processed/hf20") / prep_id.split(":")[1]
    store_dir.mkdir(parents=True, exist_ok=False)
    store_path = store_dir / "components.npz"
    # One unique store, not sliding windows: common15 hour rows and M2 day/origin rows.
    with store_path.open("xb") as stream:
        np.savez_compressed(
            stream,
            preparation_id=np.asarray(prep_id),
            maximum_numeric_date=np.asarray("2026-01-06"),
            symbols=np.asarray(SYMBOLS),
            feature_order=np.asarray(ORDER),
            starts_UTC=c.grid.start.astype("int64").to_numpy(),
            ends_UTC=c.grid.end.astype("int64").to_numpy(),
            day_index=c.day_index,
            days=np.asarray(c.days),
            source_valid=np.isfinite(c.source["close"]),
            native_refit=arrays["refit"]["raw"],
            native_m2_refit=arrays["refit"]["raw_m2"],
            inner_common=arrays["inner"]["common"],
            refit_common=arrays["refit"]["common"],
            inner_m2=arrays["inner"]["m2"],
            refit_m2=arrays["refit"]["m2"],
        )
    complete, median, mad = target_decomposition(c)
    target_path = store_dir / "target_labels.npz"
    with target_path.open("xb") as stream:
        np.savez_compressed(
            stream,
            preparation_id=np.asarray(prep_id),
            returns=c.returns,
            median=median,
            mad=mad,
            label_valid=complete,
            inner_targets=arrays["inner"]["targets"],
            refit_targets=arrays["refit"]["targets"],
        )
    provenance = pd.DataFrame(
        dict(
            step=np.repeat(np.arange(len(c.grid)), 20),
            stock_index=np.tile(np.arange(20), len(c.grid)),
            source_valid=np.isfinite(c.source["close"]).reshape(-1),
            source_partition=np.repeat(
                np.where(
                    c.grid.session.lt("2024-01-01"),
                    0,
                    np.where(c.grid.session.lt("2025-01-01"), 1, 2),
                ),
                20,
            ),
        )
    )
    provenance_path = store_dir / "source_row_provenance.parquet"
    provenance.to_parquet(provenance_path, index=False)
    write_json(
        out / "canonical_feature_store_manifest.json",
        dict(
            preparation_id=prep_id,
            store=ref(store_path),
            targets=ref(target_path),
            provenance=ref(provenance_path),
            source=source_refs,
            config=ref(config_path),
            approval=approval,
            unique_hour_stock_keys=len(provenance),
            canonical_full_hour_positions=len(c.grid),
            m2_unique_day_stock_origin_keys=len(c.days) * 40,
            common_order=COMMON,
            no_dense_windows=True,
            no_repaired_rows=True,
            numeric_barrier=str(BARRIER),
            maximum_numeric_date="2026-01-06",
            code=code,
        ),
    )
    retention = {}
    for name, table in origins.items():
        for split, chosen in (
            ("train", table.session.le("2025-03-28")),
            ("development", table.session.ge("2025-03-31")),
            ("inner_train", table.session.lt(tail_start)),
            ("inner_validation", table.session.ge(tail_start) & table.session.le("2025-03-28")),
        ):
            part = table.loc[chosen]
            admitted = part.loc[part.supervised_ready]
            key = name + ":" + split
            retention[key] = dict(
                structural_origins=len(part),
                source_ready=int(part.source_ready.sum()),
                feature_ready=int(part.feature_ready.sum()),
                forecast_issuable=int(part.forecast_issuable.sum()),
                label_ready=int(part.label_ready.sum()),
                supervised_ready=len(admitted),
                retained_fraction=len(admitted) / len(part) if len(part) else 0.0,
                usable_sessions=admitted.session.nunique(),
                per_origin={str(o): int(admitted.origin.eq(o).sum()) for o in (1, 2)},
                feature_exclusion_counts=part.input_exclusion.value_counts().to_dict(),
                label_excluded=int((~part.label_ready).sum()),
            )
    rtrain = retention["refit:train"]
    rdev = retention["refit:development"]
    inner = retention["inner:inner_validation"]
    limits = config["retention"]
    if proposal_sha == V2_PROPOSAL_SHA and (
        rtrain["supervised_ready"] != 998
        or retention["inner:inner_train"]["supervised_ready"] != 872
        or rdev["supervised_ready"] != 366
        or inner["supervised_ready"] != 110
    ):
        raise ValueError("HF20_V2_APPROVAL_REPRODUCIBILITY_CONDITION_FAILED")
    retention_pass = (
        rtrain["retained_fraction"] >= limits["minimum_train"]
        and rdev["retained_fraction"] >= limits["minimum_development"]
        and retention["inner:inner_train"]["retained_fraction"]
        >= limits.get("minimum_inner_train", 0.0)
        and rdev["usable_sessions"] >= limits["minimum_development_sessions"]
        and inner["usable_sessions"] >= 50
        and min(inner["per_origin"].values()) >= 25
    )
    retention["acceptance"] = dict(
        pass_all=retention_pass,
        train_minimum=limits["minimum_train"],
        inner_train_minimum=limits.get("minimum_inner_train"),
        development_minimum=limits["minimum_development"],
        development_sessions_minimum=limits["minimum_development_sessions"],
        inner_sessions_minimum=50,
        inner_validation_start=tail_start,
        inner_fit_stop=inner_stop,
        denominator="Fixed complete normal-session2origin grid; no future-label selection",
    )
    write_json(out / "genuine_hourly_native_retention.json", retention)
    pd.DataFrame(
        {
            k: {kk: vv for kk, vv in v.items() if not isinstance(vv, dict)}
            for k, v in retention.items()
            if k != "acceptance"
        }
    ).T.to_csv(out / "retention_summary.csv")
    status = (
        "HF20_TRAIN_INPUT_READY_CONDITIONAL"
        if retention_pass
        else "HF20_PREPARATION_COMPLETE_CRITICAL_HOLD"
    )
    contract = dict(
        readiness=status,
        preparation_id=prep_id,
        source_revision=REVISION,
        symbols=SYMBOLS,
        feature_order=ORDER,
        clock_id=config["clock_id"],
        feature_id=config["feature_id"],
        target_id=config["target_id"],
        source_policy=config["source_policy"],
        action_basis=config["price_volume_basis"],
        proposal_sha256=proposal_sha,
        approval=approval,
        amendment_approval=amendment,
        source=source_refs,
        config=ref(config_path),
        code=code,
        recipes=ref(recipe_path),
        recipe_ids={name: r["recipe_id"] for name, r in recipes.items()},
        store=ref(store_path),
        targets=ref(target_path),
        origins={name: ref(out / (name + "_origins.csv")) for name in origins},
        inner_validation_start=tail_start,
        confirmation_locked=True,
        training_authorized=False,
        legacy_checkpoint_compatible=False,
        loader="lstm_data.hf20_loader.load_hf20_train_data",
        batch_shape=[20, 48, 16],
        target_shape=[20],
        rights_status="RESEARCHER_ATTESTED_LOCAL_USE; redistribution not authorized",
        new_scientific_pairs=0,
        global_scientific_pairs=28,
    )
    # Bounded real arithmetic oracles are generated separately from input/target builders.
    from .hf20_oracles import write_oracles

    write_oracles(c, recipes, arrays, origins, out)
    # A numerical-oracle failure must never leave a READY contract on disk.
    write_json(out / "training_ready_input_contract.json", contract)
    write_json(
        out / "storage_and_resource_ledger.json",
        dict(
            started_at=started_at,
            finished_at=now(),
            source_seconds=source_seconds,
            component_seconds=component_seconds,
            recipe_seconds=recipe_seconds,
            total_seconds=time.monotonic() - started,
            source_rows=len(frame),
            unique_feature_keys=len(provenance),
            output_bytes=sum(p.stat().st_size for p in store_dir.iterdir()),
            peak_RSS_bytes=int(
                resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                * (1 if sys.platform == "darwin" else 1024)
            ),
            HTTP_requests=0,
            source_reused=True,
            neural_fits=0,
            ridge_fits=0,
            held_out_numeric_rows=0,
            ledger_before=28,
            ledger_after=28,
        ),
    )
    return contract


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True, help="New immutable preparation output")
    parser.add_argument(
        "--approval", type=Path, required=True, help="Actual scoped live human receipt"
    )
    parser.add_argument("--config", type=Path, default=CONFIG)
    parser.add_argument("--amendment", type=Path, help="Required actual v2 amendment receipt")
    args = parser.parse_args()
    result = prepare(args.out, args.approval, args.config, args.amendment)
    print(
        json.dumps(
            dict(
                readiness=result["readiness"],
                preparation_id=result["preparation_id"],
                training=False,
            )
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
