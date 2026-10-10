import json

import pytest

from lstm_data.alpaca import DataAccessError, HistoricalClient, request_params


class Response:
    def __init__(self, status=200, payload=None, headers=None):
        self.status_code = status
        self.payload = payload
        self.headers = headers or {}

    def json(self):
        return self.payload


def params(cfg):
    return request_params(cfg, ["AAPL", "JPM"], "2020-07-01T00:00:00Z", "2020-07-02T00:00:00Z")


def client_for(cfg, responses):
    iterator = iter(responses)
    calls, sleeps = [], []

    def get(url, **kwargs):
        calls.append((url, kwargs))
        return next(iterator)

    client = HistoricalClient(
        cfg,
        "fixture-key",
        "fixture-secret",
        get=get,
        sleep=sleeps.append,
        monotonic=lambda: 0.0,
        jitter=lambda: 0.0,
    )
    return client, calls, sleeps


def test_pagination_across_symbols_and_explicit_policies(cfg, bars_fixture):
    client, calls, _ = client_for(
        cfg,
        [
            Response(payload={"bars": {"AAPL": [bars_fixture]}, "next_page_token": "opaque"}),
            Response(payload={"bars": {"JPM": [bars_fixture]}, "next_page_token": None}),
        ],
    )
    data = client.bars(params(cfg))
    assert set(data.symbol) == {"AAPL", "JPM"}
    assert all(call[1]["params"]["feed"] == "sip" for call in calls)
    assert all(call[1]["params"]["adjustment"] == "split" for call in calls)
    assert calls[1][1]["params"]["page_token"] == "opaque"
    assert calls[0][1]["allow_redirects"] is False
    assert "fixture-key" not in repr(client)
    assert "fixture-secret" not in json.dumps(client.events)
    assert "opaque" not in json.dumps(client.events)


@pytest.mark.parametrize("status", [401, 403, 422])
def test_no_entitlement_retry_or_fallback(cfg, status):
    client, calls, _ = client_for(cfg, [Response(status)])
    with pytest.raises(DataAccessError, match=str(status)):
        client.bars(params(cfg))
    assert len(calls) == 1
    assert calls[0][1]["params"]["feed"] == "sip"


def test_429_bounded_backoff(cfg):
    client, calls, sleeps = client_for(cfg, [Response(429)] * cfg["retry"]["max_attempts"])
    with pytest.raises(DataAccessError, match="exhausted"):
        client.bars(params(cfg))
    assert len(calls) == 4
    assert [e["retry_seconds"] for e in client.events if "retry_seconds" in e] == [1, 2, 4]
    assert max(sleeps) <= cfg["retry"]["max_seconds"]


def test_429_retry_then_success(cfg, bars_fixture):
    client, calls, _ = client_for(
        cfg,
        [
            Response(429, headers={"Retry-After": "3"}),
            Response(payload={"bars": {"AAPL": [bars_fixture]}}),
        ],
    )
    assert len(client.bars(params(cfg))) == 1
    assert client.events[0]["retry_seconds"] == 3
    assert len(calls) == 2


def test_retry_after_too_long_stops(cfg):
    client, calls, _ = client_for(cfg, [Response(429, headers={"Retry-After": "3600"})])
    with pytest.raises(DataAccessError, match="bounded wait"):
        client.bars(params(cfg))
    assert len(calls) == 1


@pytest.mark.parametrize("change", [{"feed": "iex"}, {"adjustment": ""}])
def test_client_refuses_implicit_policy(cfg, change):
    client, calls, _ = client_for(cfg, [])
    request = params(cfg) | change
    with pytest.raises(ValueError):
        client.bars(request)
    assert calls == []


def test_duplicate_page_rows_rejected(cfg, bars_fixture):
    client, _, _ = client_for(
        cfg,
        [
            Response(payload={"bars": {"AAPL": [bars_fixture]}, "next_page_token": "one"}),
            Response(payload={"bars": {"AAPL": [bars_fixture]}}),
        ],
    )
    with pytest.raises(ValueError, match="duplicate_keys"):
        client.bars(params(cfg))


def test_repeated_page_token_rejected(cfg):
    client, _, _ = client_for(cfg, [Response(payload={"bars": {}, "next_page_token": "one"})] * 2)
    with pytest.raises(DataAccessError, match="Repeated"):
        client.bars(params(cfg))


def test_5xx_retries(cfg):
    client, calls, _ = client_for(cfg, [Response(503), Response(payload={"bars": {}})])
    assert client.bars(params(cfg)).empty
    assert len(calls) == 2


def test_missing_optional_provider_fields(cfg, bars_fixture):
    bars_fixture.pop("n")
    bars_fixture.pop("vw")
    client, _, _ = client_for(cfg, [Response(payload={"bars": {"AAPL": [bars_fixture]}})])
    data = client.bars(params(cfg))
    assert data.trade_count.isna().all()
    assert data.vwap.isna().all()
