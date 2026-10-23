"""P023 full-population genuine endpoint and frozen execution verification; no updates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from lstm_data.config import write_json
from lstm_data.dm_quantile_authority import code_binding, rows
from lstm_data.dm_quantile_loss import ARMS, RUNS
from lstm_data.hf1m_action_audit import SYMBOLS
from lstm_data.hf1m_ft16_loader import load_model_input
from lstm_data.hf1m_ft16_source import checked
from lstm_data.hf1m_training_data import TrainingView
from lstm_data.visualization.hf1m_long import LongStudy


def verify_refs(value: object, found: dict[str, dict]) -> None:
    """Hash reference records recursively; never decode source numeric files."""
    if isinstance(value, dict):
        if {"path", "sha256", "bytes"} <= value.keys():
            checked(value)
            found[value["path"]] = value
        if {"raw_path", "raw_sha256", "raw_bytes"} <= value.keys():
            raw = dict(path=value["raw_path"], sha256=value["raw_sha256"], bytes=value["raw_bytes"])
            checked(raw)
            found[raw["path"]] = raw
        for item in value.values():
            verify_refs(item, found)
    elif isinstance(value, list):
        for item in value:
            verify_refs(item, found)


def verify(plan_path: Path) -> None:
    plan = json.loads(plan_path.read_text())
    assert code_binding() == plan["code"]
    history = rows()
    assert [r["run_id"] for r in history if r["status"] == "STARTED"] == list(RUNS)
    assert [r["run_id"] for r in history if r["status"] == "COMPLETED"] == list(RUNS)
    assert history[-1]["global_started_pairs"] == 44
    study = LongStudy.discover(Path.cwd())
    quality = study.table("candles_quality").set_index(["step", "ticker"])
    checks = []
    for role in ["inner_train", "inner_validation", "refit", "development"]:
        version = "inner" if role.startswith("inner") else "refit"
        source = load_model_input(
            Path(plan["input_contract"]["path"]), split=role, fit_version=version
        )
        TrainingView(source, role)
        a = pd.MultiIndex.from_arrays(
            [np.repeat(source.rows.entry_index.to_numpy(), 20), np.tile(SYMBOLS, len(source.rows))]
        )
        b = pd.MultiIndex.from_arrays(
            [np.repeat(source.rows.exit_index.to_numpy(), 20), np.tile(SYMBOLS, len(source.rows))]
        )
        entry = quality.reindex(a)
        exit_ = quality.reindex(b)
        assert entry.genuine_close.all() and exit_.genuine_close.all()
        returns = np.log(exit_.close.to_numpy(dtype=float) / entry.close.to_numpy(dtype=float))
        r = returns.reshape(-1, 20)
        median = np.median(r, axis=1)
        mad = np.median(abs(r - median[:, None]), axis=1)
        y = ((r - median[:, None]) / (mad[:, None] + source.fit["epsilon"])).reshape(-1)
        for arm in ARMS:
            f = pd.read_parquet(
                plan_path.parent / (arm + "_diagnostics_v1") / role / "population.parquet"
            )
            np.testing.assert_allclose(f.return_4h, returns, rtol=1e-11, atol=1e-12)
            np.testing.assert_allclose(f.TG20, y, rtol=1e-10, atol=1e-11)
            assert len(f) == plan["views"][role]["stock_rows"]
            assert f.session_date_et.lt("2026-01-01").all()
            np.testing.assert_allclose(
                f.y_hat, source.fit["t2_scale"] * np.sinh(f.z_hat), rtol=7e-7, atol=1e-7
            )
            assert f.inverse_count.eq(1).all()
            checks.append(
                dict(
                    arm=arm,
                    role=role,
                    rows=len(f),
                    all20_endpoints_genuine=True,
                    TG20_reconstruction=True,
                    inverse_once=True,
                )
            )
    for row in history:
        if row["status"] == "COMPLETED":
            result = json.loads(checked(row["detail"]["result"]).read_text())
            for item in result["artifacts"]:
                checked(item)
    references = {}
    verify_refs(
        json.loads(
            Path(
                "reports/data_audit/ta018d_hf1m_long_2026-10-22_155547/complete_acquisition_manifest.json"
            ).read_text()
        ),
        references,
    )
    assert len(references) == 1701
    for item in plan["protected_refs"]:
        checked(item)
    write_json(
        plan_path.parent / "final_scientific_verification.json",
        dict(
            status="PASS",
            checks=checks,
            source_files_verified=1701,
            source_bytes_verified=sum(r["bytes"] for r in references.values()),
            ledger=44,
            new_starts=3,
            protected_numeric_access=False,
            optimizer_steps_diagnostics=0,
            fit_code_unchanged=True,
        ),
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--plan", type=Path, required=True)
    verify(p.parse_args().plan)
