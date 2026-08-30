# -*- coding: utf-8 -*-
"""
Builds the master World Bank country-year panel for Project 008, using the
same region framework as Project 007 (data/external/REGION_MAPPING_project007.csv,
reused deliberately for cross-project consistency in this portfolio rather than
building a second, potentially inconsistent, regional classification).
"""
import pandas as pd
import numpy as np

panel = pd.read_csv("data/raw/worldbank_panel_wide.csv")
regions = pd.read_csv("data/external/REGION_MAPPING_project007.csv")

df = panel.merge(
    regions[["ISO3", "Country", "Project_007_Region", "Official_Region", "Sub_Region"]],
    left_on="iso3", right_on="ISO3", how="inner",  # inner: keep only real countries, drop WB aggregates
)
df = df.drop(columns=["ISO3", "country_name"]).rename(columns={"iso3": "ISO3", "year": "Year"})
df = df.rename(columns={"Project_007_Region": "Region"})

df = df.sort_values(["ISO3", "Year"])

# CAGR 2016-2023 real trade growth proxy, using merchandise exports (current
# USD; nominal-USD caveat applies the same way it did in Project 007 -- flag
# explicitly rather than silently treat as real growth).
def cagr(first, last, n_years):
    if pd.isna(first) or pd.isna(last) or first <= 0 or n_years <= 0:
        return np.nan
    return ((last / first) ** (1 / n_years) - 1) * 100

cagr_rows = []
for iso3, g in df.groupby("ISO3"):
    g2 = g.set_index("Year")["merchandise_exports_current_usd"]
    years_present = g2.dropna().index
    if len(years_present) < 2:
        cagr_rows.append({"ISO3": iso3, "export_cagr_nominal_pct": np.nan, "cagr_start_year": np.nan, "cagr_end_year": np.nan})
        continue
    y0, y1 = years_present.min(), years_present.max()
    val = cagr(g2.loc[y0], g2.loc[y1], y1 - y0)
    cagr_rows.append({"ISO3": iso3, "export_cagr_nominal_pct": val, "cagr_start_year": y0, "cagr_end_year": y1})
cagr_df = pd.DataFrame(cagr_rows)
df = df.merge(cagr_df, on="ISO3", how="left")

df.to_csv("data/processed/master_supply_chain_panel.csv", index=False)
print("master_supply_chain_panel.csv:", df.shape)

# Latest-year snapshot per country (own most recent non-null LPI + trade data)
latest_rows = []
for iso3, g in df.groupby("ISO3"):
    g2 = g.dropna(subset=["logistics_performance_index_overall"])
    if len(g2):
        latest_rows.append(g2.sort_values("Year").iloc[-1])
latest = pd.DataFrame(latest_rows)
latest.to_csv("data/processed/latest_lpi_snapshot.csv", index=False)
print("latest_lpi_snapshot.csv:", latest.shape)
print("\nCountries per region:")
print(df.drop_duplicates("ISO3")["Region"].value_counts())
