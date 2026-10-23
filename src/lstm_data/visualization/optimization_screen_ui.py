"""P024 source-isolated completed-study explorer, with pre-read role/date barriers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from ..config import digest
from ..hf1m_action_audit import SYMBOLS
from ..hf1m_ft16_source import ORDER
from ..optimization_screen import VARIANTS
from .hf1m_long import LongStudy, dates, role
from .objective_screen import Screen, safe_features

SECTION = "HF1M Long — Optimization & Capacity (P024)"
ARMS = tuple(v.arm for v in VARIANTS)
VIEWS = (
    "Start Here",
    "Comparisons",
    "Optimization / Gradients",
    "Capacity",
    "Forecasts / Residuals",
    "Actual-Objective Tails",
    "Exact Cases",
    "History / Features",
)


@dataclass(frozen=True)
class OptimizationStudy(Screen):
    @classmethod
    def discover(cls, root: Path) -> OptimizationStudy:
        config = json.loads((root / "configs/track_a_p024_visualization_v1.json").read_text())
        path = root / config["manifest"]["path"]
        if digest(path) != config["manifest"]["sha256"]:
            raise ValueError("P024 manifest changed")
        m = json.loads(path.read_text())
        if m["status"] != "PASS_COLLECTIVE_P024" or m["ledger"] != 51:
            raise ValueError("P024 completed six-arm diagnostics required")
        contract = m["source_contract"]
        if (
            contract["sha256"] != "7adfec916b7eb74fead83ef1fe6082ff0fcee9ff0b6ebae5722077e2a82c01a5"
            or digest(root / contract["path"]) != contract["sha256"]
        ):
            raise ValueError("P024 frozen HF1M FT16/TG20 source contract changed")
        return cls(root, m["files"], config["manifest"]["sha256"], config)

    def population(self, model: str, split: str) -> pd.DataFrame:
        role(split)
        if model not in ARMS:
            raise ValueError("P024 model denied")
        return self.table(model + "/" + split + "/population.parquet")

    def filtered(self, model: str, split: str, ticker: str, start: str, end: str) -> pd.DataFrame:
        dates(start, end)
        role(split)
        if ticker not in SYMBOLS:
            raise ValueError("P024 stock denied")
        f = self.population(model, split)
        return f.loc[f.ticker.eq(ticker) & f.session_date_et.between(start, end)].copy()


def chart(fig, key: str) -> None:
    st.plotly_chart(fig, width="stretch", key=key)


def panel(root: Path) -> None:
    # Validate query requests before any manifest, numerical file or cache is accessed.
    for key in ("start", "end", "date"):
        if key in st.query_params:
            dates(str(st.query_params[key]), str(st.query_params[key]))
    if "role" in st.query_params:
        role(str(st.query_params["role"]))
    s = OptimizationStudy.discover(root)
    st.title(SECTION)
    st.caption(
        "Pinned HF1M LONG / FT16 / TG20 · six completed arms · seven charged starts45–51 "
        "including failed46 · ledger51/200 · protected Jan–Mar2026 LOCKED"
    )
    st.info(
        "Exploratory development:109 correlated trading sessions, repeatedly inspected. "
        "Compare each arm to its matched T2seed. "
        "Larger forecasts or fewer clips alone are not success."
    )
    view = st.selectbox("P024 view", VIEWS, key="p024_view")
    arm = st.selectbox("P024 arm", ARMS, key="p024_arm")
    split = st.selectbox(
        "P024 role", ("development", "inner_validation", "refit", "inner_train"), key="p024_role"
    )
    version = role(split)
    baseline = "T2/123" if arm == "ES025" else "T2/42"
    variant = next(v for v in VARIANTS if v.arm == arm)
    st.caption(
        "Primary matched reference: " + baseline + ". Refit/inner_train are in-sample; "
        "inner_validation selects checkpoints; development is exploratory."
    )
    st.caption(
        f"Head dropout p={variant.head_dropout:g} in train mode; disabled in evaluation. "
        "DROP0 has no effective head dropout in either mode. Recurrent/interlayer dropout=0."
    )
    if view == "Start Here":
        st.markdown(s.file("guide.md").read_text())
        st.dataframe(s.table("stage_audit.csv"), width="stretch")
        for key in (
            "P024_COLLECTIVE_MODEL_COMPARISON.md",
            "P024_OBJECTIVE_SPACE_EXTREME_LOSS_ATTRIBUTION.md",
        ):
            st.download_button(key, s.file(key).read_text(), file_name=key)
        return
    if view == "Comparisons":
        f = pd.DataFrame(json.loads(s.file("scores.json").read_text()))
        f = f.loc[f.role.eq(split)]
        f = f.assign(
            display_model=f.model.replace(
                {
                    "HF1M-LONG-TM0-T2-S42-DEV1": "T2/42",
                    "HF1M-LONG-TM0-T2-S123-DEV1": "T2/123",
                }
            )
        )
        chart(
            px.bar(f, x="display_model", y="mse", title="Original TG20 MSE · same population"),
            "p024_mse",
        )
        chart(
            px.bar(
                f,
                x="display_model",
                y="daily_ic",
                title="Equal-day cross-sectional Rank IC · ZERO undefined",
            ),
            "p024_ic",
        )
        st.dataframe(f, width="stretch")
        d = s.table("paired_differences.csv")
        st.dataframe(d.loc[d.arm.eq(arm) & d.role.eq(split)], width="stretch")
        st.caption(
            "400 fixed-seed whole-month / two-month block replicates preserve complete days. "
            "Intervals are exploratory; the3660 stock rows are not independent trials."
        )
        return
    if view == "Optimization / Gradients":
        f = s.table("optimization.csv")
        f = f.loc[f.arm.eq(arm)]
        for phase in ("calibration", "refit"):
            g = f.loc[f.phase.eq(phase)]
            st.subheader(phase)
            chart(
                px.line(
                    g,
                    x="epoch",
                    y="objective",
                    color="kind",
                    title="z-MSE · online train mode versus fixed validation, dropout disabled",
                ),
                "p024_loss_" + phase,
            )
            if phase == "calibration":
                chart(
                    px.line(
                        g.loc[g.kind.eq("validation")],
                        x="epoch",
                        y="original_mse",
                        title="Original TG20 validation MSE · checkpoint selection",
                    ),
                    "p024_selection",
                )
            st.dataframe(g, width="stretch")
            train = g.loc[g.kind.eq("training")]
            if len(train):
                chart(
                    px.line(
                        train,
                        x="epoch",
                        y="clipped_fraction",
                        title="Actual update clipping fraction · global norm >1",
                    ),
                    "p024_clipping_" + phase,
                )
        gradients = s.table(arm + "/gradient_quantiles.csv")
        quantities = st.multiselect(
            "P024 gradient quantities",
            gradients.quantity.unique().tolist(),
            default=["preclip", "postclip"],
        )
        chart(
            px.line(
                gradients.loc[gradients.quantity.isin(quantities)],
                x="epoch",
                y="p99",
                color="quantity",
                facet_row="phase",
                title="Per-update norm p99 · clipping cap1 applies globally",
            ),
            "p024_gradients",
        )
        st.dataframe(gradients, width="stretch")
        st.dataframe(s.table("selection.csv").query("arm == @arm"), width="stretch")
        return
    if view == "Capacity":
        f = s.table("selection.csv")
        chart(
            px.bar(
                f,
                x="arm",
                y="parameters",
                title="Measured parameters · width/depth single-factor changes",
            ),
            "p024_capacity",
        )
        st.dataframe(f, width="stretch")
        scores = pd.DataFrame(json.loads(s.file("scores.json").read_text()))
        scores = scores.loc[scores.model.isin(ARMS) & scores.role.eq(split)]
        chart(
            px.bar(
                scores,
                x="model",
                y="prediction_sd",
                title="Forecast SD · increased dispersion alone is not improvement",
            ),
            "p024_forecast_sd",
        )
        st.json(json.loads(s.file(arm + "/" + split + "/recurrent_state_sample.json").read_text()))
        st.caption(
            "Hidden/cell norms are bounded saved-checkpoint samples. No measured gate-saturation "
            "or vanishing-gradient claim follows from these norms or capacity alone."
        )
        return
    if view == "Actual-Objective Tails":
        f = s.table("cohorts.parquet")
        f = f.loc[f.arm.eq(arm) & f.role.eq(split)]
        names = st.multiselect(
            "P024 cohorts",
            f.cohort.tolist(),
            default=[
                "TARGET_RANK_TOP1",
                "TARGET_RANK_TOP5",
                "RANGE_ABS_0.99",
                "RANGE_ABS_0.95",
                "BOTH_5",
                "NUM_ONLY_5",
                "MAD_ONLY_5",
                "NEITHER_5",
            ],
        )
        g = f.loc[f.cohort.isin(names)]
        chart(
            px.bar(
                g,
                x="cohort",
                y="weighted_loss_share_pct",
                title="Actual fixed-checkpoint weighted z-MSE shares",
            ),
            "p024_tailshares",
        )
        st.dataframe(g, width="stretch")
        st.caption(
            "Rank1/5% is an observation fraction; "
            ".99/.95of the training maximum is a magnitude range. "
            "All arms optimize the same z-MSE. Overlapping groups do not add; RMSE is not additive."
        )
        population = s.population(arm, split)
        order = st.selectbox(
            "P024 rank events by", ("total", "TG20", "numerator", "cross_section_mad")
        )
        ranking = population.assign(
            abs_target=population.TG20.abs(),
            abs_numerator=population.numerator.abs(),
            canonical_stock=population.ticker.map({name: i for i, name in enumerate(SYMBOLS)}),
        ).sort_values(
            [
                {"TG20": "abs_target", "numerator": "abs_numerator"}.get(order, order),
                "origin_id",
                "canonical_stock",
            ],
            ascending=[order == "cross_section_mad", True, True],
            kind="stable",
        )
        page = int(
            st.number_input(
                "P024 event page",
                min_value=1,
                max_value=max(1, (len(ranking) + 199) // 200),
                value=1,
            )
        )
        st.dataframe(ranking.iloc[(page - 1) * 200 : page * 200], width="stretch")
        return
    if view == "Exact Cases":
        st.caption(
            "Saved refit in-sample witnesses, independent of the role selector: "
            "48input hours plus4future outcome hours."
        )
        cases = s.table(arm + "/cases.parquet")
        case = st.selectbox("P024 exact case", cases.case_id.tolist())
        if case is None:
            return
        selected = cases.loc[cases.case_id.eq(case)].iloc[0]
        st.dataframe(cases.loc[cases.case_id.eq(case)].T.astype(str), width="stretch")
        candles = s.table(arm + "/case_candles.parquet")
        candles = candles.loc[candles.case_id.eq(case)]
        fig = go.Figure(
            go.Candlestick(
                x=candles.hour_end_utc,
                open=candles.open,
                high=candles.high,
                low=candles.low,
                close=candles.close,
            )
        )
        boundary = candles.loc[candles.step.eq(selected.entry_step), "hour_end_utc"].iloc[0]
        fig.add_shape(
            type="line",
            x0=boundary,
            x1=boundary,
            y0=0,
            y1=1,
            yref="paper",
            line=dict(color="orange", dash="dash"),
        )
        chart(fig, "p024_case")
        chart(
            px.bar(
                candles,
                x="hour_end_utc",
                y="observed_volume_sum",
                color="volume_quality_tier",
                hover_data=["context", "volume_missing_assumed_zero", "hourly_volume_lower_bound"],
                title="Observed minute-volume sum · incomplete hours are lower bounds",
            ),
            "p024_case_volume",
        )
        st.dataframe(candles, width="stretch")
        features = s.table(arm + "/case_features.parquet")
        st.dataframe(features.loc[features.case_id.eq(case)], width="stretch")
        returns = s.table(arm + "/case_20_returns.parquet")
        st.dataframe(returns.loc[returns.case_id.eq(case)], width="stretch")
        return
    if view == "History / Features":
        ticker = st.selectbox("P024 history stock", SYMBOLS, index=4)
        start = st.date_input(
            "P024 start",
            date(2025, 7, 15),
            min_value=date(2010, 7, 1),
            max_value=date(2025, 12, 31),
        )
        end = st.date_input(
            "P024 end", date(2025, 7, 25), min_value=date(2010, 7, 1), max_value=date(2025, 12, 31)
        )
        dates(str(start), str(end))
        if (end - start).days > 93:
            st.warning("Choose at most93days per request.")
            return
        study = LongStudy.discover(root)
        candles = study.history(ticker, str(start), str(end))
        from .hf1m_long_ui import candles as history_plot

        history_plot(candles, "p024_history")
        st.dataframe(candles, width="stretch")
        origin = st.selectbox("P024 M2 context", (1, 2))
        feature = st.selectbox("P024 channel", ORDER)
        values = safe_features(study, ticker, str(start), str(end), version, origin)
        if len(values):
            chart(
                px.line(
                    values.loc[values.feature.eq(feature)], x="hour_end_utc", y=["native", "scaled"]
                ),
                "p024_features",
            )
        st.dataframe(values, width="stretch")
        return
    f = s.population(arm, split)
    ticker = st.selectbox("P024 output stock", ("ALL20",) + SYMBOLS, index=0)
    g = f if ticker == "ALL20" else f.loc[f.ticker.eq(ticker)]
    chart(px.histogram(g, x="TG20", title="Original target distribution"), "p024_target")
    residuals = g.assign(residual=g.y_hat - g.TG20)
    chart(
        px.histogram(residuals, x="residual", title="Original TG20 residual distribution"),
        "p024_residual",
    )
    daily = s.table(arm + "/" + split + "/daily.parquet")
    if "session_date_et" not in daily:
        daily = daily.reset_index()
    for metric in ("ic", "mse"):
        chart(
            px.line(daily, x="session_date_et", y=metric, title="Daily " + metric),
            "p024_daily_" + metric,
        )
    if ticker != "ALL20":
        b = LongStudy.discover(root).prediction(
            "HF1M-LONG-TM0-T2-S" + ("123" if arm == "ES025" else "42") + "-DEV1", split
        )
        b = b.set_index(["origin_id", "ticker"]).reindex(
            pd.MultiIndex.from_frame(g[["origin_id", "ticker"]])
        )
        overlay = g.assign(matched_T2=b.pred_original_TG20.to_numpy())
        chart(
            px.line(overlay, x="entry_end_utc", y=["TG20", "y_hat", "matched_T2"]), "p024_overlay"
        )
    profiles = pd.DataFrame(json.loads(s.file(arm + "/forecast_profiles.json").read_text()))
    st.dataframe(profiles.loc[profiles.role.eq(split)], width="stretch")
    st.dataframe(g.head(200), width="stretch")
