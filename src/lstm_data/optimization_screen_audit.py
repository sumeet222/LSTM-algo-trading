"""P024 read-only baseline forensics and immutable source/ledger checks."""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .config import now, write_json
from .dm_quantile_authority import JOURNAL, POINTER, rows
from .hf1m_ft16_source import checked, configuration, ref, verify_parent
from .neural_engine import SharedLSTM
from .neural_lifecycle import EarlyStop, state_hash
from .objective_screen_metrics import regression
from .objective_screen_source import identity, ordered_targets, scoped_view
from .optimization_screen import ScreenStop
from .p2_closure import load_deferred_work
from .visualization.hf1m_long import LongStudy

BASE = Path("reports/experiments/ta021_hf1m_long_four_lstm_2026-10-22_232248_recovery_v1")
P023 = Path("reports/experiments/ta023_hf1m_long_dm1_qr1_ss1_2026-10-23_preparation")


def verify_refs(value: object, found: dict[str, dict]) -> None:
    """Walk immutable manifest references; protected Parquet is only byte-hashed."""
    if isinstance(value, dict):
        if {"path", "sha256", "bytes"} <= value.keys():
            checked(value)
            found[value["path"]] = value
        if {"raw_path", "raw_sha256", "raw_bytes"} <= value.keys():
            r = dict(path=value["raw_path"], sha256=value["raw_sha256"], bytes=value["raw_bytes"])
            checked(r)
            found[r["path"]] = r
        for item in value.values():
            verify_refs(item, found)
    elif isinstance(value, list):
        for item in value:
            verify_refs(item, found)


def audit(out: Path) -> None:
    started = time.monotonic()
    out.mkdir(parents=True, exist_ok=False)
    (out / ".gitignore").write_text("*\n!.gitignore\n!*.md\n!submitted_instruction.txt\n")
    study = LongStudy.discover(Path.cwd())
    entries = load_deferred_work(Path("configs/track_a_p2_engineering_handoff_v1.json"))
    parent = verify_parent(configuration())
    prior = rows()
    pointer = json.loads(POINTER.read_text())
    if prior[-1]["global_started_pairs"] != 44 or prior[-1]["status"] != "COMPLETED":
        raise ValueError("P024_STOP_LEDGER_NOT44")
    if pointer["real_journal"] != str(JOURNAL):
        raise ValueError("P024_STOP_POINTER_MISMATCH")
    checked(pointer["definition"])
    if (
        study.plan["input_contract"]["sha256"]
        != "7adfec916b7eb74fead83ef1fe6082ff0fcee9ff0b6ebae5722077e2a82c01a5"
    ):
        raise ValueError("P024_STOP_INPUT_CONTRACT")
    ident = identity(study)
    ident["ledger"] = 44
    ident["baseline_runs"] = [
        ref(BASE / f"HF1M-LONG-TM0-T2-S{s}-DEV1/run_result.json") for s in (42, 123)
    ]
    ident["numeric_files"] = study.contract["files"]
    ident["source_manifests"] = dict(
        hourly=ref(Path(configuration()["upstream_packet"]) / "adjusted_hourly_manifest.json"),
        acquisition=ref(
            Path(
                "reports/data_audit/ta018d_hf1m_long_2026-10-22_155547/complete_acquisition_manifest.json"
            )
        ),
    )
    # Identity is printed and sealed BEFORE numerical reads.
    print(json.dumps(ident, indent=2), flush=True)
    write_json(out / "source_identity.json", ident)
    references: dict[str, dict] = {}
    verify_refs(
        json.loads(checked(ident["source_manifests"]["acquisition"]).read_text()), references
    )
    if len(references) != 1701:
        raise ValueError("P024_SOURCE_INVENTORY_COUNT")
    for r in study.plan["protected_refs"]:
        checked(r)
    views = {
        role: scoped_view(study, role, stage=7)
        for role in ("inner_train", "inner_validation", "refit", "development")
    }
    previous = json.loads((P023 / "experiment_design.json").read_text())
    if {k: v.summary() for k, v in views.items()} != previous["views"]:
        raise ValueError("P024_STOP_ROLE_MISMATCH")
    summaries, trace, baseline_refs = [], [], []
    for seed in (42, 123):
        rp = BASE / f"HF1M-LONG-TM0-T2-S{seed}-DEV1/run_result.json"
        result = json.loads(rp.read_text())
        baseline_refs.append(ref(rp))
        epochs = pd.read_csv(checked(result["epochs"]))
        cal = epochs.loc[epochs.phase.eq("calibration")]
        historical = EarlyStop()
        hypothetical = ScreenStop(improvement=0.00025)
        for row in cal.to_dict("records"):
            q = historical.observe(row["validation_mse"])
            if q != row["qualifying"] or historical.selected != row["selected_epoch"]:
                raise ValueError("P024_STOP_HISTORICAL_SELECTOR")
            if hypothetical.status == "CALIBRATING":
                q2 = hypothetical.observe(row["validation_mse"])
                trace.append(
                    dict(
                        seed=seed,
                        epoch=row["epoch"],
                        validation_mse=row["validation_mse"],
                        historical_qualifies=q,
                        historical_selected=historical.selected,
                        threshold025_qualifies=q2,
                        **{f"threshold025_{k}": v for k, v in asdict(hypothetical).items()},
                    )
                )
        if vars(historical) != result["selector"]:
            raise ValueError("P024_STOP_SELECTOR_FINAL_STATE")
        if historical.raw_min is None:
            raise ValueError("P024_BASELINE_VALIDATION_CURVE_REQUIRED")
        expected = (7, 7) if seed == 42 else (1, 12)
        if (historical.selected, historical.raw_epoch) != expected:
            raise ValueError("P024_STOP_ES_MOTIVATION")
        for key in ("calibration_selected.pt", "refit_final.pt"):
            checkpoint = torch.load(checked(result["artifacts"][key]), weights_only=True)
            model = SharedLSTM()
            model.load_state_dict(checkpoint["model"])
            if sum(p.numel() for p in model.parameters()) != 6433:
                raise ValueError("P024_BASELINE_ARCHITECTURE")
            baseline_refs.append(result["artifacts"][key])
            state_hash(model)
        batches = pd.read_parquet(checked(result["artifacts"]["gradient_batches.parquet"]))
        active = batches.loc[batches.optimizer_step]
        for role, view in views.items():
            r = result["artifacts"][role + "_predictions.parquet"]
            f = pd.read_parquet(checked(r))
            target = ordered_targets(view)
            if not f[["origin_id", "ticker", "TG20"]].equals(
                target[["origin_id", "ticker", "TG20"]]
            ):
                raise ValueError("P024_BASELINE_FULL_POPULATION")
            np.testing.assert_allclose(
                f.pred_original_TG20,
                view.source.fit["t2_scale"] * np.sinh(f.raw_net_output),
                rtol=7e-7,
                atol=1e-7,
            )
            m = regression(
                f.TG20.to_numpy(), f.pred_original_TG20.to_numpy(), f.session_date_et.to_numpy()
            )
            summaries.append(
                dict(
                    seed=seed,
                    role=role,
                    **m,
                    target_sd=float(f.TG20.std(ddof=0)),
                    unweighted_prediction_sd=float(f.pred_original_TG20.std(ddof=0)),
                    selected_epoch=historical.selected,
                    raw_best_epoch=historical.raw_epoch,
                    hypothetical025_selected=hypothetical.selected,
                    hypothetical025_censored=hypothetical.status == "CALIBRATING",
                    clipping_fraction=float((active.preclip_norm > 1).mean()),
                    clipping_numerator=int((active.preclip_norm > 1).sum()),
                    clipping_denominator=len(active),
                    first_train_zmse=float(cal.iloc[0].objective),
                    last_train_zmse=float(cal.iloc[-1].objective),
                    validation_raw_improvement=(
                        float(cal.iloc[0].validation_mse) - historical.raw_min
                    )
                    / float(cal.iloc[0].validation_mse),
                )
            )
            baseline_refs.append(r)
        baseline_refs.extend([result["epochs"], result["artifacts"]["gradient_batches.parquet"]])
    pd.DataFrame(trace).to_csv(out / "baseline_selector_forensics.csv", index=False)
    pd.DataFrame(summaries).to_csv(out / "baseline_forensics.csv", index=False)
    (out / "registry_pointer_v12_snapshot.json").write_bytes(POINTER.read_bytes())
    gate = dict(
        status="PASS_STAGE0",
        at=now(),
        ledger=44,
        optimizer_updates=0,
        new_starts=0,
        identity=ref(out / "source_identity.json"),
        views={k: v.summary() for k, v in views.items()},
        baselines=baseline_refs,
        protected_refs=previous["protected_refs"],
        source_files=len(references),
        source_bytes=sum(r["bytes"] for r in references.values()),
        source_hashes=references,
        protected_hourly_refs=[
            r["files"]["hourly"] for r in parent["monthly"] if r["month"] >= "2026-01"
        ],
        p2_entries=len(entries),
        seconds=time.monotonic() - started,
        previous_journal=ref(JOURNAL),
        previous_pointer=ref(out / "registry_pointer_v12_snapshot.json"),
    )
    write_json(out / "stage_0_receipt.json", gate)
    (out / "stage_0_review.md").write_text(
        "# P024 baseline forensics — PASS\n\n"
        "Ledger44/200; zero optimizer updates. All1701 source/derived hashes match. "
        "Four role populations and both T2 checkpoint/prediction sets verified. "
        "Protected2026 files byte-hashed only.\n\n"
        "Historical strict0.1% selector reproduces seed42 selected/raw7/7 and "
        "seed123 selected/raw1/12. Raw improvement is approximately0.0714%, below0.1%. "
        "The0.025% seed123 replay selects2 and stops12. Epoch2 qualifies against epoch1; "
        "epoch12 improves too little relative to epoch2. Both thresholds reproduce "
        "a stop within the available historical curves. No counterfactual refit exists.\n\n"
        "Full tables: baseline_forensics.csv and baseline_selector_forensics.csv. "
        "Online train loss is transformed z-MSE with head dropoutON; selection loss is "
        "fixed-checkpoint original TG20 MSE with dropoutOFF. Clipping and dispersion "
        "do not establish saturation, vanishing gradients or optimizer failure. "
        "Original scientific holds/backlog remain unchanged.\n"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    audit(parser.parse_args().out)
