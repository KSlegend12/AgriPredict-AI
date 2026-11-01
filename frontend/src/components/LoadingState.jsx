import React, { useState, useEffect } from 'react';
import { Sprout, CloudSun, Brain, LineChart, Loader2 } from 'lucide-react';

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
    <div className="fixed inset-0 z-50 bg-black/50 dark:bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4">
      <div className="rounded-3xl p-8 max-w-md w-full bg-white dark:bg-slate-900 border border-[#DCE8DF] dark:border-emerald-500/30 shadow-2xl text-center flex flex-col items-center">

        {/* Animated Icon Circle */}
        <div className="relative w-24 h-24 rounded-full bg-emerald-50 border-2 border-emerald-400 dark:bg-emerald-950/80 dark:border-emerald-500/50 flex items-center justify-center mb-6 shadow-inner">
          <Loader2 className="w-24 h-24 text-[#087A50] dark:text-emerald-400 animate-spin absolute inset-0 opacity-50" />
          <div className="text-4xl animate-bounce">
            {stages[stage].emoji}
          </div>
        </div>

        {/* Current Stage Title */}
        <div className="space-y-1 mb-6">
          <h3 className="text-xl font-black text-[#183C2C] dark:text-white tracking-tight">
            {stages[stage].text}
          </h3>
          <p className="text-xs text-[#607568] dark:text-slate-400 font-medium">
            Evaluating agronomic feature vectors for Maharashtra
          </p>
        </div>

        {/* Progress Bar */}
        <div className="w-full mb-6 space-y-1.5">
          <div className="flex justify-between text-xs font-bold text-[#183C2C] dark:text-slate-300">
            <span>AI Pipeline Progress</span>
            <span className="text-[#087A50] dark:text-emerald-400">{progressPct}%</span>
          </div>
          <div className="w-full bg-[#EAF2EC] dark:bg-slate-900 rounded-full h-2 border border-[#DCE8DF] dark:border-slate-800">
            <div
              className="h-2 rounded-full bg-gradient-to-r from-[#087A50] to-[#15966A] dark:from-emerald-500 dark:to-teal-400 transition-all duration-500"
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
                  ? 'bg-emerald-50 text-[#087A50] border-emerald-300 shadow-xs dark:bg-emerald-950/90 dark:text-emerald-300 dark:border-emerald-500/60'
                  : idx < stage
                  ? 'bg-[#F4F8F5] text-[#607568] border-[#DCE8DF] dark:bg-slate-900/60 dark:text-slate-400 dark:border-slate-800/80'
                  : 'bg-[#F4F8F5]/50 text-[#607568]/60 border-[#DCE8DF]/60 dark:bg-slate-900/20 dark:text-slate-600 dark:border-slate-900'
              }`}
            >
              <span className="text-base">{s.emoji}</span>
              <span className="flex-1 text-left">{s.text}</span>
              {idx < stage && <span className="text-[#087A50] dark:text-emerald-400 font-black">✓</span>}
            </div>
          ))}
        </div>

      </div>
    </div>
  );
}
