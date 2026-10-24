"""P027 actual dashboard dispatch/protection and hash-bound full component rehearsal."""

import json
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from lstm_data.config import fingerprint
from lstm_data.hf1m_ft16_source import checked
from lstm_data.peer_screen_authority import code_binding, require_gate
from lstm_data.peer_screen_spec import ARMS
from lstm_data.visualization.peer_screen_ui import SECTION, PeerStudy

ROOT = Path(__file__).resolve().parents[1]
PREPARATION = ROOT / "reports/experiments/ta027_cross_stock_2026-10-23_214637_preparation_v1"


def test_protected_file_routes_reject_before_stat(monkeypatch):
    study = PeerStudy(ROOT, {}, "UNIT_TEST_ONLY", {})

    def forbidden(*args, **kwargs):
        raise AssertionError("Protected request reached stat")

    monkeypatch.setattr(Path, "stat", forbidden)
    for key in (
        "",
        "A4/confirmation/data.parquet",
        "2026-01-01.parquet",
        "A5/held_out/data.parquet",
    ):
        with pytest.raises(ValueError):
            study.file(key)
    with pytest.raises(ValueError):
        study.population("A6", "confirmation")
    with pytest.raises(ValueError):
        study.filtered("A4", "development", "AAPL", "2025-12-01", "2026-01-01")


def test_current_app_peer_entry_and_preserved_P021_to_P026_navigation():
    app = AppTest.from_file(str(ROOT / "apps/track_a_dashboard.py"), default_timeout=90)
    app.session_state["section"] = SECTION
    app.run()
    assert not app.exception and not app.error
    if not (ROOT / "configs/track_a_p027_visualization_v1.json").exists():
        assert any("preparation only" in message.value for message in app.info)
    for section in (
        "HF1M Long — 20 stocks (2010–2025)",
        "HF1M Long — Objective Improvement Screen (P022)",
        "HF1M Long — Direction / Quantiles / Sampling (P023)",
        "HF1M Long — Optimization & Capacity (P024)",
        "HF1M Long — E1 / QR1 Replication (P025)",
        "HF1M Long — Temporal Architectures (P026)",
    ):
        app.radio(key="section").set_value(section).run()
        assert not app.exception and not app.error, section


@pytest.mark.skipif(
    not (PREPARATION / "latest_complete_rehearsal_reference.json").exists(),
    reason="current complete P027 component rehearsal required",
)
def test_full_component_rehearsal_is_current_complete_and_cannot_authorize_a_start():
    reference = json.loads((PREPARATION / "latest_complete_rehearsal_reference.json").read_text())
    receipt = json.loads(checked(reference).read_text())
    assert receipt["code"] == code_binding() and receipt["execution_sha256"] == fingerprint(
        code_binding()
    )
    assert receipt["optimizer_step_calls"] == 0 and receipt["neural_starts"] == 0
    assert receipt["all_role_exports"] == 12 and receipt["exact_cases"] == 66
    for arm, gate in zip(ARMS, receipt["gates"]):
        path = checked(gate)
        result = require_gate(path, arm, rehearsal=True)
        with pytest.raises(ValueError):
            require_gate(path, arm)
        ui = json.loads(
            checked(result["deliverables"]["ui_payload/component_receipt.json"]).read_text()
        )
        assert ui["role_view_pairs"] == 36 and ui["case_choices"] == 22
        assert (
            ui["stock_histories"] == 20
            and ui["feature_channels"] == 16
            and ui["guarded_routes"] == 4
        )
