"""Historical code versions resolve explicitly; numerical/current-code corruption never does."""

import json
from pathlib import Path

import pandas as pd
import pytest

from lstm_data.hf1m_ft16_source import ref
from lstm_data.optimization_screen_closeout import verify_lrlow_history


def test_history_resolution_keeps_numerical_and_current_code_hashes_mandatory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    payload, archive, code = Path("metrics.json"), Path("executed.py.txt"), Path("parser.py")
    payload.write_text('{"verified": true}')
    archive.write_text("original executed parser")
    code.write_text("preapproved parser with rehearsal adapter")
    base = Path("base.json")
    base.write_text(json.dumps(dict(status="PASS_LRLOW", evidence=[ref(payload)])))
    gate = Path("gate.json")
    gate.write_text(
        json.dumps(
            dict(
                status="PASS_IMMEDIATE_LRLOW",
                base_gate=ref(base),
                evidence=[ref(payload)],
                supplemental_code=ref(archive),
                type_hygiene_successor=dict(
                    path=str(code),
                    bytes=12,
                    sha256="0" * 64,
                ),
            )
        )
    )
    inventory = Path("inventory.csv")
    pd.DataFrame([ref(code)]).to_csv(inventory, index=False)
    Path("verification_closeout_receipt.json").write_text(
        json.dumps(dict(inventory=ref(inventory)))
    )
    value = verify_lrlow_history(Path("."), ref(gate))
    assert value["current_preapproved_code"] == ref(code)
    assert value["executed_archive"] == ref(archive)
    assert value["superseded_code_metadata"]["scope"] == "HISTORICAL_INTERMEDIATE_VERSION"
    code.write_text("unapproved code change")
    with pytest.raises(ValueError, match="input bytes changed"):
        verify_lrlow_history(Path("."), ref(gate))
    code.write_text("preapproved parser with rehearsal adapter")
    payload.write_text('{"verified": false}')
    with pytest.raises(ValueError, match="input bytes changed"):
        verify_lrlow_history(Path("."), ref(gate))
