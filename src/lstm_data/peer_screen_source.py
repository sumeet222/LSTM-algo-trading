"""P027 offline identity and saved T2 replay; protected outcomes are byte-hashed only."""

from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path

import numpy as np
import torch

from .config import now, write_json
from .controlled_loss import LossPolicy
from .hf1m_ft16_source import checked, ref
from .hf1m_training_run import predictions
from .neural_engine import SharedLSTM
from .neural_lifecycle import EarlyStop
from .objective_screen_metrics import regression
from .objective_screen_run import storage_bytes
from .objective_screen_source import identity, ordered_targets, scoped_view
from .p2_closure import load_deferred_work
from .peer_screen_spec import CONTRACT, P021, P026, ROLES, RUNS, SCIENCE
from .temporal_screen_authority import JOURNAL, POINTER, rows
from .visualization.hf1m_long import LongStudy


def preservation_references() -> list[dict]:
    """Keep prior P026 evidence immutable, excluding five declared reader/pointer surfaces."""
    allowed = {
        "apps/track_a_dashboard.py",
        "configs/track_a_visualization_v1.json",
        "docs/track_a/Visualization_Quickstart.md",
        "docs/track_a/Visualization_User_Guide.md",
        "configs/CURRENT_EXPERIMENT_REGISTRY.json",
    }
    references = []
    with (P026 / "final_execution_artifact_inventory.csv").open() as stream:
        for row in csv.DictReader(stream):
            if row["path"] not in allowed:
                reference = dict(path=row["path"], bytes=int(row["bytes"]), sha256=row["sha256"])
                checked(reference)
                references.append(reference)
    return references


def audit(out: Path) -> None:
    started = time.monotonic()
    out.mkdir(parents=True, exist_ok=False)
    (out / ".gitignore").write_text("*\n!.gitignore\n!*.md\n!submitted_instruction.txt\n")
    write_json(out / "scientific_definitions_v2.json", SCIENCE)
    p2 = load_deferred_work(Path("configs/track_a_p2_engineering_handoff_v1.json"))
    study = LongStudy.discover(Path.cwd())
    if study.plan["input_contract"]["sha256"] != CONTRACT:
        raise ValueError("P027_CONTRACT")
    checked(study.plan["input_contract"])
    history = rows()
    if history[-1]["global_started_pairs"] != 56 or history[-1]["status"] != "COMPLETED":
        raise ValueError("P027_LEDGER56")
    pointer = json.loads(POINTER.read_text())
    if pointer["real_journal"] != str(JOURNAL):
        raise ValueError("P027_POINTER")
    for journal in Path("reports/audit").glob("track_a_real_pairs_v*.jsonl"):
        if any(json.loads(line).get("run_id") in RUNS for line in journal.read_text().splitlines()):
            raise ValueError("P027_ID_COLLISION")
    from .temporal_screen_authority import require_gate

    seal_path = P026 / "final_execution_seal.json"
    seal = json.loads(seal_path.read_text())
    for key in (
        "proposal",
        "approval",
        "scientific",
        "input_contract",
        "journal",
        "pointer",
        "viewer_config",
        "postfit_validation",
        "independent_accounting",
        "exact_counts",
        "session_report",
        "human_review",
        "inventory",
    ):
        checked(seal[key])
    for arm in ("A1", "A2", "A3"):
        require_gate(P026 / (arm + "_immediate_gate.json"), arm)
    previous = json.loads((P026 / "experiment_design.json").read_text())
    for r in (
        list(previous["source_hashes"].values())
        + previous["protected_refs"]
        + previous["baseline_refs"]
    ):
        checked(r)
    ident = identity(study)
    if ident["revision"] != "776328445b7ac6e7815ef3a483e9c8ded1eb6d56":
        raise ValueError("P027_SOURCE")
    ident["ledger"] = 56
    write_json(out / "source_identity.json", ident)
    print(json.dumps(ident, indent=2), flush=True)
    (out / "registry_pointer_v16_snapshot.json").write_bytes(POINTER.read_bytes())
    torch.set_num_threads(4)
    checks = []
    references = {r["path"]: r for r in previous["baseline_refs"]}
    summaries = {}
    for seed in (42, 123):
        rp = P021 / f"HF1M-LONG-TM0-T2-S{seed}-DEV1/run_result.json"
        result = json.loads(rp.read_text())
        references[str(rp)] = ref(rp)
        import pandas as pd

        epochs = pd.read_csv(checked(result["epochs"]))
        selector = EarlyStop()
        for row in epochs.loc[epochs.phase.eq("calibration")].to_dict("records"):
            if (
                selector.observe(row["validation_mse"]) != row["qualifying"]
                or selector.selected != row["selected_epoch"]
            ):
                raise ValueError("P027_T2_SELECTOR_REPLAY")
        for role in ROLES:
            view = scoped_view(study, role, stage=7)
            summaries[role] = view.summary()
            version = "calibration" if role.startswith("inner") else "refit"
            cr = dict(result[version]["checkpoint"])
            cr.setdefault("bytes", Path(cr["path"]).stat().st_size)
            body = torch.load(checked(cr), weights_only=True, map_location="cpu")
            references[cr["path"]] = cr
            model = SharedLSTM()
            model.load_state_dict(body["model"])
            model.eval()
            saved = study.prediction(f"HF1M-LONG-TM0-T2-S{seed}-DEV1", role)
            target = ordered_targets(view)
            if (
                not saved[["origin_id", "ticker", "actual_TG20"]]
                .rename(columns={"actual_TG20": "TG20"})
                .equals(target[["origin_id", "ticker", "TG20"]])
            ):
                raise ValueError("P027_BASELINE_TARGETS")
            replay = predictions(
                model, view, LossPolicy("T2", scale=view.source.fit["t2_scale"]), {}
            )
            np.testing.assert_array_equal(replay.pred_original_TG20, saved.pred_original_TG20)
            y = target.TG20.to_numpy()
            days = target.session_date_et.to_numpy()
            metric = regression(y, saved.pred_original_TG20.to_numpy(), days)
            zero = regression(y, np.zeros(len(y)), days)
            checks.append(
                dict(
                    seed=seed,
                    role=role,
                    metrics=metric,
                    zero=zero,
                    checkpoint=cr,
                    rows=len(y),
                    full_reload_max_error=0,
                )
            )
            del model, view, replay, saved
    size = storage_bytes([Path(".")])
    if size + 1_000_000_000 > 10_000_000_000:
        raise ValueError("P027_STORAGE_HEADROOM")
    write_json(
        out / "P027_STAGE_0_SOURCE_AND_AUTHORITY_RECEIPT_v2.json",
        dict(
            status="PASS_P027_STAGE0_AUTHORITY_IDENTITY",
            at=now(),
            ledger=56,
            new_starts=0,
            optimizer_updates=0,
            input_contract=study.plan["input_contract"],
            scientific_definitions=ref(out / "scientific_definitions_v2.json"),
            source_identity=ref(out / "source_identity.json"),
            previous_pointer=ref(out / "registry_pointer_v16_snapshot.json"),
            previous_journal=ref(JOURNAL),
            views=summaries,
            recipes={
                v: dict(scale=study.recipe(v)["t2_scale"], epsilon=study.recipe(v)["epsilon"])
                for v in ("inner", "refit")
            },
            source_hashes=previous["source_hashes"],
            baseline_refs=list(references.values()),
            preservation_refs=preservation_references(),
            baseline_checks=checks,
            protected_refs=previous["protected_refs"],
            p2_entries=len(p2),
            protected_hash_only=True,
            storage_before=size,
            seconds=time.monotonic() - started,
            menu_status=(
                "Menu SP0/SP1/SP3 and October10 D8/D9 read; P027 explicitly elect"
                "s N20 stock-only FT16/TG20, rank4 and d16; full-peer comparator "
                "deferred with narrowed attribution"
            ),
        ),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    audit(parser.parse_args().out)


def verify_prefixes(out: Path) -> dict:
    """Reproduce prefix-only epsilon/scale populations and released feature operands."""
    import pandas as pd

    from .hf1m_ft16_source import ORDER
    from .objective_screen_source import gather, native_arrays
    from .temporal_screen_metrics import allocation

    study = LongStudy.discover(Path.cwd())
    checks = []
    for version, role in [("inner", "inner_train"), ("refit", "refit")]:
        fit = study.recipe(version)
        stop = fit["fit_stop_inclusive"]
        target = pd.read_parquet(
            checked(study.contract["files"]["targets"]),
            filters=[
                ("fit_version", "=", version),
                ("session_date_et", "<=", stop),
                ("label_eligible", "=", True),
            ],
        )
        if target.session_date_et.ge("2026-01-01").any():
            raise ValueError("P027_PROTECTED_PREFIX")
        mad = target.drop_duplicates("origin_id").cross_section_mad.to_numpy()
        epsilon = max(1e-4, 0.1 * float(np.median(mad)))
        if len(mad) != fit["epsilon_origins"] or epsilon != fit["epsilon"]:
            raise ValueError("P027_EPSILON_PREFIX_REPRODUCTION")
        view = scoped_view(study, role, stage=7)
        labels = ordered_targets(view)
        scale = max(float(np.median(abs(labels.TG20.to_numpy()))), 1e-6)
        if len(view.source.rows) != fit["t2_scale_origins"] or scale != fit["t2_scale"]:
            raise ValueError("P027_SCALE_PREFIX_REPRODUCTION")
        positions = (0, len(view.source.rows) // 2, len(view.source.rows) - 1)
        arrays = native_arrays(study, view)
        native = gather(view, arrays, positions, "native")
        fallback = gather(view, arrays, positions, "fallback")
        x = view.origin_batch(positions)["x"]
        for j, name in enumerate(ORDER):
            raw = native[..., j]
            filled = np.where(np.isfinite(raw), raw, fit["fallbacks"][name])
            expected = (
                (filled - fit["scalers"][name]["center"]) / fit["scalers"][name]["scale"]
            ).astype(np.float32)
            np.testing.assert_array_equal(x[..., j], expected)
            if not np.array_equal(~np.isfinite(raw), fallback[..., j]):
                raise ValueError("P027_FALLBACK_MASK_REPRODUCTION")
        checks.append(
            dict(
                fit_version=version,
                epsilon=epsilon,
                epsilon_origins=len(mad),
                scale=scale,
                scale_origins=len(view.source.rows),
                feature_windows=len(positions),
                channels=16,
                reconstruction="EXACT_FLOAT32",
            )
        )
    baselines = []
    for seed in (42, 123):
        for role in ROLES:
            v = "inner" if role.startswith("inner") else "refit"
            f = study.prediction(f"HF1M-LONG-TM0-T2-S{seed}-DEV1", role).copy()
            if "TG20" not in f:
                f["TG20"] = f.actual_TG20
            a = allocation(f, study.recipe(v)["t2_scale"])
            baselines.append(
                dict(seed=seed, role=role, rows=len(f), fixed_objective_z_mse=float(a.total.sum()))
            )
    receipt = dict(
        status="PASS_P027_PREFIX_NUMERICS",
        protected_numeric_access=False,
        checks=checks,
        baseline_objectives=baselines,
        optimizer_steps=0,
        new_starts=0,
    )
    write_json(out / "prefix_numerical_oracle_receipt.json", receipt)
    return receipt
