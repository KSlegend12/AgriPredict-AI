# Future Forecast Safety Audit

## Current status

The existing 2027–2031 module is a scenario baseline and should not yet be called a fully validated real-world forecast model.

## Why

The inference module correctly generates scenario weather rather than pretending that 2027–2031 weather is known. It also keeps the future module separate from the validated 2024 model.

However, the model must be validated with **forecast-origin-safe hindcasts** before its reported future accuracy is treated as real-world forecast accuracy.

## Required next validation

For each historical origin year:

1. Use only yield/weather/agricultural information available by the origin.
2. Construct the weather information that would have been available at that time (forecast/scenario proxy, not the realized target-year weather).
3. Predict the next target year.
4. Compare against the observed yield.
5. Repeat across multiple origins and districts.
6. Compare against previous-year and trend baselines.

Only after this exercise should a future model be selected for production.

## No changes made to the validated model

The current 1997–2023 GradientBoosting model and its 2024 holdout remain untouched.
