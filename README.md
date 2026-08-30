# Project 008: Global Supply Chain Intelligence

### Trade Networks, Logistics, Critical Resources, Supply Risk & Future Scenarios

<img src="./outputs/figures/02_global_trade_network.png" width="800" alt="The 59-economy global trade network, hubs are large economies but not necessarily central ones">

**Part of an [8-case-study portfolio](https://github.com/ooi-darren)**, the second global-scope project, and the first to combine trade flows, critical-materials supply, network science, and forecasting into one system.

> Understanding how the world moves, identifying where supply chains are vulnerable, and assessing where they may go next, with a Malaysia 2030+ deep dive.

## Research Question

**How has the global supply-chain system changed over the past decade, what is happening now, where are the major dependencies and vulnerabilities, and what could happen over the next 5-10 years under different scenarios? And what do these changes mean for Malaysia specifically?**

## Key Findings

**1. Network importance and raw trade volume are not the same thing.** Between 2016 and 2023, the UAE gained the most network importance of any economy (+29% PageRank), followed by China (+5%), Poland, Turkiye, Saudi Arabia, and Vietnam, a real, data-driven signature of the "China+1" diversification and Gulf-diversification narratives, not an assumption. The UK (-26%), Hong Kong (-21%), Singapore (-26%), and Japan (-17%) lost the most network importance over the same window.

**2. Four materials are highly concentrated by any standard measure.** Gallium (China, 98% of world mine production, HHI=9,626), Tungsten (China, 84%, HHI=7,166), Graphite (China, 79%, HHI=6,314), and Cobalt (DR Congo, 76%, HHI=5,822) are all far above the standard "highly concentrated" HHI threshold of 2,500. Nickel (Indonesia, 60%, HHI=3,837) is a genuine, currently unfolding case of concentration rising fast on the back of Indonesia's export/downstreaming policy.

**3. Malaysia's own trade partner concentration rose, not fell, 2016→2023**: supplier HHI from 1,125 to 1,202, customer HHI from 915 to 975. Both remain in the "unconcentrated" range (below 1,500) but the direction runs against a simple "diversification" narrative one might assume from "China+1" headlines.

**4. China is Malaysia's single largest supplier (27.2% of imports, 2023) and second-largest customer (17.4%, behind Singapore's 19.8%).** Both figures come directly from bilateral UN Comtrade data, not an assumption.

**5. A validated backtest, not a dramatic model, wins the Malaysia export forecast.** Four models were compared on a genuine 5-year rolling backtest; the simple naive-with-drift baseline beat both ARIMA and ETS on out-of-sample RMSE, reported honestly per this project's own research-integrity standard rather than hidden. Forward forecast: RM 1.87 trillion by 2030 (90% band: RM 1.53-2.21 trillion).

**6. Malaysia ranks 30th of 59 economies on this project's Supply Chain Risk Index**, mid-pack, not a standout on either end. The highest-risk economies (Cuba, Mongolia, Iraq, Hong Kong, Macao) share small/concentrated/geopolitically-exposed profiles; the lowest-risk (Germany, Canada, China, Japan, France) are large, diversified, logistically strong economies.

**7. Malaysia's imports are 86% production inputs, not final consumption** (capital + intermediate goods share of retained imports, DOSM BEC data, 2025), direct evidence that Malaysia is deeply embedded in upstream manufacturing supply chains, not primarily an import-for-consumption economy.

**8. A real Monte Carlo, not an invented one.** A 10,000-simulation, historical-bootstrap 12-month nickel price simulation gives a 25-27% probability of a >20% price increase and a 13-17% probability of a >20% decrease, with two independent bootstrap methods agreeing to within 0.6% of the median, probabilities derived from nickel's actual 798-month price history, not assumed.

## Explain It Simply

Imagine every country in the world as a person in a giant trading network, buying things from some people and selling things to others. This project asks: has that network of buying and selling changed a lot in the last ten years? What's happening in it right now? And if something goes wrong somewhere in it, who gets hurt?

Three things this project found that matter for everyone, not just economists:

- **A few countries make almost all of some critical materials.** Nearly all the world's gallium (used in chips) comes from China. Most cobalt (used in EV batteries) comes from one country, DR Congo. If either country had a problem, a lot of the world's electronics and EV supply chains would feel it fast; this project measured exactly how concentrated each material really is, not just repeated the headline.
- **Being "connected" to the trade network matters as much as being "big."** A country can trade a huge amount of stuff and still not be a particularly *important* node in the network; this project used the same kind of network math that powers things like Google's search ranking (PageRank) to measure this properly, and found some real surprises: the UAE's importance in the network jumped nearly 30% in just seven years.
- **Malaysia buys from and sells to a lot of different countries, but China matters most on both sides**: Malaysia's single biggest supplier and second-biggest customer, confirmed directly from real UN trade data, not assumed from news headlines.

This project also makes a forecast about Malaysia's exports out to 2030, and honestly reports that the simplest possible forecasting method (just "keep growing at the recent average rate") beat two much fancier statistical models when tested properly, which is itself a useful, honest finding. (New to terms like "HHI," "PageRank," or "Monte Carlo"? See the Glossary near the bottom.)

## Why This Matters

Businesses and policymakers routinely make claims about supply-chain "resilience," "diversification," or "critical dependency" without the underlying network, concentration, or forecast evidence to back them up. This project builds that evidence base directly from real trade, materials, and logistics data, with every claim traced to its source and every limitation stated plainly, the same standard as every other case study in this portfolio.

## Global Supply Chain: What Changed Since 2016, What's Happening Now

The full historical review (2016-2019 pre-COVID baseline, 2020-2022 COVID shock, 2022-2024 geopolitical/logistics shock period, 2025-2026 current environment) and the structural-change classification (temporary vs. cyclical vs. structural vs. strategic vs. technological vs. geopolitical vs. environmental) are in `notebooks/02_historical_changes.ipynb`. The headline evidence: median trade openness across tracked economies and the 2016→2023 network-importance shifts above are the two clearest, most directly measurable signals this project can support with real data, shown in Visualisation 12.

## Regional Analysis

Europe and East Asia dominate merchandise export volume among tracked economies (Visualisation 3); full regional profile methodology reuses this portfolio's Project 007 8-region framework for cross-project consistency.

## Country / Market Analysis

Country-level import dependency, logistics fragility, trade concentration, and the combined Supply Chain Risk Index are in `data/processed/supply_chain_risk_index.csv` (Visualisations 4, 5, 10); full methodology in `docs/METHODOLOGY.md`.

## Critical Raw Materials

13 materials tracked (selection criteria in `docs/SOURCES.md`), concentration computed via HHI/CR3/CR5 on real 2023 USGS production data. Four materials (Gallium, Tungsten, Graphite, Cobalt) are highly concentrated by the standard 2,500-HHI threshold; Nickel is the clearest live case of rapidly rising concentration (Visualisation 6).

## Trade Network Analysis

57-country bilateral network (United States and India structurally excluded from the free-tier data source. See `docs/LIMITATIONS.md`), betweenness/eigenvector centrality and PageRank computed via NetworkX, compared 2016 vs. 2023 (Visualisations 2, 11). Full network-importance gainers/losers table: `data/processed/trade_network_pagerank_change.csv`.

## Logistics Intelligence

World Bank Logistics Performance Index (overall + 3 sub-components) and container port traffic, compared globally (Visualisations 8, 9) and specifically across ASEAN-6 for the Malaysia deep dive.

## Supply Chain Risk

Four-pillar transparent composite (import dependency, logistics fragility, trade-partner concentration, commodity-price exposure), equal-weighted, min-max normalised, with a documented sensitivity check (Spearman ρ=0.976 against a concentration-double-weighted alternative). Full methodology: `docs/METHODOLOGY.md`.

## Future Scenarios

Two distinct tools, kept clearly separate: 8 discrete shock simulations (Section 14-style: a route closes, a supplier exits, a tariff hits) each traced SHOCK→SUPPLY→PRICE→LOGISTICS→PRODUCTION→TRADE→INDUSTRY→COUNTRY→CONSUMER, and 8 Malaysia 2030+ macro-strategic scenarios, each assessed for global/ASEAN/Malaysia impact. Full write-up, including which assumptions are grounded in a real comparable event versus illustrative: `docs/SCENARIO_METHODOLOGY.md` (Visualisation 14).

## Forecasting

Malaysia annual exports, 2001-2025 actual, forecast to 2030. Four models compared on a genuine 5-year rolling backtest (not a single train/test split); naive-with-drift won, reported honestly rather than hidden. Full methodology: `docs/FORECASTING.md` (Visualisation 13).

## Malaysia Deep Dive 🇲🇾

Malaysia is a dedicated strategic case study, not an appendix: full framework in `docs/MALAYSIA_FRAMEWORK.md`. Covers: import/export composition (DOSM), bilateral supplier/customer concentration (UN Comtrade), ASEAN-6 logistics comparison (World Bank LPI), critical-minerals position (USGS), a 5-dimension Vulnerability Index, and an evidence-graded Opportunity Radar (Visualisations 15, 16, 17).

## Malaysia 2030+ Opportunities & Risks

**Strongly evidenced opportunities:** electronics/semiconductor assembly-test-packaging (Malaysia's largest real export category, 50.3% of exports by SITC section) and regional logistics hub positioning (2nd-highest LPI in ASEAN-6, behind only Singapore). **Weakly evidenced / speculative:** critical-minerals processing (Malaysia's own production share is under 2.3% for every tracked material; any real opportunity would be processing imported feedstock, not a domestic resource advantage). **Not evidenced by this project:** data-centre/digital-infrastructure investment (no direct dataset collected, a named gap, not a claim either way). Full evidence grading: `data/processed/malaysia_opportunity_radar.csv`.

## Key Strategic Insights

1. **Network importance and raw trade volume diverge**: a market-entry or partnership strategy built purely on "biggest trading partners" will miss real structural shifts (the UAE's rising centrality, Hong Kong's falling centrality) that PageRank-style analysis catches and simple export-value ranking does not.
2. **Malaysia's rising (not falling) trade concentration is worth watching, not assuming away**: the "diversification" story implied by China+1 headlines does not show up in Malaysia's own supplier/customer HHI trend over 2016-2023.
3. **A validated, boring forecast beats an exciting, unvalidated one**; this project's own backtest discipline is itself a transferable lesson for any business forecasting exercise: test before trusting a more sophisticated model.

## Methodology

Full write-up: [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md). In brief: PPP-adjusted GDP for income comparisons, nominal USD for market-size totals, nominal (non-deflated) commodity prices to preserve real shock magnitude, Python-only (no R/Power BI/Docker, documented "simplest tool" reasoning), the same transparent equal-weighted composite-index discipline established in this portfolio's Project 007.

## Data Sources

World Bank, UN Comtrade, USGS Mineral Commodity Summaries 2025, World Bank Commodity Markets (Pink Sheet), DOSM; full citations and three genuine data-quality discoveries (not assumptions) in [`docs/SOURCES.md`](docs/SOURCES.md).

## Notebooks

| # | Question | Data Rigor |
|---|---|---|
| [01: Global Trade](./notebooks/01_global_trade.ipynb) | What does the global trade network actually look like, and who are the real hubs? | PUBLIC |
| [02: Historical Changes](./notebooks/02_historical_changes.ipynb) | What changed structurally in global supply chains since 2016? | PUBLIC |
| [03: Regional Analysis](./notebooks/03_regional_analysis.ipynb) | Which regions are gaining or losing trade importance? | PUBLIC |
| [04: Country Analysis](./notebooks/04_country_analysis.ipynb) | Who depends on whom, and how concentrated is that dependency? | PUBLIC + DERIVED |
| [05: Critical Materials](./notebooks/05_critical_materials.ipynb) | Which raw materials are genuinely supply-concentrated, and by how much? | PUBLIC + DERIVED |
| [06: Network Analysis](./notebooks/06_network_analysis.ipynb) | Which countries are structurally central, not just big traders? | PUBLIC + DERIVED |
| [07: Risk & Forecasting](./notebooks/07_risk_and_forecasting.ipynb) | Where is supply-chain risk concentrated, and what does a validated forecast say about Malaysia's exports? | PUBLIC + DERIVED |
| [08: Malaysia Deep Dive](./notebooks/08_malaysia_deep_dive.ipynb) | What does all of this mean specifically for Malaysia? | PUBLIC + DERIVED |

## Limitations

Full document: [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md). Headline items: the United States and India are structurally absent from the free-tier bilateral trade data (verified directly, not assumed); the network covers 59 (practically 57) major economies, not the full ~200; AIS/shipping-route data was not used (commercial/restricted, substituted with container port traffic); Malaysia sub-national analysis was not built (no sufficiently granular free data found); the risk index's commodity-exposure pillar is deliberately the crudest of its four pillars, named as such.

## Glossary

Plain-language definitions for the technical terms used in this project.

- **Supply chain:** The full chain of suppliers, factories, and shipping routes that turns raw materials into a finished product a business or consumer buys.
- **Trade dependency:** How much a country relies on other countries for a good, either as a source (import dependency) or a market (export dependency).
- **HHI (Herfindahl-Hirschman Index):** A standard measure of how concentrated a market is among a few players, the sum of each player's market-share-squared. Above 2,500 is conventionally considered "highly concentrated."
- **Critical minerals:** Raw materials (like lithium, cobalt, or rare earths) that are essential for modern technology (batteries, chips, magnets) and where supply is often concentrated in just a few countries.
- **Network centrality:** A family of measures (betweenness, eigenvector, PageRank) for how structurally important a node is in a network, not the same as how big or busy it is.
- **PageRank:** The same core algorithm Google originally used to rank web pages, applied here to rank countries by how much they're connected to *other well-connected* countries, not just by raw trade volume.
- **Resilience / Vulnerability:** How well (resilience) or poorly (vulnerability) a system can absorb a shock without breaking down.
- **Scenario:** A structured "what if" story about how the future could unfold, built from explicit assumptions, not a prediction.
- **Forecast:** An actual quantitative estimate of a future value, built from a validated model: different from a scenario, and always reported with its own uncertainty.
- **Monte Carlo simulation:** Running a model thousands of times with randomly varied inputs (drawn from real historical data, in this project) to see the full range of possible outcomes, not just one guess.
- **CAGR (Compound Annual Growth Rate):** The average yearly growth rate of something over several years, as if it grew at one smooth, steady pace.
- **PUBLIC / DERIVED / ESTIMATED:** How traceable a number in this project is. **PUBLIC** = taken directly from an official source. **DERIVED** = built by combining or calculating from official sources this project directly fetched. **ESTIMATED** = based on a secondary source that couldn't be independently verified. See [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md).

## Reproducibility

```bash
pip install -r requirements.txt

# 1. Collect raw data
python python/data_collection/world_bank.py
python python/data_collection/comtrade_network.py    # ~5-10 min, rate-limited to ~1 req/sec

# 2. Clean and build processed datasets
python python/cleaning/build_master_panel.py
python python/cleaning/clean_critical_materials.py
python python/cleaning/clean_commodity_prices.py
python python/cleaning/clean_malaysia_trade.py

# 3. Run the analysis layer
python python/networks/trade_network.py
python python/analysis/risk_index.py
python python/analysis/malaysia_deep_dive.py
python python/analysis/malaysia_vulnerability_opportunity.py

# 4. Forecasting and simulation
python python/forecasting/forecast_malaysia_exports.py
python python/simulation/monte_carlo_nickel.py

# 5. Generate all 17 visualisations
python python/visualisation/make_charts.py

# 6. Walk through the narrative notebooks
jupyter notebook notebooks/
```

All raw and processed data is committed to this repository (every source's licence permits redistribution. See `docs/SOURCES.md`), so steps 2-6 can be run directly without re-fetching from any API.

## Project Structure

```
project-008-global-supply-chain-intelligence/
├── README.md
├── data/
│   ├── raw/            # World Bank, UN Comtrade, USGS, DOSM, Pink Sheet pulls, unmodified
│   ├── processed/       # Cleaned panels, indices, forecasts, network tables
│   └── external/         # Region mapping, country-code reference, boundaries
├── notebooks/            # 01-08, narrative walkthrough of the python/ pipeline
├── python/
│   ├── data_collection/  # World Bank + UN Comtrade API clients
│   ├── cleaning/          # Master panel, critical materials, commodity prices, Malaysia trade
│   ├── analysis/           # Risk index, Malaysia deep dive & vulnerability/opportunity
│   ├── networks/            # Trade network centrality
│   ├── forecasting/          # Malaysia export forecast + backtest
│   ├── simulation/            # Nickel Monte Carlo
│   └── visualisation/          # House chart style + all 17 chart builders
├── outputs/
│   ├── figures/            # 17 PNG visualisations
│   └── tables/               # (chart-ready summary tables, where applicable)
├── docs/
│   ├── METHODOLOGY.md
│   ├── DATA_DICTIONARY.md
│   ├── DATA_COVERAGE.md
│   ├── DATA_QUALITY.md
│   ├── SOURCES.md
│   ├── SOURCE_HIERARCHY.md
│   ├── LIMITATIONS.md
│   ├── FORECASTING.md
│   ├── SCENARIO_METHODOLOGY.md
│   └── MALAYSIA_FRAMEWORK.md
├── requirements.txt
├── LICENSE
└── .gitignore
```

## Sources

Full citations: [`docs/SOURCES.md`](docs/SOURCES.md).

## Author

Darren Ooi, [LinkedIn](https://www.linkedin.com/in/darrenooizhixian)
