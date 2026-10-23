"""Prepare a P022 repair for live review, without optimizer updates or ledger writes."""

from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import torch

from lstm_data.config import digest, fingerprint, now, write_json
from lstm_data.hf1m_ft16_source import checked, ref
from lstm_data.hf1m_training_data import TrainingView
from lstm_data.neural_lifecycle import state_hash
from lstm_data.objective_screen_authority import rows
from lstm_data.objective_screen_loss import ARMS, RUNS, Objective, model_for
from lstm_data.objective_screen_recovery import code_binding
from lstm_data.objective_screen_run import epoch_pass, predict, record_epoch, save_checkpoint
from lstm_data.objective_screen_source import scoped_view
from lstm_data.visualization.hf1m_long import LongStudy


def verify_refs(value: object, found: dict[str, dict]) -> None:
    """Hash reference records recursively; never decode source numeric files."""
    if isinstance(value, dict):
        if {"path", "sha256", "bytes"} <= value.keys():
            checked(value)
            found[value["path"]] = value
        if {"raw_path", "raw_sha256", "raw_bytes"} <= value.keys():
            raw = dict(path=value["raw_path"], sha256=value["raw_sha256"], bytes=value["raw_bytes"])
            checked(raw)
            found[raw["path"]] = raw
        for item in value.values():
            verify_refs(item, found)
    elif isinstance(value, list):
        for item in value:
            verify_refs(item, found)


def prepare(previous: Path, out: Path) -> None:
    original = previous / "experiment_design_v2.json"
    p = json.loads(original.read_text())
    history = rows()
    if len(history) != 2 or history[-1]["status"] != "FAILED":
        raise ValueError("P022_EXACT_FAILED_HISTORY_REQUIRED")
    if history[-1]["global_started_pairs"] != 37:
        raise ValueError("STOP_LEDGER_MISMATCH")
    if (out / "experiment_design.json").exists():
        raise ValueError("P022_REPAIR_ALREADY_SEALED")
    failed_private = Path(p["private_root"]) / RUNS[0]
    batch_path = failed_private / "optimizer_batches.jsonl"
    batches = pd.DataFrame([json.loads(line) for line in batch_path.read_text().splitlines()])
    assert len(batches) == 374 and int(batches.optimizer_step.sum()) == 316
    assert set(batches.epoch) == {1, 2}
    assert not list(failed_private.glob("*.pt"))
    failure_files = [ref(f) for f in (previous / RUNS[0]).rglob("*") if f.is_file()]
    failure_files += [ref(batch_path), ref(previous / "H2_execution.log")]
    write_json(out / "failure_inventory.json", failure_files)
    write_json(
        out / "failed_start_diagnosis.json",
        dict(
            status="STOP_H2",
            ledger=37,
            failed_start=37,
            optimizer_steps=316,
            completed_training_epochs=2,
            completed_validation_epochs=2,
            retained_epoch_summaries=1,
            retained_batch_records=374,
            selected_checkpoint_available=False,
            refit_started=False,
            development_numeric_access=False,
            protected_numeric_access=False,
            cause="create-only write_json called a second time on epochs_progress.json",
            recovery_requires="new H2 start charged 38, then original W1/E1/R1 starts 39/40/41",
        ),
    )
    found: dict[str, dict] = {}
    verify_refs(p["protected_refs"], found)
    source_manifest = Path(
        "reports/data_audit/ta018d_hf1m_long_2026-10-22_155547/complete_acquisition_manifest.json"
    )
    verify_refs(json.loads(source_manifest.read_text()), found)
    write_json(
        out / "source_preservation.json",
        dict(
            status="PASS",
            files=len(found),
            bytes=sum(r["bytes"] for r in found.values()),
            mode="SHA/size only; no source numeric decoding",
            references=list(found.values()),
        ),
    )
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    study = LongStudy.discover(Path.cwd())
    print(
        json.dumps(json.loads((previous / "active_dataset_identity.json").read_text())), flush=True
    )
    private = Path("artifacts/hf20_hf1m_long_v1") / out.name
    dry = private / "zero_step_preflight"
    dry.mkdir(parents=True, exist_ok=False)
    checks = []
    with patch.object(torch.optim.AdamW, "step", side_effect=AssertionError("NO_FIT")):
        for arm in ARMS:
            model = model_for(arm)
            initial = state_hash(model)
            progress: list[dict] = []
            destination = dry / arm
            destination.mkdir()
            for role, phase in [("inner_train", "calibration"), ("refit", "refit")]:
                view = scoped_view(study, role, stage=2)
                selected = view.source.rows.loc[
                    view.source.rows.session_date_et.isin(view.sessions[:2])
                ].reset_index(drop=True)
                source = replace(
                    view.source,
                    rows=selected,
                    targets=view.source.targets.loc[
                        view.source.targets.origin_id.isin(selected.origin_id)
                    ],
                )
                tiny = TrainingView(source, role)
                policy = Objective(arm, p["recipes"][source.fit_version])
                for e in (1, 2):
                    result = epoch_pass(model, tiny, e, policy)
                    assert result["optimizer_steps"] == 0 and state_hash(model) == initial
                    progress.append(dict(phase=phase, training=result))
                    record_epoch(destination, progress)
                    assert (
                        json.loads((destination / "epochs_progress.json").read_text())[-1][
                            "training"
                        ]["epoch"]
                        == e
                    )
                checkpoint = save_checkpoint(
                    destination / f"{phase}.pt",
                    model,
                    dict(arm=arm, role=role, zero_step=True),
                    arm,
                )
                frame = predict(
                    model,
                    tiny,
                    arm,
                    dict(
                        run_id="UNTRAINED_REPAIR_PREFLIGHT", checkpoint_sha256=checkpoint["sha256"]
                    ),
                )
                path = destination / f"{role}.parquet"
                frame.to_parquet(path, index=False)
                assert len(pd.read_parquet(path)) == len(selected) * 20
                checks.append(
                    dict(
                        arm=arm,
                        role=role,
                        two_progress_writes=True,
                        optimizer_steps=0,
                        checkpoint=checkpoint,
                        export=ref(path),
                    )
                )
    write_json(
        out / "zero_step_preflight.json",
        dict(
            status="PASS",
            checks=checks,
            optimizer_steps=0,
            real_source_epochs_evaluated=16,
            protected_numeric_access=False,
        ),
    )
    snapshot = out / "registry_pointer_v10_failed_snapshot.json"
    snapshot.write_bytes(Path("configs/CURRENT_EXPERIMENT_REGISTRY.json").read_bytes())
    proposal = dict(p)
    proposal.update(
        recovery="P022_PROGRESS_REPAIR_V1",
        created=now(),
        predecessor_approved_plan=ref(original),
        previous_pointer=ref(snapshot),
        previous_journal=ref(Path("reports/audit/track_a_real_pairs_v10_p022.jsonl")),
        opening_started=37,
        maximum_new_starts=4,
        projected_final_started=41,
        failed_start_preserved=True,
        additional_h2_restart_requires_live_approval=True,
        journal="reports/audit/track_a_real_pairs_v11_p022_repair.jsonl",
        registry_definition="configs/track_a_candidate_experiment_registry_v11_p022_repair.json",
        private_root=str(private),
        code=code_binding(),
        execution_sha256=fingerprint(code_binding()),
        zero_step_preflight=ref(out / "zero_step_preflight.json"),
        correction="Immutable epoch receipts plus atomically replaced progress snapshot. "
        "No scientific change; original failed H2 remains charged. No surviving "
        "checkpoint, so H2 is a new start, not checkpoint continuation.",
        fit_authority="NONE_PENDING_NEW_LIVE_REPAIR_APPROVAL",
    )
    proposal["protected_refs"] = p["protected_refs"] + failure_files + [ref(original)]
    write_json(out / "experiment_design.json", proposal)
    print(
        json.dumps(
            dict(
                proposal_sha256=digest(out / "experiment_design.json"),
                execution_sha256=proposal["execution_sha256"],
            )
        ),
        flush=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--previous", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.previous, args.out)
