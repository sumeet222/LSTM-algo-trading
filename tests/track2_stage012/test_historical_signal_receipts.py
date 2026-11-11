"""Read-only verification of the sealed small historical signal exports, no source scan."""
from pathlib import Path
import json
from collections import defaultdict
from datetime import datetime

RUN=Path('trading/track2/stage012/audits/completion_v1/historical_run_v1')


def test_historical_receipts_and_risk_separation():
    status=json.loads((RUN/'completion.json').read_text())
    assert status['issued']==22 and status['orders_or_fills']==0 and status['pnl_calculations']==0
    before=json.loads((RUN/'signals_without_risk.json').read_text())
    after=json.loads((RUN/'signals_with_prefix_risk.json').read_text())
    signs=defaultdict(set)
    for a,b in zip(before,after):
        old,new=a['signal'],b['signal']
        assert old['calibrated_magnitude']==new['calibrated_magnitude']
        assert old['direction']==new['direction']
        assert old['checkpoint_hash']==new['checkpoint_hash']
        assert .5<=new['size_multiplier']<=1.5
        assert datetime.fromisoformat(new['decision_utc'])<datetime.fromisoformat(new['earliest_executable_observation_utc'])
        signs[(new['ticker'],new['local_origin_et'][:10])].add((new['direction'],b['session_sign_lineage']))
        assert not {'A','r','endpoint_price','execution_price','pnl','F09_complete'}&set(new)
    assert len(signs)==4 and all(len(s)==1 for s in signs.values())
    reference=json.loads((RUN/'risk_preparation_receipt.json').read_text())
    assert reference['ready']==560 and reference['counts_min']>=40
    twin=json.loads((RUN/'adversarial_historical_twins.json').read_text())
    assert twin['prior_signal_unchanged'] and not twin['source_files_modified']
