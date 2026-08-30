# Data Coverage

## Bilateral Trade Network (UN Comtrade)

- **59 economies** in the target network (`data/external/network_countries.csv`); **57 with bilateral edge data** (United States and India structurally excluded from the free-tier endpoint. See `LIMITATIONS.md` item 1).
- Two periods: **2016** and **2023**.
- Within the 57, individual reporters occasionally show 0 rows for a given (flow, period), a real reporting gap for that specific country/year, not a systematic exclusion like the US/India case. Examples observed during collection: Ethiopia (2016 exports), Iran (2023 exports), Bangladesh (2023 exports), Cuba (2023 imports), Belgium (2023 imports). These are treated as genuine missing data points for that country-year, consistent with how this portfolio handles missing-data cells elsewhere (stated explicitly, not imputed).

## World Bank Panel

- **~217 economies**, 2013-2025, 17 indicators. Full coverage detail follows the same pattern as Project 007's `DATA_COVERAGE.md` (data lags 1-2 years for most countries; LPI specifically is periodic, not annual. See `DATA_QUALITY.md` item 5).

## Critical Materials (USGS)

- **13 materials**, 2023 production data (2024 is estimate-only in the source and not used for the concentration calculation). Country counts per material range from 5 (Gallium, a genuinely small producer set) to 20 (Aluminum/refined).

## Malaysia (DOSM)

- Trade headline and SITC: monthly, **2000/2001-2025** (annualised for this project).
- BEC import composition: monthly, **2010/2011-2025**.
- No DOSM country-partner breakdown exists (checked directly, see `SOURCES.md`); bilateral figures come from UN Comtrade instead.

## Commodity Prices

- **16 priority commodities** (of 18 attempted; urea and DAP fertiliser columns not found under the expected names in the current Pink Sheet release, not pursued further given the other 16 already cover energy, industrial metals, and 4 food/agriculture series), monthly, back to 1960, through July 2026 at time of access.
