"""D6g chronology, certificate reuse rejection and scripted stop boundaries."""

from dataclasses import replace

import pandas as pd
import pytest
import torch

from lstm_data.baseline_authority import replay_permission
from lstm_data.baseline_fit import prepare
from lstm_data.baseline_fixtures import ridge_data
from lstm_data.baseline_ridge import adequacy, fitting_origins, windows
from lstm_data.calendar import schedule
from lstm_data.ft0_transforms import identity
from lstm_data.labels import FitWindow
from lstm_data.neural_data import IndexedOrigin, NeuralView, make_view
from lstm_data.neural_engine import SharedLSTM
from lstm_data.neural_lifecycle import EarlyStop, epoch_pass
from lstm_data.p3_domain import Permission, UniverseSpec


def curve(values):
    state = EarlyStop()
    for loss in values:
        if state.status != 'CALIBRATING':
            break
        state.observe(loss)
    return state


def test_strict_boundary_raw_minimum_reset_and_ties():
    state = curve([1., .999, .9995] + [1.] * 20)
    assert (state.selected, state.raw_epoch, state.epoch, state.status) == (
        1, 2, 12, 'PATIENCE_STOP'
    )
    state = curve([1., .999, .998] + [.998] * 10)
    assert (state.selected, state.epoch) == (3, 13)
    state = curve([1.] * 10 + [.9] + [.9] * 10)
    assert (state.selected, state.epoch) == (11, 21)
    assert curve([1., .5, .5] + [.5] * 12).selected == 2
    assert curve([1., .9995] + [1.] * 12).raw_epoch == 2


@pytest.mark.parametrize('loss', [0., 1e-300, 1.])
def test_flat_zero_near_zero_stop_not_before_12(loss):
    state = curve([loss] * 60)
    assert (state.selected, state.epoch) == (1, 12)


def test_cap_invalid_curve_and_missing_validation():
    state = curve([.99 ** i for i in range(60)])
    assert (state.epoch, state.selected, state.status) == (60, 60, 'MAX_EPOCHS_REACHED')
    for invalid in [None, float('nan'), float('inf'), -1.]:
        with pytest.raises(ValueError):
            EarlyStop().observe(invalid)
    with pytest.raises(ValueError):
        state.observe(.1)
    assert EarlyStop().selected == 0  # No valid calibration means no refit duration.


def test_actual_epoch_aggregation_16_plus_three():
    universe = UniverseSpec('SYN:LOSS', ('A', 'B', 'C', 'D', 'E'))
    days = tuple(f'SYN:DAY:{i:02d}' for i in range(19))
    values = torch.zeros(48, 16)
    rows = tuple(IndexedOrigin(day, 1, (tuple(range(48)),) * 5, (i ** .5,) * 5)
                 for i, day in enumerate(days))
    at = pd.Timestamp('2020-08-01T04:00Z')
    window = FitWindow('SYNTHETIC:LOSS', pd.Timestamp('2020-07-01T04:00Z'), at, at,
                       'INNER_TRAIN')
    view = NeuralView(universe, 'SYN:NEURAL_DATA:LOSS', values, rows, days, 'SYN:PREP',
                      window, identity(values.tolist()))
    model = SharedLSTM()
    with torch.no_grad():
        for parameter in model.parameters():
            parameter.zero_()
    previous = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        actual = epoch_pass(model, view, 1, 42)
    finally:
        torch.set_num_threads(previous)
    assert actual['sessions'] == 19
    assert actual['mean_session_mse'] == pytest.approx(9, abs=1e-6)
    assert (7.5 + 17) / 2 == 12.25  # Wrong unweighted batch-mean aggregation.


@pytest.fixture(scope='module')
def synthetic_fit_data():
    universe = UniverseSpec('SYN:NEURAL_TEST', ('AA', 'BB', 'CC', 'DD', 'EE'))
    return ridge_data(universe), replay_permission(Permission('ENGINEERING_SYNTHETIC_ONLY'))


def test_exact_calendar_tail_adequacy_and_maturity(synthetic_fit_data):
    data, permission = synthetic_fit_data
    inner, validation, full = windows('WF1', pd.Timestamp('2023-07-01T04:00Z'))
    expected = schedule('2020-07-01', '2023-06-30').index[-63:]
    assert validation.start.tz_convert('America/New_York').date() == expected[0].date()
    valid, rejected = fitting_origins(data.origins, data.universe, validation)
    assert adequacy(valid)['sessions'] == 63
    assert rejected  # Prefix origins are excluded, not substituted into validation.
    with pytest.raises(ValueError):
        adequacy(tuple(r for r in valid if r.label.plan.origin == 1))
    with pytest.raises(ValueError):
        adequacy(valid[:40])
    row = valid[-1]
    assert row.label.maturity is not None
    late = replace(row, label=replace(row.label, maturity=full.stop + pd.Timedelta(minutes=1)))
    accepted, exclusions = fitting_origins((late,), data.universe, full)
    assert not accepted and exclusions[0][1] == 'PURGED_SPLIT_BOUNDARY'
    train, _ = fitting_origins(data.origins, data.universe, inner)
    prep = prepare(data, inner, train, market=False, permission=permission, allow_synthetic=True)
    # All held-out fit observations may be extreme; inner objects must remain identical.
    altered = replace(data, stock_records=tuple(
        replace(r, value=1e6) if r.timestamp >= validation.start else r
        for r in data.stock_records
    ))
    other = prepare(altered, inner, train, market=False, permission=permission,
                    allow_synthetic=True)
    assert identity(prep) == identity(other)
    refit, _ = fitting_origins(data.origins, data.universe, full)
    fresh = prepare(data, full, refit, market=False, permission=permission, allow_synthetic=True)
    assert identity(prep) != identity(fresh)


def test_indexed_store_preserves_order_and_detects_mutation(synthetic_fit_data):
    data, permission = synthetic_fit_data
    # Two overlapping origins per day prove canonical sharing without rebuilding 74 windows.
    data = replace(data, origins=data.origins[:4])
    inner, _, _ = windows('WF1', pd.Timestamp('2023-07-01T04:00Z'))
    train, _ = fitting_origins(data.origins, data.universe, inner)
    prep = prepare(data, inner, train, market=False, permission=permission, allow_synthetic=True)
    view = make_view(data, inner, prep, permission, allow_synthetic=True)
    assert view.universe == data.universe
    assert view.batch((0, 1)).inputs.shape == (2, 2, 5, 48, 16)
    assert view.values.numel() < len(view.rows) * 5 * 48 * 16
    original = float(view.values[0, 0])
    view.values[0, 0] += 1
    with pytest.raises(ValueError, match='MUTATED'):
        view.batch((0,))
    view.values[0, 0] = original
    with pytest.raises(ValueError):
        make_view(replace(data, basis='DOCUMENTED'), inner, prep, permission, allow_synthetic=True)
    with pytest.raises(ValueError):
        make_view(data, inner, prep, permission)
    malformed = replace(data.origins[0], label=replace(data.origins[0].label, maturity=pd.NaT))
    with pytest.raises(ValueError, match='finite'):
        make_view(replace(data, origins=(malformed,)), inner, prep, permission,
                  allow_synthetic=True)
    assert bool(torch.isfinite(view.values).all())
