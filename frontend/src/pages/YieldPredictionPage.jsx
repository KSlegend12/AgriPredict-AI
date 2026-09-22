import React, { useState, useEffect } from 'react';
import { TrendingUp, Calculator, Calendar, MapPin, Sparkles, CheckCircle2, Info } from 'lucide-react';
import PredictionChart from '../components/PredictionChart';
import { MAHARASHTRA_DISTRICTS, ALLOWED_CROPS, SEASONS } from '../data/maharashtraData';
import { predictYield } from '../services/api';

export default function YieldPredictionPage({ selectedDistrict, setSelectedDistrict }) {
  const [district, setDistrict] = useState(selectedDistrict || 'Pune');
  const [crop, setCrop] = useState('Tomato');
  const [targetYear, setTargetYear] = useState(2026);
  const [season, setSeason] = useState('Kharif');

  const [temperature, setTemperature] = useState(27.0);
  const [rainfall, setRainfall] = useState(650.0);
  const [humidity, setHumidity] = useState(70.0);
  const [soilPh, setSoilPh] = useState(6.5);
  const [nitrogen, setNitrogen] = useState(80.0);
  const [phosphorus, setPhosphorus] = useState(45.0);
  const [potassium, setPotassium] = useState(60.0);
  const [soilMoisture, setSoilMoisture] = useState(62.0);
  const [area, setArea] = useState(1.0);
  const [fertilizerUsage, setFertilizerUsage] = useState(150.0);
  const [irrigation, setIrrigation] = useState(true);

  const [prediction, setPrediction] = useState(null);
  const [isPredicting, setIsPredicting] = useState(false);

  useEffect(() => {
    setDistrict(selectedDistrict);
    const dObj = MAHARASHTRA_DISTRICTS.find(d => d.name === selectedDistrict);
    if (dObj) {
      setRainfall(dObj.avg_rainfall);
      setSoilPh(dObj.soil_ph);
      setTemperature(dObj.temp);
    }
  }, [selectedDistrict]);

  const handlePredict = async (e) => {
    e.preventDefault();
    setIsPredicting(true);

    try {
      const res = await predictYield({
        district: district,
        crop: crop,
        target_year: parseInt(targetYear),
        season: season,
        temperature: parseFloat(temperature),
        rainfall: parseFloat(rainfall),
        humidity: parseFloat(humidity),
        wind_speed: 12.0,
        soil_ph: parseFloat(soilPh),
        nitrogen: parseFloat(nitrogen),
        phosphorus: parseFloat(phosphorus),
        potassium: parseFloat(potassium),
        soil_moisture: parseFloat(soilMoisture),
        irrigation: irrigation,
        fertilizer_usage: parseFloat(fertilizerUsage),
        cultivated_area: parseFloat(area)
      });
      setPrediction(res);
    } catch (err) {
      console.error('Prediction failed:', err);
    } finally {
      setIsPredicting(false);
    }
  };

  return (
    <div className="space-y-10 py-6 max-w-6xl mx-auto">
      
      {/* Header */}
      <div className="text-center max-w-2xl mx-auto space-y-2">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/30 text-xs font-bold">
          <TrendingUp className="w-4 h-4 text-blue-400" />
          <span>XGBOOST REGRESSION ENSEMBLE (R² = 0.9931)</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-black text-white tracking-tight">
          📈 Future Yield Prediction
        </h1>
        <p className="text-slate-400 text-sm">
          Calculate expected crop yield (tonnes/ha) for <strong className="text-white">Tomato, Onion, or Sugarcane</strong>.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Form Panel */}
        <form onSubmit={handlePredict} className="lg:col-span-4 glass-panel p-6 sm:p-8 rounded-3xl border border-slate-800 shadow-xl space-y-6">
          <h3 className="text-sm font-black uppercase tracking-wider text-slate-300 border-b border-slate-800 pb-3 flex items-center gap-2">
            <Calculator className="w-4 h-4 text-emerald-400" />
            <span>Yield Parameters</span>
          </h3>

          {/* District Select */}
          <div>
            <label className="block text-xs font-bold text-slate-400 mb-1">District</label>
            <select
              value={district}
              onChange={(e) => {
                setDistrict(e.target.value);
                setSelectedDistrict(e.target.value);
              }}
              className="w-full bg-slate-900 border border-slate-800 text-white text-sm font-bold rounded-2xl px-3.5 py-2.5"
            >
              {MAHARASHTRA_DISTRICTS.map((d) => (
                <option key={d.name} value={d.name} className="bg-slate-900 text-white">{d.name}</option>
              ))}
            </select>
          </div>

          {/* Crop Select (ONLY 3 CROPS!) */}
          <div>
            <label className="block text-xs font-bold text-slate-400 mb-1">Crop (Strictly 3 Options)</label>
            <select
              value={crop}
              onChange={(e) => setCrop(e.target.value)}
              className="w-full bg-emerald-950/80 border border-emerald-500/50 text-emerald-300 text-sm font-extrabold rounded-2xl px-3.5 py-3 cursor-pointer"
            >
              {ALLOWED_CROPS.map((c) => (
                <option key={c.name} value={c.name} className="bg-slate-900 text-white">
                  {c.icon} {c.name}
                </option>
              ))}
            </select>
          </div>

          {/* Target Year & Season */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-bold text-slate-400 mb-1">Target Year</label>
              <select
                value={targetYear}
                onChange={(e) => setTargetYear(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 text-white text-sm font-bold rounded-2xl px-3 py-2.5"
              >
                <option value={2026} className="bg-slate-900">2026</option>
                <option value={2027} className="bg-slate-900">2027</option>
                <option value={2028} className="bg-slate-900">2028</option>
                <option value={2029} className="bg-slate-900">2029</option>
                <option value={2030} className="bg-slate-900">2030</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-400 mb-1">Season</label>
              <select
                value={season}
                onChange={(e) => setSeason(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 text-white text-sm font-bold rounded-2xl px-3 py-2.5"
              >
                {SEASONS.map(s => <option key={s} value={s} className="bg-slate-900">{s}</option>)}
              </select>
            </div>
          </div>

          {/* Cultivated Area */}
          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1">Cultivated Area (Hectares)</label>
            <input
              type="number" step="0.5" value={area} onChange={(e) => setArea(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 text-white text-sm rounded-2xl px-4 py-2.5 font-bold"
            />
          </div>

          {/* Sliders */}
          <div className="space-y-3 pt-2 border-t border-slate-800">
            <div className="flex justify-between text-xs font-semibold">
              <span className="text-slate-400">Rainfall</span>
              <span className="text-emerald-400 font-bold">{rainfall} mm</span>
            </div>
            <input 
              type="range" min="200" max="3000" step="25" value={rainfall} onChange={(e) => setRainfall(e.target.value)}
              className="w-full accent-emerald-500 cursor-pointer"
            />

            <div className="flex justify-between text-xs font-semibold">
              <span className="text-slate-400">Temperature</span>
              <span className="text-amber-400 font-bold">{temperature}°C</span>
            </div>
            <input 
              type="range" min="15" max="42" step="0.5" value={temperature} onChange={(e) => setTemperature(e.target.value)}
              className="w-full accent-amber-500 cursor-pointer"
            />

            <div className="flex justify-between text-xs font-semibold">
              <span className="text-slate-400">Soil pH</span>
              <span className="text-purple-400 font-bold">{soilPh}</span>
            </div>
            <input 
              type="range" min="5.0" max="8.5" step="0.1" value={soilPh} onChange={(e) => setSoilPh(e.target.value)}
              className="w-full accent-purple-500 cursor-pointer"
            />
          </div>

          <button
            type="submit"
            disabled={isPredicting}
            className="w-full py-4 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-black text-xs shadow-lg shadow-emerald-500/20 transition cursor-pointer flex items-center justify-center gap-2 uppercase tracking-wider glow-emerald"
          >
            <Sparkles className="w-4 h-4 text-amber-950" />
            <span>{isPredicting ? "Calculating..." : "PREDICT TARGET YIELD"}</span>
          </button>
        </form>

        {/* Results Panel */}
        <div className="lg:col-span-8 space-y-6">
          
          {prediction ? (
            <div className="space-y-6">
              
              {/* Main Predicted Yield Banner */}
              <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-emerald-500/30 shadow-2xl space-y-6 glow-emerald">
                
                <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                  <div className="flex items-center gap-3">
                    <span className="text-4xl">
                      {crop === 'Tomato' ? '🍅' : crop === 'Onion' ? '🧅' : '🎋'}
                    </span>
                    <div>
                      <h2 className="text-2xl font-black text-white">{crop} Yield Prediction</h2>
                      <span className="text-xs text-slate-400 font-medium">{district}, Maharashtra • {targetYear} ({season})</span>
                    </div>
                  </div>
                  <span className="text-xs bg-emerald-500/10 text-emerald-400 px-3 py-1 rounded-full font-bold border border-emerald-500/30">
                    Voting Regressor Ensemble
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  
                  <div className="bg-slate-900/80 p-5 rounded-2xl border border-slate-800">
                    <span className="text-[11px] text-slate-400 font-semibold block mb-1">PREDICTED TARGET YIELD</span>
                    <div className="text-4xl font-black text-emerald-400">
                      {prediction.predicted_yield_ha} <span className="text-sm font-semibold text-slate-300">tonnes/ha</span>
                    </div>
                    <div className="mt-2 text-xs text-slate-300 font-medium">
                      Total Production ({area} ha): <strong className="text-white">{prediction.total_production_tonnes} tonnes</strong>
                    </div>
                  </div>

                  <div className="bg-slate-900/80 p-5 rounded-2xl border border-slate-800 space-y-2">
                    <span className="text-[11px] text-slate-400 font-semibold block">EXPECTED CONFIDENCE RANGE</span>
                    <div className="text-2xl font-bold text-amber-300">
                      {prediction.yield_range}
                    </div>
                    <p className="text-[11px] text-slate-400 leading-normal">
                      Calculated using model root-mean-squared-error (RMSE ±1.68 t/ha).
                    </p>
                  </div>

                </div>

                {/* Historical Comparison */}
                <div className="grid grid-cols-3 gap-4 pt-4 border-t border-slate-800 text-center text-xs">
                  <div>
                    <span className="text-slate-400 block text-[11px]">Historical Average</span>
                    <span className="text-lg font-black text-white">{prediction.historical_avg_ha} t/ha</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[11px]">Predicted Future</span>
                    <span className="text-lg font-black text-emerald-400">{prediction.predicted_yield_ha} t/ha</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[11px]">Expected Change</span>
                    <span className={`text-lg font-black ${prediction.percentage_change >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {prediction.percentage_change >= 0 ? '+' : ''}{prediction.percentage_change}%
                    </span>
                  </div>
                </div>

              </div>

              {/* Time Series Chart */}
              <PredictionChart trendData={prediction.trend} cropName={crop} />

            </div>
          ) : (
            <div className="glass-panel p-12 rounded-3xl border border-slate-800 text-center space-y-4">
              <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center justify-center mx-auto text-3xl">
                📈
              </div>
              <h3 className="text-xl font-bold text-white">Ready to Predict Yield</h3>
              <p className="text-xs text-slate-400 max-w-sm mx-auto">
                Adjust farm parameters on the left and click <strong>"PREDICT TARGET YIELD"</strong> to run the trained Voting Regressor ensemble.
              </p>
            </div>
          )}

        </div>

      </div>

    </div>
  );
}
