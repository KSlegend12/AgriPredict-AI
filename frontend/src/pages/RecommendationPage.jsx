import React, { useState } from 'react';
import { ShieldCheck, CloudSun, History, Layers, MapPin, AlertCircle, Info } from 'lucide-react';

const VIDARBHA_DISTRICTS = ['Akola', 'Amravati', 'Buldhana', 'Nagpur', 'Wardha', 'Washim', 'Yavatmal'];

export default function RecommendationPage({ selectedDistrict, setSelectedDistrict }) {
  const currentDistrict = VIDARBHA_DISTRICTS.includes(selectedDistrict) ? selectedDistrict : 'Akola';

  return (
    <div className="space-y-8 py-4 max-w-7xl mx-auto">
      
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-slate-200 pb-4 gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md bg-emerald-50 text-emerald-800 border border-emerald-200 text-xs font-semibold uppercase tracking-wider mb-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span>Agricultural Decision Support</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Decision Support & Advisory Signals
          </h1>
          <p className="text-xs text-slate-500 font-normal">
            Evidence-based advisory signals derived from weather, historical momentum, and model feature attributions.
          </p>
        </div>

        {/* District Selector */}
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

      {/* Advisory Disclaimer Banner */}
      <div className="p-4 rounded-md bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-center gap-3">
        <AlertCircle className="w-5 h-5 text-amber-600 shrink-0" />
        <div>
          <span className="font-bold block">Decision Support Disclaimer</span>
          <span>Advisory signals provided below are data-driven estimates designed for decision support. They do not constitute guaranteed agronomical advice.</span>
        </div>
      </div>

      {/* SECTION 1: WEATHER INSIGHT (Weather-based) */}
      <div className="agri-card p-6 border border-slate-200 space-y-4">
        <div className="border-b border-slate-100 pb-3 flex items-center justify-between">
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <CloudSun className="w-4 h-4 text-emerald-600" />
            <span>Weather Insight</span>
          </h2>
          <span className="text-[10px] font-mono bg-blue-50 text-blue-800 px-2.5 py-0.5 rounded-md font-bold border border-blue-200">
            Weather-based
          </span>
        </div>

        <div className="space-y-3 text-xs text-slate-700">
          <div className="p-4 rounded-lg bg-slate-50 border border-slate-200 space-y-1">
            <span className="font-bold text-slate-900 block">Monsoon Dry Spell Management ({currentDistrict})</span>
            <p className="text-slate-600 leading-relaxed font-normal">
              IMD historical records for {currentDistrict} indicate average monsoon dry spells of 14–22 days. Supplemental drip irrigation during flowering (August–September) is advised to prevent boll shedding during extended dry periods.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-slate-50 border border-slate-200 space-y-1">
            <span className="font-bold text-slate-900 block">Kharif High Temperature Mitigation</span>
            <p className="text-slate-600 leading-relaxed font-normal">
              When Kharif mean maximum temperatures exceed 34.0°C, soil moisture evaporation accelerates. Maintain organic mulching in cotton inter-rows to retain soil moisture.
            </p>
          </div>
        </div>
      </div>

      {/* SECTION 2: HISTORICAL INSIGHT (Historical-data-based) */}
      <div className="agri-card p-6 border border-slate-200 space-y-4">
        <div className="border-b border-slate-100 pb-3 flex items-center justify-between">
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <History className="w-4 h-4 text-emerald-600" />
            <span>Historical Insight</span>
          </h2>
          <span className="text-[10px] font-mono bg-emerald-50 text-emerald-800 px-2.5 py-0.5 rounded-md font-bold border border-emerald-200">
            Historical-data-based
          </span>
        </div>

        <div className="space-y-3 text-xs text-slate-700">
          <div className="p-4 rounded-lg bg-slate-50 border border-slate-200 space-y-1">
            <span className="font-bold text-slate-900 block">Yield Momentum Analysis (1997–2024 Records)</span>
            <p className="text-slate-600 leading-relaxed font-normal">
              Historical yield data demonstrates strong auto-correlation between prior year yield (t-1) and current harvest yield in {currentDistrict}. High previous harvest yields reflect favorable soil nutrient reserves and pest management continuity.
            </p>
          </div>
        </div>
      </div>

      {/* SECTION 3: MODEL INSIGHT (Model-based) */}
      <div className="agri-card p-6 border border-slate-200 space-y-4">
        <div className="border-b border-slate-100 pb-3 flex items-center justify-between">
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Layers className="w-4 h-4 text-emerald-600" />
            <span>Model Insight</span>
          </h2>
          <span className="text-[10px] font-mono bg-purple-50 text-purple-800 px-2.5 py-0.5 rounded-md font-bold border border-purple-200">
            Model-based
          </span>
        </div>

        <div className="space-y-3 text-xs text-slate-700">
          <div className="p-4 rounded-lg bg-slate-50 border border-slate-200 space-y-1">
            <span className="font-bold text-slate-900 block">Random Forest + SHAP Feature Weights</span>
            <p className="text-slate-600 leading-relaxed font-normal">
              Feature attribution analysis reveals that prior lag yield and Kharif maximum temperature account for over 50% of model prediction variance. Prioritize field soil health and heat stress monitoring during peak vegetative stages.
            </p>
          </div>
        </div>
      </div>

    </div>
  );
}
