"""Small scientific-oracle suite for the four new controlled task families."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import torch

from lstm_data.config import fingerprint
from lstm_data.dm_quantile_loss import terms
from lstm_data.hf20_ranking import origin_weights
from lstm_data.hf20_s5s9 import ARMS, model_for, row_objective
from lstm_data.hf20_s5s9_metrics import (
    auc,
    average_precision,
    control_raw,
    decode,
    fit_control,
    labels,
    make_frame,
)
from lstm_data.hf20_s5s9_report import verify_frame
from lstm_data.objective_screen_loss import classes

RECIPE = dict(t2_scale=0.7, epsilon=1e-4, magnitude_scale=0.01, event_cutoff=2.0)


@pytest.mark.parametrize("arm", ARMS)
def test_loss_export_independent_oracle_and_dimensions(arm: str) -> None:
    rng = np.random.default_rng(501)
    r = rng.normal(0, 0.01, (4, 20))
    mid = np.median(r, axis=1, keepdims=True)
    y = (r - mid) / (np.median(abs(r - mid), axis=1, keepdims=True) + RECIPE["epsilon"])
    raw = rng.normal(size=(4, 20, 3) if arm in ("EVENT", "QUANTILE") else (4, 20)).astype(
        np.float32
    )
    t = pd.date_range("2021-01-04 15:30", periods=4, freq="h", tz="UTC")
    rows = pd.DataFrame(
        dict(
            origin_id=t.astype(str),
            session_date_et=["2021-01-04"] * 3 + ["2021-01-05"],
            slot=["10:30"] * 4,
            category=["INTRADAY"] * 4,
            entry_end_utc=t,
            exit_end_utc=t + pd.Timedelta(hours=4),
            label_maturity_utc=t + pd.Timedelta(hours=4, minutes=2),
        )
    )
    f = make_frame(rows, tuple(f"S{i}" for i in range(20)), r, y, raw, arm, RECIPE, "oos")
    verify_frame(f, arm, RECIPE)
    np.testing.assert_allclose(
        f.groupby("origin_id", sort=False).weight.sum(), [1 / 6] * 3 + [0.5], rtol=0, atol=1e-15
    )
    model = model_for(arm)
    expected = 7201 if arm == "META-T2R" else 6499 if arm in ("EVENT", "QUANTILE") else 6433
    assert sum(p.numel() for p in model.parameters()) == expected
    assert model.lstm.num_layers == 1 and model.dropout.p == 0.1
    assert model(torch.zeros(2, 48, model.input_dim)).shape == (
        (2, 3) if arm in ("EVENT", "QUANTILE") else (2,)
    )


def test_event_labels_preserve_e1_boundaries_and_natural_ce() -> None:
    y = np.array([-3.0, -2.0, 0.0, 2.0, 3.0])
    np.testing.assert_array_equal(labels(y, 2.0), classes(y, 2.0))
    raw = torch.zeros(1, 5, 3, dtype=torch.float64)
    loss = row_objective(raw, torch.zeros(1, 5), torch.from_numpy(y[None]), "EVENT", RECIPE)
    np.testing.assert_allclose(loss, np.log(3), atol=1e-15)
    p = decode(raw.numpy(), "EVENT", RECIPE)
    np.testing.assert_allclose(p["p_ANY"], 2 / 3, atol=1e-15)


def test_quantile_original_qr1_loss_and_ordering() -> None:
    from lstm_data.hf20_s5s9_run import Selector

    selector = Selector()
    assert selector.observe(1.0)
    assert selector.observe(0.999)  # Historical D6g includes exact 0.1% improvements.
    raw = torch.linspace(-3, 3, 120, dtype=torch.float64).reshape(1, 2, 20, 3)
    y = torch.linspace(-8, 8, 40, dtype=torch.float64).reshape(1, 2, 20)
    original = terms(raw, y, torch.ones(1, 2, dtype=torch.bool), "QR1", RECIPE["t2_scale"])["loss"]
    actual = row_objective(
        raw.reshape(2, 20, 3), torch.zeros(2, 20), y.reshape(2, 20), "QUANTILE", RECIPE
    )
    torch.testing.assert_close(actual, original.reshape(2, 20), rtol=0, atol=0)
    result = decode(raw.numpy().reshape(2, 20, 3), "QUANTILE", RECIPE)
    assert (result["quantiles_y_05"] < result["quantiles_y_50"]).all()
    assert (result["quantiles_y_50"] < result["quantiles_y_95"]).all()


def test_magnitude_inverse_clamp_does_not_change_optimized_target() -> None:
    raw = np.array([[-1.0, 0.0, np.log(2)]])
    result = decode(raw, "MAG", RECIPE)
    np.testing.assert_allclose(result["prediction_A"], [[0, 0, 0.01]], atol=1e-15)
    loss = row_objective(torch.from_numpy(raw), torch.zeros(1, 3), torch.zeros(1, 3), "MAG", RECIPE)
    assert float(loss[0, 0]) == 1


def test_weighted_event_ties_and_same_task_prefix_controls() -> None:
    actual = np.array([0.0, 1.0, 0.0, 1.0])
    w = np.array([0.1, 0.2, 0.3, 0.4])
    score = np.zeros(4)
    assert average_precision(actual, score, w) == pytest.approx(0.6)
    assert auc(actual, score, w) == pytest.approx(0.5)
    r = np.tile(np.arange(1, 21) * 0.001, (4, 1))
    y = np.tile(np.linspace(-4, 4, 20), (4, 1))
    sigma = np.tile(np.linspace(0.001, 0.02, 20), (4, 1))
    days = np.array(["a", "a", "a", "b"])
    for arm in ("MAG", "EVENT", "QUANTILE"):
        fit = fit_control(r, y, sigma, days, arm, RECIPE, "GLOBAL")
        raw = control_raw(fit, sigma, arm, "GLOBAL", RECIPE)
        assert np.isfinite(raw).all()
        if arm == "MAG":
            expected = np.average(
                np.log1p(r / RECIPE["magnitude_scale"]),
                weights=np.broadcast_to(origin_weights(days)[:, None] / 20, r.shape),
            )
            np.testing.assert_allclose(raw, expected, atol=1e-15)


def test_no_live_authority_stops_before_source_loading(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import lstm_data.hf20_s5s9_run as run

    def forbidden() -> None:
        raise AssertionError("source must not load")

    monkeypatch.setattr(run, "Data", forbidden)
    with pytest.raises(FileNotFoundError):
        run.run(tmp_path)
    assert not (tmp_path / "EXECUTION_STARTED.json").exists()


def test_next_start_rejected_until_previous_stage_completed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import lstm_data.hf20_s5s9_run as run

    journal = tmp_path / "synthetic.jsonl"
    row = dict(sequence=1, previous=fingerprint([]), run_id=run.RUNS[0], status="STARTED")
    journal.write_text(json.dumps(row) + "\n")
    before = journal.read_bytes()
    (tmp_path / "prior_registry_pointer.json").write_text("{}")
    monkeypatch.setattr(run, "JOURNAL", journal)
    monkeypatch.setattr(run, "ensure", lambda _: {})
    with pytest.raises(ValueError, match="SEQUENTIAL_GATE_NO_RETRY"):
        run.event(tmp_path, run.RUNS[1], "STARTED", {})
    assert journal.read_bytes() == before
