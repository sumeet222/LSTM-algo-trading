"""Exact amended byte caps and unstarted-suffix continuation; no training."""

import pytest

from lstm_data.config import fingerprint
from lstm_data.hf20_horizon_preflight import proposed_runs
from lstm_data.hf20_horizon_resource_continue import remaining_runs
from lstm_data.hf20_horizon_resources import capacity_check

CAPS = dict(
    RAM_bytes=2_000_000_000, task_artifact_bytes=2_500_000_000, project_bytes=15_000_000_000
)


def test_exact_new_storage_and_unchanged_ram_boundaries():
    assert not any(capacity_check(2_000_000_000, 2_500_000_000, 15_000_000_000, CAPS).values())
    for values, field in (
        ((2_000_000_001, 0, 0), "RAM_bytes"),
        ((0, 2_500_000_001, 0), "task_artifact_bytes"),
        ((0, 0, 15_000_000_001), "project_bytes"),
    ):
        with pytest.raises(ValueError, match=field):
            capacity_check(*values, CAPS)
    # Both newly authorized capacities exceed the former caps without changing RAM.
    assert not any(capacity_check(1_200_000_000, 2_000_000_000, 12_000_000_000, CAPS).values())


def test_continuation_only_returns_unstarted_ids_and_never_restarts_a_fit():
    history = []
    for i, run in enumerate(proposed_runs()[:12], 75):
        for status in ("STARTED", "CALIBRATED", "REFITTING", "COMPLETED"):
            history.append(
                dict(
                    sequence=len(history) + 1,
                    previous=fingerprint(history),
                    run_id=run,
                    status=status,
                    global_started_pairs=i,
                    effective_ceiling=200,
                    detail={},
                )
            )
    assert remaining_runs(history) == proposed_runs()[12:]
    assert len(remaining_runs(history)) == 20
    history.pop()
    with pytest.raises(ValueError, match="DURABLE_COMPLETION"):
        remaining_runs(history)
