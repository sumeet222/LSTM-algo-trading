"""Prepare and supervise Package012B; real fitting always needs a separate live receipt."""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from .config import atomic_new, digest, fingerprint, now, write_json
from .controlled_authority import load_stock_inputs
from .nb1_authority import (
    JOURNAL,
    QUEUE,
    activate,
    authority,
    code_binding,
    contract,
    journal_rows,
    load_plan,
    run_id,
)
from .nb1_inputs import B1, compressed_view, fit_recipe
from .p2_closure import load_deferred_work
from .pretraining_policy import verify_ref
from .real_batch_authority import atomic_replace_json
from .real_bridge_authority import load_review
from .visualization.controlled import Study
from .visualization.loaders import Catalog


def reference(path: Path) -> dict:
    return dict(path=str(path), sha256=digest(path))


def prepare(out: Path, instruction: Path, session_started: str | None = None) -> dict:
    root = Path.cwd()
    if not out.is_relative_to(Path("reports/data_audit")) or not out.name.startswith("ta012b_nb1_"):
        raise ValueError("NEW_PACKAGE012B_NAMESPACE_REQUIRED")
    out.mkdir(exist_ok=False)
    started = time.monotonic()
    started_at = pd.Timestamp(session_started) if session_started else pd.Timestamp.now(tz="UTC")
    entries = load_deferred_work(Path("configs/track_a_p2_engineering_handoff_v1.json"))
    pointer_path = Path("configs/CURRENT_EXPERIMENT_REGISTRY.json")
    atomic_new(out / "registry_pointer_v4_snapshot.json", pointer_path.read_bytes())
    pointer = json.loads(pointer_path.read_text())
    prior = json.loads(verify_ref(root, pointer["plan"]).read_text())
    review = load_review(root, prior["producer"])
    catalog = Catalog.discover(root)
    study = Study.discover(catalog)
    recipes, views, checks, controls, distributions = {}, {}, {}, {}, []
    stock_preparations = study.json("input_binding.json")["stock_preparations"]
    code = code_binding(root)
    protected = [
        reference(Path(f"reports/audit/track_a_real_pairs_v{i}.jsonl")) for i in range(1, 5)
    ]
    protected += [
        reference(Path("configs/CURRENT_PROTOCOL.json")),
        pointer["definition"],
        pointer["plan"],
        pointer["approval"],
    ]
    protected += [review.producer["manifest"], review.manifest["canonical_store"]]
    for fold in ("WF1", "WF2"):
        inputs = load_stock_inputs(review, {"stock_preparations": stock_preparations}, fold)
        recipes[fold] = {
            prefix: fit_recipe(inputs.candidates[fold + suffix], code)
            for prefix, suffix in (("inner", "_INNER_TRAIN"), ("refit", "_REFIT"))
        }
        views[fold], checks[fold], controls[fold] = {}, {}, {}
        for key in ("inner", "validation", "refit", fold):
            prefix = "inner" if key in {"inner", "validation"} else "refit"
            new, audit = compressed_view(inputs, key, recipes[fold][prefix])
            views[fold][key], checks[fold][key] = new.summary(), audit
            original = inputs.stock_view(key)
            if key == fold and (len(new.rows) != 232 or len(new.sessions) != 116):
                raise ValueError("NOT_MATCHED")
            # Unique component table, not 48-step repeated exposures; M2 origin contexts
            # repeat identical B1 values equally. Exact fitting key counts are in recipes.
            for label, values in (
                ("C0", original.values[:, B1].numpy()),
                ("N-B1", new.values[:, B1].numpy()),
            ):
                for symbol in (*contract(fold, 42)["universe"], "POOLED"):
                    indices = sorted(
                        {
                            index
                            for row in original.rows
                            for j, stock in enumerate(contract(fold, 42)["universe"])
                            if symbol == "POOLED" or stock == symbol
                            for index in row.indices[j]
                        }
                    )
                    sample = values[indices]
                    distributions.append(
                        dict(
                            fold=fold,
                            partition=key,
                            symbol=symbol,
                            arm=label,
                            population="unique indexed component rows (origin contexts retained)",
                            count=len(sample),
                            median=float(np.median(sample)),
                            abs_p99=float(np.quantile(np.abs(sample), 0.99)),
                            abs_max=float(np.abs(sample).max()),
                            above10=float((np.abs(sample) > 10).mean()),
                        )
                    )
        for seed in (42, 123):
            frame = study.panel(fold, seed, "C0", "Development")
            if len(frame) != 1160:
                raise ValueError("C0_EXACT_MASK_REQUIRED")
            path = out / f"C0_{fold}_seed{seed}_reference.csv"
            frame.to_csv(path, index=False)
            controls[fold][str(seed)] = reference(path)
            model = "TM0" if seed == 42 else "C0 [123]"
            for field in ("models", "checkpoints"):
                ref = catalog.config[field][fold][model]
                verify_ref(root, ref)
                protected.append(ref)
        protected.extend(stock_preparations[fold].values())
    # Independent x->q->z checks of native values, including the genuine 012A B1 tail.
    audit_ref = catalog.config["normalization_audit"]
    protected.append(audit_ref)
    verify_ref(root, audit_ref)
    oracle_path = Path(audit_ref["path"]).parent / "independent_feature_oracles.csv"
    oracle_ref = reference(oracle_path)
    oracle = pd.read_csv(verify_ref(root, oracle_ref), float_precision="round_trip")
    if not oracle.passed.all():
        raise ValueError("INDEPENDENT_SOURCE_ORACLE_FAILED")
    independent = []
    for fold in ("WF1", "WF2"):
        selected = oracle.loc[oracle.fold.eq(fold) & oracle.feature.eq("B1")]
        for prefix, recipe in recipes[fold].items():
            for row in selected.to_dict("records"):
                x = float(row["native"])
                q = math.asinh(x / recipe["s"])
                z = float(np.float32((q - recipe["c"]) / recipe["a"]))
                from .nb1_inputs import transform

                if z != float(transform(np.asarray([x]), recipe)[0]):
                    raise ValueError("INDEPENDENT_NB1_ARITHMETIC_FAILED")
                independent.append(
                    dict(
                        fold=fold,
                        prefix=prefix,
                        symbol=row["symbol"],
                        timestamp=row["timestamp"],
                        x=x,
                        q=q,
                        scaled=z,
                        recipe_id=recipe["recipe_id"],
                        passed=True,
                    )
                )
    protected.append(oracle_ref)
    write_json(out / "normalization_recipes.json", recipes)
    write_json(
        out / "feature_oracles.json",
        dict(
            views=checks,
            independent_012A_oracle=oracle_ref,
            independent_012A_rows=len(oracle),
            independent_nb1_examples=independent,
            confirmation_numeric_rows=0,
            deferred_register_entries=len(entries),
            actual_recipe_fallbacks="MAD_ONLY",
            separate_synthetic_constant_SD_edge="HOLD; no behavior change",
        ),
    )
    pd.DataFrame(distributions).to_csv(out / "b1_distribution_before_after.csv", index=False)
    prompt = instruction
    statement = (
        "The user approved a future 200-pair cumulative ceiling "
        "for Package 012B in the conversation"
    )
    amendment = dict(
        id="TA012B_BUDGET_40_TO_200_v1",
        old_ceiling=40,
        new_ceiling=200,
        opening_started=24,
        prospective_only=True,
        fit_permission=False,
        recorded_at=now(),
        owner="Track A researcher",
        actor_type="human",
        verbatim_statement=statement,
        source=(
            "Package012B submitted instruction section1.1; "
            "researcher-reported prior authorization, recorded now"
        ),
        submitted_instruction_sha256=digest(prompt),
        prior_pointer=reference(out / "registry_pointer_v4_snapshot.json"),
        immutable_prior_journal=protected[3],
        effective_journal=JOURNAL,
        scope="Cumulative ceiling only; exact four real pairs need separate live approval",
    )
    write_json(out / "budget_amendment_200.json", amendment)
    definition = Path("configs/track_a_candidate_experiment_registry_v5.json")
    write_json(
        definition,
        dict(
            schema=5,
            ceiling=200,
            opening_started=24,
            new_pair_limit=4,
            real_journal=JOURNAL,
            budget_amendment=reference(out / "budget_amendment_200.json"),
            previous_pointer=reference(out / "registry_pointer_v4_snapshot.json"),
            counts_failed_starts=True,
            production_migration=False,
        ),
    )
    protected += [
        reference(out / name) for name in ("normalization_recipes.json", "feature_oracles.json")
    ]
    plan = dict(
        id="TA012B_NB1_v1",
        code_sha256=code,
        producer=prior["producer"],
        stock_preparations=stock_preparations,
        protected_refs=protected,
        recipes=recipes,
        controls=controls,
        opening_started=24,
        ceiling=200,
        maximum_new_starts=4,
        maximum_wall_seconds=7200,
        report_reserve_seconds=900,
        package_started_at=started_at.isoformat(),
        deadline=(started_at + pd.Timedelta(minutes=120)).isoformat(),
        prior_pointer_snapshot=reference(out / "registry_pointer_v4_snapshot.json"),
        budget_amendment=reference(out / "budget_amendment_200.json"),
        registry_definition=reference(definition),
        confirmation_access=False,
        production_migration=False,
        assumptions=prior["assumptions"],
        formula=(
            "x=log(H/L); s=median(x>0 training keys); q=asinh(x/s); "
            "z=(q-median(q))/MAD(q); unchanged original fallback"
        ),
        primary="matched equal-day original TG0 MSE",
        secondary="daily Rank IC, origin/month, gradient G6, tails",
        intervals="exploratory post-screen five-session blocks; NOT_SELECTION_ADJUSTED",
        controls_retrained=False,
        no_retuning=True,
        runs=[],
    )
    for fold, seed in QUEUE:
        plan["runs"].append(
            dict(
                run_id=run_id(fold, seed),
                fold=fold,
                seed=seed,
                arm="N-B1",
                architecture="TM0",
                contract=contract(fold, seed),
                views=views[fold],
                input_id=fingerprint([views[fold], recipes[fold], stock_preparations[fold]]),
                recipe_ids={p: r["recipe_id"] for p, r in recipes[fold].items()},
            )
        )
    write_json(out / "experiment_design.json", plan)
    (out / "experiment_design.md").write_text(
        "# Package012B preregistered N-B1 experiment\n\n"
        + plan["formula"]
        + "\n\nFour ordered pairs: WF1/42, WF1/123, WF2/42, WF2/123. Existing C0 controls only. "
        "All other 15 float32 channels, TG0 and masks exact. Frozen D6g/AdamW/MSE/clip1/TM0. "
        "Primary matched equal-day MSE; secondary daily IC; "
        "five-session exploratory post-screen intervals. "
        "Hypothesis: compressing genuine rare B1 amplitude may improve stability/generalization; "
        "failure mode: compression removes useful amplitude distinctions. "
        "No result-led tuning or rescue. Retrospective candidate/actions, idealized clock, "
        "researcher-attested rights; hourly-close labels are not fills. "
        "No production activation, confirmation or trading; N-V12 remains untrained.\n\n"
        f"Proposal SHA `{digest(out / 'experiment_design.json')}`; code `{code}`.\n"
        f"Budget amendment `{digest(out / 'budget_amendment_200.json')}`; "
        "24→28/200 only after live approval.\n"
    )
    write_json(
        out / "preflight_runtime.json",
        dict(seconds=time.monotonic() - started, started_at=started_at.isoformat()),
    )
    activate(root, reference(out / "experiment_design.json"))
    return plan


def execute(out: Path, receipt: Path, pair: str | None = None) -> None:
    plan_ref, receipt_ref = reference(out / "experiment_design.json"), reference(receipt)
    plan, _ = load_plan(Path.cwd(), plan_ref)
    if pair:
        from .real_bridge_run import run_worker

        permit = authority(Path.cwd(), plan_ref, receipt_ref, pair)
        run_worker(permit, (out / pair).resolve())
        return
    runtime = []
    for row in plan["runs"]:
        remaining = (
            pd.Timestamp(plan["deadline"]) - pd.Timestamp.now(tz="UTC")
        ).total_seconds() - 900
        projection = max([240.0] + [v["seconds"] * 2 for v in runtime])
        if remaining < projection:
            write_json(
                out / "prefix_stop.json",
                dict(reason="REPORT_RESERVE", next=row["run_id"], remaining=remaining),
            )
            break
        if any(e["run_id"] == row["run_id"] for e in journal_rows(Path(JOURNAL))):
            raise ValueError("NB1_DUPLICATE_NO_RETRY")
        authority(Path.cwd(), plan_ref, receipt_ref, row["run_id"])
        started = time.monotonic()
        try:
            code = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    "-m",
                    "lstm_data.nb1_experiment",
                    "--out",
                    str(out),
                    "--approval",
                    str(receipt),
                    "--pair",
                    row["run_id"],
                ],
                timeout=remaining,
                check=False,
            ).returncode
        except subprocess.TimeoutExpired:
            code = 124
        runtime.append(
            dict(run_id=row["run_id"], seconds=time.monotonic() - started, return_code=code)
        )
        atomic_replace_json(out / "queue_actual_runtime.json", dict(pairs=runtime))
        print(json.dumps(runtime[-1]), flush=True)
        if code:
            rows = [e for e in journal_rows(Path(JOURNAL)) if e["run_id"] == row["run_id"]]
            if rows and rows[-1]["status"] not in {"FAILED", "COMPLETED"}:
                authority(Path.cwd(), plan_ref, receipt_ref, row["run_id"]).append(
                    "FAILED", dict(reason="SUPERVISOR_EXIT", code=code)
                )
            write_json(
                out / "prefix_stop.json",
                dict(reason="PAIR_FAILURE_NO_RETRY", run_id=row["run_id"], code=code),
            )
            break


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--instruction", type=Path)
    parser.add_argument("--session-started")
    parser.add_argument("--approval", type=Path)
    parser.add_argument("--pair")
    args = parser.parse_args()
    if args.prepare:
        if args.instruction is None:
            raise ValueError("SUBMITTED_INSTRUCTION_RECEIPT_REQUIRED")
        plan = prepare(args.out, args.instruction, args.session_started)
        print(
            json.dumps(
                dict(
                    status="AWAITING_LIVE_APPROVAL",
                    code=plan["code_sha256"],
                    proposal=reference(args.out / "experiment_design.json"),
                )
            )
        )
    elif args.approval:
        execute(args.out, args.approval, args.pair)
    else:
        raise ValueError("NB1_NO_APPROVAL_NO_FITTING")
    return 0


if __name__ == "__main__":
    from lstm_data.nb1_experiment import main as canonical_main

    raise SystemExit(canonical_main())
