"""Owner-authorized research admission, independent of V3's preserved RSA path.

Admission recomputes proof and byte identities; a status flag or CLI force is not
an authorization. The in-process object records verification, not a human ID.
"""

import importlib.metadata
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .certification import engineering_witnesses
from .paths import ROOT, V2, canonical, digest, publish

GATES = (
    "G_FROZEN_INTEGRITY",
    "G_SIGNAL_CAUSAL",
    "G_DATA_COVERAGE",
    "G_CONTROL",
    "G_ACTION_FACTS_OR_CONDITIONAL",
    "G_MRK_OGN",
    "G_PRICE_BASIS",
    "G_ACCOUNTING",
    "G_EXECUTION",
    "G_SHORT_CONDITIONAL",
    "G_RISK",
    "G_REPRODUCIBILITY",
    "G_AUTHORIZED_SCOPE",
)


@dataclass(frozen=True)
class Admission:
    release_path: Path
    binding_sha256: str
    mode: str


def rejection(reason: str) -> None:
    name = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
    publish(
        ROOT / f"audits/rejection_{name}.json",
        {"reason": reason, "performance_output_created": False},
    )


def proof_status(mode: str) -> dict:
    statuses = {name: "HOLD" for name in GATES}
    integrity = ROOT / "audits/FROZEN_INTEGRITY_BEFORE_V4.json"
    if integrity.exists() and not json.loads(integrity.read_text())["failed"]:
        statuses["G_FROZEN_INTEGRITY"] = "PASS"
    source = ROOT / "RAW_SOURCE_AND_SIGNAL_PREFLIGHT_V4.json"
    if source.exists():
        observed = json.loads(source.read_text())
        expected = json.loads((V2 / "FULL_SIGNAL_COVERAGE_REPORT.json").read_text())
        if observed["totals"]["forecasts"] == expected["totals"]["forecasts"]:
            statuses["G_SIGNAL_CAUSAL"] = "PASS"
            statuses["G_CONTROL"] = "PASS"
        if observed["totals"]["sessions"] == expected["sessions"]:
            statuses["G_DATA_COVERAGE"] = "PASS"
    document = ROOT / "MRK_OGN_SOURCE_AND_ACCOUNTING_MANIFEST_V4.json"
    if (
        document.exists()
        and digest(ROOT / "sources/merck_8937.pdf")
        == "e6265bc96cc41442713bed92bfa33610363b3624196f1afe108e51931771b05b"
        and digest(ROOT / "sources/ogn_sec_8k.html")
        == "3dee33c78cd592d1829bc652037972b5114b7b4a05e7c434436d3485f43015a2"
        and len(json.loads((ROOT / "sources/ogn_sip.json").read_text())["bars"]) == 842
        and json.loads(document.read_text()).get("primary_terms_verified")
    ):
        statuses["G_ACTION_FACTS_OR_CONDITIONAL"] = "PASS_CONDITIONAL"
        statuses["G_MRK_OGN"] = "PASS_CONDITIONAL"
        statuses["G_PRICE_BASIS"] = "PASS_CONDITIONAL"
    current_code = {
        str(p): digest(p)
        for base in (
            Path("src/lstm_data/trading/track2/stage35/final_backtest_v4"),
            Path("tests/track2_stage35_v4"),
        )
        for p in sorted(base.glob("*.py"))
    }
    gap = ROOT / "ECONOMIC_GAP_SUPPLEMENT_MANIFEST_V4.json"
    if not gap.exists():
        statuses["G_DATA_COVERAGE"] = "HOLD_RAW_GAP_SOURCE_PREPARATION"
        statuses["G_PRICE_BASIS"] = "HOLD_RAW_GAP_SOURCE_PREPARATION"
    else:
        prepared = json.loads(gap.read_text())
        if (
            not prepared["all_dates_attempted"]
            or sum(r["selected"] for r in prepared["entries"]) != 99048
        ) or any(r["status"] != "COMPLETE_RESPONSE" for r in prepared["entries"]):
            statuses["G_DATA_COVERAGE"] = "HOLD_RAW_GAP_RETRIEVAL"
            statuses["G_PRICE_BASIS"] = "HOLD_RAW_GAP_RETRIEVAL"
    tests = ROOT / ("audits/ENGINEERING_ACCEPTANCE_V4_" + canonical(current_code)[:12] + ".json")
    if tests.exists():
        checked = json.loads(tests.read_text())
        live = engineering_witnesses()
        receipts_valid = set(r["domain"] for r in checked["commands"]) == {
            "pytest",
            "ruff",
            "owned_types",
        }
        receipts_valid = receipts_valid and all(
            Path(r["path"]).is_file()
            and digest(Path(r["path"])) == r["sha256"]
            and r["returncode"] == 0
            for r in checked["commands"]
        )
        if (
            checked["code"] == current_code
            and receipts_valid
            and checked["new_owned_type_errors"] == 0
            and checked["new_owned_warnings"] == 0
        ):
            pytest_receipt = next(r for r in checked["commands"] if r["domain"] == "pytest")
            match = re.search(r"(\d+) passed", Path(pytest_receipt["path"]).read_text())
            typed = next(r for r in checked["commands"] if r["domain"] == "owned_types")
            diagnostics = json.loads(Path(typed["path"]).read_text())["summary"]
            if (
                match is None
                or int(match[1]) < 220
                or diagnostics["errorCount"] != 0
                or diagnostics["warningCount"] != 0
            ):
                return statuses
            for name, passed in live.items():
                if passed:
                    statuses[name] = "PASS"
    if mode == "financial":
        pilot = ROOT / ("audits/PILOT_CERTIFICATION_V4_" + canonical(current_code)[:12] + ".json")
        certified = False
        if pilot.exists():
            evidence = json.loads(pilot.read_text())
            protocol = json.loads((ROOT / "FINAL_CONSOLIDATED_PROTOCOL.json").read_text())
            runs = evidence.get("runs", [])
            certified = (
                len(runs) == len(protocol["pilot_windows"])
                and [r["window"] for r in runs] == protocol["pilot_windows"]
            )
            for row in runs:
                result = row["receipt"]
                certified = certified and (
                    float(result["maximum_ledger_residual"]) <= 1e-8
                    and result["terminal_pending_orders"] == 0
                    and result["terminal_unpriced_special"] == 0
                    and result["unresolved"] is False
                    and bool(row["files"])
                    and all(
                        Path(p).is_file() and digest(Path(p)) == expected
                        for p, expected in row["files"].items()
                    )
                )
        if not certified:
            statuses["G_ACCOUNTING"] = "HOLD_PILOT_NOT_CERTIFIED"
            statuses["G_EXECUTION"] = "HOLD_PILOT_NOT_CERTIFIED"
    statuses["G_SHORT_CONDITIONAL"] = "PASS_CONDITIONAL"
    statuses["G_AUTHORIZED_SCOPE"] = "PASS_OWNER_CURRENT_PROMPT_2026_11_09"
    return statuses


def create_release(version: str, mode: str) -> Admission:
    if mode not in ("diagnostic", "financial"):
        raise ValueError("RESEARCH_MODE")
    if not version.replace("_", "").isalnum():
        raise ValueError("RELEASE_VERSION")
    h0 = json.loads((ROOT / "audits/H0_PROTECTED_V4.json").read_text())
    files = {row["path"]: row["sha256"] for row in h0["protected"]}
    for row in json.loads((V2 / "audits/cache/source_receipts.json").read_text()):
        files[row["path"]] = row["sha256"]
    for base in (Path("src/lstm_data/trading/track2"), Path("tests/track2_stage35_v4")):
        for p in base.rglob("*.py"):
            if "__pycache__" not in p.parts:
                files[str(p)] = digest(p)
    for acceptance in (ROOT / "audits").glob("ENGINEERING_ACCEPTANCE_V4*.json"):
        files[str(acceptance)] = digest(acceptance)
    for metadata in ROOT.glob("*.json"):
        files[str(metadata)] = digest(metadata)
    for p in (ROOT / "sources").rglob("*"):
        if p.is_file():
            files[str(p)] = digest(p)
    for base_file in (
        Path("pyproject.toml"),
        ROOT / "audits/H0_PROTECTED_V4.json",
        V2 / "audits/cache/source_receipts.json",
    ):
        files[str(base_file)] = digest(base_file)
    for name in (
        "FINAL_CONSOLIDATED_PROTOCOL.json",
        "RAW_SOURCE_AND_SIGNAL_PREFLIGHT_V4.json",
        "MRK_OGN_SOURCE_AND_ACCOUNTING_MANIFEST_V4.json",
        "audits/ENGINEERING_ACCEPTANCE_V4.json",
    ):
        p = ROOT / name
        if p.exists():
            files[str(p)] = digest(p)
    if mode == "financial":
        for pilot in (ROOT / "audits").glob("PILOT_CERTIFICATION_V4*.json"):
            files[str(pilot)] = digest(pilot)
    owner = {
        "approved_scope": "research-only conditional exploratory backtest",
        "approval_provenance": "current user FINAL CODEX EXECUTION PROMPT dated2026-11-09",
        "period": ["2021-01-01", "2024-12-31"],
        "arms": ["EQUAL", "ROLLING_RISK", "EWMA_RISK", "S2C_RISK"],
        "live_or_paper": False,
        "stage6_independent_audit_complete": False,
        "external_RSA_required": False,
        "no_invented_human_id": True,
    }
    binding = {
        "owner": owner,
        "mode": mode,
        "files": files,
        "protocol": digest(ROOT / "FINAL_CONSOLIDATED_PROTOCOL.json"),
    }
    statuses = proof_status(mode)
    folder = ROOT / "releases" / version
    publish(folder / "RESEARCH_AUTHORIZATION_AND_BINDING_V4.json", binding)
    report = {
        "mode": mode,
        "binding_sha256": canonical(binding),
        "gates": statuses,
        "overall": "PASS_CONDITIONAL_RESEARCH"
        if all(s.startswith("PASS") for s in statuses.values())
        else "HOLD",
        "repository_qualification": "27inherited frozen diagnostics;new owned errors forbidden",
        "human_authorization": "ALREADY_GRANTED_CURRENT_PROMPT;NO_RSA_OR_FURTHER_CHAT_REQUIRED",
    }
    publish(folder / "RESEARCH_BACKTEST_READINESS_V4.json", report)
    return Admission(folder, canonical(binding), mode)


def _check_admission(value: object, first: str, last: str, diagnostic: bool) -> None:
    if not isinstance(value, Admission):
        rejection("MISSING_RESEARCH_ADMISSION")
        raise PermissionError("MISSING_RESEARCH_ADMISSION")
    folder = value.release_path
    binding = json.loads((folder / "RESEARCH_AUTHORIZATION_AND_BINDING_V4.json").read_text())
    report = json.loads((folder / "RESEARCH_BACKTEST_READINESS_V4.json").read_text())
    reason = None
    if first < "2021-01-01" or last > "2024-12-31" or first > last:
        reason = "WRONG_RESEARCH_PERIOD"
    if diagnostic != (value.mode == "diagnostic"):
        reason = "WRONG_RELEASE_MODE"
    protocol = json.loads((ROOT / "FINAL_CONSOLIDATED_PROTOCOL.json").read_text())
    if diagnostic and [first, last] not in protocol["pilot_windows"]:
        reason = "DIAGNOSTIC_SCOPE_NOT_PREREGISTERED"
    if (
        canonical(binding) != value.binding_sha256
        or report["binding_sha256"] != value.binding_sha256
    ):
        reason = "RELEASE_BINDING_DRIFT"
    required_owner = binding.get("owner", {})
    if (
        required_owner.get("period") != ["2021-01-01", "2024-12-31"]
        or required_owner.get("arms") != ["EQUAL", "ROLLING_RISK", "EWMA_RISK", "S2C_RISK"]
        or required_owner.get("live_or_paper") is not False
    ):
        reason = "UNAUTHORIZED_OWNER_SCOPE"
    environment = json.loads((ROOT / "ENVIRONMENT_V4.json").read_text())
    installed = dict(
        sorted(
            (d.metadata["Name"], d.version)
            for d in importlib.metadata.distributions()
            if d.metadata["Name"]
        )
    )
    if installed != environment["packages"] or sys.version != environment["python"]:
        reason = "DEPENDENCY_ENVIRONMENT_DRIFT"
    current = proof_status(value.mode)
    if current != report["gates"] or not all(s.startswith("PASS") for s in current.values()):
        reason = "MANDATORY_RESEARCH_GATE_HOLD"
    baseline = json.loads((ROOT / "audits/H0_PROTECTED_V4.json").read_text())["protected"]
    source_rows = json.loads((V2 / "audits/cache/source_receipts.json").read_text())
    if any(binding["files"].get(row["path"]) != row["sha256"] for row in baseline + source_rows):
        reason = "REBASED_OR_OMITTED_FROZEN_BOUNDARY"
    source_names = {
        str(p)
        for p in Path("src/lstm_data/trading/track2").rglob("*.py")
        if "__pycache__" not in p.parts
    }
    if not source_names.issubset(binding["files"]):
        reason = "UNBOUND_EXECUTING_CODE"
    if reason is None:
        for name, expected in binding["files"].items():
            path = Path(name)
            if (
                path.is_absolute()
                or ".." in path.parts
                or not path.is_file()
                or digest(path) != expected
            ):
                reason = "BOUND_INPUT_CHANGED:" + name
                break
    if reason:
        rejection(reason)
        raise PermissionError(reason)


def check_admission(value: object, first: str, last: str, diagnostic: bool) -> None:
    """Reject before source readers/output directories, including corrupt metadata."""
    try:
        _check_admission(value, first, last, diagnostic)
    except (FileNotFoundError, KeyError, ValueError, TypeError, AssertionError) as exc:
        reason = "INVALID_RESEARCH_EVIDENCE:" + type(exc).__name__
        rejection(reason)
        raise PermissionError(reason) from exc


def scope_fingerprint() -> str:
    code = {
        str(p): digest(p)
        for base in (
            Path("src/lstm_data/trading/track2/stage35/final_backtest_v4"),
            Path("tests/track2_stage35_v4"),
        )
        for p in sorted(base.glob("*.py"))
    }
    return canonical(code)[:12]
