"""Exploratory shared-LSTM pilot. Run in existing Colab: %run -i Track_B_LSTM_Pilot.py
Requires stocks, course and grid from the audit notebook. No downloads or trades.
Start-of-bar timing and all modeling settings remain provisional.
"""
from pathlib import Path
import json, random, shutil, time
import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error

if any(name not in globals() for name in ['stocks','course','grid']):
    raise RuntimeError('First run sections 1–4 of the audit notebook in this Colab runtime.')

NAMES = ['AAPL','MSFT','NVDA','INTC','CSCO']
LOOKBACK = 48
HIDDEN = 32
SEED = 42
MAX_EPOCHS = 12
PATIENCE = 3
BATCH = 128
LEARNING_RATE = 0.001
INNER_END = pd.Timestamp('2022-10-01',tz='UTC')
TRAIN_END = pd.Timestamp('2023-01-01',tz='UTC')
VALIDATION_END = pd.Timestamp('2024-01-01',tz='UTC')
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
torch.set_num_threads(2)
OUT = Path('track_b_lstm_pilot')
if OUT.exists():
    OUT = Path('track_b_lstm_pilot_'+pd.Timestamp.now(tz='UTC').strftime('%Y%m%d_%H%M%S'))
OUT.mkdir()

def make_features(d, use_volume=True):
    lp = np.log(d['close']); r = lp.diff()
    f = pd.DataFrame({'return_1':r,'momentum_6':lp-lp.shift(6),
                      'momentum_24':lp-lp.shift(24),
                      'volatility_24':r.rolling(24,min_periods=24).std()},index=d.index)
    if use_volume:
        lv = np.log1p(d.volume)
        f['range'] = np.log(d.high/d.low)
        f['volume_relative_48'] = lv-lv.rolling(48,min_periods=48).mean()
    return f.replace([np.inf,-np.inf],np.nan)

def build_samples(stock_frames, index_frames, clock):
    # Do not construct or inspect 2024+ outcomes in this pilot.
    g = clock.loc[clock.bar_end < VALIDATION_END].sort_values('bar_start').reset_index(drop=True)
    timestamps = pd.DatetimeIndex(g.bar_start)
    stock_features=[]; closes=[]
    for name in NAMES:
        d=stock_frames[name].copy();d['timestamp']=pd.to_datetime(d.timestamp,utc=True)
        if d.timestamp.duplicated().any(): raise ValueError(name+': duplicate timestamps')
        d=d.set_index('timestamp').reindex(timestamps)
        stock_features.append(make_features(d).to_numpy(dtype=np.float32))
        closes.append(d.close.to_numpy())
    market_features=[]
    for name in ['USA500','USATECH']:
        d=index_frames[name].copy();d['timestamp']=pd.to_datetime(d.timestamp,utc=True)
        if d.timestamp.duplicated().any(): raise ValueError(name+': duplicate timestamps')
        # START-of-bar assumption; exact interval join, no future or stale fill.
        d=d.set_index('timestamp').reindex(timestamps)
        market_features.append(make_features(d,False).to_numpy(dtype=np.float32))
    stock_panel=np.stack(stock_features,axis=1)  # time × stock × 6
    market_panel=np.concatenate(market_features,axis=1)  # time × 8
    all_features=np.concatenate([stock_panel,np.repeat(market_panel[:,None,:],5,axis=1)],axis=2)
    p=pd.DataFrame(np.stack(closes,axis=1));future=p.groupby(g.session).shift(-4)
    ok=p.notna().all(axis=1)
    for step in range(1,5):ok &= p.groupby(g.session).shift(-step).notna().all(axis=1)
    returns=np.log(future/p);relative=returns.sub(returns.mean(axis=1),axis=0)
    exits=g.groupby('session').bar_end.shift(-4)
    xs=[];ys=[];meta=[]
    for t in np.flatnonzero(ok):
        if t < LOOKBACK-1:continue
        window=all_features[t-LOOKBACK+1:t+1]
        if not np.isfinite(window).all() or not np.isfinite(relative.iloc[t]).all():continue
        for i,name in enumerate(NAMES):
            xs.append(window[:,i,:]);ys.append(relative.iloc[t,i])
            meta.append({'decision_time':g.bar_end.iloc[t],'exit_time':exits.iloc[t],'symbol':name})
    if not xs:raise ValueError('No complete shared 48-observation windows.')
    return np.stack(xs),np.asarray(ys,dtype=np.float32),pd.DataFrame(meta),all_features,g

X,Y,META,PANEL,G=build_samples(stocks,course,grid)
fit_mask=(META.decision_time<INNER_END)&(META.exit_time<INNER_END)
inner_mask=(META.decision_time>=INNER_END)&(META.decision_time<TRAIN_END)&(META.exit_time<TRAIN_END)
refit_mask=(META.decision_time<TRAIN_END)&(META.exit_time<TRAIN_END)
val_mask=(META.decision_time>=TRAIN_END)&(META.exit_time<VALIDATION_END)
if any(not m.any() for m in [fit_mask,inner_mask,refit_mask,val_mask]):
    raise ValueError('An empty chronological partition prevents this pilot.')

class SharedLSTM(nn.Module):
    def __init__(self, inputs):
        super().__init__()
        self.encoder=nn.LSTM(inputs,HIDDEN,num_layers=1,batch_first=True)
        self.head=nn.Linear(HIDDEN,1)
    def forward(self,x):
        output,_=self.encoder(x)
        return self.head(output[:,-1]).squeeze(-1)

def seed_everything():
    random.seed(SEED);np.random.seed(SEED);torch.manual_seed(SEED)
    if torch.cuda.is_available():torch.cuda.manual_seed_all(SEED)
    torch.backends.cudnn.benchmark=False
    torch.backends.cudnn.deterministic=True

def preparation(columns,cutoff,training_mask):
    # Fit once on unique historical panel observations; no validation rows.
    rows=PANEL[(G.bar_end<cutoff).to_numpy()][:,:,columns].reshape(-1,len(columns))
    rows=rows[np.isfinite(rows).all(axis=1)]
    scaler=StandardScaler().fit(rows)
    transformed=scaler.transform(X[:,:,columns].reshape(-1,len(columns)))
    transformed=transformed.reshape(len(X),LOOKBACK,len(columns)).astype(np.float32)
    scale=max(float(Y[training_mask].std()),1e-6)
    return transformed,scale,scaler

def loader(x,y,mask,shuffle):
    return DataLoader(TensorDataset(torch.from_numpy(x[mask]),torch.from_numpy(y[mask])),
                      batch_size=BATCH,shuffle=shuffle,num_workers=0)

def train_epoch(model,batches,optimizer):
    model.train();total=0.;count=0
    for xb,yb in batches:
        xb,yb=xb.to(DEVICE),yb.to(DEVICE)
        optimizer.zero_grad(set_to_none=True)
        loss=nn.functional.mse_loss(model(xb),yb)
        if not torch.isfinite(loss):raise RuntimeError('Nonfinite training loss; stop and inspect.')
        loss.backward();nn.utils.clip_grad_norm_(model.parameters(),1.0);optimizer.step()
        total+=loss.item()*len(xb);count+=len(xb)
    return total/count

def predict(model,x):
    model.eval();parts=[]
    with torch.no_grad():
        for batch in torch.from_numpy(x).split(BATCH):
            parts.append(model(batch.to(DEVICE)).cpu().numpy())
    return np.concatenate(parts)

print('PROVISIONAL LSTM PILOT | start-of-bar assumption | device:',DEVICE,flush=True)
print('One shared model per arm, 48 observations, hidden width 32, one seed.',flush=True)
print('2022 Q4 selects epoch count; fresh refit through 2022; 2023 evaluates once.',flush=True)
print('2024 onward is not fitted or scored.',flush=True)
print('Common train origins:',META.loc[refit_mask].decision_time.nunique(),
      '| common 2023 origins:',META.loc[val_mask].decision_time.nunique(),flush=True)
arms={'LSTM stock only':list(range(6)),
      'LSTM stock + USA500':list(range(10)),
      'LSTM stock + USA500 + USATECH':list(range(14))}
summaries=[];predictions=[];logs=[];scaler_records={}
for name,columns in arms.items():
    start=time.monotonic();seed_everything()
    x,scale,_=preparation(columns,INNER_END,fit_mask)
    model=SharedLSTM(len(columns)).to(DEVICE)
    optimizer=torch.optim.Adam(model.parameters(),lr=LEARNING_RATE)
    batches=loader(x,Y/scale,fit_mask.to_numpy(),True)
    best_loss=np.inf;best_epoch=1;stale=0
    for epoch in range(1,MAX_EPOCHS+1):
        loss=train_epoch(model,batches,optimizer)
        pred=predict(model,x[inner_mask])
        inner_loss=float(np.mean((pred-Y[inner_mask]/scale)**2))
        logs.append(dict(model=name,phase='inner_selection',epoch=epoch,train_loss=loss,inner_loss=inner_loss))
        print(name,'selection epoch',epoch,'inner MSE',round(inner_loss,5),flush=True)
        if inner_loss<best_loss-1e-5:best_loss=inner_loss;best_epoch=epoch;stale=0
        else:stale+=1
        if stale>=PATIENCE:break
    # Fresh model and train-only scaler refitted through December 2022.
    seed_everything();x,scale,scaler=preparation(columns,TRAIN_END,refit_mask)
    model=SharedLSTM(len(columns)).to(DEVICE)
    optimizer=torch.optim.Adam(model.parameters(),lr=LEARNING_RATE)
    batches=loader(x,Y/scale,refit_mask.to_numpy(),True)
    for epoch in range(1,best_epoch+1):
        loss=train_epoch(model,batches,optimizer)
        logs.append(dict(model=name,phase='refit',epoch=epoch,train_loss=loss,inner_loss=None))
        print(name,'refit epoch',epoch,'/',best_epoch,flush=True)
    pred=predict(model,x[val_mask])*scale
    table=META.loc[val_mask].copy();table['target']=Y[val_mask]
    table['prediction']=pred;table['model']=name
    table['prediction']-=table.groupby('decision_time').prediction.transform('mean')
    ic=[]
    for _,part in table.groupby('decision_time'):
        a=part.prediction.rank();b=part.target.rank()
        if a.nunique()>1 and b.nunique()>1:ic.append(a.corr(b))
    summaries.append(dict(model=name,features=len(columns),selected_epochs=best_epoch,
                          MAE=mean_absolute_error(table.target,table.prediction),
                          RMSE=np.sqrt(mean_squared_error(table.target,table.prediction)),
                          mean_rank_IC=float(np.mean(ic)) if ic else None,
                          scored_origins=len(ic),runtime_seconds=round(time.monotonic()-start,1)))
    predictions.append(table)
    scaler_records[name]={'columns':columns,'mean':scaler.mean_.tolist(),
                          'scale':scaler.scale_.tolist(),'target_scale':scale}
    del model
    if torch.cuda.is_available():torch.cuda.empty_cache()

summary=pd.DataFrame(summaries)
print('\nPRELIMINARY 2023 RESULTS\n',summary.to_string(index=False),flush=True)
summary.to_csv(OUT/'validation_summary.csv',index=False)
pd.concat(predictions).to_csv(OUT/'validation_predictions.csv',index=False)
pd.DataFrame(logs).to_csv(OUT/'training_log.csv',index=False)
(OUT/'scalers.json').write_text(json.dumps(scaler_records,indent=2))
(OUT/'pilot_settings.json').write_text(json.dumps({
    'status':'exploratory shared-LSTM pilot, not canonical Track B implementation',
    'timestamp':'course start-of-bar ASSUMED; complete bars only',
    'universe':NAMES,'lookback':LOOKBACK,'hidden_width':HIDDEN,'layers':1,'dropout':0,
    'seed':SEED,'max_epochs':MAX_EPOCHS,'patience':PATIENCE,'batch_size':BATCH,
    'learning_rate':LEARNING_RATE,'gradient_clip':1.0,
    'inner_end':str(INNER_END),'train_end':str(TRAIN_END),'validation_end':str(VALIDATION_END),
    'target':'same-session 4h stock log return minus five-stock mean log return',
    'features':'6 stock / 4 USA500 / 4 USATECH; lags can include overnight gaps',
    'preprocessing':'train-only standard scaling; final refit uses selected inner epoch count',
    'stock_only_mask':'all arms use identical dates and complete windows including market availability',
    'device':str(DEVICE),'torch_version':torch.__version__,'pandas_version':pd.__version__,
    'limitation':'one seed, no trading/execution/cost results; compare ridge only on matched samples',
},indent=2))
archive=shutil.make_archive(str(OUT)+'_Results','zip',OUT)
print('Results:',archive,flush=True)
try:
    from google.colab import files
    files.download(archive)
except ImportError:
    pass
