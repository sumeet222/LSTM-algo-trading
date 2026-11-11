"""Original C-A annual archive only; identity-bound read-only loading."""
from dataclasses import dataclass
from pathlib import Path
import csv
import hashlib
import json
import torch
from lstm_data.hf20_s2c_ca import ComponentMAG
from lstm_data.hf20_mag_c3_io import decode
import numpy as np
from .contracts import FeatureSnapshot

SYMBOLS = tuple('VZ COP BAC BA AAPL PEP MRK SBUX CVX MS AMD KO JNJ AMZN XOM WFC AVGO TSLA MA CSCO'.split())
BASE = Path('reports/experiments/hf20_s9_mag_stage2_s2c_ca_2026-10-28')


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True)
class Bundle:
    year: int
    checkpoint: Path
    recipe: Path
    calibration: Path
    phases: Path
    identities: tuple[str, ...]

    def verify(self) -> None:
        if tuple(digest(p) for p in (self.checkpoint, self.recipe, self.calibration, self.phases)) != self.identities:
            raise ValueError('ORIGINAL_BUNDLE_IDENTITY_MISMATCH')


class ModelRegistry:
    def __init__(self, root: Path, registry: Path):
        self.root = root
        self.rows = json.loads(registry.read_text())['bundles']

    def load(self, year: int) -> 'MagnitudeForecaster':
        if year not in (2021, 2022, 2023, 2024):
            raise ValueError('NO_LEGAL_ANNUAL_BUNDLE')
        row = self.rows[str(year)]
        bundle = Bundle(year, self.root / row['checkpoint'], self.root / row['recipe'],
                        self.root / row['calibration'], self.root / row['phases'],
                        tuple(row['sha256']))
        bundle.verify()
        phases = json.loads(bundle.phases.read_text())['phases']['restricted']
        recipe = json.loads(bundle.recipe.read_text())
        if (self.root / phases['recipe_reference']).resolve() != bundle.recipe.resolve() or recipe['fit_stop_inclusive'] != phases['cutoff']:
            raise ValueError('ORIGINAL_RECIPE_ASSOCIATION_MISMATCH')
        if tuple(f['symbol'] for f in recipe['floors']) != SYMBOLS:
            raise ValueError('STOCK_ORDER_MISMATCH')
        # Constructor only; never invoke the historical seed/fit/preflight helpers.
        model = ComponentMAG().float()
        model.load_state_dict(torch.load(bundle.checkpoint, map_location='cpu', weights_only=True))
        model.eval()
        model.requires_grad_(False)
        if sum(p.numel() for p in model.parameters()) != 6572:
            raise ValueError('ARCHITECTURE_MISMATCH')
        with bundle.calibration.open() as stream:
            coefficients = list(csv.DictReader(stream))
        if any(float(c['scale']) != phases['scale'] for c in coefficients):
            raise ValueError('C3_SCALE_MISMATCH')
        return MagnitudeForecaster(bundle, model, phases['scale'],
                                   {c['group']: float(c['c_star']) for c in coefficients})


class MagnitudeForecaster:
    def __init__(self, bundle: Bundle, model: ComponentMAG, scale: float, factors: dict[str, float]):
        self.bundle, self.model, self.scale, self.factors = bundle, model, scale, factors

    def predict(self, snapshot: FeatureSnapshot) -> float:
        from zoneinfo import ZoneInfo
        if (snapshot.nominal_origin.astimezone(ZoneInfo('America/New_York')).year != self.bundle.year
                or snapshot.recipe_hash != self.bundle.identities[1] or snapshot.ticker not in SYMBOLS
                or not snapshot.valid):
            raise ValueError('SNAPSHOT_BUNDLE_MISMATCH_OR_INELIGIBLE')
        self.bundle.verify()
        self.model.eval()
        with torch.inference_mode():
            output = self.model(torch.tensor(snapshot.values, dtype=torch.float32)[None],
                                torch.tensor(snapshot.clock, dtype=torch.float32)[None])
        result = float(decode(output.numpy(), self.scale, self.factors[snapshot.category])[0])
        if not np.isfinite(result) or result < 0:
            raise ValueError('INVALID_MAGNITUDE')
        return result
