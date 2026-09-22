import React from 'react';
import { Trophy, CheckCircle, TrendingUp, Info, Sparkles, ChevronRight } from 'lucide-react';
import SuitabilityScore from './SuitabilityScore';

export default function CropCard({ recommendation, isTopMatch }) {
  const { rank, crop, icon, suitability_percentage, predicted_yield_ha, yield_range, confidence_score, why_recommendation, factor_scores } = recommendation;

  const medalEmojis = ['🥇', '🥈', '🥉'];
  const rankMedal = medalEmojis[rank - 1] || '🌱';

  const cropTheme = {
    Tomato: { border: 'border-rose-500/40', badge: 'bg-rose-500/10 text-rose-400 border-rose-500/30', bar: 'bg-rose-500' },
    Onion: { border: 'border-amber-500/40', badge: 'bg-amber-500/10 text-amber-400 border-amber-500/30', bar: 'bg-amber-500' },
    Sugarcane: { border: 'border-emerald-500/40', badge: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30', bar: 'bg-emerald-500' }
  };

  const theme = cropTheme[crop] || cropTheme.Tomato;

  return (
    <div className={`relative rounded-3xl p-6 transition-all duration-300 glass-panel hover:border-emerald-500/60 hover:shadow-xl ${
      isTopMatch ? 'border-2 border-emerald-500 ring-4 ring-emerald-500/10 glow-emerald' : theme.border
    }`}>
      
      {/* Top Match Banner */}
      {isTopMatch && (
        <div className="absolute -top-3.5 left-6 bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 text-[11px] font-black px-4 py-1 rounded-full shadow-lg flex items-center gap-1.5 uppercase tracking-wider">
          <Trophy className="w-3.5 h-3.5 text-amber-950" />
          <span>⭐ TOP RECOMMENDED MATCH</span>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between mb-6 pt-1">
        <div className="flex items-center gap-3">
          <div className="text-4xl p-3 bg-slate-900/80 border border-slate-800 rounded-2xl shadow-inner animate-float">
            {icon}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xl font-bold">{rankMedal}</span>
              <h3 className="text-2xl font-black text-white tracking-tight">{crop}</h3>
            </div>
            <span className={`inline-block text-[10px] font-bold px-2.5 py-0.5 rounded-full border mt-1 ${theme.badge}`}>
              Rank #{rank} Candidate
            </span>
          </div>
        </div>

        {/* Circular Gauge */}
        <SuitabilityScore score={suitability_percentage} rank={rank} />
      </div>

      {/* Predicted Yield Highlight */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 mb-5 flex items-center justify-between">
        <div>
          <span className="text-[11px] font-semibold text-slate-400 block">Predicted Future Yield</span>
          <div className="flex items-baseline gap-1 mt-0.5">
            <span className="text-2xl font-black text-emerald-400">{predicted_yield_ha}</span>
            <span className="text-xs font-bold text-slate-400">tonnes / ha</span>
          </div>
        </div>
        <div className="text-right">
          <span className="text-[10px] font-semibold text-slate-400 block">Expected Range</span>
          <span className="text-xs font-bold text-amber-300 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
            {yield_range}
          </span>
        </div>
      </div>

      {/* Why this recommendation? (Explainable AI) */}
      <div className="mb-5 bg-emerald-950/40 border border-emerald-500/20 rounded-2xl p-4 text-xs space-y-1">
        <div className="flex items-center gap-1.5 font-bold text-emerald-400 mb-1">
          <Sparkles className="w-3.5 h-3.5 text-amber-400 shrink-0" />
          <span>Why this recommendation?</span>
        </div>
        <p className="text-slate-300 leading-relaxed font-medium">
          {why_recommendation}
        </p>
      </div>

      {/* Agronomic Factor Breakdown */}
      <div className="space-y-2.5 pt-3 border-t border-slate-800/80">
        <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Agronomic Factor Alignment</h4>
        
        {factor_scores && Object.entries(factor_scores).map(([factor, score]) => (
          <div key={factor} className="space-y-1">
            <div className="flex justify-between text-xs font-semibold text-slate-300">
              <span className="capitalize">{factor}</span>
              <span className="text-slate-200">{score}%</span>
            </div>
            <div className="w-full bg-slate-900 rounded-full h-1.5 border border-slate-800">
              <div 
                className={`h-1.5 rounded-full ${theme.bar} transition-all duration-700`} 
                style={{ width: `${score}%` }} 
              />
            </div>
          </div>
        ))}
      </div>

      {/* Confidence */}
      <div className="mt-5 flex items-center justify-between text-[11px] text-slate-400 pt-3 border-t border-slate-800/80 font-medium">
        <span>AI Model Confidence: <strong className="text-slate-200">{confidence_score}%</strong></span>
        <span className="text-emerald-400 font-bold flex items-center gap-1">
          <CheckCircle className="w-3.5 h-3.5" /> Validated
        </span>
      </div>

    </div>
  );
}
