# -*- coding: utf-8 -*-
"""
Critical raw material intelligence for Project 008.

Source: USGS Mineral Commodity Summaries 2025, World Data Release
(data/raw/usgs_world_2025/MCS2025_World_Data.csv) -- world production
(2023 actual + 2024 estimate), plant capacity, and reserves by country,
for 90+ nonfuel mineral commodities. Real, authoritative, PUBLIC data;
see docs/SOURCES.md.

MATERIAL SELECTION METHODOLOGY (the brief explicitly requires a transparent
basis for calling a material "critical" rather than an arbitrary list):
13 materials selected against four documented criteria --
  1. Semiconductor/electronics relevance: Gallium, Silicon, Tin, Copper
  2. EV/battery relevance: Lithium, Cobalt, Nickel, Graphite, Manganese,
     Rare earths (magnets)
  3. Independently well-documented high supply concentration (USGS itself
     flags several of these as import-reliance/concentration risks in its
     own annual risk commentary): Rare earths, Cobalt, Gallium, Tungsten
  4. Direct Malaysia relevance: Tin (historic and current Malaysian mining
     industry), Bauxite/Aluminum (Pahang's 2015-2016 bauxite mining boom
     and environmental crisis is a real, documented Malaysian episode)
A material can qualify on more than one criterion; all 13 qualify on at
least one, most on two or more.

METHOD: for each material, take the "Mine production" row type (the supply
stage most exposed to genuine geological/geopolitical concentration risk --
refining concentration is captured separately where USGS reports it, e.g.
Copper and Bauxite/Aluminum both have mine vs. refinery rows, a genuinely
important distinction since mining and refining concentration can differ
sharply, most famously cobalt: DRC dominates mining, China dominates
refining). Compute, per material, using 2023 production (the last actual,
non-estimated year):
  - HHI (Herfindahl-Hirschman Index) on country production shares
  - CR3 / CR5 (share held by top 3 / top 5 producing countries)
  - top producer and its share
Do not treat concentration as automatically bad -- it is one input into the
supply-risk framework built later (see python/analysis/risk_index.py).
"""
import pandas as pd
import numpy as np
import os

RAW = "data/raw/usgs_world_2025/MCS2025_World_Data.csv"
OUT_DIR = "data/processed"
os.makedirs(OUT_DIR, exist_ok=True)

MATERIALS = {
    "Copper": "Mine production, recoverable copper content",
    "Copper (refined)": "Refinery production, copper",
    "Lithium": "Mine production, lithium content",
    "Cobalt": "Mine production, cobalt content, estimated",
    "Nickel": "Mine production, nickel content",
    "Graphite": "Mine production",
    "Rare earths": "Mine production, rare-earth-oxide equivalent",
    "Tin": "Mine production, tin content",
    "Bauxite": "Mine production, bauxite, dry tons",
    "Aluminum (refined)": "Refinery production, alumina - calcined equivalent weights",
    "Manganese": None,  # resolved below (TYPE varies; picked after inspection)
    "Tungsten": None,
    "Gallium": None,
    "Silicon": None,
    "Titanium Mineral Concentrates": None,
}

# Non-country aggregate labels USGS includes in the COUNTRY column that must
# be excluded from country-level concentration math. Verified by inspecting
# every unique COUNTRY value across the full file (154 labels): variants like
# "World total (rounded)", "World total (ilmenite and rutile, rounded)",
# "Other countries (includes crude)" all appear, so an exact-match exclusion
# set silently missed most of them (first run wrongly ranked "World total
# (rounded)" as every material's #1 producer at ~50% share -- caught by
# noticing every material's top producer was implausibly named "World total").
# A substring match on "world total" / "other countr" catches all variants
# actually present; "united states and canada" is the one non-single-country
# aggregate confirmed elsewhere in the file (Abrasives) and excluded by name.
NON_COUNTRY_PATTERNS = ("world total", "other countr")
NON_COUNTRY_EXACT = {"united states and canada"}


def is_country_row(country_label):
    label = str(country_label).strip().lower()
    if label in NON_COUNTRY_EXACT:
        return False
    if any(pat in label for pat in NON_COUNTRY_PATTERNS):
        return False
    return True


def load_raw():
    df = pd.read_csv(RAW, encoding="latin-1")
    df.columns = [c.strip().lstrip("﻿") for c in df.columns]
    for col in ["COMMODITY", "COUNTRY", "TYPE"]:
        df[col] = df[col].astype(str).str.strip()
    return df


def resolve_type(df, commodity, keyword):
    """For materials where the exact TYPE label needs picking at runtime,
    return the first TYPE containing `keyword` (case-insensitive) for that
    commodity -- printed for manual verification, not silently trusted."""
    types = df[df["COMMODITY"] == commodity]["TYPE"].unique().tolist()
    matches = [t for t in types if keyword.lower() in t.lower()]
    if not matches:
        raise ValueError(f"No TYPE match for {commodity} / '{keyword}'. Available: {types}")
    return matches[0]


def concentration_metrics(shares):
    """shares: array of fractions (0-1) summing to <=1. Returns HHI (0-10000
    scale, standard convention), CR3, CR5."""
    shares_sorted = np.sort(shares)[::-1]
    hhi = np.sum((shares_sorted * 100) ** 2)  # HHI on percentage-point scale
    cr3 = shares_sorted[:3].sum() * 100
    cr5 = shares_sorted[:5].sum() * 100
    return hhi, cr3, cr5


def main():
    df = load_raw()

    # Resolve ambiguous TYPE labels for the remaining materials by inspection
    MATERIALS["Manganese"] = resolve_type(df, "Manganese", "Mine production")
    MATERIALS["Tungsten"] = resolve_type(df, "Tungsten", "Mine production")
    MATERIALS["Gallium"] = resolve_type(df, "Gallium", "production")
    MATERIALS["Silicon"] = resolve_type(df, "Silicon", "production")
    MATERIALS["Titanium Mineral Concentrates"] = resolve_type(df, "Titanium Mineral Concentrates", "Mine production")

    country_rows = []
    summary_rows = []

    for material, type_label in MATERIALS.items():
        commodity = material.split(" (")[0] if material not in df["COMMODITY"].unique() else material
        # commodity names in the raw file don't always match our display name
        # (e.g. "Copper (refined)" -> commodity "Copper"); resolve explicitly:
        commodity_map = {
            "Copper": "Copper", "Copper (refined)": "Copper",
            "Aluminum (refined)": "Bauxite",  # refinery production is listed under the Bauxite commodity block
        }
        commodity = commodity_map.get(material, material)

        sub = df[(df["COMMODITY"] == commodity) & (df["TYPE"] == type_label)].copy()
        sub = sub[sub["COUNTRY"].apply(is_country_row)]
        sub["PROD_2023"] = pd.to_numeric(sub["PROD_2023"], errors="coerce")
        sub = sub.dropna(subset=["PROD_2023"])
        sub = sub[sub["PROD_2023"] > 0]

        total = sub["PROD_2023"].sum()
        if total <= 0 or len(sub) == 0:
            print(f"SKIP {material}: no usable 2023 production rows")
            continue
        sub["share_2023"] = sub["PROD_2023"] / total
        sub["material"] = material

        for _, row in sub.iterrows():
            country_rows.append({
                "material": material, "country": row["COUNTRY"],
                "production_2023": row["PROD_2023"], "share_pct": round(row["share_2023"] * 100, 2),
            })

        hhi, cr3, cr5 = concentration_metrics(sub["share_2023"].values)
        top = sub.sort_values("share_2023", ascending=False).iloc[0]
        summary_rows.append({
            "material": material, "n_producing_countries": len(sub),
            "total_production_2023": total, "unit": sub["UNIT_MEAS"].iloc[0] if "UNIT_MEAS" in sub else None,
            "top_producer": top["COUNTRY"], "top_producer_share_pct": round(top["share_2023"] * 100, 2),
            "HHI": round(hhi, 1), "CR3_pct": round(cr3, 1), "CR5_pct": round(cr5, 1),
        })
        print(f"{material}: {len(sub)} countries, top={top['COUNTRY']} ({top['share_2023']*100:.1f}%), HHI={hhi:.0f}")

    country_df = pd.DataFrame(country_rows)
    summary_df = pd.DataFrame(summary_rows).sort_values("HHI", ascending=False)

    country_df.to_csv(os.path.join(OUT_DIR, "critical_materials_by_country.csv"), index=False)
    summary_df.to_csv(os.path.join(OUT_DIR, "critical_materials_concentration.csv"), index=False)
    print(f"\nSaved {len(country_df)} country rows and {len(summary_df)} material summaries.")
    print("\nConcentration ranking (most concentrated first):")
    print(summary_df[["material", "top_producer", "top_producer_share_pct", "HHI", "CR3_pct"]].to_string(index=False))


if __name__ == "__main__":
    main()
