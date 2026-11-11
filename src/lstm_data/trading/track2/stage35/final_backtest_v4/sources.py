"""Predeclared binary-preserving primary sources and bounded raw OGN observations."""

import json
import os
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

from .paths import ROOT, digest, publish


def acquire() -> None:
    load_dotenv(".env", override=False)
    headers = {"User-Agent": "HF20-Academic-Research/4.0"}
    plan = json.loads((ROOT / "SOURCE_ACCESS_PLAN_V4.json").read_text())
    requests_plan = [("merck_8937", plan["urls"][0], {}), ("ogn_sec_8k", plan["urls"][1], {})]
    key = os.getenv("APCA_API_KEY_ID") or os.getenv("ALPACA_API_KEY")
    secret = os.getenv("APCA_API_SECRET_KEY") or os.getenv("ALPACA_API_SECRET")
    for name, url, params in requests_plan:
        path = ROOT / "sources" / (name + (".pdf" if name == "merck_8937" else ".html"))
        receipt = ROOT / "sources" / (name + ".receipt.json")
        if receipt.exists():
            continue
        at = datetime.now(timezone.utc).isoformat()
        try:
            response = requests.get(url, headers=headers, timeout=20, params=params)
            status = response.status_code
            payload = response.content
        except requests.RequestException as exc:
            status = 0
            payload = type(exc).__name__.encode()
        path.write_bytes(payload)
        publish(
            receipt,
            {
                "url": url,
                "query": params,
                "retrieved_utc": at,
                "http": status,
                "sha256": digest(path),
                "path": str(path),
                "rights": "public issuer/SEC research;not PIT receipt proof",
            },
        )
        print(name, status, flush=True)
    if not key or not secret:
        publish(ROOT / "sources/ogn_unavailable.json", {"status": "EXISTING_AUTH_NOT_CONFIGURED"})
        return
    for feed in ("sip", "iex"):
        params = {
            "start": "2021-06-03T13:30:00Z",
            "end": "2021-06-04T20:01:00Z",
            "timeframe": "1Min",
            "adjustment": "raw",
            "feed": feed,
            "limit": 10000,
            "sort": "asc",
        }
        path = ROOT / f"sources/ogn_{feed}.json"
        receipt = ROOT / f"sources/ogn_{feed}.receipt.json"
        if receipt.exists():
            record = json.loads(path.read_text())
            if record.get("bars"):
                break
            continue
        at = datetime.now(timezone.utc).isoformat()
        try:
            response = requests.get(
                "https://data.alpaca.markets/v2/stocks/OGN/bars",
                params=params,
                headers={**headers, "APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": secret},
                timeout=20,
            )
            status = response.status_code
            try:
                payload = response.json()
            except ValueError:
                payload = {"http": status, "non_json_body": response.text[:500]}
        except requests.RequestException as exc:
            status = 0
            payload = {"error_type": type(exc).__name__}
        sanitized = json.dumps(payload).replace(key, "<REDACTED>").replace(secret, "<REDACTED>")
        publish(path, json.loads(sanitized))
        publish(
            receipt,
            {
                "endpoint": "https://data.alpaca.markets/v2/stocks/OGN/bars",
                "query": params,
                "http": status,
                "retrieved_utc": at,
                "sha256": digest(path),
                "path": str(path),
                "basis": "RAW",
                "feed": feed,
                "stock_loan_or_NBBO": False,
            },
        )
        print("OGN", feed, status, "bars", len(payload.get("bars") or []), flush=True)
        if payload.get("bars"):
            if payload.get("next_page_token"):
                raise ValueError("BOUNDED_OGN_PAGE_INCOMPLETE")
            break


if __name__ == "__main__":
    acquire()
