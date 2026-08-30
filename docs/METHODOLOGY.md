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

**Sensitivity analysis, upgraded after external review:** the original single-alternative-weighting check (equal weights vs. double-weighting one pillar, Spearman ρ) is a reasonable starting check but not a full sensitivity analysis on its own. The Supply Chain Risk Index now also runs a 1,000-draw weight-sensitivity Monte Carlo (`risk_index_weight_sensitivity.csv`, Visualisation 18): random weight vectors drawn from a symmetric Dirichlet(1,1,1,1) distribution (uniform over the simplex of all non-negative weight combinations summing to 1, so no pillar is privileged a priori), the composite score and full ranking recomputed under each draw, and the resulting Spearman ρ distribution and each country's rank range reported directly, rather than a single data point. This surfaced a genuinely more nuanced finding than the single-check version: Malaysia's risk rank is markedly less stable than its median position suggests (90% band: rank 6-41 of 56 complete-data countries, not a tight cluster around its base rank of 29), reported honestly rather than smoothed over. See `docs/LIMITATIONS.md` item 12 for the 56-vs-59-country caveat.

## Academic Grounding (Related Work)

This project's methods sit within, rather than invent, established quantitative traditions, added here explicitly after external review noted the absence of this grounding:

- **HHI as a concentration measure**: the Herfindahl-Hirschman Index and its conventional 2,500-point "highly concentrated" threshold follow the U.S. Department of Justice / Federal Trade Commission Horizontal Merger Guidelines convention, the standard reference point cited across both antitrust economics and critical-materials-supply literature.
- **Network centrality on trade data**: computing betweenness, eigenvector centrality, and PageRank on a directed trade-flow network follows the "world trade web" research tradition (e.g. Fagiolo, Reyes, and Schiavo's work on the topological properties of the international trade network, and De Benedictis and Tajoli's work specifically applying network-centrality measures to bilateral trade), which established that a country's structural position in the trade network is a distinct, measurable property from its raw trade volume, exactly the distinction this project's own UAE/Hong Kong finding (Insight 1 in the README) rests on.
- **Rolling-origin ("walk-forward") backtesting**: the forecasting validation approach (train on everything before year Y, forecast Y+1, roll forward, repeat) is the standard time-series cross-validation convention, preferred over a single train/test split specifically because it is not vulnerable to one lucky or unlucky split.

This project does not claim to extend this literature, only to apply its established conventions correctly and cite them, rather than presenting them as original methodological choices.

## Forecasting Validation

See `docs/FORECASTING.md` for the full model-comparison and backtest methodology.

## Network Construction

See `python/networks/trade_network.py`'s docstring for the directed-graph construction (export flows only, to avoid double-counting the same physical flow reported by both the exporter and importer) and centrality-measure definitions.

## Critical Materials Selection and Concentration Methodology

See `python/cleaning/clean_critical_materials.py`'s docstring for the 13-material selection criteria and the HHI/CR3/CR5 concentration calculation.

## Scenario Methodology

See `docs/SCENARIO_METHODOLOGY.md` for the full scenario-construction approach, including which assumptions are grounded in a real comparable event from this project's own data ("real anchor") versus illustrative.
