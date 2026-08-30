# -*- coding: utf-8 -*-
"""
World Bank Commodity Price Data (the "Pink Sheet") cleaning for Project 008.

Source: World Bank Commodity Markets, monthly nominal USD prices for 70+
commodities back to 1960 (data/raw/wb_commodity_prices_monthly.xlsx, sheet
"Monthly Prices"). Real, PUBLIC, current through the latest published month.

Used for: price volatility (financial-risk dimension of the early-warning
index), historical distributions for the Monte Carlo scenario work, and as
forecast targets. Kept as NOMINAL USD -- these are commodity spot prices,
not a cross-country income comparison, so the real/PPP discipline that
applies to GDP-type series in this portfolio doesn't apply the same way
here; inflation context is noted in docs/METHODOLOGY.md instead of deflating
the series itself, since deflating would obscure the actual shock magnitude
(e.g. the 2022 gas/fertiliser price spike) that this project needs to see.
"""
import pandas as pd
import numpy as np
import os

RAW = "data/raw/wb_commodity_prices_monthly.xlsx"
OUT_DIR = "data/processed"
os.makedirs(OUT_DIR, exist_ok=True)

# Commodities prioritised for the supply-chain risk/scenario work: energy
# (shipping fuel cost + a macro shock driver), industrial metals (mirror the
# USGS critical-materials list where a price series exists), and two
# agriculture/fertiliser series (the brief explicitly calls out food/
# fertiliser shocks as a 2022-2024 supply-chain event to analyse).
PRIORITY_COMMODITIES = [
    "Crude oil, average", "Natural gas, Europe", "Coal, Australian",
    "Copper", "Aluminum", "Nickel", "Tin", "Lead", "Zinc",
    "Iron ore, cfr spot", "Urea (fertilizer)", "DAP (fertilizer)",
    "Wheat, US HRW", "Rice, Thai 5%", "Maize", "Soybeans",
]


def main():
    df = pd.read_excel(RAW, sheet_name="Monthly Prices", header=4)
    df = df.rename(columns={"Unnamed: 0": "period"})
    df = df.dropna(subset=["period"])
    df["period"] = df["period"].astype(str).str.strip()
    df = df[df["period"].str.match(r"^\d{4}M\d{2}$")]
    df["year"] = df["period"].str[:4].astype(int)
    df["month"] = df["period"].str[5:7].astype(int)
    df["date"] = pd.to_datetime(df["year"].astype(str) + "-" + df["month"].astype(str) + "-01")

    df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]
    available = [c for c in PRIORITY_COMMODITIES if c in df.columns]
    missing = [c for c in PRIORITY_COMMODITIES if c not in df.columns]
    if missing:
        print("Not found in sheet (check exact column names):", missing)

    long_rows = []
    for col in available:
        s = pd.to_numeric(df[col], errors="coerce")
        long_rows.append(pd.DataFrame({"date": df["date"], "commodity": col, "price_usd_nominal": s}))
    long_df = pd.concat(long_rows, ignore_index=True).dropna(subset=["price_usd_nominal"])
    long_df.to_csv(os.path.join(OUT_DIR, "commodity_prices_monthly.csv"), index=False)
    print("commodity_prices_monthly.csv:", long_df.shape)

    # Volatility & recent trend summary per commodity: annualised volatility
    # of monthly log returns (full history) vs. the most recent 3 years, so
    # a reader can see whether volatility itself has structurally shifted.
    summary = []
    for commodity, g in long_df.groupby("commodity"):
        g = g.sort_values("date")
        g["log_ret"] = np.log(g["price_usd_nominal"]).diff()
        recent = g[g["date"] >= g["date"].max() - pd.DateOffset(years=3)]
        latest = g.iloc[-1]
        five_yr_ago = g[g["date"] <= g["date"].max() - pd.DateOffset(years=5)]
        base_price = five_yr_ago.iloc[-1]["price_usd_nominal"] if len(five_yr_ago) else np.nan
        summary.append({
            "commodity": commodity,
            "latest_date": latest["date"].strftime("%Y-%m"),
            "latest_price": latest["price_usd_nominal"],
            "full_history_volatility_annualised_pct": g["log_ret"].std() * np.sqrt(12) * 100,
            "recent_3yr_volatility_annualised_pct": recent["log_ret"].std() * np.sqrt(12) * 100,
            "pct_change_5yr": ((latest["price_usd_nominal"] / base_price) - 1) * 100 if pd.notna(base_price) else np.nan,
        })
    summary_df = pd.DataFrame(summary).sort_values("recent_3yr_volatility_annualised_pct", ascending=False)
    summary_df.to_csv(os.path.join(OUT_DIR, "commodity_price_volatility.csv"), index=False)
    print("\nVolatility ranking (most volatile, last 3 years, first):")
    print(summary_df.round(1).to_string(index=False))


if __name__ == "__main__":
    main()
