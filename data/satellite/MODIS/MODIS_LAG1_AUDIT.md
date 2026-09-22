# MODIS lag-1 audit

{
  "coverage_rows": 26,
  "districts": [
    "Akola",
    "Amravati",
    "Buldhana",
    "Nagpur",
    "Wardha",
    "Washim",
    "Yavatmal"
  ],
  "years": [
    2018,
    2019,
    2020,
    2021,
    2022,
    2023,
    2024
  ],
  "note": "Exploratory only; lag-1 satellite features use prior-year MODIS and are forecast-origin safe. This is not the production model and does not alter/retrain the authoritative model."
}

## Mean exploratory metrics
| model    |     MAE |    RMSE |
|:---------|--------:|--------:|
| PrevYear | 112.643 | 123.369 |
| RF       | 118.872 | 133.738 |
| Ridge    | 125.9   | 142.694 |