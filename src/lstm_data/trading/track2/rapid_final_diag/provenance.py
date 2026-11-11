"""Fail-closed archive identity and immutable protocol receipts."""

import json
from pathlib import Path

from ..rapid_v1.paths import canonical, digest, publish
from ..rapid_v1.verification import preserve_check
from ..rapid_v3_dynamic.cli import verify_parents

ROOT = Path("trading/track2/rapid_final_diag_v1")
CODE = Path("src/lstm_data/trading/track2/rapid_final_diag")
TESTS = Path("tests/track2_rapid_final_diag")
V3 = Path("trading/track2/rapid_v3_dynamic")
FUNDED = V3 / "runs/rapid-v3-20261110-r1/funded_20261110T233807328833Z"


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def code_hashes() -> dict:
    return {str(p): digest(p) for folder in (CODE, TESTS) for p in sorted(folder.glob("*.py"))}


def inventory() -> dict:
    verify_parents()
    paths = set()
    for root in (
        "rapid_v1",
        "rapid_v2_diagnostics",
        "rapid_v3_dynamic",
        "rapid_r01_deep_dive",
        "rapid_exit_audit_v1",
    ):
        manifest_name = {
            "rapid_v1": "RAPID_CONTENT_MANIFEST_V1.json",
            "rapid_v2_diagnostics": "RAPID_V2_CONTENT_MANIFEST.json",
            "rapid_v3_dynamic": "V3_CONTENT_MANIFEST.json",
            "rapid_r01_deep_dive": "R01_ANALYSIS_MANIFEST.json",
            "rapid_exit_audit_v1": "ALL18_EXIT_ANALYSIS_MANIFEST.json",
        }[root]
        m = Path("trading/track2") / root / manifest_name
        if not m.exists():
            candidates = list((Path("trading/track2") / root).glob("*CONTENT_MANIFEST*"))
            if len(candidates) != 1:
                raise ValueError("MISSING_CANONICAL_MANIFEST " + str(m))
            m = candidates[0]
        paths.add(m)
        for name, expected in load(m)["files"].items():
            p = Path(name)
            sha = expected["sha256"] if isinstance(expected, dict) else expected
            if digest(p) != sha:
                raise ValueError("ARCHIVE_DRIFT " + name)
            paths.add(p)
    for name, expected in load(FUNDED / "FUNDED_OUTPUT_MANIFEST.json")["files"].items():
        p = FUNDED / name
        if digest(p) != expected:
            raise ValueError("FUNDED_DRIFT " + str(p))
        paths.add(p)
    paths.add(FUNDED / "FUNDED_OUTPUT_MANIFEST.json")
    for p in Path(".").glob("HF20*2026-11-10.md"):
        paths.add(p)
    return {
        str(p): {"sha256": digest(p), "mtime_ns": p.stat().st_mtime_ns, "bytes": p.stat().st_size}
        for p in sorted(paths)
    }


def before() -> None:
    ROOT.mkdir(exist_ok=True)
    publish(ROOT / "INPUTS_BEFORE.json", inventory())
    preserve_check(ROOT / "PROTECTED_BEFORE.json")


def verify() -> None:
    for name, old in load(ROOT / "INPUTS_BEFORE.json").items():
        p = Path(name)
        if digest(p) != old["sha256"] or p.stat().st_mtime_ns != old["mtime_ns"]:
            raise ValueError("INPUT_HASH_OR_MTIME_DRIFT " + name)


def seal(body: dict) -> None:
    verify()
    body.update(code_hashes=code_hashes(), input_seal_sha256=digest(ROOT / "INPUTS_BEFORE.json"))
    body["identity"] = canonical(body)
    publish(ROOT / "FINAL_DIAGNOSTIC_REGISTRY.json", body)
    publish(
        ROOT / "REGISTRY_SEAL.json", {"sha256": digest(ROOT / "FINAL_DIAGNOSTIC_REGISTRY.json")}
    )


def registry() -> dict:
    path = ROOT / "FINAL_DIAGNOSTIC_REGISTRY.json"
    body = load(path)
    identity = body.pop("identity")
    if (
        canonical(body) != identity
        or digest(path) != load(ROOT / "REGISTRY_SEAL.json")["sha256"]
        or body["code_hashes"] != code_hashes()
    ):
        raise ValueError("REGISTRY_OR_CODE_DRIFT")
    verify()
    return {**body, "identity": identity}
