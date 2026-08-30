# Scenario Methodology

Full transparency on how every scenario in this project was built: what it assumes, what evidence grounds it, and what it deliberately does not claim. Per the brief's own instruction: these are not predictions. "The scenario suggests," not "this will happen."

## 1. Two Different Kinds of Scenario in This Project

This project builds two distinct scenario tools, kept clearly separate:

1. **Shock simulations** (Section 14 of the original brief): a specific, discrete disruption event (a route closes, a supplier exits, a tariff hits) traced through to its downstream effects. These are structured thought experiments grounded in the magnitude of real historical shocks already observed in this project's own data (COVID-era freight-rate spikes, the 2022 gas-price shock, China's 2023-2025 gallium/rare-earth export actions).
2. **Malaysia 2030+ scenarios** (Section 23): broader macro-strategic futures for how the global trading system could evolve over the next 5-10 years, and what each implies for Malaysia specifically.

Neither is a forecast. The forecasting layer (see `docs/FORECASTING.md`) is the only place this project produces an actual point estimate with a validated backtest; scenarios are qualitative-to-semi-quantitative structured reasoning, explicitly labelled as assumption-driven throughout.

## 2. Shock Simulation Scenarios

Each scenario follows the brief's required chain: SHOCK → SUPPLY → PRICE → LOGISTICS → PRODUCTION → TRADE → INDUSTRY → COUNTRY → CONSUMER. Magnitude assumptions are anchored to a real comparable event from this project's own data wherever one exists, cited explicitly; where no comparable exists, the assumption is labelled illustrative.

| Scenario | Shock | Magnitude anchor | Most exposed (this project's data) |
|---|---|---|---|
| A. Major shipping-route disruption | A key chokepoint (e.g. a Red-Sea-style route) closes for 6+ months | Real anchor: European natural gas volatility hit ~47% annualised in the 2022 energy shock (`commodity_price_volatility.csv`); comparable magnitude used as the freight-rate-shock illustration | Countries with high logistics-fragility scores and high trade/GDP ratios in `supply_chain_risk_index.csv` |
| B. 10% raw-material supply reduction | A top producer cuts output 10% | Illustrative, no directly comparable single-country production cut of this size observed in the USGS 2023-2024 data window | Materials with the highest HHI in `critical_materials_concentration.csv` (Gallium, Tungsten, Graphite, Cobalt) |
| C. Major supplier exits market | A top-3 exporter for a given product effectively stops exporting | Real anchor: this is structurally what China's 2023-2025 gallium/germanium export licensing regime already represents for those two materials | Any country importing heavily from a single dominant supplier, per the network's export-partner HHI |
| D. Tariff escalation | Broad-based tariff increase between two major blocs | Illustrative, scaled to the trade-value reduction implied by the 2018-2019 US-China tariff episode's documented effect on bilateral trade shares | Countries with high bilateral concentration on the two blocs involved |
| E. Critical-mineral export restriction | An export licensing/quota regime on a specific material | Real anchor: China's actual 2023-2025 gallium, germanium, and graphite export control actions | Downstream semiconductor/EV-battery-dependent economies |
| F. Port disruption | A major container port closes or is severely congested for weeks | Illustrative, informed by the documented 2021-2022 global port congestion episode covered in this project's historical review | Countries most reliant on the affected port's throughput share, per World Bank container-port-traffic data |
| G. Energy price shock | A sustained 50%+ spike in a benchmark energy price | Real anchor: European natural gas price rose from its multi-year baseline to the 46.7% recent-3-year annualised volatility level directly measured in `commodity_price_volatility.csv` | Energy-import-dependent economies with low domestic production |
| H. Global recession | A broad-based demand contraction | Illustrative, scaled against the 2020 COVID trade contraction documented in the historical review notebooks | Export-concentrated economies with few alternative demand markets |

**What this table is not:** a probability estimate for any of these events, and not a claim that the "magnitude anchor" event will repeat. It is a documented basis for choosing a shock size grounded in something real rather than an arbitrary round number.

## 3. Malaysia 2030+ Scenarios

Eight macro-strategic futures, each assessed for global impact, ASEAN impact, Malaysia impact, and strategic response. Built from the structural-change evidence in this project (Notebooks 02-03) plus the concentration, logistics, and forecasting outputs, not from external forecasts this project cannot verify.

1. **Globalisation Rebounds**: trade openness returns toward pre-2018 trend levels. Malaysia impact: broadly positive given its high trade/GDP ratio and 2nd-place ASEAN logistics position; risk of complacency on supply-chain diversification already underway.
2. **Asian Regionalisation**: intra-Asian trade deepens faster than global trade (a pattern this project's network centrality analysis can directly test: rising PageRank for East/Southeast Asian nodes 2016→2023 would be first-order evidence for this already happening). Malaysia impact: likely positive, reinforces its existing electronics-supply-chain position within Asia.
3. **China+1 Accelerates**: firms continue diversifying manufacturing capacity away from sole China dependence. Malaysia impact: positive for electronics/semiconductor assembly and packaging, Malaysia's largest real export category; risk of overheating specific industrial clusters without matching infrastructure/talent investment.
4. **Geopolitical Fragmentation**: trade blocs harden, export controls widen beyond critical minerals. Malaysia impact: negative for a small, trade-dependent, non-aligned economy caught between blocs; the country's high trade/GDP ratio (`supply_chain_risk_index.csv`) is a direct vulnerability under this scenario specifically.
5. **Critical Resource Shortage**: a genuine supply-demand gap emerges in one or more battery/semiconductor-critical materials. Malaysia impact: mixed; minimal direct exposure as a producer (Malaysia's own mine-production share is under 2.3% for every tracked material per USGS), but real exposure as a downstream electronics manufacturer dependent on imported feedstock.
6. **AI / Semiconductor Boom**: sustained high demand for advanced packaging, testing, and data-centre-adjacent manufacturing. Malaysia impact: the most directly positive scenario for Malaysia's current real export structure (electronics already the dominant SITC category); the opportunity radar (`malaysia_opportunity_radar.csv`) rates this the strongest-evidenced opportunity.
7. **Major Logistics Disruption**: a Shock-Simulation-Scenario-A/F-style event becomes a recurring rather than one-off condition. Malaysia impact: partially buffered by its strong (2nd in ASEAN) logistics infrastructure score, but its high trade/GDP ratio still means large absolute exposure.
8. **Climate Stress**: more frequent extreme-weather disruption to agriculture, energy, and logistics. Malaysia impact: under-evidenced by this project specifically (no climate/disaster dataset was collected, a named limitation, not a claim either way).

## 4. Scenario Matrix (Supply × Demand)

A simple 3×3 framework, used specifically for the materials most exposed under Shock Scenario B/E (Gallium, Cobalt, Graphite, Tungsten, the four highest-HHI materials in `critical_materials_concentration.csv`):

```
                              DEMAND
                    LOW           BASE           HIGH
SUPPLY   LOW      Price falls,   Tightening,     Acute deficit risk,
                  low stress     price rises      price spike
         BASE     Oversupply,    Current          Gradual
                  price soft     trajectory       tightening
         HIGH     Oversupply     Comfortable      Absorbs demand
                  persists       surplus          growth without stress
```

Base-case placement for each of the four highest-concentration materials is qualitative (grounded in the demand-growth narrative already established in the EV/battery and AI/semiconductor literature this project's "Why Is This Happening" research draws on), not a quantified supply-demand-gap model, a full quantified version would require production-growth-pipeline data (announced new mining/refining capacity by year) this project did not collect. Named explicitly as a scope limitation in `docs/LIMITATIONS.md`.

## 5. What These Scenarios Are Not

- Not probability-weighted. No scenario here carries a stated likelihood.
- Not mutually exclusive. Several could partially co-occur (e.g. Asian Regionalisation and China+1 Accelerating are complementary, not competing, stories).
- Not a substitute for the forecasting layer's validated point estimates. Where this project makes an actual quantitative prediction (Malaysia's exports to 2030), that lives in `docs/FORECASTING.md` with a backtest, not here.
