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
import { SUPPORTED_VIDARBHA_DISTRICTS, sanitizeDistrict } from '../constants/districts';
import WhyThisPrediction from '../components/WhyThisPrediction';


const VIDARBHA_DISTRICTS = SUPPORTED_VIDARBHA_DISTRICTS;


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

  const initialDistrict = sanitizeDistrict(selectedDistrict);

  const [district, setDistrict] =
    useState(initialDistrict);

  const [selectedModelVersion, setSelectedModelVersion] =
    useState('candidate_six_district_thermal');

  useEffect(() => {
    const clean = sanitizeDistrict(selectedDistrict);
    if (clean !== district) {
      setDistrict(clean);
    }
  }, [selectedDistrict]);

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
          year,
          selectedModelVersion
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
  // RESET WHEN DISTRICT, YEAR, OR MODEL CHANGES
  // ==========================================================

  useEffect(() => {

    setInputData(null);
    setWeatherData(null);
    setHistoryData(null);
    setPrediction(null);
    setErrorMessage(null);
    setActiveStep(1);

  }, [district, year, selectedModelVersion]);


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

    if (
      (selectedModelVersion === 'candidate_satellite_smap' ||
        selectedModelVersion === 'candidate_regularized_ensemble') &&
      (year < 2018 || year > 2024)
    ) {
      setErrorMessage(
        `NASA SMAP satellite candidate models are only supported for years 2018–2024 with verified satellite coverage. Year ${year} is outside verified satellite availability. Please switch to the Production or Delta-Rolling model.`
      );
      return;
    }

    if (!VIDARBHA_DISTRICTS.includes(district)) {
      setErrorMessage(
        `Please select a supported district: ${VIDARBHA_DISTRICTS.join(', ')}.`
      );
      return;
    }

    setIsPredicting(true);
    setErrorMessage(null);

    try {

      const response =
        await predictCottonYield({
          district,
          target_year: year,
          model_version: selectedModelVersion,
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

            Verified historical weather + thermal stress features
            → Six-District Thermal Ridge model.

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

              {/* Empirically Calibrated Out-of-Fold Error Bounds */}
              {prediction.prediction_interval && (
                <div className="mt-2 rounded-lg border border-slate-200 bg-slate-50/80 p-3 text-left dark:border-slate-700 dark:bg-slate-800/60">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-slate-700 dark:text-slate-300">
                      {prediction.prediction_interval.description || "Empirically Calibrated Out-of-Fold Error Bounds"}
                    </span>
                    <span className="rounded bg-indigo-100 px-1.5 py-0.5 font-mono text-[10px] font-bold text-indigo-700 dark:bg-indigo-950/70 dark:text-indigo-300">
                      ±{prediction.prediction_interval.half_width_kg_ha} kg/ha
                    </span>
                  </div>
                  <div className="mt-1 flex items-baseline gap-1.5 text-base font-bold text-slate-900 dark:text-white">
                    <span>{prediction.prediction_interval.lower_bound_kg_ha}</span>
                    <span className="text-xs font-normal text-slate-500">to</span>
                    <span>{prediction.prediction_interval.upper_bound_kg_ha}</span>
                    <span className="text-xs font-normal text-slate-500">kg/ha</span>
                  </div>
                  <p className="mt-1.5 text-[10.5px] leading-relaxed text-slate-500 dark:text-slate-400">
                    {prediction.prediction_interval.disclaimer}
                  </p>
                  {prediction.prediction_interval.coverage_warnings?.length > 0 && (
                    <div className="mt-2 space-y-1.5">
                      {prediction.prediction_interval.coverage_warnings.map((warn, wIdx) => (
                        <div key={wIdx} className="flex items-start gap-1.5 rounded border border-amber-300 bg-amber-50 px-2 py-1 text-[11px] text-amber-900 dark:border-amber-700/50 dark:bg-amber-950/40 dark:text-amber-200">
                          <AlertCircle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-amber-600 dark:text-amber-400" />
                          <span>{warn}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}


              <div className="flex flex-wrap items-center gap-1.5 pt-1">
                {prediction.satellite_features_used ? (
                  <span className="inline-flex items-center gap-1 rounded bg-cyan-100 px-2 py-0.5 font-mono text-[10px] font-bold text-cyan-800 dark:bg-cyan-900/60 dark:text-cyan-200">
                    NASA SMAP L4 Active
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 rounded bg-emerald-100 px-2 py-0.5 font-mono text-[10px] font-bold text-emerald-800 dark:bg-emerald-900/60 dark:text-emerald-200">
                    Canonical Weather & Lags
                  </span>
                )}
                <span className="inline-flex items-center gap-1 rounded border border-slate-200 bg-white px-2 py-0.5 font-mono text-[10px] text-slate-700 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300">
                  {prediction.model_name || prediction.model_version}
                </span>
              </div>


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
                label="Model Version"
                value={prediction.model_version || 'production'}
              />

              <MetricRow
                label="Satellite Moisture"
                value={prediction.satellite_features_used ? 'NASA SMAP Active' : 'None (Canonical)'}
                valueClass={prediction.satellite_features_used ? 'text-cyan-600 dark:text-cyan-400' : 'text-slate-900 dark:text-white'}
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


            {/* Why This Prediction? — Explainable AI (XAI) Component */}
            <WhyThisPrediction
              prediction={prediction}
              loading={isPredicting}
              district={district}
              year={year}
            />


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


                {/* Model Version Architecture Selector */}
                <div>

                  <label className="mb-1.5 block text-xs font-semibold text-slate-700 dark:text-slate-300">
                    Model Architecture
                  </label>

                  <select
                    value={selectedModelVersion}
                    onChange={(e) => setSelectedModelVersion(e.target.value)}
                    className="w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-900 outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 dark:border-slate-700 dark:bg-slate-900 dark:text-white"
                  >
                    <option value="candidate_six_district_thermal">
                      Six-District Thermal Ridge (UI Default)
                    </option>
                    <option value="candidate_six_district_dar_deficit_heat_thresh">
                      DAR + Deficit + Heat Thresh (Phase 2 Best Candidate)
                    </option>
                    <option value="candidate_six_district_decoupled_agronomic">
                      Decoupled Agronomic Ridge (Phase 1 Benchmark)
                    </option>
                    <option value="candidate_six_district_physiological">
                      Six-District Physiological Ridge
                    </option>
                    <option value="production">
                      Original 7-District Baseline (GradientBoosting)
                    </option>
                  </select>

                  <p className="mt-1 text-[10px] text-slate-400 dark:text-slate-500">
                    Six-District Thermal Ridge remains the active UI default.
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


                {/* Prediction Model Review Card */}
                {(() => {
                  const modelMetaMap = {
                    candidate_six_district_thermal: {
                      title: 'Prediction Model: Six-District Thermal Ridge',
                      subtitle: 'Active UI Default; chronological CV MAE 104.75 kg/ha.',
                      badge: 'Operational Default',
                      badgeClass: 'bg-emerald-50 text-emerald-800 border-emerald-200',
                      mae: '104.75 kg/ha',
                      rmseWape: '138.10 kg/ha · 32.3%',
                      regime: 'Thermal + 3yr Rolling',
                    },
                    candidate_six_district_dar_deficit_heat_thresh: {
                      title: 'Prediction Model: DAR + Deficit + Heat Threshold',
                      subtitle: 'Phase 2 Best Candidate; chronological CV MAE 102.60 kg/ha.',
                      badge: 'Phase 2 Best Candidate',
                      badgeClass: 'bg-purple-50 text-purple-800 border-purple-200',
                      mae: '102.60 kg/ha',
                      rmseWape: '135.99 kg/ha · 31.8%',
                      regime: 'DAR + Deficit + Heat',
                    },
                    candidate_six_district_decoupled_agronomic: {
                      title: 'Prediction Model: Decoupled Agronomic Ridge',
                      subtitle: 'Phase 1 Benchmark Candidate; chronological CV MAE 104.03 kg/ha.',
                      badge: 'Phase 1 Candidate',
                      badgeClass: 'bg-blue-50 text-blue-800 border-blue-200',
                      mae: '104.03 kg/ha',
                      rmseWape: '137.31 kg/ha · 32.1%',
                      regime: 'Decoupled Anchor + Wetness',
                    },
                    candidate_six_district_physiological: {
                      title: 'Prediction Model: Six-District Physiological Ridge',
                      subtitle: 'Physiological interaction candidate; CV MAE 105.10 kg/ha.',
                      badge: 'Candidate',
                      badgeClass: 'bg-amber-50 text-amber-800 border-amber-200',
                      mae: '105.10 kg/ha',
                      rmseWape: '138.80 kg/ha · 32.5%',
                      regime: '9 Physiological Interactions',
                    },
                    production: {
                      title: 'Prediction Model: 7-District GradientBoosting',
                      subtitle: 'Authoritative 1997-2023 validated baseline pipeline.',
                      badge: '7-District Baseline',
                      badgeClass: 'bg-slate-100 text-slate-800 border-slate-300',
                      mae: '119.84 kg/ha (2024 Holdout)',
                      rmseWape: '138.57 kg/ha · 34.0%',
                      regime: 'Canonical 36 Features',
                    },
                  };
                  const activeMeta = modelMetaMap[selectedModelVersion] || modelMetaMap.candidate_six_district_thermal;

                  return (
                    <div className="space-y-3 rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-900 shadow-xs">
                      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1 border-b border-slate-100 dark:border-slate-800 pb-2.5">
                        <div>
                          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200">
                            {activeMeta.title}
                          </h3>
                          <p className="mt-0.5 text-[11px] text-slate-500 dark:text-slate-400">
                            {activeMeta.subtitle}
                          </p>
                        </div>
                        <span className={`self-start sm:self-auto rounded-full px-2.5 py-0.5 font-mono text-[10px] font-bold border ${activeMeta.badgeClass}`}>
                          {activeMeta.badge}
                        </span>
                      </div>

                      <div className="space-y-2.5 pt-1 text-xs">
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 font-mono text-[11px]">
                          <div className="rounded-md border border-slate-100 bg-slate-50/70 p-2.5 dark:border-slate-800 dark:bg-slate-800/50">
                            <span className="block text-[10px] text-slate-400 uppercase font-sans">Validation MAE</span>
                            <span className="font-bold text-slate-800 dark:text-slate-200">{activeMeta.mae}</span>
                          </div>
                          <div className="rounded-md border border-slate-100 bg-slate-50/70 p-2.5 dark:border-slate-800 dark:bg-slate-800/50">
                            <span className="block text-[10px] text-slate-400 uppercase font-sans">RMSE & WAPE</span>
                            <span className="font-bold text-slate-800 dark:text-slate-200">{activeMeta.rmseWape}</span>
                          </div>
                          <div className="rounded-md border border-slate-100 bg-slate-50/70 p-2.5 dark:border-slate-800 dark:bg-slate-800/50">
                            <span className="block text-[10px] text-slate-400 uppercase font-sans">Feature Regime</span>
                            <span className="font-bold text-slate-800 dark:text-slate-200">{activeMeta.regime}</span>
                          </div>
                        </div>

                        <div className="rounded-md border border-amber-200/80 bg-amber-50/60 p-2.5 text-[11px] leading-relaxed text-amber-900 dark:border-amber-900/50 dark:bg-amber-950/30 dark:text-amber-200">
                          <strong>Experimental Status & Limitations:</strong> Evaluated using expanding-window chronological cross-validation across the six target Vidarbha districts. Like all regression models on coarse seasonal weather aggregates, bumper harvest years (&gt; 408 kg/ha) may experience yield underprediction due to unobserved sub-seasonal pest and bolling micro-factors. Output is an empirical estimate, not a guaranteed forecast.
                        </div>
                      </div>

                      {!VIDARBHA_DISTRICTS.includes(district) && (
                        <div className="rounded-md border border-rose-300 bg-rose-50 p-3 text-[11px] text-rose-800 dark:border-rose-800 dark:bg-rose-950/40 dark:text-rose-200">
                          <strong>District Scope Notice:</strong> Please select one of the supported six Vidarbha districts: <strong>{VIDARBHA_DISTRICTS.join(', ')}</strong>.
                        </div>
                      )}
                    </div>
                  );
                })()}


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
                    disabled={isPredicting || !VIDARBHA_DISTRICTS.includes(district)}
                    className="flex w-2/3 items-center justify-center gap-2 rounded-md bg-emerald-600 py-3 text-xs font-semibold text-white hover:bg-emerald-500 disabled:bg-slate-400 dark:disabled:bg-slate-700"
                  >

                    {isPredicting ? (

                      <>
                        <RefreshCw className="h-4 w-4 animate-spin" />
                        Predicting…
                      </>

                    ) : !VIDARBHA_DISTRICTS.includes(district) ? (

                      <>
                        Select Supported District
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
                  ✓ Six-District Thermal Ridge model with closed-form SHAP feature attributions.
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