import React from 'react';
import { Thermometer, CloudRain, Droplets, Wind, TestTube, Sparkles } from 'lucide-react';

export default function WeatherCard({ weather }) {
  if (!weather) return null;

  const metrics = [
    {
      label: 'Temperature',
      value: `${weather.temperature ?? 27}°C`,
      icon: Thermometer,
      color: 'text-amber-400',
      bg: 'from-amber-950/40 to-slate-900/80 border-amber-500/20',
      sub: `Feels like ${weather.feels_like ?? weather.temperature ?? 27}°C`
    },
    {
      label: 'Rainfall',
      value: `${weather.rainfall ?? 650} mm`,
      icon: CloudRain,
      color: 'text-blue-400',
      bg: 'from-blue-950/40 to-slate-900/80 border-blue-500/20',
      sub: 'Annual avg for district'
    },
    {
      label: 'Humidity',
      value: `${weather.humidity ?? 70}%`,
      icon: Droplets,
      color: 'text-cyan-400',
      bg: 'from-cyan-950/40 to-slate-900/80 border-cyan-500/20',
      sub: 'Atmospheric moisture'
    },
    {
      label: 'Wind Speed',
      value: `${weather.wind_speed ?? 12} km/h`,
      icon: Wind,
      color: 'text-slate-300',
      bg: 'from-slate-800/40 to-slate-900/80 border-slate-700/40',
      sub: 'Breeze velocity'
    },
    {
      label: 'Soil Moisture',
      value: `${weather.soil_moisture ?? 62}%`,
      icon: Sparkles,
      color: 'text-emerald-400',
      bg: 'from-emerald-950/40 to-slate-900/80 border-emerald-500/20',
      sub: 'Root zone moisture'
    },
    {
      label: 'Soil pH',
      value: `${weather.soil_ph ?? 6.5}`,
      icon: TestTube,
      color: 'text-purple-400',
      bg: 'from-purple-950/40 to-slate-900/80 border-purple-500/20',
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
            className={`p-4 rounded-2xl border bg-gradient-to-b ${m.bg} flex flex-col justify-between transition-all duration-300 hover:scale-103 hover:shadow-lg`}
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold text-slate-300 tracking-wide">{m.label}</span>
              <div className="p-1.5 rounded-xl bg-slate-900/80 border border-slate-800">
                <IconComponent className={`w-4 h-4 ${m.color}`} />
              </div>
            </div>
            <div>
              <div className="text-2xl font-black text-white tracking-tight">{m.value}</div>
              <p className="text-[10px] text-slate-400 font-medium mt-1 truncate">{m.sub}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
