"""Prepare the exact HF20 two-pair proposal without reserving or fitting."""

from __future__ import annotations

import argparse
import json
import shutil
import time
from pathlib import Path

import numpy as np
import torch

from lstm_data.config import digest, fingerprint, write_json
from lstm_data.controlled_loss import LossPolicy
from lstm_data.hf20_source import SYMBOLS
from lstm_data.hf20_training_authority import IDS, code_binding, reference
from lstm_data.hf20_training_data import CONTRACT, fit_scale, load_views, target_values
from lstm_data.nb1_authority import journal_rows
from lstm_data.p2_closure import load_deferred_work


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out
    out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    c = json.loads(CONTRACT.read_text())
    assert len(load_deferred_work(Path("configs/track_a_p2_engineering_handoff_v1.json"))) == 16
    old = journal_rows(Path("reports/audit/track_a_real_pairs_v5.jsonl"))
    assert old[-1]["global_started_pairs"] == 28
    pointer = Path("configs/CURRENT_EXPERIMENT_REGISTRY.json")
    snapshot = out / "registry_pointer_v5_snapshot.json"
    snapshot.write_bytes(pointer.read_bytes())
    previous = reference(Path("reports/audit/track_a_real_pairs_v5.jsonl"))
    amendment = json.loads(pointer.read_text())["budget_amendment"]
    definition = Path("configs/track_a_candidate_experiment_registry_v6.json")
    write_json(
        definition,
        dict(
            schema=6,
            opening_started=28,
            ceiling=200,
            new_pair_limit=2,
            real_journal="reports/audit/track_a_real_pairs_v6.jsonl",
            previous_pointer=reference(snapshot),
            previous_journal=previous,
            budget_amendment=amendment,
            counts_failed_starts=True,
            approved_order=list(IDS),
            production_migration=False,
        ),
    )
    views = load_views()
    scales = {s: fit_scale(views[s], s) for s in ("inner_train", "refit")}
    write_json(out / "t2_scale_inner_refit.json", scales)
    examples = []
    for split, day, origin in [
        ("refit", "2023-03-22", 1),
        ("refit", "2024-03-11", 1),
        ("development", "2025-04-10", 1),
    ]:
        v = views[split]
        selected = v.source.rows.loc[
            v.source.rows.session.eq(day) & v.source.rows.origin.eq(origin)
        ]
        if selected.empty:
            # Missing source influence is an intentional exclusion, never a fabricated batch.
            index_path = Path(c["origins"]["refit"]["path"])
            import pandas as pd

            row = pd.read_csv(index_path).query("session == @day and origin == @origin").iloc[0]
            examples.append(
                dict(
                    split=split,
                    session=day,
                    origin=origin,
                    admitted=False,
                    input_exclusion=str(row.input_exclusion),
                    source_ready=bool(row.source_ready),
                )
            )
        else:
            pos = int(selected.index[0])
            b = v.source.batch((pos,))
            row = selected.iloc[0]
            assert b.x.shape == (1, 20, 48, 16) and np.isfinite(b.x).all()
            examples.append(
                dict(
                    split=split,
                    session=day,
                    origin=origin,
                    admitted=True,
                    x_shape=list(b.x.shape),
                    future_label_channels=0,
                    cutoff=str(row.feature_cutoff_UTC),
                    issuance=str(row.forecast_issuance_UTC),
                    maturity=str(row.label_maturity_UTC),
                    label_values_sha256=fingerprint(b.y.tolist()),
                )
            )
    recipes = json.loads(Path(c["recipes"]["path"]).read_text())
    decomposition = []
    with np.load(c["targets"]["path"]) as t:
        for split in ("inner_train", "refit", "development"):
            row = views[split].source.rows.iloc[0]
            d, o = int(row.day_index), int(row.origin) - 1
            returns = t["returns"][d, :, o]
            med = float(np.median(returns))
            mad = float(np.median(np.abs(returns - med)))
            recipe = "inner" if split == "inner_train" else "refit"
            epsilon = recipes[recipe]["epsilon"]
            expected = (returns - med) / (mad + epsilon)
            actual = t[recipe + "_targets"][d, :, o]
            assert np.array_equal(expected.astype(np.float32), actual)
            decomposition.append(
                dict(
                    split=split,
                    session=str(row.session),
                    origin=o + 1,
                    returns=returns.tolist(),
                    median=med,
                    MAD=mad,
                    epsilon=epsilon,
                    canonical_targets=actual.tolist(),
                    float32_exact=True,
                )
            )
    for split in scales:
        independent = max(
            float(np.median(np.abs(target_values(views[split]).astype(np.float64)))), 1e-6
        )
        assert independent == scales[split]["scale"]
        y = torch.tensor([-1e8, -20.0, 0.0, 20.0, 1e8], dtype=torch.float64)
        p = LossPolicy("T2", scale=independent)
        assert torch.allclose(p.canonical(torch.asinh(y / independent)), y, rtol=1e-12)
    write_json(
        out / "input_mask_and_target_oracles.json",
        dict(
            views={k: v.summary() for k, v in views.items()},
            examples=examples,
            targets=decomposition,
            T2_independent_scales=True,
            live_model_optimizer_steps=0,
            source_publication="UNKNOWN_IDEALIZED_BOUNDARY_ASSUMPTION",
        ),
    )
    protected = []
    # Preserve all existing raw bytes and checkpoints without decoding any protected history.
    paths = (
        set(Path("data/raw").rglob("*"))
        | set(Path("artifacts").rglob("*.pt"))
        | set(Path("checkpoints").rglob("*.pt"))
    )
    paths |= set(Path("reports").rglob("*.pt"))
    paths |= set(Path("reports/audit").glob("*.jsonl"))
    paths |= set(Path("docs/track_a").glob("*.md"))
    paths |= {
        Path("configs/CURRENT_PROTOCOL.json"),
        CONTRACT,
        Path(c["store"]["path"]),
        Path(c["targets"]["path"]),
    }
    paths |= {
        Path(r["path"])
        for r in c["code"] + [c["config"], c["recipes"]] + list(c["origins"].values())
    }
    for path in sorted(p for p in paths if p.is_file()):
        protected.append(dict(path=str(path), bytes=path.stat().st_size, sha256=digest(path)))
    write_json(out / "preservation_before.json", dict(files=protected, byte_hash_only=True))
    scope = dict(
        candidate_only=True,
        seed=42,
        architecture="TM0",
        features=c["feature_id"],
        target=c["target_id"],
        calibration="D6g_60_12_10_STRICT_0.999_CANONICAL_MSE",
        refit="FRESH_EXACT_SELECTED_EPOCHS",
        evaluation="EXPLORATORY_DEVELOPMENT_ONLY",
        training_dates=["2022-12-01", "2025-03-28"],
        development_dates=["2025-03-31", "2026-01-06"],
        heldout_locked_from="2026-01-07",
        global_budget="28_TO_30_UNDER_200",
        rights="RESEARCHER_ATTESTED_BOUNDED_LOCAL_USE",
        changes="T2_ASINH_TRAIN_TARGET_ONLY_SINGLE_INVERSE",
        no_extra_runs=True,
        no_trading=True,
    )
    plan = dict(
        package="TA-HF20-FIRST-TM0-T2-TRAINING-001",
        runs=list(IDS),
        scope=scope,
        input_contract=reference(CONTRACT),
        source_revision=c["source_revision"],
        symbols=list(SYMBOLS),
        feature_id=c["feature_id"],
        target_id=c["target_id"],
        clock_id=c["clock_id"],
        views={k: v.summary() for k, v in views.items()},
        scales=scales,
        code=code_binding(),
        code_sha256=fingerprint(code_binding()),
        opening_started=28,
        ceiling=200,
        maximum_new_starts=2,
        previous_pointer=reference(snapshot),
        previous_journal=previous,
        budget_amendment=amendment,
        registry_definition=reference(definition),
        protected_refs=[previous, amendment],
        heldout_access=False,
        cpu_threads=1,
        fit_deadline="2026-10-16T23:23:56+00:00",
        package_started_at="2026-10-16T21:38:56+00:00",
        package_deadline="2026-10-16T23:38:56+00:00",
        minimum_pair_reserve_seconds=900,
        maximum_package_seconds=7200,
        audit_reserve_seconds=900,
        historical_runtime_estimate_NOT_MEASURED_HF20=dict(
            five_stock_pair_seconds=83.79727812501369,
            five_stock_fitting_seconds=55.89974912587786,
            historical_thread_count=1,
            cautious_pair_projection_seconds=1800,
            method="Conservative allowance; no real optimizer benchmark",
        ),
    )
    write_json(out / "experiment_design.json", plan)
    write_json(
        out / "source_and_contract_check.json",
        dict(
            status="PASS_CONDITIONAL",
            contract=plan["input_contract"],
            views=plan["views"],
            ledger=28,
            source_requests=0,
            optimizer_steps=0,
            disk_free_bytes=shutil.disk_usage(".").free,
            preflight_seconds=time.monotonic() - start,
        ),
    )
    text = f"""# HF20 two-pair live approval proposal

Proposal SHA256 `{digest(out / "experiment_design.json")}`. Execution SHA256
`{plan["code_sha256"]}`.

Exactly C0 then T2, seed42, one D6g calibration plus fresh refit per pair. Shared16×48→32
LSTM,6433 parameters; AdamW .001/decay .01 weights and0biases, clip1,16whole sessions;
canonical TG20 validation MSE selects qualifying checkpoint for both. T2 pooled unique
training-observation median scale, floor1e-6, separate inner/refit, single scale*sinh inverse.
No changed source, names, masks, dates, features, TG20 or chronology. Verified872/110/998/366
origins over436/55/499/183sessions. Inner s={scales["inner_train"]["scale"]}; refit
s={scales["refit"]["scale"]}.

Two sequential append-only starts28→29→30/200; historical ledgers and40-cap metadata unchanged;
v6 links exact v5 journal/pointer. No retry or extra seed/optimizer probe, no held-out
numerical access, no trading, no Git write. Conditional retrospective cohort, unverified
issuer/action vintage/publication/dividends, as-reported units and idealized vendor
timing/hourly-close proxy remain. Bounded researcher-attested local use only; no independent
certification or redistribution authority.

Prior five-stock historical pair83.8s is context, not an HF20 measurement; fixed CPU1thread.
Cautious allowance30min/pair; package deadline23:38:56UTC with15min reserve; no pair starts
with<15min fitting reserve. No optimizer step before actual live approval.
"""
    (out / "experiment_design.md").write_text(text)
    (out / "authority_request.md").write_text(
        text + "\nThis package §D explicitly requires new exact live approval before STARTED.\n"
    )
    (out / "preflight_and_dependencies.md").write_text(
        "Clean branch feat/track-a-data-intake at ec8a1738f28b515d32517edd765c7746f9779540; "
        "fetched, upstream0/0.16P2 entries hash-verified; no gates implicitly cleared. "
        "Existing dependencies only. No secrets or source requests. All existing "
        "raw/checkpoint/journal/protocol bytes snapshotted before fits. Shared numerical "
        "engine extension regression-tested before approval; five-stock defaults preserved.\\n "
    )
    print(
        json.dumps(
            dict(
                out=str(out),
                proposal_sha256=digest(out / "experiment_design.json"),
                code_sha256=plan["code_sha256"],
                protected_files=len(protected),
            )
        )
    )


if __name__ == "__main__":
    main()
