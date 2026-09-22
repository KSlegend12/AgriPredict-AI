import React, { useEffect, useMemo, useState } from 'react';
import {
  AlertCircle,
  ArrowDownRight,
  ArrowLeft,
  ArrowRight,
  ArrowUpRight,
  BarChart3,
  Check,
  CheckCircle2,
  Database,
  History,
  MapPin,
  RefreshCw,
  ShieldCheck,
  Sparkles,
} from 'lucide-react';

import {
  getCottonHistory,
  getCottonPredictionInput,
  getCottonWeather,
  predictCottonYield,
} from '../services/api';

const VIDARBHA_DISTRICTS = [
  'Akola', 'Amravati', 'Buldhana', 'Nagpur', 'Wardha', 'Washim', 'Yavatmal',
];

const PREDICTION_YEARS = Array.from({ length: 28 }, (_, i) => 1997 + i);

function MetricRow({ label, value, valueClass = 'text-slate-900' }) {
  return (
    <div className="flex justify-between gap-4 border-b border-slate-100 pb-2 last:border-b-0">
      <span className="text-slate-500">{label}</span>
      <span className={`font-bold text-right ${valueClass}`}>{value}</span>
    </div>
  );
}

function ContributionBar({ item }) {
  const value = Number(item?.contribution_kg_ha ?? 0);
  const positive = value >= 0;
  const width = Math.min(100, (Math.abs(value) / 150) * 100);

  return (
    <div className="space-y-1.5">
      <div className="flex justify-between gap-3 text-xs">
        <span className="text-slate-700 font-medium">{item?.display_name || item?.feature}</span>
        <span className={`font-mono font-bold ${positive ? 'text-emerald-700' : 'text-rose-600'}`}>
          {positive ? '+' : ''}{value.toFixed(2)} kg/ha
        </span>
      </div>
      <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full ${positive ? 'bg-emerald-600' : 'bg-rose-500'}`}
          style={{ width: `${width}%` }}
        />
      </div>
    </div>
  );
}

export default function CottonYieldPage({ selectedDistrict, setSelectedDistrict }) {
  const initialDistrict = VIDARBHA_DISTRICTS.includes(selectedDistrict) ? selectedDistrict : 'Akola';

  const [district, setDistrict] = useState(initialDistrict);
  const [year, setYear] = useState(2024);
  const [activeStep, setActiveStep] = useState(1);
  const [inputData, setInputData] = useState(null);
  const [weatherData, setWeatherData] = useState(null);
  const [historyData, setHistoryData] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loadingInput, setLoadingInput] = useState(false);
  const [isPredicting, setIsPredicting] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  const loadVerifiedData = async () => {
    setLoadingInput(true);
    setErrorMessage(null);
    setPrediction(null);
    try {
      const [input, weather, history] = await Promise.all([
        getCottonPredictionInput(district, year),
        getCottonWeather(district, year),
        getCottonHistory(district),
      ]);
      setInputData(input);
      setWeatherData(weather);
      setHistoryData(history);
      setActiveStep(2);
    } catch (err) {
      setInputData(null);
      setWeatherData(null);
      setHistoryData(null);
      setErrorMessage(err?.response?.data?.detail || 'Verified data could not be loaded.');
    } finally {
      setLoadingInput(false);
    }
  };

  useEffect(() => {
    setInputData(null);
    setWeatherData(null);
    setHistoryData(null);
    setPrediction(null);
    setErrorMessage(null);
    setActiveStep(1);
  }, [district]);

  const handleDistrict = (value) => {
    setDistrict(value);
    setSelectedDistrict?.(value);
  };

  const handlePredict = async () => {
    if (!inputData) return;
    setIsPredicting(true);
    setErrorMessage(null);
    try {
      const response = await predictCottonYield({ district, target_year: year });
      setPrediction(response);
      setActiveStep(5);
    } catch (err) {
      setErrorMessage(err?.response?.data?.detail || 'Unable to generate prediction.');
      setActiveStep(4);
    } finally {
      setIsPredicting(false);
    }
  };

  const featureCount = useMemo(() => Object.keys(inputData?.features || {}).length, [inputData]);
  const explanation = prediction?.explanation;
  const validation = prediction?.validation_context || {};

  const weather = weatherData?.weather || {};
  const history = historyData?.records || [];
  const lastThree = history.filter((r) => r.year < year).slice(-3);

  return (
    <div className="space-y-6 py-4 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-slate-200 pb-4 gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md bg-emerald-50 text-emerald-800 border border-emerald-200 text-xs font-semibold uppercase tracking-wider mb-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            Vidarbha Cotton Yield Intelligence
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">Cotton Yield Prediction</h1>
          <p className="text-xs text-slate-500">Verified historical weather + agricultural features → validated GradientBoosting model.</p>
        </div>
        <div className="flex items-center gap-2 font-mono text-xs">
          <span className="px-3 py-1 bg-white text-slate-800 border border-slate-300 rounded-md font-semibold">
            {district}, Vidarbha · {year}
          </span>
        </div>
      </div>

      <div className="agri-card p-3 border border-slate-200 shadow-xs">
        <div className="flex items-center justify-between max-w-5xl mx-auto overflow-x-auto">
          {[
            ['01', 'District'], ['02', 'Verified Data'], ['03', 'History'], ['04', 'Review'], ['05', 'Prediction & Explanation'],
          ].map(([num, label], index) => {
            const n = index + 1;
            const active = activeStep === n;
            const done = activeStep > n;
            return (
              <React.Fragment key={num}>
                <button
                  type="button"
                  onClick={() => n === 1 || (n > 1 && inputData) ? setActiveStep(n) : null}
                  className="flex items-center gap-2 shrink-0 py-1 px-2.5 rounded-md hover:bg-slate-50"
                >
                  <div className={`w-6 h-6 rounded-md flex items-center justify-center font-mono font-bold text-xs ${active ? 'bg-emerald-600 text-white' : done ? 'bg-emerald-100 text-emerald-800 border border-emerald-300' : 'bg-slate-100 text-slate-500 border border-slate-200'}`}>
                    {done ? <Check className="w-3.5 h-3.5" /> : num}
                  </div>
                  <span className={`text-xs whitespace-nowrap ${active ? 'text-slate-900 font-bold' : 'text-slate-500'}`}>{label}</span>
                </button>
                {index < 4 && <div className={`h-0.5 flex-1 min-w-[16px] mx-1 ${activeStep > n ? 'bg-emerald-500' : 'bg-slate-200'}`} />}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {errorMessage && (
        <div className="p-4 rounded-md bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-rose-600" />
          <div><strong className="block">Prediction Error</strong>{errorMessage}</div>
        </div>
      )}

      {activeStep === 5 && prediction ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          <div className="lg:col-span-4 space-y-5">
            <div className="agri-card p-5 border border-emerald-200 bg-emerald-50/40 space-y-3">
              <div className="flex items-center gap-2 text-emerald-800 font-bold text-xs uppercase tracking-wider">
                <CheckCircle2 className="w-4 h-4" /> Prediction Generated
              </div>
              <div className="text-4xl font-extrabold text-slate-900">{Number(prediction.predicted_yield_kg_ha).toFixed(1)} <span className="text-sm font-semibold text-slate-500">kg/ha</span></div>
              <p className="text-xs text-slate-600">{district} · {year} · {prediction.prediction_status?.replaceAll('_', ' ')}</p>
              <button type="button" onClick={() => setActiveStep(1)} className="w-full py-2.5 rounded-md bg-white border border-slate-300 text-slate-700 font-semibold text-xs flex items-center justify-center gap-2">
                <ArrowLeft className="w-4 h-4" /> Modify Selection
              </button>
            </div>

            <div className="agri-card p-5 border border-slate-200 space-y-3">
              <div className="flex items-center gap-2 font-bold text-xs uppercase tracking-wider text-slate-800"><Database className="w-4 h-4 text-emerald-600" /> Data Provenance</div>
              <MetricRow label="Dataset" value="Model-ready panel" />
              <MetricRow label="Prediction year" value={year} />
              <MetricRow label="Features supplied" value={featureCount} />
              <MetricRow label="Training period" value={validation.training_period || '1997–2023'} />
              <MetricRow label="Final holdout" value="2024" />
            </div>
          </div>

          <div className="lg:col-span-8 space-y-5">
            <div className="agri-card p-5 border border-slate-200 space-y-4">
              <div className="flex items-center gap-2"><Sparkles className="w-5 h-5 text-emerald-600" /><h2 className="font-bold text-slate-900">Why did the model produce this estimate?</h2></div>
              <p className="text-xs text-slate-600">{explanation?.summary_text || 'SHAP explanation unavailable.'}</p>
              <div className="grid md:grid-cols-2 gap-5">
                <div className="space-y-3"><h3 className="text-xs font-bold text-emerald-800 flex items-center gap-1"><ArrowUpRight className="w-4 h-4" /> Increasing factors</h3>{(explanation?.increasing_factors || []).map((x) => <ContributionBar key={x.feature} item={x} />)}</div>
                <div className="space-y-3"><h3 className="text-xs font-bold text-rose-700 flex items-center gap-1"><ArrowDownRight className="w-4 h-4" /> Decreasing factors</h3>{(explanation?.decreasing_factors || []).map((x) => <ContributionBar key={x.feature} item={x} />)}</div>
              </div>
            </div>

            <div className="agri-card p-5 border border-slate-200 space-y-4">
              <div className="flex items-center gap-2"><BarChart3 className="w-5 h-5 text-emerald-600" /><h2 className="font-bold text-slate-900">Validation context</h2></div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                <MetricRow label="CV MAE" value={`${validation.mean_mae_kg_ha ?? '—'} kg/ha`} />
                <MetricRow label="CV RMSE" value={`${prediction.validation_metrics?.Mean_RMSE_kg_ha ?? '—'} kg/ha`} />
                <MetricRow label="CV MAPE" value={`${prediction.validation_metrics?.Mean_MAPE_percent ?? '—'}%`} />
                <MetricRow label="2024 holdout MAE" value={`${validation.holdout_mae_kg_ha ?? '—'} kg/ha`} />
              </div>
              <p className="text-[11px] text-slate-500">These are validation metrics, not a confidence interval. 2024 remains the final untouched evaluation holdout.</p>
            </div>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          <div className="lg:col-span-7 agri-card p-6 border border-slate-200 shadow-xs space-y-5">
            {activeStep === 1 && (
              <div className="space-y-5">
                <div className="flex items-center justify-between border-b border-slate-100 pb-2"><span className="text-[10px] font-mono font-bold uppercase tracking-widest text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200">STEP 01 / 05</span><MapPin className="w-4 h-4 text-slate-400" /></div>
                <h2 className="text-xl font-bold text-slate-900">Select District & Prediction Year</h2>
                <p className="text-xs text-slate-500">The backend will fetch the complete model-ready feature row from the authoritative Vidarbha cotton panel. No synthetic weather values are created.</p>
                <div className="grid sm:grid-cols-2 gap-2">
                  {VIDARBHA_DISTRICTS.map((item) => (
                    <button key={item} type="button" onClick={() => handleDistrict(item)} className={`p-3 rounded-lg border text-left font-semibold text-xs flex items-center justify-between ${district === item ? 'bg-emerald-50 border-emerald-500 text-emerald-950' : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'}`}>
                      <span>{item} District</span><span className="text-[10px] text-slate-400">Vidarbha</span>
                    </button>
                  ))}
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1.5">Target Year</label>
                  <select value={year} onChange={(e) => setYear(Number(e.target.value))} className="w-full bg-white border border-slate-200 rounded-md px-3 py-2.5 text-sm font-semibold">
                    {PREDICTION_YEARS.map((y) => <option key={y} value={y}>{y}{y === 2024 ? ' — final holdout' : ''}</option>)}
                  </select>
                  <p className="text-[10px] text-slate-400 mt-1">Currently verified model-ready historical years: 1997–2024.</p>
                </div>
                <button type="button" onClick={loadVerifiedData} disabled={loadingInput} className="w-full py-3 rounded-md bg-emerald-600 hover:bg-emerald-500 disabled:bg-emerald-300 text-white font-semibold text-xs flex items-center justify-center gap-2">
                  {loadingInput ? <><RefreshCw className="w-4 h-4 animate-spin" /> Loading verified data…</> : <>Load Verified Data <ArrowRight className="w-4 h-4" /></>}
                </button>
              </div>
            )}

            {activeStep === 2 && inputData && (
              <div className="space-y-5">
                <div className="flex items-center justify-between border-b border-slate-100 pb-2"><span className="text-[10px] font-mono font-bold uppercase tracking-widest text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200">STEP 02 / 05</span><span className="text-xs text-slate-500 font-mono">VERIFIED WEATHER</span></div>
                <h2 className="text-xl font-bold text-slate-900">Verified Weather & Area</h2>
                <div className="p-3 rounded-md bg-emerald-50 border border-emerald-200 text-emerald-900 text-[11px]"><strong>Source:</strong> {inputData.source?.dataset}. Values below are read-only model inputs; nothing is estimated in the frontend.</div>
                <div className="grid sm:grid-cols-2 gap-3">
                  <MetricRow label="Cotton area" value={`${Number(inputData.features.cotton_area_000ha).toFixed(2)} 000 ha`} valueClass="text-emerald-700" />
                  <MetricRow label="Annual rainfall" value={`${Number(weather.rainfall_annual_mm).toFixed(1)} mm`} valueClass="text-teal-700" />
                  <MetricRow label="Kharif rainfall" value={`${Number(weather.rainfall_kharif_mm).toFixed(1)} mm`} />
                  <MetricRow label="Monsoon rainfall" value={`${Number(weather.rainfall_monsoon_mm).toFixed(1)} mm`} />
                  <MetricRow label="Annual mean Tmax" value={`${Number(weather.tmax_annual_mean_c).toFixed(1)} °C`} />
                  <MetricRow label="Kharif mean Tmax" value={`${Number(weather.tmax_kharif_mean_c).toFixed(1)} °C`} />
                  <MetricRow label="Annual mean Tmin" value={`${Number(weather.tmin_annual_mean_c).toFixed(1)} °C`} />
                  <MetricRow label="Max dry spell" value={`${Number(weather.max_dry_spell_annual_days).toFixed(0)} days`} />
                  <MetricRow label="Rainy days" value={`${Number(weather.rainy_days_annual).toFixed(0)}`} />
                  <MetricRow label="Heavy rain days" value={`${Number(weather.heavy_rain_days_annual).toFixed(0)}`} />
                </div>
                <div className="flex gap-2"><button type="button" onClick={() => setActiveStep(1)} className="w-1/3 py-2.5 rounded-md bg-slate-100 text-slate-700 text-xs">Back</button><button type="button" onClick={() => setActiveStep(3)} className="w-2/3 py-2.5 rounded-md bg-emerald-600 text-white font-semibold text-xs flex items-center justify-center gap-2">View Historical Features <ArrowRight className="w-4 h-4" /></button></div>
              </div>
            )}

            {activeStep === 3 && inputData && (
              <div className="space-y-5">
                <div className="flex items-center justify-between border-b border-slate-100 pb-2"><span className="text-[10px] font-mono font-bold uppercase tracking-widest text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200">STEP 03 / 05</span><History className="w-4 h-4 text-slate-400" /></div>
                <h2 className="text-xl font-bold text-slate-900">Automatic Historical Yield Features</h2>
                <p className="text-xs text-slate-500">Lag features are calculated from recorded yields before the selected year. You do not enter them manually.</p>
                <div className="grid sm:grid-cols-3 gap-3">
                  <div className="p-4 bg-slate-50 border border-slate-200 rounded-md"><div className="text-[10px] text-slate-500">Previous year</div><div className="text-lg font-bold">{inputData.features.previous_year_yield_kg_ha == null ? 'Imputed' : `${Number(inputData.features.previous_year_yield_kg_ha).toFixed(1)} kg/ha`}</div></div>
                  <div className="p-4 bg-slate-50 border border-slate-200 rounded-md"><div className="text-[10px] text-slate-500">Previous 2-year</div><div className="text-lg font-bold">{inputData.features.previous_2year_yield_kg_ha == null ? 'Imputed' : `${Number(inputData.features.previous_2year_yield_kg_ha).toFixed(1)} kg/ha`}</div></div>
                  <div className="p-4 bg-slate-50 border border-slate-200 rounded-md"><div className="text-[10px] text-slate-500">3-year rolling</div><div className="text-lg font-bold">{inputData.features.rolling_3yr_yield_mean_kg_ha == null ? 'Imputed' : `${Number(inputData.features.rolling_3yr_yield_mean_kg_ha).toFixed(1)} kg/ha`}</div></div>
                </div>
                <div className="p-3 rounded-md bg-blue-50 border border-blue-200 text-blue-800 text-[11px]">{lastThree.length ? `Recorded yields available before ${year}: ${lastThree.map((r) => `${r.year}: ${Number(r.yield_kg_ha).toFixed(1)} kg/ha`).join(' · ')}` : 'Early years may have missing lag values; the model pipeline handles those using training-time preprocessing.'}</div>
                <div className="flex gap-2"><button type="button" onClick={() => setActiveStep(2)} className="w-1/3 py-2.5 rounded-md bg-slate-100 text-slate-700 text-xs">Back</button><button type="button" onClick={() => setActiveStep(4)} className="w-2/3 py-2.5 rounded-md bg-emerald-600 text-white font-semibold text-xs flex items-center justify-center gap-2">Review <ArrowRight className="w-4 h-4" /></button></div>
              </div>
            )}

            {activeStep === 4 && inputData && (
              <div className="space-y-5">
                <div className="flex items-center justify-between border-b border-slate-100 pb-2"><span className="text-[10px] font-mono font-bold uppercase tracking-widest text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200">STEP 04 / 05</span><span className="text-xs text-slate-500 font-mono">REVIEW</span></div>
                <h2 className="text-xl font-bold text-slate-900">Review Verified Model Inputs</h2>
                <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 space-y-2 text-xs font-mono">
                  <MetricRow label="District" value={district} /><MetricRow label="Target year" value={year} /><MetricRow label="Feature count" value={`${featureCount} model features`} /><MetricRow label="Area" value={`${Number(inputData.features.cotton_area_000ha).toFixed(2)} 000 ha`} /><MetricRow label="Annual rainfall" value={`${Number(inputData.features.rainfall_annual_mm).toFixed(1)} mm`} /><MetricRow label="3-year rolling yield" value={inputData.features.rolling_3yr_yield_mean_kg_ha == null ? 'Training-time imputation' : `${Number(inputData.features.rolling_3yr_yield_mean_kg_ha).toFixed(1)} kg/ha`} />
                </div>
                <div className="p-3 rounded-md bg-blue-50 border border-blue-200 text-blue-800 text-[11px] leading-relaxed"><strong>Important:</strong> The target yield is excluded from the prediction input. For 2024, this is the model's final untouched holdout year.</div>
                <div className="flex gap-2"><button type="button" onClick={() => setActiveStep(3)} className="w-1/3 py-2.5 rounded-md bg-slate-100 text-slate-700 text-xs">Back</button><button type="button" onClick={handlePredict} disabled={isPredicting} className="w-2/3 py-3 rounded-md bg-emerald-600 disabled:bg-emerald-300 text-white font-semibold text-xs flex items-center justify-center gap-2">{isPredicting ? <><RefreshCw className="w-4 h-4 animate-spin" /> Predicting…</> : <>Generate Prediction <Sparkles className="w-4 h-4" /></>}</button></div>
              </div>
            )}
          </div>

          <div className="lg:col-span-5 space-y-5">
            <div className="agri-card p-5 border border-slate-200 space-y-4">
              <div className="flex items-center gap-2"><Database className="w-5 h-5 text-emerald-600" /><h2 className="font-bold text-slate-900">How this version works</h2></div>
              <ul className="space-y-3 text-xs text-slate-600">
                <li>✓ Select district and year.</li><li>✓ Backend reads the exact verified model-ready row.</li><li>✓ Weather and lag features are no longer invented by the frontend.</li><li>✓ The target yield is excluded before prediction.</li><li>✓ The existing validated GradientBoosting model and SHAP explanation are reused.</li>
              </ul>
            </div>
            <div className="agri-card p-5 border border-slate-200 space-y-3">
              <div className="flex items-center gap-2"><BarChart3 className="w-5 h-5 text-emerald-600" /><h2 className="font-bold text-slate-900">Selected data</h2></div>
              <MetricRow label="District" value={district} />
              <MetricRow label="Year" value={year} />
              <MetricRow label="Verified data loaded" value={inputData ? 'Yes' : 'No'} valueClass={inputData ? 'text-emerald-700' : 'text-slate-500'} />
              {weatherData && <MetricRow label="Annual rainfall" value={`${Number(weather.rainfall_annual_mm).toFixed(1)} mm`} />}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
