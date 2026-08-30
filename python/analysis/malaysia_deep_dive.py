# -*- coding: utf-8 -*-
"""
Malaysia supply-chain deep dive for Project 008.

Combines:
  - The resolved bilateral trade network (data/processed/trade_network_edges_
    export.csv, Malaysia = code 458) for supplier/customer concentration
    within the now-complete 59-country network. Genuinely covers all 59:
    Malaysia's own Comtrade data never included the United States, India,
    Belgium, or Ethiopia as a trading partner at all (Comtrade's free tier
    excludes those four entirely, from every reporter's data, not just
    Malaysia's), so those relationships come from OECD's own resolution
    instead -- see python/cleaning/merge_bilateral_trade.py.

    IMPORTANT for interpreting Malaysia's customer figures specifically:
    Malaysia's export-to-US edge is a MIRROR_IMPORT_OECD edge (the US's own
    import report, not Malaysia's own export report, which does not exist
    in this project's data). python/analysis/validate_mirror_statistics.py
    measured this exact kind of edge's typical discrepancy at trade flows
    this size (~14-17% for >=$10B relationships), which is wide enough that
    the reported figure (US 15.6%, Singapore 15.8%, China 13.9%) should NOT
    be read as a precise ranking; Malaysia's #1-vs-#2 customer between the
    US and Singapore is genuinely undetermined by this project's data, and
    any report or chart built from this output should say so rather than
    presenting the three percentages as settled. See LIMITATIONS.md item 17.
  - USGS critical materials data for Malaysia's position as tin/bauxite producer
  - World Bank LPI for Malaysia vs. ASEAN peers
  - DOSM BEC import data for production-input dependency

Outputs the Malaysia Supply Chain Vulnerability Index components (Section 21
of the brief) and the ASEAN logistics comparison (Section 18).
"""
import pandas as pd
import numpy as np
import os

OUT_DIR = "data/processed"
MYS_CODE = 458
ASEAN_ISO3 = ["MYS", "SGP", "IDN", "THA", "PHL", "VNM"]


def supplier_customer_concentration():
    # Resolved export edges (see python/cleaning/merge_bilateral_trade.py)
    # directly answer both questions: "who supplies Malaysia" = edges where
    # Malaysia is the IMPORTER (other countries' exports TO Malaysia); "who
    # buys from Malaysia" = edges where Malaysia is the EXPORTER. Both
    # directions are already fully resolved across all 59 countries, so no
    # separate M/X-flow lookup is needed here.
    df = pd.read_csv(os.path.join(OUT_DIR, "trade_network_edges_export.csv"))
    countries = pd.read_csv("data/external/network_countries.csv")
    code_to_name = dict(zip(countries["comtradeReporterCode"], countries["Country"]))

    results = {}
    for period in ["2016", "2023"]:
        sub = df[df["period"].astype(str) == str(period)]

        # Who supplies Malaysia (edges where Malaysia is the importer)
        imp = sub[sub["importerCode"] == MYS_CODE].copy()
        imp["supplier"] = imp["exporterCode"].map(code_to_name)
        imp["share_pct"] = imp["primaryValue"] / imp["primaryValue"].sum() * 100
        imp = imp.sort_values("share_pct", ascending=False)
        supplier_hhi = ((imp["share_pct"]) ** 2).sum()

        # Who buys from Malaysia (edges where Malaysia is the exporter)
        exp = sub[sub["exporterCode"] == MYS_CODE].copy()
        exp["customer"] = exp["importerCode"].map(code_to_name)
        exp["share_pct"] = exp["primaryValue"] / exp["primaryValue"].sum() * 100
        exp = exp.sort_values("share_pct", ascending=False)
        customer_hhi = ((exp["share_pct"]) ** 2).sum()

        results[period] = {
            "top_suppliers": imp[["supplier", "primaryValue", "share_pct"]].head(10),
            "top_customers": exp[["customer", "primaryValue", "share_pct"]].head(10),
            "supplier_HHI": supplier_hhi, "customer_HHI": customer_hhi,
            "n_suppliers": len(imp), "n_customers": len(exp),
        }

    for period in ["2016", "2023"]:
        results[period]["top_suppliers"].to_csv(
            os.path.join(OUT_DIR, f"malaysia_top_suppliers_{period}.csv"), index=False)
        results[period]["top_customers"].to_csv(
            os.path.join(OUT_DIR, f"malaysia_top_customers_{period}.csv"), index=False)

    summary = pd.DataFrame([
        {"period": p, "supplier_HHI": results[p]["supplier_HHI"], "customer_HHI": results[p]["customer_HHI"],
         "n_suppliers": results[p]["n_suppliers"], "n_customers": results[p]["n_customers"]}
        for p in ["2016", "2023"]
    ])
    summary.to_csv(os.path.join(OUT_DIR, "malaysia_trade_concentration_summary.csv"), index=False)
    print("Malaysia trade concentration:")
    print(summary.to_string(index=False))
    print("\nTop 5 suppliers 2023:")
    print(results["2023"]["top_suppliers"].head(5).to_string(index=False))
    print("\nTop 5 customers 2023:")
    print(results["2023"]["top_customers"].head(5).to_string(index=False))
    return results


def asean_logistics_comparison():
    # Use latest_lpi_snapshot.csv (each country's own latest year WITH a
    # non-null LPI score, since LPI is only published periodically -- not
    # master_supply_chain_panel's naive "latest row per country", which
    # picks up 2025 trade-only rows with no LPI at all for every ASEAN
    # country and silently returns an all-NaN table).
    latest = pd.read_csv(os.path.join(OUT_DIR, "latest_lpi_snapshot.csv"))
    asean = latest[latest["ISO3"].isin(ASEAN_ISO3)][
        ["ISO3", "Country", "Year", "logistics_performance_index_overall",
         "logistics_performance_index_customs", "logistics_performance_index_infrastructure",
         "logistics_performance_index_timeliness", "trade_pct_of_gdp"]
    ].sort_values("logistics_performance_index_overall", ascending=False)
    asean.to_csv(os.path.join(OUT_DIR, "malaysia_asean_logistics_comparison.csv"), index=False)
    print("\nASEAN-6 logistics comparison (each country's own latest year):")
    print(asean.to_string(index=False))
    return asean


def malaysia_critical_minerals_position():
    mat = pd.read_csv(os.path.join(OUT_DIR, "critical_materials_by_country.csv"))
    mys = mat[mat["country"].str.contains("Malaysia", case=False, na=False)]
    mys.to_csv(os.path.join(OUT_DIR, "malaysia_critical_minerals_position.csv"), index=False)
    print("\nMalaysia's position in critical-minerals production (2023):")
    print(mys.to_string(index=False) if len(mys) else "(Malaysia not a top-15+ producer for any tracked material)")
    return mys


if __name__ == "__main__":
    supplier_customer_concentration()
    asean_logistics_comparison()
    malaysia_critical_minerals_position()
