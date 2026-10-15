"""Three explicit candidate pair grants and a linked append-only registry v2."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .config import atomic_new, digest, fingerprint
from .ft0_transforms import identity
from .pretraining_policy import verify_ref
from .real_batch_data import BatchInputs, load_batch_inputs
from .real_bridge_authority import CONTRACT, BridgeReview, load_review

QUEUE = ("MC0", "MC1", "E5")
SHAPES = {"MC0": (21, 7073), "MC1": (21, 7169), "E5": (23, 7329)}
SEAL = object()
JOURNAL_V2 = "reports/audit/track_a_real_pairs_v2.jsonl"
TRANSITIONS = {
    "STARTED": {"CALIBRATED", "FAILED"},
    "CALIBRATED": {"REFITTING", "FAILED"},
    "REFITTING": {"COMPLETED", "FAILED"},
    "COMPLETED": set(),
    "FAILED": set(),
}


def pair_contract(architecture: str) -> dict:
    if architecture not in QUEUE:
        raise ValueError("EXACT_MC0_MC1_E5_QUEUE_REQUIRED")
    channels, parameters = SHAPES[architecture]
    return {
        **CONTRACT,
        "architecture": architecture,
        "channels": channels,
        "parameters": parameters,
    }


def batch_code(root: Path) -> str:
    names = (
        "real_bridge_authority.py",
        "real_bridge_run.py",
        "real_bridge_data.py",
        "real_batch_data.py",
        "real_batch_authority.py",
        "real_multimodel_batch.py",
        "neural_health.py",
        "pilot_postrun.py",
        "real_batch_baseline.py",
    )
    return identity({name: digest(root / "src/lstm_data" / name) for name in names})


def load_plan(root: Path, plan_ref: dict) -> tuple[dict, BridgeReview]:
    plan = json.loads(verify_ref(root, plan_ref).read_text())
    if (
        plan.get("code_sha256") != batch_code(root)
        or [r["architecture"] for r in plan.get("runs", [])] != list(QUEUE)
        or any(r["contract"] != pair_contract(r["architecture"]) for r in plan["runs"])
        or plan.get("maximum_wall_seconds") != 7200
        or plan.get("report_reserve_seconds") != 900
        or plan.get("production_migration") is not False
        or plan.get("confirmation_access") is not False
    ):
        raise ValueError("EXACT_BOUND_BATCH_PLAN_REQUIRED")
    for name in (
        "dataset",
        "market",
        "input_binding",
        "registry_definition",
        "prior_real_journal",
        "prior_pointer_snapshot",
        "original_protocol",
        "tm0_result",
        "baseline_snapshot",
    ):
        verify_ref(root, plan[name])
    review = load_review(root, plan["producer"])
    return plan, review


def approval_scope(plan_ref: dict, approval: dict) -> tuple[str, ...]:
    selected = approval.get("approved_runs", [])
    if (
        approval.get("actor_type") != "human"
        or approval.get("owner") != "Track A researcher"
        or approval.get("status") != "APPROVED"
        or not approval.get("response_text")
        or not approval.get("response_provenance")
        or not approval.get("recorded_at")
        or approval.get("plan_sha256") != plan_ref["sha256"]
        or not selected
        or len(set(selected)) != len(selected)
        or tuple(selected) != tuple(a for a in QUEUE if a in selected)
        or approval.get("extend_researcher_attestation_to_named_batch") is not True
        or approval.get("accept_qualified_spy_fitting") is not True
        or approval.get("accept_existing_engineering_for_named_batch") is not True
        or approval.get("approve_linked_registry_v2") is not True
        or approval.get("maximum_wall_seconds") != 7200
    ):
        raise ValueError("ACTUAL_EXACT_BATCH_AND_POLICY_APPROVAL_REQUIRED")
    return tuple(selected)


def journal_rows_v2(path: Path) -> list[dict]:
    raw = path.read_bytes() if path.exists() else b""
    if raw and not raw.endswith(b"\n"):
        raise ValueError("TRUNCATED_V2_JOURNAL")
    rows = [json.loads(x) for x in raw.splitlines()]
    state = {}
    active = None
    for i, row in enumerate(rows):
        key, status = row["run_id"], row["status"]
        if (
            row.get("sequence") != i + 1
            or row.get("previous") != fingerprint(rows[:i])
            or row.get("contract") != pair_contract(row["architecture"])
        ):
            raise ValueError("V2_JOURNAL_CHAIN_OR_CONTRACT_CHANGED")
        previous = state.get(key)
        if previous is None:
            if status != "STARTED" or active is not None:
                raise ValueError("SERIAL_UNIQUE_PAIR_START_REQUIRED")
            active = key
        elif status not in TRANSITIONS[previous] or active != key:
            raise ValueError("MONOTONIC_V2_PAIR_TRANSITION_REQUIRED")
        state[key] = status
        if status in {"COMPLETED", "FAILED"}:
            active = None
    if sum(r["status"] == "STARTED" for r in rows) > 3:
        raise ValueError("THREE_NEW_PAIRS_ONLY")
    return rows


def atomic_replace_json(path: Path, value: dict) -> None:
    """Authorized pointer transition; retain predecessor snapshot/hash separately."""
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=".registry-")
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write((json.dumps(value, indent=2, sort_keys=True) + "\n").encode())
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if Path(name).exists():
            Path(name).unlink()


@dataclass(frozen=True)
class BatchPairAuthority:
    review: BridgeReview
    plan_ref: dict
    plan: dict
    approval_ref: dict
    approval: dict
    architecture: str
    seal: object
    cache: dict = field(default_factory=dict, compare=False)

    @property
    def contract(self) -> dict:
        return pair_contract(self.architecture)

    @property
    def descriptor(self) -> dict:
        return next(r for r in self.plan["runs"] if r["architecture"] == self.architecture)

    @property
    def binding(self) -> dict:
        return {"input_id": self.descriptor["input_id"], "proposal": self.plan_ref}

    @property
    def binding_ref(self) -> dict:
        # The one attributable decision contains explicit per-pair grants.
        return {
            "plan": self.plan_ref,
            "approval": self.approval_ref,
            "architecture": self.architecture,
            "run_id": self.descriptor["run_id"],
        }

    @property
    def run_id(self) -> str:
        return self.descriptor["run_id"]

    def ensure(self, activity: str, input_id: str) -> None:
        if (
            type(self) is not BatchPairAuthority
            or getattr(self, "seal", None) is not SEAL
            or activity
            not in {"START_PAIR", "CALIBRATION", "REFIT", "DEVELOPMENT_EVALUATION", "CHECKPOINT"}
            or input_id != self.binding["input_id"]
        ):
            raise ValueError("CONCRETE_EXACT_BATCH_PAIR_AUTHORITY_REQUIRED")
        self.review.ensure()
        if (
            json.loads(verify_ref(self.review.root, self.plan_ref).read_text()) != self.plan
            or self.plan["code_sha256"] != batch_code(self.review.root)
            or json.loads(verify_ref(self.review.root, self.approval_ref).read_text())
            != self.approval
            or self.architecture not in approval_scope(self.plan_ref, self.approval)
        ):
            raise ValueError("STALE_BATCH_SOURCE_CODE_OR_APPROVAL")
        for key in (
            "dataset",
            "market",
            "input_binding",
            "prior_real_journal",
            "original_protocol",
        ):
            verify_ref(self.review.root, self.plan[key])

    def inputs(self) -> BatchInputs:
        self.ensure("START_PAIR", self.binding["input_id"])
        if "inputs" not in self.cache:
            binding = json.loads(verify_ref(self.review.root, self.plan["dataset"]).read_text())
            self.cache["inputs"] = load_batch_inputs(self.review, binding)
        return self.cache["inputs"]

    def view(self, key: str):
        view = self.inputs().view(key, self.contract["channels"])
        expected = self.descriptor["views"][key]
        if view.version != expected["view_id"] or view.preparation_id != expected["preparation_id"]:
            raise ValueError("APPROVED_REAL_JOIN_OR_PREPARATION_CHANGED")
        return view

    def append(self, status: str, detail: dict) -> None:
        if status != "FAILED":
            self.ensure("CHECKPOINT", self.binding["input_id"])
        elif type(self) is not BatchPairAuthority or getattr(self, "seal", None) is not SEAL:
            raise ValueError("CONCRETE_FAILED_PAIR_AUTHORITY_REQUIRED")
        root = self.review.root
        path = root / JOURNAL_V2
        lock = path.with_suffix(".lock")
        with lock.open("x"):
            pass
        try:
            rows = journal_rows_v2(path)
            own = [r for r in rows if r["run_id"] == self.run_id]
            selected = approval_scope(self.plan_ref, self.approval)
            if status == "STARTED":
                started = [r["architecture"] for r in rows if r["status"] == "STARTED"]
                if (
                    own
                    or started != list(selected[: len(started)])
                    or selected[len(started) : len(started) + 1] != (self.architecture,)
                ):
                    raise ValueError("NO_RETRY_DUPLICATE_OR_OUT_OF_ORDER_BATCH_PAIR")
                if rows and rows[-1]["status"] != "COMPLETED":
                    raise ValueError("PRECEDING_PAIR_MUST_COMPLETE")
            elif not own or status not in TRANSITIONS[own[-1]["status"]]:
                raise ValueError("EXACT_CURRENT_PAIR_TRANSITION_REQUIRED")
            event = {
                "sequence": len(rows) + 1,
                "previous": fingerprint(rows),
                "at": datetime.now(timezone.utc).isoformat(),
                "run_id": self.run_id,
                "pair_key": fingerprint(
                    [self.binding_ref, self.binding["input_id"], self.contract]
                ),
                "architecture": self.architecture,
                "contract": self.contract,
                "status": status,
                "authority": self.binding_ref,
                "legacy_real_journal": self.plan["prior_real_journal"],
                "global_started_pairs": 1
                + sum(r["status"] == "STARTED" for r in rows)
                + int(status == "STARTED"),
                "detail": detail,
            }
            if status == "STARTED" and not rows:
                pointer = root / "configs/CURRENT_EXPERIMENT_REGISTRY.json"
                if digest(pointer) != self.plan["prior_pointer_snapshot"]["sha256"]:
                    raise ValueError("UNREVIEWED_PRIOR_REGISTRY_POINTER")
                atomic_replace_json(
                    pointer,
                    {
                        "schema": 2,
                        "definition": self.plan["registry_definition"],
                        "previous_pointer": self.plan["prior_pointer_snapshot"],
                        "legacy_real_journal": self.plan["prior_real_journal"],
                        "real_journal": JOURNAL_V2,
                        "plan": self.plan_ref,
                        "approval": self.approval_ref,
                        "counts_started_including_failed": True,
                    },
                )
            old = path.read_bytes() if path.exists() else b""
            temporary = path.with_suffix(".pending")
            atomic_new(
                temporary, old + json.dumps(event, sort_keys=True, allow_nan=False).encode() + b"\n"
            )
            journal_rows_v2(temporary)
            os.replace(temporary, path)
        finally:
            lock.unlink()


def load_pair_authority(
    root: Path, plan_ref: dict, approval_ref: dict, architecture: str
) -> BatchPairAuthority:
    plan, review = load_plan(root, plan_ref)
    approval = json.loads(verify_ref(root, approval_ref).read_text())
    if architecture not in approval_scope(plan_ref, approval):
        raise ValueError("PAIR_NOT_EXPLICITLY_APPROVED")
    result = BatchPairAuthority(review, plan_ref, plan, approval_ref, approval, architecture, SEAL)
    result.ensure("START_PAIR", result.binding["input_id"])
    return result
