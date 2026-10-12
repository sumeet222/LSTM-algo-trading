"""Hermetic source-version/permission and model-to-P3 boundary checks."""

from dataclasses import replace

import pandas as pd
import pytest
import torch

from lstm_data.baseline_authority import replay_permission
from lstm_data.baseline_fit import prepare
from lstm_data.baseline_fixtures import feature_input, ridge_data
from lstm_data.baseline_ridge import fitting_origins, windows
from lstm_data.config import digest
from lstm_data.neural_artifacts import PairIdentity, PairRegistry, load_checkpoint, save_checkpoint
from lstm_data.neural_audit import audit
from lstm_data.neural_data import data_identity, preparation_identity
from lstm_data.neural_engine import SharedLSTM, seed_all
from lstm_data.neural_lifecycle import PairRun, code_identity, forecast_scores, run_pair
from lstm_data.p3_domain import Permission, UniverseSpec


def test_real_cli_context_denied_before_any_dataset_or_output(tmp_path):
    with pytest.raises(ValueError, match='P4_3_BLOCKED'):
        audit(tmp_path / 'real', 'SCIENTIFIC_REAL')
    assert not (tmp_path / 'real').exists()
    with pytest.raises(ValueError):
        UniverseSpec('SYN:SIX', ('A', 'B', 'C', 'D', 'E', 'F'))


def test_alternate_universe_final_stage_prediction_and_source_swap(tmp_path):
    permission = replay_permission(Permission('ENGINEERING_SYNTHETIC_ONLY'))
    universe = UniverseSpec('SYN:ALT_NEURAL', ('MSFT', 'BAC', 'MRK', 'COST', 'HON'))
    data = ridge_data(universe)
    _, _, window = windows('WF1', pd.Timestamp('2023-07-01T04:00Z'))
    rows, _ = fitting_origins(data.origins, universe, window)
    prep = prepare(data, window, rows, market=False, permission=permission, allow_synthetic=True)
    p = PairIdentity('SYN:MOCK_COMPLETE', universe.universe_id, 'FT0', 'TG0', 'calendar',
                     data_identity(data), preparation_identity(prep), 'config', code_identity())
    seed_all(42)
    model = SharedLSTM()
    path = tmp_path / 'final.pt'
    save_checkpoint(path, model, p, 'REFIT_FINAL', 1)
    registry = PairRegistry(tmp_path / 'synthetic_pair_registry.json')
    registry.reserve(p)
    for state in ['CALIBRATING', 'CALIBRATED', 'REFITTING', 'COMPLETE']:
        registry.transition(p, state, checkpoint=path if state == 'COMPLETE' else None)
    run = PairRun({'refit_preparation': preparation_identity(prep),
                   'final_checkpoint': {'sha256': digest(path)}},
                  prep, p, path)
    input_row = feature_input(universe, day='2023-07-20')
    first = forecast_scores(run, input_row, permission)
    second = forecast_scores(run, input_row, permission)
    assert len(first.scores) == 5 and first == second
    assert first.universe.symbols == universe.symbols
    with pytest.raises(ValueError):
        forecast_scores(replace(run, pair=replace(p, universe='reordered')), input_row, permission)
    with pytest.raises(ValueError):
        forecast_scores(replace(run, pair=replace(p, code='stale')), input_row, permission)
    # One changed raw cell changes the dataset identity even if a constant scaler maps it to zero.
    origin = data.origins[0]
    raw = [[list(step) for step in stock] for stock in origin.inputs.stock.raw_values]
    raw[0][0][0] = .125
    corrected = tuple(tuple(tuple(step) for step in stock) for stock in raw)
    changed_row = replace(origin, inputs=replace(origin.inputs,
                                                stock=replace(origin.inputs.stock,
                                                              raw_values=corrected)))
    changed = replace(data, origins=(changed_row,) + data.origins[1:])
    assert data_identity(changed) != data_identity(data)
    with pytest.raises(ValueError):
        load_checkpoint(path, SharedLSTM(), replace(p, source_features_data=data_identity(changed)),
                        'REFIT_FINAL')
    with pytest.raises(ValueError):
        run_pair(replace(data, basis='DOCUMENTED'), 'WF1', window.fitted_at,
                 permission, tmp_path / 'observed')
    with pytest.raises(ValueError):
        run_pair(data, 'WF1', window.fitted_at, permission, tmp_path / 'historical',
                 mode='SCIENTIFIC_REAL')
    broken = replace(input_row, available_at=tuple(tuple((None,) * 16 for _ in range(48))
                                                   for _ in range(5)))
    with pytest.raises(ValueError):
        forecast_scores(run, broken, permission)
    assert torch.get_default_dtype() == torch.float32
