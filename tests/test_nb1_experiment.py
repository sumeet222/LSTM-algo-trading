"""Focused N-B1 math, leakage, recipe, authority and journal boundaries; no real fitting."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
import torch

from lstm_data.config import fingerprint
from lstm_data.nb1_authority import QUEUE, approval_scope, contract, journal_rows, run_id
from lstm_data.nb1_inputs import parameters, transform
from lstm_data.neural_engine import SharedLSTM
from lstm_data.neural_lifecycle import EarlyStop
from lstm_data.real_bridge_run import load_real_checkpoint, save_real_checkpoint


def test_hand_oracle_zero_and_positive_median():
    x = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    recipe = parameters(x)
    assert recipe["s"] == 2.5
    q = np.array([np.arcsinh(v / 2.5) for v in x])
    c, a = float(np.median(q)), float(np.median(np.abs(q - np.median(q))))
    assert (recipe["c"], recipe["a"], recipe["method"]) == (c, a, "MAD")
    assert np.array_equal(transform(x, recipe), ((q - c) / a).astype(np.float32))
    assert np.all(np.diff(transform(x, recipe)) > 0)
    assert transform(np.array([0.0]), recipe)[0] < 0


@pytest.mark.parametrize("values", [[0.0, 0.0], [-1.0, 2.0], [1.0, float("nan")], [1.0, 1.0]])
def test_invalid_or_ambiguous_populations_hold(values: list[float]):
    with pytest.raises(ValueError):
        parameters(np.asarray(values))


def test_shift_cannot_refit_recipe_and_exposures_do_not_weight_keys():
    keys = {("SYN:A", i): float(i) for i in range(1, 6)}
    fit = parameters(np.array(list(keys.values())))
    for held_out in (np.array([100.0, 1000.0]), np.array([0.0, 0.001])):
        before = dict(fit)
        transform(held_out, fit)
        assert fit == before
    repeated = list(keys.items()) + [list(keys.items())[0]] * 100
    deduplicated = dict(repeated)
    assert parameters(np.array(list(deduplicated.values()))) == fit
    assert parameters(np.array([1.0, 2.0, 3.0, 4.0, 5.0, 20.0, 30.0])) != fit


def test_exact_queue_and_unapproved_fit_denied():
    assert QUEUE == (("WF1", 42), ("WF1", 123), ("WF2", 42), ("WF2", 123))
    plan = {"runs": [{"run_id": run_id(*p)} for p in QUEUE], "budget_amendment": {}}
    with pytest.raises(ValueError, match="LIVE_FOUR_PAIR"):
        approval_scope({"sha256": "x"}, {}, plan)


def test_journal_duplicate_and_hash_change_rejected(tmp_path: Path):
    path = tmp_path / "ledger.jsonl"
    rows = []
    for status in ("STARTED", "CALIBRATED", "REFITTING", "COMPLETED"):
        rows.append(
            dict(
                sequence=len(rows) + 1,
                previous=fingerprint(rows),
                status=status,
                run_id=run_id("WF1", 42),
                contract=contract("WF1", 42),
                global_started_pairs=25,
                effective_ceiling=200,
            )
        )
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    assert len(journal_rows(path)) == 4
    rows.append({**rows[0], "sequence": 5, "previous": fingerprint(rows)})
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    with pytest.raises(ValueError, match="DUPLICATE"):
        journal_rows(path)
    rows = rows[:4]
    rows[1]["previous"] = "tampered"
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    with pytest.raises(ValueError, match="CHAIN"):
        journal_rows(path)


def test_existing_d6g_and_cpu_checkpoint_reject_stale_recipe(tmp_path: Path):
    selector = EarlyStop()
    for i in range(12):
        selector.observe(1.0 if i == 0 else 2.0)
    assert selector.selected == 1 and selector.epoch == 12
    model = SharedLSTM(16)
    path = tmp_path / "synthetic.pt"
    save_real_checkpoint(path, model, "SYN:PAIR", "SYN:RECIPE", "SYNTHETIC_SMOKE", 1)
    other = SharedLSTM(16)
    load_real_checkpoint(path, other, "SYN:PAIR", "SYN:RECIPE", "SYNTHETIC_SMOKE")
    assert all(torch.equal(v, other.state_dict()[k]) for k, v in model.state_dict().items())
    with pytest.raises(ValueError, match="BINDING"):
        load_real_checkpoint(path, other, "SYN:PAIR", "SYN:STALE", "SYNTHETIC_SMOKE")


def test_registered_real_preflight_matches_all_frozen_views_and_oracles():
    from lstm_data.visualization.controlled import Study
    from lstm_data.visualization.loaders import Catalog
    from lstm_data.visualization.nb1_ui import handoff, recipe

    catalog = Catalog.discover(Path.cwd())
    packet = handoff(catalog)
    path = Path(packet["artifacts"]["feature_oracles.json"]["path"])
    checks = json.loads(path.read_text())
    expected = Study.discover(catalog).json("input_binding.json")["views"]
    for fold in ("WF1", "WF2"):
        for key, row in checks["views"][fold].items():
            assert row["original"] == expected[fold][key]
            assert row["non_B1_float32_exact"] and row["targets_and_indices_exact"]
            assert row["masks_exact"] and row["q_float64_ties"] == 0
        assert (
            recipe(catalog, packet, fold, "inner")["keys_sha256"]
            != recipe(catalog, packet, fold, "refit")["keys_sha256"]
        )
    assert len(checks["independent_nb1_examples"]) >= 400
    assert all(row["passed"] for row in checks["independent_nb1_examples"])
    extremes = [r for r in checks["independent_nb1_examples"] if r["symbol"] == "CMCSA"]
    assert any(r["timestamp"].startswith("2022-01-27") and r["x"] > 0.08 for r in extremes)


def test_nb1_dashboard_and_tail_context_preserve_legacy_routes():
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(Path.cwd() / "apps/track_a_dashboard.py", default_timeout=60).run()
    app.sidebar.radio[0].set_value("B1 Normalization (012B)").run()
    assert not app.exception
    assert any("Native B1" in str(chart.proto.spec) for chart in app.get("plotly_chart"))
    next(
        button for button in app.button if button.label == "Show genuine B1 tail candles + 48 steps"
    ).click().run()
    assert not app.exception
    assert app.session_state["full_stock"] == "CMCSA"
    assert app.session_state["normalization_example"]["session"] == "2024-01-25"
    assert app.session_state["normalization_context"]
    # Original native/scaled 48-step figures plus the two additive N-B1 context axes.
    charts = app.get("plotly_chart")
    assert any("N_B1_scaled" in str(chart.proto.spec) for chart in charts)
    assert any("volume" in str(chart.proto.spec).lower() for chart in charts)
