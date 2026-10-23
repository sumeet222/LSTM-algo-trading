"""P025 two-seed E1/QR1 explorer with pre-read protected-role/date barriers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from ..branch_replication_metrics import corrected
from ..branch_replication_spec import CONTRACT
from ..config import digest
from ..hf1m_action_audit import SYMBOLS
from ..hf1m_ft16_source import ORDER
from .hf1m_long import LongStudy, dates, role
from .objective_screen import Screen, safe_features

SECTION = "HF1M Long — E1 / QR1 Replication (P025)"
MODELS = ("E1_42", "E1_123", "QR1_42", "QR1_123")
VIEWS = (
    "Start Here",
    "E1 Ranking / Calibration",
    "QR1 Quantiles / States",
    "Outputs",
    "Actual-Objective Tails",
    "Exact Cases",
    "History / Features",
    "Training / Gradients",
)


@dataclass(frozen=True)
class ReplicationStudy(Screen):
    @classmethod
    def discover(cls, root: Path) -> ReplicationStudy:
        config = json.loads((root / "configs/track_a_p025_visualization_v1.json").read_text())
        path = root / config["manifest"]["path"]
        if digest(path) != config["manifest"]["sha256"]:
            raise ValueError("P025 manifest changed")
        m = json.loads(path.read_text())
        if m["status"] != "PASS_COLLECTIVE_P025" or m["ledger"] != 53:
            raise ValueError("P025 complete two-run release required")
        source = m["source_contract"]
        if source["sha256"] != CONTRACT or digest(root / source["path"]) != CONTRACT:
            raise ValueError("P025 source contract changed")
        if m["protected_numeric_access"] is not False:
            raise ValueError("P025 protected lock required")
        return cls(root, m["files"], config["manifest"]["sha256"], config)

    def population(self, model: str, split: str) -> pd.DataFrame:
        role(split)
        if model not in MODELS:
            raise ValueError("P025 model denied")
        return self.table(f"{model}/{split}/population.parquet")

    def filtered(self, model: str, split: str, ticker: str, start: str, end: str) -> pd.DataFrame:
        dates(start, end)
        role(split)
        if ticker not in SYMBOLS:
            raise ValueError("P025 ticker denied")
        f = self.population(model, split)
        return f.loc[f.ticker.eq(ticker) & f.session_date_et.between(start, end)].copy()


def chart(fig, key: str) -> None:
    st.plotly_chart(fig, width="stretch", key=key)


def panel(root: Path) -> None:
    for name in ("start", "end", "date"):
        if name in st.query_params:
            dates(str(st.query_params[name]), str(st.query_params[name]))
    if "role" in st.query_params:
        role(str(st.query_params["role"]))
    s = ReplicationStudy.discover(root)
    st.title(SECTION)
    st.caption(
        (
            "Pinned HF1M LONG / FT16 / TG20 · seeds42/123 · starts52–53 · ledger53/200 "
            "· Jan–Mar2026 LOCKED"
        )
    )
    st.info(
        (
            "Exploratory development:183 origins / 3,660 stock rows / 109 reused "
            "sessions. E1 probabilities are event scores. QR1 forecasts conditional "
            "quantiles; its median MSE is descriptive. Neither implies trading or "
            "production approval."
        )
    )
    view = st.selectbox("P025 view", VIEWS, key="p025_view")
    arm = st.selectbox("P025 arm", ("E1", "QR1"), key="p025_arm")
    seed = st.selectbox("P025 seed", (123, 42), key="p025_seed")
    split = st.selectbox(
        "P025 role", ("development", "inner_validation", "refit", "inner_train"), key="p025_role"
    )
    version = role(split)
    model = f"{arm}_{seed}"
    st.caption(
        (
            "Inner roles use selected inner-calibration checkpoints and inner recipes. "
            "Refit is in-sample; development uses the final refit checkpoint and its "
            "frozen recipe."
        )
    )
    if view == "Start Here":
        st.markdown(s.file("guide.md").read_text())
        st.markdown(s.file("P025_FINAL_RESEARCH_COMPARISON.md").read_text())
        for name in (
            "P025_E1_S123_RESULT.md",
            "P025_E1_CALIBRATION_ANALYSIS.md",
            "P025_QR1_S123_RESULT.md",
            "P025_QR1_CONDITIONAL_STATE_ANALYSIS.md",
            "P025_OBJECTIVE_SPACE_EXTREME_LOSS.md",
            "P025_FINAL_RESEARCH_COMPARISON.md",
        ):
            st.download_button(name, s.file(name).read_text(), file_name=name)
        return
    if view == "E1 Ranking / Calibration":
        f = s.table("E1_calibration_scores.csv")
        f = f.loc[f.role.eq(split)]
        st.dataframe(f, width="stretch")
        chart(
            px.bar(
                f,
                x="seed",
                y="ANY_AP",
                color="mapping",
                barmode="group",
                title="ANY-event AP · event ranking, not signed alpha",
            ),
            "p025_event_ap",
        )
        r = s.table("E1_reliability.csv")
        r = r.loc[r.role.eq(split) & r.event.isin(["NEG", "POS", "ANY"]) & r.rows.gt(0)]
        chart(
            px.scatter(
                r,
                x="confidence",
                y="frequency",
                color="seed",
                symbol="mapping",
                facet_col="event",
                hover_data=["rows", "mass"],
                title="Natural-frequency reliability · bin counts retained",
            ),
            "p025_reliability",
        )
        if split == "development":
            p = s.table("E1_PR_curves.parquet")
            p = p.loc[p.event.isin(["ANY", "NEG", "POS"])]
            chart(
                px.line(
                    p,
                    x="recall",
                    y="precision",
                    color="seed",
                    line_dash="mapping",
                    facet_col="event",
                    title="Two-seed PR · raw vs analytical inverse class weight",
                ),
                "p025_pr",
            )
        st.caption(
            (
                "Inverse class weighting is a mathematical diagnostic, not a guaranteed "
                "calibrator. No temperature map or development threshold was fitted. Signed"
                " IC and ANY AP answer different questions."
            )
        )
        return
    if view == "QR1 Quantiles / States":
        state = s.table("QR1_all_state_metrics.csv")
        state = state.loc[state.role.eq(split)]
        covariate = st.selectbox(
            "P025 causal state",
            ("V1", "M2", "Q2", "market_V1", "market_M2", "market_Q2", "predicted_width_z", "era"),
        )
        f = state.loc[state.state.eq(covariate)]
        chart(
            px.bar(
                f,
                x="group",
                y="width_z",
                color="seed",
                barmode="group",
                title="Predicted 90% z-width · training-frozen causal states",
            ),
            "p025_state_width",
        )
        chart(
            px.bar(
                f,
                x="group",
                y="pinball_skill",
                color="seed",
                barmode="group",
                title="Proper pinball skill vs frozen unconditional quantiles",
            ),
            "p025_state_skill",
        )
        chart(
            px.bar(
                f,
                x="group",
                y="interval90_coverage",
                color="seed",
                barmode="group",
                title="Conditional 90% interval coverage",
            ),
            "p025_state_coverage",
        )
        st.dataframe(f, width="stretch")
        st.dataframe(
            s.table("QR1_output_variability.csv").loc[lambda x: x.role.eq(split)], width="stretch"
        )
        if split == "development":
            st.dataframe(s.table("QR1_state_decision_matrix.csv"), width="stretch")
            st.dataframe(s.table("QR1_conditional_month_sensitivity.csv"), width="stretch")
        st.caption(
            (
                "Output variability, conditional calibration and proper-score skill are "
                "separate findings. Future |z| is retrospective dispersion, never a state "
                "input. Empty cohorts remain empty."
            )
        )
        return
    if view == "Training / Gradients":
        st.caption(
            (
                "New seed123 runs only. Historical online/dropout losses differ from "
                "fixed-checkpoint dropout-OFF objectives."
            )
        )
        epochs = s.table(arm + "_epochs.csv")
        chart(
            px.line(
                epochs,
                x="epoch",
                y="train",
                color="phase",
                title=arm + " online actual training objective",
            ),
            "p025_training",
        )
        chart(
            px.line(
                epochs.loc[epochs.phase.eq("calibration")],
                x="epoch",
                y="validation",
                title=arm + " inner-validation selection objective",
            ),
            "p025_validation",
        )
        st.dataframe(s.table(arm + "_optimization.csv"), width="stretch")
        return
    if view == "Actual-Objective Tails":
        table = s.table("actual_objective_cohorts.parquet")
        table = table.loc[table.arm.eq(arm) & table.role.eq(split)]
        options = [str(x) for x in table.cohort.unique()]
        chosen = st.multiselect(
            "P025 cohorts",
            options,
            default=[
                x
                for x in (
                    "TARGET_RANK_TOP1",
                    "TARGET_RANK_TOP5",
                    "BOTH_5",
                    "MAD_ONLY_5",
                    "RANGE_ABS_0.99",
                    "RANGE_ABS_0.95",
                )
                if x in options
            ],
        )
        table = table.loc[table.cohort.isin(chosen)]
        if table.empty:
            st.info("No selected cohort rows.")
            return
        chart(
            px.bar(
                table,
                x="cohort",
                y="weighted_loss_share_pct",
                title=arm + " actual objective share · CE and pinball have different units",
            ),
            "p025_tails",
        )
        st.dataframe(table, width="stretch")
        st.caption(
            (
                "New seed123 fixed-checkpoint attribution only. Ranked1%/5% rows differ "
                "from99%/95% of training-maximum magnitude. Small MAD ranks unique origins "
                "first. Shares are accounting, not causal explanation."
            )
        )
        return
    if view == "Exact Cases":
        st.caption(
            (
                "Refit in-sample witnesses, independent of role selector:48 input candles "
                "plus4 future outcome candles. No hindsight event is an ex-ante signal."
            )
        )
        cases = s.table(model + "/cases.parquet")
        case = st.selectbox("P025 exact case", cases.case_id.tolist())
        if case is None:
            return
        selected = cases.loc[cases.case_id.eq(case)].iloc[0]
        candles = s.table(model + "/case_candles.parquet")
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
        for step, color in ((selected.entry_step, "orange"), (selected.exit_step, "green")):
            boundary = candles.loc[candles.step.eq(step), "hour_end_utc"].iloc[0]
            fig.add_shape(
                type="line",
                x0=boundary,
                x1=boundary,
                y0=0,
                y1=1,
                yref="paper",
                line=dict(color=color, dash="dash"),
            )
        fig.update_layout(title="Orange: completed input/entry close · green: four-hour exit close")
        chart(fig, "p025_case")
        chart(
            px.bar(
                candles,
                x="hour_end_utc",
                y="observed_volume_sum",
                color="volume_quality_tier",
                hover_data=["context", "volume_missing_assumed_zero", "hourly_volume_lower_bound"],
                title="Observed minute-volume sum · incomplete hours are lower bounds",
            ),
            "p025_case_volume",
        )
        st.dataframe(cases.loc[cases.case_id.eq(case)].T.astype(str), width="stretch")
        st.dataframe(candles, width="stretch")
        for name in ("case_features", "case_20_returns"):
            f = s.table(model + "/" + name + ".parquet")
            st.dataframe(f.loc[f.case_id.eq(case)], width="stretch")
        return
    if view == "History / Features":
        ticker = st.selectbox("P025 history stock", SYMBOLS, index=4)
        start = st.date_input(
            "P025 start",
            date(2025, 7, 15),
            min_value=date(2010, 7, 1),
            max_value=date(2025, 12, 31),
        )
        end = st.date_input(
            "P025 end", date(2025, 7, 25), min_value=date(2010, 7, 1), max_value=date(2025, 12, 31)
        )
        if not isinstance(start, date) or not isinstance(end, date):
            raise ValueError("P025 one-date bounds required")
        a, b = start.isoformat(), end.isoformat()
        dates(a, b)
        study = LongStudy.discover(root)
        history = study.history(ticker, a, b)
        if history.empty:
            st.info("No scheduled candles in this interval.")
            return
        chart(
            go.Figure(
                go.Candlestick(
                    x=history.hour_end_utc,
                    open=history.open,
                    high=history.high,
                    low=history.low,
                    close=history.close,
                )
            ),
            "p025_history",
        )
        st.dataframe(history, width="stretch")
        origin = st.selectbox("P025 M2 context", (1, 2))
        channel = st.selectbox("P025 channel", ORDER)
        f = safe_features(study, ticker, a, b, version, origin)
        chart(
            px.line(
                f.loc[f.feature.eq(channel)],
                x="hour_end_utc",
                y=["native", "scaled"],
                title="Native and scaled " + channel + " · different units",
            ),
            "p025_feature",
        )
        st.dataframe(f.loc[f.feature.eq(channel)], width="stretch")
        st.caption(
            (
                "Genuine/proxy/volume flags are retained. Channel T2 is a feature name. "
                "Native and scaled feature values are shown separately."
            )
        )
        return
    ticker = st.selectbox("P025 output stock", SYMBOLS, index=4)
    f = s.population(model, split)
    f = f.loc[f.ticker.eq(ticker)]
    if f.empty:
        st.info("No outputs for this stock/role.")
        return
    unit = "z"
    if arm == "E1":
        # The original seed42 export preserves probabilities, not a redundant ANY column.
        f = f.copy()
        f["ANY_score"] = f.p_NEG + f.p_POS
        f["signed_event_score"] = f.p_POS - f.p_NEG
        mapping = st.selectbox("P025 probability map", ("RAW_SOFTMAX", "INVERSE_CLASS_WEIGHT"))
        if mapping == "INVERSE_CLASS_WEIGHT":
            recipes = json.loads(s.file("recipes.json").read_text())
            p = corrected(
                f[["p_NEG", "p_NORMAL", "p_POS"]].to_numpy(dtype=float), recipes["E1"][version]
            )
            f = f.copy()
            f[["p_NEG", "p_NORMAL", "p_POS"]] = p
            f["ANY_score"], f["signed_event_score"] = p[:, 0] + p[:, 2], p[:, 2] - p[:, 0]
        columns = ["p_NEG", "p_NORMAL", "p_POS", "ANY_score", "signed_event_score"]
        st.caption(
            "Event probabilities and signed probability difference are not return forecasts."
        )
    else:
        unit = st.selectbox("P025 quantile units", ("z", "TG20"))
        prefix = "z" if unit == "z" else "y"
        columns = [f"quantiles_{prefix}_05", f"quantiles_{prefix}_50", f"quantiles_{prefix}_95"]
        st.caption(
            "Ordered conditional quantiles · lower/median/upper, once-inverted when in TG20 units."
        )
    figure = px.line(
        f,
        x="entry_end_utc",
        y=columns,
        title=f"{model} {ticker} {split} · saved checkpoint outputs",
    )
    if arm == "E1":
        f["probability_map"] = mapping
        figure.update_layout(title=f"{model} {ticker} {split} · {mapping} event scores")
    if arm == "QR1":
        import numpy as np

        recipe = json.loads(s.file("recipes.json").read_text())["QR1"][version]
        for tau, q in zip(("05", "50", "95"), recipe["quantiles_z"]):
            value = q if unit == "z" else recipe["scale"] * float(np.sinh(q))
            figure.add_hline(y=value, line_dash="dash", annotation_text="unconditional q" + tau)
    chart(figure, "p025_outputs")
    st.dataframe(f, width="stretch")
