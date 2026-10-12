"""Safe identity-bound checkpoints, epoch recovery and isolated budget races."""

import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace

import pytest
import torch

from lstm_data.config import digest
from lstm_data.neural_artifacts import PairIdentity, PairRegistry, load_checkpoint, save_checkpoint
from lstm_data.neural_engine import SharedLSTM, clip, optimizer, seed_all
from lstm_data.neural_lifecycle import state_hash


def pair():
    return PairIdentity('SYN:TEST', 'universe', 'FT0', 'TG0', 'calendar', 'source',
                        'prep', 'config', 'code')


def test_checkpoint_stage_hash_schema_and_all_version_swaps(tmp_path):
    model = SharedLSTM()
    p = pair()
    path = tmp_path / 'final.pt'
    save_checkpoint(path, model, p, 'REFIT_FINAL', 1)
    loaded = SharedLSTM()
    assert load_checkpoint(path, loaded, p, 'REFIT_FINAL')[0] == 1
    x = torch.zeros(5, 48, 16)
    model.eval()
    assert torch.equal(model(x), loaded(x))
    for field in ['universe', 'information', 'target', 'calendar_split_cutoff',
                  'source_features_data', 'preprocess', 'model_optimizer_selection', 'code']:
        with pytest.raises(ValueError):
            load_checkpoint(path, loaded, replace(p, **{field: 'changed'}), 'REFIT_FINAL')
    with pytest.raises(ValueError):
        load_checkpoint(path, loaded, replace(p, seed=123), 'REFIT_FINAL')
    with pytest.raises(ValueError):
        load_checkpoint(path, loaded, p, 'CALIBRATION_SELECTED')
    with pytest.raises(FileExistsError):
        save_checkpoint(path, model, p, 'REFIT_FINAL', 1)
    path.write_bytes(path.read_bytes() + b'corrupt')
    with pytest.raises(ValueError):
        load_checkpoint(path, loaded, p, 'REFIT_FINAL')


def test_exact_cpu_epoch_boundary_resume(tmp_path):
    previous = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        seed_all(42)
        model = SharedLSTM()
        opt = optimizer(model)
        x = torch.ones(5, 48, 16)

        def step(m, o):
            m.train()
            o.zero_grad(set_to_none=True)
            m(x).square().mean().backward()
            clip(m)
            o.step()

        step(model, opt)
        path = tmp_path / 'epoch1.pt'
        save_checkpoint(path, model, pair(), 'REFIT_BOUNDARY', 1, optimizer=opt)
        step(model, opt)
        expected = state_hash(model)
        resumed = SharedLSTM()
        resumed_opt = optimizer(resumed)
        assert load_checkpoint(path, resumed, pair(), 'REFIT_BOUNDARY',
                               optimizer=resumed_opt)[0] == 1
        step(resumed, resumed_opt)
        assert state_hash(resumed) == expected
        assert len(resumed_opt.state) == len(opt.state)
    finally:
        torch.set_num_threads(previous)


def test_registry_ceiling_failure_time_and_simultaneous_reservation(tmp_path):
    registry = PairRegistry(tmp_path / 'registry.json')
    for i in range(39):
        p = replace(pair(), experiment=f'SYN:PAIR:{i}')
        assert registry.reserve(p)
        registry.transition(p, 'FAILED')
    assert registry.reserve(replace(pair(), experiment='SYN:PAIR:39'))
    with pytest.raises(ValueError, match='FORTY'):
        registry.reserve(replace(pair(), experiment='SYN:PAIR:40'))
    with pytest.raises(ValueError):
        registry.transition(pair(), 'COMPLETE')
    timed = PairRegistry(tmp_path / 'time.json')
    timed.reserve(pair(), 24 * 3600)
    with pytest.raises(ValueError, match='ENVELOPE'):
        timed.reserve(replace(pair(), experiment='SYN:EXCESS'))
    race = PairRegistry(tmp_path / 'race.json')

    def reserve():
        try:
            return race.reserve(pair())
        except ValueError:
            return False

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sum(pool.map(lambda _: reserve(), range(2))) == 1
    with pytest.raises(ValueError):
        PairRegistry(tmp_path / 'real.json', 'SCIENTIFIC_REAL')
    with pytest.raises(ValueError):
        replace(pair(), mode='SCIENTIFIC_REAL')


def test_complete_deduplication_and_incomplete_refit_denial(tmp_path):
    registry = PairRegistry(tmp_path / 'registry.json')
    p = pair()
    assert registry.reserve(p)
    with pytest.raises(ValueError):
        registry.transition(p, 'REFITTING')
    for state in ['CALIBRATING', 'CALIBRATED', 'REFITTING']:
        registry.transition(p, state)
    path = tmp_path / 'final.pt'
    save_checkpoint(path, SharedLSTM(), p, 'REFIT_FINAL', 1)
    registry.transition(p, 'COMPLETE', checkpoint=path)
    assert not registry.reserve(p)
    path.write_bytes(b'bad')
    with pytest.raises(ValueError):
        registry.reserve(p)


def test_parsed_tensor_schema_even_with_recomputed_transport_checksum(tmp_path):
    path = tmp_path / 'shape.pt'
    p = pair()
    save_checkpoint(path, SharedLSTM(), p, 'REFIT_FINAL', 1)
    body = torch.load(path, weights_only=True)
    body['model']['lstm.weight_ih_l0'] = torch.zeros(128, 15)
    torch.save(body, path)
    manifest_path = path.with_suffix('.manifest.json')
    manifest = json.loads(manifest_path.read_text())
    manifest['sha256'] = digest(path)
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match='TENSOR_SCHEMA'):
        load_checkpoint(path, SharedLSTM(), p, 'REFIT_FINAL')


def test_failed_calibration_cannot_transition_to_refit(tmp_path):
    registry = PairRegistry(tmp_path / 'failed.json')
    registry.reserve(pair())
    registry.transition(pair(), 'CALIBRATING')
    registry.transition(pair(), 'FAILED')
    for state in ['CALIBRATED', 'REFITTING', 'COMPLETE']:
        with pytest.raises(ValueError):
            registry.transition(pair(), state)
