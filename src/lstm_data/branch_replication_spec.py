"""P025 preregistered E1/QR1 replications and read-only estimators; no numerical access."""

from pathlib import Path

ARMS = ("E1", "QR1")
RUNS = tuple(f"HF1M-LONG-TM0-{arm}-S123-DEV1" for arm in ARMS)
SEED = 123
ROLES = ("inner_train", "inner_validation", "refit", "development")
CONTRACT = "7adfec916b7eb74fead83ef1fe6082ff0fcee9ff0b6ebae5722077e2a82c01a5"
P022 = Path("reports/experiments/ta022_hf1m_long_objective_screen_2026-10-23_repair_preparation")
P023 = Path("reports/experiments/ta023_hf1m_long_dm1_qr1_ss1_2026-10-23_preparation")
P024 = Path("reports/experiments/ta024_hf1m_long_optimization_2026-10-23_recovery_preparation_v1")
SCIENCE = {
    "package": "P025",
    "runs": list(RUNS),
    "seed": SEED,
    "seed_policy": (
        "123 for initialization, dropout and whole-session epoch permutation; no sampler"
    ),
    "architecture": {
        "input": 16,
        "lookback": 48,
        "hidden": 32,
        "layers": 1,
        "head": 3,
        "head_dropout": 0.1,
        "recurrent_interlayer_dropout": 0.0,
        "parameters": 6499,
        "construction": "SharedLSTM scalar reference first, then replace head with Linear(32,3)",
    },
    "optimizer": {
        "kind": "AdamW",
        "lr": 0.001,
        "betas": [0.9, 0.999],
        "eps": 1e-8,
        "matrix_decay": 0.01,
        "bias_decay": 0.0,
        "global_clip": 1.0,
        "batch_sessions": 16,
    },
    "selector": {
        "source": "objective_screen_run.Selector",
        "minimum": 12,
        "maximum": 60,
        "patience": 10,
        "qualifier": "value <= 0.999 * qualifying_best; no tolerance",
        "E1": "inner-validation session-normalized class-weighted CE",
        "QR1": "inner-validation mean-three pinball in z units",
        "refit": "fresh same-seed initialization and optimizer for selected epochs only",
    },
    "objectives": {
        "E1": "unchanged objective_screen_loss.Objective('E1', saved_prefix_recipe)",
        "labels": "NEG:y<-q95; POS:y>q95; equality NORMAL; original linear row q95",
        "E1_weights": "saved min(4,sqrt(p_NORMAL/max(p_class,1e-12))), NORMAL=1",
        "E1_normalization": "sum(c_k*CE)/sum(c_k) per complete session, then mean sessions",
        "QR1": "unchanged dm_quantile_loss.terms/outputs; tau=[.05,.5,.95], mean of three",
        "QR1_order": "[raw0-softplus(raw1),raw0,raw0+softplus(raw2)] in z",
        "inverse": "prefix scale*sinh(q_z), exactly once; never sort/repair outputs",
    },
    "calibration": {
        "maps": ["RAW_SOFTMAX", "INVERSE_CLASS_WEIGHT"],
        "correction": "normalize(p_raw / saved fitting-prefix class_weights)",
        "interpretation": "analytical diagnostic, not guaranteed natural-frequency calibration",
        "temperature_scaling": (
            "OMITTED: inner-checkpoint calibration/refit phase transfer unverified"
        ),
        "reliability_edges": [i / 10 for i in range(11)],
        "probability_thresholds": [0.05, 0.10, 0.20, 0.50],
        "origin_top_k": [1, 4],
        "slope": "weighted linear probability calibration slope/intercept; not logistic MLE",
        "ranking_change": "Spearman raw/corrected ANY plus changed top4 membership; retain both",
    },
    "states": {
        "channels": ["V1", "M2", "Q2"],
        "input_step": 47,
        "semantics": (
            "native released causal last-input values; M2 is origin-specific prior-session momentum"
        ),
        "stock_state": "pooled training stock-row weighted inverse empirical CDF terciles",
        "market_state": "median20 causal native values at same origin, weighted training terciles",
        "weights": "equal session, eligible origin,20 stocks; market values count once per origin",
        "ties": "LOW<=cut1; MID cut1<x<=cut2; HIGH>cut2; empty cohorts stay empty",
        "fallback": (
            "use existing fitting-prefix fallback; keep flag and report missing/fallback rates"
        ),
        "eras": ["2011-2015", "2016-2020", "2021-2025"],
        "width_sort": "train-only weighted terciles of predicted z-width for each seed/fit",
        "response_stats": ["mean", "sd", "iqr", "p05", "p95", "range", "sd/unconditional_width"],
        "conditional_metrics": [
            "pinball_z",
            "coverage05/50/95",
            "interval90_coverage",
            "interval_score_z",
            "width_z",
            "width_TG20",
            "abs_future_z",
        ],
        "negative_control": {
            "statistic": (
                "equal-day Spearman of origin-median z-width with origin-median abs_future_z"
            ),
            "scheme": "400 fixed-seed intact-session circular shifts, nonzero day offsets",
            "seed": 25042,
            "scope": "read-only association reference, not neural permutation evidence",
        },
        "plots": ["width_vs_V1", "conditional_pinball_skill", "coverage_and_realized_dispersion"],
        "verdicts": ["output_variability", "conditional_calibration", "proper_score_skill"],
    },
    "uncertainty": {
        "replicates": 400,
        "seed": 22042,
        "blocks_calendar_months": [1, 2],
        "metrics": (
            "whole-day matched score differences; recompute AP from resampled full-day panels"
        ),
        "limits": (
            "109 reused development sessions; dependent stocks/origins; exploratory intervals only"
        ),
    },
    "extremes": {
        "rank_percent": [1, 5],
        "range_train_max_fractions": [0.99, 0.95],
        "tie_order": "origin_id then canonical stock index",
        "small_mad": "rank unique origins first, expand to20",
        "cases": "top5 weighted actual loss each AAPL/AMZN/TSLA/SBUX plus BOTH_5/MAD_ONLY_5",
        "context": (
            "48 genuine scheduled input hours plus4 outcome hours; no fabricated OHLC/volume"
        ),
    },
    "tolerances": {
        "hyperparameters": 0,
        "checkpoint_reload": 0,
        "target": [1e-10, 1e-11],
        "inverse": [7e-7, 1e-7],
        "point_float32_loss": [3e-5, 2e-6],
        "weighted_objective": [5e-7, 1e-8],
        "probability_sum": [1e-6, 1e-7],
    },
    "boundaries": {
        "protected_numeric_access": False,
        "maximum_numeric_date": "2025-12-31",
        "new_starts": 2,
        "opening": 51,
        "maximum": 53,
        "ceiling": 200,
        "no_retry": True,
        "training_requires_live_response": True,
        "no_download": True,
        "no_trading": True,
        "no_git_publication": True,
    },
    "resources": {
        "cpu_threads": 4,
        "interop_threads": 1,
        "peak_rss_limit": 2_000_000_000,
        "additional_storage_limit": 1_000_000_000,
        "total_storage_limit": 10_000_000_000,
        "planning_time": "0.5–6 hours for approved fitting plus diagnostics, not a benchmark",
    },
}
