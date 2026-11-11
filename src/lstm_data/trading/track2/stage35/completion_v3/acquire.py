"""Bounded free action-only HTTP, redacted receipts, immutable payload cache.

Credentials are loaded from the existing environment/.env and never printed.
Schema documentation alone is not an entitlement or completeness assertion.
"""

import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path("trading/track2/stage35/completion_v3")
USER_AGENT = "HF20-Academic-Action-Audit/3.0"


def write_once(path: Path, value: object) -> None:
    text = json.dumps(value, indent=2, sort_keys=True, default=str) + "\n"
    if path.exists():
        if path.read_text() != text:
            raise ValueError("IMMUTABLE_RECEIPT:" + str(path))
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(text)
    temp.replace(path)


def classify(status: int, data: object) -> str:
    # Only provider error envelopes, not arbitrary HTML/marketing/legal text.
    error = {}
    if isinstance(data, dict):
        error = {
            k: v
            for k, v in data.items()
            if k.lower()
            in ("error", "error message", "information", "note", "message", "error_message")
        }
    text = json.dumps(error).lower()
    if status == 429:
        return "RATE_LIMITED"
    if status in (401, 403):
        return "ACCESS_DENIED"
    if status >= 400 or status == 0:
        return "SOURCE_UNAVAILABLE"
    if any(w in text for w in ("premium", "subscription required", "upgrade your plan")):
        return "NOT_AVAILABLE_FREE"
    if any(w in text for w in ("api key", "apikey", "token is invalid")):
        return "ACCESS_DENIED"
    return "RESPONSE_RECEIVED_NOT_COMPLETENESS_PROOF"


class Acquisition:
    def __init__(self, root: Path = ROOT):
        self.root = root
        self.prefix = ""
        self.calls = sum(
            len(json.loads(p.read_text()).get("attempts", []))
            for p in (root / "audits").glob("*.receipt.json")
        )
        load_dotenv(Path(".env"), override=False)
        self.secrets = tuple(
            v
            for k in (
                "APCA_API_KEY_ID",
                "APCA_API_SECRET_KEY",
                "ALPACA_API_KEY",
                "ALPACA_API_SECRET",
                "FINNHUB_API_KEY",
                "FINNHUB_TOKEN",
                "ALPHAVANTAGE_API_KEY",
                "ALPHA_VANTAGE_API_KEY",
            )
            if (v := os.getenv(k))
        )

    def fetch(
        self,
        key: str,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
        retry429: bool = False,
    ) -> dict:
        key = self.prefix + key
        receipt_path = self.root / "audits" / f"{key}.receipt.json"
        if receipt_path.exists():
            return json.loads(receipt_path.read_text())
        if self.calls >= 100:
            raise ValueError("NETWORK_BUDGET")
        params = params or {}
        safe = {
            k: ("<REDACTED>" if k.lower() in ("token", "apikey", "api_key") else v)
            for k, v in params.items()
        }
        start = datetime.now(timezone.utc).isoformat()
        attempts = []
        body = b""
        data: object = {}
        status = 0
        for attempt in range(2 if retry429 else 1):
            self.calls += 1
            try:
                response = requests.get(
                    url,
                    params=params,
                    headers={"User-Agent": USER_AGENT, **(headers or {})},
                    timeout=20,
                )
                status = response.status_code
                body = response.content
                try:
                    data = response.json()
                except ValueError:
                    data = {"non_json_body": response.text}
            except requests.RequestException as exc:
                status = 0
                data = {"error_type": type(exc).__name__}
                body = json.dumps(data).encode()
            attempts.append({"http": status, "attempt": attempt + 1})
            if status != 429 or not retry429 or attempt:
                break
            time.sleep(2)
        digest = hashlib.sha256(body).hexdigest()
        # Never save authentication material even if a provider echoes it.
        sanitized = json.dumps(data, ensure_ascii=False)
        for secret in self.secrets:
            sanitized = sanitized.replace(secret, "<REDACTED>")
        payload = json.loads(sanitized)
        payload_path = self.root / "audits/payloads" / f"{key}.json"
        write_once(payload_path, payload)
        receipt = {
            "source_id": key,
            "endpoint": url,
            "query": safe,
            "retrieval_utc": start,
            "attempts": attempts,
            "http_status": status,
            "status": classify(status, payload),
            "original_payload_sha256": digest,
            "payload_path": str(payload_path),
            "stored_payload_sha256": hashlib.sha256(payload_path.read_bytes()).hexdigest(),
            "rights": "provider public/research access only;no redistribution or PIT certification",
            "point_in_time": False,
        }
        write_once(receipt_path, receipt)
        print(key, receipt["status"], status, flush=True)
        return receipt

    def provider_probe(self) -> None:
        plan = json.loads((self.root / "ACTION_SOURCE_PLAN_V3.json").read_text())
        key = os.getenv("APCA_API_KEY_ID") or os.getenv("ALPACA_API_KEY")
        secret = os.getenv("APCA_API_SECRET_KEY") or os.getenv("ALPACA_API_SECRET")
        # One market-data request also establishes missing-auth response if no keys.
        headers = {"APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": secret} if key and secret else {}
        params = {
            "symbols": ",".join(plan["symbols"]),
            "start": "2020-12-01",
            "end": "2024-12-31",
            "data_quality": "all",
            "limit": 1000,
            "sort": "asc",
        }
        tokens = set()
        for page in range(6):
            receipt = self.fetch(
                f"alpaca_{page}",
                "https://data.alpaca.markets/v1/corporate-actions",
                params,
                headers,
            )
            if receipt["http_status"] != 200:
                break
            data = json.loads(Path(receipt["payload_path"]).read_text())
            token = data.get("next_page_token")
            if not token:
                break
            if token in tokens:
                raise ValueError("REPEATED_PROVIDER_PAGE_TOKEN")
            tokens.add(token)
            params = {**params, "page_token": token}
        token = os.getenv("FINNHUB_API_KEY") or os.getenv("FINNHUB_TOKEN")
        fp = {"symbol": "AAPL", "from": "2021-01-01", "to": "2024-12-31"}
        self.fetch(
            "finnhub_probe",
            "https://finnhub.io/api/v1/stock/dividend",
            fp,
            {"X-Finnhub-Token": token} if token else {},
        )
        av = os.getenv("ALPHAVANTAGE_API_KEY") or os.getenv("ALPHA_VANTAGE_API_KEY")
        if av:
            self.fetch(
                "av_probe",
                "https://www.alphavantage.co/query",
                {"function": "DIVIDENDS", "symbol": "AAPL", "apikey": av},
            )
        else:
            write_once(
                self.root / "audits/av_probe.receipt.json",
                {
                    "source_id": "alpha_vantage",
                    "status": "ACCESS_NOT_CONFIGURED",
                    "endpoint": "https://www.alphavantage.co/query",
                    "function": "DIVIDENDS",
                    "key_present": False,
                    "no_account_created": True,
                    "docs": "https://www.alphavantage.co/documentation/",
                },
            )
        self.fetch(
            "nasdaq_probe",
            "https://api.nasdaq.com/api/quote/AAPL/dividends",
            {
                "assetclass": "stocks",
                "fromdate": "2021-01-01",
                "todate": "2024-12-31",
                "limit": 5000,
            },
        )
        self.fetch(
            "yahoo_probe",
            "https://query1.finance.yahoo.com/v7/finance/download/AAPL",
            {"period1": 1606780800, "period2": 1735689600, "interval": "1d", "events": "div"},
            retry429=True,
        )


if __name__ == "__main__":
    Acquisition().provider_probe()
