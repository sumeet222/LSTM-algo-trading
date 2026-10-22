"""Seal the seed123 proposal and preservation inventory; no reservation or neural fit."""

from __future__ import annotations

import argparse
import json
import shutil
import time
from pathlib import Path

import pandas as pd

from lstm_data.config import digest, fingerprint, write_json
from lstm_data.hf20_postrun_diagnostics import discover
from lstm_data.hf20_replication_authority import IDS, JOURNAL, code_binding
from lstm_data.hf20_training_authority import POINTER, reference
from lstm_data.hf20_training_data import fit_scale
from lstm_data.p2_closure import load_deferred_work


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument(
        "--registry-definition",
        type=Path,
        default=Path("configs/track_a_candidate_experiment_registry_v7.json"),
    )
    args = parser.parse_args()
    tick = time.monotonic()
    out = args.out
    out.mkdir(parents=True, exist_ok=False)
    directory, base, contract, handoff, frame, views = discover(None)
    entries = load_deferred_work(Path("configs/track_a_p2_engineering_handoff_v1.json"))
    pointer = json.loads(POINTER.read_text())
    snapshot = out / "registry_pointer_v6_snapshot.json"
    snapshot.write_bytes(POINTER.read_bytes())
    previous = reference(Path(pointer["real_journal"]))
    definition = args.registry_definition
    if definition.exists() or JOURNAL.exists():
        raise ValueError("P017_SUCCESSOR_NAMESPACE_ALREADY_EXISTS")
    write_json(
        definition,
        dict(
            schema=7,
            opening_started=30,
            ceiling=200,
            new_pair_limit=2,
            real_journal=str(JOURNAL),
            previous_pointer=reference(snapshot),
            previous_journal=previous,
            budget_amendment=pointer["budget_amendment"],
            counts_failed_starts=True,
            approved_order=list(IDS),
            production_migration=False,
        ),
    )
    scales = {s: fit_scale(views[s], s) for s in ("inner_train", "refit")}
    if scales != base["scales"]:
        raise ValueError("P017_TRAIN_ONLY_SCALE_DIFFERS_FROM_SEED42")
    # Hash bytes only: protected raw/confirmation files are never numerically decoded here.
    old_preservation = directory / "preservation_before.json"
    paths = {Path(r["path"]) for r in json.loads(old_preservation.read_text())["files"]}
    paths |= {p for p in directory.rglob("*") if p.is_file()}
    diagnosis = Path("reports/data_audit/ta_hf20_deep_diagnostics_2026-10-16_185302")
    paths |= {p for p in diagnosis.rglob("*") if p.is_file()}
    paths |= {Path("src/lstm_data") / n for n in base["code"]}
    paths |= {Path(ref["path"]) for ref in contract["code"]}
    paths |= {Path(pointer["definition"]["path"]), Path(pointer["plan"]["path"])}
    paths.discard(
        POINTER
    )  # Exact before snapshot; only approved successor may replace this pointer.
    protected = [
        dict(path=str(p), bytes=p.stat().st_size, sha256=digest(p))
        for p in sorted(paths)
        if p.is_file()
    ]
    write_json(out / "preservation_before.json", dict(files=protected, byte_hash_only=True))
    scope = dict(
        base["scope"],
        seed=123,
        global_budget="30_TO_32_UNDER_200",
        changes="SEED_123_ONLY_PAIRED_C0_T2_REPLICATION",
    )
    current = pd.Timestamp.now(tz="UTC")
    plan = dict(base)
    plan.update(
        package="TA-HF20-P017-SEED123-PAIRED-REPLICATION-001",
        runs=list(IDS),
        scope=scope,
        baseline_plan=pointer["plan"],
        baseline_handoff=reference(directory / "visualization_handoff.json"),
        opening_started=30,
        previous_pointer=reference(snapshot),
        previous_journal=previous,
        registry_definition=reference(definition),
        code=code_binding(),
        code_sha256=fingerprint(code_binding()),
        protected_refs=[
            previous,
            pointer["budget_amendment"],
            reference(snapshot),
            base["input_contract"],
            reference(out / "preservation_before.json"),
        ],
        package_started_at=current.isoformat(),
        fit_deadline=(current + pd.Timedelta(hours=24)).isoformat(),
        package_deadline=(current + pd.Timedelta(hours=25)).isoformat(),
        maximum_package_seconds=90000,
        minimum_pair_reserve_seconds=900,
        historical_runtime_estimate_NOT_MEASURED_HF20=dict(
            seed42_worker_seconds=[109.091057, 29.926897],
            cautious_pair_projection_seconds=900,
            method="Fixed conservative allowance, no optimizer probe",
        ),
    )
    write_json(out / "experiment_design.json", plan)
    (out / "experiment_design.md").write_text(f"""# Package017 exact two-pair proposal

Proposal SHA256 `{digest(out / "experiment_design.json")}`;
execution SHA256 `{plan["code_sha256"]}`.
Exactly {IDS[0]}, then {IDS[1]}, seed123 for initialization, dropout and session permutations.
The only scientific change from the completed seed42 pair is seed. Original numerical engines
remain byte-identical. Shared TM0 16×48 / hidden32 / 6433 parameters, dropout0.10, AdamW .001,
weight decay .01 matrices / zero biases, cap1,16whole-session batches. D6g maximum60/minimum12/
patience10/strict original-TG20 validation MSE<.999×qualifying best; fresh same-seed model and
empty optimizer refit for exactly selected epochs. Separate sealed inner/refit recipes.
T2 s=max(pooled unique train median|TG20|,1e-6): {scales["inner_train"]["scale"]} inner,
{scales["refit"]["scale"]} refit; asinh objective and exactly one s*sinh inverse.

Input contract SHA256 `{plan["input_contract"]["sha256"]}`; FT1_HF20_HOURLY_NATIVE_V2 /
TG20_HF20_CROSS_SECTIONAL_V1. Exact ordered20, source, dates, clock and approved v2 masks:
872 inner /110 validation /998 refit /366 development origins. Same183 development sessions,
7320 stock forecasts. No intersecting away mismatches, no changed normalization, repairs or tuning.
Two append-only linked starts30→31→32/200, charged failures, no silent retry. Activation only
after a fresh attributable exact approval; previous grants are consumed. Authority expires
{plan["fit_deadline"]}. Fixed CPU float32/one thread. No new neural benchmark or optimizer probe.

Researcher-attested bounded local-use rights and conditional retrospective as-reported source,
idealized vendor clock/hourly-close proxies continue; no independent rights/action/PIT/publication
certification. No held-out numerical access (HF20 Jan7+; original five-stock confirmation also
locked), trading, source GET, extra seeds/architectures, history acquisition or Git operations.
Full read-only paired diagnostics and the existing explorer will show both seeds without selecting
a winner for promotion. Longer-history feasibility is a separate unexecuted proposal only.
""")
    write_json(
        out / "preflight.json",
        dict(
            status="TRAINING_HOLD_PENDING_LIVE_APPROVAL",
            previous_completed_starts=30,
            baseline_metrics=handoff["artifacts"]["matched_metrics.csv"],
            exact_masks={k: v.summary() for k, v in views.items()},
            exact_development_rows=len(frame),
            scales=scales,
            p2_hash_verified_entries=len(entries),
            protected_files=len(protected),
            source_requests=0,
            optimizer_steps=0,
            disk_free_bytes=shutil.disk_usage(".").free,
            seconds=time.monotonic() - tick,
        ),
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
