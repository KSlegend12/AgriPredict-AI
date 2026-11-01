import React, { useEffect, useState } from 'react';
import { BarChart3, BrainCircuit, CheckCircle2, Clock3, GitBranch, Info, ShieldCheck, Target, TrendingDown } from 'lucide-react';
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
  const modelName = info?.model_name || info?.model || 'Six-District Thermal Ridge';

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
          <div className="flex items-center gap-3">
            <div className="h-11 w-11 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 text-[#087A50] dark:text-emerald-400 flex items-center justify-center">
              <BrainCircuit className="h-5 w-5" />
            </div>
            <div>
              <p className="text-[10px] font-extrabold uppercase tracking-widest text-[#087A50] dark:text-emerald-400">Selected model</p>
              <h2 className="text-lg font-black text-[#183C2C] dark:text-white">{modelName}</h2>
            </div>
          </div>
          <div className="mt-6 grid gap-3">
            <Param label="Model type" value="Ridge (alpha=75.0)" />
            <Param label="Heat Threshold" value="Degree-Day GDD > 32°C" />
            <Param label="Validation MAE" value="104.75 kg/ha" />
            <Param label="Scope" value="Six Vidarbha Districts" />
          </div>
          <div className="mt-5 rounded-2xl bg-[#F4F8F5] border border-[#DCE8DF] dark:border-slate-800 dark:bg-slate-900/60 p-4 text-xs leading-5 text-[#607568] dark:text-slate-400">
            <b className="text-[#183C2C] dark:text-slate-200">Training:</b> 1997–2023 · <b className="text-[#183C2C] dark:text-slate-200">Final holdout:</b> 2024 · chronological evaluation.
          </div>
        </div>

        <div className="agri-card p-6 sm:p-7">
          <div className="flex items-end justify-between gap-4">
            <div>
              <p className="text-[10px] font-extrabold uppercase tracking-widest text-[#087A50] dark:text-emerald-400">Explainability</p>
              <h2 className="mt-1 text-lg font-black text-[#183C2C] dark:text-white">Global feature contribution</h2>
              <p className="mt-1 text-xs text-[#607568] dark:text-slate-400">Mean absolute SHAP value on the 2024 holdout.</p>
            </div>
            <Info className="h-4 w-4 text-[#607568] dark:text-slate-400" />
          </div>
          <div className="mt-5 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartFeatures} layout="vertical" margin={{ top: 5, right: 15, left: 10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--chart-grid, #DCE8DF)" />
                <XAxis type="number" fontSize={10} tick={{ fill: 'var(--chart-axis, #607568)' }} />
                <YAxis type="category" dataKey="name" width={155} fontSize={10} tickLine={false} tick={{ fill: 'var(--chart-axis, #607568)' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'var(--chart-tooltip-bg, #FFFFFF)',
                    borderColor: 'var(--chart-tooltip-border, #DCE8DF)',
                    borderRadius: '8px',
                    color: 'var(--chart-tooltip-text, #183C2C)',
                    fontSize: '12px',
                    boxShadow: '0 4px 16px rgba(24, 60, 44, 0.08)'
                  }}
                  formatter={(v) => [Number(v).toFixed(2), 'Mean |SHAP|']}
                />
                <Bar dataKey="value" fill="#087A50" radius={[0, 5, 5, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <Performance title="2011–2023 expanding-window validation" data={validation} badge="Validation" />
        <Performance title="2024 final holdout" data={holdout} badge="Holdout" />
      </section>

      <section className="agri-card p-6 sm:p-7">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-[#087A50] text-white dark:bg-slate-950 flex items-center justify-center shadow-md shadow-[#087A50]/20 dark:shadow-none">
            <GitBranch className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-lg font-black text-[#183C2C] dark:text-white">Baseline context</h2>
            <p className="text-xs text-[#607568] dark:text-slate-400">The 2024 holdout is interpreted alongside simple baselines.</p>
          </div>
        </div>
        <div className="mt-5 grid gap-3 md:grid-cols-3">
          <Compare label="Thermal Ridge" value={holdout.mae} tone="green" />
          <Compare label="Previous-year baseline" value={baseline.previous} tone="slate" />
          <Compare label="Historical-mean baseline" value={baseline.historical} tone="slate" />
        </div>
        <p className="mt-5 rounded-2xl border border-amber-200 bg-amber-50/80 dark:border-amber-900/40 dark:bg-amber-950/20 p-4 text-xs leading-5 text-amber-800 dark:text-amber-300">
          <b>Interpretation:</b> the selected model improves on the historical-mean baseline for the 2024 holdout, but its 2024 MAE is higher than the previous-year baseline. This is reported transparently rather than converted into an “accuracy” score.
        </p>
      </section>

      <section className="rounded-2xl border border-[#DCE8DF] bg-white dark:border-slate-800 dark:bg-slate-900/60 p-5 flex items-start gap-3">
        <Clock3 className="mt-0.5 h-5 w-5 text-[#087A50] dark:text-emerald-400 shrink-0" />
        <div>
          <h3 className="text-sm font-extrabold text-[#183C2C] dark:text-white">Why chronological validation?</h3>
          <p className="mt-1 text-xs leading-5 text-[#607568] dark:text-slate-400">
            Agricultural forecasting is time-dependent. The project keeps 2024 untouched as the final holdout instead of randomly mixing future observations into training.
          </p>
        </div>
      </section>
    </div>
  );
}

function Hero() {
  return (
    <section className="rounded-[28px] bg-gradient-to-br from-[#087A50] via-[#096644] to-[#05442d] dark:from-slate-950 dark:to-slate-900 p-7 sm:p-9 text-white shadow-xl shadow-[#087A50]/15 dark:shadow-none">
      <div className="inline-flex items-center gap-2 rounded-full border border-emerald-300/30 bg-emerald-400/15 px-3 py-1.5 text-[10px] font-extrabold uppercase tracking-[0.18em] text-emerald-200">
        <BrainCircuit className="h-3.5 w-3.5" /> Model transparency
      </div>
      <h1 className="mt-4 text-3xl sm:text-4xl font-black tracking-tight">Model Insights & Explainability</h1>
      <p className="mt-2 max-w-3xl text-sm leading-6 text-emerald-100/90 dark:text-slate-300">
        A presentation-ready view of the selected Six-District Thermal Ridge model, its chronological validation, final 2024 holdout and SHAP feature contributions.
      </p>
    </section>
  );
}

function Metric({ label, value, note, icon: Icon }) {
  return (
    <div className="agri-card p-5">
      <div className="flex justify-between">
        <div className="h-9 w-9 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 text-[#087A50] dark:text-emerald-400 flex items-center justify-center">
          <Icon className="h-4 w-4" />
        </div>
        <span className="text-[10px] font-bold text-[#607568] dark:text-slate-400">{note}</span>
      </div>
      <div className="mt-4 text-xl font-black font-mono text-[#183C2C] dark:text-white">{value}</div>
      <div className="mt-1 text-xs font-semibold text-[#607568] dark:text-slate-400">{label}</div>
    </div>
  );
}

function Param({ label, value }) {
  return (
    <div className="flex items-center justify-between rounded-xl border border-[#DCE8DF] bg-[#F4F8F5] dark:border-slate-800 dark:bg-slate-900/60 px-4 py-3">
      <span className="font-mono text-xs text-[#607568] dark:text-slate-400">{label}</span>
      <span className="font-mono text-xs font-bold text-[#183C2C] dark:text-slate-200">{value}</span>
    </div>
  );
}

function Performance({ title, data, badge }) {
  return (
    <div className="agri-card p-6">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-[10px] font-extrabold uppercase tracking-widest text-[#087A50] dark:text-emerald-400">{badge}</p>
          <h2 className="mt-1 text-lg font-black text-[#183C2C] dark:text-white">{title}</h2>
        </div>
        <CheckCircle2 className="h-5 w-5 text-[#087A50] dark:text-emerald-400" />
      </div>
      <div className="mt-5 grid grid-cols-2 gap-3">
        <Mini label="MAE" value={`${data.mae.toFixed(2)} kg/ha`} />
        <Mini label="RMSE" value={`${data.rmse.toFixed(2)} kg/ha`} />
        <Mini label="R²" value={data.r2.toFixed(4)} />
        <Mini label="MAPE" value={`${data.mape.toFixed(2)}%`} />
      </div>
    </div>
  );
}

function Mini({ label, value }) {
  return (
    <div className="rounded-xl bg-[#F4F8F5] border border-[#DCE8DF] dark:border-slate-800 dark:bg-slate-900/60 p-4">
      <div className="text-[10px] font-extrabold uppercase tracking-widest text-[#607568] dark:text-slate-400">{label}</div>
      <div className="mt-2 font-mono text-sm font-black text-[#183C2C] dark:text-white">{value}</div>
    </div>
  );
}

function Compare({ label, value, tone }) {
  const isGreen = tone === 'green';
  return (
    <div className={`rounded-2xl border p-5 ${
      isGreen
        ? 'border-emerald-200 bg-emerald-50/70 dark:border-emerald-900/40 dark:bg-emerald-950/20'
        : 'border-[#DCE8DF] bg-[#F4F8F5] dark:border-slate-800 dark:bg-slate-900/60'
    }`}>
      <div className="text-xs font-bold text-[#607568] dark:text-slate-400">{label}</div>
      <div className={`mt-2 font-mono text-xl font-black ${
        isGreen ? 'text-[#087A50] dark:text-emerald-400' : 'text-[#183C2C] dark:text-white'
      }`}>
        {value.toFixed(2)} kg/ha
      </div>
      <div className="mt-1 text-[10px] text-[#607568] dark:text-slate-400">2024 MAE</div>
    </div>
  );
}
