# -*- coding: utf-8 -*-
"""Generates all required visualisations for Project 008 (17 minimum, per brief Section 38)."""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import geopandas as gpd
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from style import ACCENT_1, ACCENT_2, GRAY, INK, INK_SECONDARY, INK_MUTED, GRID, SURFACE, add_source, end_label

OUT = "outputs/figures"
os.makedirs(OUT, exist_ok=True)

panel = pd.read_csv("data/processed/master_supply_chain_panel.csv")
lpi_latest = pd.read_csv("data/processed/latest_lpi_snapshot.csv")
countries = pd.read_csv("data/external/network_countries.csv")
risk = pd.read_csv("data/processed/supply_chain_risk_index.csv")
mat_summary = pd.read_csv("data/processed/critical_materials_concentration.csv")
mat_by_country = pd.read_csv("data/processed/critical_materials_by_country.csv")
comtrade = pd.read_csv("data/raw/comtrade_bilateral_trade_raw.csv")
network_centrality = pd.read_csv("data/processed/trade_network_centrality.csv")
mys_headline = pd.read_csv("data/processed/malaysia_trade_headline_annual.csv")
mys_forecast = pd.read_csv("data/processed/malaysia_export_forecast_2026_2030.csv")
mys_backtest = pd.read_csv("data/processed/malaysia_export_forecast_backtest.csv")
mys_vuln = pd.read_csv("data/processed/malaysia_vulnerability_index.csv")
mys_opp = pd.read_csv("data/processed/malaysia_opportunity_radar.csv")
mys_suppliers = pd.read_csv("data/processed/malaysia_top_suppliers_2023.csv")
mys_customers = pd.read_csv("data/processed/malaysia_top_customers_2023.csv")
asean_lpi = pd.read_csv("data/processed/malaysia_asean_logistics_comparison.csv")
nickel_mc = pd.read_csv("data/processed/nickel_monte_carlo_12m.csv")

REGION_ORDER = countries["Project_007_Region"].value_counts().index.tolist()
REGION_COLORS = {r: c for r, c in zip(REGION_ORDER, [ACCENT_1, '#5a9bd6', '#8fb8de', GRAY, GRAY, GRAY, GRAY, GRAY])}


def save(fig, name):
    fig.savefig(f"{OUT}/{name}.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("saved", name)


# ---------------------------------------------------------------------------
# 01. Global trade map (choropleth: merchandise exports as % of GDP, latest year)
# ---------------------------------------------------------------------------
latest_trade = panel.sort_values("Year").groupby("ISO3").tail(1)
world = gpd.read_file("data/external/world_110m.geojson")
merged = world.merge(latest_trade, left_on="ISO_A3", right_on="ISO3", how="left")
fig, ax = plt.subplots(figsize=(14, 7.5))
merged.plot(column="trade_pct_of_gdp", ax=ax, cmap="Blues", legend=True,
            missing_kwds={"color": "#e8e8e5", "label": "No data"},
            legend_kwds={"label": "Trade (exports+imports), % of GDP", "shrink": 0.55},
            edgecolor="white", linewidth=0.3, vmax=200)
ax.set_ylim(-58, 85); ax.set_xlim(-170, 190)
ax.set_title("Trade openness varies enormously: city-states trade 300%+ of GDP, large economies under 40%", loc="left", fontsize=13)
ax.set_axis_off()
add_source(fig, "Source: World Bank, trade % of GDP, each country's own latest available year, PUBLIC.")
save(fig, "01_global_trade_map")

# ---------------------------------------------------------------------------
# 02. Global supply-chain network (2023, top 59 economies)
# ---------------------------------------------------------------------------
g = nx.DiGraph()
sub = comtrade[(comtrade["period"].astype(str) == "2023") & (comtrade["flow"] == "X")]
code_to_name = dict(zip(countries["comtradeReporterCode"], countries["Country"]))
code_to_region = dict(zip(countries["comtradeReporterCode"], countries["Project_007_Region"]))
for _, row in sub.iterrows():
    g.add_edge(int(row["reporterCode"]), int(row["partnerCode"]), weight=row["primaryValue"])
pos = nx.spring_layout(g, seed=42, k=0.4, weight="weight")
node_size = [sum(w for _, _, w in g.out_edges(n, data="weight")) / 3e8 + 20 for n in g.nodes]
node_color = [REGION_COLORS.get(code_to_region.get(n), GRAY) for n in g.nodes]
fig, ax = plt.subplots(figsize=(13, 10))
nx.draw_networkx_edges(g, pos, ax=ax, alpha=0.06, edge_color=GRAY, arrows=False)
nx.draw_networkx_nodes(g, pos, ax=ax, node_size=node_size, node_color=node_color, alpha=0.85, linewidths=0.5, edgecolors="white")
top12 = sorted(g.nodes, key=lambda n: sum(w for _, _, w in g.out_edges(n, data="weight")), reverse=True)[:12]
for n in top12:
    ax.annotate(code_to_name.get(n, n), pos[n], fontsize=8.5, color=INK_SECONDARY, ha="center", va="bottom")
ax.set_title("The 59-economy global trade network: hubs are large economies, not necessarily central ones", loc="left")
ax.set_axis_off()
add_source(fig, "Source: UN Comtrade, 2023 total exports among 59 major economies — PUBLIC. Node size = total exports; labels = top 12 by export volume.")
save(fig, "02_global_trade_network")

# ---------------------------------------------------------------------------
# 03. Regional trade comparison
# ---------------------------------------------------------------------------
reg_trade = latest_trade.groupby("Region").agg(
    total_exports=("merchandise_exports_current_usd", "sum"),
    median_trade_pct_gdp=("trade_pct_of_gdp", "median"),
).reset_index().sort_values("total_exports")
fig, ax = plt.subplots(figsize=(8.5, 5.5))
ax.barh(reg_trade["Region"], reg_trade["total_exports"] / 1e12, color=ACCENT_1)
ax.set_title("Europe and East Asia dominate merchandise exports among tracked economies", loc="left")
ax.set_xlabel("Total merchandise exports (USD trillion, each country's latest year)")
add_source(fig, "Source: World Bank merchandise exports, PUBLIC. 59-country network + full 217-economy panel where available.")
save(fig, "03_regional_trade_comparison")

# ---------------------------------------------------------------------------
# 04. Country dependency map (import dependency, % of GDP)
# ---------------------------------------------------------------------------
merged2 = world.merge(risk[["ISO3", "score_import_dependency"]].merge(
    latest_trade[["ISO3", "merchandise_imports_current_usd", "gdp_current_usd"]], on="ISO3"),
    left_on="ISO_A3", right_on="ISO3", how="left")
merged2["import_dependency_pct"] = merged2["merchandise_imports_current_usd"] / merged2["gdp_current_usd"] * 100
fig, ax = plt.subplots(figsize=(14, 7.5))
merged2.plot(column="import_dependency_pct", ax=ax, cmap="Oranges", legend=True,
             missing_kwds={"color": "#e8e8e5", "label": "Not in 59-country network"},
             legend_kwds={"label": "Imports, % of GDP", "shrink": 0.55}, edgecolor="white", linewidth=0.3, vmax=100)
ax.set_ylim(-58, 85); ax.set_xlim(-170, 190)
ax.set_title("Import dependency (% of GDP) among the 59 major economies tracked", loc="left", fontsize=13)
ax.set_axis_off()
add_source(fig, "Source: World Bank, merchandise imports / GDP, PUBLIC. Limited to the 59-country network (see docs/LIMITATIONS.md).")
save(fig, "04_country_dependency_map")

# ---------------------------------------------------------------------------
# 05. Trade concentration chart (export-partner HHI, top/bottom 15)
# ---------------------------------------------------------------------------
conc = risk.dropna(subset=["score_trade_concentration"]).sort_values("score_trade_concentration", ascending=False)
top15 = conc.head(15).sort_values("score_trade_concentration")
fig, ax = plt.subplots(figsize=(8.5, 7))
ax.barh(top15["Country"], top15["score_trade_concentration"], color=ACCENT_2)
ax.set_title("Most export-concentrated economies in the network (highest HHI, most exposed to a single market)", loc="left", fontsize=11.5)
ax.set_xlabel("Export-partner concentration score (0-100, min-max of HHI)")
add_source(fig, "Source: UN Comtrade, 2023 export destinations within the 59-country network — PUBLIC.")
save(fig, "05_trade_concentration")

# ---------------------------------------------------------------------------
# 06. Critical-material supply concentration (HHI ranking, all 15 tracked series)
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 7))
ms = mat_summary.sort_values("HHI")
colors = [ACCENT_2 if h > 5000 else (ACCENT_1 if h > 2500 else GRAY) for h in ms["HHI"]]
bars = ax.barh(ms["material"], ms["HHI"], color=colors)
for b, top, share in zip(bars, ms.sort_values("HHI")["top_producer"], ms.sort_values("HHI")["top_producer_share_pct"]):
    ax.annotate(f"{top} {share:.0f}%", xy=(b.get_width(), b.get_y() + b.get_height()/2), xytext=(5, 0),
                textcoords="offset points", va="center", fontsize=8, color=INK_SECONDARY)
ax.axvline(2500, color=INK_MUTED, linewidth=0.8, linestyle=(0, (3, 3)))
ax.set_title("Gallium, tungsten, graphite, and cobalt are the most supply-concentrated critical materials", loc="left", fontsize=12)
ax.set_xlabel("Herfindahl-Hirschman Index (HHI) of 2023 world mine production by country")
add_source(fig, "Source: USGS Mineral Commodity Summaries 2025, World Data Release — PUBLIC. Dashed line = 2500, the standard HHI \"highly concentrated\" threshold.")
save(fig, "06_critical_material_concentration")

# ---------------------------------------------------------------------------
# 07. Commodity price risk: nickel Monte Carlo (12-month simulated distribution)
# ---------------------------------------------------------------------------
prices = pd.read_csv("data/processed/commodity_prices_monthly.csv")
nickel = prices[prices["commodity"] == "Nickel"].sort_values("date")
nickel["date"] = pd.to_datetime(nickel["date"])
fig, ax = plt.subplots(figsize=(9, 6))
recent = nickel[nickel["date"] >= "2015-01-01"]
ax.plot(recent["date"], recent["price_usd_nominal"], color=ACCENT_1, linewidth=1.5)
current = nickel.iloc[-1]
mc = nickel_mc[nickel_mc["method"] == "block_bootstrap_6mo"].iloc[0]
future_date = current["date"] + pd.DateOffset(months=12)
ax.plot([current["date"], future_date], [current["price_usd_nominal"], mc["simulated_median_12m"]],
        color=ACCENT_2, linestyle="--", linewidth=1.5)
ax.fill_between([current["date"], future_date], [current["price_usd_nominal"], mc["simulated_p10_12m"]],
                 [current["price_usd_nominal"], mc["simulated_p90_12m"]], color=ACCENT_2, alpha=0.15)
ax.annotate(f"Simulated 12-month range\n(10th-90th percentile,\n10,000 bootstrap paths)", xy=(future_date, mc["simulated_p90_12m"]),
            xytext=(-140, 10), textcoords="offset points", fontsize=8.5, color=INK_SECONDARY)
ax.set_title("Nickel price: history and a 12-month Monte Carlo risk range, not a forecast", loc="left")
ax.set_ylabel("USD per metric ton")
add_source(fig, "Source: World Bank Commodity Markets (Pink Sheet), PUBLIC. Monte Carlo: historical block-bootstrap of monthly log returns, 10,000 simulations. Not a point forecast.")
save(fig, "07_nickel_price_montecarlo")

# ---------------------------------------------------------------------------
# 08. Port / logistics map (LPI overall score choropleth)
# ---------------------------------------------------------------------------
merged3 = world.merge(lpi_latest[["ISO3", "logistics_performance_index_overall"]], left_on="ISO_A3", right_on="ISO3", how="left")
fig, ax = plt.subplots(figsize=(14, 7.5))
merged3.plot(column="logistics_performance_index_overall", ax=ax, cmap="Greens", legend=True,
             missing_kwds={"color": "#e8e8e5", "label": "No data"},
             legend_kwds={"label": "Logistics Performance Index (1-5)", "shrink": 0.55}, edgecolor="white", linewidth=0.3)
ax.set_ylim(-58, 85); ax.set_xlim(-170, 190)
ax.set_title("Logistics performance is concentrated in Western Europe, East Asia, and a few global hubs", loc="left", fontsize=13)
ax.set_axis_off()
add_source(fig, "Source: World Bank Logistics Performance Index, each country's own latest published edition — PUBLIC.")
save(fig, "08_logistics_performance_map")

# ---------------------------------------------------------------------------
# 09. "Shipping route analysis" substitute: container port traffic by country
#     (documented substitution -- AIS/vessel-route data is outside this
#     project's legitimately-accessible free-data scope; see LIMITATIONS.md)
# ---------------------------------------------------------------------------
port = panel.dropna(subset=["container_port_traffic_teu"]).sort_values("Year").groupby("ISO3").tail(1)
top_ports = port.sort_values("container_port_traffic_teu", ascending=False).head(15).sort_values("container_port_traffic_teu")
fig, ax = plt.subplots(figsize=(8.5, 7))
ax.barh(top_ports["Country"], top_ports["container_port_traffic_teu"] / 1e6, color=ACCENT_1)
ax.set_title("Top 15 economies by container port traffic (a shipping-route-exposure proxy)", loc="left", fontsize=11.5)
ax.set_xlabel("Container port traffic (million TEU, latest available year)")
add_source(fig, "Source: World Bank, container port traffic, PUBLIC. Substitutes for vessel-level AIS route data, which is outside this project's free-data scope — see docs/LIMITATIONS.md.")
save(fig, "09_container_port_traffic")

# ---------------------------------------------------------------------------
# 10. Supply-chain risk heatmap (top 15 countries x 4 pillars)
# ---------------------------------------------------------------------------
top_risk = risk.sort_values("supply_chain_risk_score", ascending=False).head(15)
pillar_cols = ["score_import_dependency", "score_logistics_fragility", "score_trade_concentration", "score_commodity_exposure"]
pillar_labels = ["Import\ndependency", "Logistics\nfragility", "Trade\nconcentration", "Commodity\nexposure"]
fig, ax = plt.subplots(figsize=(7.5, 8))
im = ax.imshow(top_risk[pillar_cols].values, cmap="Reds", aspect="auto", vmin=0, vmax=100)
ax.set_yticks(range(len(top_risk))); ax.set_yticklabels(top_risk["Country"])
ax.set_xticks(range(len(pillar_labels))); ax.set_xticklabels(pillar_labels, fontsize=9)
for i in range(len(top_risk)):
    for j in range(len(pillar_cols)):
        ax.text(j, i, f"{top_risk[pillar_cols].values[i, j]:.0f}", ha="center", va="center", fontsize=8,
                color="white" if top_risk[pillar_cols].values[i, j] > 55 else INK)
ax.set_title("Highest supply-chain risk economies, by pillar (0-100, darker = higher risk)", loc="left", fontsize=11.5)
fig.colorbar(im, ax=ax, shrink=0.7, label="Risk score (0-100)")
add_source(fig, "Source: this project's Supply Chain Risk Index — see MARKET_ATTRACTIVENESS-style methodology in docs/METHODOLOGY.md.")
save(fig, "10_risk_heatmap")

# ---------------------------------------------------------------------------
# 11. Network centrality visualisation (betweenness vs eigenvector, 2023)
# ---------------------------------------------------------------------------
nc = network_centrality[network_centrality["period"] == 2023] if network_centrality["period"].dtype != object else network_centrality[network_centrality["period"] == "2023"]
fig, ax = plt.subplots(figsize=(9, 7))
ax.scatter(nc["betweenness_centrality"], nc["eigenvector_centrality"], s=nc["total_exports_to_network_usd"] / 3e9 + 15,
           color=ACCENT_1, alpha=0.6, edgecolor="white", linewidth=0.4)
top_label = nc.nlargest(10, "eigenvector_centrality")
for _, row in top_label.iterrows():
    ax.annotate(row["Country"], xy=(row["betweenness_centrality"], row["eigenvector_centrality"]),
                xytext=(5, 4), textcoords="offset points", fontsize=8, color=INK_SECONDARY)
ax.set_title("Network centrality: bridging role (x) vs. importance-by-association (y)", loc="left")
ax.set_xlabel("Betweenness centrality (bridges between otherwise-unconnected trade relationships)")
ax.set_ylabel("Eigenvector centrality (connected to other important economies)")
add_source(fig, "Source: NetworkX on UN Comtrade 2023 bilateral exports, 59-country network — PUBLIC/DERIVED. Bubble size = total exports.")
save(fig, "11_network_centrality")

# ---------------------------------------------------------------------------
# 12. Historical structural-change timeline (world trade openness + LPI trend)
# ---------------------------------------------------------------------------
world_trend = panel.groupby("Year")["trade_pct_of_gdp"].median()
fig, ax = plt.subplots(figsize=(9.5, 6))
ax.plot(world_trend.index, world_trend.values, color=ACCENT_1, linewidth=2)
for year, label in [(2020, "COVID"), (2022, "Ukraine war /\nenergy shock")]:
    ax.axvline(year, color=INK_MUTED, linewidth=0.8, linestyle=(0, (3, 3)))
    ax.annotate(label, xy=(year, ax.get_ylim()[1]), xytext=(3, -12), textcoords="offset points", fontsize=8, color=INK_MUTED)
ax.set_title("Median trade openness (trade as % of GDP) across tracked economies, 2013-2025", loc="left")
ax.set_ylabel("Trade, % of GDP (median across countries)")
add_source(fig, "Source: World Bank, PUBLIC. Vertical lines mark widely-documented global shock years, not statistically-detected break points.")
save(fig, "12_structural_change_timeline")

# ---------------------------------------------------------------------------
# 13. Forecast chart: Malaysia exports, backtest + forward forecast
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9.5, 6))
ax.plot(mys_headline["year"], mys_headline["exports"] / 1e12, color=INK, linewidth=1.8, label="Actual")
ax.plot(mys_forecast["year"], mys_forecast["forecast_exports"] / 1e12, color=ACCENT_2, linewidth=1.8, linestyle="--", label="Forecast (naive+drift, backtest winner)")
ax.fill_between(mys_forecast["year"], mys_forecast["lower_90pct_band"] / 1e12, mys_forecast["upper_90pct_band"] / 1e12, color=ACCENT_2, alpha=0.15)
ax.legend(loc="upper left", fontsize=9)
ax.set_title("Malaysia merchandise exports: actual 2001-2025, forecast to 2030", loc="left")
ax.set_ylabel("Exports (RM trillion)")
add_source(fig, "Source: DOSM, PUBLIC. Forecast model selected by 5-year rolling backtest (lowest RMSE) — see docs/FORECASTING.md; naive+drift beat ARIMA and ETS.")
save(fig, "13_malaysia_export_forecast")

# ---------------------------------------------------------------------------
# 14. Scenario comparison (Malaysia 2030+ impact, qualitative-to-semiquant)
# ---------------------------------------------------------------------------
scenarios = ["Globalisation\nRebounds", "Asian\nRegionalisation", "China+1\nAccelerates", "Geopolitical\nFragmentation",
             "Critical Resource\nShortage", "AI/Semiconductor\nBoom", "Major Logistics\nDisruption", "Climate\nStress"]
impact_score = [2, 3, 4, -3, -1, 4, -2, 0]  # -5 (very negative) to +5 (very positive) for Malaysia, documented judgment -- see SCENARIO_METHODOLOGY.md
colors = [ACCENT_1 if s > 0 else (ACCENT_2 if s < 0 else GRAY) for s in impact_score]
fig, ax = plt.subplots(figsize=(9, 6))
order = np.argsort(impact_score)
ax.barh(np.array(scenarios)[order], np.array(impact_score)[order], color=np.array(colors)[order])
ax.axvline(0, color=INK, linewidth=0.8)
ax.set_title("Malaysia 2030+ scenario impact assessment (documented judgment, not a model output)", loc="left", fontsize=11)
ax.set_xlabel("Directional impact on Malaysia (-5 very negative to +5 very positive)")
add_source(fig, "Source: this project's scenario methodology, docs/SCENARIO_METHODOLOGY.md — DERIVED judgment grounded in this project's own data, not a quantitative model.")
save(fig, "14_scenario_comparison")

# ---------------------------------------------------------------------------
# 15. Malaysia supply-chain map: top suppliers and customers, 2023
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(13, 6))
s = mys_suppliers.sort_values("share_pct").tail(8)
axes[0].barh(s["supplier"], s["share_pct"], color=ACCENT_1)
axes[0].set_title("Who supplies Malaysia (2023)", loc="left", fontsize=11)
axes[0].set_xlabel("% of Malaysia's imports")
c = mys_customers.sort_values("share_pct").tail(8)
axes[1].barh(c["customer"], c["share_pct"], color=ACCENT_2)
axes[1].set_title("Who buys from Malaysia (2023)", loc="left", fontsize=11)
axes[1].set_xlabel("% of Malaysia's exports")
add_source(fig, "Source: UN Comtrade, Malaysia bilateral trade within the 59-country network, PUBLIC.")
save(fig, "15_malaysia_suppliers_customers")

# ---------------------------------------------------------------------------
# 16. Malaysia vulnerability dashboard
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 5.5))
mv = mys_vuln.sort_values("score_0_100")
ax.barh(mv["dimension"], mv["score_0_100"], color=ACCENT_2)
ax.set_title("Malaysia Supply Chain Vulnerability Index components", loc="left", fontsize=11.5)
ax.set_xlabel("Score (0-100, higher = more vulnerable)")
add_source(fig, "Source: this project's Malaysia Vulnerability Index, DERIVED from UN Comtrade, World Bank, and DOSM data — see docs/METHODOLOGY.md.")
save(fig, "16_malaysia_vulnerability_dashboard")

# ---------------------------------------------------------------------------
# 17. Malaysia opportunity radar
# ---------------------------------------------------------------------------
strength_map = {"Strong (direct DOSM trade data)": 3, "Strong (World Bank LPI, direct comparison)": 3,
                "Weak / speculative -- named as a hypothesis, not confirmed by this project's data": 1,
                "Not evidenced by this project -- flagged as a gap, not claimed": 0}
mys_opp["strength_score"] = mys_opp["evidence_strength"].map(strength_map)
fig, ax = plt.subplots(figsize=(9, 5))
colors17 = [ACCENT_1 if s == 3 else (GRAY if s == 1 else "#c0392b") for s in mys_opp["strength_score"]]
ax.barh(mys_opp["opportunity"], mys_opp["strength_score"], color=colors17)
ax.set_xticks([0, 1, 2, 3])
ax.set_xticklabels(["Not evidenced", "", "", "Strongly evidenced"])
ax.set_title("Malaysia opportunity radar: evidence strength, not likelihood", loc="left", fontsize=11.5)
add_source(fig, "Source: this project's opportunity radar, DERIVED — evidence graded against this project's own collected data, see docs/METHODOLOGY.md.")
save(fig, "17_malaysia_opportunity_radar")

print("\nAll 17 required visualisations generated.")
