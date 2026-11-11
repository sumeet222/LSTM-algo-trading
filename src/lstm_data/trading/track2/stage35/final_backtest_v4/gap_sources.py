"""Presealed, gap-only economic raw observations; never a model-input repair."""

import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import requests
from dotenv import load_dotenv

from ...stage012.model_registry import SYMBOLS
from .market import Market, minute, stamp
from .paths import ROOT, digest, publish


def scan() -> None:
    entries = []
    market = Market(use_gap_supplement=False)
    for day in market.days(include_signals=False):
        keys = [(SYMBOLS[int(j)], int(day.starts[int(i)])) for i, j in np.argwhere(~day.valid)]
        if keys:
            path = ROOT / "sources/gap_keys" / (day.date + ".json")
            publish(
                path, {"date": day.date, "keys": keys, "canonical_source_sha256": day.source_hash}
            )
            entries.append(
                {"date": day.date, "path": str(path), "sha256": digest(path), "count": len(keys)}
            )
        if len(entries) % 100 == 0:
            print("gap_scan_dates", len(entries), flush=True)
    count = sum(e["count"] for e in entries)
    if count != 99048:
        raise ValueError("ORIGINAL_GAP_MASK_CHANGED")
    publish(
        ROOT / "PRICE_GAP_SCAN_V4.json",
        {
            "plan_sha256": digest(ROOT / "ECONOMIC_GAP_SOURCE_PLAN_V4.json"),
            "entries": entries,
            "selected_cells": count,
            "source_partitions": market.reads,
            "financial_activity": False,
            "all20_allfolds": True,
        },
    )


def valid(row: dict) -> bool:
    values = np.asarray([row.get(k, np.nan) for k in ("o", "h", "l", "c", "v")], float)
    o, h, low, c, v = values
    return bool(
        np.isfinite(values).all()
        and min(o, h, low, c) > 0
        and v >= 0
        and low <= min(o, c)
        and h >= max(o, c)
    )


def fetch() -> None:
    load_dotenv(".env", override=False)
    key = os.getenv("APCA_API_KEY_ID") or os.getenv("ALPACA_API_KEY")
    secret = os.getenv("APCA_API_SECRET_KEY") or os.getenv("ALPACA_API_SECRET")
    if not key or not secret:
        raise PermissionError("EXISTING_MARKET_DATA_AUTH_UNAVAILABLE")
    plan = json.loads((ROOT / "ECONOMIC_GAP_SOURCE_PLAN_V4.json").read_text())
    index_path = ROOT / "PRICE_GAP_SCAN_V4.json"
    if index_path.exists():
        index = json.loads(index_path.read_text())
    else:
        index = {
            "plan_sha256": digest(ROOT / "ECONOMIC_GAP_SOURCE_PLAN_V4.json"),
            "selected_cells": plan["expected_original_gap_cells"],
            "entries": [
                {"date": p.stem, "path": str(p), "sha256": digest(p)}
                for p in sorted((ROOT / "sources/gap_keys").glob("*.json"))
            ],
        }
    if index["plan_sha256"] != digest(ROOT / "ECONOMIC_GAP_SOURCE_PLAN_V4.json"):
        raise ValueError("SOURCE_PLAN_DRIFT")
    session = requests.Session()
    session.headers.update({"APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": secret})
    entries = []
    requests_used = sum(
        len(json.loads(p.read_text())["pages"])
        for p in (ROOT / "sources/gap_raw").glob("*.receipt.json")
    )
    requests_before = requests_used
    for item in index["entries"]:
        source = Path(item["path"])
        if digest(source) != item["sha256"]:
            raise ValueError("GAP_KEY_DRIFT")
        selected = json.loads(source.read_text())
        keys = {(symbol, int(t)) for symbol, t in selected["keys"]}
        if not "2021-01-01" <= item["date"] <= "2024-12-31" or any(
            symbol not in SYMBOLS or stamp(t)[:10] != item["date"] for symbol, t in keys
        ):
            raise ValueError("SOURCE_ACCESS_SCOPE")
        path = ROOT / "sources/gap_raw" / (item["date"] + ".json")
        receipt = path.with_suffix(".receipt.json")
        if receipt.exists():
            saved = json.loads(receipt.read_text())
            if saved["projected_sha256"] != digest(path):
                raise ValueError("GAP_SOURCE_DRIFT")
            entries.append(saved)
            continue
        query = {
            "symbols": ",".join(s for s in SYMBOLS if any(k[0] == s for k in keys)),
            "start": stamp(min(t for _, t in keys)),
            "end": stamp(max(t for _, t in keys) + 1),
            "timeframe": "1Min",
            "adjustment": "raw",
            "feed": "sip",
            "limit": 10000,
            "sort": "asc",
        }
        payloads = []
        retained = {}
        status = "COMPLETE_RESPONSE"
        http = 0
        token = None
        for page in range(2):
            if requests_used >= plan["maximum_requests"]:
                status = "REQUEST_BUDGET_HOLD"
                break
            params = {**query, **({"page_token": token} if token else {})}
            at = datetime.now(timezone.utc).isoformat()
            requests_used += 1
            try:
                response = session.get(plan["endpoint"], params=params, timeout=20)
                http = response.status_code
                payloads.append(
                    {
                        "page": page,
                        "retrieved_utc": at,
                        "http": http,
                        "raw_response_sha256": hashlib.sha256(response.content).hexdigest(),
                    }
                )
                if http != 200:
                    status = "RATE_LIMITED" if http == 429 else "HTTP_ACCESS_HOLD"
                    break
                body = response.json()
                if not isinstance(body.get("bars"), dict):
                    status = "FIELD_MISSING"
                    break
                for symbol, rows in body["bars"].items():
                    for row in rows:
                        lookup = (symbol, minute(row["t"]))
                        if lookup not in keys:
                            continue
                        if lookup in retained and retained[lookup] != row:
                            raise ValueError("CONFLICTING_PROVIDER_BAR")
                        if valid(row):
                            retained[lookup] = row
                next_token = body.get("next_page_token")
                if not next_token:
                    break
                if next_token == token:
                    raise ValueError("REPEATED_PROVIDER_PAGE")
                token = next_token
                if page == 1:
                    status = "PAGINATION_HOLD"
            except requests.RequestException as exc:
                status = "NETWORK_" + type(exc).__name__
                break
            time.sleep(plan["minimum_seconds_between_requests"])
        rows = [{"symbol": symbol, **row} for (symbol, t), row in sorted(retained.items())]
        publish(
            path,
            {
                "basis": "RAW_SHARE",
                "selection_key_sha256": item["sha256"],
                "bars": rows,
                "unresolved_keys": sorted(keys - set(retained)),
                "source_status": status,
            },
        )
        saved = {
            "date": item["date"],
            "path": str(path),
            "projected_sha256": digest(path),
            "query": query,
            "pages": payloads,
            "selected": len(keys),
            "retained": len(rows),
            "unresolved": len(keys) - len(rows),
            "status": status,
            "scope": (
                "projected source rows; original full response not retained; retrospective not PIT"
            ),
        }
        publish(receipt, saved)
        entries.append(saved)
        if len(entries) % 25 == 0:
            print(
                "gap_fetch_dates",
                len(entries),
                "bars",
                sum(r["retained"] for r in entries),
                flush=True,
            )
        if status == "RATE_LIMITED":
            break
        time.sleep(plan["minimum_seconds_between_requests"])
    finished = json.loads(index_path.read_text()) if index_path.exists() else None
    complete = (
        finished is not None
        and [row["date"] for row in entries] == [row["date"] for row in finished["entries"]]
        and sum(row["selected"] for row in entries) == finished["selected_cells"]
    )
    publish(
        (
            ROOT / "ECONOMIC_GAP_SUPPLEMENT_MANIFEST_V4.json"
            if complete
            else ROOT
            / "audits"
            / (
                "GAP_SUPPLEMENT_PARTIAL_"
                + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
                + ".json"
            )
        ),
        {
            "plan_sha256": digest(ROOT / "ECONOMIC_GAP_SOURCE_PLAN_V4.json"),
            "gap_index_sha256": digest(index_path) if index_path.exists() else None,
            "entries": entries,
            "all_dates_attempted": complete,
            "selected": index["selected_cells"],
            "retained": sum(r["retained"] for r in entries),
            "unresolved": sum(r["unresolved"] for r in entries),
            "requests_this_run": requests_used - requests_before,
            "requests_total": requests_used,
            "no_original_mutation": True,
            "no_financial_activity": True,
        },
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", choices=("scan", "fetch"))
    args = parser.parse_args()
    scan() if args.task == "scan" else fetch()
