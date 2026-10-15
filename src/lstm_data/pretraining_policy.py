"""Scoped conditional research preparation; never a model or production permission.

An idealized event-time study is deliberately separate from observed publication.
The strict source adapters remain unchanged in their treatment of ASSUMED clocks.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .config import digest, fingerprint

PACKAGE = "TA-PRETRAIN-HOURLY-PROXY-G3-004"
POLICY_ID = "TA-G3-ASSUMPTION-004-v1"
CANDIDATE = ("AAPL", "COST", "CMCSA", "SBUX", "CME")
MANIFEST_SHA = "45a91dd7aff21d9a0aecf3a94635fc4c7eccfbeb08d16c58ec5d196e2fe62aff"
ACTIVITIES = frozenset({"SOURCE_PREPARATION", "FEATURE_TARGET_PREPARATION", "FIT_TRANSFORM_ONLY"})


def local_path(root: Path, value: str) -> Path:
    """All persisted references are relative and confined to the supplied project."""
    if Path(value).is_absolute():
        raise ValueError("PROJECT_RELATIVE_REFERENCE_REQUIRED")
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("REFERENCE_OUTSIDE_PROJECT")
    return path


def verify_ref(root: Path, ref: dict) -> Path:
    path = local_path(root, ref["path"])
    if digest(path) != ref["sha256"]:
        raise ValueError("BOUND_REFERENCE_HASH_CHANGED")
    return path


@dataclass(frozen=True)
class PreparationAuthority:
    """Verified policy + attributable response + local-use documentary references."""

    root: Path
    policy_ref: dict
    approval_ref: dict
    policy: dict
    approval: dict

    @property
    def binding(self) -> str:
        return fingerprint([PACKAGE, self.policy_ref, self.approval_ref])

    def ensure(self, activity: str) -> None:
        # Re-read the approvals on each entry, rather than trusting mutable caller dictionaries.
        policy = json.loads(verify_ref(self.root, self.policy_ref).read_text())
        approval = json.loads(verify_ref(self.root, self.approval_ref).read_text())
        if policy != self.policy or approval != self.approval:
            raise ValueError("PREPARATION_AUTHORITY_CHANGED")
        if activity not in ACTIVITIES:
            raise ValueError("MODEL_FIT_REPLAY_CONFIRMATION_AND_RESERVATION_FORBIDDEN")
        if (
            policy.get("policy_id") != POLICY_ID
            or tuple(policy.get("universe", ())) != CANDIDATE
            or policy.get("source_manifest", {}).get("sha256") != MANIFEST_SHA
            or policy.get("availability_policy")
            != "IDEALIZED_PERIOD_END_ZERO_LATENCY_NOT_OBSERVED_PUBLICATION"
            or policy.get("action_policy")
            != "RETROSPECTIVE_VENDOR_SPLIT_PRICE_INVERSE_VOLUME_ASOF_2025-06-30"
            or policy.get("strict_observed_causality_certified") is not False
            or policy.get("minute_data_required") is not False
            or any(policy.get(k) is not False for k in
                   ("model_fit", "pair_reservation", "forecast_issuance", "trading_replay",
                    "confirmation_numeric"))
        ):
            raise ValueError("EXACT_CONDITIONAL_PREPARATION_POLICY_REQUIRED")
        if (
            approval.get("policy_sha256") != self.policy_ref["sha256"]
            or approval.get("status") not in {"APPROVED", "CONDITIONALLY_APPROVED"}
            or approval.get("actor_type") != "human"
            or approval.get("owner") != "Track A researcher"
            or not approval.get("response_text", "").strip()
            or not approval.get("response_provenance", "").strip()
            or not approval.get("recorded_at", "").strip()
            or approval.get("local_use", {}).get("status") not in {
                "DOCUMENTED_PERMITTED", "RESEARCHER_ASSUMED_LOCAL_USE_NO_LICENSE_ATTESTATION"
            }
        ):
            raise ValueError("ACTUAL_RESEARCHER_POLICY_AND_LOCAL_USE_EVIDENCE_REQUIRED")
        rights = approval["local_use"]
        if (
            approval.get("production_scope") != "CANDIDATE_PREPARATION_ONLY"
            or rights.get("redistribution_authorized") is not False
            or rights.get("license_certified") is not False
        ):
            raise ValueError("CANDIDATE_ONLY_NO_DISTRIBUTION_SCOPE_REQUIRED")
        if not rights.get("scope", "").strip() or not rights.get("evidence_refs"):
            raise ValueError("LOCAL_USE_DOCUMENTARY_BASIS_REQUIRED")
        for ref in rights["evidence_refs"]:
            verify_ref(self.root, ref)
        verify_ref(self.root, policy["source_manifest"])
        verify_ref(self.root, policy["d1_decision"])


def load_authority(root: Path, policy_ref: dict, approval_ref: dict) -> PreparationAuthority:
    """An unanswered question is never an approval, including in reconstruction."""
    policy = json.loads(verify_ref(root, policy_ref).read_text())
    approval = json.loads(verify_ref(root, approval_ref).read_text())
    authority = PreparationAuthority(root.resolve(), policy_ref, approval_ref, policy, approval)
    authority.ensure("SOURCE_PREPARATION")
    return authority
