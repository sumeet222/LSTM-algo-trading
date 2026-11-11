import hashlib
import json
from pathlib import Path

from lstm_data.trading.track2.stage35.policy_config import LIMITS


def test_frozen_namespaces_unchanged():
    before = json.loads(Path("trading/track2/stage35/audits/H0_before.json").read_text())
    for row in before["protected_files"]:
        path = Path(row["path"])
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"]
        assert path.stat().st_mtime_ns == row["mtime_ns"]


def test_bounded_cross_fold_signal_receipt_no_economics():
    root = Path("trading/track2/stage35/audits/H4_signals_v1")
    coverage = json.loads((root / "coverage.json").read_text())
    assert coverage["keys"] == 16 and coverage["folds"] == [2021, 2022, 2023, 2024]
    assert coverage["orders"] == coverage["fills"] == coverage["positions"] == coverage["pnl"] == 0
    records = json.loads((root / "signal_intents.json").read_text())
    assert coverage["source_eligible_signals"] + coverage["source_abstentions"] == 16
    for record in records:
        if "intent" in record:
            intent = record["intent"]
            assert "price" not in intent and "pnl" not in intent
            assert intent["model_hash"] == record["signal"]["checkpoint_hash"]
    assert (
        LIMITS.gross == 1
        and LIMITS.net == 1
        and str(LIMITS.name) == "0.1"
        and str(LIMITS.vintage) == "0.2"
    )
