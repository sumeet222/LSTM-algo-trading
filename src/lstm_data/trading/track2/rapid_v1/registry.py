"""Numerical defaults and code are sealed before any new financial result."""

import json

from .paths import MENU, ROOT, V5, canonical, code_identity, digest, publish
from .strategies import IDS, SLOTS, mode

FORMULAS = {
    "M01": "sign received intraday r60 when abs(r60/sigma_past20slot)>=1",
    "M02": "negative M01 sign on the identical r60 standardized move>=1",
    "M03": "negative opening gap sign when abs(gap/past20gap_sd)>=1",
    "M04": (
        "gap sign, abs(gap_z)>=1, first-hour same sign and received volume above "
        "past20same-slot mean"
    ),
    "M05": "received price outside completed0930-1000 range by5bp",
    "M06": (
        "r60 minus current leave-one-out mean,abs(past20same-slot "
        "residual_z)>=1;top/bottom2 raw residual,12peers"
    ),
    "M07": "previous20calendar-session same-clock next-half-hour mean/SE,abs(z)>=1",
    "M08": "negative identical r60 sign with abs(z)>=1 and robust prior20same-slot volume_z>=1.5",
    "M09": "negative received opening-to-current intraday sign,abs(past20same-slot z)>=1",
    "R01": "log(C[d-22]/C[d-126]);top2 positive,bottom2 negative",
    "R02": "sign log(MA20/MA60), abs(log ratio/(v60 sqrt20))>=.5",
    "R03": "received price outside strict completed prior20session high/low by5bp",
    "R04": "opposite log(C[d-1]/C[d-6]);long bottom2 negative,short top2 positive",
    "R05": (
        "KO/PEP,XOM/CVX,BAC/WFC;past60log-price OLS "
        "beta[.25,4],R2>=.3,residual_sd>1e-4;abs(z)>=2;beta-neutral atomic legs"
    ),
    "R06": (
        "past60stock/leave-one-out factor OLS,min50paired observations;last5residual"
        " sum/(past residual_sd sqrt5);reverse tails abs(z)>=1"
    ),
    "R07": "R03 breakout only when latest completed RV10 below prior60RV10 20th percentile",
    "R08": (
        "prior10 ON and ID sums opposite with abs(ON/(past60ON_sd sqrt10))>=1 and ID"
        " likewise;follow ON sign"
    ),
    "R09": (
        "last5completed robust log-volume anomalies using each day's own "
        "preceding60reference;top/bottom2 abs(mean_z)>=1"
    ),
}


def freeze_registry(reason: str = "initial implementation before outcomes") -> dict:
    baseline = json.loads((ROOT / "audits/FROZEN_BOUNDARY_BASELINE.json").read_text())
    if baseline["material_differences"]:
        raise ValueError("FROZEN_RESEARCH_DRIFT")
    body = {
        "schema": "rapid-v1-registry-1",
        "menu": str(MENU),
        "menu_sha256": digest(MENU),
        "authorization_prompt_sha256": digest(
            MENU.with_name(
                "HF20_Track2_Rapid_Backtest_Engine_All18_Micro_Retail_Codex_Prompt_2026-11-10.md"
            )
        ),
        "engineering_revision_reason": reason,
        "code": code_identity(),
        "defaults": json.loads((ROOT / "DESIGN_DEFAULTS_V1.json").read_text()),
        "support_and_basis": json.loads((ROOT / "SOURCE_AND_SUPPORT_DEFAULTS_V1.json").read_text()),
        "prior_V5_manifest_sha256": digest(V5 / "FINAL_CONTENT_MANIFEST_V5.json"),
        "initial_frozen_inventory_sha256": digest(ROOT / "audits/FROZEN_BOUNDARY_BASELINE.json"),
        "strategies": [
            {
                "id": s,
                "mode": mode(s),
                "slots": SLOTS[s],
                "formula": FORMULAS[s],
                "menu_reference": "section4" if s.startswith("M") else "section5",
                "entry_cap": 6 if s.startswith("M") else 5,
                "minimum_external_notional": 0 if s.startswith("M") else 2000,
                "horizon_scheduled_XNYS_minutes": 240,
                "pair_atomic": s == "R05",
            }
            for s in IDS
        ],
        "controls": ["LEGACY_V5_SIGN", "NO_TRADE"],
        "outcomes_seen_before_freeze": False,
        "output_limits": {
            "strategy_hard_bytes": 25 * 2**20,
            "total_hard_bytes": 500 * 2**20,
            "target_total_bytes": 200 * 2**20,
            "anomaly_rows_per_strategy": 100,
        },
        "scope": (
            "Exploratory reused 2021-24 fixed survivors; conditional actions and shorts; "
            "assumed receipt and OHLCV proxy; no Stage 6."
        ),
    }
    path = ROOT / "EXPERIMENT_REGISTRY.json"
    if path.exists():
        initial = json.loads(path.read_text())
        for key in ("defaults", "support_and_basis", "strategies", "menu_sha256"):
            if canonical(initial[key]) != canonical(body[key]):
                raise ValueError("RESEARCH_POLICY_CANNOT_CHANGE")
        body["initial_registry_sha256"] = digest(path)
        if initial["code"] == body["code"]:
            return initial
        body["identity"] = canonical(body)
        path = ROOT / "registry_versions" / (body["identity"] + ".json")
        if path.exists():
            return verify_registry()
    else:
        body["identity"] = canonical(body)
    publish(path, body)
    return body


def verify_registry() -> dict:
    initial = ROOT / "EXPERIMENT_REGISTRY.json"
    for path in [initial, *sorted((ROOT / "registry_versions").glob("*.json"))]:
        body = json.loads(path.read_text())
        identity = body.pop("identity")
        if (
            canonical(body) != identity
            or body["code"] != code_identity()
            or body["menu_sha256"] != digest(MENU)
        ):
            continue
        if path != initial and body["initial_registry_sha256"] != digest(initial):
            raise ValueError("INITIAL_POLICY_DRIFT")
        if tuple(s["id"] for s in body["strategies"]) != IDS:
            raise ValueError("EIGHTEEN_ID_AXIS")
        body["identity"] = identity
        return body
    raise ValueError("REGISTRY_CODE_OR_MENU_DRIFT")
