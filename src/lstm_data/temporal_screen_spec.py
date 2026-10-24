"""P026's bounded temporal amendment; importing this module grants no fit authority."""

from pathlib import Path

ARMS = ("A1", "A2", "A3")
ARCHITECTURES = dict(A1="TM1_ATTENTION", A2="TM3_MULTISCALE", A3="GRU32")
RUNS = tuple(f"HF1M-LONG-{ARCHITECTURES[a]}-T2-S42-DEV1" for a in ARMS)
PARAMETERS = dict(A1=6466, A2=7217, A3=4833)
SEED = 42
ROLES = ("inner_train", "inner_validation", "refit", "development")
CONTRACT = "7adfec916b7eb74fead83ef1fe6082ff0fcee9ff0b6ebae5722077e2a82c01a5"
P025 = Path("reports/experiments/ta025_e1_qr1_seed123_2026-10-23_171546_preparation_v3")
P021 = Path("reports/experiments/ta021_hf1m_long_four_lstm_2026-10-22_232248_recovery_v1")
SCIENCE = dict(
    package="P026",
    architectures=ARCHITECTURES,
    runs=list(RUNS),
    parameters=PARAMETERS,
    amendment=(
        "Narrow three-arm election supersedes October10 conditional TM1/d"
        "eferred TM3 only; no combination or broader roadmap activation."
    ),
    input=(
        "Unchanged P020 scaled/fallback FT16 [origin,20,48,16]; no new masks, observations or peers"
    ),
    A1=(
        "q dot no-affine LayerNorm(h_s,eps=1e-5)/sqrt(32); softmax48; c=s"
        "um(a*h); h48+gamma*(c-h48); scalar head with dropout0.1"
    ),
    A1_initialization=(
        "Original SharedLSTM constructed first; q~N(0,0.01) from local CP"
        "U generator seed42+2601; gamma=0; extra initialization preserves"
        " global training RNG"
    ),
    A2=(
        "For each existing scaled feature use inclusive causal means of l"
        "ast1/4/12 available positions; Linear(48,16) then original LSTM/"
        "head"
    ),
    A2_initialization=(
        "Original SharedLSTM first; extra mixer initialized [I16,0,0],bia"
        "s0 under fork_rng; exact base initialization/global RNG identity"
    ),
    A2_missing=(
        "Average released finite scaled values, including the existing tr"
        "ain-prefix fallbacks, over scheduled positions. No re-masking or"
        " renormalization by native availability."
    ),
    A3=(
        "nn.GRU(16,32,1,batch_first=True,dropout=0), zero fresh state; la"
        "st hidden, dropout0.1,Linear(32,1); construct recurrent then hea"
        "d with seed42"
    ),
    optimizer=dict(
        kind="AdamW",
        lr=0.001,
        betas=[0.9, 0.999],
        eps=1e-8,
        matrix_and_query_decay=0.01,
        bias_gamma_decay=0.0,
        clip=1.0,
        batch_sessions=16,
        schedule=None,
    ),
    selector=dict(
        source="neural_lifecycle.EarlyStop",
        metric="original TG20 validation MSE",
        qualifier="loss < 0.999 * qualifying_best; strict, no tolerance",
        minimum=12,
        maximum=60,
        patience=10,
    ),
    objective=(
        "equal session then eligible origin then20 stock (zhat-asinh(floa"
        "t32(y)/prefix_scale))^2; original scalar T2 inverse scale*sinh(z"
        "hat) once"
    ),
    refit=(
        "Fresh seed42 model and empty optimizer; selected calibration epo"
        "ch count only; refit prefix epsilon/scaler/scale"
    ),
    metrics=[
        "original MSE/MAE/RMSE",
        "equal-day origin Spearman IC (constant undefined)",
        "direction with zeros counted explicitly",
        "top/bottom4 recall",
        "forecast quantiles/SD/calibration/residuals",
        "per-stock/year/month/quality/V1-state",
    ],
    baselines="Saved T2/42 primary; T2/123 contextual and ZERO; all four roles; no baseline fits",
    uncertainty=dict(
        replicates=400,
        seed=22042,
        calendar_month_blocks=[1, 2],
        statistic=(
            "paired daily MSE/IC candidate minus T2/42; intact sessions; reco"
            "mpute day mean of origin IC"
        ),
        scope=(
            "exploratory dependence sensitivity; repeated development, three "
            "comparisons, no p-value/confirmation"
        ),
    ),
    extremes=dict(
        rank_percent=[1, 5],
        range_fraction=[0.99, 0.95],
        tie="origin_id then canonical stock order",
        MAD="unique origins ranked then expanded20",
        partition=["NUM_ONLY", "MAD_ONLY", "BOTH", "NEITHER"],
        cases=(
            "five largest weighted z-loss each AAPL AMZN TSLA SBUX plus disti"
            "nct BOTH_5 and MAD_ONLY_5 when available"
        ),
    ),
    mechanisms=dict(
        A1=(
            "gamma/q trajectory, lag entropy/mass; saved-model historical per"
            "turbation; attention is not attribution"
        ),
        A2=(
            "three block norms/identity deviations, branch signals/gradients,"
            " prefix causality and past perturbations"
        ),
        A3=(
            "actual hidden trajectory/BPTT and past perturbations; reset/upda"
            "te gates NOT_DIRECTLY_OBSERVED"
        ),
    ),
    decision=(
        "Joint dev MSE decrease and IC increase is suggestive only; mixed"
        "/negative/inconclusive/implementation failure retained. Amplitud"
        "e or module usage alone is not skill; no automatic promotion."
    ),
    tolerances=dict(
        hyperparameters=0,
        checkpoint_reload=0,
        target=[1e-10, 1e-11],
        inverse=[7e-7, 1e-7],
        point_float32_loss=[3e-5, 2e-6],
        weighted_objective=[5e-7, 1e-8],
    ),
    resources=dict(
        cpu_threads=4,
        interop_threads=1,
        peak_rss_limit=2_000_000_000,
        additional_storage_limit=1_000_000_000,
        total_storage_limit=10_000_000_000,
        planning_time="0.5–6h fitting and diagnostics, estimate only",
    ),
    boundaries=dict(
        opening=53,
        maximum=56,
        ceiling=200,
        new_starts=3,
        no_retry=True,
        protected_numeric_access=False,
        maximum_numeric_date="2025-12-31",
        live_approval_required=True,
        no_network=True,
        no_trading=True,
        no_git_publication=True,
    ),
)
