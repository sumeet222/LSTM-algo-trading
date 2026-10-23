"""Zero-optimizer-step regression oracles for the P022 progress failure and budget."""

import json
from pathlib import Path

import pytest

from lstm_data.config import fingerprint, write_json
from lstm_data.objective_screen_loss import RUNS
from lstm_data.objective_screen_recovery import ensure, validate_history
from lstm_data.objective_screen_run import record_epoch


def test_progress_across_calibration_and_refit_is_atomic_and_append_only(tmp_path: Path) -> None:
    epochs = []
    for phase, count in [("calibration", 12), ("refit", 2)]:
        for epoch in range(1, count + 1):
            epochs.append(dict(phase=phase, training=dict(epoch=epoch, optimizer_steps=0)))
            record_epoch(tmp_path, epochs)
            assert json.loads((tmp_path / "epochs_progress.json").read_text()) == epochs
            assert len(list((tmp_path / "epoch_receipts").iterdir())) == len(epochs)
    before = (tmp_path / "epochs_progress.json").read_bytes()
    with pytest.raises(FileExistsError):
        record_epoch(tmp_path, epochs)
    assert (tmp_path / "epochs_progress.json").read_bytes() == before
    assert not list(tmp_path.glob(".pending-*"))
    for record in epochs:
        path = (
            tmp_path
            / "epoch_receipts"
            / (f"{record['phase']}_{record['training']['epoch']:03d}.json")
        )
        assert json.loads(path.read_text()) == record


def test_original_create_only_writer_explains_failure(tmp_path: Path) -> None:
    path = tmp_path / "progress.json"
    write_json(path, [1])
    with pytest.raises(FileExistsError):
        write_json(path, [1, 2])
    assert json.loads(path.read_text()) == [1]


def test_repair_no_authority_means_no_reads() -> None:
    with pytest.raises(ValueError, match="REPAIR_SEPARATE_LIVE_APPROVAL"):
        ensure(Path("absent-plan"), None, RUNS[0])


def test_repair_charges_38_through_41_and_disallows_fifth_or_failed_retry() -> None:
    records = []
    for k, run_id in enumerate(RUNS):
        for status in ["STARTED", "CALIBRATED", "REFITTING", "COMPLETED"]:
            records.append(
                dict(
                    sequence=len(records) + 1,
                    previous=fingerprint(records),
                    run_id=run_id,
                    status=status,
                    global_started_pairs=38 + k,
                    effective_ceiling=200,
                )
            )
    assert validate_history(records) == records
    extra = dict(
        sequence=17,
        previous=fingerprint(records),
        run_id=RUNS[0],
        status="STARTED",
        global_started_pairs=42,
        effective_ceiling=200,
    )
    with pytest.raises(ValueError, match="NO_EXTRA_RETRY"):
        validate_history(records + [extra])
    failed = records[:1]
    failed.append(
        dict(
            sequence=2,
            previous=fingerprint(failed),
            run_id=RUNS[0],
            status="FAILED",
            global_started_pairs=38,
            effective_ceiling=200,
        )
    )
    validate_history(failed)
    next_start = dict(
        sequence=3,
        previous=fingerprint(failed),
        run_id=RUNS[1],
        status="STARTED",
        global_started_pairs=39,
        effective_ceiling=200,
    )
    with pytest.raises(ValueError, match="PRIOR_MUST_COMPLETE"):
        validate_history(failed + [next_start])
