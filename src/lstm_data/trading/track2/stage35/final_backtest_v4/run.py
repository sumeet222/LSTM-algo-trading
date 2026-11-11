"""Research-only pilot and full replay. No force switch, no RSA or live access.

The owner authorization is documented input. Every call still verifies all
engineering proofs and exact input/code bindings before constructing an account.
"""

import argparse
import json
from decimal import Decimal

from .driver import Driver
from .paths import ROOT, digest, publish
from .protocol import Scenario, freeze, scenarios
from .release import create_release, scope_fingerprint


def pilot(version: str) -> None:
    protocol = freeze()
    admission = create_release(version, "diagnostic")
    checks = []
    for first, last in protocol["pilot_windows"]:
        output = ROOT / "PILOT_LEDGER_DIAGNOSTICS" / version / first
        engine = Driver((Scenario(),), first, last, output, diagnostic=True, admission=admission)
        result = engine.run()
        passed = (
            Decimal(result["maximum_ledger_residual"]) <= Decimal("1e-8")
            and not result["terminal_pending_orders"]
            and not result["terminal_unpriced_special"]
            and not result["unresolved"]
        )
        checks.append(
            {
                "window": [first, last],
                "passed": passed,
                "receipt": result,
                "files": {str(p): digest(p) for p in output.rglob("*") if p.is_file()},
            }
        )
        print("pilot", first, "PASS" if passed else "HOLD", json.dumps(result), flush=True)
    publish(
        ROOT / ("audits/PILOT_CERTIFICATION_V4_" + scope_fingerprint() + ".json"),
        {
            "all_passed": all(row["passed"] for row in checks),
            "runs": checks,
            "performance_report": False,
            "purpose": "authorized source-backed ledger reconciliation only",
        },
    )


def financial(version: str, kind: str, selected: str | None) -> None:
    freeze()
    if kind != "baseline":
        candidates = list(
            (ROOT / "BASELINE_FOUR_ARM_RESULTS").glob("*/RUN_RECEIPT_2024-12-31.json")
        )
        if not candidates or not any(
            not json.loads(p.read_text())["unresolved"] for p in candidates
        ):
            raise PermissionError("BASELINE_MUST_BE_SEALED_BEFORE_SENSITIVITIES")
    admission = create_release(version, "financial")
    chosen = (
        (Scenario(),)
        if kind == "baseline"
        else tuple(s for s in scenarios() if s.name != "baseline")
    )
    if selected:
        chosen = tuple(s for s in chosen if s.name == selected)
        if not chosen:
            raise ValueError("UNDECLARED_SCENARIO")
    folder = "BASELINE_FOUR_ARM_RESULTS" if kind == "baseline" else "SENSITIVITY_RESULTS"
    output = ROOT / folder / version
    engine = Driver(chosen, "2021-01-01", "2024-12-31", output, admission=admission)
    result = engine.run()
    print(json.dumps(result), flush=True)
    if result["unresolved"] or result["sessions"] != 1005:
        publish(
            output / "RUNTIME_FINANCIAL_HOLD.json",
            {
                "reason": "MATERIAL_EXECUTION_OR_MARK_UNRESOLVED",
                "receipt": result,
                "headline_metrics_computed": False,
            },
        )
        return
    from .analysis import analyze

    analyze(output, admission)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", choices=("pilot", "baseline", "sensitivities", "gate"))
    parser.add_argument("--version", required=True)
    parser.add_argument("--scenario")
    args = parser.parse_args()
    if args.task == "pilot":
        pilot(args.version)
    elif args.task == "gate":
        admission = create_release(args.version, "financial")
        print(admission.release_path)
    else:
        financial(args.version, args.task, args.scenario)


if __name__ == "__main__":
    main()
