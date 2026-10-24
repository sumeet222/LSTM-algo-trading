"""P027's three fixed N=20 peer-information alternatives; no fit authority."""

from copy import deepcopy
from pathlib import Path

from .temporal_screen_spec import CONTRACT, P021, P025, ROLES
from .temporal_screen_spec import SCIENCE as TEMPORAL_SCIENCE

ARMS = ("A4", "A5", "A6")
FAMILIES = dict(A4="P027-PEER19-M1-MEANSD", A5="P027-SP3-RANK4", A6="P027-SP1-ATTN16")
ARCHITECTURES = dict(A4="PEER_SUMMARY", A5="SP3_STOCKMIXER", A6="SP1_ATTENTION")
RUNS = tuple(f"HF1M-LONG-{FAMILIES[a]}-T2-S42-DEV1" for a in ARMS)
PARAMETERS = dict(A4=6689, A5=6593, A6=8481)
P026 = Path("reports/experiments/ta026_temporal_architectures_2026-10-23_preparation_v3")
FAIRNESS = (
    "A4 sees own FT16 plus two leave-one-out peer M1 summaries at every historical step; "
    "A5/A6 encode all16 channels of all20 histories before final-state exchange. "
    "A4 is not a full-information-matched control. No fourth full-peer LSTM is authorized; "
    "A5/A6 gains cannot identify the exchange mechanism independently of information/capacity."
)
SCIENCE: dict[str, object] = {
    k: deepcopy(TEMPORAL_SCIENCE[k])
    for k in (
        "optimizer",
        "selector",
        "objective",
        "refit",
        "metrics",
        "baselines",
        "uncertainty",
        "extremes",
        "decision",
        "tolerances",
        "resources",
        "boundaries",
    )
}
SCIENCE.update(
    package="P027",
    architectures=ARCHITECTURES,
    families=FAMILIES,
    runs=list(RUNS),
    parameters=PARAMETERS,
    seed=42,
    boundaries=dict(
        opening=56,
        maximum=59,
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
    optimizer=dict(
        kind="AdamW",
        lr=0.001,
        betas=[0.9, 0.999],
        eps=1e-8,
        matrix_projection_decay=0.01,
        bias_decay=0.0,
        clip=1.0,
        batch_sessions=16,
        schedule=None,
    ),
    uncertainty=dict(
        replicates=400,
        seed=22042,
        calendar_month_blocks=[1, 2],
        statistics=(
            "Paired original MSE, equal-day origin IC and mean per-origin IC;"
            " T2/42 primary plus A5-A4,A6-A4,A6-A5; report block occupancy"
        ),
        scope=(
            "Repeated exploratory development; dependent comparisons, not p-values/confirmation"
        ),
    ),
    information_fairness=FAIRNESS,
    input="Unchanged P020 scaled/fallback [B,20,48,16]; complete fixed canonical panels only",
    A4=(
        "Append population mean/SD of the other19 scaled M1 values at eac"
        "h step; ordinary LSTM18→32; head/dropout unchanged"
    ),
    A4_variance=(
        "Explicit centered19-peer squared deviations, divisor19, clamp ro"
        "undoff-negative to0; no epsilon or separate scaler"
    ),
    A5=(
        "H[B,20,32]; H+M2 GELU(M1 LN_no_affine_eps1e-5(H)); M1[4,20],M2[2"
        "0,4],stock axis,exact GELU,no bias"
    ),
    A5_initialization=(
        "SharedLSTM first; local CPU generator seed2747; M1 Normal(0,.01)"
        ", M2=0; global RNG unchanged"
    ),
    A6=(
        "LN_no_affine_eps1e-5(H); Q,K,V=LN(H) W[32,16]; rowSoftmax(Q K^T/"
        "4); H+A V WO[16,32]; no bias/dropout/identities"
    ),
    A6_initialization=(
        "SharedLSTM first; local CPU generator seed2748; WQ/WK/WV Normal("
        "0,.01) sequentially, WO=0; global RNG unchanged"
    ),
    initialization=(
        "A4 LSTM18 then dropout.1/Linear32→1 at seed42; A5/A6 original Sh"
        "aredLSTM constructed before extra local RNG draws"
    ),
    permutations=(
        "A4 summary-equivariant; A5 requires M1'=M1 P^T,M2'=P M2; A6 intr"
        "insically equivariant in eval; loader retains canonical order"
    ),
    negative_control=dict(
        lag_eligible_sessions=10,
        slot="same 10:30/11:30 completed-hour slot",
        pool=(
            "Released source_input_eligible complete20 historical windows bou"
            "nded by role's final permissible date, using that role's phase r"
            "ecipe; admission/label/future-availability flags never choose do"
            "nors"
        ),
        eligibility=(
            "10 preceding distinct pool-eligible sessions; require same-slot "
            "complete20 finite original source window and strictly earlier is"
            "suance; otherwise diagnostic-only exclusion"
        ),
        operation=(
            "Focal own48×16 unchanged; A4 recomputes only peer summaries; A5/"
            "A6 encode shifted other-stock histories and retain own original "
            "hidden state"
        ),
        reporting=(
            "Original and shifted on identical complete20-origin subset; four"
            " roles; distribution-shifting sensitivity, not a trained null/p-"
            "value"
        ),
    ),
    mechanisms=dict(
        A4=(
            "Exact19-peer operands, own-M1 association, extra-channel derivat"
            "ives and own-fixed peer perturbations"
        ),
        A5=(
            "M1/M2 singular spectra/effective rank/conditioning/concentration"
            "; actual cross-hidden Jacobians, readout shifts and ticker depen"
            "dence"
        ),
        A6=(
            "True20×20 probabilities, entropy/effective peers/self mass by ti"
            "cker/day/V1-state; q/k/v/output norms/gradients, peer Jacobians "
            "and readout shifts"
        ),
        common=(
            "8 fixed earliest refit origins for local derivatives/peer pertur"
            "bations; full refit aggregate module measurements;22 exact sourc"
            "e cases/arm"
        ),
    ),
)

__all__ = [
    "ARMS",
    "ARCHITECTURES",
    "CONTRACT",
    "FAIRNESS",
    "FAMILIES",
    "PARAMETERS",
    "P021",
    "P025",
    "P026",
    "ROLES",
    "RUNS",
    "SCIENCE",
]
