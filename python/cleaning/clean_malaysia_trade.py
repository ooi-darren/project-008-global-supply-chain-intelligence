# -*- coding: utf-8 -*-
"""
Malaysia trade data cleaning for Project 008 -- DOSM (OpenDOSM) sources.

Sources (all PUBLIC, CC-BY 4.0, storage.dosm.gov.my/trade/):
  - trade_headline.parquet: monthly exports/imports/re-exports/balance, 2000-present
  - trade_sitc_1d.parquet: monthly exports/imports by SITC section (1-digit), 2000-present
  - trade_enduse_bec.parquet: monthly retained imports by Broad Economic
    Category (capital / intermediate / consumer goods) and end use, 2010-present
    -- this is the key supply-chain-relevant series: it shows directly
    whether Malaysia's import mix is shifting toward production inputs
    (intermediate/capital goods) or final consumption.

Note: DOSM's OpenDOSM portal does not publish a country-partner-level trade
breakdown (checked directly against the full data-catalogue file listing,
291 files, no country/partner trade dataset present). Malaysia's bilateral
supplier/customer concentration is instead built from UN Comtrade (Malaysia
is reporter 458, already part of the 59-country network pull) -- see
python/analysis/malaysia_trade_concentration.py.
"""
import pandas as pd
import os

OUT_DIR = "data/processed"
os.makedirs(OUT_DIR, exist_ok=True)


def clean_headline():
    df = pd.read_parquet("data/raw/dosm_trade_headline.parquet")
    df = df[df["series"] == "abs"].copy()  # 'abs' = absolute values (not seasonally-adjusted variant)
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    annual = df.groupby("year").agg(
        exports=("exports", "sum"), imports=("imports", "sum"),
        exports_domestic=("exports_domestic", "sum"), re_exports=("re_exports", "sum"),
        balance=("balance", "sum"),
    ).reset_index()
    annual = annual[(annual["year"] >= 2001) & (annual["year"] <= 2025)]  # drop partial first/last years
    annual["export_growth_yoy_pct"] = annual["exports"].pct_change() * 100
    annual.to_csv(os.path.join(OUT_DIR, "malaysia_trade_headline_annual.csv"), index=False)
    print("malaysia_trade_headline_annual.csv:", annual.shape)
    return annual


def clean_bec():
    df = pd.read_parquet("data/raw/dosm_trade_enduse_bec.parquet")
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    df = df[df["series"] == "abs"].copy()
    # bec arrives as an Arrow-backed string dtype from parquet (not a plain
    # int64) -- cast explicitly here rather than relying on it, since a
    # round-trip through CSV silently reinfers it as int64 (the same class
    # of dtype-mismatch bug already hit twice elsewhere in this project with
    # the Comtrade "period" column -- fixing it at the source this time
    # instead of patching every downstream comparison again).
    df["bec"] = df["bec"].astype(int)
    annual = df.groupby(["year", "end_use", "bec"])["imports"].sum().reset_index()
    annual = annual[(annual["year"] >= 2011) & (annual["year"] <= 2025)]
    annual.to_csv(os.path.join(OUT_DIR, "malaysia_imports_by_bec_annual_detail.csv"), index=False)
    print("malaysia_imports_by_bec_annual_detail.csv:", annual.shape)

    # bec == 0 is each end_use category's OWN total row; the other bec codes
    # (e.g. 111, 121, 210...) are that SAME end_use's own sub-breakdown, not
    # a different end_use. Verified directly: summing capital's + intermediate's
    # bec==0 rows and dividing by retained_imports' bec==0 total gives ~86%,
    # a plausible production-input share; summing ALL rows (bec==0 AND its own
    # sub-breakdown together) for those two end_use categories -- the bug in
    # this script's first version -- roughly DOUBLE-counts them (each
    # end_use's total plus its own components, both included), producing an
    # impossible >100% "share of imports" figure that should have been an
    # immediate red flag. This totals-only file is what downstream scripts
    # (e.g. the Malaysia vulnerability index) should read.
    totals = annual[annual["bec"] == 0].drop(columns=["bec"])
    totals.to_csv(os.path.join(OUT_DIR, "malaysia_imports_by_bec_annual.csv"), index=False)
    print("malaysia_imports_by_bec_annual.csv (totals only):", totals.shape)
    print(totals["end_use"].unique())
    return totals


def clean_sitc():
    df = pd.read_parquet("data/raw/dosm_trade_sitc_1d.parquet")
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    annual = df.groupby(["year", "section"]).agg(exports=("exports", "sum"), imports=("imports", "sum")).reset_index()
    annual = annual[(annual["year"] >= 2001) & (annual["year"] <= 2025)]
    annual.to_csv(os.path.join(OUT_DIR, "malaysia_trade_sitc_annual.csv"), index=False)
    print("malaysia_trade_sitc_annual.csv:", annual.shape)
    print(sorted(annual["section"].unique()))
    return annual


if __name__ == "__main__":
    clean_headline()
    clean_bec()
    clean_sitc()
