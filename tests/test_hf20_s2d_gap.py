"""Focused gap-only masks, chronology, baselines, rank and month aggregation."""

import io

import numpy as np
import pandas as pd
import pytest
import torch

from lstm_data import hf20_s2d_gap as s


def test_masked_loss_equal_dates_not_rows_and_zero_invalid_gradient() -> None:
    mask = torch.ones(2, 20, dtype=torch.bool)
    mask[0, 10:] = False
    labels = torch.empty(2, 20)
    labels[0] = torch.expm1(torch.tensor(1.0))
    labels[1] = torch.expm1(torch.tensor(3.0))
    labels[~mask] = float("nan")
    pred = torch.zeros(2, 20, requires_grad=True)
    loss = s.masked_loss(pred, labels, mask, 1.0)
    assert float(loss.detach()) == pytest.approx(5.0)
    loss.backward()
    assert pred.grad is not None and torch.count_nonzero(pred.grad[~mask]) == 0
    alternate = labels.clone()
    alternate[~mask] = 1e30
    torch.testing.assert_close(loss.detach(), s.masked_loss(pred.detach(), alternate, mask, 1.0))
    weights = s.panel_weights(mask.numpy())
    np.testing.assert_allclose(weights.sum(1), [0.5, 0.5])
    per_day = [
        s.masked_loss(pred.detach()[i : i + 1], labels[i : i + 1], mask[i : i + 1], 1.0)
        for i in range(2)
    ]
    torch.testing.assert_close(loss.detach(), (per_day[0] + per_day[1]) / 2)
    with pytest.raises(ValueError):
        s.masked_loss(pred[:1], labels[:1], torch.zeros(1, 20, dtype=torch.bool), 1.0)


def test_gap_maturity_independent_of_four_hour_eligibility_and_early_close() -> None:
    day = "2020-07-13"
    origin = pd.Timestamp(day + " 15:30", tz="America/New_York")
    rows = pd.DataFrame(
        dict(
            source_input_eligible=[True, True],
            regular_session=[True, False],
            slot=["15:30", "12:30"],
            session_date_et=[day, day],
            eligible=[False, True],
            label_maturity_utc=[origin + pd.Timedelta(days=10)] * 2,
        )
    )
    valid = np.ones((2, 20), bool)
    first = np.array(["2020-07-01"] * 2)
    maturity = pd.Series([pd.Timestamp("2020-07-14 09:32", tz="America/New_York")] * 2)
    item = dict(start=day, cutoff="2020-07-14", embargo_after="2020-06-30")
    np.testing.assert_array_equal(s.role_positions(rows, first, valid, maturity, item), [0])
    item["cutoff"] = day
    assert not len(s.role_positions(rows, first, valid, maturity, item))


def test_recent_twenty_never_reads_current_night_or_future_and_prefix_is_locked() -> None:
    n = 23
    rows = pd.DataFrame(
        dict(
            issuance_utc=pd.date_range("2020-01-01 15:32", periods=n, tz="UTC"),
            session_date_et=pd.date_range("2020-01-01", periods=n).strftime("%Y-%m-%d"),
        )
    )
    maturity = rows.issuance_utc + pd.Timedelta(hours=18)
    valid = np.ones((n, 20), bool)
    gap = np.repeat(np.arange(n)[:, None] / 1000, 20, axis=1)
    gap[21:] = 999
    live = s.recent_live(rows, np.array([21]), np.arange(n), valid, gap, maturity)
    np.testing.assert_allclose(live, np.arange(1, 21).mean() / 1000)
    prefix = s.prefix_baselines(rows, np.arange(20), valid, gap)
    np.testing.assert_allclose(prefix["recent20"], np.arange(20).mean() / 1000)
    gap[20:] = 1e9
    unchanged = s.prefix_baselines(rows, np.arange(20), valid, gap)
    assert prefix == unchanged


def test_variable_panel_ranks_ties_and_four_over_n_chance() -> None:
    frames = []
    for day, n in [("a", 10), ("b", 20)]:
        frames.append(
            pd.DataFrame(
                dict(session_date_et=[day] * n, A_gap=np.arange(n, dtype=float), p=np.ones(n))
            )
        )
    f = pd.concat(frames, ignore_index=True)
    r = s.ranking(f, "p")
    assert np.isnan(r["magnitude_IC"]) and r["IC_valid_sessions"] == 0
    assert r["tie_rate"] == 1 and r["constant_rate"] == 1
    assert r["pair_concordance"] == pytest.approx(0.5)
    assert r["top4"] == pytest.approx(0.3) and r["chance_top4"] == pytest.approx(0.3)
    for n in [10, 19, 20]:
        assert s.membership(np.ones(n), 4, True).sum() == pytest.approx(4)
        assert s.membership(np.arange(n), n / 2, False).sum() == pytest.approx(n / 2)


def test_month_blocks_use_session_mass_with_variable_stock_counts() -> None:
    daily = pd.DataFrame(
        dict(numerator=[1.0, 3.0, 5.0], mass=[0.5, 0.5, 0.5]),
        index=["2021-01-02", "2021-01-03", "2021-02-01"],
    )
    result = s.previous.paired_months({2021: daily})[0]
    assert result["delta"] == pytest.approx(6.0)
    bins = daily.groupby(daily.index.str[:7]).sum()
    ix = np.random.default_rng(22042).integers(2, size=(400, 2))
    draws = bins.numerator.to_numpy()[ix].sum(1) / bins.mass.to_numpy()[ix].sum(1)
    assert result["low"] == pytest.approx(np.quantile(draws, 0.025))
    assert result["high"] == pytest.approx(np.quantile(draws, 0.975))


def test_own_gap_inverse_smear_and_plain_model_reload() -> None:
    model = s.b.model_for("MAG")
    assert sum(p.numel() for p in model.parameters()) == 6433
    assert model.lstm.input_size == 16 and model.head.in_features == 32
    model.eval()
    x = torch.zeros(2, 48, 16)
    with torch.no_grad():
        p = model(x)
    stream = io.BytesIO()
    torch.save(model.state_dict(), stream)
    stream.seek(0)
    reload = s.b.model_for("MAG")
    reload.load_state_dict(torch.load(stream, weights_only=True))
    reload.eval()
    with torch.no_grad():
        torch.testing.assert_close(p, reload(x), rtol=0, atol=0)
    z = np.array([-1.0, 0.0, 1.0])
    scale = 0.004
    c = 1.3
    np.testing.assert_allclose(s.previous.raw_decode(z, scale), scale * np.expm1(np.maximum(z, 0)))
    np.testing.assert_allclose(s.c3.decode(z, scale, c), scale * np.maximum(0, np.exp(z) * c - 1))


def test_gap_key_frame_retains_canonical_variable_stocks_and_maturity() -> None:
    origin = pd.date_range("2020-07-13 19:30", periods=2, tz="UTC")
    rows = pd.DataFrame(
        dict(
            origin_id=["a", "b"],
            session_date_et=["2020-07-13", "2020-07-14"],
            slot=["15:30"] * 2,
            entry_end_utc=origin,
            issuance_utc=origin + pd.Timedelta(minutes=2),
        )
    )
    valid = np.ones((2, 20), bool)
    valid[0, 10:] = False
    gap = np.full((2, 20), 0.01)
    gap[~valid] = np.nan
    maturity = pd.Series(origin + pd.Timedelta(hours=18, minutes=2))
    f = s.gap_frame(rows, np.array([0, 1]), valid, gap, maturity)
    assert len(f) == 30 and f.groupby("session_date_et").ticker.size().tolist() == [10, 20]
    assert f.ticker.tolist() == list(s.b.SYMBOLS[:10]) + list(s.b.SYMBOLS)
    np.testing.assert_allclose(f.groupby("session_date_et").weight.sum(), [0.5, 0.5])
    assert str(f.gap_maturity_utc.dt.tz) == "UTC"
