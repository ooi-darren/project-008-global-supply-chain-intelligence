# -*- coding: utf-8 -*-
"""
Forecasting for Project 008: Malaysia annual exports, 2026-2030.

Target: data/processed/malaysia_trade_headline_annual.csv (DOSM, 2001-2025
actual annual exports) -- the single longest, cleanest, most directly
relevant series this project has for a genuine forecast with real
train/test validation, rather than forecasting a World Bank series with
1-2 year reporting lag baked in.

Models compared (per the brief's requirement not to pick a model just
because its forecast looks dramatic):
  - Naive (last value carried forward) -- the mandatory baseline
  - Naive with drift (extrapolate the average historical growth rate)
  - Holt's linear trend exponential smoothing (ETS, additive trend)
  - ARIMA, order chosen by minimising AIC over a small documented grid

Validation: rolling-origin backtest over the last 5 years of actual data
(train on everything up to year Y, forecast Y+1, compare to actual,
repeat for Y = 2019..2023), reporting MAE / RMSE / MAPE per model --
not a single train/test split, which would be one data point of luck.
The winning model (lowest average backtest RMSE) is then refit on the FULL
actual series (2001-2025) to produce the real forward forecast to 2030,
with a naive-residual-based prediction interval (documented as such, not
a formal ARIMA confidence interval, since the winning model may not be
ARIMA).
"""
import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import Holt
from statsmodels.tsa.arima.model import ARIMA
import warnings
import os

warnings.filterwarnings("ignore")
OUT_DIR = "data/processed"
os.makedirs(OUT_DIR, exist_ok=True)


def naive_forecast(train, h):
    return np.repeat(train.iloc[-1], h)


def naive_drift_forecast(train, h):
    n = len(train)
    drift = (train.iloc[-1] - train.iloc[0]) / (n - 1)
    return train.iloc[-1] + drift * np.arange(1, h + 1)


def ets_forecast(train, h):
    model = Holt(train.values, initialization_method="estimated").fit(optimized=True)
    return model.forecast(h)


def best_arima_forecast(train, h, return_model=False):
    best_aic, best_order, best_fit = np.inf, None, None
    for p in range(3):
        for d in range(2):
            for q in range(3):
                try:
                    fit = ARIMA(train.values, order=(p, d, q)).fit()
                    if fit.aic < best_aic:
                        best_aic, best_order, best_fit = fit.aic, (p, d, q), fit
                except Exception:
                    continue
    fc = best_fit.forecast(h)
    if return_model:
        return fc, best_order, best_fit
    return fc


def errors(actual, pred):
    actual, pred = np.asarray(actual), np.asarray(pred)
    mae = np.mean(np.abs(actual - pred))
    rmse = np.sqrt(np.mean((actual - pred) ** 2))
    mape = np.mean(np.abs((actual - pred) / actual)) * 100
    return mae, rmse, mape


def backtest():
    df = pd.read_csv(os.path.join(OUT_DIR, "malaysia_trade_headline_annual.csv"))
    s = df.set_index("year")["exports"].sort_index()

    models = {
        "naive": naive_forecast,
        "naive_drift": naive_drift_forecast,
        "ets_holt": ets_forecast,
        "arima": best_arima_forecast,
    }
    results = {m: [] for m in models}
    test_years = [y for y in s.index if y >= s.index.max() - 4][1:]  # last 5 backtest origins, 1-step-ahead each

    for origin_year in test_years:
        train = s[s.index < origin_year]
        actual = s.loc[origin_year]
        for name, fn in models.items():
            pred = fn(train, 1)[0] if not isinstance(fn(train, 1), tuple) else fn(train, 1)[0][0]
            results[name].append({"origin_year": origin_year, "actual": actual, "pred": pred})

    summary = []
    for name, rows in results.items():
        r = pd.DataFrame(rows)
        mae, rmse, mape = errors(r["actual"], r["pred"])
        summary.append({"model": name, "MAE": mae, "RMSE": rmse, "MAPE_pct": mape})
    summary_df = pd.DataFrame(summary).sort_values("RMSE")
    summary_df.to_csv(os.path.join(OUT_DIR, "malaysia_export_forecast_backtest.csv"), index=False)
    print("Backtest results (1-step-ahead, last 5 years):")
    print(summary_df.to_string(index=False))
    return s, summary_df


def forward_forecast(s, winning_model_name):
    h = 5  # 2026-2030
    years = list(range(int(s.index.max()) + 1, int(s.index.max()) + 1 + h))
    fn_map = {
        "naive": naive_forecast, "naive_drift": naive_drift_forecast,
        "ets_holt": ets_forecast, "arima": best_arima_forecast,
    }
    fn = fn_map[winning_model_name]
    if winning_model_name == "arima":
        fc, order, fit = best_arima_forecast(s, h, return_model=True)
        print(f"Winning ARIMA order: {order}")
    else:
        fc = fn(s, h)

    # naive prediction interval from historical 1-step residual std (documented
    # as a simple empirical band, not a formal model-based CI for every model)
    resid_std = s.diff().dropna().std()
    lower = fc - 1.645 * resid_std * np.sqrt(np.arange(1, h + 1))
    upper = fc + 1.645 * resid_std * np.sqrt(np.arange(1, h + 1))

    out = pd.DataFrame({
        "year": years, "forecast_exports": fc,
        "lower_90pct_band": lower, "upper_90pct_band": upper,
        "model_used": winning_model_name,
    })
    out.to_csv(os.path.join(OUT_DIR, "malaysia_export_forecast_2026_2030.csv"), index=False)
    print(f"\nForward forecast ({winning_model_name}), 2026-2030:")
    print(out.round(1).to_string(index=False))


if __name__ == "__main__":
    s, summary_df = backtest()
    winner = summary_df.iloc[0]["model"]
    print(f"\nWinning model (lowest backtest RMSE): {winner}")
    forward_forecast(s, winner)
