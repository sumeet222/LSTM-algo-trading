"""One-package bounded intake; uses existing client, never edits original chunks."""
import argparse
import hashlib
import io
import json
import os
import tempfile
import time
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

from lstm_data.alpaca import HistoricalClient, credentials
from lstm_data.config import atomic_new, now

PARSER = argparse.ArgumentParser()
PARSER.add_argument('--package', type=Path, required=True)
PARSER.add_argument('--execute', action='store_true')
PARSER.add_argument('--smoke', action='store_true')
ARGS = PARSER.parse_args()
PLAN = json.loads((ARGS.package / 'materialization_plan.json').read_text())
STATE_PATH = ARGS.package / 'source_storage_manifest.json'
ROOT = Path(PLAN['source_root'])
STATE = json.loads(STATE_PATH.read_text()) if STATE_PATH.exists() else {
    'schema_version': 1, 'package': 'P1.CLOSE', 'attempts': [], 'chunks': [],
    'plan_sha256': hashlib.sha256(
        (ARGS.package / 'materialization_plan.json').read_bytes()
    ).hexdigest(),
    'active_seconds': 0.0, 'status': 'PREPARED', 'source_bytes': 0,
}
assert STATE['plan_sha256'] == hashlib.sha256(
    (ARGS.package / 'materialization_plan.json').read_bytes()
).hexdigest()
RUN_START = time.monotonic()
PREVIOUS_ACTIVE = STATE['active_seconds']


def save_state():
    """Only the resumable control checkpoint is replaced atomically."""
    STATE['active_seconds'] = PREVIOUS_ACTIVE + time.monotonic() - RUN_START
    fd, name = tempfile.mkstemp(dir=ARGS.package, prefix='.checkpoint-')
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(STATE, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, STATE_PATH)
    finally:
        Path(name).unlink(missing_ok=True)


def guard():
    if len(STATE['attempts']) >= PLAN['caps']['transport_attempts']:
        raise RuntimeError('ATTEMPT_CAP_REACHED')
    if PREVIOUS_ACTIVE + time.monotonic() - RUN_START >= PLAN['caps']['active_seconds']:
        raise RuntimeError('ACTIVE_TIME_CAP_REACHED')
    if STATE['source_bytes'] >= PLAN['caps']['additional_compressed_bytes']:
        raise RuntimeError('SOURCE_STORAGE_CAP_REACHED')


def guarded_get(endpoint, **kwargs):
    """Count every actual transport attempt, preserving safe metadata only."""
    guard()
    event = {
        'id': len(STATE['attempts']) + 1, 'time': now(), 'endpoint': endpoint,
        'params': {k: v for k, v in kwargs['params'].items() if k != 'page_token'},
        'continuation': bool(kwargs['params'].get('page_token')), 'status': 'STARTED',
    }
    STATE['attempts'].append(event)
    save_state()
    try:
        response = requests.get(endpoint, **kwargs)
    except requests.RequestException as exc:
        event['status'] = 'TRANSPORT_ERROR'
        event['error_class'] = type(exc).__name__
        save_state()
        raise
    event.update(status=response.status_code, retrieved_at=now(),
                 response_bytes=len(response.content),
                 response_sha256=hashlib.sha256(response.content).hexdigest())
    save_state()
    return response


def publish(key, kind, params, data, rows, received_rows):
    """Immutable data and per-chunk manifest, no file replacement."""
    path = ROOT / f'{kind}-{key}.parquet' if kind != 'actions' else ROOT / f'{kind}-{key}.json'
    if STATE['source_bytes'] + len(data) > PLAN['caps']['additional_compressed_bytes']:
        raise RuntimeError('SOURCE_STORAGE_CAP_REACHED_BEFORE_PUBLICATION')
    sha = hashlib.sha256(data).hexdigest()
    metadata = {
        'key': key, 'kind': kind, 'params': params, 'path': str(path),
        'rows': rows, 'received_rows': received_rows, 'bytes': len(data), 'sha256': sha,
        'retrieved_at': now(), 'publication_time': None,
        'historical_vintage': 'CURRENTLY_RETRIEVED_RETROSPECTIVE_HISTORY',
    }
    manifest = path.with_suffix('.manifest.json')
    if path.exists():
        if hashlib.sha256(path.read_bytes()).hexdigest() != sha:
            raise RuntimeError('IMMUTABLE_KEY_CONFLICT')
    else:
        atomic_new(path, data)
    if not manifest.exists():
        atomic_new(manifest, (json.dumps(metadata, indent=2, sort_keys=True) + '\n').encode())
    else:
        metadata = json.loads(manifest.read_text())
    STATE['source_bytes'] += len(data)
    STATE['chunks'].append(metadata)
    save_state()


if ARGS.smoke:
    # No transport/authentication. Verify hard bounds before provider access.
    old = len(STATE['attempts'])
    STATE['attempts'] = [{}] * 400
    try:
        guard()
        raise AssertionError('Attempt guard failed')
    except RuntimeError as exc:
        assert str(exc) == 'ATTEMPT_CAP_REACHED'
    STATE['attempts'] = STATE['attempts'][:old]
    assert PLAN['minute_full_preflight']['dense_monthly_pages'] > 400
    assert len(PLAN['requests']) == 17
    print('Offline budget/preflight smoke PASS; no network or files changed')
    raise SystemExit(0)
if not ARGS.execute:
    print('Prepared plan only; execution requires --execute')
    raise SystemExit(0)

ROOT.mkdir(parents=True, exist_ok=True)
LOCK = ROOT / '.acquisition.lock'
with LOCK.open('x') as stream:
    stream.write(now())
try:
    load_dotenv(Path('.env'), override=False)
    key_value, secret_value = credentials()
    cfg = json.loads(Path('configs/track_a_data.json').read_text())
    client = HistoricalClient(cfg, key_value, secret_value, get=guarded_get)
    gaps = json.loads((ARGS.package / 'stock_source_qa.json').read_text())['gaps']
    gap_keys = {(g['symbol'], pd.Timestamp(t)) for g in gaps for t in g['missing']}
    for request in PLAN['requests']:
        guard()
        params, kind = request['params'], request['kind']
        key = hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()[:20]
        if any(c['key'] == key and c['kind'] == kind for c in STATE['chunks']):
            continue
        # Recover a complete existing chunk after checkpoint-only interruption.
        suffix = '.json' if kind == 'actions' else '.parquet'
        existing_manifest = ROOT / f'{kind}-{key}.manifest.json'
        existing_data = ROOT / f'{kind}-{key}{suffix}'
        if existing_manifest.exists() and existing_data.exists():
            metadata = json.loads(existing_manifest.read_text())
            assert hashlib.sha256(existing_data.read_bytes()).hexdigest() == metadata['sha256']
            STATE['chunks'].append(metadata)
            STATE['source_bytes'] += metadata['bytes']
            save_state()
            continue
        before = len(STATE['attempts'])
        if kind == 'actions':
            records = {}
            cursor = None
            seen = set()
            while True:
                call_params = dict(params)
                if cursor:
                    call_params['page_token'] = cursor
                # Existing action client is unavailable; same transport/rate/budgets.
                for attempt in range(cfg['retry']['max_attempts']):
                    client.sleep(60 / cfg['retry']['requests_per_minute'])
                    try:
                        response = guarded_get(request['endpoint'], params=call_params,
                                               headers={'APCA-API-KEY-ID': key_value,
                                                        'APCA-API-SECRET-KEY': secret_value},
                                               timeout=cfg['retry']['timeout_seconds'],
                                               allow_redirects=False)
                    except requests.RequestException:
                        if attempt + 1 == cfg['retry']['max_attempts']:
                            raise RuntimeError('ACTION_TRANSPORT_RETRIES_EXHAUSTED') from None
                        client.sleep(min(cfg['retry']['max_seconds'], 2 ** attempt))
                        continue
                    if response.status_code == 200:
                        break
                    if response.status_code not in {429, 500, 502, 503, 504}:
                        raise RuntimeError('ACTION_HTTP_FAILURE_NO_ENTITLEMENT_CHANGE')
                    delay = float(response.headers.get('Retry-After', 2 ** attempt))
                    if delay > cfg['retry']['max_seconds']:
                        raise RuntimeError('ACTION_RETRY_AFTER_EXCEEDS_WAIT_CAP')
                    client.sleep(delay)
                else:
                    raise RuntimeError('ACTION_RETRIES_EXHAUSTED')
                payload = response.json()
                for category, items in payload['corporate_actions'].items():
                    records.setdefault(category, []).extend(items)
                cursor = payload.get('next_page_token')
                if not cursor:
                    break
                if cursor in seen:
                    raise RuntimeError('ACTION_PAGINATION_LOOP')
                seen.add(cursor)
            data = (
                json.dumps({'corporate_actions': records}, indent=2, sort_keys=True) + '\n'
            ).encode()
            rows = sum(len(items) for items in records.values())
            publish(key, kind, params, data, rows, rows)
        else:
            frame = client.bars(params)
            received = len(frame)
            if kind == 'gap_30min':
                frame = frame.loc[[
                    (row.symbol, row.timestamp) in gap_keys for row in frame.itertuples()
                ]].copy()
            buffer = io.BytesIO()
            frame.to_parquet(buffer, index=False, compression='zstd')
            publish(key, kind, params, buffer.getvalue(), len(frame), received)
        print(json.dumps({'completed': kind, 'key': key, 'rows': STATE['chunks'][-1]['rows'],
                          'calls': len(STATE['attempts']) - before,
                          'total_attempts': len(STATE['attempts']),
                          'bytes': STATE['source_bytes']}), flush=True)
    STATE['status'] = 'SCOPED_SOURCE_ATTEMPT_COMPLETE_FULL_MINUTE_PREFLIGHT_BLOCKED'
except Exception as exc:
    STATE['status'] = 'BLOCKED_RESUMABLE'
    STATE['failure_class'] = type(exc).__name__
    print(json.dumps({'status': STATE['status'], 'failure_class': type(exc).__name__,
                      'attempts': len(STATE['attempts'])}), flush=True)
finally:
    save_state()
    LOCK.unlink()
