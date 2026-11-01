import React, { useState } from 'react';
import {
  AlertCircle,
  ArrowDownRight,
  ArrowUpRight,
  BrainCircuit,
  CheckCircle2,
  Layers,
  Sparkles,
  TrendingDown,
  TrendingUp,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
  ReferenceLine,
} from 'recharts';

export default function WhyThisPrediction({
  prediction,
  loading = false,
  error = null,
  district = '',
  year = 2024,
}) {
  const [activeTab, setActiveTab] = useState('local'); // 'local' | 'global'

  // Loading state
  if (loading) {
    return (
      <div className="agri-card space-y-4 border border-slate-200 p-6 dark:border-slate-700">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 flex items-center justify-center animate-pulse">
            <Sparkles className="h-5 w-5 animate-spin" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-900 dark:text-white">
              Why This Prediction?
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Generating Explainable AI feature attributions (SHAP)…
            </p>
          </div>
        </div>
        <div className="h-32 w-full animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800" />
      </div>
    );
  }

  // Empty state
  if (!prediction) {
    return (
      <div className="agri-card border border-dashed border-slate-300 p-8 text-center dark:border-slate-700">
        <BrainCircuit className="mx-auto h-8 w-8 text-slate-400" />
        <h3 className="mt-2 text-sm font-bold text-slate-700 dark:text-slate-300">
          Why This Prediction?
        </h3>
        <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
          Run or select a cotton yield prediction to view local SHAP explanations and factor contributions.
        </p>
      </div>
    );
  }

  const explanation = prediction?.explanation;
  const isAvailable = explanation?.available !== false;
  const predictedYield = Number(prediction?.predicted_yield_kg_ha ?? 0);
  const baseValue = Number(explanation?.base_value_kg_ha ?? 230.73);
  const deltaFromBase = predictedYield - baseValue;

  const topInfluential = explanation?.top_influential_features || [];
  const topIncreasing = explanation?.increasing_factors || [];
  const topDecreasing = explanation?.decreasing_factors || [];
  const globalShap = prediction?.global_shap_importance;

  // Chart data formatting for local waterfall / diverging bars
  const localChartData = topInfluential.slice(0, 10).map((item) => ({
    name: item.display_name?.length > 30 ? `${item.display_name.slice(0, 28)}…` : item.display_name,
    fullName: item.display_name,
    contribution: Number(item.contribution_kg_ha || 0),
    direction: item.direction,
    category: item.category || 'Agro-Climatic Factor',
    inputValue: item.input_value != null ? item.input_value : 'Observed Panel',
    relImpact: item.relative_impact_pct || 0,
  }));

  // Global chart data
  const globalFeatures = (globalShap?.top_10_features || []).slice(0, 10).map((f) => ({
    name: f.display_name?.length > 30 ? `${f.display_name.slice(0, 28)}…` : f.display_name,
    fullName: f.display_name,
    importance: Number(f.mean_abs_shap_kg_ha || 0),
    relPct: f.relative_importance_pct || 0,
    category: f.category || 'General Factor',
  }));

  return (
    <div className="agri-card space-y-6 border border-emerald-200/80 bg-white p-6 sm:p-7 shadow-sm dark:border-emerald-900/50 dark:bg-slate-900">
      {/* ======================================================
          SECTION 2: EXPLAINABLE AI (SHAP) HEADER & TABS
      ====================================================== */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-slate-100 pb-5 dark:border-slate-800">
        <div className="flex items-start gap-3">
          <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl border border-emerald-200/60 bg-emerald-50 text-emerald-700 dark:border-emerald-800/40 dark:bg-emerald-950/50 dark:text-emerald-400">
            <Sparkles className="h-6 w-6" />
          </div>
          <div>
            <div className="inline-flex items-center gap-1.5 rounded-full bg-emerald-100/70 px-2.5 py-0.5 text-[10px] font-extrabold uppercase tracking-wider text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300">
              <BrainCircuit className="h-3 w-3" />
              Explainable AI (SHAP)
            </div>
            <h2 className="mt-1 text-xl font-black tracking-tight text-slate-900 dark:text-white">
              Why This Prediction?
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Additive SHAP feature attributions for {district || prediction.district} · Season {year || prediction.target_year}
            </p>
          </div>
        </div>

        {/* Tab switch */}
        <div className="flex items-center gap-1.5 rounded-xl bg-slate-100 p-1 text-xs font-bold dark:bg-slate-800/80 self-start sm:self-auto">
          <button
            type="button"
            onClick={() => setActiveTab('local')}
            className={`rounded-lg px-3.5 py-1.5 transition-all ${
              activeTab === 'local'
                ? 'bg-white text-emerald-700 shadow-xs dark:bg-slate-700 dark:text-emerald-300'
                : 'text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white'
            }`}
          >
            Local Attribution
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('global')}
            className={`rounded-lg px-3.5 py-1.5 transition-all ${
              activeTab === 'global'
                ? 'bg-white text-emerald-700 shadow-xs dark:bg-slate-700 dark:text-emerald-300'
                : 'text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white'
            }`}
          >
            Regional Importance
          </button>
        </div>
      </div>

      {activeTab === 'local' ? (
        <>
          {/* Summary Cards Row: Model Prediction, Regional Baseline, Net Feature Impact */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="rounded-2xl border border-emerald-200 bg-gradient-to-br from-emerald-50/70 via-teal-50/30 to-white p-4 dark:border-emerald-900/60 dark:from-emerald-950/40 dark:via-teal-950/20 dark:to-slate-900">
              <span className="text-[10px] font-extrabold uppercase tracking-wider text-emerald-700 dark:text-emerald-400">
                Model Prediction
              </span>
              <div className="mt-1 flex items-baseline gap-1.5">
                <span className="font-mono text-3xl font-black text-emerald-900 dark:text-emerald-200">
                  {predictedYield.toFixed(1)}
                </span>
                <span className="text-xs font-bold text-emerald-700 dark:text-emerald-400">
                  kg/ha
                </span>
              </div>
              <p className="mt-1 text-[11px] text-emerald-800/80 dark:text-emerald-300/80">
                Final point estimate for {district || prediction.district}
              </p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50/80 p-4 dark:border-slate-800 dark:bg-slate-800/50">
              <span className="text-[10px] font-extrabold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                Regional Baseline E[f(X)]
              </span>
              <div className="mt-1 flex items-baseline gap-1.5">
                <span className="font-mono text-3xl font-black text-slate-900 dark:text-white">
                  {baseValue.toFixed(1)}
                </span>
                <span className="text-xs font-bold text-slate-500">kg/ha</span>
              </div>
              <p className="mt-1 text-[11px] text-slate-500 dark:text-slate-400">
                Expected regional yield before input anomalies
              </p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50/80 p-4 dark:border-slate-800 dark:bg-slate-800/50">
              <span className="text-[10px] font-extrabold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                Net Feature Impact
              </span>
              <div className="mt-1 flex items-baseline gap-1.5">
                <span
                  className={`font-mono text-3xl font-black ${
                    deltaFromBase >= 0
                      ? 'text-emerald-700 dark:text-emerald-400'
                      : 'text-rose-600 dark:text-rose-400'
                  }`}
                >
                  {deltaFromBase >= 0 ? `+${deltaFromBase.toFixed(1)}` : deltaFromBase.toFixed(1)}
                </span>
                <span className="text-xs font-bold text-slate-500">kg/ha</span>
              </div>
              <p className="mt-1 text-[11px] text-slate-500 dark:text-slate-400">
                {deltaFromBase >= 0 ? 'Net positive agro-climatic support' : 'Net negative seasonal stress'}
              </p>
            </div>
          </div>

          {/* Explanation fallback notice if not available */}
          {!isAvailable ? (
            <div className="flex items-start gap-3 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-xs text-amber-800 dark:border-amber-900/60 dark:bg-amber-950/40 dark:text-amber-300">
              <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-amber-600" />
              <div>
                <p className="font-bold">Explanation fallback notice</p>
                <p className="mt-0.5">
                  Detailed SHAP attributions could not be extracted for this input combination. The model prediction remains valid.
                </p>
              </div>
            </div>
          ) : (
            <>
              {/* Natural language summary narrative box */}
              <div className="rounded-2xl border border-emerald-200 bg-emerald-50/50 p-4 sm:p-5 dark:border-emerald-900/40 dark:bg-emerald-950/30">
                <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-emerald-800 dark:text-emerald-300">
                  <CheckCircle2 className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
                  Model Explanation Narrative
                </div>
                <p className="mt-2 text-sm leading-relaxed text-slate-700 dark:text-slate-200">
                  {explanation?.summary_text || 'Statistical feature attribution calculated successfully.'}
                </p>
              </div>

              {/* ======================================================
                  SECTION 3: FEATURE IMPACT ANALYSIS (BALANCED COLUMNS)
              ====================================================== */}
              <div className="space-y-4 pt-1">
                <div className="flex items-center justify-between border-b border-slate-100 pb-2 dark:border-slate-800">
                  <div className="flex items-center gap-2">
                    <Layers className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
                    <h3 className="text-xs font-extrabold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                      Feature Impact Analysis
                    </h3>
                  </div>
                  <span className="text-[11px] text-slate-500">
                    Balanced Positive & Negative Decomposition
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  {/* Left Column: Positive Factors (Green styling) */}
                  <div className="space-y-3 rounded-2xl border border-emerald-200 bg-emerald-50/25 p-4 dark:border-emerald-900/50 dark:bg-emerald-950/15">
                    <div className="flex items-center justify-between border-b border-emerald-200/70 pb-2 dark:border-emerald-900/50">
                      <span className="flex items-center gap-1.5 text-xs font-bold text-emerald-800 dark:text-emerald-300">
                        <TrendingUp className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
                        Factors Promoting Higher Yield
                      </span>
                      <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-extrabold text-emerald-800 dark:bg-emerald-900/60 dark:text-emerald-200">
                        {topIncreasing.length} Factors
                      </span>
                    </div>

                    <div className="space-y-2.5">
                      {topIncreasing.slice(0, 5).map((f, idx) => (
                        <div
                          key={f.feature || idx}
                          className="rounded-xl border border-emerald-200/70 bg-white p-3 shadow-2xs dark:border-emerald-900/40 dark:bg-slate-800/80"
                        >
                          <div className="flex items-start justify-between gap-2">
                            <span className="text-xs font-bold text-slate-900 dark:text-white">
                              {f.display_name}
                            </span>
                            <span className="inline-flex shrink-0 items-center gap-0.5 text-[10px] font-bold text-emerald-700 dark:text-emerald-400">
                              <ArrowUpRight className="h-3 w-3" />
                              Supports Yield
                            </span>
                          </div>

                          <div className="mt-2 flex items-baseline justify-between text-xs">
                            <span className="font-mono text-sm font-black text-emerald-700 dark:text-emerald-400">
                              +{Number(f.contribution_kg_ha).toFixed(2)} kg/ha
                            </span>
                            <span className="text-[11px] font-medium text-slate-500 dark:text-slate-400">
                              {f.relative_impact_pct}% impact
                            </span>
                          </div>

                          {f.input_value != null && (
                            <div className="mt-2 flex justify-between border-t border-slate-100 pt-1.5 text-[10px] text-slate-500 dark:border-slate-700 dark:text-slate-400">
                              <span>Observed Input Value:</span>
                              <span className="font-mono font-bold text-slate-700 dark:text-slate-300">
                                {f.input_value}
                              </span>
                            </div>
                          )}
                        </div>
                      ))}
                      {topIncreasing.length === 0 && (
                        <p className="p-3 text-center text-xs italic text-slate-500">
                          No major promoting factors for this observation.
                        </p>
                      )}
                    </div>
                  </div>

                  {/* Right Column: Negative Factors (Red styling) */}
                  <div className="space-y-3 rounded-2xl border border-rose-200 bg-rose-50/25 p-4 dark:border-rose-900/50 dark:bg-rose-950/15">
                    <div className="flex items-center justify-between border-b border-rose-200/70 pb-2 dark:border-rose-900/50">
                      <span className="flex items-center gap-1.5 text-xs font-bold text-rose-800 dark:text-rose-300">
                        <TrendingDown className="h-4 w-4 text-rose-600 dark:text-rose-400" />
                        Factors Suppressing Yield Potential
                      </span>
                      <span className="rounded-full bg-rose-100 px-2 py-0.5 text-[10px] font-extrabold text-rose-800 dark:bg-rose-900/60 dark:text-rose-200">
                        {topDecreasing.length} Factors
                      </span>
                    </div>

                    <div className="space-y-2.5">
                      {topDecreasing.slice(0, 5).map((f, idx) => (
                        <div
                          key={f.feature || idx}
                          className="rounded-xl border border-rose-200/70 bg-white p-3 shadow-2xs dark:border-rose-900/40 dark:bg-slate-800/80"
                        >
                          <div className="flex items-start justify-between gap-2">
                            <span className="text-xs font-bold text-slate-900 dark:text-white">
                              {f.display_name}
                            </span>
                            <span className="inline-flex shrink-0 items-center gap-0.5 text-[10px] font-bold text-rose-700 dark:text-rose-400">
                              <ArrowDownRight className="h-3 w-3" />
                              Reduces Yield
                            </span>
                          </div>

                          <div className="mt-2 flex items-baseline justify-between text-xs">
                            <span className="font-mono text-sm font-black text-rose-600 dark:text-rose-400">
                              {Number(f.contribution_kg_ha).toFixed(2)} kg/ha
                            </span>
                            <span className="text-[11px] font-medium text-slate-500 dark:text-slate-400">
                              {f.relative_impact_pct}% impact
                            </span>
                          </div>

                          {f.input_value != null && (
                            <div className="mt-2 flex justify-between border-t border-slate-100 pt-1.5 text-[10px] text-slate-500 dark:border-slate-700 dark:text-slate-400">
                              <span>Observed Input Value:</span>
                              <span className="font-mono font-bold text-slate-700 dark:text-slate-300">
                                {f.input_value}
                              </span>
                            </div>
                          )}
                        </div>
                      ))}
                      {topDecreasing.length === 0 && (
                        <p className="p-3 text-center text-xs italic text-slate-500">
                          No major suppressing factors identified.
                        </p>
                      )}
                    </div>
                  </div>
                </div>

                {/* SHAP Contribution Diverging Chart immediately below */}
                <div className="mt-4 space-y-2 rounded-2xl border border-slate-200 bg-slate-50/50 p-4 sm:p-5 dark:border-slate-800 dark:bg-slate-950/40">
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1">
                    <div>
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200">
                        SHAP Contribution Diverging Chart (kg/ha)
                      </h4>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400">
                        Green bars indicate positive adjustment toward prediction; Red bars indicate negative adjustment relative to baseline.
                      </p>
                    </div>
                    <span className="text-[11px] font-mono text-slate-500 dark:text-slate-400">
                      Baseline: {baseValue.toFixed(1)} kg/ha
                    </span>
                  </div>

                  <div className="h-80 sm:h-96 w-full pt-2">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={localChartData}
                        layout="vertical"
                        margin={{ top: 5, right: 30, left: 15, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--chart-grid, #DCE8DF)" />
                        <XAxis type="number" fontSize={11} tickFormatter={(val) => `${val} kg`} />
                        <YAxis
                          type="category"
                          dataKey="name"
                          width={210}
                          fontSize={11}
                          tickLine={false}
                          axisLine={false}
                        />
                        <ReferenceLine x={0} stroke="#64748b" strokeWidth={1.5} />
                        <Tooltip
                          content={({ active, payload }) => {
                            if (active && payload && payload.length) {
                              const data = payload[0].payload;
                              return (
                                <div className="rounded-xl border border-slate-200 bg-white p-3 shadow-lg text-xs dark:border-slate-700 dark:bg-slate-900">
                                  <p className="font-bold text-slate-900 dark:text-white">{data.fullName}</p>
                                  <p className="text-[11px] text-slate-500">Category: {data.category}</p>
                                  <div className="mt-2 border-t border-slate-100 pt-1.5 flex justify-between gap-4 font-mono font-bold dark:border-slate-800">
                                    <span>Contribution:</span>
                                    <span className={data.contribution >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}>
                                      {data.contribution >= 0 ? `+${data.contribution.toFixed(2)}` : data.contribution.toFixed(2)} kg/ha
                                    </span>
                                  </div>
                                  <div className="flex justify-between gap-4 text-[11px] text-slate-500 mt-1">
                                    <span>Relative share:</span>
                                    <span>{data.relImpact}%</span>
                                  </div>
                                  <div className="flex justify-between gap-4 text-[11px] text-slate-500 mt-0.5">
                                    <span>Observed value:</span>
                                    <span className="font-mono text-slate-700 dark:text-slate-300">{data.inputValue}</span>
                                  </div>
                                </div>
                              );
                            }
                            return null;
                          }}
                        />
                        <Bar dataKey="contribution" radius={[0, 4, 4, 0]}>
                          {localChartData.map((entry, index) => (
                            <Cell
                              key={`cell-${index}`}
                              fill={entry.contribution >= 0 ? '#087A50' : '#C53030'}
                            />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            </>
          )}
        </>
      ) : (
        /* Global Regional Importance Tab */
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
            <div>
              <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                Global Regional Feature Importance (Vidarbha Panel 1997–2023)
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Mean absolute SHAP value across all authentic historical training observations.
              </p>
            </div>
            <span className="rounded-full bg-slate-100 px-3 py-1 text-[11px] font-bold text-slate-600 dark:bg-slate-800 dark:text-slate-400 self-start sm:self-auto">
              187 historical records
            </span>
          </div>

          <div className="h-80 sm:h-96 w-full rounded-2xl border border-slate-200 bg-slate-50/50 p-4 dark:border-slate-800 dark:bg-slate-950/40">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={globalFeatures}
                layout="vertical"
                margin={{ top: 5, right: 30, left: 15, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--chart-grid, #DCE8DF)" />
                <XAxis type="number" fontSize={11} tickFormatter={(val) => `${val} kg`} />
                <YAxis
                  type="category"
                  dataKey="name"
                  width={210}
                  fontSize={11}
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip
                  formatter={(val, name, item) => [
                    `${Number(val).toFixed(2)} kg/ha (${item.payload.relPct}%)`,
                    'Mean |SHAP| Impact',
                  ]}
                />
                <Bar dataKey="importance" fill="#087A50" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Category breakdown table */}
          {globalShap?.category_summary && (
            <div className="rounded-2xl border border-slate-200 bg-white overflow-hidden dark:border-slate-800 dark:bg-slate-900">
              <div className="bg-slate-50 px-4 py-2.5 text-xs font-bold text-slate-700 dark:bg-slate-800/60 dark:text-slate-300">
                Regional Importance by Factor Category
              </div>
              <div className="divide-y divide-slate-100 dark:divide-slate-800">
                {globalShap.category_summary.map((cat) => (
                  <div key={cat.category} className="px-4 py-2.5 flex items-center justify-between text-xs">
                    <span className="font-medium text-slate-700 dark:text-slate-300">{cat.category}</span>
                    <div className="flex items-center gap-4">
                      <span className="font-mono text-slate-500">{cat.mean_abs_shap_kg_ha} kg/ha</span>
                      <span className="font-bold text-emerald-700 dark:text-emerald-400 w-12 text-right">
                        {cat.relative_importance_pct}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
