import React, { useEffect, useState } from 'react';
import { BarChart3, BrainCircuit, CheckCircle2, Clock3, Database, GitBranch, Info, ShieldCheck, Target, TrendingDown, TrendingUp } from 'lucide-react';
import { getCottonModelInfo } from '../services/api';
import { BarChart, Bar, ResponsiveContainer, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

const validation = { mae: 106.1784, rmse: 126.6537, r2: -1.5769, mape: 38.1557 };
const holdout = { mae: 230.7527, rmse: 321.4472, r2: -0.636, mape: 41.6921 };
const baseline = { previous: 189.8643, historical: 281.183 };
const features = [
  { name: 'Rolling 3-year yield mean', value: 144.70 },
  { name: 'Minimum temperature', value: 25.69 },
  { name: 'Maximum temperature', value: 12.98 },
  { name: 'Annual mean temperature', value: 8.75 },
  { name: 'Annual rainfall', value: 8.15 },
];

export default function ModelInsightsPage() {
  const [info, setInfo] = useState(null);
  useEffect(() => { getCottonModelInfo().then(setInfo); }, []);
  const modelName = info?.model_name || info?.model || 'GradientBoostingRegressor';

  const chartFeatures = (info?.global_shap_importance?.top_10_features || []).length > 0
    ? info.global_shap_importance.top_10_features.slice(0, 8).map(f => ({
        name: f.display_name?.length > 25 ? `${f.display_name.slice(0, 23)}…` : f.display_name,
        value: Number(f.mean_abs_shap_kg_ha)
      }))
    : features;

  return (
    <div className="space-y-6">
      <Hero />

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Metric label="Validation MAE" value={`${validation.mae.toFixed(2)} kg/ha`} note="2011–2023" icon={Target} />
        <Metric label="Validation RMSE" value={`${validation.rmse.toFixed(2)} kg/ha`} note="2011–2023" icon={BarChart3} />
        <Metric label="2024 Holdout MAE" value={`${holdout.mae.toFixed(2)} kg/ha`} note="untouched holdout" icon={ShieldCheck} />
        <Metric label="2024 Holdout MAPE" value={`${holdout.mape.toFixed(2)}%`} note="untouched holdout" icon={TrendingDown} />
      </section>

      <section className="grid gap-6 lg:grid-cols-[.8fr_1.2fr]">
        <div className="agri-card p-6 sm:p-7">
          <div className="flex items-center gap-3"><div className="h-11 w-11 rounded-2xl bg-emerald-50 text-emerald-700 flex items-center justify-center"><BrainCircuit className="h-5 w-5" /></div><div><p className="text-[10px] font-extrabold uppercase tracking-widest text-emerald-600">Selected model</p><h2 className="text-lg font-black">{modelName}</h2></div></div>
          <div className="mt-6 grid gap-3">
            <Param label="n_estimators" value="100" />
            <Param label="learning_rate" value="0.05" />
            <Param label="max_depth" value="3" />
            <Param label="random_state" value="42" />
          </div>
          <div className="mt-5 rounded-2xl bg-slate-50 p-4 text-xs leading-5 text-slate-600"><b className="text-slate-900">Training:</b> 1997–2023 · <b className="text-slate-900">Final holdout:</b> 2024 · chronological evaluation.</div>
        </div>

        <div className="agri-card p-6 sm:p-7">
          <div className="flex items-end justify-between gap-4"><div><p className="text-[10px] font-extrabold uppercase tracking-widest text-emerald-600">Explainability</p><h2 className="mt-1 text-lg font-black">Global feature contribution</h2><p className="mt-1 text-xs text-slate-500">Mean absolute SHAP value on the 2024 holdout.</p></div><Info className="h-4 w-4 text-slate-400" /></div>
          <div className="mt-5 h-72"><ResponsiveContainer width="100%" height="100%"><BarChart data={chartFeatures} layout="vertical" margin={{ top: 5, right: 15, left: 10, bottom: 5 }}><CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" /><XAxis type="number" fontSize={10} /><YAxis type="category" dataKey="name" width={155} fontSize={10} tickLine={false} /><Tooltip formatter={(v) => [Number(v).toFixed(2), 'Mean |SHAP|']} /><Bar dataKey="value" fill="#059669" radius={[0, 5, 5, 0]} /></BarChart></ResponsiveContainer></div>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <Performance title="2011–2023 expanding-window validation" data={validation} badge="Validation" />
        <Performance title="2024 final holdout" data={holdout} badge="Holdout" />
      </section>

      <section className="agri-card p-6 sm:p-7">
        <div className="flex items-center gap-3"><div className="h-10 w-10 rounded-xl bg-slate-950 text-white flex items-center justify-center"><GitBranch className="h-5 w-5" /></div><div><h2 className="text-lg font-black">Baseline context</h2><p className="text-xs text-slate-500">The 2024 holdout is interpreted alongside simple baselines.</p></div></div>
        <div className="mt-5 grid gap-3 md:grid-cols-3"><Compare label="Gradient Boosting" value={holdout.mae} tone="green" /><Compare label="Previous-year baseline" value={baseline.previous} tone="slate" /><Compare label="Historical-mean baseline" value={baseline.historical} tone="slate" /></div>
        <p className="mt-5 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-xs leading-5 text-amber-800"><b>Interpretation:</b> the selected model improves on the historical-mean baseline for the 2024 holdout, but its 2024 MAE is higher than the previous-year baseline. This is reported transparently rather than converted into an “accuracy” score.</p>
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-5 flex items-start gap-3"><Clock3 className="mt-0.5 h-5 w-5 text-emerald-600" /><div><h3 className="text-sm font-extrabold">Why chronological validation?</h3><p className="mt-1 text-xs leading-5 text-slate-500">Agricultural forecasting is time-dependent. The project keeps 2024 untouched as the final holdout instead of randomly mixing future observations into training.</p></div></section>
    </div>
  );
}

function Hero() { return <section className="rounded-[28px] bg-slate-950 p-7 sm:p-9 text-white"><div className="inline-flex items-center gap-2 rounded-full bg-emerald-400/10 px-3 py-1.5 text-[10px] font-extrabold uppercase tracking-[0.18em] text-emerald-300"><BrainCircuit className="h-3.5 w-3.5" /> Model transparency</div><h1 className="mt-4 text-3xl sm:text-4xl font-black tracking-tight">Model Insights & Explainability</h1><p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">A presentation-ready view of the selected Gradient Boosting model, its chronological validation, final 2024 holdout and SHAP feature contributions.</p></section>; }
function Metric({ label, value, note, icon: Icon }) { return <div className="agri-card p-5"><div className="flex justify-between"><div className="h-9 w-9 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center"><Icon className="h-4 w-4" /></div><span className="text-[10px] font-bold text-slate-400">{note}</span></div><div className="mt-4 text-xl font-black font-mono">{value}</div><div className="mt-1 text-xs font-semibold text-slate-500">{label}</div></div>; }
function Param({ label, value }) { return <div className="flex items-center justify-between rounded-xl border border-slate-200 px-4 py-3"><span className="font-mono text-xs text-slate-500">{label}</span><span className="font-mono text-xs font-bold text-slate-900">{value}</span></div>; }
function Performance({ title, data, badge }) { return <div className="agri-card p-6"><div className="flex items-start justify-between gap-3"><div><p className="text-[10px] font-extrabold uppercase tracking-widest text-emerald-600">{badge}</p><h2 className="mt-1 text-lg font-black">{title}</h2></div><CheckCircle2 className="h-5 w-5 text-emerald-600" /></div><div className="mt-5 grid grid-cols-2 gap-3"><Mini label="MAE" value={`${data.mae.toFixed(2)} kg/ha`} /><Mini label="RMSE" value={`${data.rmse.toFixed(2)} kg/ha`} /><Mini label="R²" value={data.r2.toFixed(4)} /><Mini label="MAPE" value={`${data.mape.toFixed(2)}%`} /></div></div>; }
function Mini({ label, value }) { return <div className="rounded-xl bg-slate-50 p-4"><div className="text-[10px] font-extrabold uppercase tracking-widest text-slate-400">{label}</div><div className="mt-2 font-mono text-sm font-black">{value}</div></div>; }
function Compare({ label, value, tone }) { return <div className={`rounded-2xl border p-5 ${tone === 'green' ? 'border-emerald-200 bg-emerald-50' : 'border-slate-200 bg-slate-50'}`}><div className="text-xs font-bold text-slate-600">{label}</div><div className={`mt-2 font-mono text-xl font-black ${tone === 'green' ? 'text-emerald-700' : 'text-slate-900'}`}>{value.toFixed(2)} kg/ha</div><div className="mt-1 text-[10px] text-slate-500">2024 MAE</div></div>; }
