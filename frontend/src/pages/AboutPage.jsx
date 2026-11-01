import React from 'react';
import { Database, MapPin, ShieldCheck, BrainCircuit, Satellite, Code2, Target, AlertTriangle } from 'lucide-react';
import { SUPPORTED_VIDARBHA_DISTRICTS } from '../constants/districts';

const districts = SUPPORTED_VIDARBHA_DISTRICTS;

export default function AboutPage() {
  return (
    <div className="space-y-6">
      <section className="rounded-[28px] bg-gradient-to-br from-[#087A50] via-[#096644] to-[#05442d] dark:from-slate-950 dark:to-slate-900 p-7 sm:p-10 text-white shadow-xl shadow-[#087A50]/15 dark:shadow-none">
        <div className="inline-flex items-center gap-2 rounded-full border border-emerald-300/30 bg-emerald-400/15 px-3 py-1.5 text-[10px] font-extrabold uppercase tracking-[0.18em] text-emerald-200">
          <Target className="h-3.5 w-3.5" /> Project overview
        </div>
        <h1 className="mt-4 text-3xl sm:text-4xl font-black tracking-tight">AgriPredictAI</h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-emerald-100/90 dark:text-slate-300">
          Post-Monsoon Pre-Harvest Cotton Yield Estimation and Decision Support System for Six Vidarbha Districts (Akola, Amravati, Buldhana, Nagpur, Wardha, Washim), utilizing realized Kharif weather through October 31 with transparent empirical error bounds and SHAP-based explainability.
        </p>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <Card icon={MapPin} title="Study area" text="Six Vidarbha districts: Akola, Amravati, Buldhana, Nagpur, Wardha, and Washim." />
        <Card icon={Database} title="Authoritative dataset" text="194 district-year observations covering 1997–2024, with 2024 preserved as the final holdout." />
        <Card icon={BrainCircuit} title="Production model" text="Six-District Thermal Ridge with α=75, degree-day heat threshold and realized Kharif weather." />
        <Card icon={Satellite} title="Earth observation" text="MOD13, MOD16, MOD17 and MOD11 extractions are available; SMAP and MOD15 are processing." />
        <Card icon={ShieldCheck} title="Validation" text="Chronological expanding-window validation is used for 2011–2023, followed by an untouched 2024 holdout." />
        <Card icon={Code2} title="Technology" text="React + Vite frontend, FastAPI backend, scikit-learn model pipeline and SHAP TreeExplainer." />
      </section>

      <section className="agri-card p-6 sm:p-8">
        <h2 className="text-xl font-black text-[#183C2C] dark:text-white">Supported districts</h2>
        <div className="mt-5 flex flex-wrap gap-2">
          {districts.map(d => (
            <span key={d} className="rounded-full bg-[#EAF2EC] border border-[#DCE8DF] dark:border-slate-800 dark:bg-slate-800 px-3 py-1.5 text-xs font-bold text-[#183C2C] dark:text-slate-300">
              {d}
            </span>
          ))}
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <div className="agri-card p-6">
          <h2 className="text-lg font-black text-[#183C2C] dark:text-white">Model transparency</h2>
          <p className="mt-2 text-sm leading-6 text-[#607568] dark:text-slate-400">
            The system exposes validation metrics, baseline comparisons and SHAP feature contributions instead of hiding model behaviour behind a single accuracy number.
          </p>
        </div>
        <div className="rounded-2xl border border-amber-200 bg-amber-50/80 dark:border-amber-900/40 dark:bg-amber-950/20 p-6">
          <div className="flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
            <div>
              <h2 className="text-sm font-black text-amber-900 dark:text-amber-300">Decision-support boundary</h2>
              <p className="mt-2 text-xs leading-5 text-amber-800 dark:text-amber-400/90">
                Predictions are statistical estimates. Future forecasts are scenario-based and should not be treated as guaranteed harvest outcomes.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

function Card({ icon: Icon, title, text }) {
  return (
    <div className="agri-card agri-card-hover p-5">
      <div className="h-10 w-10 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 text-[#087A50] dark:text-emerald-400 flex items-center justify-center">
        <Icon className="h-5 w-5" />
      </div>
      <h3 className="mt-4 text-sm font-black text-[#183C2C] dark:text-white">{title}</h3>
      <p className="mt-2 text-xs leading-5 text-[#607568] dark:text-slate-400">{text}</p>
    </div>
  );
}
