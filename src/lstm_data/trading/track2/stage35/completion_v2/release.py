"""Financial entry requires an independently anchored, signed exact release binding.

No keys are registered in this implementation. A reviewer must register an
independently held public-key fingerprint in a reviewed successor before release.
Editing report flags, environment variables or approver strings is insufficient.
This is an application gate, not a sandbox against arbitrary Python source edits.
"""

import hashlib
import json
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

GATES = (
    "G_PROVENANCE",
    "G_SIGNAL_CAUSAL",
    "G_ACCOUNTING",
    "G_EXECUTION",
    "G_PRICE_BASIS",
    "G_SHORT",
    "G_CONTROL",
    "G_RISK",
    "G_DATA_COVERAGE",
    "G_REPOSITORY",
    "G_HUMAN",
)
TRUSTED_REVIEWER_KEY_SHA256: frozenset[str] = frozenset()
REQUIRED_BINDINGS = (
    "protocol",
    "source_plan",
    "source_classes",
    "code_manifest",
    "checkpoints",
    "authorized_period",
    "conditional_shorting",
    "bar_open_assumption",
    "files",
)


def canonical(payload: dict) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


@dataclass(frozen=True)
class VerifiedRelease:
    binding_sha256: str
    approval_id: str
    approver_key_sha256: str


def verify_release(
    gate_path: Path, binding: dict, public_key: Path, signature: Path, openssl: str = "openssl"
) -> VerifiedRelease:
    gate = json.loads(gate_path.read_text())
    if any(gate.get("gates", {}).get(k, {}).get("status") != "PASS" for k in GATES):
        raise PermissionError("FINANCIAL_GATE_HOLD")
    if any(k not in binding for k in REQUIRED_BINDINGS) or gate.get("binding") != binding:
        raise PermissionError("EXACT_RELEASE_BINDING_REQUIRED")
    human = gate["gates"]["G_HUMAN"]
    if (
        not human.get("approval_id")
        or not human.get("approver")
        or human.get("actor_kind") != "EXTERNAL_HUMAN"
    ):
        raise PermissionError("INDEPENDENT_HUMAN_REQUIRED")
    at = datetime.fromisoformat(human.get("approved_at", ""))
    if at.tzinfo is None:
        raise PermissionError("AWARE_APPROVAL_REQUIRED")
    key_hash = hashlib.sha256(public_key.read_bytes()).hexdigest()
    if key_hash not in TRUSTED_REVIEWER_KEY_SHA256:
        raise PermissionError("REVIEWER_KEY_NOT_IN_INDEPENDENT_TRUST_ANCHOR")
    payload = {"binding": binding, "human": human, "gates": gate["gates"]}
    with tempfile.TemporaryDirectory(prefix="hf20_release_") as temp:
        message = Path(temp) / "release.json"
        message.write_bytes(canonical(payload))
        checked = subprocess.run(
            [
                openssl,
                "dgst",
                "-sha256",
                "-verify",
                str(public_key),
                "-signature",
                str(signature),
                str(message),
            ],
            capture_output=True,
            check=False,
        )
        if checked.returncode:
            raise PermissionError("INVALID_EXTERNAL_SIGNATURE")
    files = binding["files"]
    if not isinstance(files, dict) or not files:
        raise PermissionError("CONTENT_BOUND_FILE_INVENTORY_REQUIRED")
    current_source = {
        str(p) for p in Path("src/lstm_data/trading/track2/stage35/completion_v2").glob("*.py")
    }
    if not current_source.issubset(files):
        raise PermissionError("ALL_EXECUTING_MODULES_MUST_BE_BOUND")
    for name, digest in files.items():
        path = Path(name)
        if (
            path.is_absolute()
            or ".." in path.parts
            or hashlib.sha256(path.read_bytes()).hexdigest() != digest
        ):
            raise PermissionError("RELEASE_FILE_IDENTITY_CHANGED")
    return VerifiedRelease(
        hashlib.sha256(canonical(binding)).hexdigest(), human["approval_id"], key_hash
    )
