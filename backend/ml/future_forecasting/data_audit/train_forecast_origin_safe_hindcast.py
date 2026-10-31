from pathlib import Path
import numpy as np, pandas as pd, json
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / 'data' / 'vidarbha_cotton_model_ready_1997_2024.csv'
OUT = ROOT / 'backend' / 'ml' / 'future_forecasting' / 'data_audit'
df=pd.read_csv(DATA).sort_values(['district','year']).reset_index(drop=True)
DISTS=sorted(df.district.unique())
WEATHER_PREFIXES=("tmax_","tmin_","rainfall_","rainy_days_","heavy_rain_days_","max_5day_","max_dry_spell_")
WCOLS=[c for c in df.columns if c.startswith(WEATHER_PREFIXES) and 'anomaly' not in c]
ACOLS=[c for c in df.columns if c.endswith('_district_anomaly')]
FEATURES=['district','target_year','horizon','y_lag1','y_lag2','y_roll3','y_std5','y_slope3','area_origin','area_slope5']+WCOLS+ACOLS
TARGET='yield_target_kg_ha'

def safe_weather(g, origin, target):
    hist=g[g.year<=origin].sort_values('year'); recent=hist.tail(10); out={}
    for c in WCOLS: out[c]=float(recent[c].mean()) if recent[c].notna().any() else np.nan
    for c in [c for c in WCOLS if c.startswith(('tmax_','tmin_'))]:
        v=recent[['year',c]].dropna()
        if len(v)>=5:
            slope=np.polyfit(v.year.to_numpy(),v[c].to_numpy(),1)[0]
            out[c]=float(v[c].mean()+slope*(target-v.year.mean()))
    for c in ['rainfall_annual_mm','rainfall_monsoon_mm','rainfall_kharif_mm','rainy_days_annual','heavy_rain_days_annual','rainy_days_monsoon','heavy_rain_days_monsoon','rainy_days_kharif','heavy_rain_days_kharif','rainfall_max_1day_annual_mm','max_5day_rain_annual_mm','max_dry_spell_annual_days','rainfall_max_1day_monsoon_mm','max_5day_rain_monsoon_mm','max_dry_spell_monsoon_days','rainfall_max_1day_kharif_mm','max_5day_rain_kharif_mm','max_dry_spell_kharif_days']:
        pass
    for base in ['rainfall_monsoon_mm','rainfall_kharif_mm','tmax_kharif_mean_c','tmin_kharif_mean_c']:
        a=base+'_district_anomaly'
        if a in ACOLS: out[a]=float(out[base]-hist[base].mean())
    return out

def make_row(d,t,h):
    o=t-h; g=df[df.district==d].sort_values('year'); hist=g[g.year<=o]
    if len(hist)<5: return None
    l3=hist.tail(3)[TARGET]; l5=hist.tail(5)[TARGET]; a5=hist.tail(5)['cotton_area_000ha']
    r={'district':d,'target_year':t,'horizon':h,'y_lag1':hist.iloc[-1][TARGET],'y_lag2':hist.iloc[-2][TARGET], 'y_roll3':l3.mean(),'y_std5':l5.std(ddof=0),'y_slope3':np.polyfit(np.arange(3),l3.to_numpy(),1)[0], 'area_origin':hist.iloc[-1]['cotton_area_000ha'],'area_slope5':np.polyfit(np.arange(5),a5.to_numpy(),1)[0]}
    r.update(safe_weather(g,o,t)); return r

# Build all forecast-origin-safe rows. Every weather value for target t is derived only from <= origin.
rows=[]
for t in range(2009,2025):
    for h in range(1,8):
        if t-h<2004: continue
        for d in DISTS:
            r=make_row(d,t,h)
            actual=df[(df.district==d)&(df.year==t)]
            if r is not None and not actual.empty:
                r['actual']=float(actual.iloc[0][TARGET]); rows.append(r)
allr=pd.DataFrame(rows)
allr.to_csv(OUT/'forecast_origin_safe_feature_rows.csv',index=False)

# Strict rolling-origin evaluation on 2015-2024: for each target year, train only on earlier target years.
models={
 'Ridge':lambda:Pipeline([('prep',ColumnTransformer([('num',Pipeline([('imp',SimpleImputer(strategy='median')),('sc',StandardScaler())]),[c for c in FEATURES if c!='district']),('cat',OneHotEncoder(handle_unknown='ignore'),['district'])])),('model',Ridge(alpha=10.0))]),
 'RandomForest':lambda:Pipeline([('prep',ColumnTransformer([('num',SimpleImputer(strategy='median'),[c for c in FEATURES if c!='district']),('cat',OneHotEncoder(handle_unknown='ignore'),['district'])])),('model',RandomForestRegressor(n_estimators=50,max_depth=6,min_samples_leaf=2,random_state=42,n_jobs=4))]),
 'GradientBoosting':lambda:Pipeline([('prep',ColumnTransformer([('num',SimpleImputer(strategy='median'),[c for c in FEATURES if c!='district']),('cat',OneHotEncoder(handle_unknown='ignore'),['district'])])),('model',GradientBoostingRegressor(n_estimators=100,learning_rate=0.05,max_depth=3,random_state=42))])
}

test_years=range(2015,2025)
preds=[]
for h in range(1,8):
    for t in test_years:
        if t-h<2004: continue
        train=allr[(allr.target_year<t)&(allr.horizon==h)]
        test=allr[(allr.target_year==t)&(allr.horizon==h)]
        if len(train)<30 or test.empty: continue
        for name,mk in models.items():
            model=mk(); model.fit(train[FEATURES],train.actual)
            p=model.predict(test[FEATURES])
            for (_,tr),pred in zip(test.iterrows(),p):
                preds.append({'model':name,'horizon':h,'target_year':t,'origin_year':int(t-h),'district':tr.district,'actual':tr.actual,'prediction':float(pred),'previous_year_baseline':float(df[(df.district==tr.district)&(df.year<=t-h)].sort_values('year').iloc[-1][TARGET])})
pr=pd.DataFrame(preds)
pr.to_csv(OUT/'strict_forecast_origin_hindcast_predictions.csv',index=False)
summary=[]
for (h,name),g in pr.groupby(['horizon','model']):
    summary.append({'horizon':h,'model':name,'n':len(g),'mae_kg_ha':mean_absolute_error(g.actual,g.prediction),'rmse_kg_ha':mean_squared_error(g.actual,g.prediction)**0.5,'prev_year_mae_kg_ha':mean_absolute_error(g.actual,g.previous_year_baseline),'prev_year_rmse_kg_ha':mean_squared_error(g.actual,g.previous_year_baseline)**0.5})
s=pd.DataFrame(summary).sort_values(['horizon','mae_kg_ha'])
s.to_csv(OUT/'strict_forecast_origin_hindcast_summary.csv',index=False)
# 2020-2024 and h3-7 slice
sl=pr[(pr.target_year>=2020)&(pr.horizon.between(3,7))]
agg=[]
for name,g in sl.groupby('model'):
    agg.append({'model':name,'n':len(g),'mae_kg_ha':mean_absolute_error(g.actual,g.prediction),'rmse_kg_ha':mean_squared_error(g.actual,g.prediction)**0.5,'prev_year_mae_kg_ha':mean_absolute_error(g.actual,g.previous_year_baseline),'prev_year_rmse_kg_ha':mean_squared_error(g.actual,g.previous_year_baseline)**0.5})
pd.DataFrame(agg).to_csv(OUT/'strict_forecast_origin_hindcast_5year_slice.csv',index=False)
manifest={'evaluation':'strict expanding rolling-origin; each target year trained only on earlier target years; target-year weather replaced by origin-only 10-year climatology plus temperature trend','test_years':'2015-2024','horizons':'1-7','production_artifacts_modified':False,'authoritative_dataset_modified':False}
(OUT/'strict_forecast_origin_hindcast_manifest.json').write_text(json.dumps(manifest,indent=2))
print(s.to_string(index=False)); print('\n5-year slice'); print(pd.DataFrame(agg).to_string(index=False))
