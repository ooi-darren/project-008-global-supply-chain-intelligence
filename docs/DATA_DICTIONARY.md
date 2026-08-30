# Data Dictionary

## `data/processed/master_supply_chain_panel.csv` (World Bank, country x year)

| Column | Unit | Notes |
|---|---|---|
| `ISO3`, `Country`, `Region`, `Official_Region`, `Sub_Region` |; | Reused from Project 007's region mapping |
| `Year` | year | 2013-2025 |
| `trade_pct_of_gdp` | % | Exports + imports as % of GDP |
| `merchandise_exports_current_usd` / `merchandise_imports_current_usd` | current US$ | Nominal |
| `merchandise_export_price_index` | index | |
| `high_tech_exports_pct_of_manuf_exports` | % | |
| `logistics_performance_index_overall/customs/infrastructure/timeliness` | 1-5 scale | Published periodically, not annually. See `latest_lpi_snapshot.csv` for the "each country's own latest edition" version |
| `container_port_traffic_teu` | TEU | |
| `air_freight_million_ton_km` / `rail_freight_million_ton_km` | million ton-km | |
| `gdp_current_usd` | current US$ | Nominal |
| `gdp_growth_annual_pct` | % | |
| `gdp_per_capita_ppp_current_intl` | current intl $ | PPP-adjusted |
| `inflation_cpi_annual_pct` | % | |
| `official_exchange_rate_lcu_per_usd` | LCU/USD | |
| `export_cagr_nominal_pct` | % | Derived, nominal (not real). See `METHODOLOGY.md` |

## `data/raw/comtrade_bilateral_trade_raw.csv` (UN Comtrade, bilateral)

| Column | Notes |
|---|---|
| `period` | "2016" or "2023" |
| `flow` | "X" (export) or "M" (import) |
| `reporterCode` / `partnerCode` | UN Comtrade numeric country codes; map via `data/external/network_countries.csv` |
| `primaryValue` | Trade value, current USD, aggregate (motCode=0, partner2Code=0, customsCode=C00. See `SOURCES.md` for why) |

**US and India absent**. See `LIMITATIONS.md` item 1.

## `data/processed/critical_materials_by_country.csv` / `critical_materials_concentration.csv` (USGS)

| Column | Notes |
|---|---|
| `material` | One of 13 selected materials. See `SOURCES.md` for selection criteria |
| `country` | 2023 mine (or refinery, for the two "(refined)" rows) production |
| `production_2023`, `share_pct` | Country's share of total tracked 2023 production |
| `HHI`, `CR3_pct`, `CR5_pct`, `top_producer`, `top_producer_share_pct` | Concentration summary, one row per material |

## `data/processed/supply_chain_risk_index.csv`

Four-pillar composite. See `python/analysis/risk_index.py` docstring for full pillar definitions and `LIMITATIONS.md` item 6 for the commodity-exposure pillar's known crudeness.

## `data/processed/risk_index_weight_sensitivity.csv` (added after external review)

Per-country rank and score at the 5th/50th/95th percentile across 1,000 random Dirichlet-weight draws on the risk index's four pillars, plus `rank_band_width`. Covers 48 of 59 countries (those with complete pillar data only). See `METHODOLOGY.md` and `LIMITATIONS.md` item 12.

## `data/processed/malaysia_*.csv` (multiple files)

- `malaysia_trade_headline_annual.csv`: DOSM, 2001-2025 exports/imports/balance
- `malaysia_trade_sitc_annual.csv`: DOSM, exports/imports by SITC section
- `malaysia_imports_by_bec_annual.csv`: DOSM, imports by Broad Economic Category
- `malaysia_top_suppliers_2016/2023.csv`, `malaysia_top_customers_2016/2023.csv`; UN Comtrade bilateral
- `malaysia_trade_concentration_summary.csv`: supplier/customer HHI, both periods
- `malaysia_asean_logistics_comparison.csv`; LPI vs. ASEAN-6
- `malaysia_critical_minerals_position.csv`; Malaysia's share of tracked USGS materials
- `malaysia_vulnerability_index.csv`; 5-dimension composite (see `MALAYSIA_FRAMEWORK.md`)
- `malaysia_opportunity_radar.csv`: 4 hypotheses, evidence-graded
- `malaysia_export_forecast_2026_2030.csv`, `malaysia_export_forecast_backtest.csv`. See `FORECASTING.md`
- `malaysia_export_forecast_stress_test.csv` (added after external review): baseline forecast plus three shock-scenario paths (H: recession, D: trade tension, G: energy shock band), 2026-2030. See `FORECASTING.md` and `python/forecasting/scenario_stress_test.py` docstring.

## `data/processed/commodity_prices_monthly.csv` / `commodity_price_volatility.csv`

World Bank Pink Sheet, 14 commodities, nominal USD, monthly. Volatility = annualised standard deviation of monthly log returns.

## `data/processed/nickel_monte_carlo_12m.csv`

Two bootstrap methods (independent, 6-month block), 10,000 simulations each. See `python/simulation/monte_carlo_nickel.py` docstring.

## `data/processed/trade_network_centrality.csv` / `trade_network_pagerank_change.csv`

Betweenness, eigenvector centrality, and PageRank per country per period (2016, 2023), computed on the 57-country bilateral network. See `python/networks/trade_network.py`.
