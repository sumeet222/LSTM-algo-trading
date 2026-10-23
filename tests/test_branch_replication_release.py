"""P025 read-only estimators, artifact barriers and actual explorer component state."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from lstm_data.branch_replication_followup import conditional_sensitivity, month_counts
from lstm_data.branch_replication_metrics import paired_month_blocks
from lstm_data.branch_replication_release import document
from lstm_data.config import digest
from lstm_data.hf1m_action_audit import SYMBOLS
from lstm_data.hf1m_ft16_source import ORDER
from lstm_data.visualization.branch_replication_ui import MODELS, SECTION, VIEWS, ReplicationStudy

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/track_a_p025_visualization_v1.json"


def test_aggregate_bootstrap_matches_full_panel_original():
    days = np.repeat(["2025-07-01", "2025-07-02", "2025-08-01", "2025-09-01"], 20)
    values = np.repeat([1.0, 2.0, 4.0, 9.0], 20)
    direct = paired_month_blocks(
        days,
        lambda positions, pseudo: float(
            pd.DataFrame(dict(day=pseudo, v=values[positions])).groupby("day").v.mean().mean()
        ),
    )
    for size, original in zip((1, 2), direct):
        counts = month_counts(days, size)
        sampled = counts @ np.array([1.0, 2.0, 4.0, 9.0]) / counts.sum(axis=1)
        np.testing.assert_allclose(
            np.quantile(sampled, [0.025, 0.975]), original["interval"], rtol=0, atol=0
        )


def test_empty_conditional_state_stays_undefined():
    f = pd.DataFrame(
        dict(
            session_date_et=np.repeat(["2025-07-01", "2025-08-01", "2025-09-01"], 20),
            origin_id=np.repeat([1, 2, 3], 20),
            TG20=np.tile(np.linspace(-2.0, 2.0, 20), 3),
            quantiles_z_05=-1.0,
            quantiles_z_50=0.0,
            quantiles_z_95=1.0,
        )
    )
    for state in ("V1", "M2", "Q2", "market_V1", "market_M2", "market_Q2", "predicted_width_z"):
        f[state + "_state"] = "LOW"
    table, _ = conditional_sensitivity(f, dict(scale=1.0, quantiles_z=[-2.0, 0.0, 2.0]))
    empty = table.loc[table.group.eq("HIGH")]
    assert empty.defined_replicates.eq(0).all() and empty.low.isna().all()


def test_read_only_documents_cannot_overwrite(tmp_path):
    p = tmp_path / "report.md"
    document(p, "retained")
    with pytest.raises(FileExistsError):
        document(p, "changed")
    assert p.read_text() == "retained\n"


def test_all_protected_model_roles_and_dates_guard_before_numerical_access(monkeypatch):
    def denied(*args, **kwargs):
        raise AssertionError("Protected access reached file I/O")

    monkeypatch.setattr(ReplicationStudy, "table", denied)
    s = ReplicationStudy(ROOT, {}, "test", {})
    for model in MODELS:
        with pytest.raises(ValueError):
            s.population(model, "confirmation")
        with pytest.raises(ValueError):
            s.filtered(model, "development", "AAPL", "2026-01-01", "2026-03-31")
    with pytest.raises(ValueError):
        s.population("OTHER_SOURCE", "development")


def test_foreign_source_rejected_before_numerical_read(tmp_path, monkeypatch):
    def denied(*args, **kwargs):
        raise AssertionError("Foreign source reached numerical I/O")

    monkeypatch.setattr("pandas.read_parquet", denied)
    m = tmp_path / "manifest.json"
    m.write_text(
        json.dumps(
            dict(
                status="PASS_COLLECTIVE_P025",
                ledger=53,
                source_contract=dict(sha256="wrong", path="wrong"),
            )
        )
    )
    config = tmp_path / "configs/track_a_p025_visualization_v1.json"
    config.parent.mkdir()
    config.write_text(json.dumps(dict(manifest=dict(path="manifest.json", sha256=digest(m)))))
    with pytest.raises(ValueError, match="source contract"):
        ReplicationStudy.discover(tmp_path)


@pytest.mark.skipif(not CONFIG.exists(), reason="Completed private P025 release required")
def test_complete_component_state_models_roles_histories_guards_and_prior_navigation():
    app = AppTest.from_file(str(ROOT / "apps/track_a_dashboard.py"), default_timeout=90)
    app.session_state["section"] = SECTION
    app.run()
    assert not app.exception and not app.error
    for arm in ("E1", "QR1"):
        for seed in (42, 123):
            app.selectbox(key="p025_arm").select(arm)
            app.selectbox(key="p025_seed").select(seed)
            for view in VIEWS:
                app.selectbox(key="p025_view").select(view).run()
                assert not app.exception and not app.error, (
                    arm,
                    seed,
                    view,
                    [x.value for x in app.error],
                    [x.message for x in app.exception],
                )
                if view == "Exact Cases":
                    fig = json.loads(app.get("plotly_chart")[0].proto.spec)
                    assert fig["data"][0]["type"] == "candlestick"
                    assert len(fig["layout"]["shapes"]) == 2
                    assert all(s["line"]["dash"] == "dash" for s in fig["layout"]["shapes"])
            app.selectbox(key="p025_view").select("Outputs")
            for split in ("inner_train", "inner_validation", "refit", "development"):
                app.selectbox(key="p025_role").select(split).run()
                assert not app.exception and not app.error, (arm, seed, split)
            if arm == "E1":
                next(s for s in app.selectbox if s.label == "P025 probability map").select(
                    "INVERSE_CLASS_WEIGHT"
                ).run()
                assert not app.exception and not app.error
            else:
                next(s for s in app.selectbox if s.label == "P025 quantile units").select(
                    "TG20"
                ).run()
                assert not app.exception and not app.error
                fig = json.loads(app.get("plotly_chart")[0].proto.spec)
                assert len(fig["layout"]["shapes"]) == 3
    app.selectbox(key="p025_view").select("History / Features").run()
    for ticker in SYMBOLS:
        next(s for s in app.selectbox if s.label == "P025 history stock").select(ticker).run()
        assert not app.exception and not app.error, ticker
    for channel in ORDER:
        next(s for s in app.selectbox if s.label == "P025 channel").select(channel).run()
        assert not app.exception and not app.error, channel
    app.selectbox(key="p025_view").select("Actual-Objective Tails").run()
    next(s for s in app.multiselect if s.label == "P025 cohorts").set_value([]).run()
    assert not app.exception and not app.error and app.info
    for view in VIEWS:
        app.query_params.clear()
        # Protected routes return before mounting widgets. Remount after clearing them.
        app.run()
        app.selectbox(key="p025_view").select(view).run()
        app.query_params["date"] = "2026-02-01"
        app.run()
        assert app.error and not app.exception, ("protected route", view)
    app.query_params.clear()
    app.query_params["role"] = "confirmation"
    app.run()
    assert app.error and not app.exception
    app.query_params.clear()
    for section in (
        "HF1M Long — Optimization & Capacity (P024)",
        "HF1M Long — Direction / Quantiles / Sampling (P023)",
        "HF1M Long — Objective Improvement Screen (P022)",
        "HF1M Long — 20 stocks (2010–2025)",
        "Start Here",
    ):
        app.session_state["section"] = section
        app.run()
        assert not app.exception and not app.error, section
