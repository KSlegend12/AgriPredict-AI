import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import {
  Activity,
  ArrowRight,
  BrainCircuit,
  CalendarDays,
  CheckCircle2,
  CloudRain,
  Database,
  Droplets,
  Gauge,
  Leaf,
  MapPin,
  Satellite,
  ShieldCheck,
  Sparkles,
  Thermometer,
  TrendingUp,
  FlaskConical,
  CloudSun,
  Sprout,
  History,
} from 'lucide-react';

import {
  getHealth,
  getCottonHistory,
  getCottonPredictionInput,
} from '../services/api';

import {
  LineChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  CartesianGrid,
} from 'recharts';


import { SUPPORTED_VIDARBHA_DISTRICTS, sanitizeDistrict } from '../constants/districts';

/* =========================================================
   CONSTANTS
========================================================= */

const DISTRICTS = SUPPORTED_VIDARBHA_DISTRICTS;

const FALLBACK = {
  validationMAE: 106.1784,
  validationRMSE: 126.6537,
  validationR2: -1.5769,
  validationMAPE: 38.1557,

  holdoutMAE: 230.7527,
  holdoutRMSE: 321.4472,
  holdoutR2: -0.636,
  holdoutMAPE: 41.6921,
};


/* =========================================================
   2025 EXPERIMENTAL RESULTS
   RandomForest
   Train: 1997-2024
   Test: 2025
========================================================= */

const EXPERIMENTAL_2025 = {
  model: 'RandomForest',
  trainingPeriod: '1997–2024',
  testYear: 2025,

  MAE: 38.8931,
  RMSE: 64.8643,
  R2: 0.0955,
  MAPE: 10.7697,

  districts: {
    Akola: {
      actual: 406.52,
      predicted: 414.67,
      pctError: 2.00,
    },
    Amravati: {
      actual: 508.56,
      predicted: 476.14,
      pctError: 6.37,
    },
    Buldhana: {
      actual: 420.00,
      predicted: 422.49,
      pctError: 0.59,
    },
    Nagpur: {
      actual: 495.46,
      predicted: 437.27,
      pctError: 11.74,
    },
    Wardha: {
      actual: 443.92,
      predicted: 453.01,
      pctError: 2.05,
    },
    Washim: {
      actual: 509.77,
      predicted: 505.47,
      pctError: 0.84,
    },
  },
};


/* =========================================================
   2026 EXPERIMENTAL SCENARIOS
========================================================= */

const EXPERIMENTAL_2026 = {
  Akola: {
    dry: 418.46,
    normal: 449.69,
    wet: 465.75,
  },

  Amravati: {
    dry: 406.65,
    normal: 426.76,
    wet: 443.82,
  },

  Buldhana: {
    dry: 439.79,
    normal: 478.66,
    wet: 485.41,
  },

  Nagpur: {
    dry: 465.10,
    normal: 510.10,
    wet: 507.29,
  },

  Wardha: {
    dry: 447.96,
    normal: 485.21,
    wet: 484.38,
  },

  Washim: {
    dry: 409.13,
    normal: 434.85,
    wet: 457.94,
  },
};


/* =========================================================
   COMPONENT
========================================================= */

export default function Dashboard({
  selectedDistrict = 'Akola',
  setSelectedDistrict,
}) {
  const navigate = useNavigate();

  const [district, setDistrict] = useState(
    sanitizeDistrict(selectedDistrict)
  );

  const [health, setHealth] = useState(null);
  const [history, setHistory] = useState(null);
  const [weather, setWeather] = useState(null);


  /* =======================================================
     SYNC DISTRICT
  ======================================================= */

  useEffect(() => {
    if (setSelectedDistrict) {
      setSelectedDistrict(district);
    }
  }, [district, setSelectedDistrict]);


  /* =======================================================
     LOAD HEALTH
  ======================================================= */

  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch(() => setHealth(null));
  }, []);


  /* =======================================================
     LOAD HISTORICAL DATA
  ======================================================= */

  useEffect(() => {
    Promise.allSettled([
      getCottonHistory(district),
      getCottonPredictionInput(district, 2024),
    ]).then(([h, w]) => {
      if (h.status === 'fulfilled') {
        setHistory(h.value);
      }

      if (w.status === 'fulfilled') {
        setWeather(w.value);
      }
    });
  }, [district]);


  /* =======================================================
     DERIVED DATA
  ======================================================= */

  const rows = useMemo(
    () => normalizeHistory(history),
    [history]
  );

  const latest = rows.at(-1);

  const metrics = extractMetrics(health);

  const experimental2025 =
    EXPERIMENTAL_2025.districts[district] ||
    null;

  const experimental2026 =
    EXPERIMENTAL_2026[district] ||
    null;


  /* =======================================================
     UI
  ======================================================= */

  return (
    <div className="space-y-6">


      {/* ===================================================
          HEADER
      =================================================== */}

      <section className="rounded-[28px] bg-white border border-slate-200 p-6 sm:p-8 shadow-sm">

        <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-6">

          <div>

            <div className="inline-flex items-center gap-2 rounded-full bg-emerald-50 px-3 py-1.5 text-[10px] font-extrabold uppercase tracking-[0.18em] text-emerald-700">

              <Activity className="h-3.5 w-3.5" />

              Live project dashboard

            </div>

            <h1 className="mt-4 text-3xl sm:text-4xl font-black tracking-tight">

              Agricultural intelligence at a glance.

            </h1>

            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500">

              Monitor the validated historical production model,
              experimental 2025 evaluation, 2026 scenario analysis
              and 2027–2031 future cotton forecasting.

            </p>

          </div>


          <div className="flex flex-wrap gap-3">

            <label className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">

              <span className="block text-[10px] font-extrabold uppercase tracking-widest text-slate-400">

                District

              </span>

              <select
                value={district}
                onChange={(e) => setDistrict(sanitizeDistrict(e.target.value))}
                className="mt-1 bg-transparent text-sm font-black outline-none"
              >

                {DISTRICTS.map((d) => (
                  <option key={d}>{d}</option>
                ))}

              </select>

            </label>


            <button
              onClick={() => navigate('/cotton')}
              className="self-stretch rounded-2xl bg-emerald-600 px-5 text-xs font-extrabold text-white hover:bg-emerald-700 transition inline-flex items-center gap-2"
            >

              Predict

              <ArrowRight className="h-4 w-4" />

            </button>

          </div>

        </div>

      </section>


      {/* ===================================================
          PROJECT OVERVIEW
      =================================================== */}

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

        <Kpi
          icon={MapPin}
          label="Study area"
          value="7 districts"
          note="Vidarbha"
        />

        <Kpi
          icon={Database}
          label="Historical data"
          value="1997–2024"
          note="194 observations"
        />

        <Kpi
          icon={BrainCircuit}
          label="Production model"
          value="Gradient Boosting"
          note="trained 1997–2023"
        />

        <Kpi
          icon={ShieldCheck}
          label="Final holdout"
          value="2024"
          note="untouched"
        />

      </section>


      {/* ===================================================
          VALIDATED PRODUCTION MODEL METRICS
      =================================================== */}

      <section>

        <div className="mb-3 flex items-center gap-2">

          <ShieldCheck className="h-4 w-4 text-emerald-600" />

          <h2 className="text-sm font-black">
            Production model validation
          </h2>

          <span className="text-[10px] text-slate-400">
            GradientBoosting
          </span>

        </div>


        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

          <Score
            label="Validation MAE"
            value={`${metrics.validationMAE.toFixed(2)} kg/ha`}
            sub="2011–2023 expanding window"
          />

          <Score
            label="Validation RMSE"
            value={`${metrics.validationRMSE.toFixed(2)} kg/ha`}
            sub="2011–2023 expanding window"
          />

          <Score
            label="2024 Holdout MAE"
            value={`${metrics.holdoutMAE.toFixed(2)} kg/ha`}
            sub="final untouched holdout"
          />

          <Score
            label="2024 Holdout MAPE"
            value={`${metrics.holdoutMAPE.toFixed(2)}%`}
            sub="final untouched holdout"
          />

        </div>

      </section>


      {/* ===================================================
          2025 EXPERIMENTAL EVALUATION
      =================================================== */}

      <section className="rounded-[24px] border border-blue-200 bg-blue-50 p-6">

        <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-5">

          <div>

            <div className="inline-flex items-center gap-2 rounded-full bg-white px-3 py-1.5 text-[10px] font-extrabold uppercase tracking-widest text-blue-700 border border-blue-100">

              <FlaskConical className="h-3.5 w-3.5" />

              Experimental evaluation

            </div>

            <h2 className="mt-3 text-xl font-black text-slate-900">

              2025 Out-of-Sample Hindcast

            </h2>

            <p className="mt-1 max-w-3xl text-xs leading-5 text-slate-600">

              RandomForest trained on 1997–2024 and evaluated on
              unseen 2025 targets. This uses observed 2025 weather,
              so it is an end-of-season hindcast, not a pre-season
              forecast.

            </p>

          </div>


          <div className="rounded-2xl bg-white border border-blue-100 px-4 py-3">

            <div className="text-[10px] font-extrabold uppercase tracking-widest text-slate-400">

              Model

            </div>

            <div className="mt-1 text-sm font-black text-slate-900">

              RandomForest

            </div>

            <div className="text-[10px] text-slate-500">

              Train 1997–2024 → Test 2025

            </div>

          </div>

        </div>


        <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">

          <ExperimentMetric
            label="2025 MAE"
            value={`${EXPERIMENTAL_2025.MAE.toFixed(2)} kg/ha`}
          />

          <ExperimentMetric
            label="2025 RMSE"
            value={`${EXPERIMENTAL_2025.RMSE.toFixed(2)} kg/ha`}
          />

          <ExperimentMetric
            label="2025 R²"
            value={EXPERIMENTAL_2025.R2.toFixed(4)}
          />

          <ExperimentMetric
            label="2025 MAPE"
            value={`${EXPERIMENTAL_2025.MAPE.toFixed(2)}%`}
          />

        </div>


        {experimental2025 && (
          <div className="mt-5 rounded-2xl bg-white border border-blue-100 p-4">

            <div className="flex items-center justify-between">

              <div>

                <p className="text-[10px] font-extrabold uppercase tracking-widest text-slate-400">

                  Selected district · 2025

                </p>

                <p className="mt-1 text-sm font-black text-slate-900">

                  {district}

                </p>

              </div>

              <span className="rounded-full bg-blue-50 px-3 py-1 text-[10px] font-extrabold text-blue-700">

                Experimental

              </span>

            </div>


            <div className="mt-4 grid grid-cols-3 gap-3">

              <MiniStat
                label="Actual"
                value={`${experimental2025.actual.toFixed(2)} kg/ha`}
              />

              <MiniStat
                label="Prediction"
                value={`${experimental2025.predicted.toFixed(2)} kg/ha`}
              />

              <MiniStat
                label="% Error"
                value={`${experimental2025.pctError.toFixed(2)}%`}
              />

            </div>

          </div>
        )}


        <p className="mt-4 text-[10px] leading-5 text-slate-500">

          Note: 2025 metrics are experimental and are not the
          production GradientBoosting model metrics.

        </p>

      </section>


      {/* ===================================================
          2026 SCENARIO PREDICTION
      =================================================== */}

      <section className="rounded-[24px] border border-amber-200 bg-amber-50 p-6">

        <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-5">

          <div>

            <div className="inline-flex items-center gap-2 rounded-full bg-white px-3 py-1.5 text-[10px] font-extrabold uppercase tracking-widest text-amber-700 border border-amber-100">

              <CloudSun className="h-3.5 w-3.5" />

              Experimental scenario

            </div>

            <h2 className="mt-3 text-xl font-black text-slate-900">

              2026 Scenario-Based Prediction

            </h2>

            <p className="mt-1 max-w-3xl text-xs leading-5 text-slate-600">

              2026 actual annual yield is not available.
              Therefore the system shows Dry, Normal and Wet
              weather scenarios instead of claiming a validated
              2026 prediction.

            </p>

          </div>


          <div className="rounded-2xl bg-white border border-amber-100 px-4 py-3">

            <div className="text-[10px] font-extrabold uppercase tracking-widest text-slate-400">

              Target year

            </div>

            <div className="mt-1 text-sm font-black text-slate-900">

              2026

            </div>

            <div className="text-[10px] text-slate-500">

              Actual target unavailable

            </div>

          </div>

        </div>


        {experimental2026 && (
          <div className="mt-5 grid gap-3 md:grid-cols-3">

            <ScenarioCard
              title="Dry"
              value={experimental2026.dry}
              description="Below-normal rainfall"
            />

            <ScenarioCard
              title="Normal"
              value={experimental2026.normal}
              description="Normal weather scenario"
              highlighted
            />

            <ScenarioCard
              title="Wet"
              value={experimental2026.wet}
              description="Above-normal rainfall"
            />

          </div>
        )}


        <div className="mt-4 flex flex-wrap gap-3">

          <button
            onClick={() => navigate('/future-forecast')}
            className="inline-flex items-center gap-2 rounded-xl bg-amber-600 px-4 py-2.5 text-xs font-extrabold text-white hover:bg-amber-700 transition"
          >

            Open Forecast

            <ArrowRight className="h-3.5 w-3.5" />

          </button>

        </div>

      </section>


      {/* ===================================================
          TEMPORAL PROJECT TIMELINE
      =================================================== */}

      <section className="agri-card p-6">

        <div className="flex items-start justify-between gap-4">

          <div>

            <p className="text-[10px] font-extrabold uppercase tracking-[0.18em] text-emerald-600">

              Model timeline

            </p>

            <h2 className="mt-1 text-lg font-black">

              From historical validation to future forecasting

            </h2>

            <p className="mt-1 text-xs text-slate-500">

              Each period has a different evidentiary status and
              should not be interpreted as the same type of prediction.

            </p>

          </div>

          <CalendarDays className="h-5 w-5 text-emerald-600" />

        </div>


        <div className="mt-6 grid gap-3 md:grid-cols-5">

          <TimelineCard
            year="1997–2023"
            title="Training"
            text="Production GradientBoosting training period."
            type="Production"
          />

          <TimelineCard
            year="2024"
            title="Final holdout"
            text="Untouched production-model evaluation year."
            type="Production"
            highlighted
          />

          <TimelineCard
            year="2025"
            title="Experimental hindcast"
            text="RandomForest trained through 2024 and tested on 2025."
            type="Experimental"
          />

          <TimelineCard
            year="2026"
            title="Scenario prediction"
            text="Dry / Normal / Wet experimental scenarios."
            type="Experimental"
          />

          <TimelineCard
            year="2027–2031"
            title="Future forecast"
            text="Existing future forecasting module."
            type="Forecast"
          />

        </div>

      </section>


      {/* ===================================================
          HISTORICAL SIGNAL
      =================================================== */}

      <section className="grid gap-6 lg:grid-cols-[1.25fr_.75fr]">

        <div className="agri-card p-6">

          <div className="flex items-start justify-between gap-4">

            <div>

              <p className="text-[10px] font-extrabold uppercase tracking-[0.18em] text-emerald-600">

                Historical signal

              </p>

              <h2 className="mt-1 text-lg font-black">

                {district} cotton yield

              </h2>

              <p className="mt-1 text-xs text-slate-500">

                Recorded annual yield · kg/ha · historical dataset through 2024

              </p>

            </div>

            <TrendingUp className="h-5 w-5 text-emerald-600" />

          </div>


          <div className="mt-5 h-72">

            {rows.length ? (

              <ResponsiveContainer width="100%" height="100%">

                <LineChart
                  data={rows}
                  margin={{
                    top: 10,
                    right: 10,
                    left: -20,
                    bottom: 0,
                  }}
                >

                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="#e2e8f0"
                  />

                  <XAxis
                    dataKey="year"
                    fontSize={11}
                    tickLine={false}
                  />

                  <YAxis
                    fontSize={11}
                    tickLine={false}
                  />

                  <Tooltip
                    formatter={(v) => [
                      `${Number(v).toFixed(1)} kg/ha`,
                      'Yield',
                    ]}
                  />

                  <Line
                    type="monotone"
                    dataKey="yield"
                    stroke="#059669"
                    strokeWidth={3}
                    dot={false}
                    activeDot={{ r: 5 }}
                  />

                </LineChart>

              </ResponsiveContainer>

            ) : (

              <EmptyChart />

            )}

          </div>

        </div>


        {/* =================================================
            LATEST PRODUCTION RECORD
        ================================================= */}

        <div className="agri-card p-6">

          <p className="text-[10px] font-extrabold uppercase tracking-[0.18em] text-emerald-600">

            Latest verified production record

          </p>

          <h2 className="mt-1 text-lg font-black">

            {district}

          </h2>

          <div className="mt-5 space-y-3">

            <InfoRow
              icon={Leaf}
              label="2024 Yield"
              value={
                latest
                  ? `${latest.yield.toFixed(1)} kg/ha`
                  : '—'
              }
            />

            <InfoRow
              icon={CloudRain}
              label="Rainfall"
              value={
                weather?.features?.rainfall_annual != null
                  ? `${Number(
                      weather.features.rainfall_annual
                    ).toFixed(0)} mm`
                  : 'Model input'
              }
            />

            <InfoRow
              icon={Thermometer}
              label="Temperature"
              value={
                weather?.features?.tmax_annual_mean_c != null
                  ? `${Number(
                      weather.features.tmax_annual_mean_c
                    ).toFixed(1)}°C`
                  : 'Model input'
              }
            />

            <InfoRow
              icon={Gauge}
              label="Production model"
              value="Ready"
              green
            />

          </div>


          <button
            onClick={() => navigate('/history')}
            className="mt-6 w-full rounded-xl border border-slate-200 py-3 text-xs font-extrabold text-slate-700 hover:bg-slate-50"
          >

            Explore full history

          </button>

        </div>

      </section>


      {/* ===================================================
          QUICK ACTIONS
      =================================================== */}

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">

        <Quick
          icon={Sparkles}
          title="Cotton Yield Prediction"
          text="Run Thermal Ridge candidate prediction with real-time SHAP feature explanations."
          action="Predict Cotton"
          onClick={() => navigate('/cotton')}
        />

        <Quick
          icon={Sprout}
          title="Cotton Soil & Agronomy"
          text="Inspect Vertisol soil benchmark profiles, pH, and macro-nutrient baselines for Vidarbha cotton."
          action="Cotton Advisory"
          onClick={() => navigate('/recommend')}
        />

        <Quick
          icon={CloudSun}
          title="Live Weather & Agromet"
          text="Inspect live agro-meteorological advisories, monsoon progress and rainfall."
          action="View Weather"
          onClick={() => navigate('/weather')}
        />

        <Quick
          icon={History}
          title="Audit Trail & History"
          text="Review historical yield series (1997–2024) and logged decision support audits."
          action="Audit History"
          onClick={() => navigate('/history')}
        />

        <Quick
          icon={TrendingUp}
          title="Future Forecast (2026–2031)"
          text="Explore multi-year climate projections and trend scenarios across Vidarbha."
          action="Explore Scenarios"
          onClick={() => navigate('/future-forecast')}
        />

      </section>


      {/* ===================================================
          MODEL EXPLANATION
      =================================================== */}

      <section className="grid gap-4 md:grid-cols-3">

        <InfoCard
          icon={ShieldCheck}
          title="Production truth"
          text="GradientBoosting remains the validated production model. The 2024 holdout remains untouched."
        />

        <InfoCard
          icon={FlaskConical}
          title="Experimental evidence"
          text="2025 RandomForest results are shown separately so experimental evaluation is not confused with production validation."
        />

        <InfoCard
          icon={CloudSun}
          title="Future assumptions"
          text="2026 uses Dry/Normal/Wet scenarios. 2027–2031 are future forecasts and do not have actual target validation yet."
        />

      </section>

    </div>
  );
}


/* =========================================================
   KPI
========================================================= */

function Kpi({
  icon: Icon,
  label,
  value,
  note,
}) {
  return (
    <div className="agri-card p-5">

      <div className="flex items-center justify-between">

        <div className="h-9 w-9 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center">

          <Icon className="h-4 w-4" />

        </div>

        <span className="text-[10px] font-bold text-slate-400">

          {note}

        </span>

      </div>


      <div className="mt-4 text-xl font-black">

        {value}

      </div>


      <div className="mt-1 text-xs font-semibold text-slate-500">

        {label}

      </div>

    </div>
  );
}


/* =========================================================
   SCORE
========================================================= */

function Score({
  label,
  value,
  sub,
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">

      <div className="text-[10px] font-extrabold uppercase tracking-widest text-slate-400">

        {label}

      </div>

      <div className="mt-2 text-xl font-black font-mono text-slate-900">

        {value}

      </div>

      <div className="mt-1 text-[10px] text-slate-500">

        {sub}

      </div>

    </div>
  );
}


/* =========================================================
   EXPERIMENT METRIC
========================================================= */

function ExperimentMetric({
  label,
  value,
}) {
  return (
    <div className="rounded-2xl border border-blue-100 bg-white p-4">

      <div className="text-[10px] font-extrabold uppercase tracking-widest text-slate-400">

        {label}

      </div>

      <div className="mt-2 text-lg font-black font-mono text-slate-900">

        {value}

      </div>

    </div>
  );
}


/* =========================================================
   MINI STAT
========================================================= */

function MiniStat({
  label,
  value,
}) {
  return (
    <div className="rounded-xl bg-slate-50 p-3">

      <div className="text-[9px] font-extrabold uppercase tracking-widest text-slate-400">

        {label}

      </div>

      <div className="mt-1 text-xs font-black text-slate-900">

        {value}

      </div>

    </div>
  );
}


/* =========================================================
   2026 SCENARIO CARD
========================================================= */

function ScenarioCard({
  title,
  value,
  description,
  highlighted = false,
}) {
  return (
    <div
      className={`rounded-2xl border p-5 ${
        highlighted
          ? 'border-amber-300 bg-white shadow-sm'
          : 'border-amber-100 bg-white'
      }`}
    >

      <div className="flex items-center justify-between">

        <div className="text-xs font-black text-slate-900">

          {title}

        </div>

        {highlighted && (
          <span className="rounded-full bg-amber-100 px-2 py-1 text-[9px] font-extrabold text-amber-700">

            Reference

          </span>
        )}

      </div>


      <div className="mt-3 text-2xl font-black text-slate-900">

        {Number(value).toFixed(2)}

        <span className="ml-1 text-xs font-bold text-slate-500">

          kg/ha

        </span>

      </div>


      <p className="mt-1 text-[10px] text-slate-500">

        {description}

      </p>

    </div>
  );
}


/* =========================================================
   TIMELINE CARD
========================================================= */

function TimelineCard({
  year,
  title,
  text,
  type,
  highlighted = false,
}) {
  const typeClass =
    type === 'Production'
      ? 'bg-emerald-50 text-emerald-700'
      : type === 'Experimental'
        ? 'bg-blue-50 text-blue-700'
        : 'bg-amber-50 text-amber-700';

  return (
    <div
      className={`rounded-2xl border p-4 ${
        highlighted
          ? 'border-emerald-300 bg-emerald-50/40'
          : 'border-slate-200 bg-white'
      }`}
    >

      <div className="flex items-center justify-between gap-2">

        <span className="text-sm font-black text-slate-900">

          {year}

        </span>

        <span
          className={`rounded-full px-2 py-1 text-[8px] font-extrabold uppercase tracking-wide ${typeClass}`}
        >

          {type}

        </span>

      </div>


      <div className="mt-3 text-xs font-black text-slate-900">

        {title}

      </div>


      <p className="mt-1 text-[10px] leading-4 text-slate-500">

        {text}

      </p>

    </div>
  );
}


/* =========================================================
   INFO ROW
========================================================= */

function InfoRow({
  icon: Icon,
  label,
  value,
  green,
}) {
  return (
    <div className="flex items-center justify-between rounded-xl bg-slate-50 px-3 py-3">

      <span className="inline-flex items-center gap-2 text-xs font-semibold text-slate-500">

        <Icon className="h-4 w-4 text-emerald-600" />

        {label}

      </span>


      <span
        className={`text-xs font-extrabold ${
          green
            ? 'text-emerald-700'
            : 'text-slate-800'
        }`}
      >

        {value}

      </span>

    </div>
  );
}


/* =========================================================
   QUICK CARD
========================================================= */

function Quick({
  icon: Icon,
  title,
  text,
  action,
  onClick,
}) {
  return (
    <div className="agri-card agri-card-hover p-5">

      <div className="h-10 w-10 rounded-xl bg-slate-950 text-white flex items-center justify-center">

        <Icon className="h-5 w-5" />

      </div>


      <h3 className="mt-4 text-sm font-extrabold">

        {title}

      </h3>


      <p className="mt-2 min-h-10 text-xs leading-5 text-slate-500">

        {text}

      </p>


      <button
        onClick={onClick}
        className="mt-4 inline-flex items-center gap-1 text-xs font-extrabold text-emerald-700"
      >

        {action}

        <ArrowRight className="h-3.5 w-3.5" />

      </button>

    </div>
  );
}


/* =========================================================
   INFO CARD
========================================================= */

function InfoCard({
  icon: Icon,
  title,
  text,
}) {
  return (
    <div className="agri-card p-5">

      <div className="h-9 w-9 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center">

        <Icon className="h-4 w-4" />

      </div>


      <h3 className="mt-4 text-sm font-black">

        {title}

      </h3>


      <p className="mt-2 text-xs leading-5 text-slate-500">

        {text}

      </p>

    </div>
  );
}


/* =========================================================
   EMPTY CHART
========================================================= */

function EmptyChart() {
  return (
    <div className="h-full flex items-center justify-center rounded-2xl bg-slate-50 text-xs font-semibold text-slate-400">

      History unavailable from backend

    </div>
  );
}


/* =========================================================
   HISTORY NORMALIZER
========================================================= */

function normalizeHistory(data) {
  const raw =
    data?.history ||
    data?.records ||
    data?.data ||
    [];

  return Array.isArray(raw)
    ? raw
        .map((x) => ({
          year: Number(
            x.year ??
            x.Year
          ),

          yield: Number(
            x.yield_kg_ha ??
            x.yield ??
            x.productivity_kg_ha ??
            x.value
          ),
        }))
        .filter(
          (x) =>
            Number.isFinite(x.year) &&
            Number.isFinite(x.yield)
        )
        .sort(
          (a, b) =>
            a.year - b.year
        )
    : [];
}


/* =========================================================
   METRICS
========================================================= */

function extractMetrics(data) {
  const c =
    data?.cotton ||
    data?.metrics ||
    {};

  return {
    validationMAE: Number(
      c?.validation_metrics?.mae ??
      c?.validation_mae ??
      FALLBACK.validationMAE
    ),

    validationRMSE: Number(
      c?.validation_metrics?.rmse ??
      c?.validation_rmse ??
      FALLBACK.validationRMSE
    ),

    validationR2: Number(
      c?.validation_metrics?.r2 ??
      FALLBACK.validationR2
    ),

    validationMAPE: Number(
      c?.validation_metrics?.mape ??
      FALLBACK.validationMAPE
    ),

    holdoutMAE: Number(
      c?.holdout_2024_metrics?.mae ??
      c?.holdout_mae ??
      FALLBACK.holdoutMAE
    ),

    holdoutRMSE: Number(
      c?.holdout_2024_metrics?.rmse ??
      c?.holdout_rmse ??
      FALLBACK.holdoutRMSE
    ),

    holdoutR2: Number(
      c?.holdout_2024_metrics?.r2 ??
      FALLBACK.holdoutR2
    ),

    holdoutMAPE: Number(
      c?.holdout_2024_metrics?.mape ??
      c?.holdout_mape ??
      FALLBACK.holdoutMAPE
    ),
  };
}