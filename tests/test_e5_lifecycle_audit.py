"""Gate C must fail before a fit when synthetic evidence/configuration is invalid."""

import json

import pytest

from lstm_data.e5_lifecycle_audit import run


@pytest.mark.parametrize(
    "status,checks", [("FAILED", {"heldout": False}), ("PASS", {"heldout": False})]
)
def test_failed_learning_cannot_start_actual_pair(tmp_path, status, checks):
    root = tmp_path / "extension_1024"
    root.mkdir()
    (root / "health_v2_result.json").write_text(json.dumps({"status": status, "checks": checks}))
    with pytest.raises(ValueError, match="HEALTH_PASS"):
        run(tmp_path)
    assert not (tmp_path / "lifecycle_reservation.json").exists()
    assert not (tmp_path / "seed42_pair").exists()


def test_changed_prospective_config_cannot_start_actual_pair(tmp_path):
    root = tmp_path / "extension_1024"
    root.mkdir()
    (root / "health_v2_result.json").write_text(
        json.dumps({"status": "PASS", "checks": {"heldout": True}, "config_sha": "STALE"})
    )
    (root / "fixture_v2_config.json").write_text("{}")
    with pytest.raises(ValueError, match="CONFIGURATION_SHA"):
        run(tmp_path)
    assert not (tmp_path / "lifecycle_reservation.json").exists()
    assert not (tmp_path / "seed42_pair").exists()
