"""Reproduce P022 read-only interval plots and complete-origin regime IC summaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px

from lstm_data.config import write_json
from lstm_data.hf1m_ft16_source import ref
from lstm_data.objective_screen_audit import month_ci, origin_ic
from lstm_data.objective_screen_source import ordered_targets, scoped_view
from lstm_data.visualization.hf1m_long import LongStudy


def supplement(packet: Path) -> None:
    study = LongStudy.discover(Path.cwd())
    out = packet / "stage1_supplement"
    out.mkdir(exist_ok=False)
    association = pd.read_csv(packet / "stage1/associations.csv")
    association = association.query("representation=='scaled_latest'").copy()
    association["plus"] = association.ci_high - association.daily_ic
    association["minus"] = association.daily_ic - association.ci_low
    figure = px.scatter(
        association,
        x="feature",
        y="daily_ic",
        color="role",
        error_y="plus",
        error_y_minus="minus",
        title="Latest scaled feature daily Rank IC: 400 month-block descriptive intervals",
    )
    figure.write_html(out / "latest_feature_ic_intervals.html", include_plotlyjs=True)
    cut = json.loads((packet / "stage1/frozen_quintile_and_regime_boundaries.json").read_text())[
        "regimes"
    ]
    records = []
    for role in ("inner_train", "inner_validation"):
        view = scoped_view(study, role, stage=1)
        targets = ordered_targets(view)
        y = targets.TG20.to_numpy()
        days = view.source.rows.session_date_et.to_numpy()
        with np.load(packet / "stage1" / f"{role}_feature_summaries.npz") as archive:
            features = archive["native_latest"]
        for seed in (42, 123):
            prediction = study.prediction(f"HF1M-LONG-TM0-T2-S{seed}-DEV1", role)
            prediction = prediction.set_index(["origin_id", "ticker"]).reindex(
                pd.MultiIndex.from_frame(targets[["origin_id", "ticker"]])
            )
            ic = origin_ic(prediction.pred_original_TG20.to_numpy(), y)
            for channel, column in (("V1", 4), ("Q2", 10)):
                median = np.nanmedian(features[:, column].reshape(-1, 20), axis=1)
                regime = np.searchsorted(cut[channel], median)
                regime[~np.isfinite(median)] = 3
                for level in sorted(set(regime)):
                    selected = regime == level
                    daily = pd.Series(ic[selected], index=days[selected]).groupby(level=0).mean()
                    low, high = month_ci(daily)
                    records.append(
                        dict(
                            role=role,
                            seed=seed,
                            channel=channel,
                            regime=int(level),
                            origins=int(selected.sum()),
                            sessions=len(daily),
                            daily_ic=float(daily.mean()),
                            ci_low=low,
                            ci_high=high,
                            assignment=(
                                "origin median native latest; frozen training terciles; all20"
                            ),
                        )
                    )
    pd.DataFrame(records).to_csv(out / "baseline_complete_origin_regime_ic.csv", index=False)
    write_json(
        out / "receipt.json",
        dict(
            status="PASS_READ_ONLY_SUPPLEMENT",
            files=[ref(p) for p in out.iterdir() if p.is_file()],
            no_fits=True,
            no_design_change=True,
            no_development=True,
        ),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    supplement(parser.parse_args().out)
