"""Seal a reviewable S4 proposal only after read-only gates; never grants fit permission."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .hf1m_action_audit import SYMBOLS, digest
from .hf1m_ft16_source import ORDER
from .hf20_horizon_authority import validate
from .hf20_ranking_continue_report import markdown
from .hf20_s4_authority import RUNS, execution_hash, resources
from .hf20_s4_closeout import closeout


def write(path: Path, value: dict) -> None:
    with path.open("x") as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write("\n")


def seal(out: Path, static: Path, tests: Path) -> None:
    audit = out / "opening_reaudit_v2"
    checks = {
        "historical": out / "HISTORICAL_PHASE_I_GATE.json",
        "zero_step": audit / "S4_ZERO_STEP_WORKFLOW_REHEARSAL.json",
        "supplement": out / "untrained_visual_preview_v1/SUPPLEMENTAL_VERIFICATION.json",
        "browser": out / "untrained_visual_preview_v1/S4_BROWSER_QA.json",
    }
    for name, p in checks.items():
        if json.loads(p.read_text())["status"] != "PASS":
            raise ValueError("S4_PREFLIGHT_NOT_PASS:" + name)
    rehearsal = json.loads(checks["zero_step"].read_text())
    if (
        [r["run_id"] for r in rehearsal["workflows"]] != list(RUNS)
        or rehearsal["optimizer_step_calls"]
        or rehearsal["neural_starts"]
    ):
        raise ValueError("S4_EIGHT_ZERO_STEP_REQUIRED")
    summary = json.loads(static.read_text())["summary"]
    if summary["errorCount"] or summary["warningCount"]:
        raise ValueError("S4_STATIC_HOLD")
    if "24 passed" not in tests.read_text() or "failed" in tests.read_text():
        raise ValueError("S4_TEST_HOLD")
    pointer = Path("configs/CURRENT_EXPERIMENT_REGISTRY.json")
    old = json.loads(pointer.read_text())
    journal = Path(old["real_journal"])
    rows = validate([json.loads(s) for s in journal.read_text().splitlines()])
    if rows[-1]["global_started_pairs"] != 106 or rows[-1]["status"] != "COMPLETED":
        raise ValueError("S4_PRIOR_LEDGER_NOT106_COMPLETE")
    (out / "prior_registry_pointer.json").write_bytes(pointer.read_bytes())
    counts = pd.read_csv(audit / "S4_FOLD_ROLE_SLOT_COUNTS.csv")
    caps = dict(task_bytes=2_500_000_000, project_bytes=15_000_000_000, ram_bytes=2_000_000_000)
    evidence = list(checks.values()) + [
        static,
        tests,
        journal,
        out / "prior_registry_pointer.json",
        out / "submitted_instruction.txt",
    ]
    evidence += [
        audit / name
        for name in [
            "S4_SOURCE_POLICY.json",
            "S4_0930_REAUDIT_DECISION.json",
            "S4_NUMERICAL_SOURCE_READS.csv",
            "S4_ORIGIN_SOURCE_ELIGIBILITY.parquet",
            "S4_GENUINE_ENDPOINT_AND_COMPONENTS.parquet",
            "S4_FOLD_ROLE_SLOT_COUNTS.csv",
            "S4_ARCHIVED_ALL16_TENSOR_IDENTITY.csv",
            "S4_ALL16_SCALAR_SOURCE_WITNESSES.csv",
        ]
    ]
    slots = ["09:30", "10:30", "11:30", "12:30", "13:30", "14:30", "15:30"]
    exits = [
        "13:30 same",
        "14:30 same",
        "15:30 same",
        "10:00 next",
        "11:00 next",
        "12:00 next",
        "13:00 next",
    ]
    card = dict(
        kind="PROPOSED_S4A_EXACT_EIGHT_STARTS_NOT_AUTHORITY",
        execution_sha256=execution_hash(),
        run_ids=RUNS,
        source_audit=str(audit),
        symbols=SYMBOLS,
        ledger_before=106,
        maximum_after=114,
        effective_ceiling=200,
        baseline_attempts=8,
        baseline_models=["N0", "N1", "N2", "P"],
        optional_LR="NOT_INCLUDED",
        prefix_recipes=8,
        resource_caps=caps,
        resources_now=resources(out),
        resource_scope="PROPOSED_S4_ONLY; prior S3 amendment not silently inherited",
        forecast_slots=["09:30", "10:30", "11:30", "12:30", "13:30", "14:30", "15:30"],
        normal_exits=[
            "13:30 same",
            "14:30 same",
            "15:30 same",
            "10:00 next",
            "11:00 next",
            "12:00 next",
            "13:00 next",
        ],
        target=dict(
            trading_minutes=240,
            clock="XNYS including closing stub, early closes/DST/holidays",
            issuance_lag_minutes=2,
            opening_reference=(
                "genuine first-minute OPEN; prior48 full-hour features; "
                "conditional publication proxy"
            ),
            endpoint="genuine end-minus-one-minute CLOSE; never shift missing endpoint",
            intermediate_missing_close="decomposition unavailable only",
            epsilon="max(1e-4,0.1*median training complete20 MAD)",
            T2R_scale="max(median absolute admitted training TG20,1e-6)",
        ),
        features=dict(
            order=ORDER,
            steps=48,
            channels=16,
            M2=(
                "same20/60 regular-origin-day mean/RMS;19/20,57/60,max2missing; "
                "matured strictly before each historical input session open;7 origin contexts; "
                "training floor/fallback/scaler pool equal1/7"
            ),
            common=(
                "unchanged P020 formulas, native/fallback source policies; train-"
                "prefix only; no time/stock IDs"
            ),
        ),
        neural=dict(
            seed=42,
            layers=1,
            hidden=32,
            dropout=0.1,
            optimizer="AdamW",
            lr=0.001,
            betas=[0.9, 0.999],
            eps=1e-8,
            matrix_weight_decay=0.01,
            bias_weight_decay=0,
            gradient_clip=1.0,
            batch_complete_sessions=16,
            min_epochs=12,
            max_epochs=60,
            patience=10,
            qualifying_absolute_IC_improvement=0.001,
            selection="strict validation daily Rank IC; raw/qualified best separately",
            refit="fresh same-seed empty optimizer, exactly selected epochs",
            cpu_intra=4,
            cpu_inter=1,
            loader_workers=0,
        ),
        chronology=dict(
            OOS_years=[2021, 2022, 2023, 2024],
            earliest_training="2011-04-01",
            inner="last6calendar months before OOS with actual purged support",
            purge=(
                "actual endpoint+2 maturity plus inherited conservative4h "
                "boundary and48step embargo"
            ),
            validation_min_sessions=50,
            min_origins_per_slot=25,
            defined_OOS_IC_min_fraction=0.99,
        ),
        gates=(
            "historical PASS; source/clock/input PASS; prior complete "
            "numerical+visual PASS before every next start; failures permanently "
            "charged, no retry; final8individual+collective browser and "
            "diagnostic verification"
        ),
        prohibited=[
            "2025 tuning",
            "protected2026 file reads or hashes",
            "extra starts",
            "other seeds",
            "S4B",
            "new downloads",
            "trading/backtesting",
            "Git publication",
        ],
        qualification=(
            "private-use rights, publication timing/action vintage and "
            "retrospective survivor cohort remain conditional; price-only "
            "outcomes, not executable P&L"
        ),
        planning_runtime_hours=[2, 10],
        evidence=[dict(path=str(p), sha256=digest(p)) for p in evidence],
    )
    write(out / "S4_FROZEN_EXPERIMENT_CARD.json", card)
    sha = digest(out / "S4_FROZEN_EXPERIMENT_CARD.json")
    complete = counts.loc[counts.slot.eq("ALL")]
    text = (
        "# S4-A consolidated live-fit approval request\n\n"
        "**Preparation complete. Eight neural starts remain NOT_RUN; ledger106/200.** "
        "The opening re-audit selects seven daily origins. No separate "
        "opening-price approval is requested.\n\n"
        f"Proposal SHA256 `{sha}`. Execution SHA256 `{card['execution_sha256']}`.\n\n"
        "The submitted instruction, Authorization boundary, states: “Before any real historical "
        "supervised fit or neural start, if the verified live repo requires one, submit one "
        "SHA-bound S4-A approval card”. The active CURRENT_EXPERIMENT_REGISTRY.json has "
        "`fit_permission=false` and `live_approval_required=true`; it binds completed S3 only. "
        "This is the one required consolidated fit checkpoint, not a new source-question gate.\n\n"
        "Exactly the following order; no retries, combinations or extra fits:\n\n"
        + "\n".join(f"{i + 1}. `{r}` — start{107 + i}." for i, r in enumerate(RUNS))
        + "\n\nBefore neural starts: eight phase-prefix recipes and exactly eight P profile fits "
        "(four folds × inner/refit); N0, N1=M1 and N2 need no model "
        "fitting. Optional LR is omitted. "
        "Baseline and neural models use exactly the same role/stock/origin keys.\n\n"
        "| Origin ET | Normal-session exit |\n|---|---|\n"
        + "\n".join(f"|{a}|{b}|" for a, b in zip(slots, exits))
        + "\n\n09:30 uses genuine minute OPEN, with completed09:30–09:31 bar and assumed09:32 "
        "issuance. Actual publication latency and opening-auction identity are unverified. "
        "It uses only previous48 completed full hours. 13:30 remains the exact normal-session "
        "endpoint. Other origins use the completed preceding-minute close. Calendar counting "
        "includes15:30–16:00; genuine final endpoints are mandatory, intermediate close is not.\n\n"
        "All16 FT formulas remain unchanged. Expanded M2 has7 slot-specific past-return contexts, "
        "each locked at its historical input session start with original20/60 support/maturity "
        "rules. The new S4 training recipe weights these contexts equally1/7 instead of the "
        "archived two-context1/2 pooling; archived formulas/recipes/results remain immutable.\n\n"
        "Hidden32/layer1/dropout0.1; AdamW0.001, betas0.9/0.999, epsilon1e-8, matrix decay0.01 "
        "/bias0; clip1;16whole-session batches; seed42; strict+0.001 validation IC,12–60epochs, "
        "patience10; fresh selected-epoch refit. Equal stocks/origin, origins/session and "
        "sessions/year; equal annual primary weight. Equal-category contrast is secondary.\n\n"
        + markdown(complete)
        + "\n\nMinimum50validation sessions and25observations per slot pass. Existing99%defined "
        "OOS IC coverage is retained as a report-support gate, not evidence of positive edge. "
        "A constant-score/undefined-IC result is preserved, never jittered or rescued.\n\n"
        "**Resource request:** explicitly apply2.5GB task /15GB project /2GB process RAM to "
        "S4;CPU4/1,0workers. S3-only resource permission is not silently reused. Planning2–10h; "
        "actual duration depends on selected epochs. Check limits before fits and during epochs; "
        "preserve artifacts and stop on breach.\n\n"
        "Evidence: [opening audit](opening_reaudit_v2/S4_0930_REAUDIT.md), "
        "[all role/slot populations](opening_reaudit_v2/S4_FOLD_ROLE_SLOT_COUNTS.csv), "
        "[zero-step eight-workflow "
        "receipt](opening_reaudit_v2/S4_ZERO_STEP_WORKFLOW_REHEARSAL.json), "
        "[historical report](HISTORICAL_S1_S2_RANKING_VISUAL_DIAGNOSTICS.md), "
        "[readiness](S4_CLOCK_AND_ELIGIBILITY_AUDIT.md). No new empirical result exists yet.\n"
    )
    (out / "S4_LIVE_FIT_APPROVAL_REQUEST.md").write_text(text)
    write(
        out / "S4_READINESS_PASS.json",
        dict(
            status="PASS",
            fit_authorized=False,
            proposal_sha256=sha,
            execution_sha256=card["execution_sha256"],
            checks={k: str(v) for k, v in checks.items()},
            static_summary=summary,
            ledger=106,
            neural_starts=0,
        ),
    )
    closeout(out)
    print(json.dumps(dict(proposal_sha256=sha, execution_sha256=card["execution_sha256"])))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--static", type=Path, required=True)
    p.add_argument("--tests", type=Path, required=True)
    args = p.parse_args()
    seal(args.out, args.static, args.tests)
