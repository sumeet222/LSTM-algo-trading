"""V3 signed release validation; no trusted human keys registered by this agent.

Code execution is not a security sandbox against arbitrary source edits. An
external reviewer must establish the trust anchor in a reviewed successor.
"""

import hashlib
import json
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

from ..completion_v2.release import VerifiedRelease, canonical

GATES = (
    "G_SIGNAL_CAUSAL",
    "G_CONTROL",
    "G_DATA_COVERAGE",
    "G_PROVENANCE",
    "G_RISK",
    "G_ACTION_FACTS",
    "G_ACTION_CONDITIONAL",
    "G_PRICE_BASIS",
    "G_ACCOUNTING",
    "G_EXECUTION",
    "G_SHORT",
    "G_REPOSITORY",
    "G_HUMAN",
)
TRUSTED_REVIEWER_KEYS: frozenset[str] = frozenset()
BINDINGS = (
    "checkpoints",
    "recipes_c3",
    "signals_controls",
    "action_inventory",
    "assumptions",
    "raw_tapes",
    "code_manifest",
    "protocol",
    "dependencies",
    "authorized_period",
    "conditional_shorting",
    "bar_open_assumption",
    "files",
)


def verify_v3(path: Path, binding: dict, key_path: Path, signature: Path) -> VerifiedRelease:
    gate = json.loads(path.read_text())
    human = gate.get("gates", {}).get("G_HUMAN", {})
    if human.get("status") != "PASS" or human.get("actor_kind") != "EXTERNAL_HUMAN":
        raise PermissionError("V3_INDEPENDENT_HUMAN_RELEASE_NOT_APPROVED")
    if any(not human.get(k) for k in ("approval_id", "approver", "approved_at")):
        raise PermissionError("V3_HUMAN_IDENTITY_REQUIRED")
    if datetime.fromisoformat(human["approved_at"]).tzinfo is None:
        raise PermissionError("V3_AWARE_APPROVAL_REQUIRED")
    for name in GATES:
        entry = gate.get("gates", {}).get(name, {})
        if entry.get("status") not in (
            "PASS",
            "ENGINEERING_PASS_CONDITIONAL",
            "CONDITIONAL_APPROVED_IMPLEMENTATION_SCENARIO",
        ):
            raise PermissionError("V3_REQUIRED_GATE_HOLD:" + name)
        if entry.get("status") != "PASS" and name not in human.get(
            "acknowledged_conditional_gates", []
        ):
            raise PermissionError("V3_EXPLICIT_CONDITIONAL_ACKNOWLEDGEMENT_REQUIRED:" + name)
    if gate.get("binding") != binding or any(k not in binding for k in BINDINGS):
        raise PermissionError("V3_EXACT_BINDING_REQUIRED")
    if binding["authorized_period"] != ["2021-01-01", "2024-12-31"]:
        raise PermissionError("V3_AUTHORIZED_PERIOD_MISMATCH")
    key_hash = hashlib.sha256(key_path.read_bytes()).hexdigest()
    if key_hash not in TRUSTED_REVIEWER_KEYS:
        raise PermissionError("V3_REVIEWER_NOT_IN_EXTERNAL_TRUST_ANCHOR")
    files = binding["files"]
    executing = {
        str(p)
        for p in Path("src/lstm_data/trading/track2").rglob("*.py")
        if "__pycache__" not in p.parts
    }
    if not isinstance(files, dict) or not executing.issubset(files):
        raise PermissionError("V3_TRANSITIVE_CODE_BINDING_REQUIRED")
    for name, expected in files.items():
        p = Path(name)
        if (
            p.is_absolute()
            or ".." in p.parts
            or hashlib.sha256(p.read_bytes()).hexdigest() != expected
        ):
            raise PermissionError("V3_BOUND_FILE_CHANGED:" + name)
    message = canonical({"binding": binding, "human": human, "gates": gate["gates"]})
    with tempfile.TemporaryDirectory(prefix="hf20-v3-review-") as folder:
        payload = Path(folder) / "signed_payload.json"
        payload.write_bytes(message)
        result = subprocess.run(
            [
                "openssl",
                "dgst",
                "-sha256",
                "-verify",
                str(key_path),
                "-signature",
                str(signature),
                str(payload),
            ],
            check=False,
            capture_output=True,
        )
    if result.returncode:
        raise PermissionError("V3_EXTERNAL_SIGNATURE_INVALID")
    return VerifiedRelease(
        hashlib.sha256(canonical(binding)).hexdigest(), human["approval_id"], key_hash
    )
