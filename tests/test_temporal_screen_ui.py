"""Actual Streamlit component rehearsal using immutable zero-step P026 outputs."""

import base64
import json
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from lstm_data.hf1m_action_audit import SYMBOLS
from lstm_data.hf1m_ft16_source import ORDER, ref
from lstm_data.temporal_screen_spec import ARMS, ROLES
from lstm_data.visualization.temporal_screen_ui import SECTION, VIEWS, TemporalStudy

ROOT = Path(__file__).resolve().parents[1]
REHEARSAL = ROOT / "artifacts/hf20_hf1m_long_v1/p026_preparation/rehearsal_final_v5"


def test_direct_file_and_role_routes_block_before_lookup(monkeypatch):
    def denied(*args, **kwargs):
        raise AssertionError("Protected request reached filesystem")

    s = TemporalStudy(ROOT, {}, "REHEARSAL_ONLY", {})
    monkeypatch.setattr(Path, "stat", denied)
    for key in (
        "",
        "A1/confirmation/population.parquet",
        "2026-01-01.parquet",
        "A1/held_out/out.parquet",
    ):
        with pytest.raises(ValueError):
            s.file(key)
    with pytest.raises(ValueError):
        s.population("A1", "confirmation")
    with pytest.raises(ValueError):
        s.filtered("A2", "development", "AAPL", "2025-01-01", "2026-01-01")


@pytest.mark.skipif(
    not (REHEARSAL / "A3_diagnostics/gate.json").exists(),
    reason="complete zero-step rehearsal required",
)
def test_full_component_matrix_and_sources():
    files = {}
    for arm in ARMS:
        folder = REHEARSAL / (arm + "_diagnostics")
        for p in folder.rglob("*"):
            if p.is_file() and p.suffix in (".parquet", ".json", ".md"):
                files[f"{arm}/{p.relative_to(folder)}"] = ref(p.relative_to(ROOT))
    with tempfile.TemporaryDirectory(prefix="component-", dir=REHEARSAL.parent) as temporary:
        out = Path(temporary)

        def add(key, frame):
            path = out / (key.replace("/", "_"))
            frame.to_parquet(path, index=False)
            files[key] = ref(path.relative_to(ROOT))

        rows = []
        for arm in ARMS:
            r = json.loads((REHEARSAL / arm / "run_result.json").read_text())
            updates = pd.DataFrame(
                [
                    json.loads(line)
                    for line in (REHEARSAL / arm / "updates.jsonl").read_text().splitlines()
                ]
            )
            updates["batch_index"] = np.arange(len(updates))
            add(f"{arm}/updates.parquet", updates)
            add(f"{arm}/epochs.parquet", pd.DataFrame([e["training"] for e in r["epochs"]]))
            for role in ROLES:
                f = pd.read_parquet(
                    REHEARSAL / (arm + "_diagnostics") / role / "population.parquet"
                )
                rows.append(dict(arm=arm, role=role, MSE=float(f.total.sum())))
                if arm == "A1":
                    for seed in (42, 123):
                        b = f.copy()
                        b["pred_original_TG20"] = 0.0
                        add(f"baselines/{seed}/{role}.parquet", b)
        add("comparison.parquet", pd.DataFrame(rows))
        for name in ("guide.md", "comparison.md"):
            path = out / name
            path.write_text("# REHEARSAL_ONLY\nNo trained model or empirical claim.\n")
            files[name] = ref(path.relative_to(ROOT))
        source = f"""from pathlib import Path
import json
import streamlit as st
from lstm_data.visualization.temporal_screen_ui import TemporalStudy,show,guard_query,VIEWS
from lstm_data.temporal_screen_spec import ARMS,ROLES
try:
    guard_query(st.query_params)
except ValueError as exc:
    st.error(str(exc))
    st.stop()
s=TemporalStudy(Path({str(ROOT)!r}),json.loads({json.dumps(files)!r}),'REHEARSAL_ONLY',{{}})
st.caption('SYNTHETIC ZERO-STEP REHEARSAL ONLY; NOT TRAINED')
a=st.selectbox('Arm',ARMS,key='arm')
r=st.selectbox('Role',ROLES,key='role')
v=st.selectbox('View',VIEWS,key='view')
show(s,a,r,v)
"""
        app = AppTest.from_string(source, default_timeout=90).run()
        assert not app.exception and not app.error
        for arm in ARMS:
            app.selectbox(key="arm").select(arm)
            for role in ROLES:
                app.selectbox(key="role").select(role)
                for view in VIEWS:
                    app.selectbox(key="view").select(view).run()
                    assert not app.exception and not app.error, (
                        arm,
                        role,
                        view,
                        [e.message for e in app.exception],
                    )
                    if view == "Exact Cases":
                        spec = json.loads(app.get("plotly_chart")[0].proto.spec)
                        assert spec["data"][0]["type"] == "candlestick"
                        assert len(spec["layout"]["shapes"]) == 3
        app.selectbox(key="view").select("History / Features").run()
        for ticker in SYMBOLS:
            app.selectbox(key="p026_ticker").select(ticker).run()
            assert not app.exception and not app.error, ticker
            spec = json.loads(app.get("plotly_chart")[0].proto.spec)
            assert spec["data"][0]["type"] == "candlestick"
        for channel in ORDER:
            app.selectbox(key="p026_channel").select(channel).run()
            assert not app.exception and not app.error, channel
        app.query_params["date"] = "2026-01-01"
        app.run()
        assert app.error and "protected" in app.error[0].value.lower()


def test_existing_app_navigation_and_available_state():
    app = AppTest.from_file(str(ROOT / "apps/track_a_dashboard.py"), default_timeout=90)
    app.session_state["section"] = SECTION
    app.run()
    assert not app.exception and not app.error
    if (ROOT / "configs/track_a_p026_visualization_v1.json").exists():
        assert app.selectbox(key="p026_arm").options == list(ARMS)
        assert app.selectbox(key="p026_role").options == list(ROLES)
        assert any("protected2026 LOCKED" in x.value for x in app.caption)
    else:
        assert any("preparation only" in x.value for x in app.info)
    # Current real P021-P025 entries still mount; no temporary dashboard process.
    for section in (
        "HF1M Long — 20 stocks (2010–2025)",
        "HF1M Long — Objective Improvement Screen (P022)",
        "HF1M Long — Direction / Quantiles / Sampling (P023)",
        "HF1M Long — E1 / QR1 Replication (P025)",
        "HF1M Long — Optimization & Capacity (P024)",
    ):
        app.radio(key="section").set_value(section).run()
        assert not app.exception and not app.error, section


@pytest.mark.skipif(
    not (ROOT / "configs/track_a_p026_visualization_v1.json").exists(),
    reason="completed three-arm empirical release required",
)
def test_trained_component_matrix_cases_and_source_selectors():
    """Exercise the real main app against sealed trained exports, never refitting."""
    study = TemporalStudy.discover(ROOT)
    app = AppTest.from_file(str(ROOT / "apps/track_a_dashboard.py"), default_timeout=90)
    app.session_state["section"] = SECTION
    app.run()
    assert not app.exception and not app.error
    for arm in ARMS:
        app.selectbox(key="p026_arm").select(arm)
        for role in ROLES:
            app.selectbox(key="p026_role").select(role)
            for view in VIEWS:
                app.selectbox(key="p026_view").select(view).run()
                assert not app.exception and not app.error, (arm, role, view)
                if view == "Exact Cases":
                    spec = json.loads(app.get("plotly_chart")[0].proto.spec)
                    assert spec["data"][0]["type"] == "candlestick"
                    x = spec["data"][0]["x"]
                    count = (
                        np.frombuffer(base64.b64decode(x["bdata"]), dtype=x["dtype"]).size
                        if isinstance(x, dict)
                        else len(x)
                    )
                    assert count == 52
                    assert len(spec["layout"]["shapes"]) == 3
                elif view == "Actual-Objective Tails":
                    cohorts = study.table(f"{arm}/cohorts.parquet")
                    zero = cohorts.loc[cohorts.role.eq(role) & cohorts.rows.eq(0)]
                    for cohort in zero.cohort.head(1):
                        app.selectbox(key="p026_cohort").select(cohort).run()
                        assert not app.exception and not app.error
        app.selectbox(key="p026_view").select("Exact Cases").run()
        cases = study.table(f"{arm}/refit/cases.parquet")
        for row in cases.to_dict("records"):
            app.selectbox(key="p026_case_ticker").select(row["ticker"]).run()
            app.selectbox(key="p026_case").select(row["case_id"]).run()
            assert not app.exception and not app.error, (arm, row["case_id"])
    app.selectbox(key="p026_view").select("History / Features").run()
    for ticker in SYMBOLS:
        app.selectbox(key="p026_ticker").select(ticker).run()
        assert not app.exception and not app.error, ticker
    for channel in ORDER:
        app.selectbox(key="p026_channel").select(channel).run()
        assert not app.exception and not app.error, channel
    for query in ({"date": "2026-01-01"}, {"role": "confirmation"}, {"date": ""}):
        app.query_params.clear()
        app.query_params.update(query)
        app.run()
        assert app.error and not app.exception
