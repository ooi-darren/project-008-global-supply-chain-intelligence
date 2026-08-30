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

## Scenario Stress Test (Added After External Review)

The baseline forecast above and the shock scenarios in `docs/SCENARIO_METHODOLOGY.md` were originally kept "clearly separate" by design, a defensible modelling choice, but one that meant nobody could see what the 2030 number would actually look like under a real, historically-anchored shock. `python/forecasting/scenario_stress_test.py` closes that gap for three scenarios, using magnitudes derived from this project's own real data rather than an external or invented assumption:

| Scenario | Real magnitude used | Derivation |
|---|---|---|
| H: Global recession | -1.13% | Malaysia's actual year-over-year export growth in 2020, the real COVID year, `malaysia_trade_headline_annual.csv` |
| D: Trade-tension escalation | -0.85% | Malaysia's actual year-over-year export growth in 2019, the real US-China tariff-escalation year, same source |
| G: Energy price shock | ±5.2% | Natural Gas, Europe's 46.7% recent-3-year annualised price volatility, scaled down by Malaysia's own actual mineral-fuels export share (11.2% of total exports, 2025, `malaysia_trade_sitc_annual.csv`), not applied at full magnitude to the whole export base |

Scenarios H and D are applied as a one-time level shock to 2026, with the baseline model's own drift resumed afterward; Scenario G is applied as a sustained band across the full 2026-2030 path. Result: the 2030 baseline of RM1.87 trillion moves to roughly RM1.80 trillion under either Scenario H or D (both real historical magnitudes turned out to be relatively mild for Malaysia specifically, milder than the global COVID/tariff narratives alone might suggest), and to a RM1.77-1.97 trillion band under Scenario G. See `data/processed/malaysia_export_forecast_stress_test.csv` and Visualisation 19.

**What this stress test is not:** a structural, input-output-modelled forecast of how each shock would actually propagate through Malaysia's economy. The shock magnitudes are real; the mechanism applying them (a level shift or a percentage band) is a documented simplifying convention. See `docs/LIMITATIONS.md` item 13.

## What This Forecast Does Not Claim

This is one series, one horizon, one specific backtest window's winning model. It is not a claim that Malaysia's exports will grow at a constant linear rate through 2030 regardless of global conditions, the scenario analysis (`docs/SCENARIO_METHODOLOGY.md`) exists specifically to reason about the conditions under which this baseline trajectory could be disrupted in either direction, which a single time-series model cannot represent, and the stress test above now gives that reasoning an actual number rather than leaving it qualitative.
