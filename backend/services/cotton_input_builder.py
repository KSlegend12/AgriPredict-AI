"""
Build model-ready cotton prediction inputs from the authoritative dataset.

No values are synthesized here. For supported historical years (1997-2024),
all model features are read directly from the authoritative model-ready panel.
For satellite candidate model requests, verified NASA SMAP L4 soil moisture
features are loaded strictly from the verified satellite panel for supported years (2018-2024).
The target column is never passed to the predictor.
"""

from pathlib import Path
from typing import Any, Optional

import pandas as pd

from backend.config import CANONICAL_COTTON_DATASET_PATH
from backend.ml.cotton_predictor import (
    FEATURE_COLS,
    VALID_DISTRICTS,
    SATELLITE_SMAP_FEATURES,
    SATELLITE_FEATURE_COLS,
    DELTA_ROLLING_FEATURE_COLS,
    PHYSIOLOGICAL_FEATURE_COLS,
    PHYSIOLOGICAL_ENGINEERED_FEATURES,
    THERMAL_FEATURE_COLS,
    DECOUPLED_AGRONOMIC_FEATURE_COLS,
    DECOUPLED_AGRONOMIC_ENGINEERED_FEATURES,
    DECOUPLED_DEFICIT_HEAT_FEATURE_COLS,
    DECOUPLED_DEFICIT_HEAT_ENGINEERED_FEATURES,
    REGULARIZED_ENSEMBLE_FEATURE_COLS,
    AGRONOMIC_ENGINEERED_FEATURES,
    ENSEMBLE_SMAP_FEATURES,
)


DATA_PATH = CANONICAL_COTTON_DATASET_PATH
TARGET_COL = "yield_target_kg_ha"

_HERE = Path(__file__).resolve().parent
_ML_ROOT = _HERE.parent / "ml"
SATELLITE_DATA_PATH = _ML_ROOT / "experiments" / "satellite_soil_moisture_expansion" / "data" / "vidarbha_cotton_augmented_smap_modis_2017_2024.csv"


class CottonInputBuilder:
    def __init__(self) -> None:
        if not DATA_PATH.exists():
            raise FileNotFoundError(f"Authoritative cotton dataset not found: {DATA_PATH}")

        self.df = pd.read_csv(DATA_PATH)
        self.df["year"] = self.df["year"].astype(int)

        self.df = self.df[self.df["district"].isin(VALID_DISTRICTS)].copy()
        self.df = self.df.sort_values(["district", "year"]).reset_index(drop=True)

        # Load satellite-augmented dataset if present
        if SATELLITE_DATA_PATH.exists():
            self.sat_df = pd.read_csv(SATELLITE_DATA_PATH)
            self.sat_df["year"] = self.sat_df["year"].astype(int)
            self.sat_df = self.sat_df[self.sat_df["district"].isin(VALID_DISTRICTS)].copy()
            self.sat_df = self.sat_df.sort_values(["district", "year"]).reset_index(drop=True)
        else:
            self.sat_df = None

    @property
    def available_years(self) -> list[int]:
        return sorted(self.df["year"].unique().tolist())

    @property
    def available_satellite_years(self) -> list[int]:
        if self.sat_df is not None:
            # Requires both in-season and lag-1 SMAP coverage
            return [yr for yr in range(2018, 2025)]
        return []

    def _get_row(self, district: str, year: int) -> pd.Series:
        if district not in VALID_DISTRICTS:
            raise ValueError(f"District '{district}' is not a supported Vidarbha district.")

        row = self.df[(self.df["district"] == district) & (self.df["year"] == year)]
        if row.empty:
            raise ValueError(
                f"No verified model-ready data is available for {district}, {year}. "
                f"Supported years: {self.available_years[0]}–{self.available_years[-1]}."
            )
        return row.iloc[0]

    @staticmethod
    def _compute_agronomic_features(row: pd.Series) -> dict[str, float]:
        tmax_k = float(row.get("tmax_kharif_mean_c", 32.0))
        tmin_k = float(row.get("tmin_kharif_mean_c", 23.0))
        rain_k = float(row.get("rainfall_kharif_mm", 800.0))
        rainy_k = float(row.get("rainy_days_kharif", 60.0))
        dry_k = float(row.get("max_dry_spell_kharif_days", 10.0))
        hot_k = float(row.get("tmax_hot_days_ge35_kharif", 15.0))
        max1_k = float(row.get("rainfall_max_1day_kharif_mm", 50.0))
        prev_y1 = float(row.get("previous_year_yield_kg_ha", 300.0))
        prev_y2 = float(row.get("previous_2year_yield_kg_ha", 300.0))
        roll_3 = float(row.get("rolling_3yr_yield_mean_kg_ha", 300.0))

        return {
            "diurnal_range_kharif": tmax_k - tmin_k,
            "rain_intensity_kharif": rain_k / max(rainy_k, 1.0),
            "dry_heat_compound": dry_k * hot_k,
            "single_day_deluge_ratio": max1_k / max(rain_k, 1.0),
            "yield_momentum": prev_y1 - prev_y2,
            "yield_ratio_to_rolling3": prev_y1 / max(roll_3, 1.0),
        }

    @staticmethod
    def _compute_physiological_features(row: pd.Series) -> dict[str, float]:
        tmax_k = float(row.get("tmax_kharif_mean_c", 32.0))
        tmin_k = float(row.get("tmin_kharif_mean_c", 23.0))
        rain_k = float(row.get("rainfall_kharif_mm", 800.0))
        rainy_k = float(row.get("rainy_days_kharif", 60.0))
        heavy_k = float(row.get("heavy_rain_days_kharif", 1.0))
        dry_k = float(row.get("max_dry_spell_kharif_days", 10.0))
        hot_k = float(row.get("tmax_hot_days_ge35_kharif", 15.0))
        max1_k = float(row.get("rainfall_max_1day_kharif_mm", 50.0))
        prev_y1 = float(row.get("previous_year_yield_kg_ha", 300.0))
        prev_y2 = float(row.get("previous_2year_yield_kg_ha", 300.0))
        roll_3 = float(row.get("rolling_3yr_yield_mean_kg_ha", 300.0))

        return {
            "rain_gentleness_ratio": rainy_k / max(rain_k / 100.0, 0.1),
            "heavy_rain_fraction": heavy_k / max(rainy_k, 1.0),
            "extreme_heat_ratio": hot_k / 120.0,
            "diurnal_range_kharif": tmax_k - tmin_k,
            "single_day_deluge_ratio": max1_k / max(rain_k, 1.0),
            "drought_buffer_index": rain_k / max(dry_k, 1.0),
            "yield_momentum": prev_y1 - prev_y2,
            "yield_excess_over_rolling3": prev_y1 - roll_3,
            "yield_ratio_to_rolling3": prev_y1 / max(roll_3, 1.0),
        }

    @staticmethod
    def _compute_decoupled_agronomic_features(row: pd.Series) -> dict[str, float]:
        tmax_k = float(row.get("tmax_kharif_mean_c", 32.0))
        tmin_k = float(row.get("tmin_kharif_mean_c", 23.0))
        rain_k = float(row.get("rainfall_kharif_mm", 800.0))
        rainy_k = float(row.get("rainy_days_kharif", 60.0))
        dry_k = float(row.get("max_dry_spell_kharif_days", 10.0))
        hot_k = float(row.get("tmax_hot_days_ge35_kharif", 15.0))

        return {
            "extreme_heat_ratio": hot_k / 120.0,
            "diurnal_range_kharif": tmax_k - tmin_k,
            "excess_rain_kharif": max(0.0, rain_k - 800.0) / 100.0,
            "continuous_wetness_risk": (rainy_k / 120.0) / (dry_k + 1.0),
        }

    @staticmethod
    def _compute_decoupled_deficit_heat_features(row: pd.Series) -> dict[str, float]:
        tmax_k = float(row.get("tmax_kharif_mean_c", 32.0))
        tmin_k = float(row.get("tmin_kharif_mean_c", 23.0))
        rain_k = float(row.get("rainfall_kharif_mm", 800.0))
        rainy_k = float(row.get("rainy_days_kharif", 60.0))
        dry_k = float(row.get("max_dry_spell_kharif_days", 10.0))
        hot_k = float(row.get("tmax_hot_days_ge35_kharif", 15.0))

        return {
            "extreme_heat_ratio": hot_k / 120.0,
            "diurnal_range_kharif": tmax_k - tmin_k,
            "excess_rain_kharif": max(0.0, rain_k - 800.0) / 100.0,
            "continuous_wetness_risk": (rainy_k / 120.0) / (dry_k + 1.0),
            "rain_deficit_kharif": max(0.0, 750.0 - rain_k) / 100.0,
            "hot_days_thresh10": max(0.0, hot_k - 10.0) / 10.0,
        }

    @staticmethod
    def _clean(value: Any) -> Any:
        if pd.isna(value):
            return None
        if hasattr(value, "item"):
            return value.item()
        return value

    def build(self, district: str, year: int, model_version: str = "production") -> dict[str, Any]:
        norm_version = str(model_version or "production").lower().strip()
        is_delta_model = norm_version in [
            "candidate_delta_rolling",
            "delta_rolling",
            "delta",
            "candidate_ridge_delta",
            "candidate_repaired_synth",
            "repaired_synth",
            "candidate_repaired",
            "repaired",
            "repaired_biophysical_synth",
        ]
        is_regularized_ensemble = norm_version in [
            "candidate_regularized_ensemble",
            "regularized_ensemble",
            "ensemble_ridge_et",
            "hybrid_ensemble",
        ]
        is_satellite_model = norm_version in [
            "candidate_satellite_smap",
            "satellite_smap",
            "smap",
            "candidate_satellite",
        ]
        is_phys_ridge = norm_version in [
            "candidate_physiological_ridge_a100",
            "physiological_ridge_a100",
            "candidate_physiological_ridge",
            "physiological_ridge",
            "phys_ridge_a100",
            "phys_ridge",
        ]
        is_six_dist_phys = norm_version in [
            "candidate_six_district_physiological",
            "six_district_physiological",
            "six_district_ridge",
            "candidate_six_district",
            "six_district",
            "six_dist_physiological",
        ]
        is_six_dist_thermal = norm_version in [
            "candidate_six_district_thermal",
            "six_district_thermal",
            "six_district_thermal_ridge",
            "candidate_thermal_ridge",
            "thermal_ridge",
            "six_dist_thermal",
        ]
        is_six_dist_decoupled = norm_version in [
            "candidate_six_district_decoupled_agronomic",
            "six_district_decoupled_agronomic",
            "candidate_decoupled_agronomic",
            "decoupled_agronomic",
            "decoupled_ridge",
        ]
        is_six_dist_deficit_heat = norm_version in [
            "candidate_six_district_dar_deficit_heat_thresh",
            "six_district_dar_deficit_heat_thresh",
            "candidate_dar_deficit_heat_thresh",
            "dar_deficit_heat_thresh",
            "candidate_six_district_decoupled_deficit_heatthresh_a75",
            "decoupled_deficit_heatthresh",
        ]

        if is_regularized_ensemble:
            if year < 2018 or year > 2024:
                raise ValueError(
                    f"Multi-sensor hybrid ensemble 'candidate_regularized_ensemble' is only supported for years 2018–2024 with verified NASA SMAP soil moisture coverage. "
                    f"Requested year {year} is prior to verified satellite data availability."
                )
            if self.sat_df is None:
                raise ValueError("Verified satellite-augmented panel is not available.")
            if district not in VALID_DISTRICTS:
                raise ValueError(f"District '{district}' is not a supported Vidarbha district.")

            sat_row_df = self.sat_df[(self.sat_df["district"] == district) & (self.sat_df["year"] == year)]
            if sat_row_df.empty:
                raise ValueError(f"No satellite-augmented data available for {district}, {year}.")

            row = sat_row_df.iloc[0]
            feature_cols_to_use = REGULARIZED_ENSEMBLE_FEATURE_COLS
            source_type = "authoritative panel augmented with verified NASA SMAP soil moisture & agronomic ratios"
            source_name = SATELLITE_DATA_PATH.name
            satellite_used = True

        elif is_satellite_model:
            if year < 2018 or year > 2024:
                raise ValueError(
                    f"Satellite candidate model 'candidate_satellite_smap' is only supported for years 2018–2024 with verified NASA SMAP soil moisture coverage. "
                    f"Requested year {year} is prior to verified satellite data availability."
                )
            if self.sat_df is None:
                raise ValueError("Verified satellite-augmented panel is not available.")
            if district not in VALID_DISTRICTS:
                raise ValueError(f"District '{district}' is not a supported Vidarbha district.")

            sat_row_df = self.sat_df[(self.sat_df["district"] == district) & (self.sat_df["year"] == year)]
            if sat_row_df.empty:
                raise ValueError(f"No satellite-augmented data available for {district}, {year}.")

            row = sat_row_df.iloc[0]
            feature_cols_to_use = SATELLITE_FEATURE_COLS
            source_type = "authoritative panel augmented with verified NASA SMAP L4 soil moisture"
            source_name = SATELLITE_DATA_PATH.name
            satellite_used = True

        elif is_six_dist_thermal:
            if district.strip().capitalize() == "Yavatmal":
                raise ValueError(
                    "The candidate model 'candidate_six_district_thermal' excludes Yavatmal district by design. "
                    "Supported districts: Akola, Amravati, Buldhana, Nagpur, Wardha, Washim."
                )
            if district not in ["Akola", "Amravati", "Buldhana", "Nagpur", "Wardha", "Washim"]:
                raise ValueError(f"District '{district}' is not a supported six-district candidate district.")
            row = self._get_row(district, year)
            feature_cols_to_use = THERMAL_FEATURE_COLS
            source_type = "six-district model-ready panel with 2 thermal biophysical features (Yavatmal excluded)"
            source_name = "vidarbha_cotton_six_districts_1997_2024.csv"
            satellite_used = False

        elif is_six_dist_decoupled:
            if district.strip().capitalize() == "Yavatmal":
                raise ValueError(
                    "The candidate model 'candidate_six_district_decoupled_agronomic' excludes Yavatmal district by design. "
                    "Supported districts: Akola, Amravati, Buldhana, Nagpur, Wardha, Washim."
                )
            if district not in ["Akola", "Amravati", "Buldhana", "Nagpur", "Wardha", "Washim"]:
                raise ValueError(f"District '{district}' is not a supported six-district candidate district.")
            row = self._get_row(district, year)
            feature_cols_to_use = DECOUPLED_AGRONOMIC_FEATURE_COLS
            source_type = "six-district model-ready panel with decoupled anchor, thermal & wetness features (Yavatmal excluded)"
            source_name = "vidarbha_cotton_six_districts_1997_2024.csv"
            satellite_used = False

        elif is_six_dist_deficit_heat:
            if district.strip().capitalize() == "Yavatmal":
                raise ValueError(
                    "The candidate model 'candidate_six_district_dar_deficit_heat_thresh' excludes Yavatmal district by design. "
                    "Supported districts: Akola, Amravati, Buldhana, Nagpur, Wardha, Washim."
                )
            if district not in ["Akola", "Amravati", "Buldhana", "Nagpur", "Wardha", "Washim"]:
                raise ValueError(f"District '{district}' is not a supported six-district candidate district.")
            row = self._get_row(district, year)
            feature_cols_to_use = DECOUPLED_DEFICIT_HEAT_FEATURE_COLS
            source_type = "six-district model-ready panel with decoupled anchor, drought deficit & heat threshold features (Yavatmal excluded)"
            source_name = "vidarbha_cotton_six_districts_1997_2024.csv"
            satellite_used = False

        elif is_six_dist_phys:
            if district.strip().capitalize() == "Yavatmal":
                raise ValueError(
                    "The candidate model 'candidate_six_district_physiological' excludes Yavatmal district by design. "
                    "Supported districts: Akola, Amravati, Buldhana, Nagpur, Wardha, Washim."
                )
            if district not in ["Akola", "Amravati", "Buldhana", "Nagpur", "Wardha", "Washim"]:
                raise ValueError(f"District '{district}' is not a supported six-district candidate district.")
            row = self._get_row(district, year)
            feature_cols_to_use = PHYSIOLOGICAL_FEATURE_COLS
            source_type = "six-district model-ready panel with 9 physiological biophysical interaction features (Yavatmal excluded)"
            source_name = "vidarbha_cotton_six_districts_1997_2024.csv"
            satellite_used = False

        elif is_phys_ridge:
            row = self._get_row(district, year)
            feature_cols_to_use = PHYSIOLOGICAL_FEATURE_COLS
            source_type = "authoritative model-ready panel with 9 physiological biophysical interaction features"
            source_name = DATA_PATH.name
            satellite_used = False

        elif is_delta_model:
            row = self._get_row(district, year)
            feature_cols_to_use = DELTA_ROLLING_FEATURE_COLS
            source_type = "authoritative model-ready panel with agronomic biophysical ratios"
            source_name = DATA_PATH.name
            satellite_used = False

        else:
            row = self._get_row(district, year)
            feature_cols_to_use = FEATURE_COLS
            source_type = "authoritative model-ready historical panel"
            source_name = DATA_PATH.name
            satellite_used = False

        features: dict[str, Any] = {}
        missing_features: list[str] = []

        # If model requires agronomic or physiological features, compute them from row
        agri_features = {}
        if is_six_dist_deficit_heat:
            agri_features = self._compute_decoupled_deficit_heat_features(row)
        elif is_six_dist_decoupled:
            agri_features = self._compute_decoupled_agronomic_features(row)
        elif is_phys_ridge or is_six_dist_phys or is_six_dist_thermal:
            agri_features = self._compute_physiological_features(row)
        elif is_delta_model or is_regularized_ensemble:
            agri_features = self._compute_agronomic_features(row)

        for col in feature_cols_to_use:
            if col in agri_features:
                val = agri_features[col]
            else:
                val = self._clean(row[col])
            features[col] = val
            if val is None:
                missing_features.append(col)

        # For decoupled model, ensure rolling_3yr_yield_mean_kg_ha anchor is provided for delta calculation
        if is_six_dist_decoupled or is_six_dist_deficit_heat:
            features["rolling_3yr_yield_mean_kg_ha"] = self._clean(row.get("rolling_3yr_yield_mean_kg_ha"))

        # For satellite model, strictly reject if any required SMAP feature is missing (no silent fallback or fabrication)
        if is_satellite_model:
            missing_smap = [col for col in SATELLITE_SMAP_FEATURES if features.get(col) is None]
            if missing_smap:
                raise ValueError(
                    f"Verified satellite features missing for {district}, {year}: {missing_smap}. "
                    "Synthetic or fabricated fallback is disallowed for satellite candidate."
                )

        if is_regularized_ensemble:
            missing_smap = [col for col in ENSEMBLE_SMAP_FEATURES if features.get(col) is None]
            if missing_smap:
                raise ValueError(
                    f"Verified satellite soil moisture features missing for {district}, {year}: {missing_smap}. "
                    "Synthetic or fabricated fallback is disallowed for hybrid ensemble candidate."
                )

        return {
            "district": district,
            "year": year,
            "features": features,
            "missing_features": missing_features,
            "source": {
                "dataset": source_name,
                "type": source_type,
                "satellite_used": satellite_used,
                "target_excluded": True,
            },
        }

    def weather_summary(self, district: str, year: int) -> dict[str, Any]:
        row = self._get_row(district, year)

        fields = [
            "tmax_annual_mean_c", "tmax_monsoon_mean_c", "tmax_kharif_mean_c",
            "tmax_max_c", "tmax_hot_days_ge35_kharif",
            "tmin_annual_mean_c", "tmin_monsoon_mean_c", "tmin_kharif_mean_c", "tmin_min_c",
            "rainfall_annual_mm", "rainy_days_annual", "heavy_rain_days_annual",
            "rainfall_max_1day_annual_mm", "max_5day_rain_annual_mm", "max_dry_spell_annual_days",
            "rainfall_monsoon_mm", "rainy_days_monsoon", "heavy_rain_days_monsoon",
            "rainfall_kharif_mm", "rainy_days_kharif", "heavy_rain_days_kharif",
            "max_dry_spell_monsoon_days", "max_dry_spell_kharif_days",
        ]

        return {
            "district": district,
            "year": year,
            "weather": {field: self._clean(row[field]) for field in fields},
            "area": self._clean(row["cotton_area_000ha"]),
            "source": DATA_PATH.name,
        }

    def history(self, district: str) -> dict[str, Any]:
        if district not in VALID_DISTRICTS:
            raise ValueError(f"District '{district}' is not a supported Vidarbha district.")

        ddf = self.df[self.df["district"] == district].sort_values("year")
        return {
            "district": district,
            "year_range": [int(ddf["year"].min()), int(ddf["year"].max())],
            "records": [
                {
                    "year": int(row["year"]),
                    "yield_kg_ha": self._clean(row[TARGET_COL]),
                    "rainfall_annual_mm": self._clean(row.get("rainfall_annual_mm")),
                    "tmax_kharif_mean_c": self._clean(row.get("tmax_kharif_mean_c")),
                }
                for _, row in ddf.iterrows()
            ],
            "source": DATA_PATH.name,
        }


cotton_input_builder = CottonInputBuilder()
