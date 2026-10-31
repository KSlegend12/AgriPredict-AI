import React from 'react';
import { NavLink } from 'react-router-dom';
import { Sprout, MapPin, ShieldCheck, ExternalLink } from 'lucide-react';
import { SUPPORTED_VIDARBHA_DISTRICTS } from '../constants/districts';

const DISTRICTS = SUPPORTED_VIDARBHA_DISTRICTS;

export default function Footer() {
  return (
    <footer className="mt-12 bg-slate-950 text-slate-400">
      <div className="max-w-[1500px] mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="grid gap-8 md:grid-cols-4">
          <div className="md:col-span-1">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-2xl bg-emerald-600 flex items-center justify-center text-white"><Sprout className="h-5 w-5" /></div>
              <div className="text-lg font-extrabold text-white">AgriPredict<span className="text-emerald-400">AI</span></div>
            </div>
            <p className="mt-4 text-sm leading-6 text-slate-400">AI-powered cotton yield decision support for the six Vidarbha districts, combining agricultural, weather and satellite-derived signals.</p>
          </div>

          <div>
            <h3 className="text-xs font-extrabold uppercase tracking-[0.18em] text-slate-300">Explore</h3>
            <div className="mt-4 grid gap-2 text-sm">
              <NavLink to="/dashboard" className="hover:text-white">Dashboard</NavLink>
              <NavLink to="/cotton" className="hover:text-white">Cotton Prediction</NavLink>
              <NavLink to="/history" className="hover:text-white">History</NavLink>
              <NavLink to="/future-forecast" className="hover:text-white">Future Forecast</NavLink>
            </div>
          </div>

          <div>
            <h3 className="text-xs font-extrabold uppercase tracking-[0.18em] text-slate-300">ML & Data</h3>
            <div className="mt-4 grid gap-2 text-sm">
              <NavLink to="/insights" className="hover:text-white">Model Insights</NavLink>
              <NavLink to="/satellite" className="hover:text-white">Satellite Data</NavLink>
              <NavLink to="/how-it-works" className="hover:text-white">How It Works</NavLink>
              <NavLink to="/about" className="hover:text-white">About Project</NavLink>
            </div>
          </div>

          <div>
            <h3 className="flex items-center gap-2 text-xs font-extrabold uppercase tracking-[0.18em] text-slate-300"><MapPin className="h-3.5 w-3.5 text-emerald-400" /> Study Area</h3>
            <div className="mt-4 flex flex-wrap gap-1.5">
              {DISTRICTS.map((d) => <span key={d} className="rounded-lg border border-slate-800 bg-slate-900 px-2.5 py-1 text-[11px] text-slate-300">{d}</span>)}
            </div>
          </div>
        </div>

        <div className="mt-9 border-t border-slate-800 pt-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between text-xs">
          <span>© 2026 AgriPredictAI · Cotton Yield Decision Support</span>
          <span className="inline-flex items-center gap-2 text-slate-500"><ShieldCheck className="h-3.5 w-3.5 text-emerald-400" /> Gradient Boosting + SHAP</span>
        </div>
      </div>
    </footer>
  );
}
