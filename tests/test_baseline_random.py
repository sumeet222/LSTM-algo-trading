"""Stable uniform permutation substreams and independently replayed scenarios."""

from dataclasses import replace
from decimal import Decimal as D

import numpy as np
import pytest

from lstm_data.baseline_fixtures import random_fixture
from lstm_data.baseline_random import draws, path_script, random_matrix, replay_scenario
from lstm_data.p3_audit import reconstruct
from lstm_data.p3_domain import MODE, Permission, UniverseSpec


def u():
    return UniverseSpec("SYN:RANDOM:v1", ("ONE", "TWO", "THREE", "FOUR", "FIVE"))


def test1000_streams_uniform_distinct_names_global_rng_independence():
    universe = u()
    op, template, start = random_fixture(universe)
    all_draws = [
        draws(universe, op, i, Permission(MODE), allow_synthetic=True) for i in range(1000)
    ]
    assert len({d[0].stream_id for d in all_draws}) == 1000
    assert all(len(d) == 2 and len(set(x.permutation)) == 5 for d in all_draws for x in d)
    before = all_draws[499]
    np.random.seed(999)
    np.random.random(10000)
    assert before == draws(universe, op, 499, Permission(MODE), allow_synthetic=True)
    assert not op[-1].eligible and not op[-2].eligible
    # Source unknown/future publication prevents a draw; future exits aren't inputs.
    unknown = (replace(op[0], available_at=None),) + op[1:]
    assert len(draws(universe, unknown, 0, Permission(MODE), allow_synthetic=True)) == 1
    with pytest.raises(ValueError):
        draws(universe, op, 0, Permission(MODE))
    with pytest.raises(ValueError):
        replace(op[0], basis="DOCUMENTED")


def test24_fresh_scenarios_reconstructed_and_future_exit_invariant():
    universe = u()
    op, template, start = random_fixture(universe)
    from lstm_data.p3_execution import ExecutionOffer

    script, d = path_script(universe, op, template, 999, Permission(MODE))
    changed = (
        template[:2]
        + (
            replace(
                template[2], offers=tuple(ExecutionOffer(universe, r) for r in template[2].marks)
            ),
        )
        + template[3:]
    )
    _, same = path_script(universe, op, changed, 999, Permission(MODE))
    assert d == same
    hashes = set()
    veto = 0
    for policy in ("A", "B"):
        for c in (0, 2, 5, 10):
            for b in (D(0), D(".005"), D(".03")):
                e = replay_scenario(
                    Permission(MODE), universe, script, policy, c, b, D(10000), start
                )
                recovered = reconstruct(e.ledger.export(), universe)
                assert recovered["cash"] == e.book.cash and recovered["shares"] == e.book.balances
                hashes.add(e.ledger.trace_id)
                veto += e.rejections.count("POLICY_B_VIRTUAL_CONFLICT")
    assert len(hashes) == 24 and veto > 0


def test_checkpoint_binding_resume_and_alternate_order(tmp_path):
    universe = UniverseSpec("SYN:ALT", ("TIN", "MAP", "FOX", "ORB", "ZEN"))
    op, template, start = random_fixture(universe)
    first = random_matrix(
        Permission(MODE),
        universe,
        op,
        template,
        D(10000),
        start,
        tmp_path,
        allow_synthetic=True,
        stop_after_paths=1,
    )
    assert first["completed_scenarios"] == 24 and first["status"] == "CHECKPOINT_PARTIAL"
    resumed = random_matrix(
        Permission(MODE),
        universe,
        op,
        template,
        D(10000),
        start,
        tmp_path,
        allow_synthetic=True,
        stop_after_paths=2,
    )
    assert resumed["completed_scenarios"] == 48
    with pytest.raises(ValueError):
        random_matrix(
            Permission(MODE),
            universe,
            op,
            template,
            D(10001),
            start,
            tmp_path,
            allow_synthetic=True,
            stop_after_paths=2,
        )


def test_permission_lease_economic_equivalence_and_invalid_mode():
    from lstm_data.baseline_authority import replay_permission
    from lstm_data.p3_domain import Frictions
    from lstm_data.p3_replay import replay

    universe = u()
    op, template, start = random_fixture(universe)
    script, _ = path_script(universe, op, template, 499, Permission(MODE))
    original = replay(Permission(MODE), universe, script, "A", Frictions(universe), D(10000), start)
    leased = replay_scenario(Permission(MODE), universe, script, "A", 5, D(0), D(10000), start)
    assert original.ledger.trace_id == leased.ledger.trace_id
    with pytest.raises(ValueError):
        replay_permission(Permission("EMPIRICAL"))


def test_golden_first_middle_last_and_alternate_name_order():
    universe = u()
    op, _, _ = random_fixture(universe)
    expected = {
        0: ((1, 4, 2, 3, 0), (3, 1, 4, 0, 2)),
        499: ((3, 1, 2, 0, 4), (1, 0, 2, 3, 4)),
        999: ((2, 4, 3, 1, 0), (0, 1, 3, 2, 4)),
    }
    for path, indices in expected.items():
        actual = draws(universe, op, path, Permission(MODE), allow_synthetic=True)
        assert tuple(d.permutation for d in actual) == tuple(
            tuple(universe.symbols[i] for i in order) for order in indices
        )
    alternate = UniverseSpec("SYN:ALT", ("TIN", "MAP", "FOX", "ORB", "ZEN"))
    other, _, _ = random_fixture(alternate)
    actual = draws(alternate, other, 0, Permission(MODE), allow_synthetic=True)
    assert tuple(d.permutation for d in actual) == tuple(
        tuple(alternate.symbols[i] for i in order) for order in expected[0]
    )
