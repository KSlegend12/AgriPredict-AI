import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, BarChart3, BrainCircuit, CalendarDays, CheckCircle2, ChevronRight, CloudSun, Database, Leaf, MapPin, Satellite, ShieldCheck, Sparkles, Sprout, TrendingUp } from 'lucide-react';
import { SUPPORTED_VIDARBHA_DISTRICTS } from '../constants/districts';

const districts = SUPPORTED_VIDARBHA_DISTRICTS;

export default function LandingPage() {
  const navigate = useNavigate();
  return (
    <div className="space-y-8 lg:space-y-10">
      <section className="relative overflow-hidden rounded-[28px] bg-slate-950 text-white shadow-2xl shadow-slate-950/10">
        <div className="absolute inset-0 opacity-25 bg-[radial-gradient(circle_at_75%_20%,#34d399,transparent_35%),radial-gradient(circle_at_20%_90%,#0ea5e9,transparent_30%)]" />
        <div className="relative grid lg:grid-cols-[1.15fr_.85fr] gap-8 items-center p-7 sm:p-10 lg:p-12">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-emerald-400/25 bg-emerald-400/10 px-3 py-1.5 text-[10px] font-extrabold uppercase tracking-[0.18em] text-emerald-300">
              <Sparkles className="h-3.5 w-3.5" /> AI agricultural decision support
            </div>
            <h1 className="mt-5 max-w-3xl text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight leading-[1.03]">
              Cotton yield intelligence for <span className="text-emerald-400">Vidarbha.</span>
            </h1>
            <p className="mt-5 max-w-2xl text-sm sm:text-base leading-7 text-slate-300">
              AgriPredict-AI is a Post-Monsoon Pre-Harvest Cotton Yield Estimation and Decision Support System for Six Vidarbha Districts, utilizing realized Kharif weather through October 31 and SHAP explainability.
            </p>
            <div className="mt-7 flex flex-wrap gap-3">
              <button onClick={() => navigate('/cotton')} className="inline-flex items-center gap-2 rounded-xl bg-emerald-500 px-5 py-3 text-sm font-extrabold text-slate-950 hover:bg-emerald-400 transition">
                Predict Cotton Yield <ArrowRight className="h-4 w-4" />
              </button>
              <button onClick={() => navigate('/dashboard')} className="inline-flex items-center gap-2 rounded-xl border border-slate-700 bg-white/5 px-5 py-3 text-sm font-bold text-white hover:bg-white/10 transition">
                Open Dashboard <BarChart3 className="h-4 w-4" />
              </button>
            </div>
            <div className="mt-8 flex flex-wrap gap-x-6 gap-y-3 text-xs text-slate-400">
              <span className="inline-flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-emerald-400" /> 6 districts</span>
              <span className="inline-flex items-center gap-2"><CalendarDays className="h-4 w-4 text-emerald-400" /> 1997–2024 historical data</span>
              <span className="inline-flex items-center gap-2"><BrainCircuit className="h-4 w-4 text-emerald-400" /> SHAP explainability</span>
            </div>
          </div>

          <div className="relative">
            <div className="overflow-hidden rounded-3xl border border-white/10 bg-white/5">
              <img
                src="/cotton-field.jpg"
                alt="Cotton field in Maharashtra"
                className="h-[330px] sm:h-[390px] w-full object-cover"
              />
              <div className="absolute inset-x-5 bottom-5 grid grid-cols-2 gap-3">
                <div className="rounded-2xl border border-white/10 bg-slate-950/85 p-4 backdrop-blur-xl"><div className="text-2xl font-black text-emerald-400">6</div><div className="mt-1 text-[10px] uppercase tracking-widest text-slate-300">Target districts</div></div>
                <div className="rounded-2xl border border-white/10 bg-slate-950/85 p-4 backdrop-blur-xl"><div className="text-2xl font-black text-cyan-300">28</div><div className="mt-1 text-[10px] uppercase tracking-widest text-slate-300">Harvest years</div></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Feature icon={MapPin} title="6 Vidarbha districts" text="Akola, Amravati, Buldhana, Nagpur, Wardha, and Washim." />
        <Feature icon={CloudSun} title="Weather signals" text="Rainfall, temperature, extremes and seasonal features engineered for cotton." />
        <Feature icon={Satellite} title="Satellite stack" text="MODIS and SMAP datasets are being evaluated as additional signals." />
        <Feature icon={BrainCircuit} title="Explainable AI" text="SHAP feature contributions make individual predictions inspectable." />
      </section>

      <section className="agri-card p-6 sm:p-8">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-3">
          <div><p className="text-[10px] font-extrabold uppercase tracking-[0.18em] text-emerald-600">System snapshot</p><h2 className="mt-1 text-2xl font-black tracking-tight">Built for a real review demo</h2></div>
          <button onClick={() => navigate('/insights')} className="inline-flex items-center gap-1 text-xs font-extrabold text-emerald-700">View model methodology <ChevronRight className="h-4 w-4" /></button>
        </div>
        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Metric label="Selected model" value="Gradient Boosting" icon={BrainCircuit} />
          <Metric label="Training period" value="1997–2023" icon={CalendarDays} />
          <Metric label="Final holdout" value="2024" icon={ShieldCheck} />
          <Metric label="Prediction unit" value="kg / ha" icon={TrendingUp} />
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-[1.05fr_.95fr]">
        <div className="agri-card p-6 sm:p-8">
          <p className="text-[10px] font-extrabold uppercase tracking-[0.18em] text-emerald-600">Study area</p>
          <h2 className="mt-1 text-2xl font-black">Vidarbha, Maharashtra</h2>
          <div className="mt-5 flex flex-wrap gap-2">{districts.map(d => <span key={d} className="rounded-full bg-slate-100 px-3 py-1.5 text-xs font-bold text-slate-700">{d}</span>)}</div>
          <div className="mt-6 grid grid-cols-2 gap-3">
            <SmallStat icon={Database} value="194" label="district-year observations" />
            <SmallStat icon={Leaf} value="Cotton" label="primary crop" />
          </div>
        </div>
        <div className="rounded-[24px] bg-emerald-900 p-6 sm:p-8 text-white">
          <div className="h-11 w-11 rounded-2xl bg-emerald-400/15 flex items-center justify-center"><Sprout className="h-5 w-5 text-emerald-300" /></div>
          <h2 className="mt-5 text-2xl font-black">From data to a decision</h2>
          <p className="mt-3 text-sm leading-6 text-emerald-100/75">Explore the model, inspect historical trends, run a district prediction, and understand which features contributed to the estimate.</p>
          <button onClick={() => navigate('/how-it-works')} className="mt-6 inline-flex items-center gap-2 rounded-xl bg-white px-4 py-2.5 text-xs font-extrabold text-emerald-900 hover:bg-emerald-50">See the pipeline <ArrowRight className="h-4 w-4" /></button>
        </div>
      </section>
    </div>
  );
}

function Feature({ icon: Icon, title, text }) { return <div className="agri-card agri-card-hover p-5"><div className="h-10 w-10 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center"><Icon className="h-5 w-5" /></div><h3 className="mt-4 text-sm font-extrabold">{title}</h3><p className="mt-2 text-xs leading-5 text-slate-500">{text}</p></div>; }
function Metric({ label, value, icon: Icon }) { return <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4"><Icon className="h-4 w-4 text-emerald-600" /><div className="mt-4 text-lg font-black text-slate-900">{value}</div><div className="mt-1 text-[11px] font-semibold text-slate-500">{label}</div></div>; }
function SmallStat({ icon: Icon, value, label }) { return <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4"><Icon className="h-4 w-4 text-emerald-600" /><div className="mt-2 text-lg font-black">{value}</div><div className="text-[11px] text-slate-500">{label}</div></div>; }
