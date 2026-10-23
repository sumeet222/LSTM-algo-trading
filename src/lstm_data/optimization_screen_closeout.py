"""Hash-only P024 final preservation, bounded storage and complete-gate handoff."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .config import digest, fingerprint, now, write_json
from .hf1m_ft16_source import checked, ref
from .objective_screen_run import storage_bytes
from .optimization_screen_audit import verify_refs
from .optimization_screen_collective import OLD
from .optimization_screen_recovery_authority import RUNS, code_binding, require_complete_gate, rows
from .optimization_screen_recovery_authority import ensure as training_authority


def verify_lrlow_history(root: Path, reference: dict) -> dict:
    """Resolve a historical mutable code pointer through the sealed preapproval inventory.

    LRLOW's executed source is archived. Its intermediate type-hygiene pointer
    predates the empty-telemetry rehearsal adapter; that pointer describes history,
    not the current file. All numerical evidence and the executed archive still
    require their original hashes. Current code must match the preapproval seal.
    """
    path = checked(reference)
    gate = json.loads(path.read_text())
    require_complete_gate(path, "LRLOW")
    checked(gate["supplemental_code"])
    prior = json.loads((root / "verification_closeout_receipt.json").read_text())
    inventory_path = checked(prior["inventory"])
    inventory = pd.read_csv(inventory_path)
    old = gate["type_hygiene_successor"]
    matches = inventory.loc[inventory.path.eq(old["path"])]
    if len(matches) != 1:
        raise ValueError("P024_SEALED_PREAPPROVAL_PARSER_REQUIRED")
    record = matches.iloc[0]
    current = dict(path=str(record.path), bytes=int(record.bytes), sha256=str(record.sha256))
    checked(current)
    # Validate every original gate reference except the explicitly superseded
    # historical source pointer; it is retained verbatim in the resolution record.
    verify_refs({k: value for k, value in gate.items() if k != "type_hygiene_successor"}, {})
    return dict(
        status="PASS_HISTORICAL_CODE_VERSION_RESOLUTION",
        historical_gate=reference,
        executed_archive=gate["supplemental_code"],
        superseded_code_metadata=dict(
            original_path=old["path"],
            recorded_bytes=old["bytes"],
            recorded_sha256=old["sha256"],
            scope="HISTORICAL_INTERMEDIATE_VERSION",
        ),
        current_preapproved_code=current,
        inventory=ref(inventory_path),
        numerical_evidence_unchanged=True,
        optimizer_updates=0,
    )


def closeout(plan_path: Path, qa_path: Path, report: Path) -> None:
    """Create a new immutable closeout only after real stage9/10 and external QA receipts."""
    root = plan_path.parent
    plan = json.loads(plan_path.read_text())
    if plan["code"] != code_binding():
        raise ValueError("P024_APPROVED_CODE_CHANGED")
    journal = rows()
    if journal[-1]["global_started_pairs"] != 51 or journal[-1]["status"] != "COMPLETED":
        raise ValueError("P024_LEDGER51_COMPLETED_REQUIRED")
    if len([r for r in journal if r["status"] == "STARTED"]) != 5:
        raise ValueError("P024_EXACTLY_FIVE_RECOVERY_STARTS")
    for name, status in (
        ("stage_9_receipt.json", "PASS_COLLECTIVE_P024"),
        ("stage_10_receipt.json", "PASS_DASHBOARD_P024"),
    ):
        value = json.loads((root / name).read_text())
        if value["status"] != status:
            raise ValueError("P024_MISSING_FINAL_STAGE")
        verify_refs(value, {})
    qa = json.loads(qa_path.read_text())
    if qa["status"] != "PASS_FINAL_QA" or qa["protected_numeric_access"] is not False:
        raise ValueError("P024_FINAL_QA_REQUIRED")
    verify_refs(qa, {})
    types = json.loads(checked(qa["types"]).read_text())
    if types["summary"]["errorCount"] or types["summary"]["warningCount"]:
        raise ValueError("P024_STATIC_HOLD")
    if not report.is_file() or report.read_text().count("\n## ") != 17:
        raise ValueError("P024_17_SECTION_SESSION_REPORT_REQUIRED")
    # The failed start and completed LRLOW are immutable inputs, not reusable allocations.
    preservation = json.loads((root / "drop0_preservation_verified.json").read_text())
    for reference in preservation["artifacts"]:
        checked(reference)
    failed_journal = json.loads(checked(plan["previous_journal"]).read_text().splitlines()[-1])
    if failed_journal["status"] != "FAILED" or failed_journal["global_started_pairs"] != 46:
        raise ValueError("P024_FAILED46_NOT_PRESERVED")
    history_resolution = verify_lrlow_history(root, plan["completed_lrlow"])
    stage0 = json.loads(checked(plan["stage0"]).read_text())
    source_refs = stage0["source_hashes"]
    for reference in list(source_refs.values()) + plan["protected_refs"] + plan["baseline_refs"]:
        checked(reference)
    results = [OLD / "HF1M-LONG-TM0-LRLOW-S42-DEV1/run_result.json"] + [
        root / run / "run_result.json" for run in RUNS
    ]
    resources = []
    found: dict[str, dict] = {}
    for path in results:
        result = json.loads(path.read_text())
        verify_refs(result, found)
        if result["peak_rss_bytes"] > 2_000_000_000:
            raise ValueError("P024_RAM_LIMIT")
        resources.append(
            dict(
                run_id=result["run_id"],
                seconds=result["seconds"],
                peak_rss_bytes=result["peak_rss_bytes"],
                updates=result["calibration_steps"] + result["refit_steps"],
            )
        )
    # Terminal authority must reject every retry after completion, with no journal mutation.
    for run in RUNS:
        try:
            training_authority(plan_path, root / "live_approval.json", run)
        except ValueError as error:
            if str(error) != "P024_TERMINAL_NO_RETRY":
                raise
        else:
            raise ValueError("P024_COMPLETED_RETRY_NOT_REJECTED")
    total = storage_bytes([Path("data"), Path("artifacts"), Path("reports")])
    private = Path(plan["private_root"]).parent
    task_bytes = storage_bytes([root, private])
    if total > 10_000_000_000 or task_bytes > 2_000_000_000:
        raise ValueError("P024_STORAGE_LIMIT")
    paths = set()
    for directory in (root, private, OLD):
        paths.update(p for p in directory.rglob("*") if p.is_file())
    paths.update(Path("src/lstm_data").glob("optimization_screen*.py"))
    paths.update(Path("tests").glob("test_optimization_screen*.py"))
    paths.update(Path("configs").glob("*p024*.json"))
    paths.update(
        [
            Path("src/lstm_data/visualization/optimization_screen_ui.py"),
            Path("apps/track_a_dashboard.py"),
            Path("configs/track_a_visualization_v1.json"),
            Path("configs/CURRENT_EXPERIMENT_REGISTRY.json"),
            report,
            Path("reports/audit/track_a_real_pairs_v13_p024.jsonl"),
            Path("reports/audit/track_a_real_pairs_v14_p024_recovery.jsonl"),
        ]
    )
    inventory = []
    for path in sorted(paths):
        if path.name in ("artifact_inventory_final.csv", "final_closeout_receipt.json"):
            continue
        local = path.suffix in (".parquet", ".pt", ".npz") or "artifacts" in path.parts
        inventory.append(
            dict(
                path=str(path),
                bytes=path.stat().st_size,
                sha256=digest(path),
                type=path.suffix,
                purpose="private numerical evidence"
                if local
                else "implementation, compact report, config or receipt",
                git_intent="IGNORED_LOCAL_PRIVATE" if local else "REVIEW_COMPACT_ONLY",
            )
        )
    for reference in source_refs.values():
        inventory.append(
            dict(
                **reference,
                type=Path(reference["path"]).suffix,
                purpose="immutable upstream source/derived input",
                git_intent="IGNORED_LOCAL_PRIVATE",
            )
        )
    pd.DataFrame(inventory).drop_duplicates("path").to_csv(
        root / "artifact_inventory_final.csv", index=False
    )
    write_json(
        root / "final_closeout_receipt.json",
        dict(
            status="PASS_P024_COMPLETE",
            at=now(),
            ledger=51,
            effective_ceiling=200,
            successful_arms=6,
            charged_package_starts=7,
            recovery_starts=5,
            failed_start46_preserved=True,
            previous_journal=plan["previous_journal"],
            journal=ref(Path("reports/audit/track_a_real_pairs_v14_p024_recovery.jsonl")),
            proposal_sha256=digest(plan_path),
            execution_sha256=fingerprint(code_binding()),
            source_files=len(source_refs),
            source_bytes=sum(r["bytes"] for r in source_refs.values()),
            source_preserved=True,
            baseline_preserved=True,
            protected_numeric_access=False,
            resources=resources,
            total_data_artifacts_reports_bytes=total,
            recovery_namespace_and_private_parent_bytes=task_bytes,
            no_retries_allowed=True,
            qa=ref(qa_path),
            dashboard=ref(root / "stage_10_receipt.json"),
            collective=ref(root / "stage_9_receipt.json"),
            session_report=ref(report),
            inventory=ref(root / "artifact_inventory_final.csv"),
            historical_lrlow_code_resolution=history_resolution,
        ),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--qa", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    closeout(args.plan, args.qa, args.report)
