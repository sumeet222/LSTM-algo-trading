"""Exact predeclared source allowlist. No discovery/globs or financial APIs."""
from pathlib import Path
from datetime import datetime
import hashlib
import json
import pandas as pd
from lstm_data.hf1m_action_source import adjust_prices

HOUR_COLUMNS=['ticker','session_date_et','hour_start_utc','hour_end_utc','is_stub','open','close','high','low',
              'close_input_cap5','observed_volume','observed_volume_complete','genuine_count','missing_count',
              'quarantine_count','conflict_count','invalid_minutes','proxy_count','longest_gap_minutes']


def file_hash(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


class HistoricalSourceStore:
    def __init__(self,root: Path,plan_path: Path,expected_plan_hash: str):
        if file_hash(plan_path)!=expected_plan_hash:
            raise ValueError('DRYRUN_PLAN_IDENTITY_MISMATCH')
        self.root=root;self.plan=json.loads(plan_path.read_text());self.reads: list[dict]=[]
        self.inventory_hash=hashlib.sha256(json.dumps(self.plan['sources'],sort_keys=True).encode()).hexdigest()

    def checked(self,row: dict) -> Path:
        path=Path(row['path'])
        if path.is_absolute() or '..' in path.parts or not '2010-07'<=path.stem<='2024-12':
            raise ValueError('SOURCE_PARTITION_DENIED_BEFORE_IO')
        if row not in self.plan['sources'] or not str(path).startswith('data/processed/hf20_hf1m_long_v1'):
            raise ValueError('SOURCE_NOT_PREDECLARED')
        full=self.root/path
        if file_hash(full)!=row['sha256']:
            raise ValueError('SOURCE_IDENTITY_MISMATCH')
        return full

    def hours(self) -> pd.DataFrame:
        frames=[]
        for row in self.plan['sources']:
            if row['role']!='hourly_replay':continue
            frame=pd.read_parquet(self.checked(row),columns=HOUR_COLUMNS,
                                  filters=[('ticker','in',self.plan['signal_tickers']),('session_date_et','<=','2024-11-29')])
            frames.append(frame);self.reads.append({'path':row['path'],'role':row['role'],'rows_returned':len(frame),'sha256':row['sha256']})
        return pd.concat(frames,ignore_index=True)

    def minutes(self,role: str,facts: list[dict]) -> dict[tuple[str,datetime,str],float]:
        if role not in ('m2_source','risk_prefix'):raise ValueError('INVALID_SOURCE_ROLE')
        keys=[pd.Timestamp(t) for t in self.plan['minute_keys'][role]]
        tickers=self.plan['signal_tickers'] if role=='m2_source' else self.plan['risk_tickers']
        result={}
        for row in self.plan['sources']:
            if row['role']!=role:continue
            selected=[t for t in keys if t.tz_convert('America/New_York').strftime('%Y-%m')==Path(row['path']).stem]
            frame=pd.read_parquet(self.checked(row),columns=['ticker','timestamp','is_rth','open','high','low','close'],
                                  filters=[('ticker','in',tickers),('timestamp','in',selected),('is_rth','==',True)])
            if frame.duplicated(['ticker','timestamp']).any():raise ValueError('AMBIGUOUS_SOURCE_MINUTE')
            frame=adjust_prices(frame,facts)
            for ticker,at,opened,closed in frame[['ticker','timestamp','open','close']].itertuples(index=False,name=None):
                result[(str(ticker),at.to_pydatetime(),'open')]=float(opened)
                result[(str(ticker),at.to_pydatetime(),'close')]=float(closed)
            self.reads.append({'path':row['path'],'role':role,'rows_returned':len(frame),'sha256':row['sha256']})
        return result
