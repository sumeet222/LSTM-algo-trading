"""Single fixed newest-hour price-only H8 experiment; no minute volume access."""

from __future__ import annotations

import argparse
import gc
import json
import os
import subprocess
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch import nn

from . import hf20_mag_c3_io as c3
from . import hf20_mag_designa as b
from . import hf20_minute_bc as prior
from . import hf20_minute_inputs as source
from . import hf20_overnight_specialist as previous
from . import hf20_stage2_bcd as clock
from .hf20_s4_clock import sessions
from .neural_engine import seed_all

OUT = Path("reports/experiments/hf20_s9_mag_stage3_s3c_priceonly_2026-10-28")
DEST = OUT
RAW, CAL = "S3C-PRICE-RAW", "S3C-PRICE-C3"
PROTOCOL = OUT / "S3C_PRICE_ONLY_PROTOCOL.json"


def price_channels(prices: np.ndarray, observed: np.ndarray) -> np.ndarray:
    """Native RET/RANGE; false observation payloads cannot influence either field."""
    if prices.shape != (*observed.shape, 4) or observed.shape[-1] != 60:
        raise ValueError("EXACT_60_PRICE_POSITIONS_REQUIRED")
    safe = np.where(observed[..., None], prices, 1.0)
    if not np.isfinite(safe).all() or (safe <= 0).any():
        raise ValueError("INVALID_GENUINE_PRICE")
    ret_obs = observed[..., 1:] & observed[..., :-1]
    result = np.zeros((*observed.shape, 2), np.float32)
    result[..., 1] = np.where(observed, np.log(safe[..., 1] / safe[..., 2]), 0)
    result[..., 1:, 0] = np.where(ret_obs, np.log(safe[..., 1:, 3] / safe[..., :-1, 3]), 0)
    if not np.isfinite(result).all():
        raise ValueError("NONFINITE_PRICE_PATH")
    return result


def five_channels(native: np.ndarray, observed: np.ndarray, floors: np.ndarray) -> np.ndarray:
    """Assemble the exact five channels with legal stock-phase hourly floors."""
    if floors.shape != (20,) or not np.isfinite(floors).all() or (floors <= 0).any():
        raise ValueError("LAWFUL_POSITIVE_HOURLY_FLOORS_REQUIRED")
    result = np.zeros((*observed.shape, 5), np.float32)
    valid_ret = np.zeros_like(observed)
    valid_ret[..., 1:] = observed[..., 1:] & observed[..., :-1]
    result[..., 0] = np.where(valid_ret, native[..., 0], 0) / floors[None, :, None]
    result[..., 1] = np.where(observed, native[..., 1], 0) / floors[None, :, None]
    result[..., 2], result[..., 3] = observed, valid_ret
    result[..., 4] = np.arange(60, dtype=np.float32) / 59
    if not np.isfinite(result).all():
        raise ValueError("NONFINITE_MINUTE_TENSOR")
    return result


class PriceOnlyMAG(clock.ClockMAG):
    """Original hourly H32/clock information plus independent newest-hour price H8."""

    def __init__(self) -> None:
        nn.Module.__init__(self)
        self.input_dim = 16
        self.lstm = nn.LSTM(16, 32, num_layers=1, batch_first=True)
        self.dropout = nn.Dropout(0.10)
        self.minute_lstm = nn.LSTM(5, 8, num_layers=1, batch_first=True)
        self.head = nn.Linear(50, 1)

    def minute_embedding(self, minute: torch.Tensor) -> torch.Tensor:
        if minute.shape[1:] != (60, 5):
            raise ValueError("SIXTY_BY_FIVE_REQUIRED")
        price_obs, ret_obs = minute[..., 2].bool(), minute[..., 3].bool()
        clean = torch.stack(
            [
                torch.where(ret_obs, minute[..., 0], 0),
                torch.where(price_obs, minute[..., 1], 0),
                price_obs.float(),
                ret_obs.float(),
                minute[..., 4],
            ],
            dim=-1,
        )
        if not bool(torch.isfinite(clean).all()):
            raise ValueError("NONFINITE_OBSERVED_MINUTE_TENSOR")
        _, (hidden, _) = self.minute_lstm(clean)
        return torch.where(price_obs.any(dim=1)[:, None], hidden[-1], 0)

    def forward(
        self,
        x: torch.Tensor,
        clock: torch.Tensor | None = None,
        minute: torch.Tensor | None = None,
    ) -> torch.Tensor:
        if clock is None or clock.shape != (len(x), 10) or minute is None:
            raise ValueError("TEN_CLOCK_AND_PRICE_PATH_REQUIRED")
        if not bool(torch.isfinite(clock).all()):
            raise ValueError("FINITE_CLOCK_REQUIRED")
        return self.head(
            torch.cat([self.dropout(self.encode(x)), clock, self.minute_embedding(minute)], dim=1)
        ).squeeze(-1)


def model_for_price() -> PriceOnlyMAG:
    seed_all(42)
    model = PriceOnlyMAG().float()
    assert sum(p.numel() for p in model.parameters()) == 6931
    return model


class PriceView(b.View):
    """Unchanged 48x16 FT16 and one unique newest-hour path, normalized on demand."""

    def __init__(
        self, c: b.Components, rows: pd.DataFrame, returns: np.ndarray, phase: dict, paths: tuple
    ):
        recipe = b.read(Path(phase["recipe_reference"]))
        super().__init__(c, rows, returns, recipe, phase["scale"])
        self.native, self.observed, self.mapping = paths
        self.floors = np.asarray([x["hourly_floor"] for x in recipe["floors"]])
        assert (self.floors > 0).all() and np.isfinite(self.floors).all()

    def minute(self, pos: np.ndarray) -> np.ndarray:
        ix = self.mapping[self.rows.iloc[pos].entry_index.to_numpy(int)]
        if (ix < 0).any():
            raise ValueError("MISSING_ORIGINAL_MINUTE_KEY")
        return five_channels(self.native[ix], self.observed[ix], self.floors)


def load_paths() -> tuple:
    return (
        np.load(OUT / "minute_price_native.npy", mmap_mode="r"),
        np.load(OUT / "minute_price_observed.npy", mmap_mode="r"),
        np.load(OUT / "minute_hour_mapping.npy"),
    )


def resources() -> dict:
    project = int(subprocess.check_output(["du", "-sk", "."], text=True).split()[0]) * 1024
    task = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    result = dict(project_bytes=project, task_bytes=task, peak_rss_bytes=b.memory())
    if project + 50_000_000 > 15_000_000_000 or task + 50_000_000 > 2_500_000_000:
        raise ValueError("RESOURCE_CEILING", result)
    return result


def numeric_price_blocks(ref: dict, hours: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, dict]:
    """Price-only projection of the prior certified adapter; never decode volume."""
    path = Path(ref["path"])
    assert "2010-07" <= path.stem <= "2024-12" and source.REVISION in path.parts
    assert path.stat().st_size == int(ref["bytes"]) and source.digest(path) == ref["sha256"]
    starts = pd.DatetimeIndex(sorted(hours.hour_start_utc.unique()))
    ns = starts.tz_localize(None).to_numpy(dtype="datetime64[ns]").view(np.int64)
    times = pd.DatetimeIndex(
        pd.to_datetime((ns[:, None] + np.arange(60) * 60_000_000_000).ravel(), unit="ns", utc=True)
    )
    columns = [
        "ticker",
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "is_rth",
        "is_genuine",
        "is_imputed",
        "source_revision",
    ]
    minute = pd.read_parquet(
        path, columns=columns, filters=[("timestamp", "in", times.tolist()), ("is_rth", "==", True)]
    )
    assert not minute.duplicated(["ticker", "timestamp"]).any()
    assert (
        minute.is_genuine.all()
        and not minute.is_imputed.any()
        and minute.source_revision.eq(source.REVISION).all()
    )
    raw = minute[["open", "high", "low", "close"]].to_numpy(float)
    assert np.isfinite(raw).all() and (raw > 0).all()
    assert (raw[:, 1] >= np.maximum(raw[:, 0], raw[:, 3])).all()
    assert (np.minimum(raw[:, 0], raw[:, 3]) >= raw[:, 2]).all()
    excluded = source.quarantine(hours)
    bad = np.asarray([(s, t) in excluded for s, t in zip(minute.ticker, minute.timestamp)], bool)
    minute = minute.loc[~bad]
    indices = pd.Series(np.repeat(np.arange(len(starts)), 60), index=times)
    hour = minute.timestamp.map(indices).to_numpy(int)
    stock = minute.ticker.map({s: j for j, s in enumerate(b.SYMBOLS)}).to_numpy(int)
    stamps = minute.timestamp.dt.tz_localize(None).to_numpy(dtype="datetime64[ns]").view(np.int64)
    position = ((stamps - ns[hour]) // 60_000_000_000).astype(int)
    assert ((position >= 0) & (position < 60)).all()
    table = hours.set_index(["hour_start_utc", "ticker"]).reindex(
        pd.MultiIndex.from_product([starts, b.SYMBOLS])
    )
    factor = table.price_factor.to_numpy(float).reshape(-1, 20)
    assert np.isfinite(factor).all() and (factor > 0).all()
    values = minute[["open", "high", "low", "close"]].to_numpy(float, copy=True)
    values *= factor[hour, stock, None]
    prices = np.full((len(starts), 20, 60, 4), np.nan)
    prices[hour, stock, position] = values
    present = np.isfinite(prices[..., 3])
    np.testing.assert_array_equal(present.sum(-1).ravel(), table.genuine_count)
    candidates = {"open": prices[:, :, 0, 0], "close": prices[:, :, -1, 3]}
    for name, col in [("high", 1), ("low", 2)]:
        a = np.full((len(starts), 20), np.nan)
        nonempty = present.any(-1)
        a[nonempty] = (np.nanmax if name == "high" else np.nanmin)(
            prices[..., col][nonempty], axis=-1
        )
        a[table.quarantine_count.to_numpy().reshape(-1, 20) > 0] = np.nan
        candidates[name] = a
    discrepancy = {}
    for name, computed in candidates.items():
        old = table[name].to_numpy(float).reshape(-1, 20)
        np.testing.assert_array_equal(np.isnan(old), np.isnan(computed))
        keep = np.isfinite(old)
        np.testing.assert_allclose(computed[keep], old[keep], rtol=1e-10, atol=1e-10)
        discrepancy[name] = float(np.max(abs(old[keep] - computed[keep]))) if keep.any() else 0.0
    pairs = present[..., 1:] & present[..., :-1]
    return (
        price_channels(prices, present),
        present,
        dict(
            path=str(path),
            sha256=ref["sha256"],
            columns=columns,
            rows_read=len(raw),
            quarantined=int(bad.sum()),
            expected=int(present.size),
            genuine=int(present.sum()),
            adjacent=int(pairs.sum()),
            complete=int(present.all(-1).sum()),
            hours=len(starts),
            reconciliation=discrepancy,
            first=str(minute.timestamp.min()),
            last=str(minute.timestamp.max()),
            peak_rss_bytes=b.memory(),
        ),
    )


def construct() -> None:
    if (OUT / "source_receipt.json").exists() or (OUT / "minute_price_native.npy").exists():
        raise ValueError("NO_SOURCE_RETRY_COMPLETED_OR_PARTIAL_NAMESPACE")
    protocol = b.read(PROTOCOL)
    for path, sha in protocol["preservation_bindings"].items():
        assert source.digest(Path(path)) == sha, path
    grid, rows, roles = source.metadata()
    prior.validate_roles(grid, rows)
    positions = np.unique(np.concatenate(list(roles.values())))
    needed = np.unique(rows.iloc[positions].entry_index.to_numpy(int))
    old = np.load(source.OUT / "minute_summary_primitives_v2.npz")
    assert set(needed).issubset(set(old["required_hours"]))
    del old
    native = np.lib.format.open_memmap(
        OUT / "minute_price_native.npy", mode="w+", dtype=np.float32, shape=(len(needed), 20, 60, 2)
    )
    observed = np.lib.format.open_memmap(
        OUT / "minute_price_observed.npy", mode="w+", dtype=bool, shape=(len(needed), 20, 60)
    )
    mapping = np.full(len(grid), -1, int)
    mapping[needed] = np.arange(len(needed))
    np.save(OUT / "minute_hour_mapping.npy", mapping)
    refs = pd.read_csv(source.SOURCE / "S4_NUMERICAL_SOURCE_READS.csv")
    hourly = refs.loc[refs.purpose.eq("permitted adjusted hourly source")]
    minutes = refs.loc[refs.purpose.eq("permitted genuine minute endpoints; no proxy")]
    fields = [
        "ticker",
        "hour_start_utc",
        "hour_end_utc",
        "is_stub",
        "price_factor",
        "price_basis_id",
        "quarantine_count",
        "anomaly_event_ids",
        "genuine_count",
        "expected_minutes",
        "open",
        "high",
        "low",
        "close",
    ]
    receipts = []
    for month in sorted(set(grid.session_date_et.iloc[needed].str[:7])):
        ix = needed[grid.session_date_et.iloc[needed].str.startswith(month).to_numpy()]
        ref = hourly.loc[hourly.path.str.endswith(month + ".parquet")].iloc[0]
        assert source.digest(Path(ref["path"])) == ref["sha256"]
        h = pd.read_parquet(
            ref["path"],
            columns=fields,
            filters=[("hour_start_utc", "in", grid.hour_start_utc.iloc[ix].tolist())],
        )
        assert not h.is_stub.any() and h.expected_minutes.eq(60).all()
        values, flags, receipt = numeric_price_blocks(
            minutes.loc[minutes.path.str.endswith(month + ".parquet")].iloc[0].to_dict(), h
        )
        native[mapping[ix]], observed[mapping[ix]] = values, flags
        receipts.append(receipt)
        print("PRICE_SOURCE", month, receipt["genuine"], flush=True)
    native.flush()
    observed.flush()
    records = []
    for name, pos in roles.items():
        selected = rows.iloc[pos]
        for year in sorted(selected.session_date_et.str[:4].unique()):
            for slot in b.SLOTS:
                subset = selected.loc[
                    selected.session_date_et.str.startswith(year) & selected.slot.eq(slot)
                ]
                if subset.empty:
                    continue
                flags = observed[mapping[subset.entry_index.to_numpy(int)]]
                for j, ticker in enumerate(b.SYMBOLS):
                    q = flags[:, j]
                    records.append(
                        dict(
                            fold=name[:3],
                            role=name[4:],
                            input_origin_year=year,
                            slot=slot,
                            ticker=ticker,
                            origins=len(q),
                            expected=len(q) * 60,
                            genuine=int(q.sum()),
                            adjacent=int((q[:, 1:] & q[:, :-1]).sum()),
                            complete=int(q.all(-1).sum()),
                            empty=int((~q.any(-1)).sum()),
                        )
                    )
    pd.DataFrame(records).to_csv(OUT / "coverage.csv", index=False)
    source.write(
        OUT / "source_receipt.json",
        dict(
            status="PRICE_SOURCE_CERTIFIED",
            unique_hours=len(needed),
            expected=int(observed.size),
            genuine=int(observed.sum()),
            adjacent=int((observed[..., 1:] & observed[..., :-1]).sum()),
            complete=int(observed.all(-1).sum()),
            empty=int((~observed.any(-1)).sum()),
            reads=receipts,
            no_minute_volume_values_read=True,
            old_hour_proof_reused=True,
            new_uncovered_blocks=0,
            timing="publication byorigin+2min historical proxy,not arrival evidence",
            no_2025_or_2026_market=True,
            resources=resources(),
        ),
    )


def prepare() -> None:
    assert b.read(OUT / "source_receipt.json")["status"] == "PRICE_SOURCE_CERTIFIED"
    grid, rows = b.metadata()
    prior.validate_roles(grid, rows)
    c, returns = b.source_components(grid, rows)
    paths = load_paths()
    clocks, _ = clock.clock_values(rows, sessions("2010-07-01", "2025-01-10"))
    plans = clock.saved_plans(rows)
    checks = []
    for year in b.YEARS:
        dest = OUT / f"F{year % 100}"
        dest.mkdir(exist_ok=False)
        old = b.read(source.O1 / f"F{year % 100}/phases.json")
        phases = {}
        for name, role in [("initial", "inner_train"), ("restricted", "restricted_refit")]:
            phase = old["phases"][name]
            cutoff = phase["cutoff"]
            fit = b.feature_fit_hours(c.grid, rows, cutoff)
            recipe, _ = b.fit_expanded(c, fit, cutoff, approved=True)
            ref = source.O1 / f"F{year % 100}/{name}_recipe.json"
            assert recipe == b.read(ref)
            ix = plans[year][role]
            weights = np.repeat(b.origin_weights(rows.iloc[ix].session_date_et.to_numpy()) / 20, 20)
            scale = max(b.quantile(abs(returns[ix]).ravel(), 0.5, weights), 1e-8)
            assert scale == phase["scale"]
            phases[name] = dict(
                cutoff=cutoff,
                scale=scale,
                recipe_reference=str(ref),
                recipe_sha256=source.digest(ref),
                minute_normalizer="original20 hourly floors only",
            )
            view = PriceView(c, rows, returns, phases[name], paths)
            requested = [role, "selector"] if name == "initial" else [role, "calibration", "oos"]
            for r in requested:
                pos = plans[year][r]
                for start in range(0, len(pos), 128):
                    m = view.minute(pos[start : start + 128])
                    assert m.shape[1:] == (20, 60, 5) and np.isfinite(m).all()
                checks.append(
                    dict(
                        year=year,
                        phase=name,
                        role=r,
                        origins=len(pos),
                        rows=len(pos) * 20,
                        sessions=rows.iloc[pos].session_date_et.nunique(),
                        tensor_finite=True,
                        key_drops=0,
                    )
                )
            if name == "restricted":
                # Read-only reload of existing CLOCK checkpoint: one saved origin per fold.
                oldmodel = clock.model_for_clock().eval()
                oldmodel.load_state_dict(
                    torch.load(
                        clock.OUT / f"s2b_clock/F{year % 100}/restricted_final.pt",
                        weights_only=True,
                    )
                )
                pos = plans[year]["oos"][:1]
                with torch.inference_mode():
                    z = oldmodel(
                        torch.from_numpy(view.x(pos).reshape(-1, 48, 16)),
                        torch.from_numpy(np.repeat(clocks[pos], 20, axis=0)),
                    ).numpy()
                saved = pd.read_parquet(
                    clock.OUT / f"s2b_clock/F{year % 100}/oos_scores.parquet", columns=["Mhat"]
                ).Mhat.to_numpy()[:20]
                np.testing.assert_array_equal(z, saved)
            del view
        source.write(
            dest / "phases.json", dict(year=year, phases=phases, thresholds=old["thresholds"])
        )
    pd.DataFrame(checks).to_csv(OUT / "role_checks.csv", index=False)
    source.write(
        OUT / "preflight_numeric.json",
        dict(
            status="ALL_FOUR_NUMERIC_READY",
            checks=checks,
            resources=resources(),
            old_CLOCK_reload="exact one origin eachfold",
            phases="all8prefix recipes and scales exact",
            no_new_normalizer=True,
        ),
    )


def predict(
    view: PriceView, pos: np.ndarray, model: PriceOnlyMAG, clocks: np.ndarray
) -> np.ndarray:
    model.eval()
    parts = []
    with torch.inference_mode():
        for start in range(0, len(pos), 32):
            ix = pos[start : start + 32]
            x = torch.from_numpy(view.x(ix).reshape(-1, 48, 16))
            known = torch.from_numpy(np.repeat(clocks[ix], 20, axis=0))
            minute = torch.from_numpy(view.minute(ix).reshape(-1, 60, 5))
            parts.append(model(x, known, minute).numpy().reshape(-1, 20))
    result = np.concatenate(parts)
    if not np.isfinite(result).all():
        raise ValueError("NONFINITE_FORECAST")
    return result


def train_epoch(
    view: PriceView,
    pos: np.ndarray,
    model: PriceOnlyMAG,
    opt: torch.optim.AdamW,
    epoch: int,
    clocks: np.ndarray,
) -> dict:
    groups = view.rows.iloc[pos].groupby("session_date_et").indices
    days = sorted(groups, key=str)
    np.random.default_rng(42 + epoch).shuffle(days)
    model.train()
    norms = []
    for start in range(0, len(days), 16):
        ix = pos[np.concatenate([groups[d] for d in days[start : start + 16]])]
        opt.zero_grad()
        z = model(
            torch.from_numpy(view.x(ix).reshape(-1, 48, 16)),
            torch.from_numpy(np.repeat(clocks[ix], 20, axis=0)),
            torch.from_numpy(view.minute(ix).reshape(-1, 60, 5)),
        ).reshape(-1, 20)
        loss = previous.weighted_loss(
            z,
            torch.from_numpy(view.r[ix].astype(np.float32)),
            view.scale,
            b.origin_weights(view.rows.iloc[ix].session_date_et.to_numpy()),
        )
        if not bool(torch.isfinite(loss)):
            raise ValueError("NONFINITE_LOSS")
        loss.backward()
        norms.append(
            float(torch.nn.utils.clip_grad_norm_(model.parameters(), 1, error_if_nonfinite=True))
        )
        b.memory()
        opt.step()
    return dict(
        steps=len(norms), gradient_norm_max=max(norms), clipped_batches=sum(x > 1 for x in norms)
    )


def journal(year: int, status: str, detail: dict) -> None:
    protocol = b.read(PROTOCOL)
    path = OUT / "neural_starts.jsonl"
    history = [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []
    starts = [v for v in history if v["status"] == "STARTED"]
    pointer = b.read(b.POINTER)
    assert (
        pointer == protocol["previous_pointer"]
        if not history
        else pointer["real_journal"] == str(path)
    )
    if status == "STARTED":
        assert b.read(OUT / "readiness.json")["status"] == "READY_ALL_FOUR"
        assert len(starts) < 4 and year == b.YEARS[len(starts)]
        assert not history or history[-1]["status"] == "COMPLETED"
        resources()
    row = dict(
        sequence=len(history) + 1,
        at=pd.Timestamp.now(tz="UTC").isoformat(),
        experiment="S3C-PRICEONLY",
        year=year,
        status=status,
        global_started_pairs=170 + len(starts) + int(status == "STARTED"),
        effective_ceiling=300,
        detail=detail,
        previous_journal=dict(
            path=protocol["previous_pointer"]["real_journal"],
            sha256=protocol["preservation_bindings"][protocol["previous_pointer"]["real_journal"]],
        ),
        plan=dict(path=str(PROTOCOL), sha256=b.digest(PROTOCOL)),
    )
    with path.open("a") as stream:
        stream.write(json.dumps(row) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    b.write(
        b.POINTER,
        dict(
            pointer,
            schema_version=33,
            definition=row["plan"],
            plan=row["plan"],
            real_journal=str(path),
            previous_journal=row["previous_journal"],
            fit_permission=False,
        ),
    )


def run_fold(
    year: int,
    c: b.Components,
    rows: pd.DataFrame,
    returns: np.ndarray,
    paths: tuple,
    phases: dict,
    clocks: np.ndarray,
) -> None:
    dest = DEST / f"F{year % 100}"
    plans = clock.saved_plans(rows)[year]
    trace = []
    tick = time.monotonic()
    model = model_for_price()
    initial_hash = b.initial_hash(model)
    opt = b.optimizer(model)
    assert not opt.state
    inner = PriceView(c, rows, returns, phases["phases"]["initial"], paths)
    selector = b.Selector()
    best = {}
    journal(year, "STARTED", dict(run_id=f"HF20-S3CPRICE-F{year % 100}-S42", parameters=6931))
    try:
        while selector.status == "CALIBRATING":
            n = selector.epoch + 1
            started = time.monotonic()
            stats = train_epoch(inner, plans["inner_train"], model, opt, n, clocks)
            z = predict(inner, plans["selector"], model, clocks)
            target = torch.log1p(
                torch.from_numpy(returns[plans["selector"]].astype(np.float32)).abs() / inner.scale
            ).numpy()
            val = float(
                b.origin_weights(rows.iloc[plans["selector"]].session_date_et.to_numpy())
                @ ((z - target) ** 2).mean(1)
            )
            if selector.observe(val):
                best = {k: v.detach().clone() for k, v in model.state_dict().items()}
            trace.append(
                dict(
                    phase="selector",
                    epoch=n,
                    validation_M_MSE=val,
                    selected=selector.selected,
                    seconds=time.monotonic() - started,
                    **stats,
                )
            )
            pd.DataFrame(trace).to_csv(dest / "training.csv", index=False)
            print("S3CPRICE", year, "selector", n, val, "best", selector.selected, flush=True)
        model.load_state_dict(best)
        torch.save(model.state_dict(), dest / "selected_initial.pt")
        source.write(
            dest / "selection.json",
            dict(vars(selector), selected_initial_hash=b.initial_hash(model)),
        )
        journal(year, "SELECTED", dict(epoch=selector.selected))
        del inner, model, opt, best
        gc.collect()
        refit = PriceView(c, rows, returns, phases["phases"]["restricted"], paths)
        model = model_for_price()
        assert b.initial_hash(model) == initial_hash
        opt = b.optimizer(model)
        assert not opt.state
        journal(year, "REFITTING", dict(epochs=selector.selected))
        for n in range(1, selector.selected + 1):
            started = time.monotonic()
            stats = train_epoch(refit, plans["restricted_refit"], model, opt, n, clocks)
            trace.append(dict(phase="refit", epoch=n, seconds=time.monotonic() - started, **stats))
            pd.DataFrame(trace).to_csv(dest / "training.csv", index=False)
            print("S3CPRICE", year, "refit", n, "of", selector.selected, flush=True)
        frozen = b.initial_hash(model)
        torch.save(model.state_dict(), dest / "restricted_final.pt")
        zcal = predict(refit, plans["calibration"], model, clocks)
        cal = pd.read_parquet(c3.root(year) / "calibration_scores.parquet", columns=[*c3.META, "A"])
        np.testing.assert_array_equal(cal.A, abs(returns[plans["calibration"]]).ravel())
        cal["Mhat"] = zcal.ravel()
        coeffs = c3.fit_categories(cal, refit.scale)
        pd.DataFrame(coeffs).to_csv(dest / "calibration_coefficients.csv", index=False, mode="x")
        cal.to_parquet(dest / "calibration_scores.parquet", compression="zstd", index=False)
        factors = {v["group"]: v["c_star"] for v in coeffs}
        z = predict(refit, plans["oos"], model, clocks)
        reload = model_for_price()
        reload.load_state_dict(torch.load(dest / "restricted_final.pt", weights_only=True))
        np.testing.assert_array_equal(z, predict(refit, plans["oos"], reload, clocks))
        assert frozen == b.initial_hash(model)
        frame = pd.read_parquet(c3.root(year) / "oos_scores.parquet", columns=[*c3.META, "A"])
        np.testing.assert_array_equal(frame.A, abs(returns[plans["oos"]]).ravel())
        frame["Mhat"] = z.ravel()
        frame[RAW] = previous.raw_decode(z, refit.scale).ravel()
        frame[CAL] = c3.decode(z.ravel(), refit.scale, frame.category.map(factors).to_numpy())
        frame.to_parquet(dest / "oos_scores.parquet", compression="zstd", index=False)
        result = dict(
            year=year,
            status="COMPLETED",
            parameters=6931,
            selected_epoch=selector.selected,
            selector_epochs=selector.epoch,
            raw_minimum_epoch=selector.raw_epoch,
            initial_hash=initial_hash,
            frozen_parameter_hash=frozen,
            reload_max_error=0,
            initial_scale=phases["phases"]["initial"]["scale"],
            scale=refit.scale,
            optimizer_fresh=True,
            seconds=time.monotonic() - tick,
            resources=resources(),
        )
        source.write(dest / "result.json", result)
        journal(year, "COMPLETED", result)
        del refit, model, opt, reload
        gc.collect()
    except BaseException as exc:
        journal(year, "FAILED", dict(error=repr(exc), retry=False))
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", action="store_true")
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    if args.source:
        construct()
    elif args.prepare:
        prepare()
    elif args.run:
        if (OUT / "neural_starts.jsonl").exists():
            raise ValueError("NO_RETRY_STARTED_NAMESPACE")
        readiness = b.read(OUT / "readiness.json")
        assert readiness["status"] == "READY_ALL_FOUR"
        for path, sha in readiness["prefit_hashes"].items():
            assert source.digest(Path(path)) == sha, path
        grid, rows = b.metadata()
        prior.validate_roles(grid, rows)
        c, returns = b.source_components(grid, rows)
        paths = load_paths()
        clocks, _ = clock.clock_values(rows, sessions("2010-07-01", "2025-01-10"))
        for year in b.YEARS:
            run_fold(
                year, c, rows, returns, paths, b.read(OUT / f"F{year % 100}/phases.json"), clocks
            )


if __name__ == "__main__":
    main()
