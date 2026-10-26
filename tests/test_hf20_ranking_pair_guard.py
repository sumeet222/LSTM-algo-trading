"""SYN-only regression: preserve fp32 objective/gradient and charged failed65."""

from unittest.mock import patch

import numpy as np
import pytest
import torch

from lstm_data import hf20_ranking as original
from lstm_data import hf20_ranking_continue as campaign
from lstm_data.config import fingerprint
from lstm_data.hf20_ranking_pair_guard import (
    REMAINING,
    pair_terms,
    validate_events,
    validation_adapter,
)


def reproducer():
    rng = np.random.default_rng(6503)
    for batch in range(248):
        sv = rng.normal(0, (0.1, 0.2, 0.4, 1.0, 2.0)[batch % 5], (29, 20)).astype("float32")
        rv = np.round(rng.normal(0, 0.01, (29, 20)), (1, 2, 3)[batch % 3])
    return torch.tensor(sv), torch.tensor(rv)


def test_same_fp32_values_and_gradients_higher_precision_audit():
    torch.set_num_threads(4)
    score, r = reproducer()
    with pytest.raises(AssertionError):
        original.pair_terms(score, r)
    new_score = score.clone().requires_grad_()
    old_score = score.clone().requires_grad_()
    # Bypass only the known-bad old assertion in this SYN oracle, not any training operation.
    with patch("numpy.testing.assert_allclose"):
        old_terms, old_alloc = original.pair_terms(old_score, r)
    new_terms, new_alloc = pair_terms(new_score, r)
    torch.testing.assert_close(new_terms, old_terms, rtol=0, atol=0)
    torch.testing.assert_close(new_alloc, old_alloc, rtol=0, atol=0)
    old_alloc.sum().backward()
    new_alloc.sum().backward()
    torch.testing.assert_close(new_score.grad, old_score.grad, rtol=0, atol=0)
    assert new_terms.dtype == torch.float32 and new_alloc.dtype == torch.float32


def test_adapter_explicit_and_restored_and_true_defects_still_rejected():
    old = original.pair_terms
    old_hash = campaign.continuation_hash
    with validation_adapter():
        assert original.pair_terms is pair_terms
        with pytest.raises(ValueError, match="NONFINITE"):
            pair_terms(torch.full((1, 20), float("nan")), torch.arange(20)[None, :])
        with pytest.raises(ValueError, match="NO_VALID"):
            pair_terms(torch.zeros(1, 20), torch.zeros(1, 20))
    assert original.pair_terms is old and campaign.continuation_hash is old_hash


def test_successor_budget_only_nine_unstarted_runs():
    assert REMAINING[0] == "HF20-S1S2-F22-T2R-S42" and len(REMAINING) == 9
    rows = []
    for index, run in enumerate(REMAINING):
        for status in ("STARTED", "CALIBRATED", "REFITTING", "COMPLETED"):
            rows.append(
                dict(
                    sequence=len(rows) + 1,
                    previous=fingerprint(rows),
                    run_id=run,
                    status=status,
                    global_started_pairs=66 + index,
                    effective_ceiling=200,
                    detail={},
                )
            )
    validate_events(rows)
    assert rows[-1]["global_started_pairs"] == 74
    bad = dict(rows[0], run_id="HF20-S1S2-F21-PW-S42")
    with pytest.raises(ValueError, match="NO_RETRY65"):
        validate_events([bad])


def test_corrected_guard_actual_synthetic_optimizer_checkpoint():
    import io

    from lstm_data.neural_engine import SharedLSTM, optimizer, seed_all

    seed_all(42)
    model = SharedLSTM()
    opt = optimizer(model)
    x = torch.randn(40, 48, 16)
    r = torch.arange(20, dtype=torch.float64).repeat(2, 1)
    with validation_adapter():
        score = model(x).reshape(2, 20)
        loss = original.row_loss("PW", score, r, r.float(), 1).sum() / 2
        loss.backward()
        norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 1, error_if_nonfinite=True)
        assert torch.isfinite(norm)
        opt.step()
        model.eval()
        saved = io.BytesIO()
        torch.save(model.state_dict(), saved)
        saved.seek(0)
        loaded = SharedLSTM().eval()
        loaded.load_state_dict(torch.load(saved, weights_only=True))
        with torch.no_grad():
            torch.testing.assert_close(model(x), loaded(x), rtol=0, atol=0)


def test_actual_successor_journal_charges66_and_rejects65(tmp_path, monkeypatch):
    import json
    from pathlib import Path

    from lstm_data.hf20_ranking_pair_guard import GuardJournal

    monkeypatch.chdir(tmp_path)
    Path("configs").mkdir()
    Path("reports/audit").mkdir(parents=True)
    out = Path("reports/experiments/SYN_GUARD")
    out.mkdir(parents=True)
    (out / "PAIR_GUARD_PROSPECTIVE_AMENDMENT.json").write_text("{}")
    (out / "submitted_continuation_authority.txt").write_text("SYN_ONLY")
    (out / "STAGE_B_HANDOFF.json").write_text("{}")
    Path("reports/audit/SYN_v19.jsonl").write_text("SYN_PRIOR65\n")
    (out / "registry_v19_before_guard.json").write_text(
        json.dumps(dict(real_journal="reports/audit/SYN_v19.jsonl", budget_amendment={}))
    )
    journal = GuardJournal(out, {"execution_sha256": "SYN"})
    with patch("lstm_data.hf20_ranking_pair_guard.amended_hash", return_value="SYN"):
        with pytest.raises(ValueError, match="NO_RETRY65"):
            journal.event("HF20-S1S2-F21-PW-S42", "STARTED", {})
        for status in ("STARTED", "CALIBRATED", "REFITTING", "COMPLETED"):
            journal.event(REMAINING[0], status, {})
        assert journal.started == 66
        with pytest.raises(FileNotFoundError):
            journal.event(REMAINING[1], "STARTED", {})
