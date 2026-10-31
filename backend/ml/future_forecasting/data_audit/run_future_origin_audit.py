from pathlib import Path
import joblib, numpy as np, pandas as pd, json
from sklearn.metrics import mean_absolute_error, mean_squared_error

ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / 'data' / 'vidarbha_cotton_model_ready_1997_2024.csv'
ART = ROOT / 'backend' / 'ml' / 'future_forecasting' / 'artifacts' / 'future_horizon_models.joblib'
OUT = ROOT / 'backend' / 'ml' / 'future_forecasting' / 'data_audit'
OUT.mkdir(parents=True, exist_ok=True)

df=pd.read_csv(DATA).sort_values(['district','year']).reset_index(drop=True)
models=joblib.load(ART)
DISTS=sorted(df.district.unique())
WEATHER_PREFIXES=("tmax_","tmin_","rainfall_","rainy_days_","heavy_rain_days_","max_5day_","max_dry_spell_")

def weather_cols():
    cols=[c for c in df.columns if c.startswith(WEATHER_PREFIXES) and 'anomaly' not in c]
    anomalies=[c for c in df.columns if c.endswith('_district_anomaly')]
    return cols,anomalies
WCOLS,ACOLS=weather_cols()

def safe_weather(g, origin, target, scenario='normal'):
    hist=g[g.year<=origin].sort_values('year')
    recent=hist.tail(10)
    out={}
    for c in WCOLS:
        out[c]=float(recent[c].mean()) if recent[c].notna().any() else np.nan
    for c in [c for c in WCOLS if c.startswith(('tmax_','tmin_'))]:
        v=recent[['year',c]].dropna()
        if len(v)>=5:
            slope=np.polyfit(v.year.to_numpy(),v[c].to_numpy(),1)[0]
            out[c]=float(v[c].mean()+slope*(target-v.year.mean()))
    mult={'normal':1.0,'dry':0.8,'wet':1.2}[scenario]
    dmult={'normal':1.0,'dry':0.85,'wet':1.15}[scenario]
    emult={'normal':1.0,'dry':0.9,'wet':1.1}[scenario]
    smult={'normal':1.0,'dry':1.2,'wet':0.85}[scenario]
    for c in ['rainfall_annual_mm','rainfall_monsoon_mm','rainfall_kharif_mm']:
        if c in out and pd.notna(out[c]): out[c]*=mult
    for c in ['rainy_days_annual','heavy_rain_days_annual','rainy_days_monsoon','heavy_rain_days_monsoon','rainy_days_kharif','heavy_rain_days_kharif']:
        if c in out and pd.notna(out[c]): out[c]*=dmult
    for c in [c for c in WCOLS if 'rainfall_max' in c or 'max_5day' in c]:
        if c in out and pd.notna(out[c]): out[c]*=emult
    for c in [c for c in WCOLS if 'max_dry_spell' in c]:
        if c in out and pd.notna(out[c]): out[c]*=smult
    for base in ['rainfall_monsoon_mm','rainfall_kharif_mm','tmax_kharif_mean_c','tmin_kharif_mean_c']:
        a=base+'_district_anomaly'
        if a in ACOLS and base in out:
            histmean=g[g.year<=origin][base].mean()
            out[a]=float(out[base]-histmean)
    return out

def row_for(district,target,horizon,scenario='normal'):
    g=df[df.district==district].sort_values('year')
    hist=g[g.year<=target-horizon].sort_values('year')
    if len(hist)<5: return None
    last3=hist.tail(3).yield_target_kg_ha
    last5=hist.tail(5).yield_target_kg_ha
    area5=hist.tail(5).cotton_area_000ha
    origin=int(target-horizon)
    r={'district':district,'target_year':int(target),'horizon':int(horizon),'origin_year':origin,
       'y_lag1':float(hist.iloc[-1].yield_target_kg_ha),'y_lag2':float(hist.iloc[-2].yield_target_kg_ha),
       'y_roll3':float(last3.mean()),'y_std5':float(last5.std(ddof=0)),
       'y_slope3':float(np.polyfit(np.arange(3),last3.to_numpy(),1)[0]),
       'area_origin':float(hist.iloc[-1].cotton_area_000ha),
       'area_slope5':float(np.polyfit(np.arange(5),area5.to_numpy(),1)[0])}
    r.update(safe_weather(g,origin,target,scenario))
    return r

rows=[]
# Historical targets 2015-2024. This creates many genuine forecast-origin experiments.
for target in range(2015,2025):
  for h in range(1,8):
    origin=target-h
    if origin<2004: continue
    for d in DISTS:
      actual=df[(df.district==d)&(df.year==target)]
      r=row_for(d,target,h,'normal')
      if r is None or actual.empty: continue
      bundle=models[h]
      X=pd.DataFrame([r])[bundle['feature_cols']]
      pred=float(bundle['pipeline'].predict(X)[0])
      hist=df[(df.district==d)&(df.year<=origin)].sort_values('year')
      prev=float(hist.iloc[-1].yield_target_kg_ha)
      rows.append({'district':d,'target_year':target,'origin_year':origin,'horizon':h,'actual':float(actual.iloc[0].yield_target_kg_ha),'prediction_safe_normal':pred,'previous_year_baseline':prev})

res=pd.DataFrame(rows)
res.to_csv(OUT/'forecast_origin_safe_hindcast_predictions.csv',index=False)
summary=[]
for h,g in res.groupby('horizon'):
    summary.append({'horizon':int(h),'n':len(g),'model_mae':mean_absolute_error(g.actual,g.prediction_safe_normal),'model_rmse':mean_squared_error(g.actual,g.prediction_safe_normal)**0.5,'prev_year_mae':mean_absolute_error(g.actual,g.previous_year_baseline),'prev_year_rmse':mean_squared_error(g.actual,g.previous_year_baseline)**0.5,'origin_year_min':int(g.origin_year.min()),'origin_year_max':int(g.origin_year.max()),'target_year_min':int(g.target_year.min()),'target_year_max':int(g.target_year.max())})
s=pd.DataFrame(summary)
s.to_csv(OUT/'forecast_origin_safe_hindcast_summary.csv',index=False)
# Aggregate 2020-2024, horizons 3-7, closest to current 5-year-use case
sel=res[(res.target_year>=2020)&(res.horizon>=3)&(res.horizon<=7)].copy()
agg={'n':len(sel),'model_mae':mean_absolute_error(sel.actual,sel.prediction_safe_normal),'model_rmse':mean_squared_error(sel.actual,sel.prediction_safe_normal)**0.5,'prev_year_mae':mean_absolute_error(sel.actual,sel.previous_year_baseline),'prev_year_rmse':mean_squared_error(sel.actual,sel.previous_year_baseline)**0.5}
manifest={'method':'forecast-origin-safe hindcast audit using existing future horizon artifacts; weather proxy is expanding origin-only 10-year climatology with temperature trend and normal scenario','targets':'2015-2024','horizons':'1-7 where origin >= 2004','future_artifact_unchanged':True,'production_model_unchanged':True,'authoritative_dataset_unchanged':True,'five_year_slice_2020_2024_horizons_3_7':agg}
(OUT/'forecast_origin_safe_hindcast_manifest.json').write_text(json.dumps(manifest,indent=2))
print(s.to_string(index=False))
print('\n5-year slice 2020-2024, horizons 3-7:',agg)
