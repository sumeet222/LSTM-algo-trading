"""P028 additive read-only peer explorer; validate selectors before file lookup."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from ..config import digest, fingerprint, write_json
from ..hf1m_action_audit import SYMBOLS
from ..hf1m_ft16_source import ORDER, checked, ref
from ..state_screen_spec import ARMS, CONTRACT, FAIRNESS, ROLES
from .hf1m_long import LongStudy, dates, role
from .objective_screen import Screen

SECTION = "HF1M Long — Market-State Recurrence (P028)"
VIEWS = (
    "Start Here",
    "Comparison",
    "Outputs",
    "Actual-Objective Tails",
    "Exact Cases",
    "Mechanisms",
    "State Information Control",
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
        raise ValueError("P028_SELECTOR_DENIED_BEFORE_IO")
    if start is not None or end is not None:
        date.fromisoformat(start or "")
        date.fromisoformat(end or "")
        dates(start or "", end or "")


def guard_query(query) -> None:
    allowed = {"arm", "role", "ticker", "start", "end", "date", "view", "section"}
    if any(k not in allowed for k in query):
        raise ValueError("P028_UNKNOWN_ROUTE_BEFORE_IO")
    for key in ("start", "end", "date"):
        if key in query:
            date.fromisoformat(str(query[key]))
            dates(str(query[key]), str(query[key]))
    guard(
        str(query.get("arm", "A7")),
        str(query.get("role", "development")),
        str(query["ticker"]) if "ticker" in query else None,
    )
    if "view" in query and query["view"] not in VIEWS:
        raise ValueError("P028_VIEW_BEFORE_IO")


@dataclass(frozen=True)
class StateStudy(Screen):
    @classmethod
    def discover(cls, root: Path) -> StateStudy:
        from ..state_screen_authority import require_gate

        config = json.loads((root / "configs/track_a_p028_visualization_v1.json").read_text())
        manifest = json.loads(checked(config["manifest"]).read_text())
        if (
            manifest["source_contract"]["sha256"] != CONTRACT
            or digest(root / manifest["source_contract"]["path"]) != CONTRACT
            or manifest["protected_numeric_access"] is not False
        ):
            raise ValueError("P028_BOUND_PRIVATE_SOURCE_REQUIRED")
        arms = manifest.get("available_arms", [])
        if (
            manifest.get("status") not in ("PASS_P028_PARTIAL_VIEW", "PASS_P028_COLLECTIVE")
            or not arms
            or arms != list(ARMS[: len(arms)])
            or config.get("available_arms") != arms
            or manifest.get("ledger") != 59 + len(arms)
        ):
            raise ValueError("P028_ACTUAL_GATED_SUBSET_REQUIRED")
        if len(manifest.get("gates", [])) != len(arms):
            raise ValueError("P028_ALL_AVAILABLE_ARM_GATES_REQUIRED")
        for arm, reference in zip(arms, manifest["gates"]):
            require_gate(checked(reference), arm)
        return cls(root, manifest["files"], config["manifest"]["sha256"], config)

    def file(self, key: str) -> Path:
        if not key or any(
            term in key.lower() for term in ("2026", "confirmation", "held_out", "test/")
        ):
            raise ValueError("P028_PROTECTED_FILE_ROUTE_BEFORE_IO")
        return super().file(key)

    def population(self, arm: str, split: str) -> pd.DataFrame:
        guard(arm, split)
        return self.table(f"{arm}/{split}/population.parquet")

    def filtered(self, arm: str, split: str, ticker: str, start: str, end: str) -> pd.DataFrame:
        guard(arm, split, ticker, start, end)
        f = self.population(arm, split)
        return f.loc[f.ticker.eq(ticker) & f.session_date_et.between(start, end)].copy()


def show(s: StateStudy, arm: str, split: str, view: str) -> None:
    guard(arm, split)
    if view not in VIEWS:
        raise ValueError("P028_VIEW_BEFORE_IO")
    if view == "Start Here":
        st.markdown(s.file("guide.md").read_text())
        st.markdown(s.file("comparison.md").read_text())
        if "context.json" in s.files:
            st.json(json.loads(s.file("context.json").read_text()))
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
            key="p028_comparison",
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
        st.plotly_chart(intervals, key="p028_sensitivity_intervals")
        st.dataframe(s.table(f"{arm}/{split}/heterogeneity.parquet"))
    elif view == "Outputs":
        f = s.population(arm, split)
        st.plotly_chart(
            px.scatter(f, x="TG20", y="pred_original_TG20", color="ticker"), key="p028_output"
        )
        d = s.table(f"{arm}/{split}/daily.parquet")
        st.plotly_chart(px.line(d, x="session_date_et", y="ic"), key="p028_ic")
        st.json(json.loads(s.file(f"{arm}/{split}/metrics.json").read_text()))
        residual = f.pred_original_TG20 - f.TG20
        st.plotly_chart(
            px.histogram(x=residual, labels={"x": "Prediction minus TG20"}), key="p028_residuals"
        )
        overlays = []
        for seed in (42, 123):
            b = s.table(f"{arm}/{split}/T2_S{seed}.parquet").copy()
            b["model"] = f"T2/{seed}"
            overlays.append(b[["pred_original_TG20", "model"]])
        overlays.append(pd.DataFrame(dict(pred_original_TG20=f.pred_original_TG20, model=arm)))
        overlays.append(pd.DataFrame(dict(pred_original_TG20=[0.0] * len(f), model="ZERO")))
        st.plotly_chart(
            px.histogram(
                pd.concat(overlays), x="pred_original_TG20", color="model", barmode="overlay"
            ),
            key="p028_overlays",
        )
    elif view == "Actual-Objective Tails":
        table = s.table(f"{arm}/cohorts.parquet")
        table = table.loc[table.role.eq(split)]
        cohort = st.selectbox("P028 cohort", table.cohort.tolist(), key="p028_cohort")
        if cohort is None:
            raise ValueError("P028_EMPTY_COHORT_SELECTOR")
        st.dataframe(table.loc[table.cohort.eq(cohort)])
        st.plotly_chart(
            px.bar(
                table.loc[table.cohort.isin(["BOTH_5", "NUM_ONLY_5", "MAD_ONLY_5", "NEITHER_5"])],
                x="cohort",
                y="weighted_loss_share_pct",
            ),
            key="p028_tails",
        )
        st.caption(
            (
                "Fixed saved checkpoint dropout OFF; true session/origin/stock z-"
                "MSE. Overlapping cohorts are never added."
            )
        )
    elif view == "Exact Cases":
        st.caption(
            "Role-balanced exact witnesses use final refit checkpoint; source "
            "role and phase are recorded."
        )
        cases = s.table(f"{arm}/refit/cases.parquet")
        ticker = st.selectbox(
            "P028 case ticker", sorted(cases.ticker.unique()), key="p028_case_ticker"
        )
        if ticker is None:
            raise ValueError("P028_EMPTY_CASE_TICKER")
        subset = cases.loc[cases.ticker.eq(ticker)]
        case = st.selectbox("P028 case", subset.case_id.tolist(), key="p028_case")
        if case is None:
            raise ValueError("P028_EMPTY_CASE_SELECTOR")
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
        st.plotly_chart(fig, key="p028_candles")
        st.caption(f"52 hours; clock={clock}; UTC/ET in source table; future candles are labels.")
        st.dataframe(c)
        st.plotly_chart(
            px.bar(c, x="step", y="observed_volume_sum", color="volume_quality_tier"),
            key="p028_volume",
        )
        st.dataframe(s.table(f"{arm}/refit/case_20_returns.parquet").query("case_id == @case"))
        features = s.table(f"{arm}/refit/case_features.parquet")
        channel = st.selectbox("P028 feature", ORDER, key="p028_feature")
        if channel is None:
            raise ValueError("P028_EMPTY_FEATURE_SELECTOR")
        st.dataframe(features.loc[features.case_id.eq(case) & features.feature.eq(channel)])
        peers = s.table(f"{arm}/refit/case_peer_hidden.parquet")
        st.dataframe(peers.loc[peers.case_id.eq(case)])
        st.dataframe(s.table(f"{arm}/refit/case_state_history.parquet").query("case_id == @case"))
        st.dataframe(s.table(f"{arm}/refit/case_mechanisms.parquet").query("case_id == @case"))
    elif view == "Mechanisms":
        st.json(json.loads(s.file(f"{arm}/{split}/mechanisms.json").read_text()))
        st.dataframe(s.table(f"{arm}/{split}/peer_input_sensitivity.parquet"))
        st.dataframe(s.table(f"{arm}/{split}/state_module_diagnostics.parquet"))
        st.dataframe(s.table(f"{arm}/{split}/state_endpoints.parquet"))
        st.json(json.loads(s.file(f"{arm}/refit/case_selection_coverage.json").read_text()))
        st.caption(FAIRNESS + " A12 LOW development one long episode is descriptive only.")
    elif view == "State Information Control":
        summary = json.loads(s.file(f"{arm}/{split}/peer_information_control.json").read_text())
        st.json(summary)
        st.dataframe(s.table(f"{arm}/{split}/peer_shift_mapping.parquet"))
        st.dataframe(s.table(f"{arm}/{split}/peer_shift_slices.parquet"))
        if summary["matched_origins"]:
            original = s.table(f"{arm}/{split}/peer_original_matched.parquet")
            changed = s.table(f"{arm}/{split}/peer_shifted_matched.parquet")
            st.plotly_chart(
                px.scatter(
                    x=original.pred_original_TG20,
                    y=changed.pred_original_TG20,
                    labels={
                        "x": "Original matched prediction",
                        "y": "Earlier state; own unchanged",
                    },
                ),
                key="p028_control",
            )
            st.json(json.loads(s.file(f"{arm}/{split}/peer_shift_paired.json").read_text()))
        else:
            st.info(
                "No valid causal same-slot donors; empty diagnostic cohort, population unchanged."
            )
        st.caption(
            (
                "Ten preceding input-eligible sessions, same slot, matched subset"
                " only. Distribution shift, not a trained permutation null or p-v"
                "alue."
            )
        )
    elif view == "History / Features":
        ticker = st.selectbox("P028 ticker", SYMBOLS, key="p028_ticker")
        f = s.population(arm, split)
        st.dataframe(f.loc[f.ticker.eq(ticker)])
        if ticker is None:
            raise ValueError("P028_EMPTY_HISTORY_STOCK")
        channel = st.selectbox("P028 channel", ORDER, key="p028_channel")
        first = str(f.session_date_et.min())
        last = str(
            min(
                pd.Timestamp(first) + pd.Timedelta(days=10), pd.Timestamp(f.session_date_et.max())
            ).date()
        )
        start = st.text_input("P028 history start", first, key="p028_history_start")
        end = st.text_input("P028 history end", last, key="p028_history_end")
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
                key="p028_history_candles",
            )
            st.dataframe(candles)
        origin = st.selectbox("P028 origin context", (1, 2), key="p028_origin_context")
        if channel is None or origin is None:
            raise ValueError("P028_EMPTY_HISTORY_FEATURE")
        features = history.features(ticker, start, end, role(split), origin)
        selected = features.loc[features.feature.eq(channel)]
        st.plotly_chart(
            px.line(selected, x="hour_end_utc", y=["native", "model_scaled"]),
            key="p028_history_feature",
        )
        st.dataframe(selected)

    else:
        epochs = s.table(f"{arm}/epochs.parquet")
        st.dataframe(epochs)
        st.plotly_chart(
            px.line(
                epochs,
                x="epoch",
                y=["optimized_objective", "original_mse", "validation_original_mse"],
                facet_col="phase",
            ),
            key="p028_fit_curves",
        )
        st.caption(
            "Training online dropout ON; validation fixed epoch dropout OFF. "
            "z-MSE and original TG20 MSE are distinct. Qualification and raw-best "
            "epochs are both recorded."
        )
        updates = s.table(f"{arm}/updates.parquet")
        st.dataframe(updates)
        norms = [
            c
            for c in ("preclip_norm", "postclip_norm", "update_norm", "weight_norm", "raw_sd")
            if c in updates
        ]
        st.dataframe(updates[norms].quantile([0, 0.5, 0.9, 0.95, 0.99, 1]))
        st.plotly_chart(
            px.line(updates, x="batch_index", y=["preclip_norm", "postclip_norm"]),
            key="p028_gradients",
        )


def panel(root: Path) -> None:
    guard_query(st.query_params)
    st.title(SECTION)
    config = root / "configs/track_a_p028_visualization_v1.json"
    if not config.exists():
        st.info(
            (
                "P028 human approval recorded; technical release/gated results pending. Candidate"
                " results are not yet available."
            )
        )
        return
    s = StateStudy.discover(root)
    available = tuple(s.config.get("available_arms", ARMS))
    if "arm" in st.query_params and st.query_params["arm"] not in available:
        raise ValueError("P028_ARM_NOT_COMPLETED_BEFORE_PREDICTION_LOOKUP")
    arm = st.selectbox("P028 arm", available, key="p028_arm")
    split = st.selectbox("P028 role", ROLES, key="p028_role", index=3)
    view = st.selectbox("P028 view", VIEWS, key="p028_view")
    if arm is None or split is None or view is None:
        raise ValueError("P028_EMPTY_SELECTOR_BEFORE_NUMERIC_IO")
    guard(arm, split)
    st.caption(
        (
            "Pinned HF1M/FT16/TG20; approved two panel proxies; A7/A8/A"
            "6; seed42; inner vs refit "
            "recipes; development exploratory; protected2026 LOCKED."
        )
    )
    st.json(s.config.get("model_bindings", {}).get(arm, {}))
    show(s, arm, split, view)


def verify_payload(destination: Path, result: dict, *, plan: dict, rehearsal: bool) -> Path:
    """Fresh read-only process must exercise this arm's real component inputs before PASS."""
    root = destination / "ui_payload"
    root.mkdir(exist_ok=False)
    arm = result["arm"]
    files = {}
    from ..state_screen_authority import rows
    from ..state_screen_spec import AUDIT, PREPARATION, SCIENCE

    context = dict(
        scope=result["scope"],
        ledger=59 if rehearsal else rows()[-1]["global_started_pairs"],
        input_contract=plan["input_contract"],
        execution_sha256=result["execution_sha256"],
        science=plan["scientific_definitions"],
        authorization_scope=plan.get("authorization_scope"),
        source_audit=ref(AUDIT),
        cache_manifest=ref(PREPARATION / "state_cache_manifest.json"),
        architecture=SCIENCE[result["arm"]],
        support=SCIENCE["support"],
        source_support=json.loads(AUDIT.read_text())["proposed_regime_support"],
        protected_numeric_access=False,
        source_publication_independently_verified=False,
        rights="Existing researcher-attested bounded local use only",
        information_attribution=FAIRNESS,
    )
    write_json(root / "context.json", context)
    files["context.json"] = ref(root / "context.json")
    for p in sorted(destination.rglob("*")):
        if p.is_file() and p.suffix in (".parquet", ".json", ".md"):
            files[f"{arm}/{p.relative_to(destination)}"] = ref(p)
    updates = pd.DataFrame(
        [json.loads(v) for v in checked(result["optimizer_telemetry"]).read_text().splitlines()]
    )
    updates["batch_index"] = range(len(updates))
    # Forward-only dry runs honestly have empty gradient dictionaries. Keep their
    # exact JSON instead of fabricating a Parquet struct child or gradient value.
    for column in updates:
        if updates[column].map(lambda value: isinstance(value, (dict, list))).any():
            updates[column] = updates[column].map(lambda value: json.dumps(value, sort_keys=True))
    for key, frame in [
        ("updates", updates),
        (
            "epochs",
            pd.DataFrame(
                [
                    dict(
                        phase=e["phase"],
                        **e["training"],
                        validation_original_mse=e.get("validation", {}).get("original_mse"),
                        qualifies=e.get("qualifies"),
                        selected_epoch=e.get("selector", {}).get("selected"),
                        raw_best_epoch=e.get("selector", {}).get("raw_epoch"),
                    )
                    for e in result["epochs"]
                ]
            ),
        ),
    ]:
        for column in frame:
            if frame[column].map(lambda value: isinstance(value, (dict, list))).any():
                frame[column] = frame[column].map(lambda value: json.dumps(value, sort_keys=True))
        frame.to_parquet(root / (key + ".parquet"), index=False)
        files[f"{arm}/{key}.parquet"] = ref(root / (key + ".parquet"))
    comparison = []
    for split in ROLES:
        m = json.loads((destination / split / "metrics.json").read_text())
        comparison.append(
            dict(
                arm=arm,
                role=split,
                original_TG20_MSE=m["mse"],
                daily_IC=m["daily_ic"],
                actual_z_MSE=m["optimized_z_mse"],
            )
        )
    pd.DataFrame(comparison).to_parquet(root / "comparison.parquet", index=False)
    files["comparison.parquet"] = ref(root / "comparison.parquet")
    for name, text in [
        (
            "guide.md",
            f"# P028 {arm} source-bound read-only component probe\n\n{FAIRNESS}\n\n"
            "Choose a role and view. Refit is in sample; development exploratory. "
            "Protected2026 blocked. No fitting.",
        ),
        (
            "comparison.md",
            "# Scope\n\n"
            + result["scope"]
            + (
                "; raw TG20 MSE and actual optimized z-MSE remain distinct. Peer "
                "destruction is a distribution shift, not a trained null."
            ),
        ),
    ]:
        (root / name).write_text(text + "\n")
        files[name] = ref(root / name)
    write_json(
        root / "manifest.json",
        dict(
            arm=arm,
            scope=result["scope"],
            files=files,
            rehearsal=rehearsal,
            execution_sha256=result["execution_sha256"],
        ),
    )
    with (root / "component_execution.txt").open("x") as stream:
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "lstm_data.visualization.state_screen_ui",
                "--verify-payload",
                str(root / "manifest.json"),
            ],
            stdout=stream,
            stderr=subprocess.STDOUT,
            timeout=600,
        )
    if completed.returncode:
        raise ValueError(f"P028_UI_COMPONENT_STOP: {root / 'component_execution.txt'}")
    receipt = root / "component_receipt.json"
    r = json.loads(receipt.read_text())
    if (
        r["status"] != "PASS_P028_ARM_COMPONENTS"
        or r["arm"] != arm
        or r["role_view_pairs"] != len(ROLES) * len(VIEWS)
        or r["case_choices"] != 22
        or r["optimizer_step_calls"] != 0
    ):
        raise ValueError("P028_COMPLETE_ARM_UI_REQUIRED")
    return receipt


def component_probe(manifest_path: Path) -> None:
    """Standalone actual Streamlit test; no model forward or training is invoked by the UI."""
    from unittest.mock import patch

    import torch
    from streamlit.testing.v1 import AppTest

    torch.set_num_threads(4)
    manifest = json.loads(manifest_path.read_text())
    for reference in manifest["files"].values():
        checked(reference)
    arm = manifest["arm"]
    source = f"""from pathlib import Path
import json
import streamlit as st
from lstm_data.visualization.state_screen_ui import StateStudy,show,guard_query,VIEWS
from lstm_data.state_screen_spec import ROLES
try:
    guard_query(st.query_params)
except ValueError as exc:
    st.error(str(exc))
    st.stop()
s=StateStudy(Path.cwd(),json.loads({json.dumps(manifest["files"])!r}),{manifest["scope"]!r},{{}})
r=st.selectbox('Role',ROLES,key='role')
v=st.selectbox('View',VIEWS,key='view')
show(s,{arm!r},r,v)
"""
    pairs = 0
    choices = 0
    with patch.object(
        torch.optim.AdamW, "step", side_effect=AssertionError("UI_OPTIMIZER_FORBIDDEN")
    ) as forbidden:
        app = AppTest.from_string(source, default_timeout=90).run()
        if app.exception or app.error:
            raise ValueError("P028_INITIAL_COMPONENT")
        for split in ROLES:
            app.selectbox(key="role").select(split)
            for view in VIEWS:
                app.selectbox(key="view").select(view).run()
                pairs += 1
                if app.exception or app.error:
                    raise ValueError(
                        f"P028_COMPONENT_{arm}_{split}_{view}: "
                        f"{[e.message for e in app.exception]} {[e.value for e in app.error]}"
                    )
                if view == "Exact Cases":
                    figure = json.loads(app.get("plotly_chart")[0].proto.spec)
                    if (
                        figure["data"][0]["type"] != "candlestick"
                        or len(figure["layout"]["shapes"]) != 3
                    ):
                        raise ValueError("P028_REAL_CANDLE_PLOT_REQUIRED")
                if view == "Actual-Objective Tails":
                    cohorts = pd.read_parquet(checked(manifest["files"][f"{arm}/cohorts.parquet"]))
                    empty = cohorts.loc[cohorts.role.eq(split) & cohorts.rows.eq(0)]
                    for name in empty.cohort.head(1):
                        app.selectbox(key="p028_cohort").select(name).run()
                        if app.exception or app.error:
                            raise ValueError("P028_EMPTY_COHORT_RENDER")
        cases = pd.read_parquet(checked(manifest["files"][f"{arm}/refit/cases.parquet"]))
        app.selectbox(key="view").select("Exact Cases").run()
        for row in cases.to_dict("records"):
            app.selectbox(key="p028_case_ticker").select(row["ticker"]).run()
            app.selectbox(key="p028_case").select(row["case_id"]).run()
            choices += 1
            if app.exception or app.error:
                raise ValueError("P028_CASE_COMPONENT")
        app.selectbox(key="view").select("History / Features").run()
        for ticker in SYMBOLS:
            app.selectbox(key="p028_ticker").select(ticker).run()
            if app.exception or app.error:
                raise ValueError("P028_TICKER_COMPONENT")
        for channel in ORDER:
            app.selectbox(key="p028_channel").select(channel).run()
            if app.exception or app.error:
                raise ValueError("P028_FEATURE_COMPONENT")
        for query in (
            {"date": "2026-01-01"},
            {"role": "confirmation"},
            {"date": ""},
            {"arm": "A1"},
        ):
            app.query_params.clear()
            app.query_params.update(query)
            app.run()
            if not app.error or app.exception:
                raise ValueError("P028_PROTECTED_COMPONENT_GUARD")
        if forbidden.call_count:
            raise ValueError("P028_UI_STEPPED")
    write_json(
        manifest_path.parent / "component_receipt.json",
        dict(
            status="PASS_P028_ARM_COMPONENTS",
            arm=arm,
            scope=manifest["scope"],
            role_view_pairs=pairs,
            case_choices=choices,
            stock_histories=20,
            feature_channels=16,
            guarded_routes=4,
            optimizer_step_calls=0,
            manifest=ref(manifest_path),
            files_fingerprint=fingerprint(manifest["files"]),
            execution_sha256=manifest["execution_sha256"],
        ),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-payload", type=Path, required=True)
    component_probe(parser.parse_args().verify_payload)
