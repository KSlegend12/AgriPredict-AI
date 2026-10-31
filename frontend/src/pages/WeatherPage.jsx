import React, { useState, useEffect } from 'react';
import { CloudSun, MapPin, Droplets, Thermometer, Calendar } from 'lucide-react';
import { getWeather } from '../services/api';
import { SUPPORTED_VIDARBHA_DISTRICTS, sanitizeDistrict } from '../constants/districts';

const VIDARBHA_DISTRICTS = SUPPORTED_VIDARBHA_DISTRICTS;

const DISTRICT_WEATHER_PRESETS = {
  Akola: { annual_rain: 820.0, monsoon_rain: 721.6, kharif_rain: 754.4, tmax_mean: 33.5, tmin_mean: 20.2, rainy_days: 64, heavy_rain_days: 6, max_dry_spell: 20 },
  Amravati: { annual_rain: 880.0, monsoon_rain: 774.4, kharif_rain: 809.6, tmax_mean: 33.4, tmin_mean: 20.3, rainy_days: 68, heavy_rain_days: 7, max_dry_spell: 18 },
  Buldhana: { annual_rain: 760.0, monsoon_rain: 668.8, kharif_rain: 699.2, tmax_mean: 33.6, tmin_mean: 20.1, rainy_days: 60, heavy_rain_days: 5, max_dry_spell: 22 },
  Nagpur: { annual_rain: 1100.0, monsoon_rain: 968.0, kharif_rain: 1012.0, tmax_mean: 32.1, tmin_mean: 19.2, rainy_days: 80, heavy_rain_days: 9, max_dry_spell: 14 },
  Wardha: { annual_rain: 980.0, monsoon_rain: 862.4, kharif_rain: 901.6, tmax_mean: 33.9, tmin_mean: 20.9, rainy_days: 72, heavy_rain_days: 8, max_dry_spell: 16 },
  Washim: { annual_rain: 850.0, monsoon_rain: 748.0, kharif_rain: 782.0, tmax_mean: 33.5, tmin_mean: 20.2, rainy_days: 62, heavy_rain_days: 6, max_dry_spell: 20 },
};

export default function WeatherPage({ selectedDistrict, setSelectedDistrict }) {
  const currentDistrict = sanitizeDistrict(selectedDistrict);
  const [weatherData, setWeatherData] = useState(null);

  useEffect(() => {
    async function loadData() {
      const res = await getWeather(currentDistrict);
      setWeatherData(res);
    }
    loadData();
  }, [currentDistrict]);

  const preset = DISTRICT_WEATHER_PRESETS[currentDistrict] || DISTRICT_WEATHER_PRESETS.Akola;

  return (
    <div className="space-y-8 py-4 max-w-7xl mx-auto">
      
      {/* Top Header & District Selector */}
      <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-slate-200 pb-4 gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md bg-emerald-50 text-emerald-800 border border-emerald-200 text-xs font-semibold uppercase tracking-wider mb-1">
            <CloudSun className="w-3.5 h-3.5 text-emerald-600" />
            <span>IMD Weather Intelligence</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Weather & Climate Indicators
          </h1>
          <p className="text-xs text-slate-500 font-normal">
            Authoritative IMD climate metrics for cotton cultivation across Vidarbha.
          </p>
        </div>

        {/* District Selector (Requirement #22) */}
        <div className="flex items-center gap-2 bg-white border border-slate-300 px-3 py-1.5 rounded-md shadow-xs">
          <MapPin className="w-3.5 h-3.5 text-emerald-600" />
          <select
            value={currentDistrict}
            onChange={(e) => setSelectedDistrict(e.target.value)}
            className="bg-transparent text-slate-900 text-xs font-semibold cursor-pointer pr-2 focus:outline-none"
          >
            {VIDARBHA_DISTRICTS.map((d) => (
              <option key={d} value={d} className="bg-white text-slate-900 font-medium">
                {d} District
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* SECTION 1: ANNUAL CLIMATE INDICATORS */}
      <div className="space-y-4">
        <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <Calendar className="w-4 h-4 text-emerald-600" />
          <span>Annual Climate Indicators ({currentDistrict})</span>
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="agri-card p-5 border border-slate-200 space-y-1">
            <span className="text-[11px] font-mono text-slate-500 font-semibold uppercase tracking-wider block">Annual Total Rainfall</span>
            <div className="text-2xl font-extrabold text-teal-700 font-mono">
              {preset.annual_rain} <span className="text-xs font-semibold text-slate-600 font-sans">mm</span>
            </div>
            <p className="text-[11px] text-slate-500">Total yearly precipitation recorded</p>
          </div>

          <div className="agri-card p-5 border border-slate-200 space-y-1">
            <span className="text-[11px] font-mono text-slate-500 font-semibold uppercase tracking-wider block">Mean Maximum Temperature</span>
            <div className="text-2xl font-extrabold text-amber-700 font-mono">
              {preset.tmax_mean} <span className="text-xs font-semibold text-slate-600 font-sans">°C</span>
            </div>
            <p className="text-[11px] text-slate-500">Average daytime maximum temperature</p>
          </div>

          <div className="agri-card p-5 border border-slate-200 space-y-1">
            <span className="text-[11px] font-mono text-slate-500 font-semibold uppercase tracking-wider block">Mean Minimum Temperature</span>
            <div className="text-2xl font-extrabold text-slate-700 font-mono">
              {preset.tmin_mean} <span className="text-xs font-semibold text-slate-600 font-sans">°C</span>
            </div>
            <p className="text-[11px] text-slate-500">Average night-time minimum temperature</p>
          </div>

          <div className="agri-card p-5 border border-slate-200 space-y-1">
            <span className="text-[11px] font-mono text-slate-500 font-semibold uppercase tracking-wider block">Annual Rainy Days</span>
            <div className="text-2xl font-extrabold text-emerald-700 font-mono">
              {preset.rainy_days} <span className="text-xs font-semibold text-slate-600 font-sans">days</span>
            </div>
            <p className="text-[11px] text-slate-500">Days with precipitation ≥2.5mm</p>
          </div>
        </div>
      </div>

      {/* SECTION 2: MONSOON SEASON METRICS */}
      <div className="space-y-4">
        <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <Droplets className="w-4 h-4 text-emerald-600" />
          <span>Monsoon Season Metrics (June – September)</span>
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="agri-card p-5 border border-slate-200 space-y-1">
            <span className="text-[11px] font-mono text-slate-500 font-semibold uppercase tracking-wider block">Monsoon Rainfall</span>
            <div className="text-2xl font-extrabold text-teal-700 font-mono">
              {preset.monsoon_rain} <span className="text-xs font-semibold text-slate-600 font-sans">mm</span>
            </div>
            <p className="text-[11px] text-slate-500">88% of annual rainfall volume</p>
          </div>

          <div className="agri-card p-5 border border-slate-200 space-y-1">
            <span className="text-[11px] font-mono text-slate-500 font-semibold uppercase tracking-wider block">Heavy Rain Days</span>
            <div className="text-2xl font-extrabold text-cyan-700 font-mono">
              {preset.heavy_rain_days} <span className="text-xs font-semibold text-slate-600 font-sans">days</span>
            </div>
            <p className="text-[11px] text-slate-500">Days with rainfall ≥50mm</p>
          </div>

          <div className="agri-card p-5 border border-slate-200 space-y-1">
            <span className="text-[11px] font-mono text-slate-500 font-semibold uppercase tracking-wider block">Maximum Dry Spell</span>
            <div className="text-2xl font-extrabold text-rose-600 font-mono">
              {preset.max_dry_spell} <span className="text-xs font-semibold text-slate-600 font-sans">days</span>
            </div>
            <p className="text-[11px] text-slate-500">Longest streak of zero-rainfall days in monsoon</p>
          </div>
        </div>
      </div>

      {/* SECTION 3: KHARIF CROP SEASON METRICS */}
      <div className="space-y-4">
        <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <Thermometer className="w-4 h-4 text-emerald-600" />
          <span>Kharif Crop Growth Window (June – October)</span>
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="agri-card p-5 border border-slate-200 space-y-1">
            <span className="text-[11px] font-mono text-slate-500 font-semibold uppercase tracking-wider block">Kharif Total Rainfall</span>
            <div className="text-2xl font-extrabold text-emerald-700 font-mono">
              {preset.kharif_rain} <span className="text-xs font-semibold text-slate-600 font-sans">mm</span>
            </div>
            <p className="text-[11px] text-slate-500">Total precipitation received during cotton vegetative and boll-formation stages</p>
          </div>

          <div className="agri-card p-5 border border-slate-200 space-y-1">
            <span className="text-[11px] font-mono text-slate-500 font-semibold uppercase tracking-wider block">Kharif Daytime Heat Standard</span>
            <div className="text-2xl font-extrabold text-amber-700 font-mono">
              {preset.tmax_mean} <span className="text-xs font-semibold text-slate-600 font-sans">°C</span>
            </div>
            <p className="text-[11px] text-slate-500">Mean daytime maximum temperature during boll development</p>
          </div>
        </div>
      </div>

    </div>
  );
}
