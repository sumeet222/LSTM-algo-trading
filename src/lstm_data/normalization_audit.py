"""Package012A read-only FT0 audit. Run with --out <NEW package directory>."""

from __future__ import annotations

import argparse
import gzip
import json
import os
import platform
import resource
import subprocess
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

from .config import digest
from .config import write_json as write_new_json
from .ft0_transforms import ORDER, SCALED, identity
from .normalization_population import (
    BOUNDED,
    PARTS,
    PREFIX,
    Population,
    audit_guard,
    fit_records,
    population,
    preparations,
    resolve_example_consumers,
    verify_fit_binding,
)
from .normalization_stats import (
    THRESHOLDS,
    clipping_collisions,
    distribution,
    independent_scaler_check,
)
from .pretraining_policy import CANDIDATE
from .pretraining_tables import BaseTables
from .stock_source import numeric
from .visualization.controlled import Study
from .visualization.loaders import Catalog, component_base


def write_csv(out: Path, name: str, rows: list[dict]) -> None:
    path = out / name
    if path.exists():
        raise FileExistsError(path)
    pd.DataFrame(rows).to_csv(path, index=False, float_format="%.17g")


def write_json(path: Path, value: dict) -> None:
    """Serialize historical timestamp metadata while retaining exclusive new-file writes."""
    write_new_json(path, json.loads(json.dumps(value, default=str)))


def summarize(
    pop: Population, tables: dict[str, list[dict]], histograms: list[dict], tail_ids: list[dict]
) -> None:
    for feature in ORDER:
        channel = pop.channel(feature)
        for representation in ("native", "scaled"):
            field = feature if representation == "native" else feature + "_scaled"
            for stock in ("POOLED", *CANDIDATE):
                part = channel if stock == "POOLED" else channel.loc[channel.symbol.eq(stock)]
                values = part[field].to_numpy(dtype=float)
                tags = pop.tags(feature, representation, stock)
                stats = distribution(values, feature in BOUNDED)
                tables["distribution"].append(
                    {
                        **tags,
                        **stats,
                        "first_UTC": str(part.timestamp.min()),
                        "last_UTC": str(part.timestamp.max()),
                        "ever_model_input_count": int(part.ever_model_input.sum()),
                        "excluded_origins": sum(pop.metadata["exclusions"].values()),
                        "synthetic_count": 0,
                    }
                )
                finite = values[np.isfinite(values)]
                counts, edges = np.histogram(finite, bins=32)
                histograms.append(
                    {
                        **tags,
                        "unique_observations": len(part),
                        "edges": edges.tolist(),
                        "counts": counts.tolist(),
                    }
                )
                if representation == "scaled":
                    for threshold in THRESHOLDS:
                        tail = part.loc[part[field].abs().gt(threshold)]
                        keys = [
                            f"{r.symbol}|{r.timestamp}|{r.origin if feature == 'M2' else 0}"
                            for r in tail.sort_values(["timestamp", "origin"]).itertuples()
                        ]
                        keys = sorted(keys)
                        tail_ids.append(
                            {
                                **tags,
                                "abs_gt": threshold,
                                "identities": keys,
                                "identity_sha256": identity(keys),
                            }
                        )
            if representation == "scaled":
                for threshold in (3, 5, 10):
                    tables["clipping"].append(
                        {
                            **pop.tags(feature, representation),
                            **clipping_collisions(
                                channel[field].to_numpy(dtype=float),
                                channel[["symbol", "timestamp", "origin"]],
                                threshold,
                            ),
                        }
                    )
            # Compact monthly pooled drift and quarterly pooled/per-stock drift.
            for frequency, stocks in (("M", ("POOLED",)), ("Q", ("POOLED", *CANDIDATE))):
                period = channel.timestamp.dt.tz_convert("America/New_York").dt.tz_localize(None)
                dates = period.dt.to_period(frequency).astype(str)
                for stock in stocks:
                    part = channel if stock == "POOLED" else channel.loc[channel.symbol.eq(stock)]
                    for name, group in part.groupby(dates.loc[part.index], sort=True):
                        stats = distribution(group[field].to_numpy(dtype=float), feature in BOUNDED)
                        tables["temporal"].append(
                            {
                                **pop.tags(feature, representation, stock),
                                "frequency": frequency,
                                "period": name,
                                "first_UTC": str(group.timestamp.min()),
                                "last_UTC": str(group.timestamp.max()),
                                "ever_model_input_count": int(group.ever_model_input.sum()),
                                **{
                                    k: stats.get(k)
                                    for k in (
                                        "observed",
                                        "valid",
                                        "missing",
                                        "median",
                                        "MAD",
                                        "IQR",
                                        "abs_p99",
                                        "abs_gt_3_rate",
                                        "abs_gt_10_rate",
                                    )
                                },
                            }
                        )
        # Actual origin-context / slot descriptive comparisons, not window replication.
        for origin in (1, 2):
            context = pop.channel(feature, origin)
            for slot, group in context.groupby("slot"):
                tables["segments"].append(
                    {
                        **pop.tags(feature, "scaled"),
                        "origin": origin,
                        "slot": slot,
                        **distribution(group[feature + "_scaled"].to_numpy(dtype=float)),
                        "ever_model_input_count": int(group.ever_model_input.sum()),
                    }
                )
        for field in ("session_type", "ET_UTC_offset"):
            for name, group in channel.groupby(field):
                tables["segments"].append(
                    {
                        **pop.tags(feature, "scaled"),
                        "calendar_segment": field + "=" + str(name),
                        **distribution(group[feature + "_scaled"].to_numpy(dtype=float)),
                        "ever_model_input_count": int(group.ever_model_input.sum()),
                    }
                )
        for stock, group in channel.groupby("symbol"):
            values = group[feature + "_scaled"]
            # One maximum per feature/stock/population plus all tail identities in compressed JSON.
            valid = group.loc[values.notna()]
            if valid.empty:
                continue
            r = valid.iloc[int(np.argmax(valid[feature + "_scaled"].abs().to_numpy()))]
            prep = pop.preparation
            j = SCALED.index(feature) if feature in SCALED else None
            tables["examples"].append(
                {
                    **pop.tags(feature, "scaled", str(stock)),
                    "timestamp": str(r.timestamp),
                    "session": r.session,
                    "origin": int(r.origin),
                    "slot": int(r.slot),
                    "consuming_session": r.consuming_session,
                    "consuming_cutoff": r.consuming_cutoff,
                    "native": r[feature],
                    "scaled": r[feature + "_scaled"],
                    "center": prep.scaler.centers[j] if j is not None else 0.0,
                    "scale": prep.scaler.scales[j] if j is not None else 1.0,
                    "method": prep.scaler.methods[j] if j is not None else "BOUNDED_IDENTITY",
                    "source_lineage": r.source_lineage,
                    "flags": r["flags"],
                    "ever_model_input": bool(r.ever_model_input),
                    "selection": "largest |scaled|; descriptive",
                }
            )
    # Dependence reported separately for each origin context, no duplicate hourly contexts.
    for origin in (1, 2):
        frame = pop.frame.loc[pop.frame.origin.eq(origin)]
        for family in (
            ("M1", "M2", "M3", "M4"),
            ("V1", "V2", "V3"),
            ("T1", "T2", "T3", "T4", "T5"),
            ("Q1", "Q2"),
        ):
            names = [f + "_scaled" for f in family]
            values = frame[names]
            corr, ranks = values.corr(), values.rank().corr()
            for j, first in enumerate(family):
                for second in family[j + 1 :]:
                    a, b = first + "_scaled", second + "_scaled"
                    tables["dependence"].append(
                        {
                            **pop.tags(first, "scaled"),
                            "other_feature": second,
                            "origin": origin,
                            "pearson": corr.at[a, b],
                            "spearman": ranks.at[a, b],
                            "unique_observations": len(values),
                            "complete_pairs": int(values[[a, b]].notna().all(axis=1).sum()),
                            "interpretation": "Dependent stock/time; descriptive, no causation",
                        }
                    )


def scaler_records(pop: Population, base: BaseTables) -> tuple[list[dict], list[dict]]:
    checks, floors = [], []
    prep = pop.preparation
    for feature in ORDER:
        tags = pop.tags(feature, "native")
        if feature in SCALED:
            records = fit_records(pop, feature)
            j = SCALED.index(feature)
            check = independent_scaler_check(
                records[feature].to_numpy(dtype=float),
                records.origin.to_numpy() if feature == "M2" else None,
                prep.scaler.centers[j],
                prep.scaler.scales[j],
                prep.scaler.methods[j],
            )
            checks.append({**tags, "fit_records": len(records), **check})
        else:
            checks.append(
                {
                    **tags,
                    "fit_records": 0,
                    "method": "BOUNDED_IDENTITY",
                    "recorded_center": 0.0,
                    "recorded_scale": 1.0,
                    "passed": True,
                }
            )
    for p in prep.floors:
        floors.append(
            dict(
                fold=pop.fold,
                partition=pop.partition,
                recipe_id=prep.preparation_id,
                **asdict(p),
                clock="historical training prefix only",
                source_binding=prep.source_binding,
            )
        )
    return checks, floors


def stock_comparison(distributions: list[dict]) -> list[dict]:
    frame = pd.DataFrame(distributions)
    result = []
    for _, group in frame.groupby(["fold", "partition", "feature", "representation"]):
        pooled = group.loc[group.symbol.eq("POOLED")].iloc[0]
        for _, row in group.loc[~group.symbol.eq("POOLED")].iterrows():
            result.append(
                {
                    k: row[k]
                    for k in (
                        "fold",
                        "partition",
                        "feature",
                        "label",
                        "representation",
                        "symbol",
                        "recipe_id",
                        "units",
                        "clock",
                        "source_binding",
                    )
                }
                | dict(
                    unique_observations=row.observed,
                    ever_model_input_count=row.ever_model_input_count,
                    median=row["median"],
                    pooled_median=pooled["median"],
                    median_offset_over_pooled_IQR=(row["median"] - pooled["median"]) / pooled.IQR
                    if pooled.IQR
                    else None,
                    stock_IQR_over_pooled_IQR=row.IQR / pooled.IQR if pooled.IQR else None,
                    stock_abs_p99_over_pooled_abs_p99=row.abs_p99 / pooled.abs_p99
                    if pooled.abs_p99
                    else None,
                    stock_share_of_pooled_abs_gt3=row.abs_gt_3_count / pooled.abs_gt_3_count
                    if pooled.abs_gt_3_count
                    else None,
                )
            )
    return result


def floor_usage(pop: Population, base: BaseTables) -> list[dict]:
    """Measure activation of already-recorded floors and pseudocount shares, without refitting."""
    output = []
    for feature in ("M1", "M2", "M3", "M4", "V1", "V2", "V3", "Q1", "Q2"):
        channel = pop.channel(feature)
        for floor in pop.preparation.floors:
            frame = channel.loc[channel.symbol.eq(floor.symbol)]
            active = valid = 0
            shares = []
            bound = (
                floor.m2_floor
                if feature == "M2"
                else floor.daily_floor
                if feature in ("M3", "M4")
                else floor.hourly_pseudocount
                if feature == "Q1"
                else floor.daily_pseudocount
                if feature == "Q2"
                else floor.hourly_floor
            )
            for row in frame.itertuples():
                day, slot, origin = (
                    str(row.session),
                    int(numeric(row.slot)),
                    int(numeric(row.origin)),
                )
                v = base.components[floor.symbol, day, slot].values
                if feature == "M2":
                    raw = base.m2[floor.symbol, day, origin].rms60
                    bound = floor.m2_floor
                elif feature in ("M3", "M4"):
                    raw, bound = v["RMS63"], floor.daily_floor
                elif feature in ("M1", "V1", "V2", "V3"):
                    raw = v["RMS12"] if feature == "V1" else v["RMS60"]
                    bound = floor.hourly_floor
                else:
                    raw = v["Q1_MEAN"] if feature == "Q1" else v["Q2_60"]
                    bound = floor.hourly_pseudocount if feature == "Q1" else floor.daily_pseudocount
                    if raw is not None:
                        shares.append(bound / (raw + bound))
                if raw is not None:
                    valid += 1
                    active += raw < bound
            output.append(
                {
                    **pop.tags(feature, "native denominator", floor.symbol),
                    "observed": len(frame),
                    "valid_denominators": valid,
                    "ever_model_input_count": int(frame.ever_model_input.sum()),
                    "recorded_floor_or_pseudocount": bound,
                    "denominator_units": "adjusted shares"
                    if feature.startswith("Q")
                    else "dimensionless unlogged return RMS",
                    "below_floor_or_pseudocount_count": active,
                    "below_rate": active / valid if valid else None,
                    "pseudocount_denominator_share_p50": float(np.median(shares))
                    if shares
                    else None,
                    "pseudocount_denominator_share_p99": float(np.quantile(shares, 0.99))
                    if shares
                    else None,
                    "rule": "additive pseudocount, not a floor"
                    if feature.startswith("Q")
                    else "max(raw RMS, fitted floor); V3 row describes RMS60, V1 covers RMS12",
                }
            )
    return output


def run(root: Path, out: Path, end: str = "2024-06-30") -> None:
    audit_guard(end)  # Before any Catalog/store/scientific numerical reads or output creation.
    if not out.resolve().is_relative_to(root.resolve() / "reports/data_audit"):
        raise ValueError("Use a new reports/data_audit/ta012a_ft0_normalization_* directory.")
    if not out.name.startswith("ta012a_ft0_normalization_"):
        raise ValueError("Use the versioned ta012a_ft0_normalization_ namespace.")
    out.mkdir(parents=False, exist_ok=False)
    started, cpu = time.monotonic(), time.process_time()
    catalog = Catalog.discover(root)
    before = {name: digest(root / name) for name, _ in catalog.token() if (root / name).is_file()}
    base, study = component_base(catalog), Study.discover(catalog)
    views = preparations(catalog, base)
    tables: dict[str, list[dict]] = {
        k: []
        for k in (
            "distribution",
            "temporal",
            "segments",
            "examples",
            "dependence",
            "clipping",
            "scalers",
            "floors",
            "floor_usage",
        )
    }
    histograms: list[dict] = []
    tails: list[dict] = []
    populations, fit_checks = [], []
    for fold in ("WF1", "WF2"):
        for part in PARTS:
            pop = population(catalog, base, study, fold, part, views[fold, PREFIX[part]])
            print(f"{fold} / {part}: {len(pop.frame)} canonical context rows", flush=True)
            populations.append(pop.metadata)
            if part.endswith("training"):
                fit_checks.append(dict(fold=fold, partition=part, **verify_fit_binding(pop, base)))
                checks, floor = scaler_records(pop, base)
                tables["scalers"].extend(checks)
                tables["floors"].extend(floor)
            summarize(pop, tables, histograms, tails)
            tables["floor_usage"].extend(floor_usage(pop, base))
            del pop
    write_json(
        out / "population_and_recipe_bindings.json",
        dict(
            populations=populations,
            fit_population_hash_checks=fit_checks,
            source_manifest=catalog.config["source_manifest"],
            components=catalog.config["manifest"],
            study_seal=catalog.config["controlled_explorer"]["seal"],
            input_binding=study.refs["input_binding.json"],
            feature_order=ORDER,
            confirmation_numeric_rows=0,
            guard="Fixed scope pre-I/O; no protected partition accepted",
            git_commit=subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=root, text=True
            ).strip(),
            audit_code_sha256={
                str(p.relative_to(root)): digest(p)
                for p in sorted((root / "src/lstm_data").glob("normalization_*.py"))
            },
        ),
    )
    filenames = {
        "distribution": "ft0_normalization_distribution.csv",
        "temporal": "ft0_temporal_drift.csv",
        "segments": "ft0_origin_slot_audit.csv",
        "examples": "feature_replay_examples.csv",
        "dependence": "feature_dependence.csv",
        "clipping": "hypothetical_clipping_collisions.csv",
        "scalers": "ft0_tail_and_fallback_audit.csv",
        "floors": "floor_recipe_parameters.csv",
        "floor_usage": "ft0_floor_activation.csv",
    }
    for table, name in filenames.items():
        write_csv(out, name, tables[table])
    resolved = resolve_example_consumers(catalog, base, pd.DataFrame(tables["examples"]))
    resolved.to_csv(out / "feature_replay_examples_resolved.csv", index=False, float_format="%.17g")
    stability = []
    for row in tables["scalers"]:
        ref = next(
            v
            for v in tables["scalers"]
            if v["fold"] == "WF1"
            and v["partition"] == "Refit training"
            and v["feature"] == row["feature"]
        )
        stability.append(
            {
                **row,
                "scale_ratio_to_WF1_refit": row["recorded_scale"] / ref["recorded_scale"],
                "center_shift_in_WF1_refit_scale": (row["recorded_center"] - ref["recorded_center"])
                / ref["recorded_scale"],
                "reference_recipe_id": ref["recipe_id"],
            }
        )
    write_csv(out, "scaler_stability.csv", stability)
    write_csv(out, "ft0_stock_scale_comparison.csv", stock_comparison(tables["distribution"]))
    write_json(
        out / "histograms.json",
        dict(population="all canonical unique observations, not a sample", histograms=histograms),
    )
    (out / "tail_identity_sets.json.gz").write_bytes(
        gzip.compress(json.dumps(tails, separators=(",", ":")).encode(), mtime=0)
    )
    from .normalization_oracles import replay_oracles

    oracles = replay_oracles(catalog, base, tables["examples"])
    write_csv(out, "independent_feature_oracles.csv", oracles)
    after = {name: digest(root / name) for name in before}
    changed = [name for name in before if before[name] != after[name]]
    write_json(
        out / "preservation.json",
        dict(
            before=before,
            after=after,
            changed=changed,
            original_bound_files=len(before),
            pair_ledger="24/40",
        ),
    )
    numerical_pass = (
        all(v["passed"] for v in fit_checks)
        and all(v["passed"] for v in tables["scalers"])
        and all(v["passed"] for v in oracles)
    )
    write_json(
        out / "checks.json",
        dict(
            status="P012A_AUDIT_PASS" if numerical_pass and not changed else "P012A_AUDIT_HOLD",
            fit_hashes=fit_checks,
            original_artifacts_unchanged=not changed,
            scaler_oracles_passed=all(v["passed"] for v in tables["scalers"]),
            independent_oracles_passed=all(v["passed"] for v in oracles),
            confirmation_numeric_rows=0,
            new_fits=0,
            new_pairs=0,
            note="Software/static/UI tests recorded separately before human handoff",
        ),
    )
    from .normalization_report import publish_manifest, write_documents

    write_documents(out)
    write_json(out / "display_manifest.json", publish_manifest(catalog, out))
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    write_json(
        out / "resource_usage.json",
        dict(
            elapsed_seconds=time.monotonic() - started,
            cpu_seconds=time.process_time() - cpu,
            peak_RSS_bytes=rss if platform.system() == "Darwin" else rss * 1024,
            CPU=platform.processor(),
            machine=platform.machine(),
            logical_CPUs=os.cpu_count(),
            output_bytes=sum(p.stat().st_size for p in out.iterdir() if p.is_file()),
            dense_windows_written=0,
            raw_copies=0,
            feature_cache="RAM only; unique recipe rows",
        ),
    )
    if not numerical_pass or changed:
        raise ValueError("Affected numerical branch HOLD; evidence preserved in new package.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--end-date", default="2024-06-30")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    run(root, args.out.resolve(), args.end_date)


if __name__ == "__main__":
    main()
