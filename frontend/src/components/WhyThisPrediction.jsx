import React, { useState } from 'react';
import {
  AlertCircle,
  ArrowDownRight,
  ArrowUpRight,
  BarChart2,
  BrainCircuit,
  CheckCircle2,
  HelpCircle,
  Info,
  Layers,
  ShieldAlert,
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
          Run or select a cotton yield prediction above to view local SHAP explanations and factor contributions.
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
  const waterfallSteps = explanation?.waterfall_steps || [];
  const globalShap = prediction?.global_shap_importance;
  const uncertainty = explanation?.uncertainty_notice;

  // Chart data formatting for local waterfall / diverging bars
  const localChartData = topInfluential.slice(0, 8).map((item) => ({
    name: item.display_name?.length > 28 ? `${item.display_name.slice(0, 26)}…` : item.display_name,
    fullName: item.display_name,
    contribution: Number(item.contribution_kg_ha || 0),
    direction: item.direction,
    category: item.category || 'Agro-Climatic Factor',
    inputValue: item.input_value != null ? item.input_value : 'Observed Panel',
    relImpact: item.relative_impact_pct || 0,
  }));

  // Global chart data
  const globalFeatures = (globalShap?.top_10_features || []).slice(0, 8).map((f) => ({
    name: f.display_name?.length > 28 ? `${f.display_name.slice(0, 26)}…` : f.display_name,
    fullName: f.display_name,
    importance: Number(f.mean_abs_shap_kg_ha || 0),
    relPct: f.relative_importance_pct || 0,
    category: f.category || 'General Factor',
  }));

  return (
    <div className="agri-card space-y-6 border border-emerald-200/70 dark:border-emerald-900/50 p-6 sm:p-7 bg-white dark:bg-slate-900 shadow-sm">
      {/* Header with prominent predicted yield and tabs */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-slate-100 dark:border-slate-800 pb-5">
        <div className="flex items-start gap-3">
          <div className="h-11 w-11 rounded-2xl bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-400 flex items-center justify-center shrink-0 border border-emerald-200/50 dark:border-emerald-800/40">
            <Sparkles className="h-6 w-6" />
          </div>
          <div>
            <div className="inline-flex items-center gap-1.5 rounded-full bg-emerald-100/70 dark:bg-emerald-950/60 px-2.5 py-0.5 text-[10px] font-extrabold uppercase tracking-wider text-emerald-800 dark:text-emerald-300">
              <BrainCircuit className="h-3 w-3" />
              Explainable AI (XAI) Module
            </div>
            <h2 className="mt-1 text-xl font-black text-slate-900 dark:text-white tracking-tight">
              Why This Prediction?
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              SHAP TreeExplainer feature attributions for {district || prediction.district} ({year || prediction.target_year})
            </p>
          </div>
        </div>

        {/* Tab switch */}
        <div className="flex items-center gap-1.5 bg-slate-100 dark:bg-slate-800/80 p-1 rounded-xl self-start sm:self-auto text-xs font-bold">
          <button
            type="button"
            onClick={() => setActiveTab('local')}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              activeTab === 'local'
                ? 'bg-white dark:bg-slate-700 text-emerald-700 dark:text-emerald-300 shadow-xs'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            Local Attribution
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('global')}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              activeTab === 'global'
                ? 'bg-white dark:bg-slate-700 text-emerald-700 dark:text-emerald-300 shadow-xs'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            Regional Importance
          </button>
        </div>
      </div>

      {/* Prominent Predicted Yield Card */}
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-2xl border border-emerald-200 bg-gradient-to-br from-emerald-50/60 to-teal-50/30 dark:border-emerald-900/60 dark:from-emerald-950/30 dark:to-teal-950/20 p-4">
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

        <div className="rounded-2xl border border-slate-200 bg-slate-50 dark:border-slate-800 dark:bg-slate-800/50 p-4">
          <span className="text-[10px] font-extrabold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            Regional Baseline E[f(x)]
          </span>
          <div className="mt-1 flex items-baseline gap-1.5">
            <span className="font-mono text-3xl font-black text-slate-900 dark:text-white">
              {baseValue.toFixed(1)}
            </span>
            <span className="text-xs font-bold text-slate-500">kg/ha</span>
          </div>
          <p className="mt-1 text-[11px] text-slate-500 dark:text-slate-400">
            SHAP expected value before input features
          </p>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-slate-50 dark:border-slate-800 dark:bg-slate-800/50 p-4">
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
            {deltaFromBase >= 0 ? 'Net positive agro-climatic shift' : 'Net negative stress reduction'}
          </p>
        </div>
      </div>

      {/* Main Content Area based on Tab */}
      {activeTab === 'local' ? (
        <>
          {/* Explanation fallback warning if not available */}
          {!isAvailable ? (
            <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-xs text-amber-800 dark:border-amber-900/60 dark:bg-amber-950/40 dark:text-amber-300 flex items-start gap-3">
              <AlertCircle className="h-5 w-5 shrink-0 text-amber-600 mt-0.5" />
              <div>
                <p className="font-bold">Explanation fallback notice</p>
                <p className="mt-0.5">
                  Detailed SHAP attributions could not be extracted for this input combination. The model prediction remains valid.
                </p>
              </div>
            </div>
          ) : (
            <>
              {/* Natural language summary box */}
              <div className="rounded-2xl border border-emerald-200 bg-emerald-50/50 dark:border-emerald-900/40 dark:bg-emerald-950/30 p-4 sm:p-5">
                <div className="flex items-center gap-2 text-emerald-800 dark:text-emerald-300 font-bold text-xs uppercase tracking-wider">
                  <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                  Model Explanation Narrative
                </div>
                <p className="mt-2 text-sm leading-relaxed text-slate-700 dark:text-slate-200">
                  {explanation?.summary_text || 'Statistical attribution calculated successfully.'}
                </p>
              </div>

              {/* Top 3-5 influential factors cards */}
              <div>
                <h3 className="text-xs font-extrabold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-3 flex items-center gap-1.5">
                  <Layers className="h-4 w-4 text-emerald-600" />
                  Top Influencing Factors for This Prediction
                </h3>
                <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                  {topInfluential.slice(0, 3).map((factor, idx) => {
                    const isPos = factor.direction === 'positive';
                    return (
                      <div
                        key={factor.feature || idx}
                        className={`rounded-2xl border p-4 transition-all ${
                          isPos
                            ? 'border-emerald-200 bg-emerald-50/30 dark:border-emerald-900/40 dark:bg-emerald-950/20'
                            : 'border-rose-200 bg-rose-50/30 dark:border-rose-900/40 dark:bg-rose-950/20'
                        }`}
                      >
                        <div className="flex items-center justify-between text-[11px]">
                          <span className="font-bold text-slate-500 dark:text-slate-400">
                            #{idx + 1} Factor
                          </span>
                          <span
                            className={`inline-flex items-center gap-0.5 px-2 py-0.5 rounded-full text-[10px] font-extrabold ${
                              isPos
                                ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/60 dark:text-emerald-200'
                                : 'bg-rose-100 text-rose-800 dark:bg-rose-900/60 dark:text-rose-200'
                            }`}
                          >
                            {isPos ? (
                              <>
                                <ArrowUpRight className="h-3 w-3" /> Supports Yield
                              </>
                            ) : (
                              <>
                                <ArrowDownRight className="h-3 w-3" /> Reduces Yield
                              </>
                            )}
                          </span>
                        </div>

                        <h4 className="mt-2 text-sm font-bold text-slate-900 dark:text-white line-clamp-1">
                          {factor.display_name}
                        </h4>

                        <div className="mt-3 flex items-baseline justify-between">
                          <span className="font-mono text-xl font-black text-slate-900 dark:text-white">
                            {isPos ? `+${factor.contribution_kg_ha}` : factor.contribution_kg_ha}{' '}
                            <span className="text-xs font-semibold text-slate-500">kg/ha</span>
                          </span>
                          <span className="text-xs font-medium text-slate-500">
                            {factor.relative_impact_pct}% impact
                          </span>
                        </div>

                        {factor.input_value != null && (
                          <div className="mt-2 pt-2 border-t border-slate-200/60 dark:border-slate-800 flex justify-between text-[11px] text-slate-500">
                            <span>Input value:</span>
                            <span className="font-mono font-bold text-slate-700 dark:text-slate-300">
                              {factor.input_value}
                            </span>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Feature Contribution Chart */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-xs font-extrabold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                      SHAP Contribution Diverging Chart (kg/ha)
                    </h3>
                    <p className="text-[11px] text-slate-500">
                      Green indicates positive adjustment toward prediction; Red indicates negative adjustment.
                    </p>
                  </div>
                </div>

                <div className="h-72 w-full rounded-2xl border border-slate-200 bg-slate-50/50 dark:border-slate-800 dark:bg-slate-950/40 p-4">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={localChartData}
                      layout="vertical"
                      margin={{ top: 5, right: 30, left: 10, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#cbd5e1" opacity={0.5} />
                      <XAxis type="number" fontSize={11} tickFormatter={(val) => `${val} kg`} />
                      <YAxis
                        type="category"
                        dataKey="name"
                        width={180}
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
                              <div className="rounded-xl border border-slate-200 bg-white p-3 shadow-lg dark:border-slate-700 dark:bg-slate-900 text-xs">
                                <p className="font-bold text-slate-900 dark:text-white">{data.fullName}</p>
                                <p className="text-[11px] text-slate-500">Category: {data.category}</p>
                                <div className="mt-2 border-t border-slate-100 dark:border-slate-800 pt-1.5 flex justify-between gap-4 font-mono font-bold">
                                  <span>Contribution:</span>
                                  <span className={data.contribution >= 0 ? 'text-emerald-600' : 'text-rose-600'}>
                                    {data.contribution >= 0 ? `+${data.contribution}` : data.contribution} kg/ha
                                  </span>
                                </div>
                                <div className="flex justify-between gap-4 text-[11px] text-slate-500 mt-1">
                                  <span>Relative share:</span>
                                  <span>{data.relImpact}%</span>
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
                            fill={entry.contribution >= 0 ? '#10b981' : '#f43f5e'}
                          />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Factors Breakdown Columns (Increasing vs Decreasing) */}
              <div className="grid gap-5 md:grid-cols-2 pt-2">
                <div className="space-y-3 rounded-2xl border border-emerald-100 bg-emerald-50/20 dark:border-emerald-950 dark:bg-emerald-950/10 p-4">
                  <h4 className="flex items-center gap-1.5 text-xs font-bold text-emerald-800 dark:text-emerald-300">
                    <TrendingUp className="h-4 w-4" />
                    Factors Promoting Higher Yield ({topIncreasing.length})
                  </h4>
                  <div className="space-y-2">
                    {topIncreasing.slice(0, 4).map((f) => (
                      <div
                        key={f.feature}
                        className="flex items-center justify-between text-xs bg-white dark:bg-slate-800 p-2.5 rounded-xl border border-slate-100 dark:border-slate-700"
                      >
                        <span className="font-medium text-slate-700 dark:text-slate-300 truncate max-w-[220px]">
                          {f.display_name}
                        </span>
                        <span className="font-mono font-bold text-emerald-700 dark:text-emerald-400">
                          +{f.contribution_kg_ha} kg/ha
                        </span>
                      </div>
                    ))}
                    {topIncreasing.length === 0 && (
                      <p className="text-xs text-slate-500 italic p-2">No major positive factors for this scenario.</p>
                    )}
                  </div>
                </div>

                <div className="space-y-3 rounded-2xl border border-rose-100 bg-rose-50/20 dark:border-rose-950 dark:bg-rose-950/10 p-4">
                  <h4 className="flex items-center gap-1.5 text-xs font-bold text-rose-700 dark:text-rose-400">
                    <TrendingDown className="h-4 w-4" />
                    Factors Suppressing Yield Potential ({topDecreasing.length})
                  </h4>
                  <div className="space-y-2">
                    {topDecreasing.slice(0, 4).map((f) => (
                      <div
                        key={f.feature}
                        className="flex items-center justify-between text-xs bg-white dark:bg-slate-800 p-2.5 rounded-xl border border-slate-100 dark:border-slate-700"
                      >
                        <span className="font-medium text-slate-700 dark:text-slate-300 truncate max-w-[220px]">
                          {f.display_name}
                        </span>
                        <span className="font-mono font-bold text-rose-600 dark:text-rose-400">
                          {f.contribution_kg_ha} kg/ha
                        </span>
                      </div>
                    ))}
                    {topDecreasing.length === 0 && (
                      <p className="text-xs text-slate-500 italic p-2">No major suppressing factors identified.</p>
                    )}
                  </div>
                </div>
              </div>
            </>
          )}
        </>
      ) : (
        /* Global Regional Importance Tab */
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                Global Regional Feature Importance (Vidarbha Panel 1997–2023)
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Mean absolute SHAP value across all historical training observations.
              </p>
            </div>
            <span className="rounded-full bg-slate-100 dark:bg-slate-800 px-3 py-1 text-[11px] font-bold text-slate-600 dark:text-slate-400">
              187 historical records
            </span>
          </div>

          <div className="h-80 w-full rounded-2xl border border-slate-200 bg-slate-50/50 dark:border-slate-800 dark:bg-slate-950/40 p-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={globalFeatures}
                layout="vertical"
                margin={{ top: 5, right: 30, left: 10, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#cbd5e1" opacity={0.5} />
                <XAxis type="number" fontSize={11} tickFormatter={(val) => `${val} kg`} />
                <YAxis
                  type="category"
                  dataKey="name"
                  width={180}
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
                <Bar dataKey="importance" fill="#0d9488" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Category breakdown table */}
          {globalShap?.category_summary && (
            <div className="rounded-2xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900 overflow-hidden">
              <div className="bg-slate-50 dark:bg-slate-800/60 px-4 py-2.5 text-xs font-bold text-slate-700 dark:text-slate-300">
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

      {/* Uncertainty and Agronomic Disclaimer Notice */}
      <div className="rounded-2xl border border-amber-200 bg-amber-50/70 dark:border-amber-900/50 dark:bg-amber-950/20 p-4 sm:p-5 text-xs leading-relaxed text-amber-900 dark:text-amber-200 space-y-2">
        <div className="flex items-center gap-2 font-bold text-amber-800 dark:text-amber-300">
          <ShieldAlert className="h-4 w-4 shrink-0 text-amber-600" />
          <span>Model Uncertainty & Non-Causal Agronomic Disclaimer</span>
        </div>
        <p>
          {uncertainty?.interpretation_guideline ||
            'Feature contributions represent statistical associations identified by the Gradient Boosting model over historical regional data; they do NOT establish biological cause-and-effect.'}
        </p>
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 pt-1 border-t border-amber-200/60 dark:border-amber-900/40 text-[11px] text-amber-800/90 dark:text-amber-300/90 font-medium">
          <span>
            <b>Validation Baseline:</b> 2011–2023 expanding-window Mean Absolute Error: 106.2 kg/ha.
          </span>
          {uncertainty?.plausible_range_kg_ha && (
            <span className="font-mono">
              Expected plausible range: <b>{uncertainty.plausible_range_kg_ha[0]} – {uncertainty.plausible_range_kg_ha[1]} kg/ha</b>
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
