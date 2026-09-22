import React, { useState } from 'react';
import { History, MapPin, TrendingUp, Droplets, Thermometer, Sliders } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

const VIDARBHA_DISTRICTS = ['Akola', 'Amravati', 'Buldhana', 'Nagpur', 'Wardha', 'Washim', 'Yavatmal'];

const HISTORICAL_SERIES = [
  { year: 1997, yield: 180, rainfall: 850, tmax: 33.1 },
  { year: 1999, yield: 210, rainfall: 790, tmax: 33.4 },
  { year: 2001, yield: 195, rainfall: 720, tmax: 34.0 },
  { year: 2003, yield: 235, rainfall: 910, tmax: 32.8 },
  { year: 2005, yield: 260, rainfall: 840, tmax: 33.5 },
  { year: 2007, yield: 310, rainfall: 980, tmax: 32.9 },
  { year: 2009, yield: 275, rainfall: 650, tmax: 34.5 },
  { year: 2011, yield: 340, rainfall: 1050, tmax: 32.2 },
  { year: 2013, yield: 385, rainfall: 1120, tmax: 31.9 },
  { year: 2015, yield: 250, rainfall: 680, tmax: 34.2 },
  { year: 2017, yield: 410, rainfall: 890, tmax: 33.0 },
  { year: 2019, yield: 370, rainfall: 940, tmax: 33.2 },
  { year: 2021, yield: 420, rainfall: 880, tmax: 33.4 },
  { year: 2023, yield: 444, rainfall: 820, tmax: 33.5 },
  { year: 2024, yield: 262, rainfall: 760, tmax: 33.8 },
];

export default function HistoryPage() {
  const [selectedDistrict, setSelectedDistrict] = useState('Akola');
  const [startYear, setStartYear] = useState(1997);
  const [endYear, setEndYear] = useState(2024);

  const filteredData = HISTORICAL_SERIES.filter(
    (item) => item.year >= startYear && item.year <= endYear
  );

  return (
    <div className="space-y-8 py-4 max-w-7xl mx-auto">
      
      {/* Top Header */}
      <div className="border-b border-slate-200 pb-4">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md bg-emerald-50 text-emerald-800 border border-emerald-200 text-xs font-semibold uppercase tracking-wider mb-1">
          <History className="w-3.5 h-3.5 text-emerald-600" />
          <span>Historical Analytics Interface</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Historical Yield & Climate Trends (1997–2024)
        </h1>
        <p className="text-xs text-slate-500 font-normal">
          Explore historical variation across yield, annual rainfall, and Kharif temperatures.
        </p>
      </div>

      {/* FILTERS BAR (Requirement #23) */}
      <div className="agri-card p-4 border border-slate-200 shadow-xs flex flex-wrap items-center justify-between gap-4">
        
        {/* District Filter */}
        <div className="flex items-center gap-2">
          <MapPin className="w-4 h-4 text-emerald-600" />
          <span className="text-xs font-semibold text-slate-700">District:</span>
          <select
            value={selectedDistrict}
            onChange={(e) => setSelectedDistrict(e.target.value)}
            className="bg-slate-50 border border-slate-300 text-slate-900 text-xs rounded-md px-3 py-1.5 font-bold cursor-pointer focus:outline-none"
          >
            {VIDARBHA_DISTRICTS.map((d) => (
              <option key={d} value={d} className="bg-white text-slate-900 font-medium">
                {d}, Vidarbha
              </option>
            ))}
          </select>
        </div>

        {/* Year Range Filter */}
        <div className="flex items-center gap-3 text-xs font-mono">
          <Sliders className="w-4 h-4 text-emerald-600" />
          <span className="font-sans font-semibold text-slate-700">Year Range:</span>
          
          <select
            value={startYear}
            onChange={(e) => setStartYear(Number(e.target.value))}
            className="bg-slate-50 border border-slate-300 text-slate-900 text-xs rounded-md px-2.5 py-1 font-bold cursor-pointer"
          >
            {[1997, 2000, 2005, 2010, 2015, 2020].map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>

          <span className="text-slate-400">to</span>

          <select
            value={endYear}
            onChange={(e) => setEndYear(Number(e.target.value))}
            className="bg-slate-50 border border-slate-300 text-slate-900 text-xs rounded-md px-2.5 py-1 font-bold cursor-pointer"
          >
            {[2010, 2015, 2020, 2023, 2024].map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
        </div>

      </div>

      {/* CHART 1: YIELD TREND */}
      <div className="agri-card p-6 border border-slate-200 space-y-4">
        <div className="border-b border-slate-100 pb-3">
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-emerald-600" />
            <span>Yield Trend ({selectedDistrict})</span>
          </h3>
          <p className="text-xs text-slate-500">Recorded annual cotton yield (kg/ha)</p>
        </div>

        <div className="h-60 w-full pt-1">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={filteredData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="year" stroke="#64748b" fontSize={11} tickLine={false} />
              <YAxis stroke="#64748b" fontSize={11} tickLine={false} unit=" kg/ha" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                formatter={(val) => [`${val} kg/ha`, 'Yield']}
              />
              <Line type="monotone" dataKey="yield" stroke="#059669" strokeWidth={2.5} dot={{ fill: '#059669', r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* CHART 2: RAINFALL TREND */}
      <div className="agri-card p-6 border border-slate-200 space-y-4">
        <div className="border-b border-slate-100 pb-3">
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Droplets className="w-4 h-4 text-emerald-600" />
            <span>Rainfall Trend ({selectedDistrict})</span>
          </h3>
          <p className="text-xs text-slate-500">Annual precipitation (mm)</p>
        </div>

        <div className="h-60 w-full pt-1">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={filteredData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="year" stroke="#64748b" fontSize={11} tickLine={false} />
              <YAxis stroke="#64748b" fontSize={11} tickLine={false} unit=" mm" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                formatter={(val) => [`${val} mm`, 'Rainfall']}
              />
              <Line type="monotone" dataKey="rainfall" stroke="#0d9488" strokeWidth={2.5} dot={{ fill: '#0d9488', r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* CHART 3: TEMPERATURE TREND */}
      <div className="agri-card p-6 border border-slate-200 space-y-4">
        <div className="border-b border-slate-100 pb-3">
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Thermometer className="w-4 h-4 text-emerald-600" />
            <span>Temperature Trend ({selectedDistrict})</span>
          </h3>
          <p className="text-xs text-slate-500">Kharif season mean maximum temperature (°C)</p>
        </div>

        <div className="h-60 w-full pt-1">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={filteredData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="year" stroke="#64748b" fontSize={11} tickLine={false} />
              <YAxis stroke="#64748b" fontSize={11} tickLine={false} domain={[30, 36]} unit=" °C" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                formatter={(val) => [`${val} °C`, 'Kharif Max Temp']}
              />
              <Line type="monotone" dataKey="tmax" stroke="#b45309" strokeWidth={2.5} dot={{ fill: '#b45309', r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

    </div>
  );
}
