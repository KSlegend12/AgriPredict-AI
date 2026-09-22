import React, { useEffect, useMemo, useState } from 'react';

import {
  AlertCircle,
  ArrowDownRight,
  ArrowLeft,
  ArrowRight,
  ArrowUpRight,
  BarChart3,
  Check,
  CheckCircle2,
  Database,
  History,
  MapPin,
  RefreshCw,
  ShieldCheck,
  Sparkles,
} from 'lucide-react';

import {
  getCottonHistory,
  getCottonPredictionInput,
  getCottonWeather,
  predictCottonYield,
} from '../services/api';


const VIDARBHA_DISTRICTS = [
  'Akola',
  'Amravati',
  'Buldhana',
  'Nagpur',
  'Wardha',
  'Washim',
  'Yavatmal',
];


const PREDICTION_YEARS = Array.from(
  { length: 28 },
  (_, i) => 1997 + i
);


// ============================================================
// METRIC ROW
// ============================================================

function MetricRow({
  label,
  value,
  valueClass = 'text-slate-900 dark:text-white',
}) {
  return (
    <div className="flex justify-between gap-4 border-b border-slate-100 pb-2 last:border-b-0 dark:border-slate-700">

      <span className="text-slate-500 dark:text-slate-400">
        {label}
      </span>

      <span
        className={`font-bold text-right ${valueClass}`}
      >
        {value}
      </span>

    </div>
  );
}


// ============================================================
// SHAP CONTRIBUTION BAR
// ============================================================

function ContributionBar({ item }) {

  const value = Number(
    item?.contribution_kg_ha ?? 0
  );

  const positive = value >= 0;

  const width = Math.min(
    100,
    (Math.abs(value) / 150) * 100
  );


  return (
    <div className="space-y-1.5">

      <div className="flex justify-between gap-3 text-xs">

        <span className="font-medium text-slate-700 dark:text-slate-300">
          {item?.display_name || item?.feature}
        </span>

        <span
          className={`font-mono font-bold ${
            positive
              ? 'text-emerald-700 dark:text-emerald-400'
              : 'text-rose-600 dark:text-rose-400'
          }`}
        >
          {positive ? '+' : ''}
          {value.toFixed(2)} kg/ha
        </span>

      </div>


      <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-700">

        <div
          className={`h-full rounded-full ${
            positive
              ? 'bg-emerald-600 dark:bg-emerald-500'
              : 'bg-rose-500 dark:bg-rose-400'
          }`}
          style={{
            width: `${width}%`,
          }}
        />

      </div>

    </div>
  );
}


// ============================================================
// MAIN PAGE
// ============================================================

export default function CottonYieldPage({
  selectedDistrict,
  setSelectedDistrict,
}) {

  const initialDistrict =
    VIDARBHA_DISTRICTS.includes(
      selectedDistrict
    )
      ? selectedDistrict
      : 'Akola';


  const [district, setDistrict] =
    useState(initialDistrict);

  const [year, setYear] =
    useState(2024);

  const [activeStep, setActiveStep] =
    useState(1);

  const [inputData, setInputData] =
    useState(null);

  const [weatherData, setWeatherData] =
    useState(null);

  const [historyData, setHistoryData] =
    useState(null);

  const [prediction, setPrediction] =
    useState(null);

  const [loadingInput, setLoadingInput] =
    useState(false);

  const [isPredicting, setIsPredicting] =
    useState(false);

  const [errorMessage, setErrorMessage] =
    useState(null);


  // ==========================================================
  // LOAD VERIFIED DATA
  // ==========================================================

  const loadVerifiedData = async () => {

    setLoadingInput(true);
    setErrorMessage(null);
    setPrediction(null);

    try {

      const [
        input,
        weather,
        history,
      ] = await Promise.all([
        getCottonPredictionInput(
          district,
          year
        ),

        getCottonWeather(
          district,
          year
        ),

        getCottonHistory(
          district
        ),
      ]);


      setInputData(input);
      setWeatherData(weather);
      setHistoryData(history);

      setActiveStep(2);

    } catch (err) {

      setInputData(null);
      setWeatherData(null);
      setHistoryData(null);

      setErrorMessage(
        err?.response?.data?.detail ||
        'Verified data could not be loaded.'
      );

    } finally {

      setLoadingInput(false);

    }
  };


  // ==========================================================
  // RESET WHEN DISTRICT CHANGES
  // ==========================================================

  useEffect(() => {

    setInputData(null);
    setWeatherData(null);
    setHistoryData(null);
    setPrediction(null);
    setErrorMessage(null);
    setActiveStep(1);

  }, [district]);


  // ==========================================================
  // DISTRICT HANDLER
  // ==========================================================

  const handleDistrict = (value) => {

    setDistrict(value);

    setSelectedDistrict?.(value);

  };


  // ==========================================================
  // PREDICT
  // ==========================================================

  const handlePredict = async () => {

    if (!inputData) return;

    setIsPredicting(true);
    setErrorMessage(null);

    try {

      const response =
        await predictCottonYield({
          district,
          target_year: year,
        });


      setPrediction(response);

      setActiveStep(5);

    } catch (err) {

      setErrorMessage(
        err?.response?.data?.detail ||
        'Unable to generate prediction.'
      );

      setActiveStep(4);

    } finally {

      setIsPredicting(false);

    }
  };


  // ==========================================================
  // DERIVED DATA
  // ==========================================================

  const featureCount = useMemo(
    () =>
      Object.keys(
        inputData?.features || {}
      ).length,
    [inputData]
  );


  const explanation =
    prediction?.explanation;


  const validation =
    prediction?.validation_context || {};


  const weather =
    weatherData?.weather || {};


  const history =
    historyData?.records || [];


  const lastThree =
    history
      .filter((r) => r.year < year)
      .slice(-3);


  // ==========================================================
  // UI
  // ==========================================================

  return (

    <div className="mx-auto max-w-7xl space-y-6 py-4">


      {/* ======================================================
          HEADER
      ====================================================== */}

      <div className="flex flex-col justify-between gap-4 border-b border-slate-200 pb-4 dark:border-slate-700 md:flex-row md:items-center">

        <div>

          <div className="mb-1 inline-flex items-center gap-1.5 rounded-md border border-emerald-200 bg-emerald-50 px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wider text-emerald-800 dark:border-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300">

            <ShieldCheck className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400" />

            Vidarbha Cotton Yield Intelligence

          </div>


          <h1 className="text-2xl font-extrabold tracking-tight text-slate-900 dark:text-white sm:text-3xl">

            Cotton Yield Prediction

          </h1>


          <p className="text-xs text-slate-500 dark:text-slate-400">

            Verified historical weather + agricultural features
            → validated GradientBoosting model.

          </p>

        </div>


        <div className="flex items-center gap-2 font-mono text-xs">

          <span className="rounded-md border border-slate-300 bg-white px-3 py-1 font-semibold text-slate-800 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-200">

            {district}, Vidarbha · {year}

          </span>

        </div>

      </div>


      {/* ======================================================
          STEPPER
      ====================================================== */}

      <div className="agri-card border border-slate-200 p-3 shadow-xs dark:border-slate-700">

        <div className="mx-auto flex max-w-5xl items-center justify-between overflow-x-auto">

          {[
            ['01', 'District'],
            ['02', 'Verified Data'],
            ['03', 'History'],
            ['04', 'Review'],
            ['05', 'Prediction & Explanation'],
          ].map(([num, label], index) => {

            const n = index + 1;

            const active =
              activeStep === n;

            const done =
              activeStep > n;


            return (

              <React.Fragment key={num}>

                <button
                  type="button"
                  onClick={() =>
                    n === 1 ||
                    (n > 1 && inputData)
                      ? setActiveStep(n)
                      : null
                  }
                  className="flex shrink-0 items-center gap-2 rounded-md px-2.5 py-1 hover:bg-slate-50 dark:hover:bg-slate-800"
                >

                  <div
                    className={`flex h-6 w-6 items-center justify-center rounded-md font-mono text-xs font-bold ${
                      active
                        ? 'bg-emerald-600 text-white'
                        : done
                        ? 'border border-emerald-300 bg-emerald-100 text-emerald-800 dark:border-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300'
                        : 'border border-slate-200 bg-slate-100 text-slate-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-400'
                    }`}
                  >

                    {done ? (
                      <Check className="h-3.5 w-3.5" />
                    ) : (
                      num
                    )}

                  </div>


                  <span
                    className={`whitespace-nowrap text-xs ${
                      active
                        ? 'font-bold text-slate-900 dark:text-white'
                        : 'text-slate-500 dark:text-slate-400'
                    }`}
                  >
                    {label}
                  </span>

                </button>


                {index < 4 && (

                  <div
                    className={`mx-1 h-0.5 min-w-[16px] flex-1 ${
                      activeStep > n
                        ? 'bg-emerald-500'
                        : 'bg-slate-200 dark:bg-slate-700'
                    }`}
                  />

                )}

              </React.Fragment>

            );

          })}

        </div>

      </div>


      {/* ======================================================
          ERROR
      ====================================================== */}

      {errorMessage && (

        <div className="flex items-center gap-3 rounded-md border border-rose-200 bg-rose-50 p-4 text-xs text-rose-800 dark:border-rose-800 dark:bg-rose-950/30 dark:text-rose-200">

          <AlertCircle className="h-5 w-5 text-rose-600 dark:text-rose-400" />

          <div>

            <strong className="block">
              Prediction Error
            </strong>

            {errorMessage}

          </div>

        </div>

      )}


      {/* ======================================================
          FINAL PREDICTION
      ====================================================== */}

      {activeStep === 5 && prediction ? (

        <div className="grid grid-cols-1 items-start gap-6 lg:grid-cols-12">


          {/* LEFT */}

          <div className="space-y-5 lg:col-span-4">


            {/* Prediction generated */}

            <div className="agri-card space-y-3 border border-emerald-200 bg-emerald-50/40 p-5 dark:border-emerald-800 dark:bg-emerald-950/20">

              <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-emerald-800 dark:text-emerald-300">

                <CheckCircle2 className="h-4 w-4" />

                Prediction Generated

              </div>


              <div className="text-4xl font-extrabold text-slate-900 dark:text-white">

                {Number(
                  prediction.predicted_yield_kg_ha
                ).toFixed(1)}

                <span className="text-sm font-semibold text-slate-500 dark:text-slate-400">
                  {' '}kg/ha
                </span>

              </div>


              <p className="text-xs text-slate-600 dark:text-slate-300">

                {district} · {year} ·{' '}
                {prediction.prediction_status?.replaceAll(
                  '_',
                  ' '
                )}

              </p>


              <button
                type="button"
                onClick={() => setActiveStep(1)}
                className="flex w-full items-center justify-center gap-2 rounded-md border border-slate-300 bg-white py-2.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800"
              >

                <ArrowLeft className="h-4 w-4" />

                Modify Selection

              </button>

            </div>


            {/* Data provenance */}

            <div className="agri-card space-y-3 border border-slate-200 p-5 dark:border-slate-700">

              <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200">

                <Database className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />

                Data Provenance

              </div>


              <MetricRow
                label="Dataset"
                value="Model-ready panel"
              />

              <MetricRow
                label="Prediction year"
                value={year}
              />

              <MetricRow
                label="Features supplied"
                value={featureCount}
              />

              <MetricRow
                label="Training period"
                value={
                  validation.training_period ||
                  '1997–2023'
                }
              />

              <MetricRow
                label="Final holdout"
                value="2024"
              />

            </div>

          </div>


          {/* RIGHT */}

          <div className="space-y-5 lg:col-span-8">


            {/* SHAP */}

            <div className="agri-card space-y-4 border border-slate-200 p-5 dark:border-slate-700">

              <div className="flex items-center gap-2">

                <Sparkles className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />

                <h2 className="font-bold text-slate-900 dark:text-white">

                  Why did the model produce this estimate?

                </h2>

              </div>


              <p className="text-xs text-slate-600 dark:text-slate-300">

                {explanation?.summary_text ||
                  'SHAP explanation unavailable.'}

              </p>


              <div className="grid gap-5 md:grid-cols-2">


                {/* Increasing */}

                <div className="space-y-3">

                  <h3 className="flex items-center gap-1 text-xs font-bold text-emerald-800 dark:text-emerald-300">

                    <ArrowUpRight className="h-4 w-4" />

                    Increasing factors

                  </h3>


                  {(explanation?.increasing_factors || []).map(
                    (x) => (
                      <ContributionBar
                        key={x.feature}
                        item={x}
                      />
                    )
                  )}

                </div>


                {/* Decreasing */}

                <div className="space-y-3">

                  <h3 className="flex items-center gap-1 text-xs font-bold text-rose-700 dark:text-rose-400">

                    <ArrowDownRight className="h-4 w-4" />

                    Decreasing factors

                  </h3>


                  {(explanation?.decreasing_factors || []).map(
                    (x) => (
                      <ContributionBar
                        key={x.feature}
                        item={x}
                      />
                    )
                  )}

                </div>

              </div>

            </div>


            {/* Validation */}

            <div className="agri-card space-y-4 border border-slate-200 p-5 dark:border-slate-700">

              <div className="flex items-center gap-2">

                <BarChart3 className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />

                <h2 className="font-bold text-slate-900 dark:text-white">

                  Validation context

                </h2>

              </div>


              <div className="grid grid-cols-2 gap-3 text-xs md:grid-cols-4">

                <MetricRow
                  label="CV MAE"
                  value={`${validation.mean_mae_kg_ha ?? '—'} kg/ha`}
                />

                <MetricRow
                  label="CV RMSE"
                  value={`${prediction.validation_metrics?.Mean_RMSE_kg_ha ?? '—'} kg/ha`}
                />

                <MetricRow
                  label="CV MAPE"
                  value={`${prediction.validation_metrics?.Mean_MAPE_percent ?? '—'}%`}
                />

                <MetricRow
                  label="2024 holdout MAE"
                  value={`${validation.holdout_mae_kg_ha ?? '—'} kg/ha`}
                />

              </div>


              <p className="text-[11px] text-slate-500 dark:text-slate-400">

                These are validation metrics, not a confidence
                interval. 2024 remains the final untouched
                evaluation holdout.

              </p>

            </div>

          </div>

        </div>

      ) : (

        <div className="grid grid-cols-1 items-start gap-6 lg:grid-cols-12">


          {/* ==================================================
              LEFT MAIN FORM
          ================================================== */}

          <div className="agri-card space-y-5 border border-slate-200 p-6 shadow-xs dark:border-slate-700 lg:col-span-7">


            {/* STEP 1 */}

            {activeStep === 1 && (

              <div className="space-y-5">


                <div className="flex items-center justify-between border-b border-slate-100 pb-2 dark:border-slate-700">

                  <span className="rounded-md border border-emerald-200 bg-emerald-50 px-2 py-0.5 font-mono text-[10px] font-bold uppercase tracking-widest text-emerald-800 dark:border-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300">

                    STEP 01 / 05

                  </span>


                  <MapPin className="h-4 w-4 text-slate-400 dark:text-slate-500" />

                </div>


                <h2 className="text-xl font-bold text-slate-900 dark:text-white">

                  Select District & Prediction Year

                </h2>


                <p className="text-xs text-slate-500 dark:text-slate-400">

                  The backend will fetch the complete model-ready
                  feature row from the authoritative Vidarbha cotton
                  panel. No synthetic weather values are created.

                </p>


                {/* Districts */}

                <div className="grid gap-2 sm:grid-cols-2">

                  {VIDARBHA_DISTRICTS.map(
                    (item) => {

                      const selected =
                        district === item;


                      return (

                        <button
                          key={item}
                          type="button"
                          onClick={() =>
                            handleDistrict(item)
                          }
                          className={`flex items-center justify-between rounded-lg border p-3 text-left text-xs font-semibold transition ${
                            selected
                              ? 'border-emerald-500 bg-emerald-50 text-emerald-950 dark:border-emerald-400 dark:bg-emerald-950/50 dark:text-emerald-200'
                              : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800'
                          }`}
                        >

                          <span>
                            {item} District
                          </span>


                          <span
                            className={`text-[10px] ${
                              selected
                                ? 'text-emerald-700 dark:text-emerald-300'
                                : 'text-slate-400 dark:text-slate-500'
                            }`}
                          >
                            Vidarbha
                          </span>

                        </button>

                      );

                    }
                  )}

                </div>


                {/* Year */}

                <div>

                  <label className="mb-1.5 block text-xs font-semibold text-slate-700 dark:text-slate-300">

                    Target Year

                  </label>


                  <select
                    value={year}
                    onChange={(e) =>
                      setYear(
                        Number(e.target.value)
                      )
                    }
                    className="w-full rounded-md border border-slate-200 bg-white px-3 py-2.5 text-sm font-semibold text-slate-900 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 dark:border-slate-700 dark:bg-slate-900 dark:text-white"
                  >

                    {PREDICTION_YEARS.map(
                      (y) => (

                        <option
                          key={y}
                          value={y}
                          className="bg-white text-slate-900 dark:bg-slate-900 dark:text-white"
                        >

                          {y}

                          {y === 2024
                            ? ' — final holdout'
                            : ''}

                        </option>

                      )
                    )}

                  </select>


                  <p className="mt-1 text-[10px] text-slate-400 dark:text-slate-500">

                    Currently verified model-ready
                    historical years: 1997–2024.

                  </p>

                </div>


                {/* Load */}

                <button
                  type="button"
                  onClick={loadVerifiedData}
                  disabled={loadingInput}
                  className="flex w-full items-center justify-center gap-2 rounded-md bg-emerald-600 py-3 text-xs font-semibold text-white transition hover:bg-emerald-500 disabled:bg-emerald-300 dark:disabled:bg-emerald-900"
                >

                  {loadingInput ? (

                    <>
                      <RefreshCw className="h-4 w-4 animate-spin" />

                      Loading verified data…

                    </>

                  ) : (

                    <>
                      Load Verified Data

                      <ArrowRight className="h-4 w-4" />

                    </>

                  )}

                </button>

              </div>

            )}


            {/* =================================================
                STEP 2
            ================================================= */}

            {activeStep === 2 && inputData && (

              <div className="space-y-5">


                <div className="flex items-center justify-between border-b border-slate-100 pb-2 dark:border-slate-700">

                  <span className="rounded-md border border-emerald-200 bg-emerald-50 px-2 py-0.5 font-mono text-[10px] font-bold uppercase tracking-widest text-emerald-800 dark:border-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300">

                    STEP 02 / 05

                  </span>


                  <span className="font-mono text-xs text-slate-500 dark:text-slate-400">

                    VERIFIED WEATHER

                  </span>

                </div>


                <h2 className="text-xl font-bold text-slate-900 dark:text-white">

                  Verified Weather & Area

                </h2>


                <div className="rounded-md border border-emerald-200 bg-emerald-50 p-3 text-[11px] text-emerald-900 dark:border-emerald-800 dark:bg-emerald-950/30 dark:text-emerald-200">

                  <strong>Source:</strong>{' '}

                  {inputData.source?.dataset}.

                  {' '}Values below are read-only model inputs;
                  nothing is estimated in the frontend.

                </div>


                <div className="grid gap-3 sm:grid-cols-2">

                  <MetricRow
                    label="Cotton area"
                    value={`${Number(inputData.features.cotton_area_000ha).toFixed(2)} 000ha`}
                    valueClass="text-emerald-700 dark:text-emerald-400"
                  />

                  <MetricRow
                    label="Annual rainfall"
                    value={`${Number(weather.rainfall_annual_mm).toFixed(1)} mm`}
                    valueClass="text-teal-700 dark:text-teal-400"
                  />

                  <MetricRow
                    label="Kharif rainfall"
                    value={`${Number(weather.rainfall_kharif_mm).toFixed(1)} mm`}
                  />

                  <MetricRow
                    label="Monsoon rainfall"
                    value={`${Number(weather.rainfall_monsoon_mm).toFixed(1)} mm`}
                  />

                  <MetricRow
                    label="Annual mean Tmax"
                    value={`${Number(weather.tmax_annual_mean_c).toFixed(1)} °C`}
                  />

                  <MetricRow
                    label="Kharif mean Tmax"
                    value={`${Number(weather.tmax_kharif_mean_c).toFixed(1)} °C`}
                  />

                  <MetricRow
                    label="Annual mean Tmin"
                    value={`${Number(weather.tmin_annual_mean_c).toFixed(1)} °C`}
                  />

                  <MetricRow
                    label="Max dry spell"
                    value={`${Number(weather.max_dry_spell_annual_days).toFixed(0)} days`}
                  />

                  <MetricRow
                    label="Rainy days"
                    value={`${Number(weather.rainy_days_annual).toFixed(0)}`}
                  />

                  <MetricRow
                    label="Heavy rain days"
                    value={`${Number(weather.heavy_rain_days_annual).toFixed(0)}`}
                  />

                </div>


                <div className="flex gap-2">

                  <button
                    type="button"
                    onClick={() => setActiveStep(1)}
                    className="w-1/3 rounded-md bg-slate-100 py-2.5 text-xs text-slate-700 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700"
                  >
                    Back
                  </button>


                  <button
                    type="button"
                    onClick={() => setActiveStep(3)}
                    className="flex w-2/3 items-center justify-center gap-2 rounded-md bg-emerald-600 py-2.5 text-xs font-semibold text-white hover:bg-emerald-500"
                  >

                    View Historical Features

                    <ArrowRight className="h-4 w-4" />

                  </button>

                </div>

              </div>

            )}


            {/* =================================================
                STEP 3
            ================================================= */}

            {activeStep === 3 && inputData && (

              <div className="space-y-5">


                <div className="flex items-center justify-between border-b border-slate-100 pb-2 dark:border-slate-700">

                  <span className="rounded-md border border-emerald-200 bg-emerald-50 px-2 py-0.5 font-mono text-[10px] font-bold uppercase tracking-widest text-emerald-800 dark:border-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300">

                    STEP 03 / 05

                  </span>


                  <History className="h-4 w-4 text-slate-400 dark:text-slate-500" />

                </div>


                <h2 className="text-xl font-bold text-slate-900 dark:text-white">

                  Automatic Historical Yield Features

                </h2>


                <p className="text-xs text-slate-500 dark:text-slate-400">

                  Lag features are calculated from recorded yields
                  before the selected year. You do not enter them
                  manually.

                </p>


                <div className="grid gap-3 sm:grid-cols-3">

                  <div className="rounded-md border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-900">

                    <div className="text-[10px] text-slate-500 dark:text-slate-400">
                      Previous year
                    </div>

                    <div className="text-lg font-bold text-slate-900 dark:text-white">

                      {inputData.features.previous_year_yield_kg_ha == null
                        ? 'Imputed'
                        : `${Number(inputData.features.previous_year_yield_kg_ha).toFixed(1)} kg/ha`}

                    </div>

                  </div>


                  <div className="rounded-md border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-900">

                    <div className="text-[10px] text-slate-500 dark:text-slate-400">
                      Previous 2-year
                    </div>

                    <div className="text-lg font-bold text-slate-900 dark:text-white">

                      {inputData.features.previous_2year_yield_kg_ha == null
                        ? 'Imputed'
                        : `${Number(inputData.features.previous_2year_yield_kg_ha).toFixed(1)} kg/ha`}

                    </div>

                  </div>


                  <div className="rounded-md border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-900">

                    <div className="text-[10px] text-slate-500 dark:text-slate-400">
                      3-year rolling
                    </div>

                    <div className="text-lg font-bold text-slate-900 dark:text-white">

                      {inputData.features.rolling_3yr_yield_mean_kg_ha == null
                        ? 'Imputed'
                        : `${Number(inputData.features.rolling_3yr_yield_mean_kg_ha).toFixed(1)} kg/ha`}

                    </div>

                  </div>

                </div>


                <div className="rounded-md border border-blue-200 bg-blue-50 p-3 text-[11px] text-blue-800 dark:border-blue-800 dark:bg-blue-950/30 dark:text-blue-200">

                  {lastThree.length
                    ? `Recorded yields available before ${year}: ${lastThree.map((r) => `${r.year}: ${Number(r.yield_kg_ha).toFixed(1)} kg/ha`).join(' · ')}`
                    : 'Early years may have missing lag values; the model pipeline handles those using training-time preprocessing.'}

                </div>


                <div className="flex gap-2">

                  <button
                    type="button"
                    onClick={() => setActiveStep(2)}
                    className="w-1/3 rounded-md bg-slate-100 py-2.5 text-xs text-slate-700 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700"
                  >
                    Back
                  </button>


                  <button
                    type="button"
                    onClick={() => setActiveStep(4)}
                    className="flex w-2/3 items-center justify-center gap-2 rounded-md bg-emerald-600 py-2.5 text-xs font-semibold text-white hover:bg-emerald-500"
                  >

                    Review

                    <ArrowRight className="h-4 w-4" />

                  </button>

                </div>

              </div>

            )}


            {/* =================================================
                STEP 4
            ================================================= */}

            {activeStep === 4 && inputData && (

              <div className="space-y-5">


                <div className="flex items-center justify-between border-b border-slate-100 pb-2 dark:border-slate-700">

                  <span className="rounded-md border border-emerald-200 bg-emerald-50 px-2 py-0.5 font-mono text-[10px] font-bold uppercase tracking-widest text-emerald-800 dark:border-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300">

                    STEP 04 / 05

                  </span>


                  <span className="font-mono text-xs text-slate-500 dark:text-slate-400">
                    REVIEW
                  </span>

                </div>


                <h2 className="text-xl font-bold text-slate-900 dark:text-white">

                  Review Verified Model Inputs

                </h2>


                <div className="space-y-2 rounded-lg border border-slate-200 bg-slate-50 p-4 text-xs font-mono dark:border-slate-700 dark:bg-slate-900">

                  <MetricRow
                    label="District"
                    value={district}
                  />

                  <MetricRow
                    label="Target year"
                    value={year}
                  />

                  <MetricRow
                    label="Feature count"
                    value={`${featureCount} model features`}
                  />

                  <MetricRow
                    label="Area"
                    value={`${Number(inputData.features.cotton_area_000ha).toFixed(2)} 000 ha`}
                  />

                  <MetricRow
                    label="Annual rainfall"
                    value={`${Number(inputData.features.rainfall_annual_mm).toFixed(1)} mm`}
                  />

                  <MetricRow
                    label="3-year rolling yield"
                    value={
                      inputData.features.rolling_3yr_yield_mean_kg_ha == null
                        ? 'Training-time imputation'
                        : `${Number(inputData.features.rolling_3yr_yield_mean_kg_ha).toFixed(1)} kg/ha`
                    }
                  />

                </div>


                <div className="rounded-md border border-blue-200 bg-blue-50 p-3 text-[11px] leading-relaxed text-blue-800 dark:border-blue-800 dark:bg-blue-950/30 dark:text-blue-200">

                  <strong>Important:</strong>{' '}
                  The target yield is excluded from the prediction
                  input. For 2024, this is the model's final
                  untouched holdout year.

                </div>


                <div className="flex gap-2">

                  <button
                    type="button"
                    onClick={() => setActiveStep(3)}
                    className="w-1/3 rounded-md bg-slate-100 py-2.5 text-xs text-slate-700 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700"
                  >
                    Back
                  </button>


                  <button
                    type="button"
                    onClick={handlePredict}
                    disabled={isPredicting}
                    className="flex w-2/3 items-center justify-center gap-2 rounded-md bg-emerald-600 py-3 text-xs font-semibold text-white hover:bg-emerald-500 disabled:bg-emerald-300 dark:disabled:bg-emerald-900"
                  >

                    {isPredicting ? (

                      <>
                        <RefreshCw className="h-4 w-4 animate-spin" />
                        Predicting…
                      </>

                    ) : (

                      <>
                        Generate Prediction
                        <Sparkles className="h-4 w-4" />
                      </>

                    )}

                  </button>

                </div>

              </div>

            )}

          </div>


          {/* ==================================================
              RIGHT INFORMATION PANEL
          ================================================== */}

          <div className="space-y-5 lg:col-span-5">


            {/* HOW IT WORKS */}

            <div className="agri-card space-y-4 border border-slate-200 p-5 dark:border-slate-700">

              <div className="flex items-center gap-2">

                <Database className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />

                <h2 className="font-bold text-slate-900 dark:text-white">

                  How this version works

                </h2>

              </div>


              <ul className="space-y-3 text-xs text-slate-600 dark:text-slate-300">

                <li>
                  ✓ Select district and year.
                </li>

                <li>
                  ✓ Backend reads the exact verified model-ready row.
                </li>

                <li>
                  ✓ Weather and lag features are no longer invented by the frontend.
                </li>

                <li>
                  ✓ The target yield is excluded before prediction.
                </li>

                <li>
                  ✓ The existing validated GradientBoosting model and SHAP explanation are reused.
                </li>

              </ul>

            </div>


            {/* SELECTED DATA */}

            <div className="agri-card space-y-3 border border-slate-200 p-5 dark:border-slate-700">

              <div className="flex items-center gap-2">

                <BarChart3 className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />

                <h2 className="font-bold text-slate-900 dark:text-white">

                  Selected data

                </h2>

              </div>


              <MetricRow
                label="District"
                value={district}
              />

              <MetricRow
                label="Year"
                value={year}
              />

              <MetricRow
                label="Verified data loaded"
                value={
                  inputData
                    ? 'Yes'
                    : 'No'
                }
                valueClass={
                  inputData
                    ? 'text-emerald-700 dark:text-emerald-400'
                    : 'text-slate-500 dark:text-slate-400'
                }
              />


              {weatherData && (

                <MetricRow
                  label="Annual rainfall"
                  value={`${Number(weather.rainfall_annual_mm).toFixed(1)} mm`}
                />

              )}

            </div>

          </div>

        </div>

      )}

    </div>
  );
}