"""P023 extra proper interval scores by stock, period and target mechanism."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from lstm_data.objective_screen_attribution import cohort_masks
from lstm_data.objective_screen_metrics import equal_weights


def check(root: Path) -> None:
    records = []
    for role in ["inner_train", "inner_validation", "refit", "development"]:
        f = pd.read_parquet(root / role / "population.parquet")
        training = pd.read_parquet(
            root / ("inner_train" if role.startswith("inner") else "refit") / "population.parquet"
        )
        masks, _ = cohort_masks(f, training)
        groups = {
            k: m
            for k, m in masks.items()
            if k in ["ALL", "BOTH_5", "NUM_ONLY_5", "MAD_ONLY_5", "NEITHER_5", "TARGET_RANK_TOP5"]
        }
        groups.update({"stock:" + str(t): (f.ticker == t).to_numpy() for t in f.ticker.unique()})
        groups.update(
            {
                "year:" + str(y): f.session_date_et.str.startswith(y).to_numpy()
                for y in sorted(set(f.session_date_et.str[:4]))
            }
        )
        for name, mask in groups.items():
            g = f.loc[mask]
            if not len(g):
                continue
            w = equal_weights(g.session_date_et.to_numpy())
            z = g.z.to_numpy()
            q = g[["quantiles_z_05", "quantiles_z_50", "quantiles_z_95"]].to_numpy()
            error = z[:, None] - q
            tau = np.array([0.05, 0.5, 0.95])
            score = (
                q[:, 2]
                - q[:, 0]
                + 20 * np.maximum(q[:, 0] - z, 0)
                + 20 * np.maximum(z - q[:, 2], 0)
            )
            records.append(
                dict(
                    role=role,
                    group=name,
                    rows=len(g),
                    pinball=float(w @ np.maximum(tau * error, (tau - 1) * error).mean(axis=1)),
                    lower_coverage=float(w @ (z <= q[:, 0])),
                    upper_coverage=float(w @ (z <= q[:, 2])),
                    interval_coverage=float(w @ ((z >= q[:, 0]) & (z <= q[:, 2]))),
                    interval_width=float(w @ (q[:, 2] - q[:, 0])),
                    interval_score=float(w @ score),
                )
            )
    pd.DataFrame(records).to_csv(root / "supplement_v1/quantile_interval_strata.csv", index=False)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--diagnostics", type=Path, required=True)
    check(p.parse_args().diagnostics)
