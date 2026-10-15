"""Sealed Package011 approval, linked budget and immutable sequential pair identities."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from .config import atomic_new, digest, fingerprint, now
from .controlled_loss import LossPolicy
from .pretraining_policy import verify_ref
from .pretraining_store import read_preparation
from .pretraining_transforms import CandidateView
from .real_batch_authority import TRANSITIONS, atomic_replace_json, journal_rows_v2
from .real_batch_data import BatchInputs
from .real_bridge_authority import CONTRACT, BridgeReview, load_review
from .real_bridge_data import RealInputView, load_inputs
from .wf2_replication import journal_rows as journal_rows_v3

JOURNAL = "reports/audit/track_a_real_pairs_v4.jsonl"
SEAL = object()
QUEUE = tuple(
    (arm, fold, seed)
    for seed, arms in ((42, ("H1", "T1", "T2", "O1")), (123, ("C0", "H1", "T1", "T2", "O1")))
    for arm in arms
    for fold in ("WF1", "WF2")
)


def run_id(arm: str, fold: str, seed: int) -> str:
    return f"TA011-{arm}-S{seed}-{fold}"


def contract(arm: str, fold: str, seed: int) -> dict:
    if (arm, fold, seed) not in QUEUE:
        raise ValueError("EXACT_18_CASE_QUEUE_REQUIRED")
    return {
        **CONTRACT,
        "arm": arm,
        "seed": seed,
        "stage": fold,
        "cutoff": "2023-06-30" if fold == "WF1" else "2023-12-31",
        "clip": 5.0 if arm == "O1" else 1.0,
        "objective": {
            "H1": "HUBER_DELTA_2",
            "T1": "CAPPED_TRAIN_TARGET_MSE",
            "T2": "ASINH_TARGET_MSE",
        }.get(arm, "MSE"),
        "target_clipping": arm == "T1",
        "target_representation": "ASINH_FIXED_TRAIN_SCALE" if arm == "T2" else "TG0",
        "pair_limit": 18,
        "amendment": "TA011_v1",
    }


def code_binding(root: Path) -> str:
    names = (
        "controlled_loss.py",
        "controlled_authority.py",
        "controlled_batch.py",
        "real_bridge_run.py",
        "real_bridge_authority.py",
        "real_bridge_data.py",
        "real_batch_data.py",
        "batch_telemetry.py",
        "neural_engine.py",
        "neural_lifecycle.py",
        "neural_health.py",
        "pretraining_transforms.py",
        "pretraining_store.py",
        "baseline_ridge.py",
    )
    return fingerprint({n: digest(root / "src/lstm_data" / n) for n in names})


def journal_rows(path: Path) -> list[dict]:
    raw = path.read_bytes() if path.exists() else b""
    if raw and not raw.endswith(b"\n"):
        raise ValueError("TA011_TRUNCATED_JOURNAL")
    rows = [json.loads(r) for r in raw.splitlines()]
    states: dict[str, str] = {}
    started = []
    for i, r in enumerate(rows):
        key = r["run_id"]
        status = r["status"]
        if (
            r["sequence"] != i + 1
            or r["previous"] != fingerprint(rows[:i])
            or status not in TRANSITIONS
        ):
            raise ValueError("TA011_CHAIN_OR_STATUS")
        c = r["contract"]
        if c != contract(c["arm"], c["stage"], c["seed"]) or key != run_id(
            c["arm"], c["stage"], c["seed"]
        ):
            raise ValueError("TA011_CONTRACT_IDENTITY")
        if status == "STARTED":
            expected = run_id(*QUEUE[len(started)]) if len(started) < 18 else None
            if (
                key in states
                or key != expected
                or (i and rows[i - 1]["status"] not in {"COMPLETED", "FAILED"})
            ):
                raise ValueError("TA011_NO_RETRY_REORDER_OR_OVERLAP")
            started.append(key)
        elif key not in states or status not in TRANSITIONS[states[key]]:
            raise ValueError("TA011_MONOTONE_TRANSITION_REQUIRED")
        states[key] = status
        if r["global_started_pairs"] != 6 + len(started):
            raise ValueError("TA011_GLOBAL_BUDGET_CHAIN")
    return rows


def load_plan(root: Path, ref: dict) -> tuple[dict, BridgeReview]:
    plan = json.loads(verify_ref(root, ref).read_text())
    if (
        plan.get("id") != "TA011_CONTROLLED_18_v1"
        or plan.get("code_sha256") != code_binding(root)
        or plan.get("ceiling") != 40
        or plan.get("opening_started") != 6
        or plan.get("confirmation_access") is not False
        or plan.get("production_migration") is not False
        or plan.get("report_reserve_seconds") != 900
    ):
        raise ValueError("TA011_EXACT_PLAN_CODE_AND_SCOPE_REQUIRED")
    if [(r["arm"], r["fold"], r["seed"]) for r in plan["runs"]] != list(QUEUE):
        raise ValueError("TA011_EXACT_QUEUE_REQUIRED")
    for r in plan["runs"]:
        if r["contract"] != contract(r["arm"], r["fold"], r["seed"]) or r["run_id"] != run_id(
            r["arm"], r["fold"], r["seed"]
        ):
            raise ValueError("TA011_EXACT_RUN_CONTRACT")
    for ref in plan["protected_refs"]:
        verify_ref(root, ref)
    for refs in plan["stock_preparations"].values():
        for ref in refs.values():
            verify_ref(root, ref)
    old2 = journal_rows_v2(root / "reports/audit/track_a_real_pairs_v2.jsonl")
    old3 = journal_rows_v3(root / "reports/audit/track_a_real_pairs_v3.jsonl")
    if (
        sum(r["status"] == "STARTED" for r in old2) != 3
        or sum(r["status"] == "STARTED" for r in old3) != 2
        or old3[-1]["status"] != "COMPLETED"
    ):
        raise ValueError("TA011_SIX_PAIR_PREDECESSOR_REQUIRED")
    return plan, load_review(root, plan["producer"])


def approval_scope(ref: dict, approval: dict, plan: dict) -> None:
    if (
        approval.get("actor_type") != "human"
        or approval.get("owner") != "Track A researcher"
        or approval.get("status") != "APPROVED"
        or approval.get("proposal_sha256") != ref["sha256"]
        or approval.get("approved_runs") != [r["run_id"] for r in plan["runs"]]
        or approval.get("approve_registry_v4") is not True
        or approval.get("extend_qualified_attestation") is not True
        or not approval.get("response_text")
        or not approval.get("response_provenance")
    ):
        raise ValueError("TA011_ACTUAL_HASH_BOUND_HUMAN_BATCH_APPROVAL_REQUIRED")


def load_stock_inputs(review: BridgeReview, plan: dict, fold: str) -> BatchInputs:
    if fold not in {"WF1", "WF2"}:
        raise ValueError("ONLY_TWO_DEVELOPMENT_FOLDS")
    base, _ = load_inputs(review, (fold + "_REFIT",))
    candidates = {
        k: CandidateView(base, read_preparation(review.root, ref))
        for k, ref in plan["stock_preparations"][fold].items()
    }
    return BatchInputs(review, base, candidates, {}, fold="WF1" if fold == "WF1" else "WF2")


@dataclass(frozen=True)
class ControlledAuthority:
    review: BridgeReview
    plan_ref: dict
    plan: dict
    approval_ref: dict
    approval: dict
    run_id: str
    seal: object
    cache: dict = field(default_factory=dict, compare=False)

    @property
    def descriptor(self) -> dict:
        return next(r for r in self.plan["runs"] if r["run_id"] == self.run_id)

    @property
    def contract(self) -> dict:
        return self.descriptor["contract"]

    @property
    def binding(self) -> dict:
        return {"input_id": self.descriptor["input_id"], "proposal": self.plan_ref}

    @property
    def binding_ref(self) -> dict:
        return {"plan": self.plan_ref, "approval": self.approval_ref, "run_id": self.run_id}

    def ensure(self, activity: str, input_id: str) -> None:
        if (
            type(self) is not ControlledAuthority
            or getattr(self, "seal", None) is not SEAL
            or activity
            not in {"START_PAIR", "CALIBRATION", "REFIT", "DEVELOPMENT_EVALUATION", "CHECKPOINT"}
            or input_id != self.binding["input_id"]
        ):
            raise ValueError("TA011_CONCRETE_SEALED_AUTHORITY_REQUIRED")
        approval_scope(self.plan_ref, self.approval, self.plan)
        if (
            json.loads(verify_ref(self.review.root, self.plan_ref).read_text()) != self.plan
            or json.loads(verify_ref(self.review.root, self.approval_ref).read_text())
            != self.approval
            or code_binding(self.review.root) != self.plan["code_sha256"]
        ):
            raise ValueError("TA011_STALE_CODE_OR_APPROVAL")
        self.review.ensure()
        for ref in self.plan["protected_refs"]:
            verify_ref(self.review.root, ref)
        rows = journal_rows(self.review.root / JOURNAL)
        pointer = self.review.root / "configs/CURRENT_EXPERIMENT_REGISTRY.json"
        if not rows:
            if digest(pointer) != self.plan["prior_pointer_snapshot"]["sha256"]:
                raise ValueError("TA011_PRIOR_POINTER_CHANGED")
        else:
            active = json.loads(pointer.read_text())
            if (
                active.get("plan") != self.plan_ref
                or active.get("approval") != self.approval_ref
                or active.get("real_journal") != JOURNAL
                or active.get("definition") != self.plan["registry_definition"]
            ):
                raise ValueError("TA011_ACTIVE_POINTER_CHANGED")

    def inputs(self) -> BatchInputs:
        self.ensure("START_PAIR", self.binding["input_id"])
        if "inputs" not in self.cache:
            self.cache["inputs"] = load_stock_inputs(self.review, self.plan, self.contract["stage"])
        return self.cache["inputs"]

    def view(self, key: str) -> RealInputView:
        value = self.inputs().stock_view(key)
        expected = self.descriptor["views"][key]
        if (
            value.version != expected["view_id"]
            or value.preparation_id != expected["preparation_id"]
        ):
            raise ValueError("TA011_MASK_OR_RECIPE_CHANGED")
        return value

    def policy(self, preparation: str) -> LossPolicy:
        params = self.descriptor["target_parameters"]
        row = next(v for v in params.values() if v["preparation_id"] == preparation)
        return LossPolicy(**row["policy"])

    def append(self, status: str, detail: dict) -> None:
        if status != "FAILED":
            self.ensure("CHECKPOINT", self.binding["input_id"])
        elif type(self) is not ControlledAuthority or getattr(self, "seal", None) is not SEAL:
            raise ValueError("TA011_CONCRETE_FAILURE_AUTHORITY")
        path = self.review.root / JOURNAL
        lock = path.with_suffix(".lock")
        with lock.open("x"):
            pass
        try:
            rows = journal_rows(path)
            own = [r for r in rows if r["run_id"] == self.run_id]
            starts = sum(r["status"] == "STARTED" for r in rows)
            if status == "STARTED":
                if (
                    own
                    or starts >= 18
                    or self.run_id != run_id(*QUEUE[starts])
                    or (rows and rows[-1]["status"] not in {"COMPLETED", "FAILED"})
                ):
                    raise ValueError("TA011_NO_RETRY_REORDER_OR_OVERLAP")
            elif not own or status not in TRANSITIONS[own[-1]["status"]]:
                raise ValueError("TA011_CURRENT_TRANSITION_REQUIRED")
            event = dict(
                sequence=len(rows) + 1,
                previous=fingerprint(rows),
                at=now(),
                run_id=self.run_id,
                contract=self.contract,
                pair_key=fingerprint([self.binding_ref, self.binding["input_id"], self.contract]),
                authority=self.binding_ref,
                status=status,
                detail=detail,
                global_started_pairs=6 + starts + int(status == "STARTED"),
            )
            if status == "STARTED" and not rows:
                atomic_replace_json(
                    self.review.root / "configs/CURRENT_EXPERIMENT_REGISTRY.json",
                    dict(
                        schema=4,
                        definition=self.plan["registry_definition"],
                        previous_pointer=self.plan["prior_pointer_snapshot"],
                        real_journal=JOURNAL,
                        plan=self.plan_ref,
                        approval=self.approval_ref,
                        counts_started_including_failed=True,
                    ),
                )
            temporary = path.with_suffix(".pending")
            atomic_new(
                temporary,
                (path.read_bytes() if path.exists() else b"")
                + json.dumps(event, sort_keys=True, allow_nan=False).encode()
                + b"\n",
            )
            journal_rows(temporary)
            os.replace(temporary, path)
        finally:
            lock.unlink()


def authority(root: Path, plan_ref: dict, approval_ref: dict, name: str) -> ControlledAuthority:
    plan, review = load_plan(root, plan_ref)
    approval = json.loads(verify_ref(root, approval_ref).read_text())
    approval_scope(plan_ref, approval, plan)
    value = ControlledAuthority(review, plan_ref, plan, approval_ref, approval, name, SEAL)
    value.ensure("START_PAIR", value.binding["input_id"])
    return value
