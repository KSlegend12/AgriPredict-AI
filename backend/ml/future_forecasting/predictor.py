"""
Inference helper for the future cotton-yield forecasting module.

IMPORTANT:
- This module is separate from the validated 2024 model.
- It never changes the authoritative dataset.
- Future weather is scenario-generated because verified 2027-2031 weather is unavailable.
- Uncertainty bands are based on historical out-of-sample calibration.
"""

from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd


HERE = Path(__file__).resolve()
BACKEND_DIR = HERE.parents[2]
MODULE_DIR = BACKEND_DIR / "ml" / "future_forecasting"

DATA_PATH = BACKEND_DIR / "data" / "vidarbha_cotton_model_ready_1997_2024.csv"

MODEL_PATH = MODULE_DIR / "artifacts" / "future_horizon_models.joblib"

UNCERTAINTY_PATH = (
    MODULE_DIR / "artifacts" / "uncertainty_calibration.json"
)


DISTRICTS = [
    "Akola",
    "Amravati",
    "Buldhana",
    "Nagpur",
    "Wardha",
    "Washim",
    "Yavatmal",
]

SCENARIOS = ("normal", "dry", "wet")

FORECAST_YEARS = tuple(range(2027, 2032))


_WEATHER_PREFIXES = (
    "tmax_",
    "tmin_",
    "rainfall_",
    "rainy_days_",
    "heavy_rain_days_",
    "max_5day_",
    "max_dry_spell_",
)


def _load():
    """Load authoritative data, future models, and uncertainty calibration."""

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Authoritative dataset not found: {DATA_PATH}"
        )

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Future model artifact not found: {MODEL_PATH}"
        )

    if not UNCERTAINTY_PATH.exists():
        raise FileNotFoundError(
            f"Uncertainty calibration artifact not found: {UNCERTAINTY_PATH}"
        )

    df = (
        pd.read_csv(DATA_PATH)
        .sort_values(["district", "year"])
        .reset_index(drop=True)
    )

    models = joblib.load(MODEL_PATH)

    uncertainty = json.loads(
        UNCERTAINTY_PATH.read_text()
    )

    return df, models, uncertainty


def _weather_columns(df):
    cols = [
        c
        for c in df.columns
        if c.startswith(_WEATHER_PREFIXES)
        and "anomaly" not in c
    ]

    anomaly = [
        c
        for c in df.columns
        if c.endswith("_district_anomaly")
    ]

    return cols, anomaly


def _future_weather(df, district, year, scenario):
    g = df[df["district"] == district].sort_values("year")

    recent = g.tail(10)

    weather_cols, anomaly_cols = _weather_columns(df)

    out = {}

    for c in weather_cols:
        val = recent[c].mean()

        out[c] = (
            float(val)
            if pd.notna(val)
            else np.nan
        )

    # Temperature uses the recent historical linear trend only.
    temp_cols = [
        c
        for c in weather_cols
        if c.startswith(("tmax_", "tmin_"))
    ]

    for c in temp_cols:
        valid = recent[["year", c]].dropna()

        if len(valid) >= 5:
            slope = np.polyfit(
                valid["year"].to_numpy(),
                valid[c].to_numpy(),
                1,
            )[0]

            out[c] = float(
                valid[c].mean()
                + slope
                * (year - valid["year"].mean())
            )

    rainfall_mult = {
        "normal": 1.00,
        "dry": 0.80,
        "wet": 1.20,
    }[scenario]

    day_mult = {
        "normal": 1.00,
        "dry": 0.85,
        "wet": 1.15,
    }[scenario]

    extreme_mult = {
        "normal": 1.00,
        "dry": 0.90,
        "wet": 1.10,
    }[scenario]

    dryspell_mult = {
        "normal": 1.00,
        "dry": 1.20,
        "wet": 0.85,
    }[scenario]

    rain_cols = [
        "rainfall_annual_mm",
        "rainfall_monsoon_mm",
        "rainfall_kharif_mm",
    ]

    count_cols = [
        "rainy_days_annual",
        "heavy_rain_days_annual",
        "rainy_days_monsoon",
        "heavy_rain_days_monsoon",
        "rainy_days_kharif",
        "heavy_rain_days_kharif",
    ]

    maxrain_cols = [
        c
        for c in weather_cols
        if "rainfall_max" in c
        or "max_5day" in c
    ]

    dry_cols = [
        c
        for c in weather_cols
        if "max_dry_spell" in c
    ]

    for c in rain_cols:
        if c in out and pd.notna(out[c]):
            out[c] *= rainfall_mult

    for c in count_cols:
        if c in out and pd.notna(out[c]):
            out[c] *= day_mult

    for c in maxrain_cols:
        if c in out and pd.notna(out[c]):
            out[c] *= extreme_mult

    for c in dry_cols:
        if c in out and pd.notna(out[c]):
            out[c] *= dryspell_mult

    # Recalculate anomaly fields against the district historical mean.
    for base in (
        "rainfall_monsoon_mm",
        "rainfall_kharif_mm",
        "tmax_kharif_mean_c",
        "tmin_kharif_mean_c",
    ):
        anomaly = base + "_district_anomaly"

        if anomaly in anomaly_cols and base in out:
            out[anomaly] = float(
                out[base] - g[base].mean()
            )

    return out


def _future_row(
    df,
    district,
    target_year,
    horizon,
    scenario,
):
    g = df[df["district"] == district].sort_values("year")

    observed = g[g["year"] <= 2024]

    if len(observed) < 5:
        raise ValueError(
            f"Not enough historical rows for {district}"
        )

    last3 = observed.tail(3)["yield_target_kg_ha"]

    last5 = observed.tail(5)["yield_target_kg_ha"]

    area5 = observed.tail(5)["cotton_area_000ha"]

    row = {
        "district": district,
        "target_year": int(target_year),
        "horizon": int(horizon),
        "origin_year": 2024,

        "y_lag1": float(
            observed.iloc[-1]["yield_target_kg_ha"]
        ),

        "y_lag2": float(
            observed.iloc[-2]["yield_target_kg_ha"]
        ),

        "y_roll3": float(
            last3.mean()
        ),

        "y_std5": float(
            last5.std(ddof=0)
        ),

        "y_slope3": float(
            np.polyfit(
                np.arange(3),
                last3.to_numpy(),
                1,
            )[0]
        ),

        "area_origin": float(
            observed.iloc[-1]["cotton_area_000ha"]
        ),

        "area_slope5": float(
            np.polyfit(
                np.arange(5),
                area5.to_numpy(),
                1,
            )[0]
        ),
    }

    row.update(
        _future_weather(
            df,
            district,
            target_year,
            scenario,
        )
    )

    return row


def forecast_district(district: str):
    if district not in DISTRICTS:
        raise ValueError(
            f"Unknown district: {district}. "
            f"Allowed: {', '.join(DISTRICTS)}"
        )

    df, models, uncertainty = _load()

    result = {
        "district": district,
        "origin_year": 2024,
        "forecast_years": list(FORECAST_YEARS),
        "scenarios": {},
        "method": "direct horizon-specific ML models",
        "weather_note": (
            "2027-2031 weather is scenario-based, "
            "not verified future weather."
        ),
        "uncertainty_note": (
            "Empirical horizon-specific prediction "
            "error bands calibrated on 2015-2020 and "
            "evaluated on 2021-2024. These are not "
            "guaranteed future confidence intervals."
        ),
    }

    for scenario in SCENARIOS:
        items = []

        for year in FORECAST_YEARS:

            horizon = year - 2024

            bundle = models[horizon]

            row = _future_row(
                df,
                district,
                year,
                horizon,
                scenario,
            )

            X = pd.DataFrame([row])[
                bundle["feature_cols"]
            ]

            pred = float(
                bundle["pipeline"].predict(X)[0]
            )

            # Existing point prediction remains unchanged.
            point = max(0.0, pred)

            # Horizon-specific empirical uncertainty band.
            band = float(
                uncertainty[
                    "horizon_q90_kg_ha"
                ][str(horizon)]
            )

            lower = max(
                0.0,
                point - band,
            )

            upper = point + band

            items.append({
                "year": year,

                "predicted_yield_kg_ha": round(
                    point,
                    2,
                ),

                "uncertainty_lower_kg_ha": round(
                    lower,
                    2,
                ),

                "uncertainty_upper_kg_ha": round(
                    upper,
                    2,
                ),

                "uncertainty_band_kg_ha": round(
                    band,
                    2,
                ),

                "uncertainty_method": uncertainty[
                    "method"
                ],

                "model": bundle[
                    "selected_model"
                ],

                "horizon_years": horizon,
            })

        result["scenarios"][scenario] = items

    return result


def forecast_all():
    return [
        forecast_district(d)
        for d in DISTRICTS
    ]