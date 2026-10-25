"""Synthetic arithmetic and pre-I/O rejection; never fit or invoke a model."""

import json
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest
from audit import Reader, decomposition, rank_metrics, ranked, weights
from components import parts


def fixture() -> pd.DataFrame:
    return pd.DataFrame(
        dict(
            origin_id=np.repeat([0, 1, 2], 20),
            ticker=np.tile([f"T{i}" for i in range(20)], 3),
            stock_order=np.tile(np.arange(20), 3),
            session_date_et=np.repeat(["2025-01-02", "2025-01-02", "2025-01-03"], 20),
        )
    )


def test_hierarchical_weights_and_partitions() -> None:
    f = fixture()
    w = weights(f)
    np.testing.assert_allclose([w[:20].sum(), w[20:40].sum(), w[40:].sum()], [0.25, 0.25, 0.5])
    mask = ranked(np.ones(60), f, 5)
    assert np.flatnonzero(mask).tolist() == [0, 1, 2]
    np.testing.assert_allclose(w[mask].sum() + w[~mask].sum(), 1, atol=1e-15)
    with pytest.raises(ValueError, match="DUPLICATE"):
        weights(pd.concat([f, f.iloc[[0]]]))
    with pytest.raises(ValueError, match="INCOMPLETE"):
        weights(f.iloc[:-1])


@pytest.mark.parametrize("offset", [0.0, 1.0, -5.0])
def test_decomposition_and_rank_invariance(offset: float) -> None:
    y = np.arange(40, dtype=float).reshape(2, 20) / 7
    p = y * 0.1 + offset
    total, common, centered = decomposition(y, p)
    np.testing.assert_allclose(total, common + centered, rtol=1e-13)
    np.testing.assert_allclose(rank_metrics(y, p)["ic"], 1)


def test_ties_constants_reversed_ranks() -> None:
    y = np.arange(20, dtype=float)[None, :]
    constant = rank_metrics(y, y * 0)
    assert np.isnan(constant["ic"]).all()
    np.testing.assert_allclose(constant["concordance"], 0.5)
    np.testing.assert_allclose(constant["top4"], 0.2)
    np.testing.assert_allclose(rank_metrics(y, -y)["ic"], -1)
    np.testing.assert_allclose(rank_metrics(y, y)["top4"], 1)


@pytest.mark.parametrize("role", ["confirmation", "2026", "", "held_out"])
def test_protected_role_rejected_before_io(tmp_path: Path, role: str) -> None:
    (tmp_path / "input_manifest.json").write_text(json.dumps({"evidence": []}))
    reader = Reader(tmp_path)
    with patch("pandas.read_parquet", side_effect=AssertionError("I/O must not occur")):
        with pytest.raises(ValueError, match="PROTECTED_OR_UNKNOWN_ROLE_BEFORE_IO"):
            reader.table(Path("not-opened.parquet"), role)


def test_nonallowlisted_path_rejected_before_io(tmp_path: Path) -> None:
    (tmp_path / "input_manifest.json").write_text(json.dumps({"evidence": []}))
    reader = Reader(tmp_path)
    with patch("pandas.read_parquet", side_effect=AssertionError("I/O must not occur")):
        with pytest.raises(ValueError, match="NONALLOWLISTED"):
            reader.table(Path("not-opened.parquet"), "development")


def test_subset_cross_term_cannot_be_discarded() -> None:
    y = np.arange(20, dtype=float)
    p = np.zeros(20)
    common, centered, cross = parts(y, p)
    np.testing.assert_allclose(common + centered + cross, (y - p) ** 2)
    np.testing.assert_allclose(cross.mean(), 0, atol=1e-13)
    assert abs(cross[-1]) > 1
