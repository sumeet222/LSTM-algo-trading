"""MC0 mathematical, causal D7, complete-session and alignment oracles."""

import math
from dataclasses import replace

import pandas as pd
import pytest
import torch

from lstm_data.baseline_authority import replay_permission
from lstm_data.baseline_fit import prepare
from lstm_data.baseline_fixtures import ridge_data
from lstm_data.baseline_ridge import fitting_origins, windows
from lstm_data.neural_engine import (
    SessionBatch,
    SharedLSTM,
    batch_prediction,
    seed_all,
    session_losses,
)
from lstm_data.neural_market import MarketEvidence, MarketStamp, market_data_identity, market_input
from lstm_data.p3_domain import Permission, UniverseSpec


@pytest.fixture(scope="module", autouse=True)
def cpu_threads():
    previous = torch.get_num_threads()
    torch.set_num_threads(1)
    yield
    torch.set_num_threads(previous)


@pytest.fixture(scope="module")
def market_case():
    permission = replay_permission(Permission("ENGINEERING_SYNTHETIC_ONLY"))
    universe = UniverseSpec("SYN:MARKET_TEST", ("AA", "BB", "CC", "DD", "EE"))
    data = ridge_data(universe)
    vectors = tuple(
        replace(
            v, values=(float(i % 7), float(i % 11), float(i % 13), float(i % 17), float(i % 19))
        )
        for i, v in enumerate(data.market_vectors)
    )
    data = replace(data, market_vectors=vectors)
    history = MarketEvidence(
        "SYN:MKT_A",
        vectors,
        tuple(MarketStamp(v.timestamp, v.timestamp, v.timestamp, v.evidence_ids) for v in vectors),
    )
    inner, _, _ = windows("WF1", pd.Timestamp("2023-07-01T04:00Z"))
    inner = replace(inner, fitted_at=inner.stop)
    train, _ = fitting_origins(data.origins, universe, inner)
    prep = prepare(data, inner, train, market=True, permission=permission, allow_synthetic=True)
    row = data.origins[-1].inputs
    return data, history, prep, row, permission


def test_mc0_count_forward_axis_dropout_peer_and_gradient():
    seed_all(42)
    model = SharedLSTM(21)
    assert sum(p.numel() for p in model.parameters()) == 7073
    x = torch.randn(5, 48, 21, requires_grad=True)
    model.eval()
    y = model(x)
    assert y.shape == (5,) and torch.equal(y, model(x))
    assert torch.allclose(y, torch.cat([model(v[None]) for v in x]), atol=1e-7)
    order = [4, 0, 1, 2, 3]
    assert torch.allclose(model(x[order]), y[order], atol=1e-7)
    changed = x.detach().clone()
    changed[0] += 1
    assert torch.equal(model(changed)[1:], y[1:])
    assert not torch.allclose(model(x.flip(1)), y)
    other = x.detach().clone()
    other[..., 16:] += 0.7
    assert not torch.allclose(model(other), y)
    y.square().sum().backward()
    assert x.grad is not None
    assert x.grad[..., :16].abs().sum() > 0 and x.grad[..., 16:].abs().sum() > 0
    model.train()
    assert not torch.equal(model(x), model(x))
    assert model.lstm.dropout == 0 and model.dropout.p == 0.1
    with pytest.raises(ValueError):
        model(torch.zeros(5, 47, 21))
    with pytest.raises(ValueError):
        model(x.double())


def test_market_sentinel_and_zero_masks(market_case):
    data, history, prep, row, permission = market_case
    processed, trace = market_input(row, prep, history, permission)
    assert trace
    m = processed.market
    assert m is not None and m.values is not None and prep.market_scaler is not None
    lookup = {v.timestamp: v for v in history.vectors}
    for s, value in zip(row.stock.steps, m.values):
        raw = lookup[s.end].values
        assert raw is not None
        assert value == prep.market_scaler.transform(raw)[0]
    times = {row.stock.steps[3].end, row.stock.steps[7].end}
    vectors = tuple(
        replace(v, values=None, reason="MISSING_SPY_SOURCE", evidence_ids=())
        if v.timestamp in times
        else v
        for v in history.vectors
    )
    stamps = tuple(
        replace(s, period_end=None, available_at=None, evidence_ids=())
        if s.timestamp in times
        else s
        for s in history.stamps
    )
    missing = replace(history, vectors=vectors, stamps=stamps)
    filled, changed_trace = market_input(
        row, replace(prep, market_vectors=vectors), missing, permission
    )
    assert filled.market is not None and filled.market.values is not None
    assert sum(filled.market.valid_mask) == 46 and changed_trace != trace
    assert filled.market.values[3] == (0.0,) * 5 and filled.market.values[7] == (0.0,) * 5
    stocks = torch.tensor(filled.stock.values)
    markets = torch.tensor(filled.market.values)
    joined = torch.cat((stocks, markets[None].expand(5, -1, -1)), dim=-1)
    assert joined.shape == (5, 48, 21)
    assert torch.equal(joined[..., :16], stocks)
    assert torch.equal(joined[..., 16:], markets[None].expand(5, -1, -1))
    assert market_data_identity(
        replace(data, market_vectors=vectors), missing
    ) != market_data_identity(data, history)
    third = row.stock.steps[11].end
    bad_vectors = tuple(
        replace(v, values=None, reason="MISSING_SPY_SOURCE", evidence_ids=())
        if v.timestamp == third
        else v
        for v in vectors
    )
    bad_stamps = tuple(
        replace(s, period_end=None, available_at=None, evidence_ids=())
        if s.timestamp == third
        else s
        for s in stamps
    )
    with pytest.raises(ValueError, match="46_OF_48"):
        market_input(
            row,
            replace(prep, market_vectors=bad_vectors),
            replace(missing, vectors=bad_vectors, stamps=bad_stamps),
            permission,
        )


@pytest.mark.parametrize("kind", ["unknown", "late", "future", "nat", "conflict", "stale"])
def test_publication_failures_before_forward(market_case, kind):
    _, history, prep, row, permission = market_case
    endpoint = row.stock.steps[-1].end

    def change(s):
        if s.timestamp != endpoint:
            return s
        if kind == "unknown":
            return replace(s, available_at=None)
        if kind == "late":
            return replace(s, available_at=endpoint + pd.Timedelta(nanoseconds=1))
        if kind == "future":
            return replace(s, period_end=endpoint + pd.Timedelta(seconds=1))
        if kind == "nat":
            return replace(s, available_at=pd.NaT)
        if kind == "conflict":
            return replace(s, evidence_ids=("SYN:FOREIGN",))
        return replace(s, period_end=endpoint - pd.Timedelta(minutes=91))

    bad = replace(history, stamps=tuple(change(s) for s in history.stamps))
    with pytest.raises(ValueError):
        market_input(row, prep, bad, permission)


def test_bad_endpoint_schedule_preprocess_and_permissions(market_case):
    _, history, prep, row, permission = market_case
    end = row.stock.steps[-1].end
    vectors = tuple(
        replace(v, values=None, reason="MISSING_SPY_SOURCE", evidence_ids=())
        if v.timestamp == end
        else v
        for v in history.vectors
    )
    stamps = tuple(
        replace(s, period_end=None, available_at=None, evidence_ids=()) if s.timestamp == end else s
        for s in history.stamps
    )
    with pytest.raises(ValueError):
        market_input(
            row,
            replace(prep, market_vectors=vectors),
            replace(history, vectors=vectors, stamps=stamps),
            permission,
        )
    with pytest.raises(ValueError):
        market_input(
            replace(row, stock=replace(row.stock, steps=row.stock.steps[:-1])),
            prep,
            history,
            permission,
        )
    with pytest.raises(ValueError):
        market_input(row, prep, history, Permission("SCIENTIFIC_REAL"))
    assert prep.market_floors is not None and prep.market_scaler is not None
    with pytest.raises(ValueError):
        late_window = replace(prep.market_floors.window, fitted_at=end + pd.Timedelta(seconds=1))
        market_input(
            row,
            replace(
                prep,
                market_floors=replace(prep.market_floors, window=late_window),
                market_scaler=replace(prep.market_scaler, window=late_window),
            ),
            history,
            permission,
        )
    with pytest.raises(ValueError):
        market_input(row, prep, history, permission, "FORGED")


def test_mc0_session_loss_oracle():
    pred = torch.tensor(
        [[[math.sqrt(2)] * 5, [math.sqrt(6)] * 5], [[math.sqrt(10)] * 5, [0.0] * 5]]
    )
    mask = torch.tensor([[True, True], [True, False]])
    batch = SessionBatch(
        ("SYN:A", "SYN:B"), torch.zeros(2, 2, 5, 48, 21), torch.zeros_like(pred), mask
    )
    assert session_losses(pred, batch.targets, mask).mean().item() == pytest.approx(7, abs=1e-6)
    assert batch_prediction(SharedLSTM(21), batch).shape == (2, 2, 5)


def test_market_view_alignment_epoch_weighting_and_mutation(market_case):
    from lstm_data.ft0_transforms import identity
    from lstm_data.labels import FitWindow
    from lstm_data.neural_data import IndexedOrigin, NeuralView
    from lstm_data.neural_lifecycle import epoch_pass
    from lstm_data.neural_market import MarketIndex, MarketNeuralView, make_market_view

    data, history, prep, _, permission = market_case
    subset = replace(data, origins=data.origins[:4])
    view = make_market_view(subset, prep.window, prep, permission, history, allow_synthetic=True)
    batch = view.batch((0, 1))
    assert batch.inputs.shape == (2, 2, 5, 48, 21)
    plain = view.stock.batch((0, 1))
    assert torch.equal(batch.inputs[..., :16], plain.inputs)
    for i, day in enumerate(batch.ids):
        for r in view.market_rows:
            if r.session == day:
                expected = view.market_values[torch.tensor(r.indices)]
                assert torch.equal(
                    batch.inputs[i, r.origin - 1, :, :, 16:], expected[None].expand(5, -1, -1)
                )
    view.market_values[0, 0] += 1
    with pytest.raises(ValueError, match="MUTATED"):
        view.batch((0,))
    view.market_values[0, 0] -= 1
    days = tuple(f"SYN:DAY:{i:02d}" for i in range(19))
    values = torch.zeros(48, 16)
    rows = tuple(
        IndexedOrigin(day, 1, (tuple(range(48)),) * 5, (math.sqrt(i),) * 5)
        for i, day in enumerate(days)
    )
    at = pd.Timestamp("2020-08-01T04:00Z")
    window = FitWindow("SYNTHETIC:LOSS", pd.Timestamp("2020-07-01T04:00Z"), at, at, "INNER_TRAIN")
    stock = NeuralView(
        data.universe,
        "SYN:NEURAL_DATA:LOSS",
        values,
        rows,
        days,
        "SYN:PREP",
        window,
        identity(values.tolist()),
    )
    m = torch.zeros(48, 5)
    mr = tuple(MarketIndex(day, 1, tuple(range(48)), (True,) * 48, "SYN:TRACE") for day in days)
    joined = MarketNeuralView(
        stock, m, mr, "SYN:PREP", "SYN:NEURAL_MARKET_DATA:LOSS", identity([m.tolist(), mr])
    )
    for architecture in ("MC0", "MC1"):
        from lstm_data.neural_models import create_model

        model = create_model(architecture)
        with torch.no_grad():
            for p in model.parameters():
                p.zero_()
        result = epoch_pass(model, joined, 1, 42)
        assert result["mean_session_mse"] == pytest.approx(9, abs=1e-6)
        assert result["sessions"] == 19
        if architecture == "MC1":
            assert result["gate"]["positive"]


@pytest.mark.parametrize("architecture", ["MC0", "MC1"])
def test_forecast_checkpoint_source_swap_and_alternate_order(market_case, tmp_path, architecture):
    from lstm_data.baseline_fixtures import feature_input
    from lstm_data.config import digest
    from lstm_data.neural_artifacts import (
        PairIdentity,
        PairRegistry,
        load_checkpoint,
        save_checkpoint,
    )
    from lstm_data.neural_lifecycle import (
        EarlyStop,
        PairRun,
        code_identity,
        forecast_scores,
        run_pair,
    )
    from lstm_data.neural_market import market_preparation_identity
    from lstm_data.neural_market_audit import fabricated_history
    from lstm_data.neural_models import create_model

    data, history, prep, _, permission = market_case
    pair = PairIdentity(
        "SYN:MC_TEST",
        data.universe.universe_id,
        "FT0_D7_" + architecture,
        "TG0",
        "SYN:CUTOFF",
        market_data_identity(data, history),
        market_preparation_identity(prep),
        "SYN:CONFIG",
        code_identity(),
    )
    model = create_model(architecture)
    path = tmp_path / "refit_final.pt"
    save_checkpoint(path, model, pair, "REFIT_FINAL", 1)
    registry = PairRegistry(tmp_path / "synthetic_pair_registry.json")
    registry.reserve(pair)
    for state in ("CALIBRATING", "CALIBRATED", "REFITTING", "COMPLETE"):
        registry.transition(pair, state, checkpoint=path if state == "COMPLETE" else None)
    run = PairRun(
        {
            "refit_preparation": market_preparation_identity(prep),
            "final_checkpoint": {"sha256": digest(path)},
        },
        prep,
        pair,
        path,
        history,
    )
    row = feature_input(data.universe, day="2023-07-20")
    later = replace(
        fabricated_history(tuple(s.end for s in row.stock.steps)), version=history.version
    )
    f = forecast_scores(run, row, permission, market_history=later)
    assert f == forecast_scores(run, row, permission, market_history=later) and len(f.scores) == 5
    assert f.universe.symbols == ("AA", "BB", "CC", "DD", "EE")
    with pytest.raises(ValueError):
        load_checkpoint(
            path, create_model("MC1" if architecture == "MC0" else "MC0"), pair, "REFIT_FINAL"
        )
    for field in (
        "source_features_data",
        "preprocess",
        "model_optimizer_selection",
        "code",
        "universe",
        "calendar_split_cutoff",
    ):
        with pytest.raises(ValueError):
            load_checkpoint(
                path,
                create_model(architecture),
                replace(pair, **{field: "SYN:CHANGED"}),
                "REFIT_FINAL",
            )
    v = history.vectors[0]
    assert v.values is not None
    altered = replace(
        history, vectors=(replace(v, values=(123.0,) + v.values[1:]),) + history.vectors[1:]
    )
    with pytest.raises(ValueError, match="REBUILD"):
        forecast_scores(run, row, permission, market_history=altered)
    changed_stamp = replace(
        history.stamps[0], period_end=history.stamps[0].timestamp - pd.Timedelta(seconds=1)
    )
    clock_changed = replace(history, stamps=(changed_stamp,) + history.stamps[1:])
    with pytest.raises(ValueError, match="REBUILD"):
        forecast_scores(run, row, permission, market_history=clock_changed)
    assert prep.market_scaler is not None
    changed_scaler = replace(prep.market_scaler, evidence_ref="SYN:CORRECTED_SCALER")
    with pytest.raises(ValueError):
        forecast_scores(
            replace(run, preparation=replace(prep, market_scaler=changed_scaler)),
            row,
            permission,
            market_history=later,
        )
    reordered = UniverseSpec("SYN:REORDERED", tuple(reversed(data.universe.symbols)))
    with pytest.raises(ValueError):
        forecast_scores(run, replace(row, universe=reordered), permission, market_history=later)
    curve = EarlyStop()
    for value in (1.0, 0.9995) + (1.0,) * 10:
        curve.observe(value)
    assert (curve.selected, curve.raw_epoch, curve.epoch) == (1, 2, 12)
    with pytest.raises(ValueError):
        run_pair(
            data,
            "WF1",
            prep.window.fitted_at,
            permission,
            tmp_path / "real",
            architecture=architecture,
            market_history=history,
            mode="SCIENTIFIC_REAL",
        )
    assert not (tmp_path / "real").exists()
    # A later, irrelevant fabricated vector cannot replace any historical step.
    future_time = row.stock.steps[-1].end + pd.Timedelta(hours=1)
    future = replace(fabricated_history((future_time,)), version=history.version)
    assert forecast_scores(run, row, permission, market_history=later.extend(future)) == f


@pytest.mark.parametrize("architecture", ["MC0", "MC1"])
def test_market_epoch_boundary_resume(tmp_path, architecture):
    from lstm_data.neural_artifacts import PairIdentity, load_checkpoint, save_checkpoint
    from lstm_data.neural_engine import clip, optimizer
    from lstm_data.neural_lifecycle import state_hash
    from lstm_data.neural_models import create_model

    p = PairIdentity(
        "SYN:RESUME",
        "SYN:UNIVERSE",
        "FT0_D7_" + architecture,
        "TG0",
        "clock",
        "data",
        "prep",
        "config",
        "code",
    )
    seed_all(42)
    model = create_model(architecture)
    opt = optimizer(model)
    stock = torch.randn(2, 5, 48, 16)
    m = torch.randn(2, 48, 5)
    x = torch.cat((stock, m[:, None].expand(-1, 5, -1, -1)), dim=-1).reshape(10, 48, 21)

    def step(model, opt):
        model.train()
        opt.zero_grad(set_to_none=True)
        (model(x) - torch.arange(10.0) * 0.1).square().mean().backward()
        clip(model)
        opt.step()

    step(model, opt)
    path = tmp_path / "boundary.pt"
    save_checkpoint(path, model, p, "REFIT_BOUNDARY", 1, optimizer=opt)
    step(model, opt)
    expected = state_hash(model)
    loaded = create_model(architecture)
    resumed = optimizer(loaded)
    load_checkpoint(path, loaded, p, "REFIT_BOUNDARY", optimizer=resumed)
    step(loaded, resumed)
    assert state_hash(loaded) == expected


def test_market_fit_prefix_freeze_shape_conflicts_and_permission(market_case, tmp_path):
    from lstm_data.neural_market import market_preparation_identity
    from lstm_data.neural_market_audit import audit
    from lstm_data.neural_models import create_model, trace_model

    data, history, prep, row, permission = market_case
    altered = replace(
        data,
        market_vectors=tuple(
            replace(v, values=(1e6,) * 5) if v.timestamp >= prep.window.stop else v
            for v in data.market_vectors
        ),
    )
    train, _ = fitting_origins(altered.origins, data.universe, prep.window)
    other = prepare(
        altered, prep.window, train, market=True, permission=permission, allow_synthetic=True
    )
    assert market_preparation_identity(other) == market_preparation_identity(prep)
    duplicate = replace(history, vectors=history.vectors + (history.vectors[0],))
    with pytest.raises(ValueError, match="UNIQUE"):
        duplicate.validate()
    for steps in (row.stock.steps[:-1], row.stock.steps + (row.stock.steps[-1],)):
        with pytest.raises(ValueError):
            market_input(
                replace(row, stock=replace(row.stock, steps=steps)), prep, history, permission
            )
    processed, trace = market_input(row, prep, history, permission)
    assert processed.market is not None and processed.market.values is not None
    x = torch.cat(
        (
            torch.tensor(processed.stock.values),
            torch.tensor(processed.market.values)[None].expand(5, -1, -1),
        ),
        dim=-1,
    )
    for architecture in ("MC0", "MC1"):
        model = create_model(architecture)
        model.train()
        result = trace_model(model, x, "SYN:TRACE:" + trace)
        assert model.training and len(result["scores"][0]) == 5
        assert result["provenance"] == "SYN:TRACE:" + trace
    bad = torch.zeros(1, 2, 5, 48, 21)
    bad[0, 0, 1, 0, 16] = 1
    with pytest.raises(ValueError, match="SHARED"):
        SessionBatch(
            ("SYN:DAY",), bad, torch.zeros(1, 2, 5), torch.tensor([[True, False]])
        ).validate()
    with pytest.raises(ValueError):
        SessionBatch(
            ("SYN:DAY",),
            torch.zeros(1, 2, 5, 48, 22),
            torch.zeros(1, 2, 5),
            torch.tensor([[True, False]]),
        ).validate()
    with pytest.raises(ValueError):
        create_model("MC2")
    with pytest.raises(ValueError):
        audit(tmp_path / "real", "SCIENTIFIC_REAL")
    assert not (tmp_path / "real").exists()


def test_training_constant_market_channel_retains_novelty_flag(market_case):
    data, history, prep, row, permission = market_case
    vectors = tuple(
        replace(v, values=((3.0 if v.timestamp < prep.window.stop else 4.0),) + v.values[1:])
        for v in history.vectors
        if v.values is not None
    )
    changed = replace(data, market_vectors=vectors)
    train, _ = fitting_origins(changed.origins, changed.universe, prep.window)
    fitted = prepare(
        changed, prep.window, train, market=True, permission=permission, allow_synthetic=True
    )
    evidence = replace(history, version="SYN:MKT_NOVEL", vectors=vectors)
    processed, _ = market_input(row, fitted, evidence, permission)
    assert fitted.market_scaler is not None and fitted.market_scaler.methods[0] == "CONSTANT"
    assert processed.market is not None and processed.market.values is not None
    assert 0 in processed.market.novel_constant_channels
    assert all(value[0] == 0.0 for value in processed.market.values)
