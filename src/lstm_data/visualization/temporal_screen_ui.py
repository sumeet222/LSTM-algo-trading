"""P026 additive read-only temporal explorer; validate selectors before file lookup."""

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
from ..hf1m_ft16_source import ORDER, checked
from ..temporal_screen_spec import ARMS, CONTRACT, ROLES
from .hf1m_long import LongStudy, dates, role
from .objective_screen import Screen

SECTION = "HF1M Long — Temporal Architectures (P026)"
VIEWS = (
    "Start Here",
    "Comparison",
    "Outputs",
    "Actual-Objective Tails",
    "Exact Cases",
    "Mechanisms",
    "History / Features",
    "Training / Gradients",
)


def guard(
    arm: str,
    split: str,
    ticker: str | None = None,
    start: str | None = None,
    end: str | None = None,
) -> None:
    role(split)
    if arm not in ARMS or (ticker is not None and ticker not in SYMBOLS):
        raise ValueError("P026_SELECTOR_DENIED_BEFORE_IO")
    if start is not None or end is not None:
        date.fromisoformat(start or "")
        date.fromisoformat(end or "")
        dates(start or "", end or "")


def guard_query(query) -> None:
    allowed = {"arm", "role", "ticker", "start", "end", "date", "view", "section"}
    if any(k not in allowed for k in query):
        raise ValueError("P026_UNKNOWN_ROUTE_BEFORE_IO")
    for key in ("start", "end", "date"):
        if key in query:
            date.fromisoformat(str(query[key]))
            dates(str(query[key]), str(query[key]))
    guard(
        str(query.get("arm", "A1")),
        str(query.get("role", "development")),
        str(query["ticker"]) if "ticker" in query else None,
    )
    if "view" in query and query["view"] not in VIEWS:
        raise ValueError("P026_VIEW_BEFORE_IO")


@dataclass(frozen=True)
class TemporalStudy(Screen):
    @classmethod
    def discover(cls, root: Path) -> TemporalStudy:
        config = json.loads((root / "configs/track_a_p026_visualization_v1.json").read_text())
        m = json.loads(checked(config["manifest"]).read_text())
        if (
            m["status"] != "PASS_P026_COLLECTIVE"
            or m["ledger"] != 56
            or m["source_contract"]["sha256"] != CONTRACT
            or digest(root / m["source_contract"]["path"]) != CONTRACT
            or m["protected_numeric_access"] is not False
        ):
            raise ValueError("P026_COMPLETE_BOUND_RELEASE_REQUIRED")
        return cls(root, m["files"], config["manifest"]["sha256"], config)

    def file(self, key: str) -> Path:
        if not key or any(
            term in key.lower() for term in ("2026", "confirmation", "held_out", "test/")
        ):
            raise ValueError("P026_PROTECTED_FILE_ROUTE_BEFORE_IO")
        return super().file(key)

    def population(self, arm: str, split: str) -> pd.DataFrame:
        guard(arm, split)
        return self.table(f"{arm}/{split}/population.parquet")

    def filtered(self, arm: str, split: str, ticker: str, start: str, end: str) -> pd.DataFrame:
        guard(arm, split, ticker, start, end)
        f = self.population(arm, split)
        return f.loc[f.ticker.eq(ticker) & f.session_date_et.between(start, end)].copy()


def show(s: TemporalStudy, arm: str, split: str, view: str) -> None:
    guard(arm, split)
    if view not in VIEWS:
        raise ValueError("P026_VIEW_BEFORE_IO")
    if view == "Start Here":
        st.markdown(s.file("guide.md").read_text())
        st.markdown(s.file("comparison.md").read_text())
    elif view == "Comparison":
        st.dataframe(s.table("comparison.parquet"))
        d = s.table(f"{arm}/{split}/paired_daily.parquet")
        st.plotly_chart(
            px.line(
                d,
                x="session_date_et",
                y=["mse", "ic"],
                title="Paired differences vs T2/42; exploratory",
            ),
            key="p026_comparison",
        )
        paired = json.loads(s.file(f"{arm}/{split}/matched_T2_S42.json").read_text())
        st.json(paired)
        intervals = go.Figure()
        for item in paired["intervals"]:
            lo, hi = item["interval"]
            if lo is not None and hi is not None:
                label = f"{item['metric']} / {item['block_months']} month"
                intervals.add_trace(
                    go.Scatter(x=[lo, hi], y=[label, label], mode="lines", name=label)
                )
                intervals.add_trace(
                    go.Scatter(x=[item["delta"]], y=[label], mode="markers", name=label + " delta")
                )
        intervals.add_vline(x=0)
        intervals.update_layout(title="400 paired month-block sensitivities; candidate minus T2/42")
        st.plotly_chart(intervals, key="p026_sensitivity_intervals")
        st.dataframe(s.table(f"{arm}/{split}/heterogeneity.parquet"))
    elif view == "Outputs":
        f = s.population(arm, split)
        st.plotly_chart(
            px.scatter(f, x="TG20", y="pred_original_TG20", color="ticker"), key="p026_output"
        )
        d = s.table(f"{arm}/{split}/daily.parquet")
        st.plotly_chart(px.line(d, x="session_date_et", y="ic"), key="p026_ic")
        st.json(json.loads(s.file(f"{arm}/{split}/metrics.json").read_text()))
        residual = f.pred_original_TG20 - f.TG20
        st.plotly_chart(
            px.histogram(x=residual, labels={"x": "Prediction minus TG20"}), key="p026_residuals"
        )
        overlays = []
        for seed in (42, 123):
            b = s.table(f"baselines/{seed}/{split}.parquet").copy()
            b["model"] = f"T2/{seed}"
            overlays.append(b[["pred_original_TG20", "model"]])
        overlays.append(pd.DataFrame(dict(pred_original_TG20=f.pred_original_TG20, model=arm)))
        overlays.append(pd.DataFrame(dict(pred_original_TG20=[0.0] * len(f), model="ZERO")))
        st.plotly_chart(
            px.histogram(
                pd.concat(overlays), x="pred_original_TG20", color="model", barmode="overlay"
            ),
            key="p026_overlays",
        )
    elif view == "Actual-Objective Tails":
        table = s.table(f"{arm}/cohorts.parquet")
        table = table.loc[table.role.eq(split)]
        cohort = st.selectbox("P026 cohort", table.cohort.tolist(), key="p026_cohort")
        if cohort is None:
            raise ValueError("P026_EMPTY_COHORT_SELECTOR")
        st.dataframe(table.loc[table.cohort.eq(cohort)])
        st.plotly_chart(
            px.bar(
                table.loc[table.cohort.isin(["BOTH_5", "NUM_ONLY_5", "MAD_ONLY_5", "NEITHER_5"])],
                x="cohort",
                y="weighted_loss_share_pct",
            ),
            key="p026_tails",
        )
        st.caption(
            (
                "Fixed saved checkpoint dropout OFF; true session/origin/stock z-"
                "MSE. Overlapping cohorts are never added."
            )
        )
    elif view == "Exact Cases":
        st.caption("Exact source witnesses always use the final refit checkpoint and refit recipe.")
        cases = s.table(f"{arm}/refit/cases.parquet")
        ticker = st.selectbox(
            "P026 case ticker", sorted(cases.ticker.unique()), key="p026_case_ticker"
        )
        if ticker is None:
            raise ValueError("P026_EMPTY_CASE_TICKER")
        subset = cases.loc[cases.ticker.eq(ticker)]
        case = st.selectbox("P026 case", subset.case_id.tolist(), key="p026_case")
        if case is None:
            raise ValueError("P026_EMPTY_CASE_SELECTOR")
        c = s.table(f"{arm}/refit/case_candles.parquet")
        c = c.loc[c.case_id.eq(case)].copy()
        row = subset.loc[subset.case_id.eq(case)].iloc[0]
        clock = next(k for k in ("end_utc", "bar_end_utc", "timestamp", "step") if k in c)
        # Scheduled step keys avoid any invented wall-clock column.
        fig = go.Figure(
            go.Candlestick(
                x=c.step,
                open=c.open,
                high=c.high,
                low=c.low,
                close=c.close,
                name="genuine released hourly OHLC",
            )
        )
        fig.add_vline(x=int(row.entry_step), annotation_text="Input end / entry")
        fig.add_vline(x=int(row.entry_step) + 2 / 60, annotation_text="Issuance +2min")
        fig.add_vline(x=int(row.exit_step), annotation_text="4h exit")
        st.dataframe(subset.loc[subset.case_id.eq(case)])
        clock_et = pd.Timestamp(row.issuance_utc).tz_convert("America/New_York")
        st.caption(f"Issuance UTC {row.issuance_utc}; ET {clock_et}")
        st.plotly_chart(fig, key="p026_candles")
        st.caption(f"52 hours; clock={clock}; UTC/ET in source table; future candles are labels.")
        st.dataframe(c)
        st.plotly_chart(
            px.bar(c, x="step", y="observed_volume_sum", color="volume_quality_tier"),
            key="p026_volume",
        )
        st.dataframe(s.table(f"{arm}/refit/case_20_returns.parquet").query("case_id == @case"))
        features = s.table(f"{arm}/refit/case_features.parquet")
        channel = st.selectbox("P026 feature", ORDER, key="p026_feature")
        if channel is None:
            raise ValueError("P026_EMPTY_FEATURE_SELECTOR")
        st.dataframe(features.loc[features.case_id.eq(case) & features.feature.eq(channel)])
    elif view == "Mechanisms":
        st.json(json.loads(s.file(f"{arm}/refit/mechanisms.json").read_text()))
        g = s.table(f"{arm}/refit/history_gradient.parquet")
        st.plotly_chart(px.line(g, x="lag", y="input_gradient_norm"), key="p026_history_gradient")
        if arm == "A1":
            a = s.table("A1/refit/attention_by_lag_stock.parquet")
            st.plotly_chart(
                px.line(a, x="lag", y="mean_weight", color="ticker"), key="p026_attention"
            )
        st.caption(
            (
                "Module use, attention and input perturbations are diagnostic sen"
                "sitivity, not causal explanations or evidence of predictive skil"
                "l. GRU gates are not directly observed."
            )
        )
    elif view == "History / Features":
        ticker = st.selectbox("P026 ticker", SYMBOLS, key="p026_ticker")
        f = s.population(arm, split)
        st.dataframe(f.loc[f.ticker.eq(ticker)])
        if ticker is None:
            raise ValueError("P026_EMPTY_HISTORY_STOCK")
        channel = st.selectbox("P026 channel", ORDER, key="p026_channel")
        first = str(f.session_date_et.min())
        last = str(
            min(
                pd.Timestamp(first) + pd.Timedelta(days=10), pd.Timestamp(f.session_date_et.max())
            ).date()
        )
        start = st.text_input("P026 history start", first, key="p026_history_start")
        end = st.text_input("P026 history end", last, key="p026_history_end")
        guard(arm, split, ticker, start, end)
        history = LongStudy.discover(s.root)
        candles = history.history(ticker, start, end)
        if len(candles):
            st.plotly_chart(
                go.Figure(
                    go.Candlestick(
                        x=candles.hour_start_utc,
                        open=candles.open,
                        high=candles.high,
                        low=candles.low,
                        close=candles.close,
                    )
                ),
                key="p026_history_candles",
            )
            st.dataframe(candles)
        origin = st.selectbox("P026 origin context", (1, 2), key="p026_origin_context")
        if channel is None or origin is None:
            raise ValueError("P026_EMPTY_HISTORY_FEATURE")
        features = history.features(ticker, start, end, role(split), origin)
        selected = features.loc[features.feature.eq(channel)]
        st.plotly_chart(
            px.line(selected, x="hour_end_utc", y=["native", "model_scaled"]),
            key="p026_history_feature",
        )
        st.dataframe(selected)

    else:
        st.dataframe(s.table(f"{arm}/epochs.parquet"))
        updates = s.table(f"{arm}/updates.parquet")
        st.plotly_chart(
            px.line(updates, x="batch_index", y=["preclip_norm", "postclip_norm"]),
            key="p026_gradients",
        )
        if arm == "A1":
            st.plotly_chart(
                px.line(updates, x="batch_index", y=["gamma", "query_norm"]), key="p026_gamma"
            )


def panel(root: Path) -> None:
    guard_query(st.query_params)
    st.title(SECTION)
    config = root / "configs/track_a_p026_visualization_v1.json"
    if not config.exists():
        st.info(
            (
                "P026 preparation only. No training starts or numerical candidate"
                " results are authorized yet."
            )
        )
        return
    s = TemporalStudy.discover(root)
    arm = st.selectbox("P026 arm", ARMS, key="p026_arm")
    split = st.selectbox("P026 role", ROLES, key="p026_role", index=3)
    view = st.selectbox("P026 view", VIEWS, key="p026_view")
    guard(arm, split)
    st.caption(
        (
            "Pinned HF1M/FT16/TG20; seed42; inner calibration vs fresh refit "
            "recipes; development exploratory; protected2026 LOCKED."
        )
    )
    st.json(s.config.get("model_bindings", {}).get(arm, {}))
    show(s, arm, split, view)
