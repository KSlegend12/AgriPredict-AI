import React from 'react';
import { ArrowDown, BrainCircuit, Database, Gauge, GitBranch, Layers3, Satellite, ShieldCheck, Sparkles, Thermometer, TrendingUp } from 'lucide-react';

export default function HowItWorksPage() {
  const steps = [
    ['01', 'Agricultural data', 'Historical district-level cotton area and yield observations form the core supervised-learning dataset.', Database],
    ['02', 'Weather features', 'Annual, monsoon and Kharif rainfall/temperature features plus lagged yield signals are engineered.', Thermometer],
    ['03', 'Satellite features', 'MODIS and SMAP observations are converted into district-year features and independently evaluated.', Satellite],
    ['04', 'Temporal validation', 'Chronological expanding-window validation avoids mixing future observations into earlier training.', GitBranch],
    ['05', 'Six-District Thermal Ridge', 'The selected Thermal Ridge model with α=75 produces the cotton yield estimate in kg/ha.', BrainCircuit],
    ['06', 'SHAP explanation', 'TreeExplainer and linear attributions provide feature contributions for an individual prediction and global importance.', Sparkles],
  ];

  return (
    <div className="space-y-6">
      <section className="rounded-[28px] bg-gradient-to-br from-[#087A50] via-[#096644] to-[#05442d] dark:from-emerald-950 dark:to-[#07130f] p-7 sm:p-10 text-white shadow-xl shadow-[#087A50]/15 dark:shadow-none">
        <div className="inline-flex items-center gap-2 rounded-full border border-emerald-300/30 bg-emerald-400/15 px-3 py-1.5 text-[10px] font-extrabold uppercase tracking-[0.18em] text-emerald-200">
          <Layers3 className="h-3.5 w-3.5" /> End-to-end pipeline
        </div>
        <h1 className="mt-4 text-3xl sm:text-4xl font-black tracking-tight">How AgriPredictAI works</h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-emerald-100/90 dark:text-emerald-100/75">
          A transparent story for the review: verified observations → engineered signals → time-safe evaluation → yield estimate → explanation.
        </p>
      </section>

      <section className="grid gap-3">
        {steps.map(([n, title, text, Icon], i) => (
          <React.Fragment key={n}>
            <div className="agri-card p-5 sm:p-6 flex gap-5 items-start">
              <div className="shrink-0 h-12 w-12 rounded-2xl bg-[#087A50] text-white dark:bg-slate-950 flex items-center justify-center shadow-md shadow-[#087A50]/20 dark:shadow-none">
                <Icon className="h-5 w-5" />
              </div>
              <div className="flex-1">
                <div className="font-mono text-[10px] font-bold text-[#087A50] dark:text-emerald-400">STEP {n}</div>
                <h2 className="mt-1 text-lg font-black text-[#183C2C] dark:text-white">{title}</h2>
                <p className="mt-2 text-sm leading-6 text-[#607568] dark:text-slate-400">{text}</p>
              </div>
            </div>
            {i < steps.length - 1 && (
              <div className="flex justify-center">
                <ArrowDown className="h-5 w-5 text-[#087A50]/40 dark:text-slate-600" />
              </div>
            )}
          </React.Fragment>
        ))}
      </section>

      <section className="grid gap-4 sm:grid-cols-3">
        <Callout icon={ShieldCheck} title="Leakage control" text="2024 is kept as a final holdout. Target-derived lag features use prior years only." />
        <Callout icon={Gauge} title="Model evaluation" text="MAE, RMSE, R² and MAPE are reported separately; R² is not presented as accuracy." />
        <Callout icon={TrendingUp} title="Future forecasting" text="2027–2031 forecasts use explicit weather scenarios and remain separate from the validated 2024 holdout model." />
      </section>
    </div>
  );
}

function Callout({ icon: Icon, title, text }) {
  return (
    <div className="agri-card p-5">
      <div className="h-10 w-10 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 text-[#087A50] dark:text-emerald-400 flex items-center justify-center">
        <Icon className="h-5 w-5" />
      </div>
      <h3 className="mt-4 text-sm font-black text-[#183C2C] dark:text-white">{title}</h3>
      <p className="mt-2 text-xs leading-5 text-[#607568] dark:text-slate-400">{text}</p>
    </div>
  );
}
