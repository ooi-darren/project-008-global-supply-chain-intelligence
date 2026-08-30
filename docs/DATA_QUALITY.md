# Data Quality

Real issues found and fixed while building this project, per the brief's Section 31. Every one listed here was caught by checking the data against a plausibility test (does this match known real-world facts?), not assumed away.

## 1. UN Comtrade: Triple Double-Counting Trap

Three independent breakdown dimensions (`motCode`, `partner2Code`, `customsCode`) each split a reporter's data into an aggregate row plus its own breakdown; naively summing all rows for a partner overstates trade value by 2-10x depending on how many dimensions a given reporter reports at. Caught because China's Argentina-export figure for 2016 was implausibly ~2x too high on first pass, and separately because Spain returned 266 rows for 58 possible partners. Fixed by requesting `motCode=0&partner2Code=0&customsCode=C00` as explicit server-side filters. Full detail in `python/data_collection/comtrade_network.py`.

## 2. UN Comtrade: 500-Row Page Cap Silently Truncates Detailed Reporters

Before the server-side filter fix above, China's unfiltered response for a single (reporter, flow, period) combination hit exactly 500 rows and truncated before any aggregate (motCode=0) rows survived, the client-side-only filter would have silently returned **zero** data for China, one of the most important nodes in the network, without erroring. Caught by inspecting `raw_rows` vs. `rows_kept` in the collection log for every call, not just trusting a non-empty response.

## 3. UN Comtrade: USA and India Structurally Absent

See `SOURCES.md` and `LIMITATIONS.md` item 1. Verified directly (bare total-query returns zero rows; confirmed other countries' data never lists either as a partner) rather than assumed to be a temporary gap.

## 4. USGS: "World Total" Rows Mixed into the Country Column

11 distinct aggregate-label variants (`"World total (rounded)"`, `"World total (ilmenite and rutile, rounded)"`, `"Other countries (includes crude)"`, etc.) appear in the same COUNTRY column as genuine countries. An exact-match exclusion list missed most variants on the first pass; every material's computed "top producer" was wrongly "World total" at ~50% share. Caught because a ~50% share for an unnamed aggregate as literally every material's #1 producer was an obvious red flag; fixed with a substring-pattern exclusion (`"world total"`, `"other countr"`) that catches every variant actually present in the file.

## 5. World Bank LPI: Periodic, Not Annual, Publication

Logistics Performance Index is published roughly every 2 years, not annually. A naive "each country's literal latest row in the panel" join returns null LPI for every country if the panel's latest year happens to be a non-LPI year (which it was: 2025). Fixed with a dedicated "each country's own latest year WITH a non-null LPI value" snapshot (`data/processed/latest_lpi_snapshot.csv`), used specifically wherever LPI is needed rather than the general per-country-latest-year table.

## 6. DOSM BEC Dataset: Confirming the "Total" Row Convention

The `bec` code `"000"` was assumed (not just guessed) to represent the all-categories total per `end_use`/year, matching a convention seen elsewhere in DOSM data, verified by checking it is consistently the largest value across bec codes for each (year, end_use) group before relying on it for the vulnerability-index production-input-share calculation.

## 7. Currency/Classification Consistency

UN Comtrade's `classificationCode` field shows some data reported under HS revision H4 and other data under H6 depending on the year and reporter (visible directly in the raw JSON responses). This project uses `cmdCode=TOTAL` throughout, which is classification-revision-independent for the aggregate figure, avoiding the need to reconcile HS revisions row-by-row, a deliberate scope choice, not an oversight (a full HS-6-digit-level version of this project would need to handle H4/H5/H6 crosswalks explicitly).
