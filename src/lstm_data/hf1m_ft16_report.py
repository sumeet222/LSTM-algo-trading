"""Seal P020 feature readiness and an untrained matched-pair handoff."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .hf1m_action_source import publish_json
from .hf1m_ft16_source import ORDER, checked, configuration, ref


def mdtable(columns: list[str], rows: list[list]) -> str:
    return (
        "\n".join(
            ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
            + ["| " + " | ".join(str(x).replace("|", "/") for x in row) + " |" for row in rows]
        )
        + "\n\n"
    )


def write(path: Path, text: str) -> None:
    if path.exists():
        if path.read_text() != text:
            raise ValueError("IMMUTABLE_REPORT_CHANGED: " + str(path))
    else:
        path.write_text(text)


def publish(out: Path) -> None:
    def read(name: str):
        return json.loads((out / name).read_text())

    config = configuration()
    d = read("model_input_contract.json")
    q = read("quantitative_qa.json")
    oracle = read("independent_oracle_and_causality.json")
    quality = read("quality_and_fit_prefix_receipt.json")
    tests = read("tests_static_receipt.json")
    fits = read("train_only_fit_recipes.json")
    if (
        oracle["result"] != "PASS"
        or quality["result"] != "PASS"
        or tests["static_errors"]
        or not tests["focused_tests_passed"]
    ):
        raise ValueError("STOP_FEATURE_UNSAFE: incomplete QA")
    ready = (
        d["split_counts"]["refit"] >= 3000
        and d["split_counts"]["development"] >= 100
        and q["train_years_at_least100"] >= 10
        and q["maximum_admitted_channel_fallback_fraction"] <= 0.8
        and q["final16_all_finite"]
    )
    status = "FEATURE_READY_FOR_TRAINING" if ready else "CONDITIONAL_FEATURE_READY"
    origin = pd.read_parquet(checked(d["files"]["origins"]))
    headline = f"**{status}. Dataset preparation only; neural training is not authorized.**\n\n"
    lineage = (
        "Only mito0o852/OHLCV-1m at revision `776328445b7ac6e7815ef3a483e9c8ded1eb6d56`. "
        "Parent `HF20_HF1M_LONG_v1_ACTION_QA_v1`, P019B current v3 action ledger and "
        "PRE_FEATURE_READY_WITH_QUARANTINES gate. All9 split events,6 "
        "genuine moves,18 quarantined "
        "RTH minutes/14 bins, EH/KO exclusion and COP boundary masks "
        "retained. Root anomaly register "
        "and all original source bytes are unchanged. No old "
        "Alpaca/Twelve Data numeric inputs, "
        "fitted statistics, model outputs or checkpoints.\n\n"
        "New IDs: `HF20_HF1M_LONG_v1_FT16_v1`, `HF20_HF1M_LONG_v1_TG20_4H_v1`, "
        "`HF20_HF1M_LONG_v1_MODEL_INPUT_v1`. Ordered20: " + ",".join(config["symbols"]) + ".\n\n"
        "Rights remain "
        "HUMAN_REPORTED_MAINTAINER_PERMISSION_FOR_PRIVATE_RESEARCH, not "
        "independent "
        "legal certification; numerical stores and price examples remain ignored/local. "
        "Publication timing remains UNKNOWN. Completed-hour end+2minute "
        "issuance and maturity are "
        "conditional research assumptions, not executable-fill evidence.\n\n"
    )
    dates = (
        "Frozen chronology: warmup2010-07-01–2011-03-31; research "
        "train2011-04-01–2025-06-30; "
        "inner train ends2023-01-23; nominal inner validation2023-01-24–2025-06-30; "
        "development2025-07-01–2025-12-31; protected confirmation2026-01-01–2026-03-31 "
        "(keys/calendar/source quality only). First48complete-hour "
        "contexts after fit cutoffs are "
        "embargoed. All horizons mature within the same session; no "
        "crossing labels survive. "
        "The nominal15calendar-year research/confirmation span "
        "contains14years3months of fitted "
        "training history plus9months earlier startup. Missing dates and "
        "hourly positions never compress.\n\n"
    )
    dates += mdtable(
        ["Split", "Admitted origins", "Stock rows", "First/last admitted date"],
        [
            [
                split,
                d["split_counts"][split],
                d["split_counts"][split] * 20,
                str(origin.loc[origin[split + "_admitted"], "session_date_et"].min())
                + " / "
                + str(origin.loc[origin[split + "_admitted"], "session_date_et"].max()),
            ]
            for split in ["inner_train", "inner_validation", "refit", "development"]
        ],
    )
    policies = (
        "For feature calculation only, an ABSENT minute contributes0 to "
        "volume. This is not evidence "
        "of no trades. Observed sums remain lower bounds; measured zeros, "
        "absent assumptions and "
        "unknown conflict/quarantine volumes have distinct flags. An "
        "hourly volume is usable only "
        "with at least one genuine minute, <=5 total absent minutes, "
        "longest gap<=5, no conflicting, "
        "quarantined or invalid minute. Sensitivities0/1/2/5 are reported "
        "without changing the declared "
        "threshold. Severe hours remain indexed and their volume channels missing.\n\n"
        "Q1 uses previous20matching slots (>=19 valid,maxgap2). Q2 uses "
        "previous5/60regular sessions "
        "(5/5 and57/60,maxgap2); a daily volume requires all6full-hour "
        "sums to meet the tier, excludes "
        "the closing stub and remains a six-hour lower bound, never "
        "verified full-day exchange volume. "
        "No inverse split share-volume multiplier is applied. Matching "
        "histories must remain in one "
        "volume_basis_id regime; ratios reset at split share-unit "
        "changes. Pseudocounts are1% of "
        "positive unique training medians separately by stock and "
        "compatible share regime; an "
        "unseen/unfitted regime stays missing and receives the documented "
        "feature fallback.\n\n"
        "Prices use only P019B bounded cap5 causal input closes. Genuine "
        "opening minutes are required "
        "for M1; independently observed trustworthy range is required for "
        "B1/B2. Partial ranges are "
        "observed ranges with extrema_complete=false, not certified "
        "complete-hour extrema. A proxy "
        "outside that observed range makes B2 missing, not clipped. "
        "Genuine15:30 last-full-hour closes "
        "on ordinary6hour sessions are independent prior-day close "
        "surrogates, not16:00 exchange "
        "closes. No stale earlier-hour or external daily close is substituted.\n\n"
        "For each historical step, M2 is session-locked to strictly prior "
        "regular sessions with "
        "already matured genuine same-origin4h outcomes. The forecast "
        "origin1/2 selects its history "
        "across all48steps; two small M2 contexts accompany15shared "
        "hourly channels, preserving "
        "the established16-channel tensor without storing overlapping windows.\n\n"
        "Invalid closes freeze EMA and disconnect the RSI predecessor; "
        ">=3consecutive invalid "
        "scheduled full-hour positions or a COP price-basis change reset "
        "state. Regular overnight "
        "closure is expected calendar progression, not an outage. T3/T4 "
        "require>=360usable updates "
        "and69/72recent valid closes,maxgap2. RSI requires14seed "
        "changes+140Wilder updates. All16 "
        "features are dimensionless and invariant to uniform future "
        "split-unit rescaling; independent "
        "multiplier7 and prefix tests passed with fixed fitting recipe.\n\n"
        "Native nonfinite values remain missing in stored components. For "
        "fixed-width model input, "
        "use native training medians for13unbounded channels and "
        "explicitly neutral0 for B2/T2/T5. "
        "Fit on the union of eligible training history keys, "
        "prefix-clipped, with no duplicated "
        "overlapping windows. M2 uses unique stock/session/origin keys "
        "and50/50origin mass. "
        "Fit separate inner/refit recipes. Scale13channels by pooled "
        "train median/unscaledMAD, "
        "then IQR/1.349, populationSD, or scale1 for an exact constant if "
        "needed. B2/T2/T5 remain "
        "native identity; there is no clipping, asinh input mapping or "
        "extra17th model channel. "
        "Full reason masks remain separate from inputs. Prefix-only "
        "recomputation reproduced every "
        "floor, pseudocount, scaler and fallback; no development fitting.\n\n"
    )
    policies += mdtable(
        ["Input category", "Computational action", "Retained evidence"],
        [
            [
                "Genuine price/volume",
                "Use valid observation",
                "source row/hash, genuine endpoints, completeness",
            ],
            ["Bounded price proxy", "Input-close continuity only", "proxy count/age, never target"],
            [
                "Absent minute volume",
                "Assume0 only for small-gap feature tier",
                "observed=false, lower bound, missing_assumed_zero=true",
            ],
            [
                "Conflicting source row",
                "No arbitrary selection or zero",
                "volume unknown, field/dependency masks",
            ],
            ["Material anomaly", "P019B local exclusion", "18minutes/14bins and causal masks"],
            [
                "Split share regime",
                "Reset volume history; never invented conversion",
                "volume_basis_id and reset reason",
            ],
            [
                "True missing/long gap",
                "Native missing then permitted train fallback; no price-window repair",
                "indexed gaps and channel fallback mask",
            ],
        ],
    )
    write(
        out / "P020_VOLUME_AND_FEATURE_IMPUTATION_POLICY.md",
        "# P020 volume and feature imputation\n\n"
        + headline
        + policies
        + "Source-wide minute assumptions in this permissible numeric span: "
        + str(quality["assumed_zero_minutes"])
        + " absent minutes; "
        + str(quality["unknown_conflict_quarantine_minutes"])
        + " conflict/quarantine/invalid minutes remain unknown. These "
        "include startup history and are not all admitted training "
        "observations. No complete48hour all20volume tape is claimed. See "
        "volume_quality_stock_year.csv, "
        "volume_threshold_sensitivity_stock_year.csv and "
        "source_channel_reason_rates_stock_year.csv.\n",
    )
    dictionary = read("formula_compatibility_frozen.json")
    table = mdtable(
        ["Order/name", "Formula", "History", "Inputs / availability", "Fallback / scaling"],
        [
            [
                str(i + 1) + " " + f["feature"],
                f["formula"],
                f["lookback"],
                f["source_and_cutoff"],
                f["fallback"] + "; " + f["scaling"],
            ]
            for i, f in enumerate(dictionary["features"])
        ],
    )
    write(
        out / "P020_FEATURE_DICTIONARY_AND_AUDIT.md",
        "# P020 FT16 dictionary and audit\n\n"
        + headline
        + table
        + policies
        + "Reference implementations were reviewed as mathematics only: "
        "hf20_features.py, hf20_transforms.py, stock_features.py and "
        "ft0_transforms.py. No prior dataset or fitted values were "
        "loaded. This new version intentionally adapts minute-quality "
        "volume tiers, channel fallbacks, share-regime resets and severe "
        "indicator gaps. It preserves16economic channel meanings and the "
        "prior approved independent15:30surrogate policy.\n\n"
        "Independent scalar source examples cover all16channels at three "
        "real dates/stocks (48checks), with operands retained privately. "
        "Prefix checks cover2011startup, COP2012,2020halt period and2024; "
        "a November2015 real example follows DST. Protected synthetic "
        "rows fail before computation. Original source future/stub "
        "perturbation leaves earlier48step features unchanged. Real "
        "arithmetic operands: independent_oracle_and_causality.json links "
        "the private Parquet.\n\n"
        "Exact fit values and populations: train_only_fit_recipes.json. "
        "Native availability, fallback runs and volume/proxy reliance: "
        "feature_missingness_stock_year.csv and "
        "source_channel_reason_rates_stock_year.csv. Train "
        "distributions/outliers/constants: "
        "feature_distributions_train_unique.csv; drift: "
        "feature_drift_train_vs_development.csv. Training input/target "
        "Spearman diagnostics are descriptive only and do not select "
        "features. No channel was dropped.\n",
    )
    target = (
        "At each allowed origin, "
        "r_i=log(genuine_exit_close/genuine_entry_close), m=median20(r), "
        "a=median20(abs(r-m)), TG20_i=(r_i-m)/(a+epsilon). "
        "Epsilon=max(1e-4,0.1median_unique_train(a)), "
        "fit independently for each training prefix using all "
        "complete20genuine mature origins, "
        "independent of feature values. No volatility scaling, 5stock "
        "cross-section, clipping or "
        "partial19/20target. If one genuine compatible endpoint is "
        "unavailable, all20labels are "
        "ineligible. No proxy, stub, overnight or COP-crossing price generates a label.\n\n"
        "Regular-session completed-end clocks:10:30→14:30 and11:30→15:30 "
        "ET, with issuance and "
        "maturity2minutes later under the inherited publication "
        "assumption. Early closes produce no "
        "synthetic four-hour horizon. Feature input admission is separate "
        "from eventual ex-post label "
        "validity. Historical M2 outcomes are distinct past own-stock "
        "source signals; current future "
        "TG20 labels are never feature arguments.\n\n"
        "T2 preprocessing "
        "s=max(median_unique_admitted_training_origin_stock(abs(TG20)),1e-"
        "6), "
        "z=asinh(TG20/s), inverse=s*sinh(z_prediction) exactly once. No "
        "learned model or target "
        "prediction was computed. C0 and T2 use the identical X, origin "
        "mask and original TG20 "
        "evaluation scale. Validation selection next package must use "
        "inverse-transformed original "
        "TG20 MSE, not transformed-space MSE or development results.\n\n"
    )
    target += mdtable(
        ["Fit", "Train end", "Epsilon", "Epsilon origins", "T2 scale", "T2 origins"],
        [
            [
                name,
                f["fit_stop_inclusive"],
                f["epsilon"],
                f["epsilon_origins"],
                f["t2_scale"],
                f["t2_scale_origins"],
            ]
            for name, f in fits.items()
        ],
    )
    target += (
        "Training target quantiles (uncapped): "
        + json.dumps(q["training_TG20_quantiles"])
        + ".\n\n"
    )
    target += (
        "Training-only tail thresholds: "
        + json.dumps(q["train_only_tail_thresholds"])
        + ". Tail mechanisms: "
        + json.dumps(q["tail_mechanism_counts"])
        + ". These thresholds are diagnostic labels, not target filters. "
        "Top absolute target, numerator and smallest-MAD examples remain "
        "private, with endpoint and source row links. Fifty extreme "
        "endpoints were independently verified against genuine candles. "
        "Protected2026numeric features/returns/targets were never "
        "calculated or stored.\n"
    )
    write(
        out / "P020_TARGET_TG20_AND_CLOCK_AUDIT.md",
        "# P020 TG20 and clock audit\n\n" + headline + target,
    )
    waterfall = mdtable(
        [
            "Split",
            "Scheduled",
            "Past input",
            "Finite FT16",
            "Future20",
            "Joint before embargo",
            "Final",
            "Stock rows",
        ],
        [
            [
                r["split"],
                r["scheduled"],
                r["past_source_input"],
                r["finite16_after_declared_fallback"],
                r["genuine20_future"],
                r["joint_before_fit_embargo"],
                r["final_admitted"],
                r["stock_rows"],
            ]
            for r in q["waterfall"]
        ],
    )
    fallbacks = mdtable(
        ["Feature", "Refit fallback %", "Development fallback %"],
        [
            [
                name,
                format(
                    next(
                        r["fallback_fraction"]
                        for r in q["admitted_fallback_rates"]
                        if r["split"] == "refit" and r["feature"] == name
                    ),
                    ".4%",
                ),
                format(
                    next(
                        r["fallback_fraction"]
                        for r in q["admitted_fallback_rates"]
                        if r["split"] == "development" and r["feature"] == name
                    ),
                    ".4%",
                ),
            ]
            for name in ORDER
        ],
    )
    readiness = (
        headline + dates + waterfall + "P019B upper bounds were5,210training /194development joint "
        "closing-price origins, not FT counts. "
        "Actual finite16channels preserve5,210/5,210=100%of the train "
        "bound. Development retains183/194=94.3299%; "
        "11source-qualified origins fall in the predeclared48hour "
        "transform-availability embargo. "
        "Relative to scheduled opportunities: train5,210/7,104=73.3390%; "
        "development183/250=73.2%. "
        "Masks do not resurrect COP or long unavailable price contexts. "
        "Volume fallback provides "
        "usable fixed-width features without pretending the original "
        "incomplete volume tape became complete.\n\n"
        + fallbacks
        + "All15training calendar years have>=100eligible origins; exact counts: "
        + json.dumps(q["year_train_origin_counts"])
        + ".\n\n"
        "The maximum admitted channel fallback over all four splits is "
        + format(q["maximum_admitted_channel_fallback_fraction"], ".4%")
        + ", below the declared80%screen. The13scaled channels are finite; "
        "native Q1/Q2 vary substantially rather than becoming constants. "
        "These are engineering screens, not statistical power or "
        "predictive-alpha claims. Sources retain missingness, "
        "retrospective cohort selection and incomplete volume "
        "limitations.\n\n"
        + mdtable(
            ["Hypothetical exclusion", "Retained names", "Feature+endpoint potential"],
            [
                [
                    r["excluded_hypothetical"],
                    r["retained_stocks"],
                    r["feature_and_endpoint_potential"],
                ]
                for r in quality["weak_stock_counterfactuals"]
            ],
        )
        + "These quality-only counterfactuals do not construct smaller "
        "targets or change the20-stock cohort. "
        "No universe change is implemented or needed to meet the "
        "predeclared readiness screens.\n"
    )
    write(out / "P020_ACTUAL_ORIGIN_READINESS.md", "# P020 actual origin readiness\n\n" + readiness)
    evidence = [
        "model_input_contract.json",
        "train_only_fit_recipes.json",
        "quantitative_qa.json",
        "independent_oracle_and_causality.json",
        "quality_and_fit_prefix_receipt.json",
        "provenance_overlay_manifest.json",
        "tests_static_receipt.json",
    ]
    gate = {
        "status": status,
        "source": config["source"],
        "revision": config["revision"],
        "feature_id": config["feature_id"],
        "target_id": config["target_id"],
        "model_input_id": config["model_input_id"],
        "symbols": config["symbols"],
        "evidence": {name: ref(out / name) for name in evidence},
        "upstream_gate_sha256": config["upstream_gate_sha256"],
        "root_register_unchanged_sha256": config["root_register_sha256"],
        "split_counts": d["split_counts"],
        "model_training_authorized": False,
        "ledger": 32,
        "protected_numeric_access": False,
        "required_next_action": "separate explicit live authorization for matched seed42 C0/T2 "
        "pair; no automatic fitting",
    }
    publish_json(out / "release_gate.json", gate)
    training = {
        "candidate_run_ids": ["HF1M-LONG-TM0-C0-S42-DEV1", "HF1M-LONG-TM0-T2-S42-DEV1"],
        "model_input_contract": ref(out / "model_input_contract.json"),
        "release_gate": ref(out / "release_gate.json"),
        "fit_versions": {
            "inner_train": "inner",
            "inner_validation": "inner",
            "refit": "refit",
            "development": "refit",
        },
        "seed": 42,
        "input_shape": [20, 48, 16],
        "model": "shared stock-only TM0;one LSTM layer,width32,dropout0.1,scalar head",
        "nominal_parameters": 6433,
        "parameter_count_formula": "4*32*(16+32+2)+32+1=6433",
        "optimizer": {
            "name": "AdamW",
            "learning_rate": 0.001,
            "betas": [0.9, 0.999],
            "eps": 1e-8,
            "weight_decay_weights": 0.01,
            "weight_decay_bias": 0.0,
            "amsgrad": False,
        },
        "global_L2_gradient_clip": 1,
        "batch_sessions": 16,
        "loss": "session-weighted equal-origin equal-stock MSE",
        "calibration": "D6g60epoch cap;min12epochs;patience10;qualifying improvement "
        "loss<0.999*best;select original TG20 validation MSE",
        "refit": "fresh seed42 weights and optimizer;full-prefix refit "
        "recipe;exact selected calibration epoch count",
        "diagnostics": [
            "original_TG20_MSE",
            "daily_Rank_IC",
            "ZERO_MSE",
            "prediction variance",
            "tails and gradient clipping",
        ],
        "model_training_authorized": False,
        "neural_starts": 0,
        "ledger": 32,
        "engine_code": {
            name: ref(Path("src/lstm_data") / name)
            for name in ["neural_engine.py", "neural_lifecycle.py"]
        },
        "preserve_10_plus_3_improvement_hypotheses": True,
        "checkpoints_used": False,
    }
    publish_json(out / "next_training_manifest_NOT_AUTHORIZED.json", training)
    handoff = (
        headline + dates + "**No model has been trained in Package 020**. No optimization, "
        "checkpoint access, inference, "
        "portfolio or final-test work occurred. The next task must "
        "separately approve the exact matched "
        "C0→T2 seed42 pairs and any ledger amendment before "
        "reservation/start. This file grants none.\n\n"
        "Read release_gate.json, model_input_contract.json and "
        "next_training_manifest_NOT_AUTHORIZED.json. "
        "Use "
        "lstm_data.hf1m_ft16_loader.load_model_input(contract,split=...,fi"
        "t_version=...). "
        "The only splits are "
        "inner_train/inner_validation/refit/development, with "
        "inner/inner/refit/refit "
        'recipes. batch(positions,target_mode="C0" or "T2") returns '
        "finite float32 X[B,20,48,16], "
        "Y[B,20]. Flatten only stock examples within eligible sessions "
        "for the shared LSTM; preserve "
        "equal-session/origin/stock loss and absent-origin padding masks. "
        "Original/older HF20 loaders "
        "cannot consume these new data; do not call them or copy their "
        "hard-coded counts.\n\n"
        "TM0 compatibility is code-reviewed: one layer,width32,dropout0.10,6,433parameters "
        "(4*32*(16+32+2)+33), AdamW lr0.001,betas0.9/0.999,eps1e-8,weight "
        "decay0.01matrix/0bias, "
        "globalL2clip1,16sessions/batch. "
        "D6gmin12,max60,patience10,qualifying0.1%improvement. "
        "Calibrate using inner-only preprocessing and original-scale "
        "validation MSE for both arms; "
        "then fresh same-seed refit on full prefix with its own recipe "
        "for the selected epoch count. "
        "C0 original TG20; T2 asinh with saved fit scale; invert once "
        "before original-scale selection "
        "and development diagnostics. No parameter or architecture search.\n\n"
        "Frozen source, cohort, dates, feature definitions, fallbacks, "
        "scalers, target and T2 metadata "
        "are ready to load; do not choose them again from model outcomes. "
        "Preserve the10+3later "
        "hypotheses. Known limitations remain conditional source "
        "latency/rights, retrospective "
        "survivorship selection, price-only dividends,15:30daily "
        "surrogate, observed-range and "
        "incomplete-volume lower bounds, local quarantine and channel fallback.\n"
    )
    write(out / "P020_TRAINING_HANDOFF.md", "# P020 untrained matched-pair handoff\n\n" + handoff)
    spec = {
        "visibility": "LOCAL_PRIVATE_ONLY",
        "contract": ref(out / "model_input_contract.json"),
        "charts": [
            {
                "name": "coverage_by_year",
                "table": "quantitative_qa.json:year_train_origin_counts",
                "x": "year",
                "y": "origins",
            },
            {
                "name": "channel_fallback_heatmap",
                "table": "feature_missingness_stock_year.csv",
                "filters": ["ticker", "year", "feature"],
            },
            {
                "name": "volume_quality",
                "table": "volume_quality_stock_year.csv",
                "filters": ["ticker", "year"],
            },
            {
                "name": "input_candles_and_quality",
                "file": d["files"]["candles_quality"],
                "filters": ["ticker", "session_date_et", "step"],
            },
            {
                "name": "target_extremes",
                "file": q["quality_artifacts"]["target_extremes"],
                "filters": ["selection", "ticker", "origin_id"],
            },
            {
                "name": "48step_native_scaled",
                "file": d["files"]["components"],
                "index": d["files"]["grid"],
                "instructions": "joinorigin first_step:entry_index inclusive;common15 channels "
                "plus forecast-origin M2 context;usefit version;separate "
                "fallback/reason mask",
            },
        ],
        "existing_Streamlit_integration": (
            "new allowlisted contract adapter required; old FT0/Twelve Data pages "
            "must not silently treat new stores as their own; no dashboard changed"
        ),
    }
    publish_json(out / "plotly_ready_explorer_manifest.json", spec)
    write(
        out / "REPRODUCTION.md",
        "# Reproduction\n\nUse repository .venv setup and lawful private "
        "upstream source cache. No network, new dependencies or "
        "credentials. From repository root:\n\n```bash\n"
        + "\n".join(
            ".venv/bin/python -B -m lstm_data.hf1m_ft16_" + name + " --out " + out.as_posix()
            for name in ["prepare", "audit", "oracles", "quality", "report"]
        )
        + "\n```\n\nExisting preparation command checks sealed file hashes; "
        "numeric stores are not rebuilt. Audits/reports permit identical "
        "replay and reject changed immutable evidence. A fresh full "
        "derivation requires a NEW report/private output directory, the "
        "same frozen config plus recreated preflight/formula freeze "
        "evidence, exact approved parent manifests and source allowlists. "
        "No paths depend on a username. Do not redistribute ignored "
        "source/component/target stores or load untrusted "
        "checkpoint/pickle content. No model training command is part of "
        "Package020. Full focused test/static commands and final code "
        "hashes are in tests_static_receipt.json and the session report.\n",
    )
    write(
        out / "human_review_card.md",
        "# P020 human review card\n\n"
        + headline
        + lineage
        + dates
        + "16features usable under frozen causal fallback. Refit "
        "Q1fallback6.7006%,Q2fallback21.6755%; development "
        "Q1fallback4.4553%,Q2fallback10.0529%. Maximum across all "
        "channels/splits "
        + format(q["maximum_admitted_channel_fallback_fraction"], ".4%")
        + ". Native components and missing masks remain separate; no claim "
        "of complete minute volume.\n\n"
        "TG20 uses genuine same-session4hour returns, exactly20stock median/unscaledMAD, "
        "and separate train-only inner/refit epsilon. T2 uses saved train-only "
        "s=median(abs(TG20)), asinh(y/s), with inverse s*sinh(z) once. "
        "No clipping or target imputation. Details: P020_TARGET_TG20_AND_CLOCK_AUDIT.md.\n\n"
        "Readiness:5,210training origins/104,200stock "
        "rows;183development/3,660stock rows;4,428inner "
        "training/88,560stock rows;766inner validation/15,320stock rows. "
        "Training covers15years with>=100origins each. Final development "
        "reduction11/194 is the frozen embargo. All20stocks retained.\n\n"
        "Top limitations: incomplete/lower-bound volume, Q2fallback, "
        "historical source latency unverified,15:30daily surrogate, "
        "retrospective cohort and split units, dividends not "
        "reconstructed. All16future-split invariance and causal checks "
        "passed. No protected numeric features/targets stored.\n\n"
        "83 focused tests passed; full static check:292files,0errors,0warnings; Ruff passed. "
        "Measured new storage157.4MB at receipt; peak processRSS1.295GB. Continuous storage "
        "peak was not instrumented; conservative transient bound is below0.5GB, versus10GB "
        "ceiling. Exact bytes and scope: final_resource_receipt.json. "
        "Ledger32/200unchanged. Next action is separately authorized "
        "matched seed42 C0/T2 training; "
        "no model has been trained and no training permission is implied.\n",
    )
    print(status)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", required=True, type=Path)
    publish(p.parse_args().out)


if __name__ == "__main__":
    main()
