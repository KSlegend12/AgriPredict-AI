import React, { useEffect, useMemo, useState } from 'react';

import {
  AlertTriangle,
  CloudRain,
  Droplets,
  Leaf,
  Loader2,
  MapPin,
  RefreshCw,
  ThermometerSun,
  TrendingUp,
} from 'lucide-react';

import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import {
  getCottonFutureForecast,
  getCotton2026ScenarioPrediction,
} from '../services/api';
import { SUPPORTED_VIDARBHA_DISTRICTS, sanitizeDistrict } from '../constants/districts';


const DISTRICTS = SUPPORTED_VIDARBHA_DISTRICTS;


const SCENARIOS = {
  normal: {
    label: 'Normal',
    description: 'Recent district weather climatology',
    icon: CloudRain,
  },

  dry: {
    label: 'Dry',
    description: 'Below-normal rainfall scenario',
    icon: ThermometerSun,
  },

  wet: {
    label: 'Wet',
    description: 'Above-normal rainfall scenario',
    icon: Droplets,
  },
};


const formatYield = (value) =>
  typeof value === 'number'
    ? `${value.toFixed(1)} kg/ha`
    : '—';


export default function FutureCottonForecastPage({
  selectedDistrict,
  setSelectedDistrict,
}) {

  // =========================================================
  // STATES
  // =========================================================

  const [district, setDistrict] = useState(sanitizeDistrict(selectedDistrict));

  const [scenario, setScenario] = useState('normal');

  // Existing 2027–2031 forecast
  const [data, setData] = useState(null);

  // Experimental 2026 scenario prediction
  const [experimental2026, setExperimental2026] =
    useState(null);

  const [loading, setLoading] = useState(true);

  const [loading2026, setLoading2026] =
    useState(true);

  const [error, setError] = useState('');

  const [error2026, setError2026] =
    useState('');


  // =========================================================
  // SYNC DISTRICT
  // =========================================================

  useEffect(() => {

    if (DISTRICTS.includes(selectedDistrict)) {
      setDistrict(selectedDistrict);
    }

  }, [selectedDistrict]);


  // =========================================================
  // LOAD EXISTING 2027–2031 FORECAST
  // =========================================================

  const loadForecast = async (value = district) => {

    setLoading(true);
    setError('');

    try {

      const result =
        await getCottonFutureForecast(value);

      setData(result);

    } catch (err) {

      console.error(
        'Future forecast error:',
        err
      );

      setError(
        err?.response?.data?.detail ||
        'Future forecast could not be loaded. Make sure the FastAPI backend is running.'
      );

      setData(null);

    } finally {

      setLoading(false);

    }
  };


  // =========================================================
  // LOAD EXPERIMENTAL 2026 PREDICTION
  // =========================================================

  const load2026Prediction = async (
    value = district
  ) => {

    setLoading2026(true);
    setError2026('');

    try {

      const result =
        await getCotton2026ScenarioPrediction(value);

      setExperimental2026(result);

    } catch (err) {

      console.error(
        '2026 scenario prediction error:',
        err
      );

      setError2026(
        err?.response?.data?.detail ||
        '2026 scenario prediction could not be loaded.'
      );

      setExperimental2026(null);

    } finally {

      setLoading2026(false);

    }
  };


  // =========================================================
  // LOAD WHEN DISTRICT CHANGES
  // =========================================================

  useEffect(() => {

    loadForecast(district);
    load2026Prediction(district);

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [district]);


  // =========================================================
  // DISTRICT CHANGE
  // =========================================================

  const handleDistrictChange = (event) => {

    const value = event.target.value;

    setDistrict(value);

    if (setSelectedDistrict) {
      setSelectedDistrict(value);
    }
  };


  // =========================================================
  // 2026 SCENARIO VALUES
  // =========================================================

  const scenario2026Rows =
    experimental2026?.scenarios || [];


  const prediction2026 = {

    dry:
      scenario2026Rows.find(
        (item) => item.scenario === 'dry'
      )?.predicted_yield_kg_ha,

    normal:
      scenario2026Rows.find(
        (item) => item.scenario === 'normal'
      )?.predicted_yield_kg_ha,

    wet:
      scenario2026Rows.find(
        (item) => item.scenario === 'wet'
      )?.predicted_yield_kg_ha,

  };


  // =========================================================
  // 2027–2031 DATA
  // =========================================================

  const scenarioRows =
    data?.scenarios?.[scenario] || [];


  // =========================================================
  // 2026 + 2027–2031 COMBINED CHART
  // =========================================================

  const chartData = useMemo(() => {

    const current2026 =
      prediction2026[scenario];


    const point2026 =
      typeof current2026 === 'number'
        ? [
            {
              year: '2026',
              yield: current2026,
              type: 'Experimental scenario prediction',
            },
          ]
        : [];


    const futureRows =
      scenarioRows.map((row) => ({
        year: String(row.year),
        yield: row.predicted_yield_kg_ha,
        type: 'Future forecast',
      }));


    return [
      ...point2026,
      ...futureRows,
    ];

  }, [
    scenario,
    experimental2026,
    data,
  ]);


  // =========================================================
  // SELECTED SCENARIO
  // =========================================================

  const selectedScenario =
    SCENARIOS[scenario];

  const ScenarioIcon =
    selectedScenario.icon;


  const latest =
    scenarioRows[scenarioRows.length - 1];


  const current2026 =
    prediction2026[scenario];


  // =========================================================
  // RENDER
  // =========================================================

  return (

    <div className="space-y-6">


      {/* =====================================================
          HEADER
      ===================================================== */}

      <section className="relative overflow-hidden rounded-2xl bg-slate-900 px-6 py-7 text-white shadow-sm sm:px-8 dark:border dark:border-slate-800">

        <div className="absolute -right-20 -top-24 h-64 w-64 rounded-full bg-emerald-500/10 blur-3xl" />

        <div className="relative">

          <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-xs font-semibold text-emerald-300">

            <TrendingUp className="h-3.5 w-3.5" />

            COTTON FUTURE FORECAST

          </div>


          <h1 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">

            Cotton Yield Forecast · 2026–2031

          </h1>


          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">

            2026 is shown as an experimental scenario-based
            prediction because the actual annual 2026 yield is
            not available yet. The future forecasting module
            covers 2027–2031.

          </p>

        </div>

      </section>


      {/* =====================================================
          CONTROLS
      ===================================================== */}

      <section className="grid gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-900 lg:grid-cols-[1fr_1fr_auto]">


        {/* DISTRICT */}

        <div>

          <label className="mb-2 block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">

            District

          </label>


          <div className="relative">

            <MapPin className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-emerald-600 dark:text-emerald-400" />


            <select
              value={district}
              onChange={handleDistrictChange}
              className="w-full appearance-none rounded-xl border border-slate-200 bg-slate-50 py-3 pl-10 pr-4 text-sm font-semibold text-slate-800 outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100 dark:focus:border-emerald-400 dark:focus:ring-emerald-900/40"
            >

              {DISTRICTS.map((item) => (

                <option
                  key={item}
                  value={item}
                >

                  {item}, Vidarbha

                </option>

              ))}

            </select>

          </div>

        </div>


        {/* SCENARIO */}

        <div>

          <label className="mb-2 block text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">

            Weather Scenario

          </label>


          <div className="grid grid-cols-3 gap-2">

            {Object.entries(SCENARIOS).map(
              ([key, item]) => {

                const Icon = item.icon;

                const active =
                  scenario === key;


                return (

                  <button
                    key={key}
                    type="button"
                    onClick={() =>
                      setScenario(key)
                    }
                    className={`flex items-center justify-center gap-2 rounded-xl border px-3 py-3 text-xs font-bold transition ${
                      active
                        ? 'border-emerald-500 bg-emerald-50 text-emerald-700 dark:border-emerald-400 dark:bg-emerald-950/50 dark:text-emerald-300'
                        : 'border-slate-200 bg-slate-50 text-slate-600 hover:border-slate-300 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:border-slate-600'
                    }`}
                  >

                    <Icon className="h-4 w-4" />

                    {item.label}

                  </button>

                );

              }
            )}

          </div>

        </div>


        {/* REFRESH */}

        <div className="flex items-end">

          <button
            type="button"
            onClick={() => {
              loadForecast();
              load2026Prediction();
            }}
            disabled={
              loading || loading2026
            }
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-slate-900 px-5 py-3 text-sm font-bold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60 dark:bg-emerald-600 dark:hover:bg-emerald-500 lg:w-auto"
          >

            {loading || loading2026 ? (

              <Loader2 className="h-4 w-4 animate-spin" />

            ) : (

              <RefreshCw className="h-4 w-4" />

            )}

            Refresh

          </button>

        </div>

      </section>


      {/* =====================================================
          2026 ERROR
      ===================================================== */}

      {error2026 && (

        <div className="flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800 dark:border-amber-800 dark:bg-amber-950/30 dark:text-amber-200">

          <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" />

          <div>

            <p className="font-bold">

              2026 scenario prediction unavailable

            </p>

            <p className="mt-1">

              {error2026}

            </p>

          </div>

        </div>

      )}


      {/* =====================================================
          2027–2031 ERROR
      ===================================================== */}

      {error && (

        <div className="flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800 dark:border-amber-800 dark:bg-amber-950/30 dark:text-amber-200">

          <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" />

          <div>

            <p className="font-bold">

              Future forecast unavailable

            </p>

            <p className="mt-1">

              {error}

            </p>

          </div>

        </div>

      )}


      {/* =====================================================
          LOADING
      ===================================================== */}

      {(loading || loading2026) &&
        (!data || !experimental2026) ? (

        <div className="flex min-h-72 items-center justify-center rounded-2xl border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-900">

          <div className="text-center">

            <Loader2 className="mx-auto h-8 w-8 animate-spin text-emerald-600 dark:text-emerald-400" />

            <p className="mt-3 text-sm font-semibold text-slate-600 dark:text-slate-300">

              Loading {district} forecast…

            </p>

          </div>

        </div>

      ) : data || experimental2026 ? (

        <>


          {/* =================================================
              SUMMARY CARDS
          ================================================= */}

          <section className="grid gap-4 sm:grid-cols-3">


            {/* 2026 */}

            <div className="rounded-2xl border border-amber-200 bg-white p-5 shadow-sm dark:border-amber-800 dark:bg-slate-900">

              <div className="flex items-center gap-3">

                <div className="rounded-xl bg-amber-50 p-2.5 text-amber-600 dark:bg-amber-950/40 dark:text-amber-400">

                  <Leaf className="h-5 w-5" />

                </div>


                <div>

                  <p className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">

                    2026 · Experimental

                  </p>


                  <p className="text-lg font-bold text-slate-900 dark:text-white">

                    {formatYield(current2026)}

                  </p>

                </div>

              </div>

            </div>


            {/* 2031 */}

            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-900">

              <div className="flex items-center gap-3">

                <div className="rounded-xl bg-sky-50 p-2.5 text-sky-600 dark:bg-sky-950/40 dark:text-sky-400">

                  <TrendingUp className="h-5 w-5" />

                </div>


                <div>

                  <p className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">

                    2031

                  </p>


                  <p className="text-lg font-bold text-slate-900 dark:text-white">

                    {formatYield(
                      latest?.predicted_yield_kg_ha
                    )}

                  </p>

                </div>

              </div>

            </div>


            {/* SCENARIO */}

            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-900">

              <div className="flex items-center gap-3">

                <div className="rounded-xl bg-emerald-50 p-2.5 text-emerald-600 dark:bg-emerald-950/40 dark:text-emerald-400">

                  <ScenarioIcon className="h-5 w-5" />

                </div>


                <div>

                  <p className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">

                    Scenario

                  </p>


                  <p className="text-lg font-bold text-slate-900 dark:text-white">

                    {selectedScenario.label}

                  </p>

                </div>

              </div>

            </div>

          </section>


          {/* =================================================
              MAIN 2026–2031 CHART
          ================================================= */}

          <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-900 sm:p-6">


            <div className="mb-5 flex flex-col justify-between gap-2 sm:flex-row sm:items-center">

              <div>

                <h2 className="text-lg font-bold text-slate-900 dark:text-white">

                  {district} · {selectedScenario.label} Weather Scenario

                </h2>


                <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">

                  2026 experimental scenario prediction + 2027–2031 future forecast

                </p>


                <p className="mt-2 text-xs leading-5 text-amber-700 dark:text-amber-300">

                  2026 is an experimental scenario-based prediction
                  because the actual annual 2026 yield is not available
                  yet. 2027–2031 values are future model forecasts.

                </p>

              </div>


              <span className="rounded-full bg-slate-100 px-3 py-1.5 text-xs font-semibold text-slate-600 dark:bg-slate-800 dark:text-slate-300">

                Forecast origin: 2024

              </span>

            </div>


            <div className="h-80 w-full">

              <ResponsiveContainer
                width="100%"
                height="100%"
              >

                <LineChart
                  data={chartData}
                  margin={{
                    top: 10,
                    right: 20,
                    left: 5,
                    bottom: 5,
                  }}
                >

                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="#64748b"
                    opacity={0.25}
                  />


                  <XAxis
                    dataKey="year"
                    tick={{
                      fill: '#94a3b8',
                      fontSize: 12,
                    }}
                  />


                  <YAxis
                    tickFormatter={(value) =>
                      `${value}`
                    }
                    width={55}
                    tick={{
                      fill: '#94a3b8',
                      fontSize: 12,
                    }}
                  />


                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'var(--forecast-tooltip-bg, #0f172a)',
                      border: '1px solid #475569',
                      borderRadius: '10px',
                      color: '#f8fafc',
                    }}
                    labelStyle={{
                      color: '#f8fafc',
                      fontWeight: 700,
                    }}
                    itemStyle={{
                      color: '#a7f3d0',
                    }}
                    formatter={(value, name, props) => {

                      const label =
                        props?.payload?.year === '2026'
                          ? '2026 Experimental Prediction'
                          : 'Predicted Yield';

                      return [
                        `${Number(value).toFixed(1)} kg/ha`,
                        label,
                      ];

                    }}
                  />


                  <Legend
                    wrapperStyle={{
                      color: '#94a3b8',
                      fontSize: '12px',
                    }}
                  />


                  <Line
                    type="monotone"
                    dataKey="yield"
                    name="Predicted yield"
                    stroke="#10b981"
                    strokeWidth={3}
                    dot={{
                      r: 5,
                      fill: '#10b981',
                    }}
                    activeDot={{
                      r: 7,
                      fill: '#34d399',
                    }}
                  />

                </LineChart>

              </ResponsiveContainer>

            </div>

          </section>


          {/* =================================================
              2026–2031 TABLE
          ================================================= */}

          <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-900">

            <div className="border-b border-slate-100 px-5 py-4 dark:border-slate-700">

              <h2 className="font-bold text-slate-900 dark:text-white">

                2026–2031 Forecast Table

              </h2>


              <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">

                2026 is an experimental scenario-based prediction;
                2027–2031 use the existing future forecasting module.

              </p>

            </div>


            <div className="overflow-x-auto">

              <table className="w-full min-w-[760px] text-left text-sm">

                <thead className="bg-slate-50 text-xs uppercase tracking-wider text-slate-500 dark:bg-slate-800 dark:text-slate-400">

                  <tr>

                    <th className="px-5 py-3 font-bold">
                      Year
                    </th>

                    <th className="px-5 py-3 font-bold">
                      Predicted Yield
                    </th>

                    <th className="px-5 py-3 font-bold">
                      Prediction Type
                    </th>

                    <th className="px-5 py-3 font-bold">
                      Horizon
                    </th>

                    <th className="px-5 py-3 font-bold">
                      Model
                    </th>

                  </tr>

                </thead>


                <tbody>


                  {/* 2026 */}

                  {typeof current2026 === 'number' && (

                    <tr className="border-t border-amber-100 bg-amber-50/40 dark:border-amber-900 dark:bg-amber-950/20">

                      <td className="px-5 py-4 font-bold text-slate-900 dark:text-white">

                        2026

                      </td>


                      <td className="px-5 py-4 font-semibold text-amber-700 dark:text-amber-300">

                        {formatYield(current2026)}

                      </td>


                      <td className="px-5 py-4">

                        <span className="rounded-full bg-amber-100 px-2.5 py-1 text-xs font-bold text-amber-700 dark:bg-amber-950/60 dark:text-amber-300">

                          Scenario-based experimental

                        </span>

                      </td>


                      <td className="px-5 py-4 text-slate-600 dark:text-slate-300">

                        Current year

                      </td>


                      <td className="px-5 py-4 text-slate-600 dark:text-slate-300">

                        GradientBoosting

                      </td>

                    </tr>

                  )}


                  {/* 2027–2031 */}

                  {scenarioRows.map((row) => (

                    <tr
                      key={row.year}
                      className="border-t border-slate-100 dark:border-slate-700"
                    >

                      <td className="px-5 py-4 font-bold text-slate-900 dark:text-white">

                        {row.year}

                      </td>


                      <td className="px-5 py-4 font-semibold text-emerald-700 dark:text-emerald-400">

                        {formatYield(
                          row.predicted_yield_kg_ha
                        )}

                      </td>


                      <td className="px-5 py-4">

                        <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-600 dark:bg-slate-800 dark:text-slate-300">

                          Future forecast

                        </span>

                      </td>


                      <td className="px-5 py-4 text-slate-600 dark:text-slate-300">

                        {row.horizon_years}-year

                      </td>


                      <td className="px-5 py-4 text-slate-600 dark:text-slate-300">

                        {row.model}

                      </td>

                    </tr>

                  ))}

                </tbody>

              </table>

            </div>

          </section>


          {/* =================================================
              2026 EXPLANATION
          ================================================= */}

          <section className="rounded-2xl border border-amber-200 bg-amber-50 p-5 dark:border-amber-800 dark:bg-amber-950/30">

            <div className="flex items-start gap-3">

              <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-amber-600 dark:text-amber-400" />


              <div>

                <h3 className="font-bold text-amber-900 dark:text-amber-200">

                  2026 prediction status

                </h3>


                <p className="mt-1 text-sm leading-6 text-amber-800 dark:text-amber-200">

                  The actual annual 2026 cotton yield is not
                  available yet because the year is still incomplete.
                  Therefore, the 2026 value shown here is a
                  scenario-based experimental prediction using the
                  selected weather scenario.

                </p>


                <p className="mt-2 text-sm leading-6 text-amber-800 dark:text-amber-200">

                  Since the actual 2026 target is unavailable,
                  MAE, RMSE, R² and MAPE are not reported for 2026.

                </p>

              </div>

            </div>

          </section>


          {/* =================================================
              UNCERTAINTY
          ================================================= */}

          <section className="rounded-2xl border border-sky-200 bg-sky-50 p-5 dark:border-sky-800 dark:bg-sky-950/30">

            <div className="flex items-start gap-3">

              <TrendingUp className="mt-0.5 h-5 w-5 shrink-0 text-sky-600 dark:text-sky-400" />


              <div>

                <h3 className="font-bold text-sky-900 dark:text-sky-200">

                  About the uncertainty range

                </h3>


                <p className="mt-1 text-sm leading-6 text-sky-800 dark:text-sky-200">

                  The displayed uncertainty information for the
                  2027–2031 forecasts represents historical empirical
                  prediction error and is not a guaranteed future
                  confidence interval.

                </p>


                <p className="mt-2 text-sm leading-6 text-sky-800 dark:text-sky-200">

                  The 2026 experimental prediction does not have
                  an actual-year validation metric because the
                  2026 target is not available yet.

                </p>

              </div>

            </div>

          </section>


          {/* =================================================
              DATA PROVENANCE & OBSERVATION BOUNDARIES
          ================================================= */}

          <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">

            <div className="flex items-start gap-3">

              <Leaf className="mt-0.5 h-5 w-5 shrink-0 text-emerald-600 dark:text-emerald-400" />


              <div className="w-full space-y-2">

                <h3 className="font-bold text-slate-900 dark:text-slate-100">

                  Data Provenance & Observation Boundaries

                </h3>


                <p className="text-xs leading-5 text-slate-500 dark:text-slate-400">

                  AgriPredict-AI strictly distinguishes measured observations from scenario models. Forecast values are estimates, not guaranteed outcomes.

                </p>


                <div className="grid gap-3 pt-2 text-xs sm:grid-cols-2">

                  <div className="rounded-xl border border-slate-200 bg-slate-50 p-3.5 dark:border-slate-700 dark:bg-slate-800">

                    <span className="mb-1 block font-bold text-slate-800 dark:text-slate-200">

                      Historical Baseline (1997–2024)

                    </span>

                    <p className="text-slate-600 dark:text-slate-400 leading-relaxed">

                      Verified district cotton panels with authoritative IMD weather telemetry and historical agricultural yield statistics.

                    </p>

                  </div>


                  <div className="rounded-xl border border-slate-200 bg-slate-50 p-3.5 dark:border-slate-700 dark:bg-slate-800">

                    <span className="mb-1 block font-bold text-slate-800 dark:text-slate-200">

                      Satellite Soil Moisture (NASA SMAP)

                    </span>

                    <p className="text-slate-600 dark:text-slate-400 leading-relaxed">

                      Physical observations (SPL4SMGP.008) verified for 2017–2024 only. Unobserved for 2025–2031 future horizons.

                    </p>

                  </div>


                  <div className="rounded-xl border border-slate-200 bg-slate-50 p-3.5 dark:border-slate-700 dark:bg-slate-800">

                    <span className="mb-1 block font-bold text-slate-800 dark:text-slate-200">

                      Forecast Weather (2027–2031)

                    </span>

                    <p className="text-slate-600 dark:text-slate-400 leading-relaxed">

                      10-year rolling climatology with historical linear temperature trend and scenario multipliers (Normal 1.0x, Dry 0.8x, Wet 1.2x).

                    </p>

                  </div>


                  <div className="rounded-xl border border-slate-200 bg-slate-50 p-3.5 dark:border-slate-700 dark:bg-slate-800">

                    <span className="mb-1 block font-bold text-slate-800 dark:text-slate-200">

                      Forecast Origin Safety

                    </span>

                    <p className="text-slate-600 dark:text-slate-400 leading-relaxed">

                      Evaluated using expanding rolling-origin chronological protocol; zero future weather or target leakage into feature representations.

                    </p>

                  </div>

                </div>

              </div>

            </div>

          </section>


        </>

      ) : null}

    </div>
  );
}