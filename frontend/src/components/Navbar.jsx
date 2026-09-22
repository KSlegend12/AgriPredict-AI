import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { Sprout, MapPin, Sparkles, Menu, X, ChevronDown, BarChart3, Satellite, BrainCircuit, Workflow, Sun, Moon } from 'lucide-react';

const DISTRICTS = ['Akola', 'Amravati', 'Buldhana', 'Nagpur', 'Wardha', 'Washim', 'Yavatmal'];

const links = [
  { to: '/dashboard', label: 'Dashboard', icon: BarChart3 },
  { to: '/cotton', label: 'Prediction', icon: Sparkles },
  { to: '/insights', label: 'Model Insights', icon: BrainCircuit },
  { to: '/satellite', label: 'Satellite', icon: Satellite },
  { to: '/future-forecast', label: 'Forecast', icon: BarChart3 },
  { to: '/how-it-works', label: 'How It Works', icon: Workflow },
];

export default function Navbar({ selectedDistrict, setSelectedDistrict, isRealModel, theme, setTheme }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const navigate = useNavigate();
  const district = DISTRICTS.includes(selectedDistrict) ? selectedDistrict : 'Akola';
  const isDark = theme === 'dark';

  const toggleTheme = () => setTheme(isDark ? 'light' : 'dark');

  return (
    <header className="app-header sticky top-0 z-50 border-b border-slate-200/80 bg-white/95 backdrop-blur-xl shadow-[0_2px_18px_rgba(15,23,42,0.05)]">
      <div className="max-w-[1500px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="h-[72px] flex items-center justify-between gap-4">
          <NavLink to="/" className="flex items-center gap-3 shrink-0 group">
            <div className="h-10 w-10 rounded-2xl bg-emerald-600 text-white flex items-center justify-center shadow-lg shadow-emerald-600/20 group-hover:bg-emerald-700 transition">
              <Sprout className="h-5 w-5" />
            </div>
            <div>
              <div className="text-[17px] font-extrabold tracking-tight text-slate-950">
                AgriPredict<span className="text-emerald-600">AI</span>
              </div>
              <div className="text-[9px] uppercase tracking-[0.18em] text-slate-400 font-semibold">
                Vidarbha Cotton Intelligence
              </div>
            </div>
          </NavLink>

          <nav className="hidden xl:flex items-center gap-1">
            <NavLink to="/" end className={navClass}>Home</NavLink>
            {links.map(({ to, label }) => (
              <NavLink key={to} to={to} className={navClass}>{label}</NavLink>
            ))}
          </nav>

          <div className="flex items-center gap-2">
            <div className="hidden lg:flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2">
              <MapPin className="h-3.5 w-3.5 text-emerald-600" />
              <select
                value={district}
                onChange={(e) => setSelectedDistrict?.(e.target.value)}
                className="district-select bg-transparent text-xs font-bold text-slate-700 outline-none cursor-pointer pr-4"
              >
                {DISTRICTS.map((d) => <option key={d} value={d}>{d}</option>)}
              </select>
              <ChevronDown className="h-3 w-3 text-slate-400 -ml-5 pointer-events-none" />
            </div>

            <button
              type="button"
              onClick={toggleTheme}
              className="theme-toggle h-10 w-10 rounded-xl border border-slate-200 bg-white text-slate-700 flex items-center justify-center hover:border-emerald-300 hover:text-emerald-600 transition"
              aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
              title={isDark ? 'Light mode' : 'Dark mode'}
            >
              {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </button>

            <div className="hidden md:flex items-center gap-2 rounded-xl border border-emerald-100 bg-emerald-50 px-3 py-2 text-[10px] font-bold text-emerald-700">
              <span className={`h-2 w-2 rounded-full ${isRealModel ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`} />
              {isRealModel ? 'MODEL ONLINE' : 'GRADIENT BOOSTING READY'}
            </div>

            <button
              onClick={() => navigate('/cotton')}
              className="hidden sm:flex items-center gap-2 rounded-xl bg-slate-950 px-4 py-2.5 text-xs font-bold text-white shadow-lg shadow-slate-950/10 hover:bg-emerald-700 transition"
            >
              <Sparkles className="h-3.5 w-3.5" /> Predict Yield
            </button>

            <button
              onClick={() => setMobileOpen((v) => !v)}
              className="xl:hidden rounded-xl border border-slate-200 bg-white p-2.5 text-slate-700"
              aria-label="Open menu"
            >
              {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>

        {mobileOpen && (
          <div className="mobile-menu xl:hidden border-t border-slate-100 py-3 pb-5 space-y-1">
            <div className="mb-3 flex items-center gap-2 rounded-xl bg-slate-50 p-3">
              <MapPin className="h-4 w-4 text-emerald-600" />
              <select value={district} onChange={(e) => setSelectedDistrict?.(e.target.value)} className="district-select flex-1 bg-transparent text-sm font-bold outline-none">
                {DISTRICTS.map((d) => <option key={d} value={d}>{d}</option>)}
              </select>
            </div>
            <button type="button" onClick={toggleTheme} className="theme-mobile-button w-full flex items-center justify-between rounded-xl px-4 py-3 text-sm font-bold">
              <span>{isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}</span>
              {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </button>
            <NavLink to="/" end onClick={() => setMobileOpen(false)} className={mobileClass}>Home</NavLink>
            {links.map(({ to, label }) => <NavLink key={to} to={to} onClick={() => setMobileOpen(false)} className={mobileClass}>{label}</NavLink>)}
            <NavLink to="/history" onClick={() => setMobileOpen(false)} className={mobileClass}>History</NavLink>
            <NavLink to="/weather" onClick={() => setMobileOpen(false)} className={mobileClass}>Weather</NavLink>
            <NavLink to="/about" onClick={() => setMobileOpen(false)} className={mobileClass}>About</NavLink>
          </div>
        )}
      </div>
    </header>
  );
}

const navClass = ({ isActive }) => `px-3 py-2 rounded-xl text-[11px] font-bold transition ${isActive ? 'bg-emerald-50 text-emerald-700' : 'text-slate-600 hover:bg-slate-50 hover:text-slate-950'}`;
const mobileClass = ({ isActive }) => `block rounded-xl px-4 py-3 text-sm font-bold ${isActive ? 'bg-emerald-50 text-emerald-700' : 'text-slate-700 hover:bg-slate-50'}`;
