# -*- coding: utf-8 -*-
"""
Supply Chain Risk / Early-Warning composite index for Project 008.

Per the brief: "Do NOT use arbitrary weights. Document variables,
transformations, normalisation, weights, scoring, sensitivity analysis."
Follows the exact same transparent-index discipline established in this
portfolio's Project 007 (equal-weighted, min-max normalised pillars, a
documented sensitivity check, retained sub-scores so a reader can recompute
with their own weights) -- see MARKET_ATTRACTIVENESS_METHODOLOGY.md there
for the precedent this follows.

FOUR PILLARS (country-level, i.e. "how exposed is this country's supply
chain", not a single global score):

  1. Import Dependency: merchandise imports as a % of GDP (World Bank) --
     a country that imports a larger share of its economy has, mechanically,
     more of its economic activity exposed to external supply disruption.

  2. Logistics Fragility: (100 - Logistics Performance Index overall score
     rescaled to 0-100) -- LOW LPI = HIGH fragility, so this is inverted
     before combining with the other (higher-is-riskier) pillars.

  3. Trade Partner Concentration: HHI of each country's export-market
     concentration within the 59-country network (computed from the same
     Comtrade bilateral data used for the network analysis) -- a country
     selling to a small number of markets is more exposed to any one
     market's demand shock or policy action.

  4. Commodity Price Exposure: for each country, the network-weighted
     recent-3-year volatility of the commodity price series most relevant
     to its actual export mix is NOT attempted here (would need a full
     export-composition-by-commodity dataset this project does not have at
     country-product granularity for all 59 countries) -- instead this
     pillar uses the GLOBAL average recent-3-year commodity price volatility
     (data/processed/commodity_price_volatility.csv) as a single shared
     input applied uniformly, explicitly flagged as the crudest of the four
     pillars and named as a limitation, not disguised as country-specific.

Each pillar min-max normalised 0-100 within the sample of countries with a
valid value; composite = unweighted mean of available pillars (country
scored on remaining pillars if one is missing, na_pillars recorded).
Sensitivity check: alternative version double-weighting Trade Partner
Concentration (the pillar most directly tied to "dependency" in the
project's own core research question), Spearman rank correlation reported.
"""
import pandas as pd
import numpy as np
from scipy.stats import spearmanr
import os

OUT_DIR = "data/processed"


def minmax(s):
    rng = s.max() - s.min()
    if rng == 0 or pd.isna(rng):
        # A constant column can't be min-max differentiated (would divide by
        # zero -> NaN for every row, silently breaking the whole pillar, as
        # happened here on the first run with the deliberately-uniform
        # commodity-exposure pillar). A uniform input contributes the same
        # fixed midpoint to every country's score, which is the honest
        # representation of "this pillar doesn't differentiate anyone."
        return pd.Series(50.0, index=s.index)
    return (s - s.min()) / rng * 100


def build_export_concentration():
    """HHI of each reporter's export destinations within the 59-country
    network, most-recent period (2023)."""
    df = pd.read_csv("data/raw/comtrade_bilateral_trade_raw.csv")
    sub = df[(df["period"].astype(str) == "2023") & (df["flow"] == "X")]
    rows = []
    for reporter, g in sub.groupby("reporterCode"):
        total = g["primaryValue"].sum()
        if total <= 0:
            continue
        shares = g["primaryValue"] / total
        hhi = (shares * 100) ** 2
        rows.append({"comtradeReporterCode": reporter, "export_partner_HHI": hhi.sum()})
    return pd.DataFrame(rows)


def main():
    countries = pd.read_csv("data/external/network_countries.csv")
    panel = pd.read_csv("data/processed/master_supply_chain_panel.csv")
    latest = panel.sort_values("Year").groupby("ISO3").tail(1)  # each country's own most recent year (trade/GDP)
    # LPI specifically needs its OWN latest-with-real-value snapshot, not the
    # naive latest-row-per-country above -- LPI is periodic (not annual), so
    # the naive join returns null LPI for every single country (this exact
    # bug already surfaced once in malaysia_deep_dive.py; recurred here
    # because this is a separate script building its own "latest" table).
    lpi_latest = pd.read_csv("data/processed/latest_lpi_snapshot.csv")

    df = countries[["ISO3", "Country", "Project_007_Region", "comtradeReporterCode"]].rename(
        columns={"Project_007_Region": "Region"})
    df = df.merge(latest[["ISO3", "merchandise_imports_current_usd", "gdp_current_usd"]], on="ISO3", how="left")
    df = df.merge(lpi_latest[["ISO3", "logistics_performance_index_overall"]], on="ISO3", how="left")
    df["import_dependency_pct_gdp"] = df["merchandise_imports_current_usd"] / df["gdp_current_usd"] * 100

    conc = build_export_concentration()
    df = df.merge(conc, on="comtradeReporterCode", how="left")

    vol = pd.read_csv(os.path.join(OUT_DIR, "commodity_price_volatility.csv"))
    global_avg_vol = vol["recent_3yr_volatility_annualised_pct"].mean()
    df["commodity_price_exposure"] = global_avg_vol  # uniform, documented limitation -- see module docstring

    # Pillars (all oriented so HIGHER = MORE RISK before normalising)
    df["score_import_dependency"] = minmax(df["import_dependency_pct_gdp"])
    df["score_logistics_fragility"] = minmax(100 - df["logistics_performance_index_overall"] * 20)  # LPI is 1-5 scale -> invert to 0-100 fragility
    df["score_trade_concentration"] = minmax(df["export_partner_HHI"])
    df["score_commodity_exposure"] = minmax(df["commodity_price_exposure"])

    score_cols = ["score_import_dependency", "score_logistics_fragility",
                  "score_trade_concentration", "score_commodity_exposure"]
    df["n_pillars_available"] = df[score_cols].notna().sum(axis=1)
    df["supply_chain_risk_score"] = df[score_cols].mean(axis=1, skipna=True)
    df.loc[df["n_pillars_available"] == 0, "supply_chain_risk_score"] = np.nan

    # Sensitivity: double-weight trade concentration
    def alt_weighted(row):
        if row[score_cols].isna().any():
            return np.nan
        vals = [row["score_import_dependency"], row["score_logistics_fragility"],
                row["score_trade_concentration"], row["score_commodity_exposure"]]
        weights = [1, 1, 2, 1]
        return np.average(vals, weights=weights)
    df["score_alt_concentration_weighted"] = df.apply(alt_weighted, axis=1)

    result = df.dropna(subset=["supply_chain_risk_score"]).sort_values(
        "supply_chain_risk_score", ascending=False).reset_index(drop=True)
    result["rank"] = result.index + 1

    comparable = result.dropna(subset=["score_alt_concentration_weighted"])
    rho, p = spearmanr(comparable["supply_chain_risk_score"], comparable["score_alt_concentration_weighted"])
    print(f"Sensitivity check (equal weights vs 2x concentration weight, n={len(comparable)}): Spearman rho = {rho:.3f}")

    out_cols = ["rank", "Country", "ISO3", "Region", "supply_chain_risk_score",
                "n_pillars_available"] + score_cols
    result[out_cols].to_csv(os.path.join(OUT_DIR, "supply_chain_risk_index.csv"), index=False)
    print(f"\nSaved supply_chain_risk_index.csv: {result.shape}")
    print("\nHighest supply-chain risk (top 15):")
    print(result[["rank", "Country", "Region", "supply_chain_risk_score"]].head(15).to_string(index=False))
    print("\nLowest supply-chain risk (bottom 10):")
    print(result[["rank", "Country", "Region", "supply_chain_risk_score"]].tail(10).to_string(index=False))


if __name__ == "__main__":
    main()
