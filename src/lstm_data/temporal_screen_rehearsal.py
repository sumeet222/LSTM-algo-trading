"""P026 controlled synthetic full lifecycle; step calls and ledger mutations are forbidden."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import torch

from .config import fingerprint, now, write_json
from .hf1m_action_audit import SYMBOLS
from .hf1m_ft16_loader import ModelInput
from .hf1m_ft16_source import COMMON, ref
from .hf1m_training_data import TrainingView
from .temporal_screen_spec import ARMS, ROLES, RUNS
from .visualization.hf1m_long import LongStudy


class SyntheticStudy(LongStudy):
    """Controlled candles and finite prefix inputs, exclusively for rehearsal scopes."""

    def __init__(self, destination: Path) -> None:
        super().__init__(Path.cwd(), {}, {}, destination, {}, "REHEARSAL_ONLY")
        destination.mkdir(parents=True, exist_ok=False)
        rng = np.random.default_rng(26042)
        count = 180
        common = rng.normal(0, 0.1, (count, 20, len(COMMON))).astype(np.float32)
        m2 = rng.normal(0, 0.1, (count, 20, 2)).astype(np.float32)
        prices = np.broadcast_to(100 + np.arange(20, dtype=float), (count, 20)).copy()
        origins = []
        for day in range(20):
            for slot in (0, 1):
                entry = 47 + day * 6 + slot
                stop = entry + 4
                spread = 1e-6 if day == 0 and slot == 0 else 0.001 * (1 + (day % 5))
                returns = np.linspace(-spread, spread, 20)
                if day == 0 and slot == 0:
                    returns[SYMBOLS.index("AAPL")] = 0.1
                    returns[SYMBOLS.index("VZ")] = 0.09
                prices[stop] = prices[entry] * np.exp(returns)
                origins.append(
                    dict(
                        origin_id=f"SYN:P026:{day:02d}:{slot}",
                        session_date_et=f"2024-04-{day + 1:02d}",
                        first_step=entry - 47,
                        entry_index=entry,
                        exit_index=stop,
                        entry_end_utc=pd.Timestamp(
                            f"2024-04-{day + 1:02d} {14 + slot}:30:00", tz="UTC"
                        ),
                        issuance_utc=pd.Timestamp(
                            f"2024-04-{day + 1:02d} {14 + slot}:32:00", tz="UTC"
                        ),
                    )
                )
        self.origins = pd.DataFrame(origins)
        self.common, self.m2 = common, m2
        self.quality = pd.DataFrame(
            dict(
                step=np.repeat(np.arange(count), 20),
                ticker=np.tile(SYMBOLS, count),
                open=prices.reshape(-1),
                high=prices.reshape(-1),
                low=prices.reshape(-1),
                close=prices.reshape(-1),
                genuine_close=True,
                observed_volume_sum=100.0,
                volume_quality_tier="SYNTHETIC_CONTROLLED_NOT_VENDOR",
                volume_missing_assumed_zero=False,
                hourly_volume_lower_bound=False,
            )
        )
        arrays = {}
        for version in ("inner", "refit"):
            for name, value in dict(
                native_common=common,
                native_m2=m2,
                fallback_common=np.zeros_like(common, dtype=bool),
                fallback_m2=np.zeros_like(m2, dtype=bool),
            ).items():
                arrays[version + "_" + name] = value
        path = destination / "controlled_components.npz"
        np.savez(path, **arrays)
        self.contract = dict(files=dict(components=ref(path)))

    def recipe(self, version: str) -> dict:
        if version not in ("inner", "refit"):
            raise ValueError("P026_SYNTHETIC_FIT")
        return dict(
            epsilon=1e-5 if version == "inner" else 2e-5,
            t2_scale=0.7 if version == "inner" else 0.8,
        )

    def mock_view(self, role: str) -> TrainingView:
        if role not in ROLES:
            raise ValueError("P026_SYNTHETIC_PROTECTED_ROLE")
        version = "inner" if role.startswith("inner") else "refit"
        fit = self.recipe(version)
        q = self.quality.set_index(["step", "ticker"])
        records = []
        for o in self.origins.to_dict("records"):
            entry = (
                q.loc[(o["entry_index"], slice(None)), :]
                .reindex(pd.MultiIndex.from_product([[o["entry_index"]], SYMBOLS]))["close"]
                .to_numpy()
            )
            exit_ = (
                q.loc[(o["exit_index"], slice(None)), :]
                .reindex(pd.MultiIndex.from_product([[o["exit_index"]], SYMBOLS]))["close"]
                .to_numpy()
            )
            r = np.log(exit_ / entry)
            median = np.median(r)
            mad = np.median(abs(r - median))
            for j, ticker in enumerate(SYMBOLS):
                records.append(
                    dict(
                        origin_id=o["origin_id"],
                        ticker=ticker,
                        session_date_et=o["session_date_et"],
                        TG20=(r[j] - median) / (mad + fit["epsilon"]),
                        return_4h=r[j],
                        cross_section_median=median,
                        cross_section_mad=mad,
                        numerator=r[j] - median,
                        epsilon=fit["epsilon"],
                        label_eligible=True,
                    )
                )
        return TrainingView(
            ModelInput(self.origins, self.common, self.m2, pd.DataFrame(records), version, fit),
            role,
        )

    def table(self, key: str) -> pd.DataFrame:
        if key != "candles_quality":
            raise ValueError("P026_SYNTHETIC_SOURCE_ALLOWLIST")
        return self.quality.copy()

    def prediction(self, run_id: str, role: str) -> pd.DataFrame:
        if run_id not in ("HF1M-LONG-TM0-T2-S42-DEV1", "HF1M-LONG-TM0-T2-S123-DEV1"):
            raise ValueError("P026_SYNTHETIC_BASELINE")
        from .objective_screen_source import ordered_targets

        f = ordered_targets(self.mock_view(role))
        f["pred_original_TG20"] = 0.0
        f["raw_net_output"] = np.float32(0.0)
        return f


def rehearse(
    out: Path, private: Path, validation: Path, receipt_name: str = "stage_1_receipt.json"
) -> None:
    from .objective_screen_run import storage_bytes
    from .temporal_screen_authority import (
        JOURNAL,
        POINTER,
        code_binding,
        ensure,
        predecessor_gate,
        require_gate,
    )
    from .temporal_screen_diagnostics import diagnose
    from .temporal_screen_run import lifecycle

    stage0_path = out / "P026_STAGE_0_SOURCE_AND_AUTHORITY_RECEIPT.json"
    stage0 = json.loads(stage0_path.read_text())
    if (
        stage0["status"] != "PASS_P026_IDENTITY_AND_AUTHORITY"
        or private.exists()
        or JOURNAL.exists()
    ):
        raise ValueError("P026_NEW_REHEARSAL_NAMESPACE_REQUIRED")
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    before = ref(POINTER)
    started = time.monotonic()
    private.mkdir(parents=True)
    (private / ".gitignore").write_text("*\n!.gitignore\n")
    study = SyntheticStudy(private / "controlled_source")
    code = code_binding()
    draft = dict(
        scope="REHEARSAL_ONLY",
        code=code,
        input_contract=stage0["input_contract"],
        scientific_definitions=stage0["scientific_definitions"],
        recipes={
            a: {
                v: dict(scale=study.recipe(v)["t2_scale"], epsilon=study.recipe(v)["epsilon"])
                for v in ("inner", "refit")
            }
            for a in ARMS
        },
        source_hashes=stage0["source_hashes"],
        baseline_refs=stage0["baseline_refs"],
        protected_refs=stage0["protected_refs"],
        validation=ref(validation),
        storage_before=storage_bytes([Path(".")]),
    )
    draft_path = private / "rehearsal_plan.json"
    write_json(draft_path, draft)
    calls = 0
    gates = []
    blocked = []

    def forbidden_step(*args, **kwargs):
        nonlocal calls
        calls += 1
        raise RuntimeError("P026_REHEARSAL_STEP_FORBIDDEN")

    with patch.object(torch.optim.AdamW, "step", forbidden_step):
        for arm in ARMS:
            result = lifecycle(draft_path, arm, private / arm, rehearsal=True, study_override=study)
            gate = diagnose(
                draft,
                result,
                private / (arm + "_diagnostics"),
                rehearsal=True,
                study_override=study,
            )
            gp = private / (arm + "_diagnostics/gate.json")
            require_gate(gp, arm, rehearsal=True)
            try:
                require_gate(gp, arm)
            except ValueError:
                blocked.append(arm + "_REHEARSAL_NOT_LIVE")
            else:
                raise ValueError("P026_REHEARSAL_ESCAPED")
            gates.append(ref(gp))
            print(gate["status"] + " REHEARSAL_ONLY", flush=True)
    for label, operation in [
        ("NO_APPROVAL", lambda: ensure(draft_path, None, RUNS[0])),
        ("A2_NO_PRIOR_GATE", lambda: predecessor_gate(draft_path, RUNS[1], [])),
        ("A3_NO_PRIOR_GATE", lambda: predecessor_gate(draft_path, RUNS[2], [])),
    ]:
        try:
            operation()
        except (ValueError, FileNotFoundError):
            blocked.append(label)
        else:
            raise ValueError("P026_CONTROLLER_BYPASS")
    if calls or ref(POINTER) != before or JOURNAL.exists() or code_binding() != code:
        raise ValueError("P026_REHEARSAL_MUTATED_AUTHORITY")
    write_json(
        out / receipt_name,
        dict(
            status="PASS_P026_ZERO_STEP_REHEARSAL_AND_PROPOSAL",
            scope="REHEARSAL_ONLY",
            at=now(),
            ledger=53,
            neural_starts=0,
            optimizer_step_calls=calls,
            code=code,
            execution_sha256=fingerprint(code),
            gates=gates,
            blocked=blocked,
            all_role_exports=12,
            exact_cases=66,
            synthetic_controlled_candles=True,
            source_identity=ref(stage0_path),
            validation=ref(validation),
            seconds=time.monotonic() - started,
        ),
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--private", type=Path, required=True)
    p.add_argument("--validation", type=Path, required=True)
    p.add_argument("--receipt-name", default="stage_1_receipt.json")
    a = p.parse_args()
    rehearse(a.out, a.private, a.validation, a.receipt_name)
