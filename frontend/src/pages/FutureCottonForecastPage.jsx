
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
import { getCottonFutureForecast } from '../services/api';

const DISTRICTS = [
  'Akola',
  'Amravati',
  'Buldhana',
  'Nagpur',
  'Wardha',
  'Washim',
  'Yavatmal',
];

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
  typeof value === 'number' ? `${value.toFixed(1)} kg/ha` : '—';

const formatRange = (lower, upper) =>
  typeof lower === 'number' && typeof upper === 'number'
    ? `${lower.toFixed(1)} – ${upper.toFixed(1)} kg/ha`
    : '—';

export default function FutureCottonForecastPage({
  selectedDistrict,
  setSelectedDistrict,
}) {
  const [district, setDistrict] = useState(
    DISTRICTS.includes(selectedDistrict) ? selectedDistrict : 'Akola'
  );
  const [scenario, setScenario] = useState('normal');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (DISTRICTS.includes(selectedDistrict)) {
      setDistrict(selectedDistrict);
    }
  }, [selectedDistrict]);

  const loadForecast = async (value = district) => {
    setLoading(true);
    setError('');

    try {
      const result = await getCottonFutureForecast(value);
      setData(result);
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          'Future forecast could not be loaded. Make sure the FastAPI backend is running.'
      );
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadForecast(district);
    // Initial load + district changes only.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [district]);

  const handleDistrictChange = (event) => {
    const value = event.target.value;
    setDistrict(value);

    if (setSelectedDistrict) {
      setSelectedDistrict(value);
    }
  };

  const chartData = useMemo(() => {
    const rows = data?.scenarios?.[scenario] || [];

    return rows.map((row) => ({
      year: String(row.year),
      yield: row.predicted_yield_kg_ha,
    }));
  }, [data, scenario]);

  const selectedScenario = SCENARIOS[scenario];
  const ScenarioIcon = selectedScenario.icon;
  const scenarioRows = data?.scenarios?.[scenario] || [];
  const latest = scenarioRows[scenarioRows.length - 1];

  return (
    <div className="space-y-6">
      {/* Header */}
      <section className="relative overflow-hidden rounded-2xl bg-slate-900 px-6 py-7 text-white shadow-sm sm:px-8">
        <div className="absolute -right-20 -top-24 h-64 w-64 rounded-full bg-emerald-500/10 blur-3xl" />

        <div className="relative">
          <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-xs font-semibold text-emerald-300">
            <TrendingUp className="h-3.5 w-3.5" />
            5-YEAR FUTURE FORECAST
          </div>

          <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
            Cotton Yield Forecast · 2027–2031
          </h1>

          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">
            A separate future-safe ML forecasting module for the 7 Vidarbha
            districts. Future weather is represented with explicit scenarios
            because verified 2027–2031 weather is not available yet.
          </p>
        </div>
      </section>

      {/* Controls */}
      <section className="grid gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm lg:grid-cols-[1fr_1fr_auto]">
        <div>
          <label className="mb-2 block text-xs font-bold uppercase tracking-wider text-slate-500">
            District
          </label>

          <div className="relative">
            <MapPin className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-emerald-600" />

            <select
              value={district}
              onChange={handleDistrictChange}
              className="w-full appearance-none rounded-xl border border-slate-200 bg-slate-50 py-3 pl-10 pr-4 text-sm font-semibold text-slate-800 outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100"
            >
              {DISTRICTS.map((item) => (
                <option key={item} value={item}>
                  {item}, Vidarbha
                </option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="mb-2 block text-xs font-bold uppercase tracking-wider text-slate-500">
            Weather Scenario
          </label>

          <div className="grid grid-cols-3 gap-2">
            {Object.entries(SCENARIOS).map(([key, item]) => {
              const Icon = item.icon;
              const active = scenario === key;

              return (
                <button
                  key={key}
                  type="button"
                  onClick={() => setScenario(key)}
                  className={`flex items-center justify-center gap-2 rounded-xl border px-3 py-3 text-xs font-bold transition ${
                    active
                      ? 'border-emerald-500 bg-emerald-50 text-emerald-700'
                      : 'border-slate-200 bg-slate-50 text-slate-600 hover:border-slate-300'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                </button>
              );
            })}
          </div>
        </div>

        <div className="flex items-end">
          <button
            type="button"
            onClick={() => loadForecast()}
            disabled={loading}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-slate-900 px-5 py-3 text-sm font-bold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60 lg:w-auto"
          >
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="h-4 w-4" />
            )}
            Refresh
          </button>
        </div>
      </section>

      {/* Error */}
      {error && (
        <div className="flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
          <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" />

          <div>
            <p className="font-bold">Forecast unavailable</p>
            <p className="mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Loading */}
      {loading && !data ? (
        <div className="flex min-h-72 items-center justify-center rounded-2xl border border-slate-200 bg-white">
          <div className="text-center">
            <Loader2 className="mx-auto h-8 w-8 animate-spin text-emerald-600" />

            <p className="mt-3 text-sm font-semibold text-slate-600">
              Loading {district} forecast…
            </p>
          </div>
        </div>
      ) : data ? (
        <>
          {/* Summary cards */}
          <section className="grid gap-4 sm:grid-cols-3">
            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex items-center gap-3">
                <div className="rounded-xl bg-emerald-50 p-2.5 text-emerald-600">
                  <Leaf className="h-5 w-5" />
                </div>

                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    2027
                  </p>

                  <p className="text-lg font-bold text-slate-900">
                    {formatYield(
                      scenarioRows[0]?.predicted_yield_kg_ha
                    )}
                  </p>
                </div>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex items-center gap-3">
                <div className="rounded-xl bg-sky-50 p-2.5 text-sky-600">
                  <TrendingUp className="h-5 w-5" />
                </div>

                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    2031
                  </p>

                  <p className="text-lg font-bold text-slate-900">
                    {formatYield(latest?.predicted_yield_kg_ha)}
                  </p>
                </div>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex items-center gap-3">
                <div className="rounded-xl bg-amber-50 p-2.5 text-amber-600">
                  <ScenarioIcon className="h-5 w-5" />
                </div>

                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    Scenario
                  </p>

                  <p className="text-lg font-bold text-slate-900">
                    {selectedScenario.label}
                  </p>
                </div>
              </div>
            </div>
          </section>

          {/* Chart */}
          <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
            <div className="mb-5 flex flex-col justify-between gap-2 sm:flex-row sm:items-center">
              <div>
                <h2 className="text-lg font-bold text-slate-900">
                  {district} · {selectedScenario.label} Weather Scenario
                </h2>

                <p className="mt-1 text-xs text-slate-500">
                  {selectedScenario.description} · predicted yield in kg/ha
                </p>
              </div>

              <span className="rounded-full bg-slate-100 px-3 py-1.5 text-xs font-semibold text-slate-600">
                Forecast origin: 2024
              </span>
            </div>

            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={chartData}
                  margin={{
                    top: 10,
                    right: 20,
                    left: 5,
                    bottom: 5,
                  }}
                >
                  <CartesianGrid strokeDasharray="3 3" />

                  <XAxis dataKey="year" />

                  <YAxis
                    tickFormatter={(value) => `${value}`}
                    width={55}
                  />

                  <Tooltip
                    formatter={(value) => [
                      `${Number(value).toFixed(1)} kg/ha`,
                      'Yield',
                    ]}
                  />

                  <Legend />

                  <Line
                    type="monotone"
                    dataKey="yield"
                    name="Predicted yield"
                    strokeWidth={3}
                    dot={{ r: 5 }}
                    activeDot={{ r: 7 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </section>

          {/* Forecast table */}
          <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
            <div className="border-b border-slate-100 px-5 py-4">
              <h2 className="font-bold text-slate-900">
                2027–2031 Forecast Table
              </h2>

              <p className="mt-1 text-xs text-slate-500">
                Point prediction with historical empirical uncertainty range
              </p>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full min-w-[760px] text-left text-sm">
                <thead className="bg-slate-50 text-xs uppercase tracking-wider text-slate-500">
                  <tr>
                    <th className="px-5 py-3 font-bold">Year</th>

                    <th className="px-5 py-3 font-bold">
                      Predicted Yield
                    </th>

                    <th className="px-5 py-3 font-bold">
                      Empirical Range
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
                  {scenarioRows.map((row) => (
                    <tr
                      key={row.year}
                      className="border-t border-slate-100"
                    >
                      <td className="px-5 py-4 font-bold text-slate-900">
                        {row.year}
                      </td>

                      <td className="px-5 py-4 font-semibold text-emerald-700">
                        {formatYield(row.predicted_yield_kg_ha)}
                      </td>

                      <td className="px-5 py-4">
                        <div className="font-semibold text-slate-800">
                          {formatRange(
                            row.uncertainty_lower_kg_ha,
                            row.uncertainty_upper_kg_ha
                          )}
                        </div>

                        <div className="mt-1 text-xs text-slate-500">
                          ±{formatYield(row.uncertainty_band_kg_ha)}
                        </div>
                      </td>

                      <td className="px-5 py-4 text-slate-600">
                        {row.horizon_years}-year
                      </td>

                      <td className="px-5 py-4 text-slate-600">
                        {row.model}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          {/* Uncertainty explanation */}
          <section className="rounded-2xl border border-sky-200 bg-sky-50 p-5">
            <div className="flex items-start gap-3">
              <TrendingUp className="mt-0.5 h-5 w-5 shrink-0 text-sky-600" />

              <div>
                <h3 className="font-bold text-sky-900">
                  About the uncertainty range
                </h3>

                <p className="mt-1 text-sm leading-6 text-sky-800">
                  The displayed range is an empirical, horizon-specific
                  prediction-error band calibrated using historical
                  out-of-sample forecasts from 2015–2020 and evaluated on
                  2021–2024.
                </p>

                <p className="mt-2 text-sm leading-6 text-sky-800">
                  It is provided to show historical prediction uncertainty
                  and is <strong>not a guaranteed future confidence interval</strong>.
                </p>
              </div>
            </div>
          </section>

          {/* Forecast interpretation */}
          <section className="rounded-2xl border border-amber-200 bg-amber-50 p-5">
            <div className="flex items-start gap-3">
              <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-amber-600" />

              <div>
                <h3 className="font-bold text-amber-900">
                  Forecast interpretation
                </h3>

                <p className="mt-1 text-sm leading-6 text-amber-800">
                  These are model-based future estimates under an explicit
                  weather scenario. They are not verified observations and
                  should not be treated as guaranteed yields. The current
                  2024 validated holdout model remains separate and unchanged.
                </p>
              </div>
            </div>
          </section>
        </>
      ) : null}
    </div>
  );
}

