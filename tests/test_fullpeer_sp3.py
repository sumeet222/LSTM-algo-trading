"""D9 independent arithmetic, grouping, causal source and untrained-authority regressions."""

from dataclasses import replace

import pandas as pd
import pytest
import torch

from lstm_data.config import digest
from lstm_data.fullpeer import (
    FullPeerView,
    fullpeer_values,
    make_fullpeer_view,
    operator_batch,
    operator_input,
)
from lstm_data.fullpeer_sp3_audit import UNIVERSE, audit, operator_oracles, planted
from lstm_data.neural_artifacts import PairIdentity, load_checkpoint, save_checkpoint
from lstm_data.neural_engine import SessionBatch, batch_prediction, seed_all
from lstm_data.neural_models import architecture_for_information, create_model, model_version
from lstm_data.operator_artifacts import BoundOperator, load_operator, save_operator
from lstm_data.p3_domain import Permission, UniverseSpec
from lstm_data.spatial_operator import SpatialLSTM


@pytest.fixture(scope="module", autouse=True)
def cpu_threads():
    previous = torch.get_num_threads()
    torch.set_num_threads(1)
    yield
    torch.set_num_threads(previous)


@pytest.fixture(scope="module")
def case():
    from lstm_data.regime_peer_audit import fabricated_case

    return fabricated_case()


def test_independent_parameter_mixer_gradient_permutation_and_peer_oracles():
    proof = operator_oracles()
    assert proof["counts"] == {"FULLPEER": 15265, "MC0": 7073, "SP3": 7093, "mixer": 20}
    assert proof["optimizer_updates"] == 0
    assert proof["initial_m1_gradient"] == 0
    assert proof["initial_m2_gradient"] > 0 and proof["nonzero_m2_m1_gradient"] > 0
    assert proof["MC0_cross_input_derivative"] == proof["MC0_cross_hidden_derivative"] == 0
    assert proof["sampler_19_sizes"] == [16, 3]


def test_full_85_hand_sentinels_all_steps_exclusion_and_exact_21_prefix():
    stock = torch.arange(5 * 48 * 16, dtype=torch.float32).reshape(5, 48, 16)
    market = torch.arange(48 * 5, dtype=torch.float32).reshape(1, 48, 5).expand(5, -1, -1)
    prefix = torch.cat((stock, market), dim=-1)
    result = fullpeer_values(prefix)
    assert result.shape == (5, 48, 85) and torch.equal(result[..., :21], prefix)
    for i in range(5):
        others = [j for j in range(5) if j != i]
        for k, j in enumerate(others):
            assert torch.equal(result[i, :, 21 + 16 * k : 37 + 16 * k], stock[j])
    changed = prefix.clone()
    changed[2, :, :16] += 10
    assert torch.equal(fullpeer_values(changed)[2, :, 21:], result[2, :, 21:])
    for bad in (prefix[:4], prefix[:, :47], prefix.double(), prefix * float("nan")):
        with pytest.raises(ValueError):
            fullpeer_values(bad)
    forged = prefix.clone()
    forged[1, 0, 16] += 1
    with pytest.raises(ValueError, match="MC0_PANEL"):
        fullpeer_values(forged)


@pytest.mark.parametrize("architecture", ["FULLPEER", "SP3"])
def test_bound_inputs_untrained_artifact_and_source_order_stage_rejections(
    case, tmp_path, architecture
):
    data, history, prep, _, permission = case
    row = data.origins[-1].inputs
    item = operator_input(row, prep, history, permission, architecture=architecture)
    bound = BoundOperator(create_model(architecture, universe=data.universe).eval(), item.binding)
    before = bound.scores(item).detach()
    assert before.shape == (5,) and torch.isfinite(before).all()
    path = tmp_path / "operator.pt"
    manifest = save_operator(path, bound)
    assert manifest["prediction_authoritative"] is False
    loaded = load_operator(path, item.binding, architecture)
    assert torch.equal(loaded.scores(item), before)
    for field in ("source", "preparation", "target"):
        changed = replace(item.binding, **{field: "SYN:CHANGED"})
        with pytest.raises(ValueError):
            load_operator(path, changed, architecture)
        with pytest.raises(ValueError):
            loaded.scores(replace(item, binding=changed))
    changed_universe = replace(data.universe, symbols=data.universe.symbols[::-1])
    with pytest.raises(ValueError):
        load_operator(path, replace(item.binding, universe=changed_universe), architecture)
    with pytest.raises(ValueError):
        loaded.scores(replace(item, binding=replace(item.binding, universe=changed_universe)))
    with pytest.raises(ValueError):
        load_operator(path, item.binding, "SP3" if architecture == "FULLPEER" else "FULLPEER")
    with pytest.raises(FileExistsError):
        save_operator(path, bound)
    mutated = item.values.clone()
    mutated[0, 0, -1] += 1
    with pytest.raises(ValueError):
        loaded.scores(replace(item, values=mutated))
    with pytest.raises(ValueError):
        loaded.scores(item, mode="SCIENTIFIC_REAL")
    with pytest.raises(ValueError):
        replace(item.binding, mode="SCIENTIFIC_REAL")
    with pytest.raises(ValueError):
        replace(item.binding, code="SYN:STALE_CODE")
    pair = PairIdentity(
        "SYN:P411",
        item.binding.universe.universe_id,
        "FT0_D7_" + architecture,
        "TG0",
        "SYN:CUTOFF",
        item.binding.source,
        item.binding.preparation,
        "SYN:CONFIG",
        item.binding.code,
    )
    with pytest.raises(ValueError, match="OPERATOR_ARTIFACT_ONLY"):
        save_checkpoint(tmp_path / "fake_final.pt", loaded.model, pair, "REFIT_FINAL", 1)
    assert not (tmp_path / "fake_final.pt").exists()
    with pytest.raises(ValueError):
        load_checkpoint(path, loaded.model, pair, "REFIT_FINAL")
    before_sha = digest(path)
    with path.open("ab") as f:
        f.write(b"tamper")
    assert digest(path) != before_sha
    with pytest.raises(ValueError):
        load_operator(path, item.binding, architecture)


@pytest.mark.parametrize(
    "fault",
    [
        "order",
        "missing",
        "partial",
        "future",
        "unknown",
        "nat",
        "unknown_mask",
        "source",
        "source_only",
        "real",
        "scaler",
        "floor",
        "duplicate_step",
        "stub",
        "market_unknown",
        "market_future",
        "market_stale",
        "market_duplicate",
    ],
)
def test_strict_upstream_causality_and_policy_negatives(case, fault):
    data, history, prep, _, permission = case
    row = data.origins[-1].inputs
    if fault in {"unknown", "nat", "future"}:
        at = (
            None
            if fault == "unknown"
            else pd.NaT
            if fault == "nat"
            else (row.stock.steps[0].end + pd.Timedelta(nanoseconds=1))
        )
        clocks = list(row.available_at)
        stock = list(clocks[1])
        cell = list(stock[0])
        cell[0] = at
        stock[0] = tuple(cell)
        clocks[1] = tuple(stock)
        row = replace(row, available_at=tuple(clocks))
    elif fault == "order":
        row = replace(row, universe=replace(row.universe, symbols=row.universe.symbols[::-1]))
    elif fault == "partial":
        row = replace(row, stock=replace(row.stock, raw_values=row.stock.raw_values[:4]))
    elif fault in {"missing", "unknown_mask"}:
        masks = list(row.stock.mask)
        stock = list(masks[2])
        stock[0] = (False if fault == "missing" else 1,) + stock[0][1:]
        masks[2] = tuple(stock)
        row = replace(row, stock=replace(row.stock, mask=tuple(masks)))
    elif fault == "source":
        row = replace(row, stock=replace(row.stock, source_binding="SYN:STALE_SOURCE"))
    elif fault in {"real", "source_only"}:
        row = replace(
            row,
            stock=replace(row.stock, synthetic=False)
            if fault == "real"
            else replace(row.stock, source_only=True),
        )
    elif fault in {"scaler", "floor"}:
        prep = (
            replace(prep, stock_scaler=replace(prep.stock_scaler, source_binding="f" * 64))
            if (fault == "scaler")
            else replace(prep, stock_floors=replace(prep.stock_floors, source_binding="f" * 64))
        )
    elif fault in {"duplicate_step", "stub"}:
        first = (
            row.stock.steps[1]
            if fault == "duplicate_step"
            else replace(
                row.stock.steps[0], end=row.stock.steps[0].start + pd.Timedelta(minutes=30)
            )
        )
        row = replace(row, stock=replace(row.stock, steps=(first,) + row.stock.steps[1:]))
    elif fault == "market_duplicate":
        history = replace(history, stamps=history.stamps + (history.stamps[0],))
    else:
        end = row.stock.steps[0].end
        stamps = tuple(
            replace(s, available_at=None)
            if fault == "market_unknown"
            else replace(s, available_at=s.timestamp + pd.Timedelta(nanoseconds=1))
            if (fault == "market_future")
            else replace(s, period_end=s.timestamp - pd.Timedelta(minutes=91))
            if s.timestamp == end
            else s
            for s in history.stamps
        )
        history = replace(history, stamps=stamps)
    with pytest.raises(ValueError):
        operator_input(row, prep, history, permission, architecture="FULLPEER")


def test_indexed_view_shared_tables_masks_forgery_duplicates_and_real_rejection(case):
    data, history, prep, val, permission = case
    small = replace(data, origins=data.origins[-2:])
    view = make_fullpeer_view(small, val, prep, permission, history, allow_synthetic=True)
    assert isinstance(view, FullPeerView)
    base = view.market.batch((0,))
    batch = view.batch((0,))
    assert batch.inputs.shape == (1, 2, 5, 48, 85)
    assert torch.equal(batch.inputs[..., :21], base.inputs)
    assert torch.equal(batch.targets, base.targets) and torch.equal(batch.origins, base.origins)
    assert not hasattr(view, "peer_values")
    for architecture in ("FULLPEER", "SP3"):
        grouped = operator_batch(view.market, (0,), architecture=architecture)
        bound = BoundOperator(
            create_model(architecture, universe=data.universe).eval(), grouped.binding
        )
        assert bound.batch_scores(grouped).shape == (1, 2, 5)
        assert torch.equal(grouped.batch.targets, base.targets)
        assert torch.equal(grouped.batch.origins, base.origins)
        assert torch.equal(grouped.batch.inputs[..., :21], base.inputs)
        with pytest.raises(ValueError):
            bound.batch_scores(
                replace(grouped, binding=replace(grouped.binding, universe=UNIVERSE))
            )
    forged = batch.inputs.clone()
    forged[0, 0, 0, 0, 21] += 1
    with pytest.raises(ValueError, match="FULLPEER_CHANNELS"):
        replace(batch, inputs=forged).validate()
    with pytest.raises(ValueError):
        replace(view, universe=UNIVERSE).batch((0,))
    with pytest.raises(ValueError):
        view.batch((0, 0))
    with pytest.raises(ValueError):
        make_fullpeer_view(
            replace(small, origins=small.origins + (small.origins[0],)),
            val,
            prep,
            permission,
            history,
            allow_synthetic=True,
        )
    with pytest.raises(ValueError):
        make_fullpeer_view(
            small, val, prep, permission, history, allow_synthetic=True, mode="SCIENTIFIC_REAL"
        )
    with pytest.raises(ValueError):
        make_fullpeer_view(
            small, val, prep, Permission("SCIENTIFIC_REAL"), history, allow_synthetic=True
        )
    with pytest.raises(ValueError):
        make_fullpeer_view(small, val, prep, permission, history)
    bad_stock = view.market.values.clone()
    bad_stock[0, 0] += 1
    forged_view = replace(view.market, stock=replace(view.market.stock, values=bad_stock))
    with pytest.raises(ValueError, match="MUTATED"):
        replace(view, market=forged_view).batch((0,))


def test_grouped_origin_isolation_dropout_masks_clipping_and_factory_boundaries():
    seed_all(42)
    model = create_model("SP3", universe=UNIVERSE)
    assert isinstance(model, SpatialLSTM)
    planted(model.mixer)
    model.eval()
    x = torch.randn(2, 5, 48, 21)
    x[..., 16:] = x[:, :1, :, 16:]
    output = model(x.reshape(10, 48, 21))
    assert torch.allclose(output[:5], model(x[0]), rtol=0, atol=1e-7)
    assert torch.allclose(output[5:], model(x[1]), rtol=0, atol=1e-7)
    changed = x.clone()
    changed[1, 2] += 1
    changed[1, :, :, 16:] = x[1, :1, :, 16:]
    assert torch.equal(model(changed.reshape(10, 48, 21))[:5], output[:5])
    model.train()
    assert not torch.equal(model(x.reshape(10, 48, 21)), model(x.reshape(10, 48, 21)))
    assert model.core.dropout.p == 0.1 and model.core.lstm.dropout == 0
    batch = SessionBatch(("SYN:DAY",), x[None], torch.zeros(1, 2, 5), torch.tensor([[True, False]]))
    model.eval()
    assert torch.equal(batch_prediction(model, batch)[0, 0], model(x[0]))
    assert torch.equal(batch_prediction(model, batch)[0, 1], torch.zeros(5))
    for bad in (x.reshape(10, 48, 21)[:4], x[0].double(), x[0, :, :47]):
        with pytest.raises(ValueError):
            model(bad)
    with pytest.raises(ValueError):
        UniverseSpec("SYN:BAD", ("A", "B", "C", "D", "D"))
    with pytest.raises(ValueError):
        create_model("SP3")
    with pytest.raises(ValueError):
        create_model("FULLPEER", mode="SCIENTIFIC_REAL")
    for branch in ("MC2", "LL1", "SP1", "MC1_SP3", "P4.12"):
        with pytest.raises(ValueError):
            create_model(branch)
    assert architecture_for_information("FT0_D7_FULLPEER") == "FULLPEER"
    assert architecture_for_information("FT0_D7_SP3") == "SP3"
    assert model_version(model) == "SYN:SP3:1"


def test_operator_audit_cannot_promote_mode_or_overwrite(tmp_path):
    out = tmp_path / "real"
    with pytest.raises(ValueError):
        audit(out, "SCIENTIFIC_REAL")
    assert not out.exists()
    out.mkdir()
    with pytest.raises(ValueError):
        audit(out)


def test_canonical_dst_early_close_and_overnight_step_publications(case):
    from lstm_data.baseline_fixtures import feature_input
    from lstm_data.neural_market_audit import fabricated_history

    data, history, prep, _, permission = case
    traces = {}
    for day in ("2023-11-06", "2023-11-27"):
        row = feature_input(data.universe, day=day)
        later = replace(
            fabricated_history(tuple(s.end for s in row.stock.steps)), version=history.version
        )
        combined = history.extend(later)
        updated = prep.with_market_history(combined.vectors, permission, allow_synthetic=True)
        inputs = operator_input(row, updated, combined, permission, architecture="FULLPEER")
        assert inputs.values.shape == (5, 48, 85)
        assert row.plan.cutoff is not None
        assert all(s.end <= row.plan.cutoff for s in row.stock.steps)
        traces[day] = row.stock.steps
    assert traces["2023-11-06"][-1].end == pd.Timestamp("2023-11-06T15:30Z")
    assert traces["2023-11-06"][-2].end == pd.Timestamp("2023-11-03T19:30Z")
    assert traces["2023-11-27"][-2].end == pd.Timestamp("2023-11-24T17:30Z")
    assert all(s.end - s.start == pd.Timedelta(hours=1) for s in traces["2023-11-27"])
    with pytest.raises(ValueError):
        feature_input(data.universe, day="2023-11-24")
