"""Freeze Package 022 design and validate source identity without optimizer steps."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from unittest.mock import patch

import numpy as np

from lstm_data.config import digest, now, write_json
from lstm_data.hf1m_ft16_source import checked, ref
from lstm_data.hf1m_training_data import CONTRACT, COUNTS
from lstm_data.hf1m_training_recovery import read_rows
from lstm_data.neural_lifecycle import state_hash
from lstm_data.objective_screen_loss import ARMS, RUNS, model_for
from lstm_data.objective_screen_source import identity, scoped_view
from lstm_data.p2_closure import load_deferred_work
from lstm_data.visualization.hf1m_long import LongStudy, dates


def prepare(out: Path, instruction: Path) -> None:
    if out.exists():
        raise ValueError("P022_NEW_OUTPUT_REQUIRED")
    study = LongStudy.discover(Path.cwd())
    ledger = read_rows()
    if ledger[-1]["global_started_pairs"] != 36 or ledger[-1]["status"] != "COMPLETED":
        raise ValueError("STOP_LEDGER_MISMATCH")
    ident = identity(study)
    print(json.dumps(ident, indent=2), flush=True)
    deferred = load_deferred_work(Path("configs/track_a_p2_engineering_handoff_v1.json"))
    for reference in study.plan["protected_refs"] + list(study.contract["files"].values()):
        checked(reference)
    out.mkdir(parents=True)
    (out / ".gitignore").write_text("*\n!.gitignore\n")
    (out / "submitted_instruction.txt").write_bytes(instruction.read_bytes())
    write_json(out / "active_dataset_identity.json", ident)
    design = dict(
        schema=1,
        created=now(),
        identity=ident,
        runs=list(RUNS),
        arms=list(ARMS),
        seed=42,
        opening_started=36,
        maximum_new_starts=4,
        final_started=40,
        ceiling=200,
        input_contract=ref(CONTRACT),
        baseline_plan=study.plan,
        prior_pointer=ref(Path("configs/CURRENT_EXPERIMENT_REGISTRY.json")),
        prior_journal=ref(Path("reports/audit/track_a_real_pairs_v9.jsonl")),
        submitted_instruction=ref(out / "submitted_instruction.txt"),
        stage1=dict(
            roles=["inner_train", "inner_validation"],
            summaries=["latest", "valid_mean48", "last_minus_first"],
            representations=["native", "scaled"],
            precursor_channels=["M1", "V1", "Q2", "B1"],
            subperiods=[
                ["2010-07-01", "2014-12-31"],
                ["2015-01-01", "2018-12-31"],
                ["2019-01-01", "2023-01-23"],
            ],
            quintiles=[0.2, 0.4, 0.6, 0.8],
            bins="below train min; frozen quintiles; above train max; missing",
            bootstrap_replicates=400,
            bootstrap_seed=22042,
            bootstrap=(
                "resample entire calendar months; recompute equal-day mean "
                "IC; descriptive percentile95 CI"
            ),
            sensitivity="nonoverlapping adjacent two-month blocks, same400 replicates",
            controls="all NORMAL cases, no post-event matching",
            regimes="native V1 and Q2 latest training terciles; missing separate",
            missing=(
                "native valid-only summaries; scaled fallback-inclusive; "
                "first/last difference requires both finite"
            ),
            ties=(
                "average ranks; constant vectors undefined; all190 rank "
                "pairs skip genuine label ties"
            ),
        ),
        objectives=dict(
            H2="e² if abs(e)<=1 else2abs(e)-1; e=asinh(y/s)-zhat",
            W1="a=2 if abs(z)>trainq95absz else1; sum(a*e²)/sum(a) per session",
            E1=(
                "NEG y<-q95, POS y>q95, equality NORMAL; cNORMAL=1; "
                "ctail=min(4,sqrt(pNORMAL/max(pk,1e-12))); "
                "session-normalized CE"
            ),
            R1=(
                "equal_session(mean_origin_stock e² +0.5mean_origin "
                "mean_valid190 softplus(-sign(yi-yj)*(zhati-zhatj))); tau1"
            ),
        ),
        thresholds=(
            "linear unweighted stock-row q95; class prevalence "
            "equal-session/origin/stock; separate inner/refit prefixes"
        ),
        selector=dict(
            H2="original_TG20_MSE",
            W1="original_TG20_MSE",
            E1="normalized_training_class_weighted_CE",
            R1="original_TG20_MSE",
        ),
        d6g=dict(
            min_epochs=12,
            max_epochs=60,
            patience=10,
            relative_qualifying_improvement=0.001,
            boundary=(
                "inclusive >=0.1% as explicitly requested by P022; legacy "
                "uses strict >; record exact-equality case if encountered"
            ),
            refit="fresh same seed and new optimizer; exactly qualified selected epochs",
        ),
        architecture=dict(
            input=16,
            lookback=48,
            width=32,
            layers=1,
            head_dropout=0.1,
            recurrent_dropout=0,
            parameters_regression=6433,
            parameters_E1=6499,
        ),
        optimizer=dict(
            name="AdamW",
            lr=0.001,
            betas=[0.9, 0.999],
            eps=1e-8,
            matrix_decay=0.01,
            bias_decay=0,
            clip=1,
            sessions_per_batch=16,
        ),
        resource_plan=dict(
            cpu_threads=4,
            additional_storage_ceiling_bytes=1_000_000_000,
            total_storage_ceiling_bytes=10_000_000_000,
            peak_ram_budget_bytes=2_000_000_000,
            runtime_estimate_hours=[0.5, 6],
        ),
        evaluation=dict(
            roles=list(COUNTS),
            class_rule=(
                "argmax NEG/NORMAL/POS; top4 per20-stock origin; average precision step integral"
            ),
            reliability_bins=list(np.linspace(0, 1, 11)),
            ranking_score="pPOS-pNEG; ANY=pPOS+pNEG",
            tail_masks=(
                "ranked |y|/|n| top1/5%; unique-origin MAD bottom1/5%; "
                "both/only/neither; train .99/.95 max and sign-specific "
                "maxima"
            ),
            regression=(
                "originaly MSE/MAE/RMSE/dailyIC/top4/dispersion/ZERO "
                "decomposition; no fabricated E1yhat"
            ),
            attribution=(
                "final refit checkpoint dropoutOFF; historical online "
                "dropoutON separate; R1half-pair endpoints"
            ),
            event_cases=(
                "top5 contribution per AAPL/AMZN/TSLA/SBUX; R1pairs; E1rare misses/false positives"
            ),
            uncertainty=(
                "400 month blocks seed22042 with two-month sensitivity; no iid stock inference"
            ),
        ),
        permissions=dict(
            fit=False,
            live_approval_required=True,
            development_stage1=False,
            protected_numeric=False,
            new_download=False,
            trading=False,
            git_mutations=False,
            extra_runs=False,
        ),
        backlog=(
            "Original10+3 retained unchanged; exact named list requested "
            "from researcher; no replacement invented"
        ),
    )
    # Seal the entire scientific design before any feature/label association is inspected.
    write_json(out / "frozen_design.json", design)
    (out / "P022_FROZEN_EXPERIMENT_DESIGN.md").write_text(
        "# P022 frozen experiment design\n\nFour independent seed42 "
        "arms in fixed order H2 → W1 → E1 → R1. "
        "Ledger36→40/200 only after separate exact live approval. No authority granted here.\n\n"
        "The attached [complete specification](submitted_instruction.txt) is normative. "
        "[Machine design](frozen_design.json) fixes all probes, "
        "losses, thresholds, reductions, selection and diagnostics "
        "before Stage1.\n\n"
        "H2 uses2×Huber(delta1) in z; W1 uses normalized doubled "
        "training-tail weight; E1 is a three-class "
        "weighted-CE task; R1 adds0.5 times all-pair logistic ordering loss to T2. "
        "No combinations, threshold searches or seed123 fits. "
        "Regression selects originalTG20 validationMSE; "
        "E1 selects normalized class-weighted validationCE. "
        "D6g12–60epochs/patience10/fresh selected-epoch refit. "
        "P022 explicitly uses inclusive ≥0.1% improvement; legacy "
        "code uses strict > at exact equality only.\n\n"
        "Source/input/roles/16formulas remain P019B→P020. "
        "Conditional private-research rights, ex-post split units, "
        "share-volume limits, proxy/fallback quality and unverified "
        "publication/dividend facts persist. "
        "Protected2026 remains locked. Development row numerics are "
        "deferred until Stage7; only saved aggregate "
        "baseline metrics are checked at Stage0 as requested.\n\n"
        "Stage1 examines all16 channels, native/scaled latest, "
        "valid48mean and endpoint difference; "
        "M1/V1/Q2/B1 trajectories; training-only quintiles; three "
        "fixed eras; 400 month-block resamples "
        "seed22042 and adjacent two-month sensitivity. Undefined constant ranks remain missing. "
        "No learned diagnostic model and no proof of learnability. "
        "All NORMAL events are controls.\n\n"
        "Stage7 separates actual objective units, normalized "
        "weighting and pair allocations; all four roles "
        "remain distinct. E1 has class-prior and normal-only "
        "baselines, never a fabricated return forecast. "
        "Exact candles remain private. Stage8 is an additive "
        "existing-dashboard extension after four completed runs.\n\n"
        "Resource plan: CPU4,0.5–6hours,2GB peakRAM,≤1GB additional storage within10GB ceiling. "
        "No optimizer step or start reservation until the Stage2 "
        "proposal is validated and explicitly approved.\n"
    )
    baseline = study.diagnostic("metrics.csv")
    baseline = baseline.loc[baseline.arm.eq("T2") & baseline.partition.eq("development")]
    if (
        len(baseline) != 2
        or not baseline.rows.eq(3660).all()
        or not baseline.sessions.eq(109).all()
    ):
        raise ValueError("P022_BASELINE_POPULATIONS")
    baseline.to_csv(out / "saved_baseline_development_aggregates.csv", index=False)
    checks = []
    for split in ("inner_train", "inner_validation"):
        v = scoped_view(study, split, stage=0)
        positions = (0, len(v.source.rows) // 2, len(v.source.rows) - 1)
        a, b = v.origin_batch(positions), v.source.batch(positions)
        assert np.array_equal(a["x"], b["x"]) and np.array_equal(a["y"], b["y"])
        checks.append(
            dict(
                role=split, summary=v.summary(), batch_shape=list(a["x"].shape), source_parity=True
            )
        )
    with patch.object(Path, "read_text", side_effect=AssertionError("forbidden access")):
        for split in ("development", "confirmation", "2026", "test"):
            try:
                scoped_view(study, split, stage=1)
            except ValueError:
                pass
            else:
                raise AssertionError("role guard failed")
        try:
            dates("2026-01-01", "2026-03-31")
        except ValueError:
            pass
        else:
            raise AssertionError("date guard failed")
    models = {arm: model_for(arm) for arm in ARMS}
    assert len({state_hash(models[a]) for a in ("H2", "W1", "R1")}) == 1
    for a in ARMS:
        for key, value in models["H2"].lstm.state_dict().items():
            assert np.array_equal(value.numpy(), models[a].lstm.state_dict()[key].numpy())
    references = [
        ref(CONTRACT),
        ref(Path("UNRESOLVED_MARKET_DATA_ANOMALIES.md")),
        design["prior_pointer"],
        design["prior_journal"],
    ]
    references += study.plan["protected_refs"] + list(study.contract["files"].values())
    for seed in (42, 123):
        r = study.run_result(f"HF1M-LONG-TM0-T2-S{seed}-DEV1")
        references += list(r["artifacts"].values())
    for r in references:
        checked(r)
    write_json(out / "preserved_references.json", references)
    write_json(
        out / "stage_00_identity_design_gate.json",
        dict(
            status="PASS_FROZEN_DESIGN",
            at=now(),
            design_sha256=digest(out / "frozen_design.json"),
            checks=checks,
            protected_before_read=True,
            saved_dev_aggregates_only=True,
            p2_entries=len(deferred),
            ledger=36,
            new_starts=0,
            initialization={a: state_hash(m) for a, m in models.items()},
            baseline_sha256=digest(out / "saved_baseline_development_aggregates.csv"),
        ),
    )
    print("PASS_FROZEN_DESIGN", out, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--instruction", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.out, args.instruction)
