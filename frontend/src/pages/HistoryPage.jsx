import React, { useState, useEffect } from 'react';
import {
  History,
  MapPin,
  TrendingUp,
  Droplets,
  Thermometer,
  Sliders,
  Database,
  CheckCircle2,
  AlertTriangle,
  FlaskConical,
  ShieldAlert,
  Send,
  Sparkles,
  Layers,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import {
  getCottonHistory,
  getHistory,
  getFieldObservations,
  submitFieldObservation,
  getOutcomeValidationSummary
} from '../services/api';
import { SUPPORTED_VIDARBHA_DISTRICTS, sanitizeDistrict } from '../constants/districts';
import { DISTRICT_TALUKAS } from '../data/maharashtraData';

const VIDARBHA_DISTRICTS = SUPPORTED_VIDARBHA_DISTRICTS;

const HISTORICAL_SERIES = [
  { year: 1997, yield: 180, rainfall: 850, tmax: 33.1 },
  { year: 1999, yield: 210, rainfall: 790, tmax: 33.4 },
  { year: 2001, yield: 195, rainfall: 720, tmax: 34.0 },
  { year: 2003, yield: 235, rainfall: 910, tmax: 32.8 },
  { year: 2005, yield: 260, rainfall: 840, tmax: 33.5 },
  { year: 2007, yield: 310, rainfall: 980, tmax: 32.9 },
  { year: 2009, yield: 275, rainfall: 650, tmax: 34.5 },
  { year: 2011, yield: 340, rainfall: 1050, tmax: 32.2 },
  { year: 2013, yield: 385, rainfall: 1120, tmax: 31.9 },
  { year: 2015, yield: 250, rainfall: 680, tmax: 34.2 },
  { year: 2017, yield: 410, rainfall: 890, tmax: 33.0 },
  { year: 2019, yield: 370, rainfall: 940, tmax: 33.2 },
  { year: 2021, yield: 420, rainfall: 880, tmax: 33.4 },
  { year: 2023, yield: 444, rainfall: 820, tmax: 33.5 },
  { year: 2024, yield: 262, rainfall: 760, tmax: 33.8 },
];

export default function HistoryPage() {
  const [selectedDistrict, setSelectedDistrict] = useState(() => sanitizeDistrict(localStorage.getItem('agripredict-district')));
  const [startYear, setStartYear] = useState(1997);
  const [endYear, setEndYear] = useState(2024);
  const [dataSeries, setDataSeries] = useState(HISTORICAL_SERIES);
  const [predictionLogs, setPredictionLogs] = useState([]);
  const [dataSource, setDataSource] = useState('Default Series');

  // Phase 11: Real Field Observations & Outcome Validation State
  const [validationSummary, setValidationSummary] = useState(null);
  const [fieldObservations, setFieldObservations] = useState([]);
  const [showObsForm, setShowObsForm] = useState(false);
  const [obsSubmitting, setObsSubmitting] = useState(false);
  const [obsMessage, setObsMessage] = useState(null);
  const [obsError, setObsError] = useState(null);

  // Form state
  const availableTalukas = DISTRICT_TALUKAS[selectedDistrict] || ["Central"];
  const [obsForm, setObsForm] = useState({
    district: selectedDistrict,
    taluka: availableTalukas[0] || "Akola",
    crop: "Cotton",
    variety: "Bt-Cotton RCH-2",
    season: "Kharif",
    sowing_date: "2025-06-25",
    harvest_date: "2025-11-20",
    cultivated_area_ha: 1.5,
    actual_yield: 950.0,
    yield_unit: "kg_per_ha",
    irrigation_type: "rainfed",
    total_rainfall_mm: 780.0,
    data_source: "farmer_reported",
    consent_confirmed: true
  });

  useEffect(() => {
    let isMounted = true;
    async function loadData() {
      try {
        const res = await getCottonHistory(selectedDistrict);
        if (isMounted && res && res.records && res.records.length > 0) {
          const formatted = res.records.map((r) => ({
            year: r.year,
            yield: r.yield_kg_ha != null ? Math.round(r.yield_kg_ha) : null,
            rainfall: r.rainfall_annual_mm != null ? Math.round(r.rainfall_annual_mm) : 800,
            tmax: r.tmax_kharif_mean_c != null ? Number(r.tmax_kharif_mean_c.toFixed(1)) : 33.0,
          }));
          setDataSeries(formatted);
          setDataSource(res.source || 'Canonical Panel (1997-2024)');
        }
      } catch (err) {
        if (isMounted) setDataSource('Default Reference Series');
      }
    }

    async function loadLogs() {
      try {
        const hist = await getHistory(20);
        if (isMounted && hist && hist.history) {
          setPredictionLogs(hist.history);
        }
      } catch (err) {
        // Ignore log fetch error
      }
    }

    async function loadFieldValidation() {
      try {
        const summary = await getOutcomeValidationSummary();
        if (isMounted && summary) setValidationSummary(summary);

        const obs = await getFieldObservations(selectedDistrict, null, 20);
        if (isMounted && obs && obs.observations) setFieldObservations(obs.observations);
      } catch (err) {
        // Ignore field validation fetch error
      }
    }

    loadData();
    loadLogs();
    loadFieldValidation();

    return () => {
      isMounted = false;
    };
  }, [selectedDistrict]);

  // Update taluka when district changes
  const handleDistrictChange = (dist) => {
    const clean = sanitizeDistrict(dist);
    setSelectedDistrict(clean);
    const talukas = DISTRICT_TALUKAS[clean] || ["Central"];
    setObsForm(prev => ({ ...prev, district: clean, taluka: talukas[0] || "Central" }));
  };

  const handleObsFormSubmit = async (e) => {
    e.preventDefault();
    setObsSubmitting(true);
    setObsMessage(null);
    setObsError(null);
    try {
      const payload = {
        ...obsForm,
        cultivated_area_ha: parseFloat(obsForm.cultivated_area_ha) || 1.0,
        actual_yield: parseFloat(obsForm.actual_yield) || 0.0,
        total_rainfall_mm: parseFloat(obsForm.total_rainfall_mm) || null,
      };
      const res = await submitFieldObservation(payload);
      setObsMessage(`Observation successfully recorded! Assigned Anonymous ID: ${res.anonymous_farm_id}`);
      // Refresh observations and summary
      const updatedObs = await getFieldObservations(selectedDistrict, null, 20);
      if (updatedObs?.observations) setFieldObservations(updatedObs.observations);
      const updatedSummary = await getOutcomeValidationSummary();
      if (updatedSummary) setValidationSummary(updatedSummary);
    } catch (err) {
      setObsError(err?.response?.data?.detail || 'Failed to record field observation. Check input parameters.');
    } finally {
      setObsSubmitting(false);
    }
  };

  const filteredData = dataSeries.filter(
    (item) => item.year >= startYear && item.year <= endYear
  );

  return (
    <div className="space-y-8 py-4 max-w-7xl mx-auto">

      {/* Top Header */}
      <div className="border-b border-slate-200 pb-4">
        <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md bg-emerald-50 text-emerald-800 border border-emerald-200 text-xs font-semibold uppercase tracking-wider mb-1">
          <History className="w-3.5 h-3.5 text-emerald-600" />
          <span>Historical Analytics & Field Validation Infrastructure</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Historical Yield & Climate Trends (1997–2024)
        </h1>
        <p className="text-xs text-slate-500 font-normal">
          Rigorous agricultural benchmarking: Canonical panels (1997–2024) paired with authentic farmer harvest observations • Source: <span className="font-mono text-emerald-700">{dataSource}</span>
        </p>
      </div>

      {/* SCIENTIFIC PROVENANCE CLASSIFICATION BAR (WP9) */}
      <div className="agri-card p-4 border border-slate-200 bg-slate-50/70 rounded-xl space-y-2">
        <div className="flex items-center gap-2 text-xs font-bold text-slate-800">
          <Layers className="w-4 h-4 text-emerald-600" />
          <span>Authentic Scientific Data Provenance Taxonomy</span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2 pt-1 text-[11px]">
          <div className="bg-white p-2 rounded border border-slate-200 flex flex-col">
            <span className="font-bold text-slate-800">🤖 Model Predictions</span>
            <span className="text-slate-500 text-[10px]">Algorithmic ML inference</span>
          </div>
          <div className="bg-white p-2 rounded border border-slate-200 flex flex-col">
            <span className="font-bold text-emerald-800">🌾 Observed Outcomes</span>
            <span className="text-slate-500 text-[10px]">Real harvested field yields</span>
          </div>
          <div className="bg-white p-2 rounded border border-slate-200 flex flex-col">
            <span className="font-bold text-blue-800">📊 Historical Panels</span>
            <span className="text-slate-500 text-[10px]">1997–2024 DES/IMD records</span>
          </div>
          <div className="bg-white p-2 rounded border border-slate-200 flex flex-col">
            <span className="font-bold text-purple-800">🧪 Synthetic Scenarios</span>
            <span className="text-slate-500 text-[10px]">Simulation stress tests only</span>
          </div>
          <div className="bg-white p-2 rounded border border-slate-200 flex flex-col">
            <span className="font-bold text-amber-800">⏳ Unverified Records</span>
            <span className="text-slate-500 text-[10px]">Self-reported farmer logs</span>
          </div>
          <div className="bg-white p-2 rounded border border-slate-200 flex flex-col">
            <span className="font-bold text-teal-800">✅ Verified Trials</span>
            <span className="text-slate-500 text-[10px]">Extension / KVK verified</span>
          </div>
        </div>
      </div>

      {/* PHASE 11: FIELD VALIDATION SUMMARY & OUTCOME TRACKING (WP4, WP6, WP9) */}
      <div className="agri-card p-6 border border-emerald-200 bg-white rounded-xl shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-3">
          <div>
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <FlaskConical className="w-5 h-5 text-emerald-600" />
              <span>Real-World Field Validation & Empirical Error Tracker</span>
            </h3>
            <p className="text-xs text-slate-500">
              Comparing model predictions directly against documented agricultural harvest outcomes.
            </p>
          </div>
          <button
            onClick={() => setShowObsForm(!showObsForm)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-semibold rounded-lg shadow-xs transition"
          >
            <span>{showObsForm ? 'Close Observation Form' : 'Log Field Harvest Outcome'}</span>
            {showObsForm ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>

        {/* Validation Metrics Grid per Crop */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {["Cotton"].map((cropName) => {
            const cropStat = validationSummary?.crops?.[cropName];
            const n = cropStat?.sample_size_n ?? 0;
            const isRobust = n >= 30;
            const isPreliminary = n >= 10 && n < 30;

            return (
              <div key={cropName} className="p-3.5 rounded-lg border border-slate-200 bg-slate-50/60 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-900 text-xs">{cropName} Validation</span>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold ${
                    isRobust ? 'bg-emerald-100 text-emerald-800' :
                    isPreliminary ? 'bg-amber-100 text-amber-800' :
                    'bg-slate-200 text-slate-600'
                  }`}>
                    {isRobust ? 'CERTIFIED' : isPreliminary ? 'PRELIMINARY' : 'INSUFFICIENT'}
                  </span>
                </div>
                <div className="text-xs text-slate-600 space-y-1 font-mono">
                  <div>Sample Size: <strong className="text-slate-900">{n}</strong> observations</div>
                  {n >= 10 ? (
                    <>
                      <div>Mean Abs Error: <strong className="text-slate-900">{cropStat.mean_absolute_error}</strong></div>
                      <div>Coverage: <strong className="text-emerald-700">{cropStat.within_bounds_coverage_pct}%</strong></div>
                    </>
                  ) : (
                    <div className="text-[11px] text-amber-700 font-sans italic pt-1">
                      ⚠️ Aggregate accuracy withheld: Minimum threshold (N ≥ 10) not yet reached.
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* INTERACTIVE LOG FIELD OBSERVATION FORM */}
        {showObsForm && (
          <form onSubmit={handleObsFormSubmit} className="mt-4 p-4 border border-emerald-300 bg-emerald-50/40 rounded-xl space-y-4">
            <div className="border-b border-emerald-200 pb-2 flex items-center justify-between">
              <span className="text-xs font-bold text-emerald-950 uppercase tracking-wide">
                Submit Anonymized Field Harvest Observation
              </span>
              <span className="text-[11px] text-emerald-800">
                🔒 Privacy Assured: Farmer PII is anonymized with cryptographic hashing
              </span>
            </div>

            {obsMessage && (
              <div className="p-2.5 rounded-lg bg-emerald-100 border border-emerald-300 text-emerald-900 text-xs font-medium">
                {obsMessage}
              </div>
            )}
            {obsError && (
              <div className="p-2.5 rounded-lg bg-rose-100 border border-rose-300 text-rose-900 text-xs font-medium">
                {obsError}
              </div>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">District</label>
                <select
                  value={obsForm.district}
                  onChange={(e) => handleDistrictChange(e.target.value)}
                  className="w-full bg-white border border-slate-300 rounded-lg p-2 font-medium"
                >
                  {VIDARBHA_DISTRICTS.map((d) => (
                    <option key={d} value={d}>{d}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Taluka</label>
                <select
                  value={obsForm.taluka}
                  onChange={(e) => setObsForm({ ...obsForm, taluka: e.target.value })}
                  className="w-full bg-white border border-slate-300 rounded-lg p-2 font-medium"
                >
                  {(DISTRICT_TALUKAS[obsForm.district] || ["Central"]).map((t) => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Crop</label>
                <select
                  value={obsForm.crop}
                  onChange={(e) => setObsForm({ ...obsForm, crop: e.target.value })}
                  className="w-full bg-white border border-slate-300 rounded-lg p-2 font-medium"
                >
                  <option value="Cotton">Cotton (Gossypium hirsutum - Kharif)</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Season</label>
                <select
                  value={obsForm.season}
                  onChange={(e) => setObsForm({ ...obsForm, season: e.target.value })}
                  className="w-full bg-white border border-slate-300 rounded-lg p-2 font-medium"
                >
                  <option value="Kharif">Kharif</option>
                  <option value="Rabi">Rabi</option>
                  <option value="Summer">Summer</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Sowing Date</label>
                <input
                  type="date"
                  value={obsForm.sowing_date}
                  onChange={(e) => setObsForm({ ...obsForm, sowing_date: e.target.value })}
                  className="w-full bg-white border border-slate-300 rounded-lg p-2 font-medium"
                  required
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Harvest Date</label>
                <input
                  type="date"
                  value={obsForm.harvest_date}
                  onChange={(e) => setObsForm({ ...obsForm, harvest_date: e.target.value })}
                  className="w-full bg-white border border-slate-300 rounded-lg p-2 font-medium"
                  required
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Actual Yield</label>
                <input
                  type="number"
                  step="0.1"
                  min="0.1"
                  value={obsForm.actual_yield}
                  onChange={(e) => setObsForm({ ...obsForm, actual_yield: e.target.value })}
                  className="w-full bg-white border border-slate-300 rounded-lg p-2 font-mono font-bold"
                  required
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Yield Unit</label>
                <select
                  value={obsForm.yield_unit}
                  onChange={(e) => setObsForm({ ...obsForm, yield_unit: e.target.value })}
                  className="w-full bg-white border border-slate-300 rounded-lg p-2 font-medium"
                >
                  <option value="kg_per_ha">kg / hectare (kg/ha)</option>
                  <option value="quintal_per_acre">quintal / acre (q/acre)</option>
                </select>
              </div>
            </div>

            <div className="flex items-center justify-between pt-2">
              <label className="flex items-center gap-2 text-xs text-slate-600 cursor-pointer">
                <input
                  type="checkbox"
                  checked={obsForm.consent_confirmed}
                  onChange={(e) => setObsForm({ ...obsForm, consent_confirmed: e.target.checked })}
                  className="rounded text-emerald-600 focus:ring-emerald-500"
                />
                <span>Farmer consent confirmed: Data will be used strictly for research evaluation with anonymized IDs.</span>
              </label>

              <button
                type="submit"
                disabled={obsSubmitting}
                className="px-4 py-2 bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-bold rounded-lg shadow-xs transition disabled:opacity-50 flex items-center gap-1.5"
              >
                <Send className="w-3.5 h-3.5" />
                <span>{obsSubmitting ? 'Recording...' : 'Submit Field Observation'}</span>
              </button>
            </div>
          </form>
        )}
      </div>

      {/* FILTERS BAR (Requirement #23) */}
      <div className="agri-card p-4 border border-slate-200 shadow-xs flex flex-wrap items-center justify-between gap-4">

        {/* District Filter */}
        <div className="flex items-center gap-2">
          <MapPin className="w-4 h-4 text-emerald-600" />
          <span className="text-xs font-semibold text-slate-700">District:</span>
          <select
            value={selectedDistrict}
            onChange={(e) => handleDistrictChange(e.target.value)}
            className="bg-slate-50 border border-slate-300 text-slate-900 text-xs rounded-md px-3 py-1.5 font-bold cursor-pointer focus:outline-none"
          >
            {VIDARBHA_DISTRICTS.map((d) => (
              <option key={d} value={d} className="bg-white text-slate-900 font-medium">
                {d}, Vidarbha
              </option>
            ))}
          </select>
        </div>

        {/* Year Range Filter */}
        <div className="flex items-center gap-3 text-xs font-mono">
          <Sliders className="w-4 h-4 text-emerald-600" />
          <span className="font-sans font-semibold text-slate-700">Year Range:</span>

          <select
            value={startYear}
            onChange={(e) => setStartYear(Number(e.target.value))}
            className="bg-slate-50 border border-slate-300 text-slate-900 text-xs rounded-md px-2.5 py-1 font-bold cursor-pointer"
          >
            {[1997, 2000, 2005, 2010, 2015, 2020].map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>

          <span className="text-slate-400">to</span>

          <select
            value={endYear}
            onChange={(e) => setEndYear(Number(e.target.value))}
            className="bg-slate-50 border border-slate-300 text-slate-900 text-xs rounded-md px-2.5 py-1 font-bold cursor-pointer"
          >
            {[2010, 2015, 2020, 2023, 2024].map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
        </div>

      </div>

      {/* CHART 1: YIELD TREND */}
      <div className="agri-card p-6 border border-slate-200 space-y-4">
        <div className="border-b border-slate-100 pb-3">
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-emerald-600" />
            <span>Yield Trend ({selectedDistrict})</span>
          </h3>
          <p className="text-xs text-slate-500">Recorded annual cotton yield (kg/ha)</p>
        </div>

        <div className="h-60 w-full pt-1">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={filteredData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid, #DCE8DF)" />
              <XAxis dataKey="year" stroke="var(--chart-axis, #607568)" fontSize={11} tickLine={false} />
              <YAxis stroke="var(--chart-axis, #607568)" fontSize={11} tickLine={false} domain={['dataMin - 50', 'dataMax + 50']} unit=" kg" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--chart-tooltip-bg, #FFFFFF)',
                  borderColor: 'var(--chart-tooltip-border, #DCE8DF)',
                  borderRadius: '10px',
                  color: 'var(--chart-tooltip-text, #183C2C)',
                  fontSize: '12px',
                  boxShadow: '0 4px 16px rgba(24, 60, 44, 0.08)'
                }}
                formatter={(val) => [`${val} kg/ha`, 'Yield']}
              />
              <Line type="monotone" dataKey="yield" stroke="#087A50" strokeWidth={2.5} dot={{ fill: '#087A50', r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* CHART 2: RAINFALL TREND */}
      <div className="agri-card p-6 border border-slate-200 space-y-4">
        <div className="border-b border-slate-100 pb-3">
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Droplets className="w-4 h-4 text-emerald-600" />
            <span>Annual Rainfall Trend ({selectedDistrict})</span>
          </h3>
          <p className="text-xs text-slate-500">Total recorded annual precipitation (mm)</p>
        </div>

        <div className="h-60 w-full pt-1">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={filteredData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid, #DCE8DF)" />
              <XAxis dataKey="year" stroke="var(--chart-axis, #607568)" fontSize={11} tickLine={false} />
              <YAxis stroke="var(--chart-axis, #607568)" fontSize={11} tickLine={false} domain={['dataMin - 100', 'dataMax + 100']} unit=" mm" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--chart-tooltip-bg, #FFFFFF)',
                  borderColor: 'var(--chart-tooltip-border, #DCE8DF)',
                  borderRadius: '10px',
                  color: 'var(--chart-tooltip-text, #183C2C)',
                  fontSize: '12px',
                  boxShadow: '0 4px 16px rgba(24, 60, 44, 0.08)'
                }}
                formatter={(val) => [`${val} mm`, 'Rainfall']}
              />
              <Line type="monotone" dataKey="rainfall" stroke="#2563eb" strokeWidth={2.5} dot={{ fill: '#2563eb', r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* CHART 3: TEMPERATURE TREND */}
      <div className="agri-card p-6 border border-slate-200 space-y-4">
        <div className="border-b border-slate-100 pb-3">
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Thermometer className="w-4 h-4 text-emerald-600" />
            <span>Temperature Trend ({selectedDistrict})</span>
          </h3>
          <p className="text-xs text-slate-500">Kharif season mean maximum temperature (°C)</p>
        </div>

        <div className="h-60 w-full pt-1">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={filteredData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--chart-grid, #DCE8DF)" />
              <XAxis dataKey="year" stroke="var(--chart-axis, #607568)" fontSize={11} tickLine={false} />
              <YAxis stroke="var(--chart-axis, #607568)" fontSize={11} tickLine={false} domain={['dataMin - 1', 'dataMax + 1']} unit=" °C" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--chart-tooltip-bg, #FFFFFF)',
                  borderColor: 'var(--chart-tooltip-border, #DCE8DF)',
                  borderRadius: '10px',
                  color: 'var(--chart-tooltip-text, #183C2C)',
                  fontSize: '12px',
                  boxShadow: '0 4px 16px rgba(24, 60, 44, 0.08)'
                }}
                formatter={(val) => [`${val} °C`, 'Kharif Max Temp']}
              />
              <Line type="monotone" dataKey="tmax" stroke="#b45309" strokeWidth={2.5} dot={{ fill: '#b45309', r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* PREDICTION HISTORY AUDIT LOG TABLE */}
      <div className="agri-card p-6 border border-slate-200 space-y-4">
        <div className="border-b border-slate-100 pb-3 flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Database className="w-4 h-4 text-emerald-600" />
              <span>Prediction Audit Trail</span>
            </h3>
            <p className="text-xs text-slate-500">Live SQLite session logs for crop and yield queries</p>
          </div>
          <span className="text-xs font-medium px-2 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200">
            {predictionLogs.filter((log) => VIDARBHA_DISTRICTS.includes(log.district)).length} Records
          </span>
        </div>

        {predictionLogs.filter((log) => VIDARBHA_DISTRICTS.includes(sanitizeDistrict(log.district))).length === 0 ? (
          <div className="text-center py-8 text-slate-400 text-xs flex flex-col items-center justify-center gap-2">
            <Database className="w-8 h-8 text-slate-300" />
            <p>No predictions logged yet for Vidarbha districts.</p>
            <p className="text-[11px] text-slate-400">Run a prediction from the Cotton Yield or Crop Advisory modules to record audit entries here.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-200 text-slate-600 bg-slate-50/50">
                  <th className="py-2.5 px-3 font-semibold">Timestamp</th>
                  <th className="py-2.5 px-3 font-semibold">District</th>
                  <th className="py-2.5 px-3 font-semibold">Target / Crop</th>
                  <th className="py-2.5 px-3 font-semibold">Predicted Yield</th>
                  <th className="py-2.5 px-3 font-semibold">Model / Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {predictionLogs.filter((log) => VIDARBHA_DISTRICTS.includes(sanitizeDistrict(log.district))).map((log, idx) => {
                  const crop = (log.crop_type || log.recommended_crop || 'Cotton').toString();
                  const unit = 'kg/ha';

                  return (
                    <tr key={log.id || idx} className="hover:bg-slate-50/70 transition-colors">
                      <td className="py-2 px-3 font-mono text-slate-500">{log.timestamp || 'Just now'}</td>
                      <td className="py-2 px-3 font-medium text-slate-900">{log.district}</td>
                      <td className="py-2 px-3">
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-100 text-emerald-800">
                          <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                          {crop}
                        </span>
                      </td>
                      <td className="py-2 px-3 font-semibold text-slate-900">
                        {log.predicted_yield != null ? `${Number(log.predicted_yield).toFixed(1)} ${unit}` : 'N/A'}
                      </td>
                      <td className="py-2 px-3 text-slate-500 text-[11px] font-mono">
                        {log.model_version || (log.season ? `Season: ${log.season}` : 'Production')}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

    </div>
  );
}
