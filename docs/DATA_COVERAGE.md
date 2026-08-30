# Data Coverage

## Bilateral Trade Network (UN Comtrade)

- **59 economies** in the target network (`data/external/network_countries.csv`); **all 59 with bilateral edge data**. UN Comtrade's free tier alone only ever returned **55** as a reporter (see below).
- Two periods: **2016** and **2023**.
- **Correction to this document's own earlier claim, found by checking it against the raw data rather than trusting it:** an earlier version of this section listed "Ethiopia (2016 exports)" and "Belgium (2023 imports)" as isolated, one-off missing-data cells alongside genuinely isolated gaps like Iran (2023 exports), Bangladesh (2023 exports), and Cuba (2023 imports). That framing was wrong for Ethiopia and Belgium specifically: both had **zero rows as a reporter across every flow and period**, and zero rows as a partner in any other country's data either, a complete, systematic exclusion exactly like the already-documented US/India case, not an isolated country-year gap. This was only caught while building the OECD-based fix for USA and India and verifying the resulting reporter count directly (`comtrade["reporterCode"].nunique()` returned 55, not the 57 this document itself had been claiming). Iran (2023 exports), Bangladesh (2023 exports), and Cuba (2023 imports) remain genuine, isolated single-cell reporting gaps, unaffected by this correction. See `docs/DATA_QUALITY.md` item 3 for the full discovery-and-fix account.

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
