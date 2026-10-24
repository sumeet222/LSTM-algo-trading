"""P027 controlled synthetic full lifecycle; step calls and ledger mutations are forbidden."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from unittest.mock import patch

import torch

from .config import fingerprint, now, write_json
from .hf1m_ft16_source import ref
from .peer_screen_spec import ARMS, RUNS
from .temporal_screen_rehearsal import SyntheticStudy


def genuine_forward_probes(stage0: dict, private: Path) -> dict:
    """Two training prefixes only, three sparse origins each, no backward or fit loop."""
    import numpy as np

    from .hf1m_action_audit import SYMBOLS
    from .hf1m_ft16_source import ORDER, checked
    from .objective_screen_source import ordered_targets, scoped_view
    from .optimization_screen_diagnostics import original_identity
    from .peer_screen_data import donor_map, panel_from_rows, pool_for, validate_metadata
    from .peer_screen_engine import save_checkpoint, state_hash
    from .peer_screen_models import model_for, peer_statistics
    from .visualization.hf1m_long import LongStudy

    study = LongStudy.discover(Path.cwd())
    probes = []
    donors = []
    with np.load(checked(study.contract["files"]["components"]), allow_pickle=False) as archive:
        symbols = tuple(archive["symbols"])
        channels = tuple(archive["feature_order"])
    for version, role in [("inner", "inner_train"), ("refit", "refit")]:
        view = scoped_view(study, role, stage=7)
        validate_metadata(
            symbols, channels, view.source.fit["t2_scale"], stage0["recipes"][version]["scale"]
        )
        if view.summary() != stage0["views"][role]:
            raise ValueError("P027_REAL_PREFIX_POPULATION")
        original_identity(study, view, ordered_targets(view))
        positions = (0, len(view.source.rows) // 2, len(view.source.rows) - 1)
        x = torch.from_numpy(view.origin_batch(positions)["x"])
        actual_peer = peer_statistics(x[..., 0]).numpy()
        values = x[..., 0].numpy().astype(float)
        for i in range(20):
            other = np.delete(values, i, axis=1)
            np.testing.assert_allclose(actual_peer[:, i, :, 0], other.mean(1), rtol=1e-6, atol=2e-7)
            np.testing.assert_allclose(
                actual_peer[:, i, :, 1], other.std(1, ddof=0), rtol=1e-6, atol=2e-7
            )
        pool = pool_for(study, view)
        mapping = donor_map(view.source.rows, pool)
        mapping.to_parquet(private / (role + "_donor_mapping.parquet"), index=False)
        if len(mapping.loc[mapping.status.eq("MATCHED")]):
            selected = mapping.loc[mapping.status.eq("MATCHED")].iloc[:2]
            checked_panel = panel_from_rows(
                view, pool.iloc[selected.donor_position.to_numpy(dtype=int)]
            )
            if checked_panel.shape != (len(selected), 20, 48, 16):
                raise ValueError("P027_REAL_DONOR_SHAPE")
        donors.append(
            dict(
                role=role,
                origins=len(mapping),
                matched=int(mapping.status.eq("MATCHED").sum()),
                source_input_only=True,
            )
        )
        for arm in ARMS:
            model = model_for(arm).eval()
            before = state_hash(model)
            with torch.inference_mode():
                output = model(x)
                reference, reload = save_checkpoint(
                    private / f"UNTRAINED_FORWARD_ONLY_{arm}_{version}.pt",
                    model,
                    arm,
                    dict(scope="DRY_RUN_REAL_TRAIN_PREFIX", role=role, fit_version=version),
                )
                torch.testing.assert_close(output, reload.eval()(x), rtol=0, atol=0)
            if state_hash(model) != before:
                raise ValueError("P027_REAL_FORWARD_PROBE_UPDATED")
            probes.append(
                dict(
                    arm=arm,
                    role=role,
                    origins=3,
                    stock_sequences=60,
                    output_shape=list(output.shape),
                    checkpoint=reference,
                    backward_calls=0,
                    optimizer_step_calls=0,
                    genuine_source_target_oracle=True,
                    genuine_peer_M1_oracle=True,
                )
            )
        del view
    if symbols != SYMBOLS or channels != ORDER:
        raise ValueError("P027_REAL_COMPONENT_ORDER")
    return dict(scope="DRY_RUN_FORWARD_ONLY_REAL_TRAIN_PREFIX", probes=probes, donor_counts=donors)


def rehearse(
    out: Path, private: Path, validation: Path, receipt_name: str = "stage_1_receipt.json"
) -> None:
    from .peer_screen_authority import (
        JOURNAL,
        POINTER,
        code_binding,
        ensure,
        predecessor_gate,
        require_gate,
    )
    from .peer_screen_diagnostics import diagnose
    from .peer_screen_run import lifecycle

    stage0_path = out / "P027_STAGE_0_SOURCE_AND_AUTHORITY_RECEIPT_v2.json"
    stage0 = json.loads(stage0_path.read_text())
    if (
        stage0["status"] != "PASS_P027_STAGE0_AUTHORITY_IDENTITY"
        or private.exists()
        or JOURNAL.exists()
    ):
        raise ValueError("P027_NEW_REHEARSAL_NAMESPACE_REQUIRED")
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    before = ref(POINTER)
    started = time.monotonic()
    private.mkdir(parents=True)
    (private / ".gitignore").write_text("*\n!.gitignore\n")
    study = SyntheticStudy(private / "controlled_source")
    study.origins["origin_id"] = study.origins.origin_id.str.replace(
        "SYN:P026", "DRY_RUN:P027", regex=False
    )
    code = code_binding()
    draft = dict(
        scope="REHEARSAL_ONLY",
        code=code,
        input_contract=stage0["input_contract"],
        scientific_definitions=stage0["scientific_definitions"],
        recipes={
            a: {
                v: dict(scale=study.recipe(v)["t2_scale"], epsilon=study.recipe(v)["epsilon"])
                for v in ("inner", "refit")
            }
            for a in ARMS
        },
        source_hashes=stage0["source_hashes"],
        baseline_refs=stage0["baseline_refs"],
        protected_refs=stage0["protected_refs"],
        preservation_refs=stage0["preservation_refs"],
        validation=ref(validation),
        storage_before=stage0["storage_before"],
    )
    draft_path = private / "rehearsal_plan.json"
    write_json(draft_path, draft)
    calls = 0
    gates = []
    blocked = []

    def forbidden_step(*args, **kwargs):
        nonlocal calls
        calls += 1
        raise RuntimeError("P027_REHEARSAL_STEP_FORBIDDEN")

    with patch.object(torch.optim.AdamW, "step", forbidden_step):
        real_probes = genuine_forward_probes(stage0, private)
        for arm in ARMS:
            result = lifecycle(draft_path, arm, private / arm, rehearsal=True, study_override=study)
            gate = diagnose(
                draft,
                result,
                private / (arm + "_diagnostics"),
                rehearsal=True,
                study_override=study,
            )
            gp = private / (arm + "_diagnostics/gate.json")
            require_gate(gp, arm, rehearsal=True)
            try:
                require_gate(gp, arm)
            except ValueError:
                blocked.append(arm + "_REHEARSAL_NOT_LIVE")
            else:
                raise ValueError("P027_REHEARSAL_ESCAPED")
            gates.append(ref(gp))
            print(gate["status"] + " REHEARSAL_ONLY", flush=True)
    for label, operation in [
        ("NO_APPROVAL", lambda: ensure(draft_path, None, RUNS[0])),
        ("A5_NO_PRIOR_GATE", lambda: predecessor_gate(draft_path, RUNS[1], [])),
        ("A6_NO_PRIOR_GATE", lambda: predecessor_gate(draft_path, RUNS[2], [])),
    ]:
        try:
            operation()
        except (ValueError, FileNotFoundError):
            blocked.append(label)
        else:
            raise ValueError("P027_CONTROLLER_BYPASS")
    if calls or ref(POINTER) != before or JOURNAL.exists() or code_binding() != code:
        raise ValueError("P027_REHEARSAL_MUTATED_AUTHORITY")
    write_json(
        out / receipt_name,
        dict(
            status="PASS_P027_ZERO_STEP_REHEARSAL",
            scope="REHEARSAL_ONLY",
            at=now(),
            ledger=56,
            neural_starts=0,
            optimizer_step_calls=calls,
            code=code,
            execution_sha256=fingerprint(code),
            gates=gates,
            blocked=blocked,
            all_role_exports=12,
            exact_cases=66,
            synthetic_controlled_candles=True,
            dry_run=True,
            real_train_prefix_probes=real_probes,
            selector_receipts_are_stationary_metadata_simulations=True,
            source_identity=ref(stage0_path),
            validation=ref(validation),
            seconds=time.monotonic() - started,
        ),
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--private", type=Path, required=True)
    p.add_argument("--validation", type=Path, required=True)
    p.add_argument("--receipt-name", default="stage_1_receipt.json")
    a = p.parse_args()
    rehearse(a.out, a.private, a.validation, a.receipt_name)
