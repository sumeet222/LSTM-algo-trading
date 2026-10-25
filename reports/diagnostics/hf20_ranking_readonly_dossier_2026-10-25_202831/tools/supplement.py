"""Read-only minute observability, archived model inventory, and source-clock witnesses."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from audit import BASE, ROLES, Reader, digest, table, weights


def references(node: object) -> list[dict]:
    found = []
    if isinstance(node, dict):
        if "path" in node and "sha256" in node:
            found.append(node)
        else:
            for value in node.values():
                found.extend(references(value))
    elif isinstance(node, list):
        for value in node:
            found.extend(references(value))
    return found


def inventory(out: Path) -> None:
    roots = [
        Path("reports/experiments/ta021_hf1m_long_four_lstm_2026-10-22_232248_recovery_v1"),
        Path("reports/experiments/ta022_hf1m_long_objective_screen_2026-10-23_repair_preparation"),
        Path("reports/experiments/ta023_hf1m_long_dm1_qr1_ss1_2026-10-23_preparation"),
        Path("reports/experiments/ta024_hf1m_long_optimization_2026-10-23_preparation_v3"),
        Path("reports/experiments/ta024_hf1m_long_optimization_2026-10-23_recovery_preparation_v1"),
        Path("artifacts/hf20_hf1m_long_v1/p025_seed123_preparation/approved_runs"),
        Path("artifacts/hf20_hf1m_long_v1/p026_approved_runs"),
        Path("artifacts/hf20_hf1m_long_v1/p027_approved_runs"),
        BASE,
    ]
    models, evidence = [], []
    stage7 = json.loads(
        Path(
            "reports/experiments/ta022_hf1m_long_objective_screen_2026-10-23_repair_preparation/stage7_view_manifest.json"
        ).read_text()
    )["files"]
    for root in roots:
        for path in sorted(root.glob("HF1M-LONG-*/run_result.json")):
            d = json.loads(path.read_text())
            if d.get("run_id", "").startswith("HF1M-LONG-"):
                refs = references(d)
                selected = [r for r in refs if Path(r["path"]).suffix in (".pt", ".parquet")]
                if root.name.endswith("repair_preparation"):
                    arm = d.get("arm")
                    selected += [
                        r for k, r in stage7.items() if k == f"{arm}/development/population.parquet"
                    ]
                # Inventory exact metadata/bytes only: do not decode other-arm outputs/checkpoints.
                for r in selected:
                    q = Path(r["path"])
                    if q.exists():
                        actual = digest(q)
                        if actual != r["sha256"]:
                            raise ValueError("ARCHIVED_MODEL_REFERENCE_CHANGED")
                        evidence.append(dict(run_id=d["run_id"], **r, verified_sha256=actual))
                pops = d.get("populations", {})
                prediction_refs = [
                    r
                    for r in selected
                    if Path(r["path"]).suffix == ".parquet"
                    and any(
                        role in Path(r["path"]).name or f"/{role}/population.parquet" in r["path"]
                        for role in ROLES
                    )
                ]
                models.append(
                    dict(
                        run_id=d["run_id"],
                        arm=d.get("arm", d.get("variant", {}).get("arm")),
                        seed=d.get("seed", d.get("variant", {}).get("seed")),
                        seed_declared_run_id=d["run_id"].split("-S")[-1].split("-")[0],
                        status=d.get("status"),
                        result_path=str(path),
                        result_sha256=digest(path),
                        roles=json.dumps(
                            list(pops)
                            if pops
                            else [r for r in ROLES if any(r in x["path"] for x in prediction_refs)]
                        ),
                        source_contract=(
                            "P020 7adfec916b7eb74fead83ef1fe6082ff0fcee9ff0b6ebae5722077e2a82c01a5"
                        ),
                        horizon="four-hour historical price-only TG20",
                        feature=(
                            "FT16; architecture-specific additions declared in source "
                            "result/settings"
                        ),
                        checkpoint_refs=json.dumps(
                            [r for r in selected if r["path"].endswith(".pt")]
                        ),
                        forecast_refs=json.dumps(prediction_refs),
                        actual_objective=(
                            "E1: weighted three-class CE; QR1: pinball; DM1: "
                            "direction/magnitude; other arm formula in frozen settings/recipe; "
                            "T2 architectures: z-MSE"
                        ),
                        settings_json=json.dumps(d.get("settings", d.get("recipes", {}))),
                        chrono_status=(
                            "inner/refit in sample; inner validation selects; development "
                            "reused exploratory; no earlier-cutoff OOS folds in these run receipts"
                        ),
                        fit_seconds=d.get("seconds", d.get("wall_seconds")),
                    )
                )
    table(out, "model_inventory_v2.csv", models)
    (out / "model_artifact_references_v2.json").write_text(json.dumps(evidence, indent=2) + "\n")


def minute_audit(out: Path) -> None:
    manifest = json.loads((out / "minute_read_manifest.json").read_text())
    rows, proxy_rows = [], []
    for r in manifest["files"]:
        if r["month"] not in ("2015-11", "2025-07") or r["month"] >= "2026-01":
            raise ValueError("PROTECTED_MONTH_BEFORE_IO")
        path = Path(r["path"])
        if digest(path) != r["sha256"]:
            raise ValueError("MINUTE_HASH_MISMATCH")
        day = "2015-11-02" if r["month"] == "2015-11" else "2025-07-15"
        start = pd.Timestamp(day, tz="America/New_York").tz_convert("UTC")
        end = start + pd.Timedelta(days=1)
        # Predicate pushdown selects only two predeclared securities and one day per file.
        f = pd.read_parquet(
            path,
            filters=[
                ("ticker", "in", ["AAPL", "VZ"]),
                ("timestamp", ">=", start),
                ("timestamp", "<", end),
            ],
        )
        if r["kind"] == "fill_proxies_cap5":
            proxy_rows.append(
                dict(
                    day=day,
                    rows=len(f),
                    reasons=json.dumps(f.fill_reason.value_counts().to_dict()),
                    age_basis=(
                        "gap_length_known_at_completion and available_at_utc; prices not "
                        "substituted here"
                    ),
                )
            )
            continue
        assert f.is_genuine.all() and not f.is_imputed.any()
        f["et"] = pd.to_datetime(f.timestamp, utc=True).dt.tz_convert("America/New_York")
        for ticker in ("AAPL", "VZ"):
            for hour in (9, 10):
                lo = pd.Timestamp(day + f" {hour}:30", tz="America/New_York")
                g = f.loc[
                    f.ticker.eq(ticker) & f.et.ge(lo) & f.et.lt(lo + pd.Timedelta(hours=1))
                ].sort_values("timestamp")
                if g.empty:
                    rows.append(dict(day=day, ticker=ticker, hour=hour, status="MISSING_NO_REPAIR"))
                    continue
                p = g.close.to_numpy(float)
                changes = np.diff(np.log(p))
                middle = g.loc[g.et.lt(lo + pd.Timedelta(minutes=30))]
                cut = float(middle.close.iloc[-1]) if len(middle) else np.nan
                rows.append(
                    dict(
                        day=day,
                        ticker=ticker,
                        hour=hour,
                        status="OBSERVED_SOURCE_ONLY",
                        observed_minutes=len(g),
                        minute_zero_volumes=int(g.volume.eq(0).sum()),
                        early_log_move=float(np.log(cut / float(g.open.iloc[0]))),
                        late_log_move=float(np.log(float(g.close.iloc[-1]) / cut)),
                        close_path_realized_variation=float(changes @ changes),
                        high_minute=str(g.loc[[g.high.idxmax()], "et"].iloc[0]),
                        low_minute=str(g.loc[[g.low.idxmin()], "et"].iloc[0]),
                        max_observed_gap_minutes=float(
                            g.timestamp.diff().dt.total_seconds().max() / 60
                        ),
                        first_source_row=int(g.source_row.iloc[0]),
                        last_source_row=int(g.source_row.iloc[-1]),
                        source_path=str(path),
                        source_sha256=r["sha256"],
                        units=(
                            "unadjusted canonical minute source; no cross-action return or "
                            "new label"
                        ),
                    )
                )
    table(out, "minute_path_observability_cases.csv", rows)
    table(out, "minute_proxy_support_cases.csv", proxy_rows)


def source_and_rank_strata(out: Path) -> None:
    reader = Reader(out)
    contract = json.loads(Path(reader.manifest["source_contract"]["path"]).read_text())
    origins = reader.table(Path(contract["files"]["origins"]["path"]), "refit")
    grid = reader.table(Path(contract["files"]["grid"]["path"]), "refit")
    overlay_path = next(
        Path(k) for k in reader.refs if k.endswith("P020_hour_provenance_overlay.parquet")
    )
    overlay = reader.table(overlay_path, "refit")
    quality = reader.table(Path(contract["files"]["candles_quality"]["path"]), "refit")
    q = quality.merge(
        overlay[["hour_id", "terminal_input_price_age_minutes", "issue_reasons"]],
        on="hour_id",
        validate="one_to_one",
    )
    source_rows, rankrows, clockrows = [], [], []
    for role in ROLES:
        selected = origins.loc[origins[role + "_admitted"]].sort_values("origin_id")
        union = np.zeros(len(grid), bool)
        for r in selected.to_dict("records"):
            union[int(r["first_step"]) : int(r["entry_index"]) + 1] = True
        g = q.loc[q.step.isin(np.flatnonzero(union))]
        for (ticker, year), a in g.groupby(["ticker", g.session_date_et.str[:4]]):
            source_rows.append(
                dict(
                    role=role,
                    ticker=ticker,
                    year=year,
                    unique_hours=len(a),
                    age_max=float(a.terminal_input_price_age_minutes.max()),
                    age_mean=float(a.terminal_input_price_age_minutes.mean()),
                    close_proxy_hours=int(a.terminal_input_price_age_minutes.gt(0).sum()),
                    genuine_open_missing=int((~a.genuine_open).sum()),
                    genuine_close_missing=int((~a.genuine_close).sum()),
                    incomplete_extrema=int((~a.extrema_complete).sum()),
                    missing_assumed_zero=int(a.assumed_zero_missing_count.sum()),
                    volume_lower_bound_hours=int(a.hourly_volume_lower_bound.sum()),
                )
            )
        # Predeclare first origin of each slot after relevant calendar/source event.
        regular_counts = grid.groupby("session_date_et").size()
        short_days = set(regular_counts[regular_counts < 6].index)
        conditions = {
            "EARLY_CLOSE_IN_INPUT": lambda s: s.session_date_et.isin(short_days).any(),
            "HOLIDAY_OR_WEEKEND_IN_INPUT": lambda s: (
                pd.to_datetime(s.hour_end_utc, utc=True)
                .diff()
                .dt.total_seconds()
                .gt(48 * 3600)
                .any()
            ),
        }
        for label, condition in conditions.items():
            for r in selected.to_dict("records"):
                seq = grid.iloc[int(r["first_step"]) : int(r["entry_index"]) + 1]
                if condition(seq):
                    clockrows.append(
                        dict(
                            role=role,
                            case=label,
                            origin_id=r["origin_id"],
                            issuance=str(r["issuance_utc"]),
                            target_start=str(r["entry_end_utc"]),
                            target_end=str(r["exit_end_utc"]),
                            maturity=str(r["label_maturity_utc"]),
                            full48_clock=json.dumps(seq.hour_end_utc.astype(str).tolist()),
                            short_session_dates=json.dumps(
                                sorted(set(seq.session_date_et) & short_days)
                            ),
                        )
                    )
                    break
        for arm in ("A7", "A12"):
            f = reader.table(
                BASE / f"{arm}_immediate_diagnostics" / role / "population.parquet", role
            )
            f["stock_order"] = f.ticker.map({s: i for i, s in enumerate(contract["symbols"])})
            f = f.sort_values(["origin_id", "stock_order"]).reset_index(drop=True)
            w = weights(f)
            yr = pd.DataFrame(f.TG20.to_numpy().reshape(-1, 20)).rank(axis=1).to_numpy()
            pr = (
                pd.DataFrame(f.pred_original_TG20.to_numpy().reshape(-1, 20))
                .rank(axis=1)
                .to_numpy()
            )
            yc, pc = yr - yr.mean(1)[:, None], pr - pr.mean(1)[:, None]
            norm = np.sqrt((yc * yc).sum(1) * (pc * pc).sum(1))
            # Multiply by20 because each row has 1/20 of its origin's weight.
            contribution = np.divide(
                20 * yc * pc, norm[:, None], out=np.full_like(yc, np.nan), where=norm[:, None] > 0
            ).reshape(-1)
            err = (abs(yr - pr) / 19).reshape(-1)
            for group in ("ticker", "quality", "fallback_state", "V1_state"):
                for label, idx in f.groupby(group).indices.items():
                    mass = w[idx].sum()
                    rankrows.append(
                        dict(
                            role=role,
                            model=arm,
                            group=group,
                            label=str(label),
                            weight_mass=mass,
                            rank_mae=float(w[idx] @ err[idx] / mass),
                            signed_daily_ic_contribution=float(w[idx] @ contribution[idx]),
                            meaning=(
                                "cross-sectional contribution; not stockwise time-series "
                                "correlation"
                            ),
                        )
                    )
    table(out, "source_age_by_role_stock_year.csv", source_rows)
    table(out, "ranking_quality_stock_strata.csv", rankrows)
    table(out, "calendar_edge_cases.csv", clockrows)
    (out / "supplement_receipt.json").write_text(
        json.dumps(
            dict(
                status="PASS_BOUNDED_OFFLINE",
                numeric_reads=reader.reads,
                no_fitting=True,
                no_model_forwards=True,
            ),
            indent=2,
        )
        + "\n"
    )


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--inventory-only", action="store_true")
    args = p.parse_args()
    if args.inventory_only:
        inventory(args.out)
        return
    if (args.out / "model_inventory_v2.csv").exists():
        raise ValueError("NO_OVERWRITE")
    inventory(args.out)
    minute_audit(args.out)
    source_and_rank_strata(args.out)


if __name__ == "__main__":
    main()
