# -*- coding: utf-8 -*-
"""
World Bank data collection for Project 008 -- Global Supply Chain Intelligence.

Same pattern as Project 007's world_bank.py (api.worldbank.org/v2, no auth,
CC-BY 4.0): pull one CSV per indicator across all 217 real economies
(region.value != 'Aggregates', filtered downstream via REGION_MAPPING).

Usage: python python/data_collection/world_bank.py
"""
import requests
import pandas as pd
import time
import os

INDICATORS = {
    # Trade structure & openness
    "NE.TRD.GNFS.ZS": "trade_pct_of_gdp",
    "TX.VAL.MRCH.CD.WT": "merchandise_exports_current_usd",
    "TM.VAL.MRCH.CD.WT": "merchandise_imports_current_usd",
    "TX.VAL.MRCH.XD.WD": "merchandise_export_price_index",
    "TX.VAL.TECH.MF.ZS": "high_tech_exports_pct_of_manuf_exports",
    # Logistics & infrastructure
    "LP.LPI.OVRL.XQ": "logistics_performance_index_overall",
    "LP.LPI.CUST.XQ": "logistics_performance_index_customs",
    "LP.LPI.INFR.XQ": "logistics_performance_index_infrastructure",
    "LP.LPI.TIME.XQ": "logistics_performance_index_timeliness",
    "IS.SHP.GOOD.TU": "container_port_traffic_teu",
    "IS.AIR.GOOD.MT.K1": "air_freight_million_ton_km",
    "IS.RRS.GOOD.MT.K6": "rail_freight_million_ton_km",
    # Macro context (needed for real/PPP comparisons, reused convention from Project 007)
    "NY.GDP.MKTP.CD": "gdp_current_usd",
    "NY.GDP.MKTP.KD.ZG": "gdp_growth_annual_pct",
    "NY.GDP.PCAP.PP.CD": "gdp_per_capita_ppp_current_intl",
    "FP.CPI.TOTL.ZG": "inflation_cpi_annual_pct",
    "PA.NUS.FCRF": "official_exchange_rate_lcu_per_usd",
}

YEAR_RANGE = "2013:2025"
BASE = "https://api.worldbank.org/v2/country/all/indicator/{code}"
OUT_DIR = os.path.join("data", "raw", "worldbank")
os.makedirs(OUT_DIR, exist_ok=True)


def fetch_indicator(code, name):
    all_rows = []
    page = 1
    while True:
        url = BASE.format(code=code)
        params = {"format": "json", "date": YEAR_RANGE, "per_page": 20000, "page": page}
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        payload = resp.json()
        if not isinstance(payload, list) or len(payload) < 2 or payload[1] is None:
            break
        meta, rows = payload[0], payload[1]
        all_rows.extend(rows)
        if page >= meta.get("pages", 1):
            break
        page += 1
    df = pd.DataFrame([
        {
            "country_name": r["country"]["value"],
            "iso3": r["countryiso3code"],
            "year": int(r["date"]),
            name: r["value"],
        }
        for r in all_rows
    ])
    df = df[df["iso3"].notna() & (df["iso3"] != "")]
    out_path = os.path.join(OUT_DIR, f"{name}.csv")
    df.to_csv(out_path, index=False)
    print(f"{code} ({name}): {len(df)} rows, {df['iso3'].nunique()} countries -> {out_path}")
    return df


def main():
    frames = []
    for code, name in INDICATORS.items():
        df = fetch_indicator(code, name)
        frames.append(df.set_index(["iso3", "year", "country_name"])[[name]])
        time.sleep(0.3)
    combined = pd.concat(frames, axis=1).reset_index()
    combined.to_csv(os.path.join("data", "raw", "worldbank_panel_wide.csv"), index=False)
    print("Combined panel:", combined.shape)


if __name__ == "__main__":
    main()
