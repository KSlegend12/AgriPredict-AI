import React from 'react';
import { Thermometer, CloudRain, Droplets, Wind, TestTube, Sparkles } from 'lucide-react';

export default function WeatherCard({ weather }) {
  if (!weather) return null;

  const metrics = [
    {
      label: 'Temperature',
      value: `${weather.temperature ?? 27}°C`,
      icon: Thermometer,
      iconColor: 'text-amber-500 dark:text-amber-400',
      containerClass: 'from-amber-500/10 to-amber-500/5 border-amber-200/80 dark:from-amber-950/40 dark:to-slate-900/80 dark:border-amber-500/20',
      sub: `Feels like ${weather.feels_like ?? weather.temperature ?? 27}°C`
    },
    {
      label: 'Rainfall',
      value: `${weather.rainfall ?? 650} mm`,
      icon: CloudRain,
      iconColor: 'text-blue-500 dark:text-blue-400',
      containerClass: 'from-blue-500/10 to-blue-500/5 border-blue-200/80 dark:from-blue-950/40 dark:to-slate-900/80 dark:border-blue-500/20',
      sub: 'Annual avg for district'
    },
    {
      label: 'Humidity',
      value: `${weather.humidity ?? 70}%`,
      icon: Droplets,
      iconColor: 'text-cyan-600 dark:text-cyan-400',
      containerClass: 'from-cyan-500/10 to-cyan-500/5 border-cyan-200/80 dark:from-cyan-950/40 dark:to-slate-900/80 dark:border-cyan-500/20',
      sub: 'Atmospheric moisture'
    },
    {
      label: 'Wind Speed',
      value: `${weather.wind_speed ?? 12} km/h`,
      icon: Wind,
      iconColor: 'text-[#607568] dark:text-slate-300',
      containerClass: 'from-slate-500/10 to-slate-500/5 border-[#DCE8DF] dark:from-slate-800/40 dark:to-slate-900/80 dark:border-slate-700/40',
      sub: 'Breeze velocity'
    },
    {
      label: 'Soil Moisture',
      value: `${weather.soil_moisture ?? 62}%`,
      icon: Sparkles,
      iconColor: 'text-[#087A50] dark:text-emerald-400',
      containerClass: 'from-emerald-500/10 to-emerald-500/5 border-emerald-200/80 dark:from-emerald-950/40 dark:to-slate-900/80 dark:border-emerald-500/20',
      sub: 'Root zone moisture'
    },
    {
      label: 'Soil pH',
      value: `${weather.soil_ph ?? 6.5}`,
      icon: TestTube,
      iconColor: 'text-purple-600 dark:text-purple-400',
      containerClass: 'from-purple-500/10 to-purple-500/5 border-purple-200/80 dark:from-purple-950/40 dark:to-slate-900/80 dark:border-purple-500/20',
      sub: 'Optimal neutral-alkaline'
    }
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4">
      {metrics.map((m, idx) => {
        const IconComponent = m.icon;
        return (
          <div
            key={idx}
            className={`p-4 rounded-2xl border bg-gradient-to-b ${m.containerClass} bg-white dark:bg-transparent flex flex-col justify-between transition-all duration-300 hover:scale-103 hover:shadow-md`}
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold text-[#607568] dark:text-slate-300 tracking-wide">{m.label}</span>
              <div className="p-1.5 rounded-xl bg-white/90 border border-[#DCE8DF] dark:bg-slate-900/80 dark:border-slate-800 shadow-2xs">
                <IconComponent className={`w-4 h-4 ${m.iconColor}`} />
              </div>
            </div>
            <div>
              <div className="text-2xl font-black text-[#183C2C] dark:text-white tracking-tight">{m.value}</div>
              <p className="text-[10px] text-[#607568] dark:text-slate-400 font-medium mt-1 truncate">{m.sub}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
