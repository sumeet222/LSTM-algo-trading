"""Zero-step P021 dry precheck and exact four-run proposal; grants no fit authority."""

from __future__ import annotations

import argparse
import json
import resource
import time
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import torch

from lstm_data.config import atomic_new, fingerprint, now, write_json
from lstm_data.controlled_loss import LossPolicy
from lstm_data.hf1m_ft16_loader import inverse_t2, load_model_input
from lstm_data.hf1m_ft16_source import ORDER, checked, read_hourly, ref
from lstm_data.hf1m_training_authority import IDS, POINTER, code_binding, ensure
from lstm_data.hf1m_training_data import CONTRACT, load_views
from lstm_data.hf20_replication_authority import read_rows
from lstm_data.neural_engine import SharedLSTM, batch_prediction, optimizer, seed_all
from lstm_data.neural_lifecycle import EarlyStop, state_hash


def prepare(out: Path) -> None:
    started = time.monotonic()
    stage0 = json.loads((out / "stage0_identity.json").read_text())
    if stage0["status"] != "PASS_IDENTITY" or checked(stage0["contract"]) != CONTRACT:
        raise ValueError("P021_IDENTITY_FIRST")
    gate = json.loads(checked(stage0["gate"]).read_text())
    for r in gate["evidence"].values():
        checked(r)
    allowlist = CONTRACT.parent / "numeric_file_allowlist.json"
    private = json.loads(allowlist.read_text())
    for r in private["files"]:
        checked(r)
    pointer = json.loads(POINTER.read_text())
    if read_rows(Path(pointer["real_journal"]))[-1]["global_started_pairs"] != 32:
        raise ValueError("P021_RECONCILE_LIVE_LEDGER")
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    # Guards execute before any file open, including hostile API role/date inputs.
    denied = []
    with patch.object(Path, "read_text", side_effect=AssertionError("unexpected file read")):
        for split in ("confirmation", "2026", "heldout", "test"):
            try:
                load_model_input(CONTRACT, split=split, fit_version="refit")
            except ValueError:
                denied.append(split)
        try:
            read_hourly({}, stop="2026-01-01")
        except ValueError:
            denied.append("protected_date")
    assert len(denied) == 5
    views = load_views(CONTRACT)
    parity = []
    for split, v in views.items():
        positions = (0, len(v.source.rows) // 2, len(v.source.rows) - 1)
        oracle = v.source.batch(positions)
        gathered = v.origin_batch(positions)
        assert np.array_equal(oracle["x"], gathered["x"])
        assert np.array_equal(oracle["y"], gathered["y"])
        scaled = v.source.batch(positions, target_mode="T2")["y"]
        s = v.source.fit["t2_scale"]
        reconstructed = inverse_t2(scaled.astype(np.float64), s)
        assert np.allclose(reconstructed, oracle["y"], atol=1e-5, rtol=1e-6)
        batch = v.batch(tuple(range(min(16, len(v.sessions)))))
        batch.validate()
        parity.append(
            dict(
                split=split,
                shape=list(batch.inputs.shape),
                origins=int(batch.origins.sum()),
                scale=s,
                source_batch_exact=True,
                inverse_max_error=float(np.max(abs(reconstructed - oracle["y"]))),
            )
        )
    init = {}
    forward = []
    for seed in (42, 123):
        seed_all(seed)
        model = SharedLSTM()
        initial = state_hash(model)
        init[str(seed)] = initial
        assert sum(v.numel() for v in model.parameters()) == 6433
        opt = optimizer(model)
        assert not opt.state
        assert [g["weight_decay"] for g in opt.param_groups] == [0.01, 0.0]
        assert len({id(p) for g in opt.param_groups for p in g["params"]}) == len(
            list(model.parameters())
        )
        model.eval()
        with torch.inference_mode():
            batch = views["inner_train"].batch(tuple(range(16)))
            t = time.monotonic()
            raw = batch_prediction(model, batch)
            elapsed = time.monotonic() - t
            assert raw.shape == batch.targets.shape and bool(torch.isfinite(raw).all())
            for arm in ("C0", "T2"):
                policy = LossPolicy(
                    arm, scale=views["inner_train"].source.fit["t2_scale"] if arm == "T2" else 1.0
                )
                assert bool(
                    torch.isfinite(
                        policy.objective(raw, batch.targets, batch.origins, stock_count=20)
                    ).all()
                )
                assert bool(torch.isfinite(policy.canonical(raw)).all())
        assert state_hash(model) == initial and not opt.state
        seed_all(seed)
        assert state_hash(SharedLSTM()) == initial
        forward.append(dict(seed=seed, seconds=elapsed, optimizer_steps=0, unchanged_weights=True))
    assert init["42"] != init["123"]
    selector = EarlyStop()
    for _ in range(12):
        selector.observe(1.0)
    assert selector.selected == 1 and selector.epoch == 12 and selector.status == "PATIENCE_STOP"
    precheck = dict(
        status="PASS_DRY_PRECHECK_AWAITING_LIVE_APPROVAL",
        optimizer_steps=0,
        parameters=6433,
        feature_order=list(ORDER),
        views={k: v.summary() for k, v in views.items()},
        batch_oracles=parity,
        protected_denied_before_file_read=denied,
        initial_hashes=init,
        forward_only=forward,
        dropout="nn.Dropout(0.10) after last hidden; no recurrent dropout",
        d6g_epoch1_selection_verified=True,
        all10_private_hashes_verified=len(private["files"]),
        elapsed_seconds=time.monotonic() - started,
        peak_rss_bytes_macos=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    )
    write_json(out / "dry_precheck.json", precheck)
    snapshot = out / "registry_pointer_v7_snapshot.json"
    atomic_new(snapshot, POINTER.read_bytes())
    registry = Path("configs/track_a_candidate_experiment_registry_v8_p021.json")
    write_json(
        registry,
        dict(
            schema=8,
            study="HF20_HF1M_LONG_v1",
            runs=list(IDS),
            opening_started=32,
            maximum_new_starts=4,
            effective_ceiling=200,
            permission=False,
            heldout_access=False,
            previous_definition=pointer["definition"],
            previous_journal=ref(Path(pointer["real_journal"])),
        ),
    )
    p = dict(
        schema=1,
        package="021",
        sealed_at=now(),
        fit_deadline=(pd.Timestamp.now(tz="UTC") + pd.Timedelta(hours=24)).isoformat(),
        runs=list(IDS),
        run_specs={
            i: dict(seed=s, arm=a)
            for i, s, a in zip(IDS, (42, 42, 123, 123), ("C0", "T2", "C0", "T2"))
        },
        opening_started=32,
        maximum_new_starts=4,
        ceiling=200,
        heldout_access=False,
        cpu_threads=4,
        device="cpu",
        workers=0,
        private_root=str(Path("artifacts/hf20_hf1m_long_v1") / out.name),
        input_contract=ref(CONTRACT),
        fit_recipes=ref(CONTRACT.parent / "train_only_fit_recipes.json"),
        source_revision=stage0["revision"],
        symbols=stage0["symbols"],
        feature_id=stage0["feature_id"],
        target_id=stage0["target_id"],
        model_input_id=stage0["input_id"],
        feature_order=list(ORDER),
        views=precheck["views"],
        code=code_binding(),
        code_sha256=fingerprint(code_binding()),
        previous_pointer=ref(snapshot),
        previous_journal=ref(Path(pointer["real_journal"])),
        registry_definition=ref(registry),
        budget_amendment=pointer["budget_amendment"],
        protected_refs=[
            stage0["gate"],
            stage0["closeout"],
            ref(allowlist),
            ref(CONTRACT.parent / "train_only_fit_recipes.json"),
            ref(Path("UNRESOLVED_MARKET_DATA_ANOMALIES.md")),
        ],
        dry_precheck=ref(out / "dry_precheck.json"),
        frozen_training=dict(
            layers=1,
            width=32,
            parameters=6433,
            dropout=0.1,
            dropout_location="output hidden",
            lookback=48,
            optimizer="AdamW",
            lr=0.001,
            betas=[0.9, 0.999],
            eps=1e-8,
            decay=[0.01, 0],
            clip=1,
            batch_sessions=16,
            d6g_min_epochs=12,
            d6g_max_epochs=60,
            d6g_patience=10,
            qualifying_loss_factor=0.999,
            selection="original TG20 equal-session validation MSE",
            refit="fresh same seed; selected epochs only",
        ),
        resources=dict(
            additional_storage_bound_bytes=1000000000,
            project_ceiling_bytes=10000000000,
            estimated_peak_rss_bytes=2000000000,
            estimated_four_run_wall_hours=[0.5, 6],
            estimate_basis="bounded CPU planning estimate; no optimization benchmark",
        ),
        rights=stage0["rights"],
        status="FROZEN_AWAITING_LIVE_APPROVAL",
    )
    plan = out / "experiment_design.json"
    write_json(plan, p)
    try:
        ensure(plan, None, IDS[0])
    except ValueError as error:
        assert str(error) == "P021_LIVE_APPROVAL_REQUIRED_ZERO_STEPS"
    else:
        raise AssertionError("unapproved fitting accepted")
    text = f"""# Package 021 four-run approval proposal

Frozen proposal SHA256: `{ref(plan)["sha256"]}`.
Execution code SHA256: `{p["code_sha256"]}`.
Input contract SHA256: `{p["input_contract"]["sha256"]}`.

Exactly C0 seed42 → T2 seed42 → C0 seed123 → T2 seed123, IDs {", ".join(IDS)}.
Four candidate starts charge 32→33→34→35→36/200; no retry, tuning or extra fit.
Same released HF minute-derived FT16/TG20 inputs, 20-stock order and saved inner/refit recipes.
6,433-parameter TM0, output dropout0.10, AdamW .001, clip1, 16 sessions/batch,
D6g 12–60/patience10/0.1% qualifying original-TG20 validation improvement; fresh same-seed refit.
The selected epoch may be1. Calibration and refit predictions retain distinct roles and checkpoints.

Dry precheck passed with zero optimizer steps: all frozen counts, loader/gather parity,
saved T2 inverse, RNG separation, parameter/optimizer groups and protected-role/date rejection.
CPU4 threads, zero workers; planning estimate0.5–6h, ≤2GB peak RSS, ≤1GB additional local storage,
within the inherited10GB storage ceiling. No market data network acquisition.

This is exploratory, stock-only private research under the existing reported maintainer permission
and assumed publication clock. It is not rights/execution certification. No2026 numerical access,
production/trading, legacy numerical inputs, extra starts or Git operations are granted.
Authority expires at {p["fit_deadline"]}; no starts or optimization after expiry.
Package021 introductory execution-style paragraph and §1.3 preserve the separate live ledger gate.

Read `experiment_design.json` and `dry_precheck.json` for exact bindings and populations.
Training and downstream dashboard completion await the live response; no start is reserved yet.
"""
    atomic_new(out / "experiment_design.md", text.encode())
    print(
        json.dumps(
            dict(proposal=ref(plan), code_sha256=p["code_sha256"], precheck=precheck), indent=2
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    prepare(parser.parse_args().out)
