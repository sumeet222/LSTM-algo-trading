"""Immutable V3 integrity checks and NOT_APPROVED financial review packet.

This command never runs inference, trades, a financial replay, or human signing.
"""

import argparse
import importlib.metadata
import json
import platform
from pathlib import Path

from .acquire import ROOT, write_once
from .inventory import digest
from .tapes import load_actions

V2 = Path("trading/track2/stage35/completion_v2")


def integrity(root: Path = ROOT) -> dict:
    h0 = json.loads((root / "audits/H0_PROVENANCE.json").read_text())
    failed = []
    for item in h0["protected"]:
        path = Path(item["path"])
        if (
            not path.exists()
            or digest(path) != item["sha256"]
            or path.stat().st_mtime_ns != item["mtime_ns"]
        ):
            failed.append(item["path"])
    sources = json.loads((V2 / "audits/cache/source_receipts.json").read_text())
    for item in sources:
        path = Path(item["path"])
        if digest(path) != item["sha256"] or path.stat().st_mtime_ns != item["mtime_ns"]:
            failed.append(item["path"])
    counts = json.loads((V2 / "FULL_SIGNAL_COVERAGE_REPORT.json").read_text())["totals"]
    if counts["forecasts"] != 131111 or counts["matched"] != 87557:
        failed.append("FROZEN_SIGNAL_TOTALS_CHANGED")
    result = {
        "protected_objects": len(h0["protected"]),
        "source_partitions": len(sources),
        "failed": failed,
        "status": "PASS" if not failed else "HOLD",
        "protected_sha256_and_mtime_unchanged": not failed,
        "signal_totals": counts,
        "new_model_forward_calls": 0,
        "historical_financial_backtest_run": False,
    }
    write_once(root / "audits/FINAL_INTEGRITY_V3.json", result)
    if failed:
        raise ValueError("FROZEN_INTEGRITY_HOLD")
    return result


def packet(root: Path = ROOT) -> None:
    integrity(root)
    owned = json.loads((root / "audits/FINAL_OWNED_TYPES.json").read_text())
    repo = json.loads((root / "audits/FINAL_REPOSITORY_TYPES.json").read_text())
    prior = json.loads((V2 / "audits/validation_release_v2/repository_types.json").read_text())

    def diagnostics(value: dict) -> list:
        return sorted(
            (d["file"], d["message"], json.dumps(d["range"], sort_keys=True))
            for d in value["generalDiagnostics"]
        )

    if (
        owned["summary"]["errorCount"]
        or owned["summary"]["warningCount"]
        or diagnostics(repo) != diagnostics(prior)
    ):
        raise ValueError("OWNED_OR_CHANGED_REPOSITORY_DIAGNOSTIC_HOLD")
    versions = {
        name: importlib.metadata.version(name)
        for name in (
            "numpy",
            "pandas",
            "pyarrow",
            "torch",
            "exchange-calendars",
            "requests",
            "python-dotenv",
            "ruff",
            "pyright",
        )
    }
    deps = {
        "python": platform.python_version(),
        "packages": versions,
        "dependency_changes": "NONE",
        "manifest": digest(Path("pyproject.toml")),
    }
    write_once(root / "DEPENDENCY_ENVIRONMENT_V3.json", deps)
    old_gate = json.loads((V2 / "BACKTEST_READINESS_GATE_V2.json").read_text())
    files = dict(old_gate["binding"]["files"])
    for base in (Path("src/lstm_data/trading/track2"), Path("tests/track2_stage35_completion_v3")):
        for path in sorted(base.rglob("*.py")):
            if "__pycache__" not in path.parts:
                files[str(path)] = digest(path)
    # Bind all execution inputs, current source/assumption inventories and evidence.
    excluded = {
        "BACKTEST_READINESS_GATE_V3.json",
        "stage35_completion_v3_manifest.json",
        "RELEASE_CODE_SOURCE_SCOPE_MANIFEST_V3.json",
    }
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name in excluded or "payloads" in path.parts:
            continue
        files[str(path)] = digest(path)
    for action in load_actions(root):
        for source in action.sources:
            key = source.source_id.split(":", 1)[-1]
            receipt = root / f"audits/{key}.receipt.json"
            if receipt.exists():
                payload = Path(json.loads(receipt.read_text())["payload_path"])
                files[str(payload)] = digest(payload)
    scope = {
        "version": "V3_RELEASE_CODE_AND_INPUT_SCOPE",
        "base_git": json.loads((root / "audits/H0_PROVENANCE.json").read_text())["head"],
        "files": files,
        "gate_self_exclusion": (
            "gate, scope self and final child manifest excluded to avoid cycles"
        ),
    }
    scope_path = root / "RELEASE_CODE_SOURCE_SCOPE_MANIFEST_V3.json"
    write_once(scope_path, scope)
    files[str(scope_path)] = digest(scope_path)
    binding = {
        "checkpoints": old_gate["binding"]["checkpoints"],
        "recipes_c3": digest(Path("trading/track2/stage012/original_bundles.json")),
        "signals_controls": {
            name: digest(V2 / name)
            for name in (
                "FULL_SIGNAL_COVERAGE_REPORT.json",
                "CLASSICAL_MATURED_CONTROLS_MANIFEST.json",
            )
        },
        "action_inventory": digest(root / "ACTION_PROVENANCE_V3.jsonl"),
        "assumptions": {
            name: digest(root / name)
            for name in (
                "ORDINARY_DIVIDEND_ASSUMPTIONS_V3.jsonl",
                "CURRENCY_UNIT_ASSUMPTIONS_V3.jsonl",
                "CONDITIONAL_POPULATIONS_V3.json",
                "STANDALONE_PROXY_SCHEDULE_V3.jsonl",
            )
        },
        "raw_tapes": {
            name: digest(root / name)
            for name in (
                "RAW_SHARE_SOURCE_COVERAGE_V3.json",
                "HISTORICAL_ACTION_AND_CARRY_TAPE_MANIFEST_V3.json",
            )
        },
        "code_manifest": digest(scope_path),
        "protocol": digest(root / "DIVIDEND_FALLBACK_POLICY_V3.json"),
        "dependencies": digest(root / "DEPENDENCY_ENVIRONMENT_V3.json"),
        "authorized_period": ["2021-01-01", "2024-12-31"],
        "conditional_shorting": "CONDITIONAL_ACADEMIC_SHORT_2PCT_ACT365;NOT_OBSERVED_LOCATES",
        "bar_open_assumption": "PRE_EVENT_SUBMISSION_EX_POST_RAW_OPEN_SETTLEMENT;NOT_EXCHANGE_FILL",
        "files": files,
    }
    gates: dict[str, dict[str, object]] = {
        name: {"status": "PASS", "evidence": "unchanged frozen source/signal/control integrity"}
        for name in ("G_SIGNAL_CAUSAL", "G_CONTROL", "G_DATA_COVERAGE", "G_PROVENANCE", "G_RISK")
    }
    gates.update(
        {
            "G_ACTION_FACTS": {
                "status": "HOLD",
                "issue": "V3-ACTION-001",
                "cash_records": 267,
                "verified_cash": 16,
                "single_provider_cash": 251,
                "unpriced_special_events": 1,
                "unknown_nonpayer_security_years": 8,
            },
            "G_ACTION_CONDITIONAL": {
                "status": "ENGINEERING_PASS_CONDITIONAL",
                "ordinary_date_amount_existence_imputations": 0,
                "date_only_availability_assumptions": 270,
                "USD_unit_assumptions": 251,
                "proxy_security_years": 8,
                "proxy_templates": 2922,
                "proxy_amounts_computed": False,
                "truth_not_upgraded": True,
            },
            "G_PRICE_BASIS": {
                "status": "HOLD",
                "raw_source_lineage_and_11_samples": "PASS",
                "issue": "MRK_OGN_CIL_VALUE_AND_SPECIAL_BASIS_UNRESOLVED",
            },
            "G_ACCOUNTING": {
                "status": "ENGINEERING_PASS_CONDITIONAL",
                "ordinary_bridge": "PASS_SYNTHETIC_BOOK_AND_ACTUAL_SOURCE_CLAIM_SHARE_WITNESS",
                "special_positions": "RETAINED_UNRESOLVED;NO_INVENTED_VALUE",
            },
            "G_EXECUTION": {
                "status": "ENGINEERING_PASS_CONDITIONAL",
                "evidence": "original V2 causal fill tests plus V3 due/carry/restart",
                "actual_historical_fills_run": False,
            },
            "G_SHORT": {
                "status": "CONDITIONAL_APPROVED_IMPLEMENTATION_SCENARIO",
                "baseline": ".02",
                "sensitivities": [".01", ".05"],
                "strict_locate": "NOT_CERTIFIED_NO_OBSERVED_DATA",
            },
            "G_REPOSITORY": {
                "status": "ENGINEERING_PASS_CONDITIONAL",
                "owned_errors": 0,
                "owned_warnings": 0,
                "inherited_errors": 27,
                "repository_status": "HOLD_T2_010_UNCHANGED_FROZEN_ERRORS",
            },
            "G_HUMAN": {
                "status": "NOT_APPROVED",
                "approval_id": None,
                "approver": None,
                "approved_at": None,
                "actor_kind": None,
                "acknowledged_conditional_gates": [],
                "trust_anchor": "EMPTY;NO_AGENT_KEY_GENERATED",
            },
        }
    )
    write_once(
        root / "BACKTEST_READINESS_GATE_V3.json",
        {
            "schema_version": 3,
            "overall": "HOLD",
            "verdict": "STAGE35_PARTIAL_EVIDENCED_SOURCE_OR_POLICY_BLOCKER",
            "engineering_scope": "CONDITIONAL_ORDINARY_ACTION_INTEGRATION_IMPLEMENTED",
            "historical_financial_backtest_run": False,
            "gates": gates,
            "binding": binding,
        },
    )
    inventory = {
        str(p): digest(p)
        for p in sorted(root.rglob("*"))
        if p.is_file() and p.name != "stage35_completion_v3_manifest.json"
    }
    inventory.update(
        {
            str(p): digest(p)
            for p in Path("src/lstm_data/trading/track2/stage35/completion_v3").glob("*.py")
        }
    )
    inventory.update(
        {str(p): digest(p) for p in Path("tests/track2_stage35_completion_v3").glob("*.py")}
    )
    write_once(
        root / "stage35_completion_v3_manifest.json",
        {
            "version": "V3_COMPLETION_CHILD",
            "parent_manifest_sha256": digest(V2 / "stage35_completion_manifest_v2.json"),
            "self_exclusion": "this manifest only;source payload caches are local inputs",
            "files": inventory,
            "historical_financial_backtest_run": False,
            "human_review": "NOT_APPROVED",
        },
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--integrity-only", action="store_true")
    args = parser.parse_args()
    integrity() if args.integrity_only else packet()
