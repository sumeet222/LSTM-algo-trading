"""Typed loader for the versioned review contract, with immutable human facts."""
from dataclasses import dataclass
from pathlib import Path
import json
from .model_registry import SYMBOLS


@dataclass(frozen=True)
class ProtocolContract:
    strategy_id: str
    gross_cap: float
    net_cap: float
    name_cap: float
    sleeve_cap: float
    clip: tuple[float, float]
    latency_minutes: int
    dynamic_rebalancing_enabled: bool = False

    @classmethod
    def load(cls, path: Path) -> 'ProtocolContract':
        data = json.loads(path.read_text())
        h, d = data['human_approved'], data['proposed_defaults']
        if (h['horizon_scheduled_minutes'] != 240 or h['holding'] != 'fixed'
                or h['dynamic_rebalancing_enabled'] or tuple(h['stock_order']) != SYMBOLS
                or h['origins_et'] != ['09:30','10:30','11:30','12:30','13:30','14:30','15:30']
                or h['calendar'] != 'XNYS' or not h['longs_and_shorts'] or data['stage3_enabled']):
            raise ValueError('HUMAN_FACTS_IMMUTABLE')
        caps = tuple(float(d[k]) for k in ('gross_nav_cap','net_nav_cap','name_gross_nav_cap','new_vintage_gross_nav_cap'))
        if any(not 0 < v <= 1 for v in caps) or d['latency_wall_minutes'] not in (1,2,5):
            raise ValueError('INVALID_DEFAULTS')
        return cls(data['strategy_id'], caps[0], caps[1], caps[2], caps[3],
                   (float(d['magnitude_ratio_clip'][0]), float(d['magnitude_ratio_clip'][1])),
                   d['latency_wall_minutes'])
