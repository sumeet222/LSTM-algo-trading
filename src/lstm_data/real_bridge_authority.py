"""Package005 review and fitting authorities; neither is a synthetic permission."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .real_batch_authority import BatchPairAuthority
    from .wf2_replication import WF2PairAuthority

from .config import digest, fingerprint
from .ft0_transforms import identity
from .pretraining_policy import CANDIDATE, PreparationAuthority, load_authority, verify_ref

PACKAGE = "TA-REAL-INPUT-BRIDGE-005"
RELEASE_SHA = "ffc2932434ad6ec966cb0046ab4a230d693bdf04acbbaddbf26f51cf0c6baad0"
INVENTORY_SHA = "fdaf23ec6bb8b640abd65bb95da5a859b3347f2152b62f89d0b64f51d54580be"
REVIEW_SEAL = object()
FIT_SEAL = object()
ACTIVE_SECONDS = 14400
HARD_SECONDS = 16200
CONTRACT = {
    "architecture": "TM0",
    "seed": 42,
    "stage": "WF1",
    "cutoff": "2023-06-30",
    "universe": list(CANDIDATE),
    "steps": 48,
    "channels": 16,
    "parameters": 6433,
    "width": 32,
    "layers": 1,
    "dropout": 0.1,
    "batch_sessions": 16,
    "optimizer": "AdamW",
    "betas": [0.9, 0.999],
    "optimizer_epsilon": 1e-8,
    "amsgrad": False,
    "lr": 0.001,
    "weight_decay_matrix": 0.01,
    "weight_decay_bias": 0.0,
    "clip": 1.0,
    "max_epochs": 60,
    "minimum_stop": 12,
    "patience": 10,
    "qualifying_multiplier": 0.999,
    "target_clipping": False,
    "device": "CPU_FLOAT32",
    "active_fit_seconds": ACTIVE_SECONDS,
    "hard_fit_seconds": HARD_SECONDS,
    "pair_limit": 1,
    "confirmation": False,
    "economic_claims": False,
    "mode": "ASSUMPTION_CONDITIONAL_CANDIDATE_PILOT_NOT_PRODUCTION",
}


def producer_snapshot(root: Path, producer: dict) -> tuple[dict, dict]:
    inv = verify_ref(root, producer["inventory"])
    rows = {r["path"]: r for r in csv.DictReader(inv.open())}
    pre = inv.parent / "preflight.json"
    if digest(pre) != rows[str(pre.relative_to(root))]["sha256"]:
        raise ValueError("SEALED_PRODUCER_PREFLIGHT_CHANGED")
    before = json.loads(pre.read_text())["protected"]
    modules = {
        p: r["sha256"]
        for p, r in before.items()
        if p.startswith("src/lstm_data/") and p.endswith(".py")
    }
    for name, row in rows.items():
        if name.startswith("src/lstm_data/") and name.endswith(".py"):
            modules[name] = row["sha256"]
    raw = {p: r["sha256"] for p, r in before.items() if p.startswith("data/raw/")}
    return modules, raw


def file_stamp(root: Path, name: str) -> tuple[str, int, int, int]:
    stat = (root / name).stat()
    return name, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns


def bridge_code(root: Path) -> str:
    """Bind the additive bridge, independently of the unchanged Package004 producer."""
    return identity(
        {
            str(p.relative_to(root)): digest(p)
            for p in sorted((root / "src/lstm_data").glob("real_bridge_*.py"))
        }
    )


@dataclass(frozen=True)
class BridgeReview:
    root: Path
    producer_ref: dict
    producer: dict
    manifest: dict
    preparation_authority: PreparationAuthority
    seal: object
    source_stamps: tuple[tuple[str, int, int, int], ...] = ()

    @property
    def binding(self) -> str:
        return fingerprint([PACKAGE, self.producer_ref, self.producer["manifest"]])

    def ensure(self) -> None:
        if type(self) is not BridgeReview or self.seal is not REVIEW_SEAL:
            raise ValueError("FORGED_BRIDGE_REVIEW_AUTHORITY")
        if json.loads(verify_ref(self.root, self.producer_ref).read_text()) != self.producer:
            raise ValueError("PRODUCER_BINDING_CHANGED")
        if (
            self.producer["manifest"]["sha256"] != RELEASE_SHA
            or self.producer["inventory"]["sha256"] != INVENTORY_SHA
        ):
            raise ValueError("EXACT_REVIEWED_PACKAGE004_RELEASE_REQUIRED")
        manifest = json.loads(verify_ref(self.root, self.producer["manifest"]).read_text())
        if (
            manifest != self.manifest
            or tuple(manifest["universe"]) != CANDIDATE
            or manifest.get("MODEL_FIT_FORBIDDEN") is not True
            or manifest.get("production_migrated") is not False
        ):
            raise ValueError("UNCHANGED_CANDIDATE_NAMESPACE_REQUIRED")
        # Reconstruct producer code from its sealed inventory and pre-edit snapshot.
        modules, raw = producer_snapshot(self.root, self.producer)
        if (
            modules != self.producer["modules"]
            or identity(modules) != manifest["code_sha256"]
            or any(digest(self.root / p) != sha for p, sha in modules.items())
        ):
            raise ValueError("PRODUCER_SOURCE_MATH_OR_ENGINE_CHANGED")
        if tuple(p for p, *_ in self.source_stamps) != tuple(sorted(raw)) or any(
            file_stamp(self.root, s[0]) != s for s in self.source_stamps
        ):
            raise ValueError("RAW_SOURCE_CHANGED_SINCE_VERIFIED_LOAD")
        verify_ref(self.root, self.producer["source_manifest"])
        verify_ref(self.root, self.producer["original_protocol"])
        verify_ref(self.root, manifest["canonical_store"])
        for ref in manifest["preparations"].values():
            verify_ref(self.root, ref)
        self.preparation_authority.ensure("FEATURE_TARGET_PREPARATION")


def load_review(root: Path, producer_ref: dict) -> BridgeReview:
    root = root.resolve()
    producer = json.loads(verify_ref(root, producer_ref).read_text())
    if (
        producer["inventory"]["sha256"] != INVENTORY_SHA
        or producer["manifest"]["sha256"] != RELEASE_SHA
    ):
        raise ValueError("EXACT_REVIEWED_PACKAGE004_RELEASE_REQUIRED")
    manifest = json.loads(verify_ref(root, producer["manifest"]).read_text())
    _, raw = producer_snapshot(root, producer)
    if any(digest(root / name) != sha for name, sha in raw.items()):
        raise ValueError("RAW_SOURCE_HASH_CHANGED")
    a = manifest["authority"]
    review = BridgeReview(
        root.resolve(),
        producer_ref,
        producer,
        manifest,
        load_authority(root, a["policy_ref"], a["approval_ref"]),
        REVIEW_SEAL,
        tuple(file_stamp(root, p) for p in sorted(raw)),
    )
    review.ensure()
    return review


@dataclass(frozen=True)
class TrainingAuthority:
    """Only the factory can issue a permit after every applicable bound gate passes."""

    review: BridgeReview
    binding_ref: dict
    binding: dict
    seal: object

    def ensure(self, activity: str, input_id: str) -> None:
        if self.seal is not FIT_SEAL or activity not in {
            "START_PAIR",
            "CALIBRATION",
            "REFIT",
            "DEVELOPMENT_EVALUATION",
            "CHECKPOINT",
        }:
            raise ValueError("EXACT_SINGLE_PAIR_FITTING_AUTHORITY_REQUIRED")
        self.review.ensure()
        current = json.loads(verify_ref(self.review.root, self.binding_ref).read_text())
        if current != self.binding or input_id != current["input_id"]:
            raise ValueError("TRAINING_INPUT_OR_AUTHORITY_CHANGED")
        validate_training_binding(self.review, current)


def validate_training_binding(review: BridgeReview, binding: dict) -> None:
    """Facts need evidence; a researcher's assumption or a PASS string is insufficient."""
    if set(binding) != {
        "proposal",
        "input_id",
        "researcher_decision",
        "local_use_rights",
        "shared_clock",
        "gates",
    }:
        raise ValueError("COMPLETE_ACTUAL_TRAINING_AUTHORITY_BINDING_REQUIRED")
    root = review.root
    proposal = json.loads(verify_ref(root, binding["proposal"]).read_text())
    if (
        proposal.get("contract") != CONTRACT
        or proposal.get("review_binding") != review.binding
        or proposal.get("code_sha256") != bridge_code(root)
        or proposal.get("input_id") != binding.get("input_id")
    ):
        raise ValueError("EXACT_DATA_CODE_POLICY_BOUND_RUN_REQUIRED")
    dataset = json.loads(verify_ref(root, proposal["dataset_input_binding"]).read_text())
    if (
        dataset.get("input_id") != binding["input_id"]
        or dataset.get("status") != "BRIDGE_READY"
        or dataset.get("code_sha256") != bridge_code(root)
        or dataset.get("review_binding") != review.binding
        or dataset.get("producer") != review.producer_ref
        or dataset.get("contract") != CONTRACT
        or dataset.get("shape") != [5, 48, 16]
    ):
        raise ValueError("INDEPENDENT_VERIFIED_BRIDGE_REQUIRED")
    decision = json.loads(verify_ref(root, binding["researcher_decision"]).read_text())
    if (
        decision.get("actor_type") != "human"
        or decision.get("owner") != "Track A researcher"
        or decision.get("status") != "APPROVED"
        or decision.get("proposal_sha256") != binding["proposal"]["sha256"]
        or decision.get("scope") != "ONE_CONDITIONAL_TM0_WF1_SEED42_PAIR_ONLY"
        or not decision.get("response_text")
        or not decision.get("response_provenance")
        or not decision.get("recorded_at")
        or decision.get("accept_retrospective_parameter_application") is not True
        or decision.get("approve_registry_transition") is not True
    ):
        raise ValueError("ACTUAL_EXACT_RESEARCHER_GO_REQUIRED")
    definition = json.loads(verify_ref(root, proposal["registry_definition"]).read_text())
    if (
        definition.get("real_pair_journal") != "reports/audit/track_a_real_pairs_v1.jsonl"
        or definition.get("activation_pointer") != "configs/CURRENT_EXPERIMENT_REGISTRY.json"
        or definition.get("overwrite_legacy_history") is not False
        or definition.get("ceiling") != 40
    ):
        raise ValueError("REVIEWED_GLOBAL_PAIR_ACCOUNTING_TRANSITION_REQUIRED")
    # Course substitution is not needed for stock-only TM0; the course experiment
    # remains required. Shared clock and contractual local use cannot be self-waived.
    for kind, owner in (
        ("local_use_rights", "source-rights reviewer"),
        ("shared_clock", "Track B collaborator"),
    ):
        fact = json.loads(verify_ref(root, binding[kind]).read_text())
        if (
            fact.get("status") != "EVIDENCED"
            or fact.get("actor_type") != "human"
            or fact.get("owner_role") != owner
            or not fact.get("recorded_at")
            or not fact.get("response_provenance")
            or not fact.get("evidence_refs")
            or fact.get("proposal_sha256") != binding["proposal"]["sha256"]
        ):
            raise ValueError("ACTUAL_RIGHTS_AND_SHARED_CLOCK_EVIDENCE_REQUIRED")
        for ref in fact["evidence_refs"]:
            verify_ref(root, ref)
    gates = json.loads(verify_ref(root, binding["gates"]).read_text())
    if (
        gates.get("input_id") != binding["input_id"]
        or gates.get("code_sha256") != bridge_code(root)
        or any(
            gates.get(k) != "PASS_APPLICABLE_CONDITIONAL_PILOT"
            for k in ("G0", "G1", "G2", "G3", "G5")
        )
        or gates.get("G4") != "COMPARATIVE_AND_ECONOMIC_CLAIMS_HELD"
        or gates.get("G6") != "POSTRUN_AUDIT_PLANNED"
        or not gates.get("evidence_refs")
    ):
        raise ValueError("APPLICABLE_SCIENTIFIC_GATES_REQUIRED")
    for ref in gates["evidence_refs"]:
        verify_ref(root, ref)


def load_training_authority(review: BridgeReview, binding_ref: dict) -> TrainingAuthority:
    if type(review) is not BridgeReview:
        raise ValueError("CONCRETE_VERIFIED_REVIEW_AUTHORITY_REQUIRED")
    review.ensure()
    binding = json.loads(verify_ref(review.root, binding_ref).read_text())
    validate_training_binding(review, binding)
    return TrainingAuthority(review, binding_ref, binding, FIT_SEAL)


def require_training(
    authority: TrainingAuthority | BatchPairAuthority | WF2PairAuthority,
    activity: str,
    input_id: str,
) -> None:
    """Single public admission boundary; duck-typed/subclass permissions cannot opt in."""
    from .real_batch_authority import BatchPairAuthority
    from .wf2_replication import WF2PairAuthority

    if type(authority) is BatchPairAuthority or type(authority) is WF2PairAuthority:
        authority.ensure(activity, input_id)
        return
    if type(authority) is not TrainingAuthority:
        raise ValueError("CONCRETE_REVIEWED_TRAINING_AUTHORITY_REQUIRED")
    authority.ensure(activity, input_id)
