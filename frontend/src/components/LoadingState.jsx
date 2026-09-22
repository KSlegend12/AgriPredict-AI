import React, { useState, useEffect } from 'react';
import { Sprout, CloudSun, Brain, LineChart, Loader2, Sparkles } from 'lucide-react';

export default function LoadingState({ onComplete }) {
  const [stage, setStage] = useState(0);

  const stages = [
    { icon: Sprout, text: "Analyzing your farm conditions...", emoji: "🌱" },
    { icon: CloudSun, text: "Processing weather data...", emoji: "🌦️" },
    { icon: Brain, text: "Running AI models...", emoji: "🧠" },
    { icon: LineChart, text: "Estimating crop yield...", emoji: "📈" }
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setStage((prev) => {
        if (prev < stages.length - 1) {
          return prev + 1;
        } else {
          clearInterval(timer);
          if (onComplete) setTimeout(onComplete, 450);
          return prev;
        }
      });
    }, 450);

    return () => clearInterval(timer);
  }, []);

  const progressPct = Math.min(100, Math.round(((stage + 1) / stages.length) * 100));

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-xl flex items-center justify-center p-4">
      <div className="glass-panel rounded-3xl p-8 max-w-md w-full border border-emerald-500/30 shadow-2xl text-center flex flex-col items-center glow-emerald">
        
        {/* Animated Icon Circle */}
        <div className="relative w-24 h-24 rounded-full bg-emerald-950/80 border-2 border-emerald-500/50 flex items-center justify-center mb-6 shadow-inner">
          <Loader2 className="w-24 h-24 text-emerald-400 animate-spin absolute inset-0 opacity-50" />
          <div className="text-4xl animate-bounce">
            {stages[stage].emoji}
          </div>
        </div>

        {/* Current Stage Title */}
        <div className="space-y-1 mb-6">
          <h3 className="text-xl font-black text-white tracking-tight">
            {stages[stage].text}
          </h3>
          <p className="text-xs text-slate-400 font-medium">
            Evaluating agronomic feature vectors for Maharashtra
          </p>
        </div>

        {/* Progress Bar */}
        <div className="w-full mb-6 space-y-1.5">
          <div className="flex justify-between text-xs font-bold text-slate-300">
            <span>AI Pipeline Progress</span>
            <span className="text-emerald-400">{progressPct}%</span>
          </div>
          <div className="w-full bg-slate-900 rounded-full h-2 border border-slate-800">
            <div 
              className="h-2 rounded-full bg-gradient-to-r from-emerald-500 to-teal-400 transition-all duration-500" 
              style={{ width: `${progressPct}%` }}
            />
          </div>
        </div>

        {/* Stage Step Indicators */}
        <div className="w-full space-y-2">
          {stages.map((s, idx) => (
            <div 
              key={idx}
              className={`flex items-center gap-3 p-3 rounded-2xl border text-xs font-bold transition-all duration-300 ${
                idx === stage 
                  ? 'bg-emerald-950/90 text-emerald-300 border-emerald-500/60 shadow-md scale-102' 
                  : idx < stage 
                  ? 'bg-slate-900/60 text-slate-400 border-slate-800/80 opacity-70' 
                  : 'bg-slate-900/20 text-slate-600 border-slate-900 opacity-40'
              }`}
            >
              <span className="text-base">{s.emoji}</span>
              <span className="flex-1 text-left">{s.text}</span>
              {idx < stage && <span className="text-emerald-400 font-black">✓</span>}
            </div>
          ))}
        </div>

      </div>
    </div>
  );
}
