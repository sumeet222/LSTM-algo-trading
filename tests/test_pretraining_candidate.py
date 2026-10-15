"""Hermetic candidate-policy/barrier/clock oracles; all prices here are synthetic."""
from __future__ import annotations

import json
import math
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from lstm_data.config import digest
from lstm_data.ft0_transforms import ORDER, robust_parameters
from lstm_data.m2 import return_moments
from lstm_data.pretraining_policy import (
    ACTIVITIES,
    CANDIDATE,
    PreparationAuthority,
    load_authority,
    local_path,
)
from lstm_data.pretraining_source import BARRIER, ConditionalHistory, read_native
from lstm_data.pretraining_store import load_candidate_view
from lstm_data.pretraining_tables import m2_moments, proxy_panel, target_moments, tg0
from lstm_data.pretraining_transforms import (
    CandidateFloors,
    CandidateScaler,
    check_candidate_window,
)
from lstm_data.stock_features import apply_component_floors
from lstm_data.stock_source import StockBar, StockCalendar, source_reason


class SyntheticFixtureAuthority(PreparationAuthority):
    """Test fixture only. No real archives or permission decisions enter these tests."""

    def ensure(self, activity: str) -> None:
        if activity not in ACTIVITIES:
            raise ValueError("MODEL_FIT_REPLAY_CONFIRMATION_AND_RESERVATION_FORBIDDEN")


def synthetic_authority(root: Path, policy: dict | None = None) -> PreparationAuthority:
    return SyntheticFixtureAuthority(root, {}, {}, policy or {}, {})


def history(root: Path, start: str = "2020-07-01", stop: str = "2020-07-02"):
    authority = synthetic_authority(root)
    calendar = StockCalendar(start, stop)
    bars = []
    for symbol in CANDIDATE:
        for step in calendar.steps:
            close = 100 + step.slot + CANDIDATE.index(symbol) * step.slot / 10
            bars.append(StockBar(symbol, step.session, step.slot, step.start, step.end,
                                 close, close + 1, close - 1, close, 100,
                                 (f"SYNTHETIC:{symbol}:{step.end}",), basis="ASSUMED",
                                 evidence_ref=authority.binding, universe=CANDIDATE,
                                 action_ref="RETROSPECTIVE_VENDOR_ADJUSTMENT_UNVERIFIED_VINTAGE"))
    return ConditionalHistory(calendar, tuple(bars), authority)


@pytest.mark.parametrize("operation", ["MODEL_FIT", "run_pair", "RIDGE_FIT", "FORECAST_ISSUE",
                                       "TRADING_REPLAY", "CONFIRMATION", "PAIR_RESERVATION"])
def test_preparation_cannot_authorize_other_activities(tmp_path, operation):
    policy, approval = tmp_path / "policy.json", tmp_path / "approval.json"
    policy.write_text("{}")
    approval.write_text("{}")
    a = PreparationAuthority(tmp_path, {"path": policy.name, "sha256": digest(policy)},
                             {"path": approval.name, "sha256": digest(approval)}, {}, {})
    with pytest.raises(ValueError, match="FORBIDDEN"):
        a.ensure(operation)


def test_pending_and_tampered_policy_rejected(tmp_path):
    p, a = tmp_path / "p.json", tmp_path / "a.json"
    p.write_text("{}")
    a.write_text('{"status":"PENDING"}')
    pref, aref = {"path": p.name, "sha256": digest(p)}, {"path": a.name, "sha256": digest(a)}
    with pytest.raises(ValueError, match="EXACT_CONDITIONAL"):
        load_authority(tmp_path, pref, aref)
    p.write_text('{"changed":true}')
    with pytest.raises(ValueError, match="HASH_CHANGED"):
        load_authority(tmp_path, pref, aref)
    with pytest.raises(ValueError, match="RELATIVE"):
        local_path(tmp_path, str(p))
    with pytest.raises(ValueError, match="OUTSIDE"):
        local_path(tmp_path, "../elsewhere")


@pytest.mark.parametrize("day", ["2020-07-01", "2020-08-31", "2021-03-12", "2021-03-15"])
@pytest.mark.parametrize("origin", [1, 2])
def test_exact_proxy_clock_and_c01_future_removal(tmp_path, day, origin):
    h = history(tmp_path, day, day)
    panel = proxy_panel(h, day, origin)
    assert panel.label_valid and all(panel.entry_valid)
    assert panel.entry_event - panel.cutoff == pd.Timedelta(minutes=3)
    assert panel.exit_event - panel.entry_event == pd.Timedelta(minutes=240)
    assert panel.maturity == panel.exit_event
    b = h.bars[CANDIDATE[0], day, origin]
    assert b.available_at is None and not b.action_verified
    assert source_reason(b, b.end) == "SOURCE_PUBLICATION_UNKNOWN"
    assert h.source_status(replace(b, basis="DOCUMENTED"), b.end) != "SOURCE_VALID"
    assert h.source_status(replace(b, available_at=b.end), b.end) != "SOURCE_VALID"
    assert h.source_status(b, b.end - pd.Timedelta(nanoseconds=1)) != "SOURCE_VALID"
    h.bars.pop((CANDIDATE[-1], day, origin + 4))
    changed = proxy_panel(h, day, origin)
    assert changed.entry_valid == panel.entry_valid
    assert not changed.label_valid and changed.maturity is None
    assert changed.entry_prices == panel.entry_prices
    assert changed.returns[-1] is None


def test_early_close_and_confirmation_no_proxy(tmp_path):
    h = history(tmp_path, "2020-11-27", "2020-11-27")
    assert len(h.calendar.steps) == 3
    with pytest.raises(ValueError, match="ELIGIBLE_PROXY_PLAN"):
        proxy_panel(h, "2020-11-27", 1)
    h = history(tmp_path, "2024-07-01", "2024-07-01")
    with pytest.raises(ValueError, match="CONFIRMATION"):
        proxy_panel(h, "2024-07-01", 1)


def test_tg0_independent_five_stock_and_zero_mad():
    r = (-.03, -.01, 0., .01, .05)
    center, mad = target_moments(r)
    assert center == 0 and mad == .01
    assert tg0(r, 1e-4) == pytest.approx(tuple(x / .0101 for x in r))
    assert tg0((.02,) * 5, 1e-4) == (0.,) * 5
    with pytest.raises(ValueError):
        tg0(r, 0.)
    with pytest.raises(ValueError):
        target_moments(r[:-1])


def test_shared_ft0_and_robust_oracles():
    p = CandidateFloors("AAPL", .002, .01, 10., 100., .003)
    v: dict[str, float | None] = {name: None for name in ORDER}
    v.update({"OC": .01, "RMS12": .001, "RMS60": .004, "RMS63": .02,
              "MOM5": .03, "MOM105": -.07, "Q1_MEAN": 120., "VOLUME_H": 250.,
              "Q2_5": 700., "Q2_60": 900.})
    f = apply_component_floors(v, p)
    assert f["M1"] == .01 / .004
    assert f["M3"] == pytest.approx(.03 / (math.sqrt(5) * .02))
    assert f["M4"] == pytest.approx(-.07 / (math.sqrt(105) * .02))
    assert f["V1"] == math.log(.002) and f["V2"] == math.log(.004)
    assert f["V3"] == math.log(.002) - math.log(.004)
    assert f["Q1"] == math.log(260 / 130) and f["Q2"] == math.log(800 / 1000)
    assert robust_parameters(np.array([1., 2., 3., 4., 5.])) == (3., 1., "MAD")
    assert robust_parameters(np.ones(5)) == (1., 1., "CONSTANT")
    center, scale, method = robust_parameters(np.array([0., 0., 0., 0., 1.]))
    assert center == 0 and scale > 0 and method == "AUDITED_POPULATION_SD"
    with pytest.raises(ValueError):
        CandidateFloors("AAPL", 0, 1, 1, 1, 1)
    with pytest.raises(ValueError):
        CandidateScaler((0.,), (1.,), ("MAD",))


def test_m2_mature_prior_sessions_not_future_panel(tmp_path):
    h = history(tmp_path, "2020-03-02", "2020-07-02")
    panels = {(d, o): proxy_panel(h, d, o) for d in h.calendar.days for o in (1, 2)
              if len(h.calendar.clock(d).hours) == 6}
    stat = m2_moments(h, panels, "AAPL", "2020-07-01", 1)
    assert stat.valid20 == 20 and stat.valid60 == 60 and stat.max_missing_run == 0
    assert stat.maturity is not None and stat.maturity < panels["2020-07-01", 1].cutoff
    before = stat
    panels.pop(("2020-07-02", 1))
    assert m2_moments(h, panels, "AAPL", "2020-07-01", 1) == before
    previous = h.calendar.prior["2020-07-01", 1][-1]
    p = panels[previous, 1]
    panels[previous, 1] = replace(p, exit_event=panels["2020-07-01", 1].exit_event)
    changed = m2_moments(h, panels, "AAPL", "2020-07-01", 1)
    assert changed.valid20 == 19 and changed.valid60 == 59
    mean, rms = return_moments((1., 2.), (1., 2., 3.))
    assert mean == 1.5 and rms == pytest.approx(math.sqrt(14 / 3))


def test_native_arrow_confirmation_filter_and_unit_tamper(tmp_path):
    # Synthetic immutable parquet spans the barrier; no protected real data used.
    folder = tmp_path / "track_a"
    folder.mkdir()
    data, meta, index = folder / "bars.parquet", folder / "meta.json", tmp_path / "source.json"
    frame = pd.DataFrame({"symbol": ["AAPL", "AAPL"],
                          "timestamp": [BARRIER - pd.Timedelta(days=1), BARRIER],
                          "open": [100., 900.], "high": [101., 901.], "low": [99., 899.],
                          "close": [100., 900.], "volume": [10., 10.], "trade_count": [1, 1],
                          "source_timeframe": ["30Min"] * 2, "feed": ["sip"] * 2,
                          "adjustment": ["split"] * 2, "provenance_id": ["SYN1", "SYN2"]})
    frame.to_parquet(data, index=False)
    params = {"feed": "sip", "adjustment": "split", "asof": "2025-06-30", "timeframe": "30Min",
              "currency": "USD", "start": "2024-06-01T00:00:00Z"}
    meta.write_text(json.dumps({"params": params, "sha256": digest(data)}))
    ref = {"data": str(data.relative_to(tmp_path)), "manifest": str(meta.relative_to(tmp_path)),
           "sha256": digest(data), "manifest_sha256": digest(meta), "params": params}
    index.write_text(json.dumps({"ordered_universe": CANDIDATE,
                                "source_by_stock": {s: [ref] for s in CANDIDATE}}))
    policy = {"source_manifest": {"path": index.name, "sha256": digest(index)}}
    a = synthetic_authority(tmp_path, policy)
    native, audit = read_native(a)
    assert len(native) == 1 and native.close.iloc[0] == 100
    assert audit["confirmation_numeric_rows"] == 0
    data.write_bytes(data.read_bytes() + b"tamper")
    with pytest.raises(ValueError, match="ARCHIVE_CHANGED"):
        read_native(a)


def test_review_loader_rejects_model_scope_before_store_access(tmp_path):
    p = tmp_path / "manifest.json"
    p.write_text(json.dumps({"MODEL_FIT_FORBIDDEN": False}))
    with pytest.raises(ValueError, match="CODE_SCOPE_OR_CACHE"):
        load_candidate_view(tmp_path, {"path": p.name, "sha256": digest(p)}, "WF1_REFIT")


def test_optional_market_requires_own_assent_and_retains_unknown(tmp_path):
    from lstm_data.market_features import MarketClose, MarketObservation, observation_reason
    from lstm_data.pretraining_market import ConditionalMarketHistory, ensure_annex

    authority = synthetic_authority(tmp_path)
    annex = tmp_path / "annex.json"
    annex.write_text('{"status":"PENDING"}')
    with pytest.raises(ValueError, match="SEPARATE_ACTUAL"):
        ensure_annex(authority, {"path": annex.name, "sha256": digest(annex)})
    calendar = StockCalendar("2020-07-01", "2020-07-01")
    s = calendar.steps[0]
    obs = MarketObservation(s.start, s.end, 100., 101., None, "UNKNOWN", "SYNTHETIC_ROW", False)
    session_close = calendar.clock(s.session).close
    assert session_close is not None
    close = MarketClose(session_close, 102., None, "UNKNOWN", "SYN_CLOSE", False)
    h = ConditionalMarketHistory(calendar, (obs,), {s.session: close})
    assert observation_reason(obs, s.end) == "PUBLICATION_UNKNOWN"
    assert h._return(s) == math.log(101 / 100)
    assert h._close(s.session, s.end) is None
    assert h.hours[s.end].available_at is None and not h.hours[s.end].splits_verified


def test_market_pure_five_channel_oracle():
    from lstm_data.market_features import market_values

    v = market_values(.01, .003, .004, .02, .03, -.04, .002, .005)
    expected = (.01 / .004, math.log(.004), math.log(.003 / .004),
                .03 / (math.sqrt(5) * .02), -.04 / (math.sqrt(20) * .02))
    assert v == pytest.approx(expected)
    with pytest.raises(ValueError, match="POSITIVE"):
        market_values(.01, .003, .004, .02, .03, -.04, 0., .005)


def test_real_candidate_rejects_legacy_synthetic_window_exception():
    from lstm_data.labels import fitting_window

    window = fitting_window("WF1", "INNER_TRAIN", fitted_at="2026-10-14T00:00:00Z")
    check_candidate_window(window)
    # The legacy helper permits this marker for toy fixtures. Genuine candidate
    # preprocessing must reject it, including shortened arbitrary fit intervals.
    for stop in (window.stop, window.stop - pd.Timedelta(days=1)):
        altered = replace(window, window_id="SYNTHETIC:arbitrary", stop=stop)
        with pytest.raises(ValueError, match="FROZEN_NONSYNTHETIC"):
            check_candidate_window(altered)
