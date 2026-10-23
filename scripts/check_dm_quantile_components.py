"""Conserve actual objective components over every P023 tail cohort."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from lstm_data.objective_screen_attribution import cohort_masks


def check(root: Path) -> None:
    records = []
    for role in ["inner_train", "inner_validation", "refit", "development"]:
        f = pd.read_parquet(root / role / "population.parquet")
        training = pd.read_parquet(
            root / ("inner_train" if role.startswith("inner") else "refit") / "population.parquet"
        )
        masks, _ = cohort_masks(f, training)
        columns = [str(c) for c in f if str(c).startswith("component_")]
        np.testing.assert_allclose(f[columns].sum(axis=1), f.total, rtol=4e-7, atol=1e-10)
        for name, mask in masks.items():
            r = dict(
                role=role,
                cohort=name,
                rows=int(mask.sum()),
                weighted_total=float(f.loc[mask, "total"].sum()),
            )
            for column in columns:
                r[str(column)] = float(f.loc[mask, column].sum())
                r[str(column) + "_unweighted"] = float(
                    (f.loc[mask, column] / f.loc[mask, "ordinary_weight"]).sum()
                )
            records.append(r)
    pd.DataFrame(records).to_csv(
        root / "supplement_v1/objective_components_by_cohort.csv", index=False
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--diagnostics", type=Path, required=True)
    check(p.parse_args().diagnostics)
