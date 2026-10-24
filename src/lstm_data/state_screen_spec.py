"""P028 human-approved three-arm frozen scientific configuration."""

from copy import deepcopy
from pathlib import Path

from .peer_screen_spec import SCIENCE as PRIOR
from .temporal_screen_spec import CONTRACT, P021, P025, ROLES

ARMS = ("A7", "A8", "A12")
FAMILIES = dict(A7="P028-MC1", A8="P028-GLOBAL8-LOCAL32", A12="P028-SOFT2")
ARCHITECTURES = dict(A7="MC1", A8="GLOBAL_LOCAL", A12="SOFT_EXPERTS")
RUNS = tuple(f"HF1M-LONG-{FAMILIES[a]}-T2-S42-DEV1" for a in ARMS)
PARAMETERS = dict(A7=6737, A8=7841, A12=6728)
P026 = Path("reports/experiments/ta027_cross_stock_2026-10-23_214637_preparation_v1")
PREPARATION = Path("reports/experiments/ta028_market_state_2026-10-24_014518_preparation_v2")
AUDIT = PREPARATION / (
    "ta028_market_state_2026-10-24_014518_preparation_v2_verified_audit_v2/market_state_audit.json"
)
FAIRNESS = (
    "Two panel-derived proxies include the focal stock; no independent index. Saved T2/42 "
    "has 16 stock channels, so its contrast combines information and architecture. No "
    "trained 18-input control; architecture-only attribution unidentified. A7/A8/A12 "
    "share source proxies but differ in processing/capacity. Reused development is exploratory."
)
CUTS = dict(inner=-0.06340353935956955, refit=-0.03880869597196579)
SCIENCE = {
    k: deepcopy(PRIOR[k])
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
    )
}
SCIENCE.update(
    package="P028",
    architectures=ARCHITECTURES,
    families=FAMILIES,
    runs=list(RUNS),
    parameters=PARAMETERS,
    seed=42,
    information_fairness=FAIRNESS,
    boundaries=dict(
        opening=59,
        maximum=62,
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
    input="Original float32 [B,20,48,16] plus [B,48,2] exact panel proxies",
    state=(
        "float64 mean20 scaled/fallback M1; median20 scaled/fallback V1 "
        "central9/10 average; round32 once"
    ),
    A7=(
        "MC1 endpoint Linear2→16 zero logits; alpha16softmax tau1; "
        "gated16+direct2→LSTM32; dropout.1 scalar head"
    ),
    A8=(
        "globalCell2→8 then shared localCell24→32 each step, zero local "
        "global-input columns16:24; no feedback"
    ),
    A12=(
        "LSTM18→32; dropout.1 once; cloned scalar heads; router Linear2→2 "
        "tau1 local generator2812 Normal(0,.01),bias0"
    ),
    support=dict(
        first_origin="10:30 else11:30",
        cuts=CUTS,
        fitting_min_sessions=50,
        fitting_min_episodes=5,
        validation_min_sessions=20,
        validation_min_episodes=2,
        episode_min_sessions=5,
        maximal=True,
        development="descriptive WARN: LOW35sessions/1episode, HIGH74/8",
    ),
    negative_control=dict(
        lag_eligible_sessions=10,
        slot="same origin slot",
        pool="source_input_eligible only, no donor labels",
        operation="replace only two shared state histories; retain all own16 stock inputs",
        scope="distribution-shift sensitivity, not null significance",
    ),
    cases=dict(
        count=22,
        selection=(
            "deterministic stable-key role-balanced coverage; no "
            "prediction/loss-dependent selection"
        ),
        roles=["refit", "development"],
        classes=[
            "both origin slots",
            "LOW",
            "HIGH",
            "near training cut",
            "normal TG20",
            "extreme TG20",
            "small MAD",
            "quality",
            "fallback",
        ],
        fallback="NOT_PRESENT then earliest unused stable key",
    ),
)

__all__ = [
    "CONTRACT",
    "P021",
    "P025",
    "P026",
    "ROLES",
    "ARMS",
    "RUNS",
    "SCIENCE",
    "PARAMETERS",
    "FAIRNESS",
    "ARCHITECTURES",
    "FAMILIES",
    "PREPARATION",
    "AUDIT",
]
