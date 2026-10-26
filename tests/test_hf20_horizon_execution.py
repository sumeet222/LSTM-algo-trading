"""S3 journal/role corruption barriers without a market fit or optimizer call."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from lstm_data.config import fingerprint
from lstm_data.hf20_horizon_authority import validate
from lstm_data.hf20_horizon_data import HorizonData, relative_output
from lstm_data.hf20_horizon_diagnostics import verify_role
from lstm_data.hf20_horizon_preflight import proposed_runs


def event(history: list[dict], run: str, status: str, count: int, isolated: bool = False) -> dict:
    return dict(
        sequence=len(history) + 1,
        previous=fingerprint(history),
        run_id=run,
        status=status,
        global_started_pairs=count,
        effective_ceiling=200,
        detail=dict(isolated=isolated),
    )


def test_next_model_requires_completed_or_explicitly_isolated_previous():
    runs = proposed_runs()
    history = [event([], runs[0], "STARTED", 75)]
    with pytest.raises(ValueError, match="PREVIOUS_GATE"):
        validate(history + [event(history, runs[1], "STARTED", 76)])
    history.append(event(history, runs[0], "CALIBRATED", 75))
    with pytest.raises(ValueError, match="PREVIOUS_GATE"):
        validate(history + [event(history, runs[1], "STARTED", 76)])
    history.append(event(history, runs[0], "REFITTING", 75))
    history.append(event(history, runs[0], "COMPLETED", 75))
    validate(history + [event(history, runs[1], "STARTED", 76)])
    with pytest.raises(ValueError, match="NO_RETRY"):
        validate(history + [event(history, runs[0], "STARTED", 76)])


@pytest.mark.parametrize("isolated", [False, True])
def test_failure_is_charged_permanently_and_never_retried(isolated: bool):
    runs = proposed_runs()
    h = [event([], runs[0], "STARTED", 75)]
    h.append(event(h, runs[0], "FAILED", 75, isolated))
    with pytest.raises(ValueError, match="NO_RETRY"):
        validate(h + [event(h, runs[0], "STARTED", 76)])
    if isolated:
        validate(h + [event(h, runs[1], "STARTED", 76)])
    else:
        with pytest.raises(ValueError, match="PREVIOUS_GATE"):
            validate(h + [event(h, runs[1], "STARTED", 76)])


def test_exact32_order_and_start106_ceiling():
    h = []
    for n, run in enumerate(proposed_runs(), 75):
        for status in ("STARTED", "CALIBRATED", "REFITTING", "COMPLETED"):
            h.append(event(h, run, status, n))
    assert validate(h)[-1]["global_started_pairs"] == 106
    with pytest.raises(ValueError, match="NO_RETRY"):
        validate(h + [event(h, "EXTRA", "STARTED", 107)])
    changed = [dict(r) for r in h]
    changed[-1]["global_started_pairs"] = 105
    with pytest.raises(ValueError, match="ACCOUNTING"):
        validate(changed)


def test_receipt_paths_match_for_absolute_tempfile_and_relative_project_paths():
    path = Path("reports/experiments/example/A/F24_H1")
    assert relative_output(path) == relative_output(path.resolve()) == path
    with pytest.raises(ValueError):
        relative_output(Path.cwd().parent / "outside")


def test_corrupt_stored_origin_or_stock_is_detected_before_numerical_decode(tmp_path: Path):
    data = object.__new__(HorizonData)
    data.rows = pd.DataFrame(dict(origin_id=["o1"], session_date_et=["2021-02-01"]))
    data.plans = {2021: ({}, {"oos": np.array([True])})}
    data.symbols = tuple(f"S{i}" for i in range(20))
    f = pd.DataFrame(dict(origin_id=["o1"] * 20, ticker=list(data.symbols)))
    f.loc[19, "ticker"] = "S0"
    f.to_parquet(tmp_path / "oos_scores.parquet", index=False)
    with pytest.raises(ValueError, match="DUPLICATE"):
        verify_role(data, 2021, "oos", tmp_path)
    f.loc[19, "ticker"] = "WRONG_STOCK"
    f.to_parquet(tmp_path / "oos_scores.parquet", index=False)
    with pytest.raises(AssertionError):
        verify_role(data, 2021, "oos", tmp_path)
