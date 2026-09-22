"""
Build model-ready cotton prediction inputs from the authoritative dataset.

No values are synthesized here. For supported historical years (1997-2024),
all model features are read directly from the authoritative model-ready panel.
The target column is never passed to the predictor.
"""

from pathlib import Path
from typing import Any

import pandas as pd

from backend.ml.cotton_predictor import FEATURE_COLS, VALID_DISTRICTS


DATA_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "vidarbha_cotton_model_ready_1997_2024.csv"
)
TARGET_COL = "yield_target_kg_ha"


class CottonInputBuilder:
    def __init__(self) -> None:
        if not DATA_PATH.exists():
            raise FileNotFoundError(f"Authoritative cotton dataset not found: {DATA_PATH}")

        self.df = pd.read_csv(DATA_PATH)
        self.df["year"] = self.df["year"].astype(int)

        self.df = self.df[self.df["district"].isin(VALID_DISTRICTS)].copy()
        self.df = self.df.sort_values(["district", "year"]).reset_index(drop=True)

    @property
    def available_years(self) -> list[int]:
        return sorted(self.df["year"].unique().tolist())

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
    def _clean(value: Any) -> Any:
        if pd.isna(value):
            return None
        if hasattr(value, "item"):
            return value.item()
        return value

    def build(self, district: str, year: int) -> dict[str, Any]:
        row = self._get_row(district, year)

        features: dict[str, Any] = {}
        missing_features: list[str] = []

        for col in FEATURE_COLS:
            value = self._clean(row[col])
            features[col] = value
            if value is None:
                missing_features.append(col)

        return {
            "district": district,
            "year": year,
            "features": features,
            "missing_features": missing_features,
            "source": {
                "dataset": DATA_PATH.name,
                "type": "authoritative model-ready historical panel",
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
                }
                for _, row in ddf.iterrows()
            ],
            "source": DATA_PATH.name,
        }


cotton_input_builder = CottonInputBuilder()
