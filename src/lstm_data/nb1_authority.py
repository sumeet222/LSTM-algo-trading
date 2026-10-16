"""Hash-bound four-pair N-B1 authority and additive prospective 200-cap ledger."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from .config import atomic_new, digest, fingerprint, now
from .controlled_authority import code_binding as prior_code_binding
from .controlled_authority import journal_rows as prior_rows
from .controlled_authority import load_stock_inputs
from .nb1_inputs import compressed_view
from .pretraining_policy import verify_ref
from .real_batch_authority import TRANSITIONS, atomic_replace_json
from .real_batch_data import BatchInputs
from .real_bridge_authority import CONTRACT, BridgeReview, load_review
from .real_bridge_data import RealInputView

JOURNAL = "reports/audit/track_a_real_pairs_v5.jsonl"
QUEUE = (("WF1", 42), ("WF1", 123), ("WF2", 42), ("WF2", 123))
SEAL = object()


def run_id(fold: str, seed: int) -> str:
    return f"TA012B-N-B1-S{seed}-{fold}"


def contract(fold: str, seed: int) -> dict:
    if (fold, seed) not in QUEUE:
        raise ValueError("EXACT_NB1_QUEUE_REQUIRED")
    return {
        **CONTRACT,
        "seed": seed,
        "stage": fold,
        "cutoff": "2023-06-30" if fold == "WF1" else "2023-12-31",
        "arm": "N-B1",
        "objective": "MSE",
        "target_representation": "TG0",
        "pair_limit": 4,
        "amendment": "TA012B_v1",
    }


def code_binding(root: Path) -> str:
    return fingerprint(
        [
            prior_code_binding(root),
            {
                name: digest(root / "src/lstm_data" / name)
                for name in (
                    "nb1_inputs.py",
                    "nb1_authority.py",
                    "nb1_experiment.py",
                    "ft0_transforms.py",
                    "config.py",
                    "neural_data.py",
                )
            },
        ]
    )


def journal_rows(path: Path) -> list[dict]:
    raw = path.read_bytes() if path.exists() else b""
    if raw and not raw.endswith(b"\n"):
        raise ValueError("NB1_TRUNCATED_JOURNAL")
    rows = [json.loads(line) for line in raw.splitlines()]
    states: dict[str, str] = {}
    starts = 0
    for i, row in enumerate(rows):
        status, name = row["status"], row["run_id"]
        if (
            row["sequence"] != i + 1
            or row["previous"] != fingerprint(rows[:i])
            or status not in TRANSITIONS
        ):
            raise ValueError("NB1_JOURNAL_CHAIN")
        c = row["contract"]
        if c != contract(c["stage"], c["seed"]) or name != run_id(c["stage"], c["seed"]):
            raise ValueError("NB1_JOURNAL_CONTRACT")
        if status == "STARTED":
            if (
                starts >= 4
                or name in states
                or name != run_id(*QUEUE[starts])
                or (i and rows[i - 1]["status"] not in {"COMPLETED", "FAILED"})
            ):
                raise ValueError("NB1_NO_DUPLICATE_REORDER_OR_OVERLAP")
            starts += 1
        elif name not in states or status not in TRANSITIONS[states[name]]:
            raise ValueError("NB1_INVALID_TRANSITION")
        states[name] = status
        if row["global_started_pairs"] != 24 + starts or row["effective_ceiling"] != 200:
            raise ValueError("NB1_BUDGET_CHAIN")
    return rows


def approval_scope(ref: dict, receipt: dict, plan: dict) -> None:
    if (
        receipt.get("actor_type") != "human"
        or receipt.get("owner") != "Track A researcher"
        or receipt.get("status") != "APPROVED"
        or not receipt.get("response_text")
        or not receipt.get("response_provenance")
        or receipt.get("proposal_sha256") != ref["sha256"]
        or receipt.get("approved_runs") != [r["run_id"] for r in plan["runs"]]
        or receipt.get("budget_amendment") != plan["budget_amendment"]
        or receipt.get("extend_qualified_attestation") is not True
    ):
        raise ValueError("NB1_EXPLICIT_LIVE_FOUR_PAIR_APPROVAL_REQUIRED")


def load_plan(root: Path, ref: dict) -> tuple[dict, BridgeReview]:
    plan = json.loads(verify_ref(root, ref).read_text())
    if (
        plan.get("id") != "TA012B_NB1_v1"
        or plan.get("code_sha256") != code_binding(root)
        or plan.get("opening_started") != 24
        or plan.get("ceiling") != 200
        or plan.get("confirmation_access") is not False
        or plan.get("production_migration") is not False
        or plan.get("maximum_wall_seconds") != 7200
        or plan.get("report_reserve_seconds") != 900
        or [(r["fold"], r["seed"]) for r in plan["runs"]] != list(QUEUE)
    ):
        raise ValueError("NB1_EXACT_CODE_PLAN_SCOPE_REQUIRED")
    for row in plan["runs"]:
        if row["contract"] != contract(row["fold"], row["seed"]) or row["run_id"] != run_id(
            row["fold"], row["seed"]
        ):
            raise ValueError("NB1_EXACT_RUN_CONTRACT")
    for bound in plan["protected_refs"]:
        verify_ref(root, bound)
    old = prior_rows(root / "reports/audit/track_a_real_pairs_v4.jsonl")
    if len(old) != 72 or old[-1]["status"] != "COMPLETED" or old[-1]["global_started_pairs"] != 24:
        raise ValueError("NB1_EXPECTED_24_COMPLETED_PREFIX")
    amendment = json.loads(verify_ref(root, plan["budget_amendment"]).read_text())
    if (
        amendment["old_ceiling"] != 40
        or amendment["new_ceiling"] != 200
        or amendment["opening_started"] != 24
        or amendment["prospective_only"] is not True
        or amendment["fit_permission"] is not False
        or not amendment["verbatim_statement"]
    ):
        raise ValueError("NB1_BUDGET_AMENDMENT_REQUIRED")
    verify_ref(root, plan["registry_definition"])
    return plan, load_review(root, plan["producer"])


@dataclass(frozen=True)
class NormalizationAuthority:
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
            type(self) is not NormalizationAuthority
            or self.seal is not SEAL
            or activity
            not in {"START_PAIR", "CALIBRATION", "REFIT", "DEVELOPMENT_EVALUATION", "CHECKPOINT"}
            or input_id != self.binding["input_id"]
        ):
            raise ValueError("NB1_SEALED_AUTHORITY_REQUIRED")
        approval_scope(self.plan_ref, self.approval, self.plan)
        if (
            json.loads(verify_ref(self.review.root, self.plan_ref).read_text()) != self.plan
            or json.loads(verify_ref(self.review.root, self.approval_ref).read_text())
            != self.approval
            or code_binding(self.review.root) != self.plan["code_sha256"]
        ):
            raise ValueError("NB1_STALE_CODE_OR_AUTHORITY")
        self.review.ensure()
        for ref in self.plan["protected_refs"]:
            verify_ref(self.review.root, ref)
        pointer = json.loads(
            (self.review.root / "configs/CURRENT_EXPERIMENT_REGISTRY.json").read_text()
        )
        if (
            pointer.get("schema") != 5
            or pointer.get("plan") != self.plan_ref
            or pointer.get("definition") != self.plan["registry_definition"]
            or pointer.get("budget_amendment") != self.plan["budget_amendment"]
            or pointer.get("real_journal") != JOURNAL
        ):
            raise ValueError("NB1_EFFECTIVE_REGISTRY_REQUIRED_BEFORE_START")
        journal_rows(self.review.root / JOURNAL)

    def inputs(self) -> BatchInputs:
        self.ensure("START_PAIR", self.binding["input_id"])
        if "inputs" not in self.cache:
            self.cache["inputs"] = load_stock_inputs(self.review, self.plan, self.contract["stage"])
        return self.cache["inputs"]

    def view(self, key: str) -> RealInputView:
        if key not in self.descriptor["views"]:
            raise ValueError("NB1_ONLY_REGISTERED_PARTITIONS")
        if key not in self.cache:
            prefix = "inner" if key in {"inner", "validation"} else "refit"
            value, _ = compressed_view(
                self.inputs(), key, self.plan["recipes"][self.contract["stage"]][prefix]
            )
            if value.summary() != self.descriptor["views"][key]:
                raise ValueError("NB1_STALE_RECIPE_OR_MASK")
            self.cache[key] = value
        return self.cache[key]

    def append(self, status: str, detail: dict) -> None:
        self.ensure("CHECKPOINT", self.binding["input_id"])
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
                    or starts >= 4
                    or self.run_id != run_id(*QUEUE[starts])
                    or (rows and rows[-1]["status"] not in {"COMPLETED", "FAILED"})
                ):
                    raise ValueError("NB1_NO_DUPLICATE_REORDER_OR_OVERLAP")
            elif not own or status not in TRANSITIONS[own[-1]["status"]]:
                raise ValueError("NB1_INVALID_TRANSITION")
            event = dict(
                sequence=len(rows) + 1,
                previous=fingerprint(rows),
                at=now(),
                run_id=self.run_id,
                contract=self.contract,
                authority=self.binding_ref,
                pair_key=fingerprint([self.binding_ref, self.binding["input_id"], self.contract]),
                status=status,
                detail=detail,
                global_started_pairs=24 + starts + int(status == "STARTED"),
                effective_ceiling=200,
                budget_amendment=self.plan["budget_amendment"],
            )
            temp = path.with_suffix(".pending")
            atomic_new(
                temp,
                (path.read_bytes() if path.exists() else b"")
                + json.dumps(event, sort_keys=True, allow_nan=False).encode()
                + b"\n",
            )
            journal_rows(temp)
            os.replace(temp, path)
        finally:
            lock.unlink()


def authority(root: Path, plan_ref: dict, approval_ref: dict, name: str) -> NormalizationAuthority:
    plan, review = load_plan(root, plan_ref)
    receipt = json.loads(verify_ref(root, approval_ref).read_text())
    approval_scope(plan_ref, receipt, plan)
    value = NormalizationAuthority(review, plan_ref, plan, approval_ref, receipt, name, SEAL)
    value.ensure("START_PAIR", value.binding["input_id"])
    return value


def activate(root: Path, plan_ref: dict) -> None:
    """Make the already researcher-authorized budget effective, granting zero fitting permission."""
    plan, _ = load_plan(root, plan_ref)
    pointer = root / "configs/CURRENT_EXPERIMENT_REGISTRY.json"
    if digest(pointer) != plan["prior_pointer_snapshot"]["sha256"]:
        raise ValueError("NB1_PRIOR_POINTER_CHANGED")
    atomic_replace_json(
        pointer,
        dict(
            schema=5,
            definition=plan["registry_definition"],
            plan=plan_ref,
            budget_amendment=plan["budget_amendment"],
            real_journal=JOURNAL,
            previous_pointer=plan["prior_pointer_snapshot"],
            counts_started_including_failed=True,
            fit_permission=False,
        ),
    )
