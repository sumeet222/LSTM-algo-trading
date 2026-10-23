"""Seal the reviewed P024 six-arm proposal without activating its journal or fitting."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict
from pathlib import Path

from .config import digest, fingerprint, now, write_json
from .hf1m_ft16_source import checked, ref
from .objective_screen_run import storage_bytes
from .optimization_screen import RUNS, VARIANTS, parameter_audit
from .optimization_screen_authority import JOURNAL, code_binding


def freeze(out: Path, tests: Path, types: Path) -> None:
    stage0 = json.loads((out / "stage_0_receipt.json").read_text())
    preflight = json.loads((out / "stage_1_preflight_final.json").read_text())
    diagnostic = json.loads(types.read_text())
    if (
        stage0["status"] != "PASS_STAGE0"
        or preflight["status"] != "PASS_ZERO_UPDATE_PREFLIGHT"
        or diagnostic["summary"]["errorCount"] != 0
        or diagnostic["summary"]["warningCount"] != 0
        or "passed" not in tests.read_text()
        or JOURNAL.exists()
    ):
        raise ValueError("P024_PREPARATION_GATE_OR_JOURNAL")
    for r in stage0["source_hashes"].values():
        checked(r)
    for r in stage0["baselines"] + stage0["protected_refs"]:
        checked(r)
    contract = json.loads(checked(stage0["identity"]).read_text())["input_contract"]
    identity = json.loads(checked(stage0["identity"]).read_text())
    audits = [parameter_audit(v) for v in VARIANTS]
    for v, a in zip(VARIANTS, audits, strict=True):
        expected = 21057 if v.arm == "H64" else 14881 if v.arm == "L2H32" else 6433
        if len(a["delta"]) != 1 or a["parameters"] != expected or a["interlayer_dropout"] != 0:
            raise ValueError("P024_SINGLE_FACTOR_ARCHITECTURE")
    write_json(out / "parameter_diff_audit.json", audits)
    (out / "focused_tests.txt").write_bytes(tests.read_bytes())
    (out / "static_check.json").write_bytes(types.read_bytes())
    design = dict(
        package="P024",
        variants=[asdict(v) for v in VARIANTS],
        runs=list(RUNS),
        reference="P021 T2 scalar signed asinh regression; matched seed42 except ES025/123",
        source=identity,
        opening_started=44,
        maximum_new_starts=6,
        ceiling=200,
        objective="mean_session(mean_admitted_origin(mean20((asinh(float32(y)/s_fit)-z_hat)^2)))",
        original_export_target="float64 frozen TG20; exactly-once s_fit*sinh(z_hat)",
        selection=dict(
            metric="original TG20 inner-validation MSE, historical float32 supervision",
            comparator="strict < (1-threshold)*last_qualified_best; no tolerance",
            minimum=12,
            maximum=60,
            patience=10,
            threshold=0.001,
            ES025_threshold=0.00025,
        ),
        early_stop_motivation=(
            "Verified seed123 historical selected1/raw12; threshold0.025% "
            "replay selects2/stops12. No counterfactual refit or expectation of"
            " epoch12 selection."
        ),
        optimizer=dict(
            name="AdamW",
            lr=0.001,
            betas=[0.9, 0.999],
            eps=1e-8,
            matrix_weight_decay=0.01,
            bias_weight_decay=0,
            amsgrad=False,
            clip_cap=1.0,
            sessions_per_batch=16,
        ),
        chronology=(
            "P020 frozen48-step availability embargo, genuine same-session4h "
            "endpoints; no2026 numerics"
        ),
        diagnostics=dict(
            roles=["inner_train", "inner_validation", "refit", "development"],
            near_zero_bands=[0.01, 0.05, 0.10],
            rank_tail_percent=[1, 5],
            range_fractions=[0.99, 0.95],
            rank_ties="origin_id then canonical stock ordinal, stable",
            small_mad="bottom1/5% unique origins expanded20stocks",
            event_threshold=(
                "training |original TG20| empirical0.95 quantile with "
                "method=higher; unchanged later roles"
            ),
            prediction_loss=(
                "fixed final checkpoint/dropoutOFF actual weighted z-MSE, distinct "
                "from online gradients"
            ),
            witnesses=(
                "five highest weighted refit losses per AAPL/AMZN/TSLA/SBUX plus "
                "BOTH_5 and MAD_ONLY_5 representatives"
            ),
            bootstrap=dict(
                replicates=400,
                seed=22042,
                blocks="whole calendar-month / two-month blocks of intact trading days",
                interval=[0.025, 0.975],
                interpretation=(
                    "exploratory, correlated stocks/windows and repeatedly "
                    "used109development sessions"
                ),
            ),
        ),
        acceptance=(
            "Mathematical/stage correctness gates; forecasting evidence is "
            "exploratory with no automatic winner or promotion. "
            "MSE/RankIC/tail-event assessment must use same-seed T2. Larger "
            "outputs/lower train loss/less clipping alone are not success."
        ),
        source_rights=(
            "Existing researcher-attested private local use only; no "
            "source/checkpoint redistribution or independent certification"
        ),
        backlog=[
            "original10+3 directions",
            "E1seed123 replication/calibration",
            "QR1seed123 replication",
            "QR1conditional quantile state dependence",
            "walk-forward",
            "permutation",
            "protected confirmation scientific holds",
        ],
        resources=dict(
            cpu_threads=4,
            interop_threads=1,
            planning_hours="0.5–6",
            peak_ram_bytes=2_000_000_000,
            additional_storage_bytes=2_000_000_000,
            total_storage_ceiling_bytes=10_000_000_000,
        ),
        failure_policy=(
            "Failure consumes its start; stop before next arm; no "
            "restart/refund/extra fit. Changed-code empirical continuation "
            "requires new live authorization."
        ),
        downstream=(
            "After each fit: immediate scientific diagnostics; after all six "
            "PASS: collective comparisons and additive existing-dashboard "
            "integration; no training in stages9–11"
        ),
    )
    write_json(out / "scientific_design.json", design)
    source_names = sorted(Path("src/lstm_data").glob("optimization_screen*.py"))
    diff = []
    for path in source_names + [Path("tests/test_optimization_screen.py")]:
        r = subprocess.run(
            ["git", "diff", "--no-index", "--", "/dev/null", str(path)],
            capture_output=True,
            text=True,
            check=False,
        )
        if r.returncode not in (0, 1):
            raise ValueError("P024_SOURCE_DIFF_FAILED")
        diff.append(r.stdout)
    (out / "implementation_source.patch").write_text("\n".join(diff))
    stage1 = dict(
        status="PASS_STAGE1_PREPARED",
        optimizer_updates=0,
        model_starts=0,
        ledger=44,
        preflight=ref(out / "stage_1_preflight_final.json"),
        tests=ref(out / "focused_tests.txt"),
        types=ref(out / "static_check.json"),
        parameter_audit=ref(out / "parameter_diff_audit.json"),
        source_diff=ref(out / "implementation_source.patch"),
        selector_interpretation=ref(out / "stage_0_review_correction.md"),
    )
    write_json(out / "stage_1_receipt.json", stage1)
    plan = dict(
        created=now(),
        package="P024",
        runs=list(RUNS),
        variants=[asdict(v) for v in VARIANTS],
        opening_started=44,
        maximum_new_starts=6,
        ceiling=200,
        code=code_binding(),
        execution_sha256=fingerprint(code_binding()),
        input_contract=contract,
        source_revision=identity["revision"],
        stage0=ref(out / "stage_0_receipt.json"),
        stage1=ref(out / "stage_1_receipt.json"),
        frozen_design=ref(out / "scientific_design.json"),
        protected_refs=stage0["protected_refs"] + stage0["protected_hourly_refs"],
        baseline_refs=stage0["baselines"],
        views=stage0["views"],
        previous_journal=stage0["previous_journal"],
        previous_pointer=stage0["previous_pointer"],
        private_root=str(Path("artifacts/hf20_hf1m_long_v1") / out.name / "trained_runs"),
        registry_definition="configs/track_a_candidate_experiment_registry_v13_p024.json",
        requires_separate_live_approval=True,
        fit_permission=False,
        protected_numeric_access=False,
        resources=design["resources"],
        opening_storage_bytes=storage_bytes([Path("data"), Path("artifacts"), Path("reports")]),
    )
    write_json(out / "experiment_design.json", plan)
    write_json(
        out / "proposed_registry_v13_NOT_ACTIVATED.json",
        dict(
            schema_version=13,
            package="P024",
            runs=list(RUNS),
            journal=str(JOURNAL),
            opening_started=44,
            maximum_started=50,
            effective_ceiling=200,
            plan=ref(out / "experiment_design.json"),
            activation_authorized=False,
        ),
    )
    md = [
        "# P024 frozen experiment design — PREPARED_NOT_TRAINED\n\n",
        (
            "Ledger **44/200**, zero new starts or optimizer updates. Six "
            "proposed runs in this exact order:\n\n"
        ),
        "|Start|Run|Controlled change|Parameters|\n|---|---|---|---|\n",
    ]
    for i, (v, a) in enumerate(zip(VARIANTS, audits, strict=True), 45):
        md.append(f"|{i}|`{RUNS[i - 45]}`|`{a['delta']}`|{a['parameters']}|\n")
    md.extend(
        [
            (
                "\nES025 compares primarily with saved T2/123; all other arms with "
                "T2/42. Verified seed1230.025% replay selects **epoch2**, stops12; "
                "raw minimum12 does not imply qualification against epoch2. This "
                "corrects the initial stage0 narrative; numeric tables were always "
                "correct.\n\n"
            ),
            (
                "Reuse unchanged P021 T2 epoch/export computation, SharedLSTM "
                "encoder, weighting, transforms, sampler and clipping. Capacity "
                "variants change only LSTM dimensions. Observational hooks record "
                "original/clipped per-module norms and parameter updates without "
                "changing gradients, RNG or AdamW. Fresh same-seed refit and "
                "optimizer after calibration; strict historical comparator "
                "preserved.\n\n"
            ),
            (
                "Risk: weak information may persist; six correlated single-seed "
                "exploratory screens on reused development data cannot certify "
                "alpha. Conditional source/clock/rights and quality limitations "
                "persist. H64/depth increase compute/overfit risk. More "
                "dispersion/lower training loss/less clipping is not success. No "
                "automatic promotion.\n\n"
            ),
            (
                "Frozen math/thresholds, bootstrap400/seed22042, tails, witnesses, "
                "source boundaries, backlog and exact resources are in "
                "`scientific_design.json`. Every arm must pass its complete "
                "immediate gate before the next start. Dashboard/collective stages "
                "remain pending until six genuine completed fits. No held-out "
                "numerics, new data, extra seeds, combinations, retries, trading or"
                " Git publication. CPU4; planning0.5–6h; RAM≤2GB; additional "
                "storage≤2GB and total local task-data/artifact/report "
                "storage≤10GB.\n\n"
            ),
            f"Proposal SHA256: `{digest(out / 'experiment_design.json')}`\n\n"
            f"Execution SHA256: `{plan['execution_sha256']}`\n\n",
            (
                "Implementation diff: `implementation_source.patch`. Independent "
                "parameter/groups: `parameter_diff_audit.json`. Final zero-update "
                "full-population export/reload proof: "
                "`stage_1_preflight_final.json`. Tests/static check and immutable "
                "stage receipts are bound by the proposal. Proposed successor is "
                "not activated.\n\n"
            ),
            (
                "Package024 Stage2 explicitly requires separate live human approval"
                " before any start. Preserve failed historical starts. Approval "
                "must name the exact six runs, proposal and execution hashes.\n"
            ),
        ]
    )
    (out / "P024_EXPERIMENT_DESIGN_FROZEN.md").write_text("".join(md))
    (out / "stage_1_review.md").write_text(
        (
            "# Stage1 — PASS, prepared only\n\nSingle-factor architecture/groups,"
            " strict selector cases, transforms/weighting, source barriers, "
            "fresh-refit identity, zero-update gradients/full-population "
            "checkpoint exports and immutable14receipt progress regression "
            "pass. See frozen design and receipts. No starts, no "
            "journal/pointer activation, no six-way scientific result or "
            "P024dashboard completion claim.\n"
        )
    )
    write_json(
        out / "stage_2_receipt.json",
        dict(
            status="PREPARED_NOT_TRAINED",
            live_approval_received=False,
            ledger=44,
            new_starts=0,
            optimizer_updates=0,
            proposal=ref(out / "experiment_design.json"),
            execution_sha256=plan["execution_sha256"],
            next="Separate live approval as explicitly required by Package024 Stage2",
        ),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--tests", type=Path, required=True)
    parser.add_argument("--types", type=Path, required=True)
    args = parser.parse_args()
    freeze(args.out, args.tests, args.types)
