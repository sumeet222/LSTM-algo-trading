"""SIP-only historical GET client: bounded retries, pagination and redacted logs."""

from __future__ import annotations

import os
import random
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import cast

import pandas as pd
import requests

from .config import now
from .validation import normalize, require_valid

ENDPOINT = "https://data.alpaca.markets/v2/stocks/bars"


class DataAccessError(RuntimeError):
    """Safe error with no headers, response body, credentials or request tokens."""


def credentials() -> tuple[str, str]:
    """Read standard names; retain the repository's legacy aliases without logging."""
    key = os.getenv("APCA_API_KEY_ID") or os.getenv("ALPACA_API_KEY")
    secret = os.getenv("APCA_API_SECRET_KEY") or os.getenv("ALPACA_API_SECRET")
    if not key or not secret:
        raise DataAccessError(
            "Missing APCA_API_KEY_ID / APCA_API_SECRET_KEY (or legacy aliases). "
            "Set locally; never paste credentials in chat."
        )
    return key, secret


def request_params(cfg: dict, symbols: list[str], start: str, end: str) -> dict:
    """Always specify material provider choices, including entity-mapping date."""
    if cfg["feed"] != "sip":
        raise ValueError("IEX fallback is forbidden")
    if "adjustment" not in cfg or not cfg["adjustment"]:
        raise ValueError("Adjustment must be explicit")
    return {
        "symbols": ",".join(symbols),
        "start": start,
        "end": end,
        "feed": "sip",
        "timeframe": cfg["timeframe"],
        "adjustment": cfg["adjustment"],
        "asof": cfg["asof"],
        "currency": cfg["currency"],
        "sort": "asc",
        "limit": cfg["page_limit"],
    }


@dataclass
class HistoricalClient:
    """Read-only fixed-host client. Inject transport/sleep for fully offline tests."""

    cfg: dict
    key: str = field(repr=False)
    secret: str = field(repr=False)
    get: Callable = requests.get
    sleep: Callable = time.sleep
    monotonic: Callable = time.monotonic
    jitter: Callable = random.random
    events: list[dict] = field(default_factory=list)
    _last_request: float | None = None

    def _request(self, params: dict) -> dict:
        policy = self.cfg["retry"]
        safe = {k: v for k, v in params.items() if k != "page_token"}
        for attempt in range(1, policy["max_attempts"] + 1):
            if self._last_request is not None:
                self.sleep(
                    max(
                        0,
                        60 / policy["requests_per_minute"]
                        - (self.monotonic() - self._last_request),
                    )
                )
            self._last_request = self.monotonic()
            response = None
            try:
                response = self.get(
                    ENDPOINT,
                    params=params,
                    headers={"APCA-API-KEY-ID": self.key, "APCA-API-SECRET-KEY": self.secret},
                    timeout=policy["timeout_seconds"],
                    allow_redirects=False,
                )
                status = response.status_code
            except requests.RequestException:
                status = "transport_error"
            self.events.append(
                {
                    "time": now(),
                    "endpoint": ENDPOINT,
                    "params": safe,
                    "attempt": attempt,
                    "status": status,
                    "continued_page": "page_token" in params,
                }
            )
            if status == 200:
                try:
                    # status=200 requires a returned response; transport failure sets a string.
                    payload = cast(requests.Response, response).json()
                except ValueError:
                    raise DataAccessError("Invalid JSON response; acquisition stopped") from None
                if not isinstance(payload, dict) or not isinstance(payload.get("bars"), dict):
                    raise DataAccessError("Unexpected bars response schema")
                return payload
            if status in {401, 403, 422}:
                raise DataAccessError(
                    f"Alpaca HTTP {status}: check credentials/SIP entitlement and "
                    "historical end time. No feed fallback; bulk blocked."
                )
            if (
                status != "transport_error"
                and status != 429
                and not (isinstance(status, int) and 500 <= status <= 599)
            ):
                raise DataAccessError(f"Alpaca HTTP {status}: request failed; no feed fallback")
            if attempt == policy["max_attempts"]:
                raise DataAccessError(f"Alpaca {status}: exhausted {attempt} bounded attempts")
            delay = min(
                policy["max_seconds"],
                policy["base_seconds"] * 2 ** (attempt - 1)
                + self.jitter() * policy["jitter_seconds"],
            )
            if response is not None:
                retry_after = response.headers.get("Retry-After")
                if retry_after:
                    try:
                        requested_delay = max(0, float(retry_after))
                    except ValueError:
                        requested_delay = delay
                    if requested_delay > policy["max_seconds"]:
                        raise DataAccessError(
                            "Retry-After exceeds bounded wait policy; resume later"
                        )
                    delay = max(delay, requested_delay)
            self.events[-1]["retry_seconds"] = delay
            self.sleep(delay)
        raise AssertionError("Unreachable retry state")

    def bars(self, params: dict) -> pd.DataFrame:
        """Consume every page across all symbols, rejecting duplicate or invalid keys."""
        if params.get("feed") != "sip" or not params.get("adjustment"):
            raise ValueError("Explicit SIP feed and adjustment required; no IEX fallback")
        rows = []
        token = None
        seen = set()
        for _ in range(self.cfg["max_pages_per_request"]):
            page_params = dict(params)
            if token:
                page_params["page_token"] = token
            payload = self._request(page_params)
            for symbol, bars in payload["bars"].items():
                if symbol not in params["symbols"].split(",") or not isinstance(bars, list):
                    raise DataAccessError("Unrequested symbol or invalid bars list")
                for bar in bars:
                    try:
                        rows.append(
                            {
                                "symbol": symbol,
                                "timestamp": bar["t"],
                                "open": bar["o"],
                                "high": bar["h"],
                                "low": bar["l"],
                                "close": bar["c"],
                                "volume": bar["v"],
                                "trade_count": bar.get("n"),
                                "vwap": bar.get("vw"),
                            }
                        )
                    except (KeyError, TypeError):
                        raise DataAccessError("Missing provider OHLCV fields") from None
            token = payload.get("next_page_token")
            if not token:
                break
            if not isinstance(token, str) or token in seen:
                raise DataAccessError("Repeated or invalid pagination token")
            seen.add(token)
        else:
            raise DataAccessError(
                "Pagination exceeded bounded page budget; no partial dataset saved"
            )
        columns = [
            "symbol",
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "trade_count",
            "vwap",
        ]
        frame = normalize(pd.DataFrame(rows, columns=columns), stocks=True)
        # Optional fields may be absent; only required fields determine fatal null defects.
        require_valid(frame.drop(columns=["trade_count", "vwap"]), stocks=True)
        lower, upper = pd.Timestamp(params["start"]), pd.Timestamp(params["end"])
        if ((frame.timestamp < lower) | (frame.timestamp > upper)).any():
            raise DataAccessError("Provider returned timestamps outside inclusive request bounds")
        for key, column in (
            ("feed", "feed"),
            ("adjustment", "adjustment"),
            ("timeframe", "source_timeframe"),
        ):
            frame[column] = params[key]
        frame["trade_count"] = pd.to_numeric(frame.trade_count, errors="raise").astype("Int64")
        frame["vwap"] = pd.to_numeric(frame.vwap, errors="raise").astype("float64")
        if (frame.trade_count.dropna() < 0).any() or (frame.vwap.dropna() <= 0).any():
            raise DataAccessError("Invalid provider trade_count/VWAP")
        return frame.sort_values(["symbol", "timestamp"]).reset_index(drop=True)
