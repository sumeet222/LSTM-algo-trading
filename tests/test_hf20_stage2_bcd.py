"""Focused calendar, head, label algebra and prospective-budget fixtures."""

import io
import json

import numpy as np
import pandas as pd
import pytest
import torch

from lstm_data import hf20_mag_designa as b
from lstm_data import hf20_stage2_bcd as s
from lstm_data.hf20_s4_clock import schedule, sessions


def test_known_clock_full_day_early_close_and_weekend() -> None:
    calendar = sessions("2020-11-23", "2020-12-01")
    rows = schedule(calendar, stop="2020-11-27")
    vector, following = s.clock_values(rows, calendar)
    assert vector.shape[1] == 10
    full = rows.session_date_et.eq("2020-11-23") & rows.slot.eq("09:30")
    early = rows.session_date_et.eq("2020-11-27") & rows.slot.eq("09:30")
    a, b_ = np.flatnonzero(full)[0], np.flatnonzero(early)[0]
    np.testing.assert_array_equal(vector[a, :7], vector[b_, :7])
    assert vector[a, 7] == pytest.approx(390 / 240)
    assert vector[b_, 7] == pytest.approx(210 / 240)
    assert vector[a, 8] == 0 and vector[b_, 8] == 1
    assert vector[a, 9] == pytest.approx(1 / 7)
    assert vector[b_, 9] == pytest.approx(3 / 7)
    assert (
        pd.Timestamp(following.iloc[b_]).tz_convert("America/New_York").strftime("%Y-%m-%d")
        == "2020-11-30"
    )


def test_clock_head_parameter_count_trunk_and_reload() -> None:
    old = b.model_for("MAG")
    new = s.model_for_clock()
    assert sum(p.numel() for p in new.parameters()) == 6443
    for key, value in old.lstm.state_dict().items():
        torch.testing.assert_close(value, new.lstm.state_dict()[key], rtol=0, atol=0)
    x = torch.zeros((2, 48, 16))
    known = torch.zeros((2, 10))
    known[1, 7] = 1
    new.eval()
    with torch.no_grad():
        p = new(x, known)
    assert p.shape == (2,) and torch.isfinite(p).all()
    assert float(p[1] - p[0]) == pytest.approx(float(new.head.weight.detach()[0, 39]), abs=1e-7)
    stream = io.BytesIO()
    torch.save(new.state_dict(), stream)
    stream.seek(0)
    reloaded = s.model_for_clock()
    reloaded.load_state_dict(torch.load(stream, weights_only=True))
    reloaded.eval()
    with torch.no_grad():
        torch.testing.assert_close(p, reloaded(x, known), rtol=0, atol=0)
    with pytest.raises(ValueError):
        new(x, torch.zeros((2, 9)))


def test_signed_component_identity_is_not_absolute_additivity() -> None:
    origin, close, opened, endpoint = 100.0, 102.0, 99.0, 101.0
    pieces = np.log([close / origin, opened / close, endpoint / opened])
    total = np.log(endpoint / origin)
    assert pieces.sum() == pytest.approx(total, abs=1e-14)
    assert abs(total) != pytest.approx(abs(pieces).sum())
    assert pieces[1] < 0


def test_gap_target_maturity_and_full_session_origin_are_distinct() -> None:
    origin = pd.Timestamp("2020-09-30 15:30", tz="America/New_York")
    close = origin + pd.Timedelta(minutes=30)
    next_open = pd.Timestamp("2020-10-01 09:30", tz="America/New_York")
    gap_maturity = next_open + pd.Timedelta(minutes=2)
    four_hour_maturity = next_open + pd.Timedelta(minutes=212)
    assert close.strftime("%H:%M") == "16:00"
    assert gap_maturity < four_hour_maturity
    assert not gap_maturity < b.limit("2020-09-30")
    assert gap_maturity < b.limit("2020-10-01")
    assert np.log(101 / 102) != pytest.approx(np.log(101 / 100))


def test_budget_ceiling_increase_does_not_charge_or_rewrite_history(tmp_path, monkeypatch) -> None:
    journal = tmp_path / "old.jsonl"
    text = (
        json.dumps(dict(status="COMPLETED", global_started_pairs=154, effective_ceiling=200)) + "\n"
    )
    journal.write_text(text)
    old = tmp_path / "old_budget.json"
    old.write_text("{}")
    pointer = tmp_path / "current.json"
    original = dict(
        real_journal=str(journal),
        effective_ceiling=200,
        counts_started_including_failed=True,
        budget_amendment=dict(path=str(old), sha256=b.digest(old)),
        schema_version=27,
        fit_permission=False,
    )
    pointer.write_text(json.dumps(original))
    monkeypatch.setattr(b, "POINTER", pointer)
    out = tmp_path / "new"
    out.mkdir()
    changed = s.budget_amendment(out)
    assert changed["effective_ceiling"] == 300 and changed["real_journal"] == str(journal)
    assert not changed["fit_permission"]
    assert journal.read_text() == text
    receipt = b.read(out / "budget_amendment_300.json")
    assert receipt["opening_started"] == 154 and receipt["prospective_only"]
    assert receipt["previous_pointer"] == original
    assert s.budget_amendment(out) == changed
