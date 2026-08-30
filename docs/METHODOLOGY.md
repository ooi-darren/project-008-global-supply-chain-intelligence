# Methodology

## Real vs. Nominal, Currency, and Comparability Discipline

- **GDP / income comparisons across countries**: PPP-adjusted (`gdp_per_capita_ppp_current_intl`), correcting for local price-level differences.
- **Market-size totals (trade values)**: nominal USD, since "how much trade flows through this economy" is inherently a nominal-currency question; cross-country nominal comparisons carry the usual exchange-rate caveat, stated explicitly wherever such a comparison is made.
- **Commodity prices**: kept nominal-USD deliberately, not inflation-deflated. See `LIMITATIONS.md` item 10 for why.
- **Malaysia's own trade series**: kept in DOSM's native currency (RM) since these are analysed as a single-country time series, not compared cross-country; converting to USD would introduce an unnecessary exchange-rate assumption.

## Regional Framework

Reuses this portfolio's Project 007 8-region classification (`data/external/REGION_MAPPING_project007.csv`) rather than building a second, potentially inconsistent regional framework; deliberate cross-project consistency, not a shortcut. See Project 007's own `docs/METHODOLOGY.md` for the full region-assignment methodology and documented overrides.

## Tool Selection

Per the brief's own "Tool Principle" (Section 27: "Never use a technology just to make the project look impressive... use the simplest tool capable of answering the research question rigorously"):

| Considered | Decision | Reasoning |
|---|---|---|
| **R** | Not used | Every analysis in this project (data cleaning, network science via NetworkX, forecasting via statsmodels, simulation via NumPy) has a mature, equally rigorous Python equivalent. Running two languages for one solo-authored project would add real maintenance/reproducibility overhead without adding analytical capability, the brief itself warns against tool choices made "to look impressive." |
| **SQL / DuckDB** | Not used | Data volumes here (thousands, not millions, of rows per table) do not need a query engine; pandas is simpler and equally rigorous at this scale. |
| **Power BI** | Not used | No licensed instance available in this environment. Static, sourced, reproducible charts (`outputs/figures/`) serve the same communicative function for a portfolio audience; the brief itself frames Power BI as "where appropriate," not mandatory. |
| **Docker / environment.yml / pyproject.toml** | Not used | `requirements.txt` matches the convention already established across every other repo in this portfolio; a solo reproducibility target does not need a second, redundant environment-pinning mechanism. |
| **NetworkX** | Used | Genuinely the right tool for the trade-network centrality analysis (Section 9), no simpler alternative computes betweenness/eigenvector centrality/PageRank correctly. |
| **statsmodels (ARIMA, ETS)** | Used | Needed for the forecasting model comparison (Section 16); a naive baseline alone would not satisfy the brief's explicit requirement to compare against real alternative models. |
| **GeoPandas** | Used | Needed for the choropleth maps (Visualisations 1, 4, 8); reused from Project 007's proven pattern. |

## Market Attractiveness / Risk Index Precedent

The Supply Chain Risk Index (`python/analysis/risk_index.py`) and Malaysia Vulnerability Index (`python/analysis/malaysia_vulnerability_opportunity.py`) both follow the exact transparent-index discipline established in this portfolio's Project 007 Market Attractiveness Index: equal-weighted pillars, min-max normalisation within the sample, retained sub-scores so a reader can recompute with different weights, and a documented sensitivity check (alternative weighting + Spearman rank correlation) rather than a single unexplained score. Full pillar definitions are in each script's own docstring, not duplicated here.

## Forecasting Validation

See `docs/FORECASTING.md` for the full model-comparison and backtest methodology.

## Network Construction

See `python/networks/trade_network.py`'s docstring for the directed-graph construction (export flows only, to avoid double-counting the same physical flow reported by both the exporter and importer) and centrality-measure definitions.

## Critical Materials Selection and Concentration Methodology

See `python/cleaning/clean_critical_materials.py`'s docstring for the 13-material selection criteria and the HHI/CR3/CR5 concentration calculation.

## Scenario Methodology

See `docs/SCENARIO_METHODOLOGY.md` for the full scenario-construction approach, including which assumptions are grounded in a real comparable event from this project's own data ("real anchor") versus illustrative.
