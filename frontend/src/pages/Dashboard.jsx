import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, ArrowRight, BarChart3, BrainCircuit, CheckCircle2, CloudRain, Database, Droplets, Gauge, Leaf, MapPin, Satellite, ShieldCheck, Sparkles, Thermometer, TrendingUp } from 'lucide-react';
import { getHealth, getCottonHistory, getCottonPredictionInput } from '../services/api';
import { LineChart, Line, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid, AreaChart, Area } from 'recharts';

const DISTRICTS = ['Akola', 'Amravati', 'Buldhana', 'Nagpur', 'Wardha', 'Washim', 'Yavatmal'];
const FALLBACK = { validationMAE: 106.1784, validationRMSE: 126.6537, validationR2: -1.5769, validationMAPE: 38.1557, holdoutMAE: 230.7527, holdoutRMSE: 321.4472, holdoutR2: -0.636, holdoutMAPE: 41.6921 };

export default function Dashboard({ selectedDistrict = 'Akola', setSelectedDistrict }) {
  const navigate = useNavigate();
  const [district, setDistrict] = useState(selectedDistrict || 'Akola');
  const [health, setHealth] = useState(null);
  const [history, setHistory] = useState(null);
  const [weather, setWeather] = useState(null);

  useEffect(() => { if (setSelectedDistrict) setSelectedDistrict(district); }, [district, setSelectedDistrict]);
  useEffect(() => { getHealth().then(setHealth); }, []);
  useEffect(() => {
    Promise.allSettled([getCottonHistory(district), getCottonPredictionInput(district, 2024)]).then(([h, w]) => {
      if (h.status === 'fulfilled') setHistory(h.value);
      if (w.status === 'fulfilled') setWeather(w.value);
    });
  }, [district]);

  const rows = useMemo(() => normalizeHistory(history), [history]);
  const latest = rows.at(-1);
  const metrics = extractMetrics(health);

  return (
    <div className="space-y-6">
      <section className="rounded-[28px] bg-white border border-slate-200 p-6 sm:p-8 shadow-sm">
        <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full bg-emerald-50 px-3 py-1.5 text-[10px] font-extrabold uppercase tracking-[0.18em] text-emerald-700"><Activity className="h-3.5 w-3.5" /> Live project dashboard</div>
            <h1 className="mt-4 text-3xl sm:text-4xl font-black tracking-tight">Agricultural intelligence at a glance.</h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">Monitor model readiness, historical cotton performance and the evidence behind AgriPredictAI.</p>
          </div>
          <div className="flex flex-wrap gap-3">
            <label className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3"><span className="block text-[10px] font-extrabold uppercase tracking-widest text-slate-400">District</span><select value={district} onChange={e => setDistrict(e.target.value)} className="mt-1 bg-transparent text-sm font-black outline-none">{DISTRICTS.map(d => <option key={d}>{d}</option>)}</select></label>
            <button onClick={() => navigate('/cotton')} className="self-stretch rounded-2xl bg-emerald-600 px-5 text-xs font-extrabold text-white hover:bg-emerald-700 transition inline-flex items-center gap-2">Predict <ArrowRight className="h-4 w-4" /></button>
          </div>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Kpi icon={MapPin} label="Study area" value="7 districts" note="Vidarbha" />
        <Kpi icon={Database} label="Historical data" value="1997–2024" note="194 observations" />
        <Kpi icon={BrainCircuit} label="ML model" value="Gradient Boosting" note="final model" />
        <Kpi icon={ShieldCheck} label="Holdout" value="2024" note="kept separate" />
      </section>

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Score label="Validation MAE" value={`${metrics.validationMAE.toFixed(2)} kg/ha`} sub="2011–2023 expanding window" />
        <Score label="Validation RMSE" value={`${metrics.validationRMSE.toFixed(2)} kg/ha`} sub="2011–2023 expanding window" />
        <Score label="2024 Holdout MAE" value={`${metrics.holdoutMAE.toFixed(2)} kg/ha`} sub="final untouched holdout" />
        <Score label="2024 Holdout MAPE" value={`${metrics.holdoutMAPE.toFixed(2)}%`} sub="final untouched holdout" />
      </section>

      <section className="grid gap-6 lg:grid-cols-[1.25fr_.75fr]">
        <div className="agri-card p-6">
          <div className="flex items-start justify-between gap-4"><div><p className="text-[10px] font-extrabold uppercase tracking-[0.18em] text-emerald-600">Historical signal</p><h2 className="mt-1 text-lg font-black">{district} cotton yield</h2><p className="mt-1 text-xs text-slate-500">Recorded annual yield · kg/ha</p></div><TrendingUp className="h-5 w-5 text-emerald-600" /></div>
          <div className="mt-5 h-72">{rows.length ? <ResponsiveContainer width="100%" height="100%"><LineChart data={rows} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}><CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" /><XAxis dataKey="year" fontSize={11} tickLine={false} /><YAxis fontSize={11} tickLine={false} /><Tooltip formatter={v => [`${Number(v).toFixed(1)} kg/ha`, 'Yield']} /><Line type="monotone" dataKey="yield" stroke="#059669" strokeWidth={3} dot={false} activeDot={{ r: 5 }} /></LineChart></ResponsiveContainer> : <EmptyChart />}</div>
        </div>

        <div className="agri-card p-6">
          <p className="text-[10px] font-extrabold uppercase tracking-[0.18em] text-emerald-600">Latest available record</p>
          <h2 className="mt-1 text-lg font-black">{district}</h2>
          <div className="mt-5 space-y-3">
            <InfoRow icon={Leaf} label="Yield" value={latest ? `${latest.yield.toFixed(1)} kg/ha` : '—'} />
            <InfoRow icon={CloudRain} label="Rainfall" value={weather?.features?.rainfall_annual != null ? `${Number(weather.features.rainfall_annual).toFixed(0)} mm` : 'Model input'} />
            <InfoRow icon={Thermometer} label="Temperature" value={weather?.features?.tmax_annual_mean_c != null ? `${Number(weather.features.tmax_annual_mean_c).toFixed(1)} °C` : 'Model input'} />
            <InfoRow icon={Gauge} label="Model status" value="Ready" green />
          </div>
          <button onClick={() => navigate('/history')} className="mt-6 w-full rounded-xl border border-slate-200 py-3 text-xs font-extrabold text-slate-700 hover:bg-slate-50">Explore full history</button>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <Quick icon={Sparkles} title="Run a prediction" text="Use verified district inputs and automatic historical lag features." action="Open Prediction" onClick={() => navigate('/cotton')} />
        <Quick icon={Satellite} title="Inspect satellite stack" text="Track MODIS, SMAP and vegetation/productivity datasets." action="View Satellite Data" onClick={() => navigate('/satellite')} />
        <Quick icon={BrainCircuit} title="Explain the model" text="Review validation, holdout performance and SHAP contributions." action="Open Insights" onClick={() => navigate('/insights')} />
      </section>
    </div>
  );
}

function Kpi({ icon: Icon, label, value, note }) { return <div className="agri-card p-5"><div className="flex items-center justify-between"><div className="h-9 w-9 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center"><Icon className="h-4 w-4" /></div><span className="text-[10px] font-bold text-slate-400">{note}</span></div><div className="mt-4 text-xl font-black">{value}</div><div className="mt-1 text-xs font-semibold text-slate-500">{label}</div></div>; }
function Score({ label, value, sub }) { return <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5"><div className="text-[10px] font-extrabold uppercase tracking-widest text-slate-400">{label}</div><div className="mt-2 text-xl font-black font-mono text-slate-900">{value}</div><div className="mt-1 text-[10px] text-slate-500">{sub}</div></div>; }
function InfoRow({ icon: Icon, label, value, green }) { return <div className="flex items-center justify-between rounded-xl bg-slate-50 px-3 py-3"><span className="inline-flex items-center gap-2 text-xs font-semibold text-slate-500"><Icon className="h-4 w-4 text-emerald-600" />{label}</span><span className={`text-xs font-extrabold ${green ? 'text-emerald-700' : 'text-slate-800'}`}>{value}</span></div>; }
function Quick({ icon: Icon, title, text, action, onClick }) { return <div className="agri-card agri-card-hover p-5"><div className="h-10 w-10 rounded-xl bg-slate-950 text-white flex items-center justify-center"><Icon className="h-5 w-5" /></div><h3 className="mt-4 text-sm font-extrabold">{title}</h3><p className="mt-2 min-h-10 text-xs leading-5 text-slate-500">{text}</p><button onClick={onClick} className="mt-4 inline-flex items-center gap-1 text-xs font-extrabold text-emerald-700">{action} <ArrowRight className="h-3.5 w-3.5" /></button></div>; }
function EmptyChart() { return <div className="h-full flex items-center justify-center rounded-2xl bg-slate-50 text-xs font-semibold text-slate-400">History unavailable from backend</div>; }
function normalizeHistory(data) { const raw = data?.history || data?.records || data?.data || []; return Array.isArray(raw) ? raw.map(x => ({ year: Number(x.year ?? x.Year), yield: Number(x.yield_kg_ha ?? x.yield ?? x.productivity_kg_ha ?? x.value) })).filter(x => Number.isFinite(x.year) && Number.isFinite(x.yield)).sort((a,b)=>a.year-b.year) : []; }
function extractMetrics(data) { const c = data?.cotton || data?.metrics || {}; return { validationMAE: Number(c?.validation_metrics?.mae ?? c?.validation_mae ?? FALLBACK.validationMAE), validationRMSE: Number(c?.validation_metrics?.rmse ?? c?.validation_rmse ?? FALLBACK.validationRMSE), validationR2: Number(c?.validation_metrics?.r2 ?? FALLBACK.validationR2), validationMAPE: Number(c?.validation_metrics?.mape ?? FALLBACK.validationMAPE), holdoutMAE: Number(c?.holdout_2024_metrics?.mae ?? c?.holdout_mae ?? FALLBACK.holdoutMAE), holdoutRMSE: Number(c?.holdout_2024_metrics?.rmse ?? c?.holdout_rmse ?? FALLBACK.holdoutRMSE), holdoutR2: Number(c?.holdout_2024_metrics?.r2 ?? FALLBACK.holdoutR2), holdoutMAPE: Number(c?.holdout_2024_metrics?.mape ?? c?.holdout_mape ?? FALLBACK.holdoutMAPE) }; }
