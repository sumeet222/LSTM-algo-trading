"""Audit-precision correction only; retain failed65 and run the nine unstarted lifecycles."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import numpy as np
import torch
from torch import Tensor
from torch.nn import functional as F

from . import hf20_ranking as ranking
from . import hf20_ranking_continue as campaign
from . import hf20_ranking_diagnostics as diagnostics
from .config import fingerprint, now
from .hf20_ranking_authority import resources
from .hf20_ranking_run import CODE, POINTER, sha, write
from .real_batch_authority import atomic_replace_json

AMENDMENT = "PAIR_GUARD_PROSPECTIVE_AMENDMENT.json"
JOURNAL_V20 = Path("reports/audit/track_a_real_pairs_v20_hf20_ranking_guard.jsonl")
DEFINITION_V20 = Path("configs/track_a_candidate_experiment_registry_v20_hf20_ranking_guard.json")
REMAINING = ranking.RUNS[3:]


def amended_hash() -> str:
    paths = (*CODE, *campaign.NEW_CODE, "src/lstm_data/hf20_ranking_pair_guard.py")
    return hashlib.sha256(
        json.dumps({p: sha(Path(p)) for p in paths}, sort_keys=True).encode()
    ).hexdigest()


def pair_terms(score: Tensor, returns: Tensor, tau: float = 1.0) -> tuple[Tensor, Tensor]:
    """Identical float32 forward/autograd; only detached conservation audit sums are float64."""
    if score.shape != returns.shape or score.shape[-1] < 2 or tau != 1.0:
        raise ValueError("PAIR_SHAPE_OR_FROZEN_TEMPERATURE")
    if not bool(torch.isfinite(score).all()) or not bool(torch.isfinite(returns).all()):
        raise ValueError("NONFINITE_PAIR_INPUT")
    i, j = torch.triu_indices(score.shape[-1], score.shape[-1], offset=1)
    direction = torch.sign(returns[..., i] - returns[..., j]).to(score.dtype)
    valid = direction.ne(0)
    denominator = valid.sum(-1)
    if bool(denominator.eq(0).any()):
        raise ValueError("NO_VALID_UNTIED_PAIRS")
    terms = F.softplus(-direction * (score[..., i] - score[..., j]) / tau) * valid
    allocation = torch.zeros_like(score)
    half = terms / (2 * denominator[..., None])
    allocation = allocation.index_add(-1, i, half).index_add(-1, j, half)
    np.testing.assert_allclose(
        allocation.detach().double().sum(-1).numpy(),
        (terms.detach().double().sum(-1) / denominator.double()).numpy(),
        rtol=3e-7,
        atol=1e-8,
    )
    return terms, allocation


@contextmanager
def validation_adapter() -> Iterator[None]:
    """Explicit prospective runtime binding; no historical source/checkpoint byte is edited."""
    old_pair, old_diag = ranking.pair_terms, diagnostics.pair_terms
    old_hash, old_manifest = campaign.continuation_hash, campaign.MANIFEST
    ranking.pair_terms = pair_terms
    diagnostics.pair_terms = pair_terms
    campaign.continuation_hash = amended_hash
    campaign.MANIFEST = AMENDMENT
    try:
        yield
    finally:
        ranking.pair_terms = old_pair
        diagnostics.pair_terms = old_diag
        campaign.continuation_hash = old_hash
        campaign.MANIFEST = old_manifest


def validate_events(history: list[dict]) -> list[dict]:
    states = {}
    count = 0
    allowed = {
        "STARTED": {"CALIBRATED", "FAILED"},
        "CALIBRATED": {"REFITTING", "FAILED"},
        "REFITTING": {"COMPLETED", "FAILED"},
        "FAILED": set(),
        "COMPLETED": set(),
    }
    for i, row in enumerate(history):
        if row["sequence"] != i + 1 or row["previous"] != fingerprint(history[:i]):
            raise ValueError("GUARD_JOURNAL_CHAIN")
        run, status = row["run_id"], row["status"]
        if status == "STARTED":
            if count >= 9 or run != REMAINING[count] or run in states:
                raise ValueError("NO_RETRY65_OR_EXTRA_START")
            if (
                i
                and history[i - 1]["status"] != "COMPLETED"
                and not (
                    history[i - 1]["status"] == "FAILED"
                    and history[i - 1]["detail"].get("isolated") is True
                )
            ):
                raise ValueError("PREVIOUS_SHARED_OR_UNVERIFIED_FAILURE")
            count += 1
        elif run not in states or status not in allowed[states[run]]:
            raise ValueError("GUARD_JOURNAL_TRANSITION")
        if row["global_started_pairs"] != 65 + count or row["effective_ceiling"] != 200:
            raise ValueError("GUARD_NEURAL_BUDGET")
        states[run] = status
    return history


class GuardJournal(campaign.ContinuationJournal):
    def __init__(self, out: Path, manifest: dict):
        self.out, self.manifest = out, manifest
        self.baseline_keys = []
        self.started = 65
        self.original = json.loads((out / "registry_v19_before_guard.json").read_text())

    def event(self, run: str, status: str, detail: dict) -> None:
        if amended_hash() != self.manifest["execution_sha256"]:
            raise ValueError("CONTINUATION_EXECUTION_CHANGED")
        lock = JOURNAL_V20.with_suffix(".lock")
        with lock.open("x"):
            pass
        try:
            raw = JOURNAL_V20.read_bytes() if JOURNAL_V20.exists() else b""
            if raw and not raw.endswith(b"\n"):
                raise ValueError("TRUNCATED_CONTINUATION_JOURNAL")
            history = validate_events([json.loads(r) for r in raw.splitlines()])
            if status == "STARTED":
                resources(self.out)
                if not (self.out / "STAGE_B_HANDOFF.json").exists():
                    raise ValueError("COMMON_READINESS_HANDOFF_REQUIRED")
                if history and history[-1]["status"] == "COMPLETED":
                    gate = json.loads((self.out / history[-1]["run_id"] / "PASS.json").read_text())
                    if gate["status"] != "PASS_TECHNICAL":
                        raise ValueError("PRIOR_OUTPUT_GATE")
                    for path, expected in gate["files"].items():
                        if sha(Path(path)) != expected:
                            raise ValueError("PRIOR_VERIFIED_OUTPUT_CHANGED")
                elif history and history[-1]["detail"].get("isolated") is not True:
                    raise ValueError("PRIOR_FAILURE_NOT_INDEPENDENTLY_ISOLATED")
            self.started = (
                65 + sum(r["status"] == "STARTED" for r in history) + int(status == "STARTED")
            )
            row = dict(
                sequence=len(history) + 1,
                previous=fingerprint(history),
                at=now(),
                run_id=run,
                status=status,
                global_started_pairs=self.started,
                effective_ceiling=200,
                plan=dict(path=str(self.out / AMENDMENT), sha256=sha(self.out / AMENDMENT)),
                authority=dict(
                    path=str(self.out / "submitted_continuation_authority.txt"),
                    sha256=sha(self.out / "submitted_continuation_authority.txt"),
                ),
                previous_journal=dict(
                    path=self.original["real_journal"],
                    sha256=sha(Path(self.original["real_journal"])),
                ),
                detail=detail,
            )
            validate_events(history + [row])
            with JOURNAL_V20.open("ab") as f:
                f.write((json.dumps(row, sort_keys=True, allow_nan=False) + "\n").encode())
                f.flush()
                os.fsync(f.fileno())
            if not DEFINITION_V20.exists():
                write(
                    DEFINITION_V20,
                    dict(
                        schema_version=20,
                        package="HF20_S1_S2_AUDIT_PRECISION",
                        runs=list(REMAINING),
                        plan=row["plan"],
                        previous_journal=row["previous_journal"],
                    ),
                )
            atomic_replace_json(
                POINTER,
                dict(
                    schema_version=20,
                    definition=dict(path=str(DEFINITION_V20), sha256=sha(DEFINITION_V20)),
                    plan=row["plan"],
                    real_journal=str(JOURNAL_V20),
                    previous_journal=row["previous_journal"],
                    counts_started_including_failed=True,
                    effective_ceiling=200,
                    fit_permission=False,
                    live_approval_required=True,
                    budget_amendment=self.original["budget_amendment"],
                ),
            )
        finally:
            lock.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out
    manifest = json.loads((out / AMENDMENT).read_text())
    if manifest["execution_sha256"] != amended_hash() or manifest["remaining_neural_runs"] != list(
        REMAINING
    ):
        raise ValueError("PROSPECTIVE_GUARD_BINDING")
    for ref in manifest["preserve_refs"]:
        if sha(Path(ref["path"])) != ref["sha256"]:
            raise ValueError("GUARD_PRESERVATION_CHANGED:" + ref["path"])
    if JOURNAL_V20.exists() or (out / "GUARD_EXECUTION_STARTED.json").exists():
        raise ValueError("NO_GUARD_RETRY")
    prior = campaign.validate_events(
        [json.loads(x) for x in Path(manifest["previous_journal"]["path"]).read_text().splitlines()]
    )
    if (
        prior[-1]["global_started_pairs"] != 65
        or prior[-1]["status"] != "FAILED"
        or prior[-1]["run_id"] != ranking.RUNS[2]
    ):
        raise ValueError("FAILED65_NOT_PRESERVED")
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    resources(out)
    write(
        out / "GUARD_EXECUTION_STARTED.json",
        dict(
            at=now(),
            manifest_sha256=sha(out / AMENDMENT),
            failed65_unchanged=True,
            no_new_baseline_fits=True,
        ),
    )
    journal = GuardJournal(out, manifest)
    with validation_adapter():
        data = campaign.FoldData(live_approved=True)
        try:
            for year in (2022, 2023, 2024):
                for arm in ranking.ARMS:
                    campaign.neural_one(data, out, journal, year, arm)
        except BaseException as error:
            write(
                out / "GUARD_FATAL_STOP.json",
                dict(
                    at=now(),
                    message=str(error),
                    global_started_pairs=journal.started,
                    no_retry=True,
                ),
            )
            raise
        write(
            out / "FITTING_FINISHED.json",
            dict(
                at=now(),
                neural_started_total=3 + journal.started - 65,
                global_started_pairs=journal.started,
                prior_failed_start65_preserved=True,
                resources=resources(out),
            ),
        )
        from .hf20_ranking_continue_report import collective

        collective(out)


if __name__ == "__main__":
    main()
