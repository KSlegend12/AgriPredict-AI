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
          <PolarGrid stroke="rgba(255, 255, 255, 0.1)" />
          <PolarAngleAxis dataKey="factor" tick={{ fill: '#94a3b8', fontSize: 11, fontWeight: 600 }} />
          <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
          <Radar 
            name="Suitability Factor Score" 
            dataKey="score" 
            stroke="#10b981" 
            fill="#10b981" 
            fillOpacity={0.4} 
            strokeWidth={2}
          />
          <Tooltip 
            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
            formatter={(value) => [`${value}% Match`, 'Factor Match']}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
