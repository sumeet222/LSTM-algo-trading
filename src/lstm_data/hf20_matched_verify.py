"""Independent saved-state GARCH audit; no optimizer or neural calls."""

from __future__ import annotations

import numpy as np
import pandas as pd
from arch.univariate import GARCH

from . import hf20_matched as task
from .hf20_classical_math import folded_normal


def verify_garch() -> None:
    """Recompute the supported prefix filter and every saved later update/forecast."""
    b, old, out = task.b, task.old, task.OUT
    status = b.read(out / "garch_status.json")
    if status["fits"] == 0:
        return
    _, rows = b.metadata()
    plans = old.clock.saved_plans(rows)
    signed = old.signed_targets(rows)
    audit = pd.read_csv(out / "garch_overlap_audit.csv")
    traces = pd.read_csv(out / "garch_filter_trace.csv", float_precision="round_trip")
    diagnostics = pd.read_csv(out / "garch_fit_diagnostics.csv")
    assert len(diagnostics) == 560 and not diagnostics.duplicated(["year", "ticker", "slot"]).any()
    checks = []
    for d in diagnostics.to_dict("records"):
        year = int(d["year"])
        slot = str(d["slot"])
        ticker = str(d["ticker"])
        dest = out / f"GARCH/F{year % 100}" / (ticker + "_" + slot.replace(":", ""))
        assert (dest / "started.json").exists()
        if d["status"] != "PASS":
            checks.append(dict(year=year, slot=slot, ticker=ticker, status=d["status"]))
            continue
        fit = b.read(dest / "parameters.json")
        with np.load(dest / "fit_state.npz") as saved:
            ix = saved["indices"]
            x = saved["x"]
            h = saved["h"]
        retained = audit.loc[audit.slot.eq(slot) & audit.retained, "row_index"].to_numpy(int)
        np.testing.assert_array_equal(ix, np.intersect1d(retained, plans[year]["restricted_refit"]))
        j = list(b.SYMBOLS).index(ticker)
        np.testing.assert_array_equal(x, 100 * signed[ix, j])
        mu = float(fit["mu_percent"])
        omega = float(fit["omega_percent_squared"])
        alpha = float(fit["alpha"])
        beta = float(fit["beta"])
        vol = GARCH(p=1, q=1)
        initial = x - x.mean()
        computed = vol.compute_variance(
            np.array([omega, alpha, beta]),
            x - mu,
            np.zeros(len(x)),
            vol.backcast(initial),
            vol.variance_bounds(initial),
        )
        np.testing.assert_allclose(h, computed, rtol=1e-12, atol=1e-12)
        u = pd.read_csv(dest / "state_updates.csv", float_precision="round_trip")
        state = omega + alpha * (x[-1] - mu) ** 2 + beta * h[-1]
        states = [state]
        future = retained[retained > ix[-1]]
        np.testing.assert_array_equal(u.row_index, future[: len(u)])
        for update in u.to_dict("records"):
            idx = int(update["row_index"])
            np.testing.assert_allclose(update["h_before"], state, rtol=1e-12)
            assert update["x"] == 100 * signed[idx, j]
            state = omega + alpha * (update["x"] - mu) ** 2 + beta * state
            np.testing.assert_allclose(update["h_after"], state, rtol=1e-12)
            states.append(state)
        f = traces.loc[(traces.year == year) & (traces.slot == slot) & (traces.ticker == ticker)]
        for record in f.to_dict("records"):
            issue = pd.Timestamp(record["issue"])
            latest = int(record["updates_after_fit"])
            admissible = rows.iloc[future].label_maturity_utc.lt(issue).to_numpy()
            assert latest == int(admissible.sum())
            index = int(future[latest - 1]) if latest else int(ix[-1])
            assert rows.iloc[index].origin_id == record["latest_update_origin"]
            assert rows.iloc[index].label_maturity_utc < issue
            np.testing.assert_allclose(
                record["variance_percent_squared"], states[latest], rtol=1e-12
            )
            pred = folded_normal(np.array([mu / 100]), np.array([states[latest] / 10000]))[0]
            np.testing.assert_allclose(record["prediction"], pred, rtol=1e-12, atol=1e-15)
        checks.append(
            dict(
                year=year,
                slot=slot,
                ticker=ticker,
                status="PASS",
                updates=len(u),
                forecasts=len(f),
                max_variance=float(max(states)),
            )
        )
    pd.DataFrame(checks).to_csv(out / "garch_replay_verification.csv", index=False)
    b.write(
        out / "garch_verification.json",
        dict(
            status="PASS_DIAGNOSTIC_REPLAY",
            eligible_complete_arm=status["status"] == "COMPLETE",
            units=len(checks),
            passing_units=int(diagnostics.status.eq("PASS").sum()),
            forecasts_checked=len(traces),
            all_maturity_frontiers=True,
            initial_filters_and_all_updates_replayed=True,
            **task.resources(),
        ),
    )


if __name__ == "__main__":
    verify_garch()
