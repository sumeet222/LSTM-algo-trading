"""Saved-output oracles reject source and weight corruption without any model fit."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from lstm_data.hf20_horizon_closeout import role_oracle
from lstm_data.hf20_ranking import rank_targets


@pytest.mark.parametrize("arm", ["T2R", "NR"])
def test_saved_horizon_units_and_corruption(tmp_path: Path, arm: str):
    group = tmp_path / "A" / "F21_H1"
    dest = group / arm
    dest.mkdir(parents=True)
    returns = np.array([np.linspace(-0.02, 0.03, 20), np.linspace(-0.01, 0.02, 20)])
    med = np.median(returns, axis=1)
    mad = np.median(abs(returns - med[:, None]), axis=1)
    y = (returns - med[:, None]) / (mad[:, None] + 0.0001)
    target = (
        np.arcsinh(y.astype(np.float32) / np.float32(0.9))
        if arm == "T2R"
        else rank_targets(returns)
    )
    score = (target + np.float32(0.1)).astype(np.float32)
    f = pd.DataFrame(
        dict(
            origin_id=np.repeat(["o1", "o2"], 20),
            ticker=np.tile([f"S{i}" for i in range(20)], 2),
            session_date_et=np.repeat(["2021-01-20", "2021-01-21"], 20),
            return_h=returns.reshape(-1),
            entry_source_close=100.0,
            exit_source_close=100 * np.exp(returns.reshape(-1)),
            TG20=y.reshape(-1),
            epsilon=0.0001,
            scale=0.9,
            score=score.reshape(-1),
            weight=1 / 40,
            role="inner_train",
            model=arm,
            year=2021,
        )
    )
    path = dest / "inner_train_scores.parquet"
    f.to_parquet(path, index=False)
    (dest / "inner_train_metrics.json").write_text(
        json.dumps(dict(actual_objective=float(((score - target) ** 2).mean())))
    )
    pd.DataFrame(dict(origin_id=["o1", "o2"])).to_csv(
        group / "F21_inner_train_indices.csv", index=False
    )
    assert role_oracle(path)["source_ratio"] == "PASS"
    wrong = f.copy()
    wrong.loc[0, "weight"] = 2 / 40
    wrong.to_parquet(path, index=False)
    with pytest.raises(AssertionError):
        role_oracle(path)
    wrong = f.copy()
    wrong.loc[0, "exit_source_close"] = 110.0 * np.exp(returns[0, 0])
    wrong.to_parquet(path, index=False)
    with pytest.raises(AssertionError):
        role_oracle(path)
