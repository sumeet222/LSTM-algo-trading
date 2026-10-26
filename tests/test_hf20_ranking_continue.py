"""Small policy/journal/complete synthetic workflow checks; no real-data fit."""

import json
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest
import torch

from lstm_data.config import fingerprint
from lstm_data.hf20_ranking import RUNS
from lstm_data.hf20_ranking_continue import (
    ContinuationJournal,
    baseline_plan,
    fit_baseline,
    neural_one,
    validate_events,
)
from lstm_data.hf20_ranking_data import FoldData


def test_exact_reuse_and_no_LP_or_extra_baseline():
    tasks = baseline_plan()
    assert len(tasks) == 29 and len(set(tasks)) == 29
    assert tasks[:2] == ["F21/P/refit", "F21/LR/refit"]
    assert not any("/LP/" in t or "F21/P/inner" in t or "F21/LR/inner" in t for t in tasks)


def test_isolated_failure_can_continue_but_shared_failure_cannot():
    history = []
    for run, status, isolated in [
        (RUNS[0], "STARTED", False),
        (RUNS[0], "FAILED", True),
        (RUNS[1], "STARTED", False),
    ]:
        count = 62 + sum(r["status"] == "STARTED" for r in history) + int(status == "STARTED")
        history.append(
            dict(
                sequence=len(history) + 1,
                previous=fingerprint(history),
                run_id=run,
                status=status,
                detail=dict(isolated=isolated),
                global_started_pairs=count,
                effective_ceiling=200,
            )
        )
    validate_events(history)
    bad = [dict(r) for r in history]
    bad[1]["detail"] = {"isolated": False}
    bad[2]["previous"] = fingerprint(bad[:2])
    with pytest.raises(ValueError, match="SHARED_FATAL"):
        validate_events(bad)
    bad = [dict(r) for r in history]
    bad[2]["run_id"] = RUNS[0]
    with pytest.raises(ValueError, match="NO_RETRY"):
        validate_events(bad)


def test_baseline_failure_preserved_no_retry(tmp_path):
    j = ContinuationJournal.__new__(ContinuationJournal)
    j.out = tmp_path
    j.baseline_keys = []

    def isolated():
        raise np.linalg.LinAlgError("SYN_ISOLATED")

    assert fit_baseline(j, "F21/P/refit", isolated, tmp_path / "failed.npy") is None
    assert fit_baseline(j, "F21/LR/refit", lambda: np.zeros(769), tmp_path / "ok.npy") is not None
    with pytest.raises(ValueError, match="NO_BASELINE_RETRY"):
        fit_baseline(j, "F21/P/refit", lambda: np.zeros(20), tmp_path / "unauthorized.npy")
    events = [
        json.loads(x)
        for x in (tmp_path / "baseline_continuation_events.jsonl").read_text().splitlines()
    ]
    assert [r["attempt"] for r in events] == [9, 9, 10, 10]
    assert events[1]["status"] == "FAILED" and events[1]["detail"]["isolated"]


class SyntheticData(FoldData):
    def __init__(self):
        self.symbols = tuple(f"S{i}" for i in range(20))
        self.contract = {"revision": "SYN_ONLY"}
        self.rows = pd.DataFrame(
            dict(
                origin_id=["SYN1", "SYN2"],
                session_date_et=["2021-02-01", "2021-02-02"],
                entry_end_utc=["2021-02-01T15:30Z", "2021-02-02T16:30Z"],
                exit_end_utc=["2021-02-01T19:30Z", "2021-02-02T20:30Z"],
                label_maturity_utc=["2021-02-01T19:32Z", "2021-02-02T20:32Z"],
            )
        )
        self.returns = np.tile(np.linspace(-0.01, 0.01, 20), (2, 1))
        self.recipe = {"epsilon": 0.001, "t2_scale": 1.0}
        self.x = np.zeros((2, 20, 48, 16), np.float32)
        self.x[:, :, :, 0] = self.returns[:, :, None] * 20

    def positions(self, year, role):
        return np.arange(2)

    def phase(self, year, phase, out):
        path = out / f"F21_{phase}_recipe.json"
        if not path.exists():
            path.write_text(json.dumps(self.recipe))
        return self.recipe

    def arrays(self, positions):
        r = self.returns[positions]
        mad = np.median(abs(r - np.median(r, axis=1)[:, None]), axis=1)
        return self.x[positions], r, r / (mad[:, None] + 0.001)

    def quality_fields(self, positions):
        return {
            k: np.zeros(len(positions) * 20)
            for k in (
                "assumed_zero_minute_count",
                "price_proxy_minute_count",
                "feature_fallback_cells",
                "max_terminal_price_age_minutes",
            )
        }


class SyntheticJournal(ContinuationJournal):
    def __init__(self):
        self.records = []

    def event(self, run, status, detail):
        self.records.append(dict(run=run, status=status, detail=detail))


@pytest.mark.parametrize("arm", ["T2R", "NR", "PW"])
def test_complete_new_neural_workflow_synthetic_only(tmp_path, arm):
    torch.set_num_threads(4)
    data = SyntheticData()
    journal = SyntheticJournal()
    (tmp_path / "CONTINUATION_AUTHORITY_AND_RUN_MANIFEST.json").write_text(
        json.dumps({"old_namespace": str(tmp_path / "old_empty")})
    )
    pd.DataFrame(
        dict(
            case_id=[1, 2],
            year=[2021, 2021],
            origin_id=data.rows.origin_id,
            ticker=["S0", "S1"],
            session_date_et=data.rows.session_date_et,
            witness_return_4h=[data.returns[0, 0], data.returns[1, 1]],
        )
    ).to_csv(tmp_path / "shared_source_case_keys.csv", index=False)
    for role in ("inner_train", "inner_validation", "refit", "oos"):
        data.rows[["origin_id"]].to_csv(tmp_path / f"F21_{role}_indices.csv", index=False)
    # Flat synthetic selector trace bounds the rehearsal at12+1 epochs; real selector tests reused.
    with patch("lstm_data.hf20_ranking_continue.daily_ic", return_value=0.1):
        neural_one(data, tmp_path, journal, 2021, arm)
    assert [r["status"] for r in journal.records] == [
        "STARTED",
        "CALIBRATED",
        "REFITTING",
        "COMPLETED",
    ]
    dest = tmp_path / f"HF20-S1S2-F21-{arm}-S42"
    assert len(list(dest.glob("*_scores.parquet"))) == 4
    gate = json.loads((dest / "PASS.json").read_text())
    assert gate["selector"]["selected"] == 1
    assert len(list(dest.glob("calibration_???.json"))) == 12
    from lstm_data.hf20_ranking_continue_report import cohort_tables

    c, _, p, _ = cohort_tables(dest / "oos_scores.parquet")
    assert c.loc[c.cohort.eq("ALL"), "weight_mass"].iloc[0] == pytest.approx(1)
    assert p.weighted_pair_mass.sum() == pytest.approx(1)
    from lstm_data.hf20_ranking_continue_report import collective

    collective(tmp_path)
    assert (tmp_path / "COLLECTIVE_TABLES_RECEIPT.json").exists()
    assert not pd.read_csv(tmp_path / "equal_year_summary.csv").complete_four_years.any()
    assert (tmp_path / "F21_refit_source_case_inputs.npz").exists()


def test_actual_continuation_journal_writer_and_hash_gate(tmp_path, monkeypatch):
    from lstm_data.hf20_ranking_run import sha

    monkeypatch.chdir(tmp_path)
    Path("configs").mkdir()
    Path("reports/audit").mkdir(parents=True)
    out = Path("reports/experiments/SYN_CONTINUATION")
    out.mkdir(parents=True)
    (out / "CONTINUATION_AUTHORITY_AND_RUN_MANIFEST.json").write_text("{}")
    (out / "submitted_continuation_authority.txt").write_text("SYNTHETIC_ONLY")
    Path("reports/audit/old.jsonl").write_text("SYN_ONLY\n")
    (out / "prior_registry_pointer.json").write_text(
        json.dumps(dict(real_journal="reports/audit/old.jsonl", budget_amendment={"SYN": True}))
    )
    (out / "STAGE_B_HANDOFF.json").write_text("{}")
    j = ContinuationJournal(out, {"execution_sha256": "SYN"})
    with patch("lstm_data.hf20_ranking_continue.continuation_hash", return_value="SYN"):
        j.event(RUNS[0], "STARTED", {})
        j.event(RUNS[0], "FAILED", {"isolated": True})
        for status in ("STARTED", "CALIBRATED", "REFITTING", "COMPLETED"):
            j.event(RUNS[1], status, {})
        with pytest.raises(FileNotFoundError):
            j.event(RUNS[2], "STARTED", {})
        gate = out / RUNS[1]
        gate.mkdir()
        proof = gate / "SYN_verified.txt"
        proof.write_text("original")
        (gate / "PASS.json").write_text(
            json.dumps(dict(status="PASS_TECHNICAL", files={str(proof): sha(proof)}))
        )
        proof.write_text("changed")
        with pytest.raises(ValueError, match="OUTPUT_CHANGED"):
            j.event(RUNS[2], "STARTED", {})
        proof.write_text("original")
        j.event(RUNS[2], "STARTED", {})
        assert j.started == 65
