# Forecasting Methodology

Full write-up for `python/forecasting/forecast_malaysia_exports.py`.

## Target Series

Malaysia's annual merchandise exports, 2001-2025 (DOSM `trade_headline`, `data/processed/malaysia_trade_headline_annual.csv`), the longest, cleanest, most directly relevant series available in this project for a genuine forecast, rather than a World Bank series carrying a 1-2 year reporting lag.

## Models Compared

| Model | Description |
|---|---|
| Naive | Last actual value carried forward, the mandatory baseline per the brief |
| Naive + drift | Last value extrapolated at the average historical growth rate |
| ETS (Holt's linear trend) | Exponential smoothing with an additive trend component |
| ARIMA | Order chosen by minimising AIC over a (p≤2, d≤1, q≤2) grid |

## Validation

**Rolling-origin backtest, not a single train/test split.** For each of the last 5 actual years, the model is trained on everything before that year and produces a 1-step-ahead forecast, compared against the real actual value. This gives 5 independent forecast errors per model rather than one, which would be one data point of luck either way. Reported: MAE, RMSE, MAPE per model, averaged across the 5 backtest origins.

## Result: Reported Honestly

The **naive-with-drift model won** the backtest (lowest RMSE), beating both ARIMA and ETS. This is reported as-is, per the brief's explicit instruction: "If a model performs poorly: report it. Do not hide poor results." A simple linear-growth extrapolation outperforming more sophisticated models is itself a real finding about this series; Malaysia's export growth over the backtest window was close enough to a steady trend that the added complexity of ARIMA/ETS did not pay off in out-of-sample accuracy, at least on this specific 5-year backtest window and this specific 1-step-ahead horizon.

## Forward Forecast

The winning model (naive + drift) is refit on the full 2001-2025 actual series and projected to 2030. A 90% prediction band is constructed from the empirical standard deviation of the series' historical 1-step changes (a simple, documented empirical band, not a formal model-based confidence interval, since the winning model is not ARIMA and a from-first-principles CI is a more defensible choice than borrowing one model's CI formula for a different winning model).

## What This Forecast Does Not Claim

This is one series, one horizon, one specific backtest window's winning model. It is not a claim that Malaysia's exports will grow at a constant linear rate through 2030 regardless of global conditions, the scenario analysis (`docs/SCENARIO_METHODOLOGY.md`) exists specifically to reason about the conditions under which this baseline trajectory could be disrupted in either direction, which a single time-series model cannot represent.
