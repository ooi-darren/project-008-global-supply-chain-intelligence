# Limitations

Professional research does not hide its limitations. This document is deliberately thorough, following the same standard as this portfolio's other case studies.

## 1. The United States and India Are Absent from the Bilateral Trade Network

Verified directly, not assumed (see `docs/SOURCES.md` for the exact test): UN Comtrade's free/unauthenticated "preview" tier excludes the United States and India entirely from bilateral trade data, both as reporter and as partner in every other country's reported data. This means the trade network, network centrality analysis, and Malaysia's supplier/customer concentration figures are built on a **57-country bilateral network** (59 minus these two), even though the project's broader country-level analyses (trade openness, logistics, the risk index, GDP) fully include both: those come from World Bank data, an unrelated source unaffected by this restriction.

**Consequence:** any claim in this project about "who Malaysia's top suppliers/customers are" or "which countries are the most central network nodes" should be read as "...among the 57-country bilateral network," not as a claim that the US and India are unimportant; they plausibly rank highly on both measures in reality, this project simply cannot compute their bilateral figures from a free-tier source. Malaysia's real trade with the US (historically a top-3 export market) is present in Malaysia's own DOSM headline figures, just not broken into the bilateral network's centrality metrics.

## 2. The Network Is 59 (Practically 57) Economies, Not All ~200

The full UN Comtrade universe covers roughly 200 reporting economies. This project deliberately limits the bilateral network to the top-10-by-GDP economies per region (Project 007's 8-region framework), reasoning that a full 200×200 matrix at the free-tier ~1 request/second rate limit would take many hours and add mostly very-small-economy noise rather than analytical value. This is the same "meaningful coverage over exhaustive coverage" principle applied throughout this portfolio (e.g. Project 007's 182-country panel deliberately excluding negligible-trade micro-states).

## 3. Two Points in Time, Not a Full Annual Series, for the Bilateral Network

The bilateral network uses 2016 and 2023 specifically (pre-COVID baseline vs. most recent complete year) rather than every year in between, for the same rate-limit-budget reason as above. The World Bank-sourced country-level panel (2013-2025 annual) is used for the historical trend/structural-change timeline instead, where a full annual series matters more than bilateral detail.

## 4. Shipping-Route / AIS Data Was Not Used

The brief explicitly permits investigating "legally accessible" AIS/satellite vessel-tracking data. Genuine AIS feeds at any meaningful global coverage are commercial products this project does not have paid access to, and the brief explicitly says not to use restricted data. Visualisation 9 ("shipping route analysis") is substituted with container port traffic by country (World Bank, real PUBLIC data), a real but coarser proxy for shipping-route exposure, labelled as a substitution in the chart itself, not presented as route-level data it is not.

## 5. Malaysia Sub-National (State/Cluster) Analysis Was Not Built

Section 20 of the brief asks for state/cluster-level analysis (Northern Corridor, Klang Valley, etc.) where data is available. No freely-accessible, sufficiently granular state-level manufacturing/logistics/trade dataset was found within this project's research window that would support a genuine, evidence-based state-level vulnerability or opportunity claim (as opposed to a plausible-sounding but unverified one). Rather than force a weak proxy, this layer is named here as not built, consistent with the brief's own instruction: "Do NOT assume a region is strategically important without evidence."

## 6. The Commodity-Exposure Pillar of the Country Risk Index Is Deliberately the Crudest

The four-pillar Supply Chain Risk Index's commodity-price-exposure pillar uses a single global average commodity-volatility figure applied uniformly to every country, not a country-specific figure weighted by that country's actual export commodity mix (which would need an HS-level export-composition dataset by country this project does not have at the necessary granularity for all 59 economies). Named explicitly in the index's own methodology (`docs/METHODOLOGY.md`) as the weakest of the four pillars, not disguised as country-specific.

## 7. Malaysia's Own Critical-Minerals Import Reliance Is Proxied, Not Directly Measured

The Malaysia Vulnerability Index substitutes DOSM's BEC "intermediate + capital goods" share of retained imports for a true commodity-level import-dependency measure (which would need an HS-code-level Malaysia import breakdown this project did not pull, to avoid a third large data-collection detour on top of the trade network and critical materials work already completed). This is a real, Malaysia-specific measure of production-input exposure, just not the literal "which specific critical mineral does Malaysia import how much of" figure a fuller version of this project would build.

## 8. Forecasting Covers One Series in Depth, Not Every Variable Listed in the Brief

Section 16 lists many candidate forecast targets (trade, exports, imports, commodity demand/supply, port throughput, shipping demand, manufacturing indicators). This project forecasts one (Malaysia's annual exports) but does so with genuine rigour: four models compared, a 5-year rolling backtest (not a single train/test split), and an honest result (the naive-with-drift baseline beat both ARIMA and ETS on backtest RMSE, reported as such per the brief's explicit instruction not to hide a poor model result). Depth on one series was prioritised over shallow point-forecasts on many.

## 9. Scenarios Are Structured Reasoning, Not Probability-Weighted Predictions

Every scenario in `docs/SCENARIO_METHODOLOGY.md` is explicitly qualitative-to-semi-quantitative, grounded in this project's own data where a real comparable exists (labelled "real anchor") and explicitly marked illustrative where none does. No scenario carries a stated probability. The Malaysia 2030+ scenario impact scores (Visualisation 14) are a documented judgment call, not a model output, stated as such in the chart's own footnote.

## 10. Currency and Price-Level Discipline

Commodity prices are kept nominal-USD (not inflation-deflated) deliberately, since deflating would obscure the actual shock magnitude this project needs to see (e.g. the real 2022 gas-price spike). GDP and trade-value comparisons across countries use PPP where the comparison is about income levels and nominal USD where the comparison is about market size, following the same discipline established in this portfolio's Project 007. Malaysia's own export/import figures are in the currency DOSM itself publishes them in (RM), not converted, to avoid introducing an extra exchange-rate assumption into a series that is analysed as its own time series, not compared cross-country.

## 11. What This Project Does Not Claim

This project does not claim to have identified every material or country that matters, does not claim its 13-material or 59/57-country selections are the only defensible choices, and does not claim any forecast or scenario would replicate identically with a different reasonable methodological choice. It claims to have applied a transparent, reproducible, evidence-based methodology to real public data, verified its own pipeline against known real-world facts wherever possible (China's rare-earth dominance, DRC's cobalt dominance, Singapore's ASEAN logistics lead, Indonesia's nickel rise all appear correctly in this project's own output), and to report honestly where that methodology's limits are.
