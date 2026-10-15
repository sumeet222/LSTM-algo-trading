"""Non-fitting hand checks of the candidate baseline adapter."""

import json

import numpy as np
import pytest

from lstm_data.config import digest
from lstm_data.pilot_postrun import lag_design, require_baseline_decision


def test_frozen_ridge_lags_are_lag_major_channel_minor():
    source = np.arange(5 * 48 * 16).reshape(5, 48, 16)
    actual = lag_design(source)
    assert actual.shape == (5, 112)
    for offset, lag in enumerate((0, 1, 2, 5, 11, 23, 47)):
        np.testing.assert_array_equal(
            actual[:, offset * 16 : (offset + 1) * 16], source[:, 47 - lag]
        )


def test_approval_is_exact_and_not_neural_authority(tmp_path):
    proposal = tmp_path / "proposal.json"
    proposal.write_text(json.dumps({"scope": "WF1"}))
    decision = {
        "actor_type": "human",
        "owner": "Track A researcher",
        "status": "APPROVED",
        "scope": "M1_AND_OWN_RIDGE_112_WF1_ONLY",
        "proposal_sha256": digest(proposal),
        "response_text": "Approve this non-neural baseline scope",
        "response_provenance": "test",
    }
    require_baseline_decision(decision, proposal)
    with pytest.raises(ValueError, match="NONNEURAL"):
        require_baseline_decision(
            {**decision, "scope": "ONE_CONDITIONAL_TM0_WF1_SEED42_PAIR_ONLY"}, proposal
        )
    proposal.write_text("changed")
    with pytest.raises(ValueError, match="NONNEURAL"):
        require_baseline_decision(decision, proposal)
