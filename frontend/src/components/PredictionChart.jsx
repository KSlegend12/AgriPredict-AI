import React from 'react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

export default function PredictionChart({ trendData, cropName }) {
  if (!trendData || trendData.length === 0) return null;

  return (
    <div className="agri-card p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-extrabold text-[#183C2C] dark:text-white">Historical vs Predicted Yield Trend</h3>
          <p className="text-xs text-[#607568] dark:text-slate-400">Time-series progression for {cropName} (tonnes / hectare)</p>
        </div>
        <span className="text-xs font-bold px-3 py-1 bg-emerald-500/10 text-[#087A50] dark:text-emerald-400 border border-emerald-500/20 rounded-full">
          XGBoost Time-Series
        </span>
      </div>

      <div className="h-72 w-full pt-2">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={trendData} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
            <defs>
              <linearGradient id="yieldGlow" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid, #DCE8DF)" />
            <XAxis dataKey="year" tick={{ fontSize: 11, fill: 'var(--chart-axis, #607568)' }} />
            <YAxis tick={{ fontSize: 11, fill: 'var(--chart-axis, #607568)' }} domain={['auto', 'auto']} />
            <Tooltip
              contentStyle={{
                backgroundColor: 'var(--chart-tooltip-bg, #FFFFFF)',
                borderColor: 'var(--chart-tooltip-border, #DCE8DF)',
                borderRadius: '12px',
                color: 'var(--chart-tooltip-text, #183C2C)',
                fontSize: '12px',
                boxShadow: '0 4px 16px rgba(24, 60, 44, 0.08)'
              }}
              itemStyle={{ color: '#087A50' }}
              formatter={(val) => [`${val} tonnes/ha`, 'Yield']}
            />
            <Legend wrapperStyle={{ fontSize: '12px', color: 'var(--chart-axis, #607568)' }} />
            <Area
              type="monotone"
              dataKey="yield"
              name="Yield (tonnes/ha)"
              stroke="#087A50"
              strokeWidth={3}
              fillOpacity={1}
              fill="url(#yieldGlow)"
              activeDot={{ r: 8, fill: '#15966A', stroke: '#087A50', strokeWidth: 3 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
