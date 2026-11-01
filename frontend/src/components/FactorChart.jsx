import React from 'react';
import { ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Tooltip } from 'recharts';

export default function FactorChart({ factorScores }) {
  if (!factorScores) return null;

  const data = [
    { factor: 'Temperature', score: factorScores.temperature || 85 },
    { factor: 'Rainfall', score: factorScores.rainfall || 80 },
    { factor: 'Soil pH', score: factorScores.soil || 90 },
    { factor: 'Humidity', score: factorScores.humidity || 75 },
    { factor: 'Season', score: factorScores.season || 92 }
  ];

  return (
    <div className="w-full h-56 relative">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="75%" data={data}>
          <PolarGrid stroke="var(--chart-grid, #DCE8DF)" />
          <PolarAngleAxis dataKey="factor" tick={{ fill: 'var(--chart-axis, #607568)', fontSize: 11, fontWeight: 600 }} />
          <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
          <Radar
            name="Suitability Factor Score"
            dataKey="score"
            stroke="#087A50"
            fill="#087A50"
            fillOpacity={0.35}
            strokeWidth={2}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'var(--chart-tooltip-bg, #FFFFFF)',
              borderColor: 'var(--chart-tooltip-border, #DCE8DF)',
              borderRadius: '8px',
              color: 'var(--chart-tooltip-text, #183C2C)',
              fontSize: '12px',
              boxShadow: '0 4px 16px rgba(24, 60, 44, 0.08)'
            }}
            formatter={(value) => [`${value}% Match`, 'Factor Match']}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
