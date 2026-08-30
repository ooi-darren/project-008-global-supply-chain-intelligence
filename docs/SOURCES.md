# Sources

Full citations for every dataset used in Project 008. See `DATA_DICTIONARY.md` for how each was used and `DATA_COVERAGE.md` / `DATA_QUALITY.md` for coverage and known gaps. See `SOURCE_HIERARCHY.md` for how sources were evaluated and prioritised.

## Primary trade network source: UN Comtrade

**Publisher:** UN Comtrade (UN Statistics Division) | **Access:** `comtradeapi.un.org/public/v1/preview/...` (the free/unauthenticated "preview" tier, the full `data/v1/` API returns HTTP 401 without a paid or registered subscription key, verified directly) | **License:** UN Comtrade data is freely reusable with attribution | **Date accessed:** 2026-08-30

Covers total bilateral (reporter-partner) merchandise trade for a 59-major-economy network (`data/external/network_countries.csv`, built as the top-10-by-GDP economies per Project 007's region framework, minus small non-sovereign/negligible-trade entities), for 2016 (pre-COVID baseline) and 2023 (most recent complete year), export and import flows. Fetch script: `python/data_collection/comtrade_network.py`.

**Genuine data-quality discoveries made building this, all verified and fixed, not assumed** (full detail in the script's own docstring):
1. Rows are split by `motCode` (transport mode): `motCode=0` is the aggregate, non-zero values are its breakdown. Summing all values double-counts.
2. Rows are independently split by `partner2Code` (re-export/transit country) for detailed reporters like China: `partner2Code=0` is the direct/aggregate total.
3. Rows are independently split by `customsCode` (customs procedure regime) for detailed reporters like Spain and Germany: `customsCode=C00` is the aggregate.
All three are passed as explicit server-side filter parameters (`motCode=0&partner2Code=0&customsCode=C00`) rather than requested-then-filtered, which also avoids a real truncation bug: China's full unfiltered response hits the API's ~500-row page cap before its aggregate rows appear, so a client-side-only filter would have silently returned zero data for China specifically.

**Known coverage gap, verified directly, not assumed:** the **United States and India are absent from this free-tier endpoint entirely, both as reporter and as partner in every other country's data.** Tested directly: a bare USA-as-reporter total query returns zero rows for both 2016 and 2023; separately, China's own reported exports (54 partner countries returned) never include USA or India as a partner, even though China-USA trade is among the largest bilateral relationships in the world. This is consistent with a deliberate feature restriction of the free/unauthenticated preview tier (reserving these two economies' data for the paid API), not a data availability problem with UN Comtrade itself. **Effect on this project:** the bilateral trade network and Malaysia-specific supplier/customer concentration analysis are built on a 57-country network in practice (all 59 minus USA and India for bilateral edges specifically); both countries remain fully present in every World Bank-sourced analysis (trade openness, logistics, GDP, the country-level risk index), since that is an unrelated data source unaffected by this restriction. See `LIMITATIONS.md`.

## World Bank Open Data

**Publisher:** World Bank | **Access:** `api.worldbank.org/v2` (public REST API, no authentication) | **License:** CC-BY 4.0 | **Date accessed:** 2026-08-30

17 indicators, 2013-2025, ~217 economies: trade openness, merchandise exports/imports, high-tech export share, Logistics Performance Index (overall + 3 sub-components), container port traffic, air/rail freight, GDP (current, growth, PPP per capita), inflation, exchange rate. Fetch script: `python/data_collection/world_bank.py`. Same reproducible pattern as this portfolio's Project 007.

## USGS Mineral Commodity Summaries 2025

**Publisher:** U.S. Geological Survey, National Minerals Information Center | **Access:** ScienceBase data release, DOI [10.5066/P13XCP3R](https://doi.org/10.5066/P13XCP3R), file `World_Data_Release_MCS_2025.zip` | **License:** U.S. Government work, public domain | **Date accessed:** 2026-08-30

World mine/refinery production (2023 actual + 2024 estimate), plant capacity, and reserves by country, for 90+ nonfuel mineral commodities. This project uses 13 materials selected against four documented criteria (semiconductor relevance, EV/battery relevance, independently well-known supply concentration, direct Malaysia relevance). See the full methodology in `python/cleaning/clean_critical_materials.py`'s docstring. Cleaning required a real fix: the COUNTRY column mixes genuine countries with aggregate labels like "World total (rounded)" and "World total (ilmenite and rutile, rounded)" (11 distinct variant labels found across the file), an exact-match exclusion list silently missed most of them on the first pass (every material's "top producer" was wrongly computed as "World total" at ~50% share); fixed with a substring-pattern exclusion instead.

## World Bank Commodity Markets ("Pink Sheet")

**Publisher:** World Bank | **Access:** `thedocs.worldbank.org`, monthly XLSX download | **License:** CC-BY 4.0 | **Date accessed:** 2026-08-30

Monthly nominal-USD prices for 70+ commodities, 1960-present (through July 2026 at time of access). Used for price volatility (a pillar of the risk index), the nickel Monte Carlo simulation, and forecast-target grounding. Kept nominal (not inflation-deflated) deliberately. See `docs/METHODOLOGY.md` for why.

## DOSM (Department of Statistics Malaysia) / OpenDOSM

**Publisher:** DOSM | **Access:** `storage.dosm.gov.my/trade/*.parquet` (direct parquet download, no authentication) | **License:** CC-BY 4.0 | **Date accessed:** 2026-08-30

Three datasets: `trade_headline` (monthly exports/imports/balance, 2000-2026), `trade_sitc_1d` (monthly exports/imports by SITC section, 2000-2026), `trade_enduse_bec` (monthly retained imports by Broad Economic Category (capital/intermediate/consumer goods) 2010-2026). **Checked directly against the full public data-catalogue file listing (291 files) and confirmed DOSM does not publish a country-partner-level trade breakdown**; Malaysia's bilateral supplier/customer concentration is instead built from UN Comtrade (Malaysia is reporter 458, part of the network above), not from DOSM.

## Sources Evaluated but Not Used

- **AIS / satellite / remote-sensing vessel-tracking data**: the brief explicitly permits investigating this "where legally accessible," but genuine AIS feeds are commercial/restricted at any meaningful coverage, so not pursued. Shipping-route exposure is proxied instead with World Bank container port traffic (a real, if coarser, PUBLIC substitute). See `LIMITATIONS.md`.
- **WTO tariff-line data**: evaluated. The detailed tariff schedule API would have required a comparable multi-day discovery effort to what UN Comtrade required here, for a dimension (tariff *rates*, as opposed to *flows*, *concentration*, and *prices*, all of which this project does cover) judged lower-priority given the project's time budget. Named explicitly as a scope decision, not an oversight.
- **R, Power BI, Docker**. See `docs/METHODOLOGY.md` "Tool Selection" for the documented reasoning (this portfolio's established "simplest tool that answers the question rigorously" principle, same as Project 007).
