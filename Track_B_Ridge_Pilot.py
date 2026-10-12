"""Run inside the audit notebook with: %run -i Track_B_Quick_Experiment.py

Uses existing stocks, course and grid variables; does not download or place trades.
Start-of-bar semantics and chronological split dates remain provisional.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error

needed = ['stocks', 'course', 'grid']
if any(name not in globals() for name in needed):
    raise RuntimeError('Run sections 1–4 of the Alpaca audit notebook in this runtime first. '
                       'This cell needs its stocks, course and grid variables.')

SYMBOLS_QUICK = ['AAPL', 'MSFT', 'NVDA', 'INTC', 'CSCO']
# Replace only if you and Sumeet have already agreed on different boundaries.
TRAIN_END = pd.Timestamp('2023-01-01', tz='UTC')
VALIDATION_END = pd.Timestamp('2024-01-01', tz='UTC')
RIDGE_ALPHA = 10.0  # Fixed pilot setting, no hyperparameter search
OUTPUT = Path('track_b_quick_experiment')
OUTPUT.mkdir(exist_ok=True)

def quick_features(bars):
    """Causal features; momentum uses retained trading observations, including overnight gaps."""
    lp = np.log(bars['close'])
    r = lp.diff()
    lv = np.log1p(bars['volume'])
    return pd.DataFrame({
        'return_1': r,
        'momentum_6': lp - lp.shift(6),
        'momentum_24': lp - lp.shift(24),
        'momentum_48': lp - lp.shift(48),
        'volatility_24': r.rolling(24, min_periods=24).std(),
        'range': np.log(bars['high'] / bars['low']),
        'volume_relative_48': lv - lv.rolling(48, min_periods=48).mean(),
    }, index=bars.index)

g = grid.sort_values('bar_start').reset_index(drop=True).copy()
assert not g['bar_start'].duplicated().any()
dates = pd.DatetimeIndex(g.bar_start)
stock_inputs, stock_closes = {}, {}
for symbol in SYMBOLS_QUICK:
    d = stocks[symbol].copy()
    d['timestamp'] = pd.to_datetime(d['timestamp'], utc=True)
    if d.timestamp.duplicated().any():
        raise ValueError(f'{symbol}: duplicate timestamps')
    aligned = d.set_index('timestamp').reindex(dates)
    stock_inputs[symbol] = quick_features(aligned)
    stock_closes[symbol] = aligned['close'].to_numpy()
prices = pd.DataFrame(stock_closes, index=g.index)

# The origin is the end of a full stock hour. Require all intermediate stock bars.
future = prices.groupby(g.session).shift(-4)
continuous = prices.notna().all(axis=1)
for step in range(1, 5):
    continuous &= prices.groupby(g.session).shift(-step).notna().all(axis=1)
exit_time = g.groupby('session')['bar_end'].shift(-4)
future_return = np.log(future / prices)
# One fixed peer-basket target; course index returns are never future inputs.
target = future_return.sub(future_return.mean(axis=1), axis=0)

market_features = []
market_complete = np.ones(len(g), dtype=bool)
for name in ['USA500', 'USATECH']:
    d = course[name].copy()
    d['timestamp'] = pd.to_datetime(d['timestamp'], utc=True)
    if d.timestamp.duplicated().any():
        raise ValueError(f'{name}: duplicate timestamps')
    # Provisional START convention: same start = same interval; usable at bar_end.
    aligned = d.set_index('timestamp').reindex(dates)
    market_complete &= aligned['close'].notna().to_numpy()
    lp = np.log(aligned['close'])
    r = lp.diff()
    f = pd.DataFrame({
        name+'_return_1': r,
        name+'_momentum_6': lp - lp.shift(6),
        name+'_momentum_24': lp - lp.shift(24),
        name+'_volatility_24': r.rolling(24, min_periods=24).std(),
    }, index=dates)
    market_features.append(f)
market = pd.concat(market_features, axis=1)

parts = []
for symbol in SYMBOLS_QUICK:
    x = pd.concat([stock_inputs[symbol], market], axis=1).reset_index(drop=True)
    # Shared additive market inputs alone cannot distinguish stocks at one time.
    # Small state-by-stock interactions allow heterogeneous stock responses.
    for market_column in market.columns:
        for stock_column in ['momentum_6', 'volatility_24']:
            x[market_column+'__x__'+stock_column] = x[market_column]*x[stock_column]
    x['symbol'] = symbol
    x['decision_time'] = g.bar_end
    x['exit_time'] = exit_time
    x['target'] = target[symbol]
    x = x.loc[continuous & market_complete].replace([np.inf, -np.inf], np.nan).dropna()
    parts.append(x)
data = pd.concat(parts, ignore_index=True)
# Fair comparison: every model sees exactly the same complete five-stock origins.
counts = data.groupby('decision_time').symbol.nunique()
data = data[data.decision_time.isin(counts[counts == len(SYMBOLS_QUICK)].index)].copy()
train = data[(data.decision_time < TRAIN_END) & (data.exit_time < TRAIN_END)].copy()
validation = data[(data.decision_time >= TRAIN_END) &
                  (data.decision_time < VALIDATION_END) &
                  (data.exit_time < VALIDATION_END)].copy()
if len(train) == 0 or len(validation) == 0:
    raise ValueError('No usable training/validation samples. Inspect coverage and split dates.')

stock_columns = list(stock_inputs[SYMBOLS_QUICK[0]].columns)
usa_columns = [c for c in data if c.startswith('USA500_')]
tech_columns = [c for c in data if c.startswith('USATECH_')]
experiments = {
    'Stock only': stock_columns,
    'Stock + USA500': stock_columns + usa_columns,
    'Stock + USA500 + USATECH': stock_columns + usa_columns + tech_columns,
}

print('PROVISIONAL pilot: course timestamps assumed to mark interval START.')
print('Training: July 2020–December 2022; validation: calendar 2023.')
print('January 2024 onward is not used for fitting, tuning or scoring.')
print('Market arms include fixed momentum/volatility interactions with market features.')
print('Training origins:', train.decision_time.nunique(),
      '| validation origins:', validation.decision_time.nunique())

def rank_ic(group):
    a = group['prediction'].rank()
    b = group['target'].rank()
    return a.corr(b) if a.nunique() > 1 and b.nunique() > 1 else np.nan

results, predictions, ic_tables = [], [], []
for name, columns in experiments.items():
    model = make_pipeline(StandardScaler(), Ridge(alpha=RIDGE_ALPHA))
    model.fit(train[columns], train.target)
    pred = model.predict(validation[columns])
    evaluated = validation[['decision_time','exit_time','symbol','target']].copy()
    evaluated['prediction'] = pred
    evaluated['model'] = name
    # Center predictions on the same five-stock relative scale used for targets.
    evaluated['prediction'] -= evaluated.groupby('decision_time').prediction.transform('mean')
    ic = pd.Series({t: rank_ic(part) for t,part in evaluated.groupby('decision_time')}, name='rank_ic')
    results.append(dict(model=name, features=len(columns),
                        MAE=mean_absolute_error(evaluated.target,evaluated.prediction),
                        RMSE=np.sqrt(mean_squared_error(evaluated.target,evaluated.prediction)),
                        mean_rank_IC=ic.mean(), scored_origins=int(ic.notna().sum())))
    predictions.append(evaluated)
    table = ic.rename_axis('decision_time').reset_index()
    table['model'] = name
    ic_tables.append(table)

summary = pd.DataFrame(results)
summary['MAE_change_vs_stock_only'] = summary.MAE - summary.MAE.iloc[0]
summary['IC_change_vs_stock_only'] = summary.mean_rank_IC - summary.mean_rank_IC.iloc[0]
print('\nLower MAE/RMSE is better; higher mean rank IC is better. Errors are log-return units.')
print(summary.to_string(index=False))
summary.to_csv(OUTPUT/'validation_summary.csv',index=False)
pd.concat(predictions).to_csv(OUTPUT/'validation_predictions.csv',index=False)
pd.concat(ic_tables).to_csv(OUTPUT/'validation_rank_ic.csv',index=False)
(OUTPUT/'pilot_settings.json').write_text(json.dumps({
    'status':'PROVISIONAL development experiment; not final test evidence',
    'course_timestamp_convention':'start ASSUMED, not course-export verified',
    'stock_feed':'Use audit_metadata.json to confirm downloaded feed',
    'train_end_exclusive':str(TRAIN_END), 'validation_end_exclusive':str(VALIDATION_END),
    'ridge_alpha':RIDGE_ALPHA, 'symbols':SYMBOLS_QUICK,
    'target':'4h same-session stock log return minus equal-weight five-stock mean log return',
    'features':'Retained trading-observation lags; can span overnight gaps',
    'market_interactions':'Each market feature times stock momentum_6 and volatility_24; fixed in advance',
    'matching':'Exact full-hour intervals; no index forward-fill',
    'execution':'Prediction audit only; no tradable fills, costs or profitability claimed',
},indent=2))
import shutil
archive = shutil.make_archive('Track_B_Quick_Experiment_Results','zip',OUTPUT)
print('\nSaved:',archive)
try:
    from google.colab import files
    files.download(archive)
except ImportError:
    pass
