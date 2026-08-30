# -*- coding: utf-8 -*-
"""
Stress-tests the Malaysia export forecast (malaysia_export_forecast_2026_2030.csv,
the naive-with-drift baseline that won the rolling-origin backtest) against
three of the discrete shock scenarios documented in docs/SCENARIO_METHODOLOGY.md,
added after external review specifically because keeping the forecast and the
shock scenarios "clearly separate" (the original design) meant nobody could see
what the 2030 number would look like under a real, historically-anchored shock.

Every shock magnitude here is derived from THIS PROJECT'S OWN DATA, not an
external assumption:

  - Scenario H (global recession): the actual year-over-year export growth
    Malaysia recorded in 2020 (the real COVID year), from
    malaysia_trade_headline_annual.csv's own export_growth_yoy_pct column.
  - Scenario D (trade-tension escalation): the actual year-over-year export
    growth Malaysia recorded in 2019 (the real US-China tariff-escalation
    year), same source.
  - Scenario G (energy/commodity price shock): the recent-3-year annualised
    volatility of the Natural Gas, Europe price series (commodity_price_
    volatility.csv), scaled down by Malaysia's own actual mineral-fuels
    export share (SITC section 3 / total exports, malaysia_trade_sitc_
    annual.csv, most recent year) -- applying the raw commodity volatility
    figure to 100% of Malaysia's export base would overstate the real
    pass-through, since fuels are roughly a ninth of Malaysia's export mix,
    not all of it. This scaling is a documented simplifying assumption, not
    a modelled input-output pass-through -- see docs/LIMITATIONS.md.

Scenarios H and D are applied as a one-time level shock to the first
forecast year (2026), with the SAME absolute year-over-year increment as
the baseline naive-with-drift model carried forward afterward (a standard
"one-off shock, trend resumes" convention). Scenario G is applied as a
symmetric band around the entire 2026-2030 baseline path, since a sustained
energy-price shock is a multi-year condition, not a single-year event.
"""
import pandas as pd
import numpy as np
import os

OUT_DIR = "data/processed"


def main():
    baseline = pd.read_csv(os.path.join(OUT_DIR, "malaysia_export_forecast_2026_2030.csv"))
    headline = pd.read_csv(os.path.join(OUT_DIR, "malaysia_trade_headline_annual.csv"))
    sitc = pd.read_csv(os.path.join(OUT_DIR, "malaysia_trade_sitc_annual.csv"))
    vol = pd.read_csv(os.path.join(OUT_DIR, "commodity_price_volatility.csv"))

    actual_2025 = headline.loc[headline["year"] == 2025, "exports"].iloc[0]
    recession_shock_pct = headline.loc[headline["year"] == 2020, "export_growth_yoy_pct"].iloc[0]
    trade_tension_shock_pct = headline.loc[headline["year"] == 2019, "export_growth_yoy_pct"].iloc[0]

    latest_sitc_year = sitc["year"].max()
    sitc_latest = sitc[sitc["year"] == latest_sitc_year]
    fuel_share = (sitc_latest.loc[sitc_latest["section"] == "3", "exports"].iloc[0] /
                  sitc_latest.loc[sitc_latest["section"] == "overall", "exports"].iloc[0])
    energy_vol_pct = vol.loc[vol["commodity"] == "Natural gas, Europe", "recent_3yr_volatility_annualised_pct"].iloc[0]
    energy_shock_pct = fuel_share * energy_vol_pct

    print(f"Real shock magnitudes derived from this project's own data:")
    print(f"  Scenario H (global recession): {recession_shock_pct:+.2f}% (Malaysia's actual 2020 export growth)")
    print(f"  Scenario D (trade-tension escalation): {trade_tension_shock_pct:+.2f}% (Malaysia's actual 2019 export growth)")
    print(f"  Scenario G (energy price shock): +/-{energy_shock_pct:.2f}% "
          f"({energy_vol_pct:.1f}% Natural Gas Europe 3yr volatility x {fuel_share:.1%} fuel export share)")

    years = baseline["year"].tolist()
    baseline_vals = baseline["forecast_exports"].to_numpy()
    drift_increment = baseline_vals[1] - baseline_vals[0]  # constant, naive+drift is linear

    def one_time_shock_path(shock_pct):
        year1 = actual_2025 * (1 + shock_pct / 100)
        return year1 + drift_increment * np.arange(0, len(years))

    recession_path = one_time_shock_path(recession_shock_pct)
    trade_tension_path = one_time_shock_path(trade_tension_shock_pct)
    energy_upper_path = baseline_vals * (1 + energy_shock_pct / 100)
    energy_lower_path = baseline_vals * (1 - energy_shock_pct / 100)

    out = pd.DataFrame({
        "year": years,
        "baseline_naive_drift": baseline_vals,
        "scenario_H_recession": recession_path,
        "scenario_D_trade_tension": trade_tension_path,
        "scenario_G_energy_shock_upper": energy_upper_path,
        "scenario_G_energy_shock_lower": energy_lower_path,
    })
    out.to_csv(os.path.join(OUT_DIR, "malaysia_export_forecast_stress_test.csv"), index=False)

    b2030 = baseline_vals[-1]
    print(f"\n2030 baseline forecast: RM {b2030/1e12:.2f}T")
    print(f"2030 under Scenario H (recession):        RM {recession_path[-1]/1e12:.2f}T "
          f"({(recession_path[-1]/b2030-1)*100:+.1f}% vs baseline)")
    print(f"2030 under Scenario D (trade tension):     RM {trade_tension_path[-1]/1e12:.2f}T "
          f"({(trade_tension_path[-1]/b2030-1)*100:+.1f}% vs baseline)")
    print(f"2030 under Scenario G (energy shock band): RM {energy_lower_path[-1]/1e12:.2f}T to "
          f"RM {energy_upper_path[-1]/1e12:.2f}T ({-energy_shock_pct:+.1f}% / {energy_shock_pct:+.1f}% vs baseline)")
    print(f"\nSaved malaysia_export_forecast_stress_test.csv: {out.shape}")


if __name__ == "__main__":
    main()
