import React from 'react';
import { NavLink } from 'react-router-dom';
import { Sprout, MapPin, ShieldCheck } from 'lucide-react';
import { SUPPORTED_VIDARBHA_DISTRICTS } from '../constants/districts';

const DISTRICTS = SUPPORTED_VIDARBHA_DISTRICTS;

export default function Footer() {
  return (
    <footer className="mt-12 bg-[#0b1d14] text-[#8fa89b] border-t border-[#163526] dark:bg-slate-950 dark:text-slate-400 dark:border-slate-800">
      <div className="max-w-[1500px] mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="grid gap-8 md:grid-cols-4">
          <div className="md:col-span-1">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-2xl bg-[#087A50] dark:bg-emerald-600 flex items-center justify-center text-white shadow-md shadow-emerald-950/40">
                <Sprout className="h-5 w-5" />
              </div>
              <div className="text-lg font-extrabold text-white">
                AgriPredict<span className="text-[#34d399] dark:text-emerald-400">AI</span>
              </div>
            </div>
            <p className="mt-4 text-sm leading-6 text-[#8fa89b] dark:text-slate-400">
              AI-powered cotton yield decision support for the six Vidarbha districts, combining agricultural, weather and satellite-derived signals.
            </p>
          </div>

          <div>
            <h3 className="text-xs font-extrabold uppercase tracking-[0.18em] text-[#d6eae0] dark:text-slate-300">
              Explore
            </h3>
            <div className="mt-4 grid gap-2 text-sm">
              <NavLink to="/dashboard" className="text-[#8fa89b] hover:text-white dark:text-slate-400 dark:hover:text-white transition">Dashboard</NavLink>
              <NavLink to="/cotton" className="text-[#8fa89b] hover:text-white dark:text-slate-400 dark:hover:text-white transition">Cotton Prediction</NavLink>
              <NavLink to="/history" className="text-[#8fa89b] hover:text-white dark:text-slate-400 dark:hover:text-white transition">History</NavLink>
              <NavLink to="/future-forecast" className="text-[#8fa89b] hover:text-white dark:text-slate-400 dark:hover:text-white transition">Future Forecast</NavLink>
            </div>
          </div>

          <div>
            <h3 className="text-xs font-extrabold uppercase tracking-[0.18em] text-[#d6eae0] dark:text-slate-300">
              ML & Data
            </h3>
            <div className="mt-4 grid gap-2 text-sm">
              <NavLink to="/insights" className="text-[#8fa89b] hover:text-white dark:text-slate-400 dark:hover:text-white transition">Model Insights</NavLink>
              <NavLink to="/satellite" className="text-[#8fa89b] hover:text-white dark:text-slate-400 dark:hover:text-white transition">Satellite Data</NavLink>
              <NavLink to="/how-it-works" className="text-[#8fa89b] hover:text-white dark:text-slate-400 dark:hover:text-white transition">How It Works</NavLink>
              <NavLink to="/about" className="text-[#8fa89b] hover:text-white dark:text-slate-400 dark:hover:text-white transition">About Project</NavLink>
            </div>
          </div>

          <div>
            <h3 className="flex items-center gap-2 text-xs font-extrabold uppercase tracking-[0.18em] text-[#d6eae0] dark:text-slate-300">
              <MapPin className="h-3.5 w-3.5 text-[#34d399] dark:text-emerald-400" /> Study Area
            </h3>
            <div className="mt-4 flex flex-wrap gap-1.5">
              {DISTRICTS.map((d) => (
                <span
                  key={d}
                  className="rounded-lg border border-[#1b3e2e] bg-[#12291d] px-2.5 py-1 text-[11px] text-[#c0dbcc] dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300"
                >
                  {d}
                </span>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-9 border-t border-[#163526] dark:border-slate-800 pt-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between text-xs text-[#8fa89b] dark:text-slate-400">
          <span>© 2026 AgriPredictAI · Cotton Yield Decision Support</span>
          <span className="inline-flex items-center gap-2 text-[#738d80] dark:text-slate-500">
            <ShieldCheck className="h-3.5 w-3.5 text-[#34d399] dark:text-emerald-400" /> Six-District Thermal Ridge
          </span>
        </div>
      </div>
    </footer>
  );
}
