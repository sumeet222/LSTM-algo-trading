"""Read-only, hash-bound HF20 input bridge; no model/checkpoint or held-out interface."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .config import digest
from .hf20_features import COMMON, ORDER
from .hf20_source import BARRIER, REVISION, SYMBOLS

PROPOSAL_SHA = "4d5793805d0d327a7115a792f6d9dbf95f18858d72d4191ae9d6e581f8493eaf"
V2_PROPOSAL_SHA = "bfc0eac3b504a9ae428e365e96fd9043bb1c43eedbff661310c42f3dac511c77"
V2_ANSWER = (
    "Approve the HF20 v2 validity-rule amendment, with its revised retention thresholds, "
    "provided the reported diagnostics are reproducible."
)
PROPOSALS = {
    PROPOSAL_SHA: "FT1_HF20_HOURLY_NATIVE_V1",
    V2_PROPOSAL_SHA: "FT1_HF20_HOURLY_NATIVE_V2",
}


def local(root: Path, name: str) -> Path:
    """Contract references are project-relative and cannot escape the checkout."""
    path = (root / name).resolve()
    if Path(name).is_absolute() or not path.is_relative_to(root.resolve()):
        raise ValueError("HF20_PROJECT_RELATIVE_REFERENCE_REQUIRED")
    return path


def verified(root: Path, ref: dict) -> Path:
    path = local(root, ref["path"])
    if not path.is_file() or digest(path) != ref["sha256"]:
        raise ValueError("HF20_BOUND_CONTENT_CHANGED")
    return path


def require_approval(
    root: Path, ref: dict, *, proposal_sha: str = PROPOSAL_SHA, amendment_ref: dict | None = None
) -> dict:
    """An actual scoped live researcher response, not a readiness report, grants policy."""
    receipt = json.loads(verified(root, ref).read_text())
    if (
        receipt.get("proposal_sha256") != PROPOSAL_SHA
        or receipt.get("actor") != "user"
        or receipt.get("methodology_answer") != "Approve this exact conditional methodology"
        or receipt.get("rights_answer") != "I attest these bounded local-use rights"
        or receipt.get("rights_status") != "RESEARCHER_ATTESTED_LOCAL_USE"
        or receipt.get("training_authorized") is not False
    ):
        raise ValueError("HF20_ACTUAL_METHODOLOGY_AND_LOCAL_RIGHTS_APPROVAL_REQUIRED")
    if proposal_sha not in PROPOSALS:
        raise ValueError("HF20_EXACT_PROPOSAL_REQUIRED")
    if proposal_sha == V2_PROPOSAL_SHA:
        if amendment_ref is None:
            raise ValueError("HF20_V2_ACTUAL_AMENDMENT_APPROVAL_REQUIRED")
        amendment = json.loads(verified(root, amendment_ref).read_text())
        if (
            amendment.get("actor") != "user"
            or amendment.get("proposal_sha256") != V2_PROPOSAL_SHA
            or amendment.get("answer") != V2_ANSWER
            or amendment.get("training_authorized") is not False
        ):
            raise ValueError("HF20_V2_ACTUAL_AMENDMENT_APPROVAL_REQUIRED")
    return receipt


def check_identity(contract: dict, *, mode: str, split: str, recipe: str) -> None:
    """Fail before component deserialization on missing policy, wrong lineage or lock."""
    if split not in {
        "inner_train",
        "inner_validation",
        "refit",
        "development",
        "forecast_development",
    }:
        raise ValueError("HF20_CONFIRMATION_OR_UNKNOWN_SPLIT_DENIED")
    if (
        mode != "CANDIDATE_HOURLY_NATIVE"
        or recipe not in {"inner", "refit"}
        or contract.get("source_revision") != REVISION
        or tuple(contract.get("symbols", ())) != SYMBOLS
        or tuple(contract.get("feature_order", ())) != ORDER
        or contract.get("clock_id") != "HF20_COMPLETED_VENDOR_HOUR_CLOSE_PROXY_V1"
        or contract.get("feature_id") != PROPOSALS.get(str(contract.get("proposal_sha256", "")))
        or contract.get("target_id") != "TG20_HF20_CROSS_SECTIONAL_V1"
        or contract.get("proposal_sha256") not in PROPOSALS
        or contract.get("training_authorized") is not False
        or contract.get("readiness")
        not in {"HF20_TRAIN_INPUT_READY_CONDITIONAL", "HF20_TRAIN_INPUT_READY_STRICT"}
    ):
        raise ValueError("HF20_EXACT_READY_SOURCE_CLOCK_COHORT_TARGET_PREPARATION_REQUIRED")
    if (split in {"inner_train", "inner_validation"}) != (recipe == "inner"):
        raise ValueError("HF20_INNER_VS_REFIT_RECIPE_MISMATCH")
    if not contract.get("approval") or not contract.get("preparation_id"):
        raise ValueError("HF20_ACTUAL_APPROVAL_AND_PREPARATION_REQUIRED")
    if contract.get("config", {}).get("sha256") != contract["proposal_sha256"]:
        raise ValueError("HF20_CONFIG_AND_APPROVED_PROPOSAL_MISMATCH")


@dataclass(frozen=True)
class HF20Batch:
    x: np.ndarray
    y: np.ndarray
    label_valid: np.ndarray
    sessions: tuple[str, ...]
    origins: tuple[int, ...]
    preparation_id: str
    recipe_id: str


@dataclass(frozen=True)
class HF20View:
    """Unique common-hour and M2-day components plus lightweight origin indices."""

    common: np.ndarray
    m2: np.ndarray
    targets: np.ndarray
    day_index: np.ndarray
    rows: pd.DataFrame
    preparation_id: str
    recipe_id: str

    def batch(self, positions: tuple[int, ...]) -> HF20Batch:
        if (
            not positions
            or len(set(positions)) != len(positions)
            or any(type(p) is not int or not 0 <= p < len(self.rows) for p in positions)
        ):
            raise ValueError("HF20_UNIQUE_VALID_ORIGIN_POSITIONS_REQUIRED")
        x, y, labels, sessions, origins = [], [], [], [], []
        for position in positions:
            row = self.rows.iloc[position]
            last, day, origin = int(row.last_step), int(row.day_index), int(row.origin) - 1
            historical = np.arange(last - 47, last + 1)
            common = self.common[historical].transpose(1, 0, 2)
            m2 = self.m2[self.day_index[historical], :, origin].T
            values = np.empty((20, 48, 16), dtype=np.float32)
            for k, name in enumerate(ORDER):
                values[..., k] = m2 if name == "M2" else common[..., COMMON.index(name)]
            if not np.isfinite(values).all():
                raise ValueError("HF20_COMPLETE_FINITE_BATCH_REQUIRED")
            target = self.targets[day, :, origin]
            label = bool(row.label_ready)
            if label and not np.isfinite(target).all():
                raise ValueError("HF20_FULL20_FINITE_TARGET_REQUIRED")
            x.append(values)
            y.append(target)
            labels.append(label)
            sessions.append(str(row.session))
            origins.append(origin + 1)
        return HF20Batch(
            np.stack(x),
            np.stack(y),
            np.asarray(labels, dtype=bool),
            tuple(sessions),
            tuple(origins),
            self.preparation_id,
            self.recipe_id,
        )


def load_hf20_train_data(
    contract_path: Path,
    *,
    mode: str = "CANDIDATE_HOURLY_NATIVE",
    split: str = "development",
    recipe: str = "refit",
    root: Path | None = None,
) -> HF20View:
    """No held-out split, model weights, fitting, network or original-project input reads."""
    root = (root or Path.cwd()).resolve()
    contract = json.loads(contract_path.read_text())
    check_identity(contract, mode=mode, split=split, recipe=recipe)
    require_approval(
        root,
        contract["approval"],
        proposal_sha=contract["proposal_sha256"],
        amendment_ref=contract.get("amendment_approval"),
    )
    for ref in contract["code"] + contract["source"] + [contract["config"], contract["recipes"]]:
        verified(root, ref)
    index = pd.read_csv(verified(root, contract["origins"][recipe]))
    if index.session.ge(str(BARRIER.date())).any():
        raise ValueError("HF20_CONFIRMATION_INDEX_DENIED")
    tail = contract["inner_validation_start"]
    selected = {
        "inner_train": index.session.lt(tail),
        "inner_validation": index.session.ge(tail) & index.session.le("2025-03-28"),
        "refit": index.session.le("2025-03-28"),
        "development": index.session.ge("2025-03-31"),
        "forecast_development": index.session.ge("2025-03-31"),
    }[split]
    selected &= (
        index.forecast_issuable if split == "forecast_development" else index.supervised_ready
    )
    index = index.loc[selected].reset_index(drop=True)
    with np.load(verified(root, contract["store"]), allow_pickle=False) as store:
        if (
            tuple(store["symbols"].tolist()) != SYMBOLS
            or str(store["preparation_id"].item()) != contract["preparation_id"]
            or str(store["maximum_numeric_date"].item()) >= str(BARRIER.date())
        ):
            raise ValueError("HF20_STORE_PREPARATION_OR_LOCK_CHANGED")
        common = store[recipe + "_common"]
        m2 = store[recipe + "_m2"]
        day_index = store["day_index"]
    with np.load(verified(root, contract["targets"]), allow_pickle=False) as target_store:
        if str(target_store["preparation_id"].item()) != contract["preparation_id"]:
            raise ValueError("HF20_TARGET_PREPARATION_CHANGED")
        targets = target_store[recipe + "_targets"]
    for array in (common, m2, targets, day_index):
        array.setflags(write=False)
    return HF20View(
        common,
        m2,
        targets,
        day_index,
        index,
        contract["preparation_id"],
        contract["recipe_ids"][recipe],
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--split", default="development")
    parser.add_argument("--recipe", choices=("inner", "refit"), default="refit")
    args = parser.parse_args()
    view = load_hf20_train_data(args.contract, split=args.split, recipe=args.recipe)
    batch = view.batch(tuple(range(min(3, len(view.rows)))))
    print(
        json.dumps(
            dict(
                origins=len(view.rows),
                shape=batch.x.shape,
                finite=bool(np.isfinite(batch.x).all()),
                sessions=batch.sessions,
                preparation_id=batch.preparation_id,
                training=False,
            )
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
