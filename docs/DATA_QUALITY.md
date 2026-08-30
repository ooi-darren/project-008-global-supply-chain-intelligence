# Data Quality

Real issues found and fixed while building this project, per the brief's Section 31. Every one listed here was caught by checking the data against a plausibility test (does this match known real-world facts?), not assumed away.

## 1. UN Comtrade: Triple Double-Counting Trap

Three independent breakdown dimensions (`motCode`, `partner2Code`, `customsCode`) each split a reporter's data into an aggregate row plus its own breakdown; naively summing all rows for a partner overstates trade value by 2-10x depending on how many dimensions a given reporter reports at. Caught because China's Argentina-export figure for 2016 was implausibly ~2x too high on first pass, and separately because Spain returned 266 rows for 58 possible partners. Fixed by requesting `motCode=0&partner2Code=0&customsCode=C00` as explicit server-side filters. Full detail in `python/data_collection/comtrade_network.py`.

## 2. UN Comtrade: 500-Row Page Cap Silently Truncates Detailed Reporters

Before the server-side filter fix above, China's unfiltered response for a single (reporter, flow, period) combination hit exactly 500 rows and truncated before any aggregate (motCode=0) rows survived, the client-side-only filter would have silently returned **zero** data for China, one of the most important nodes in the network, without erroring. Caught by inspecting `raw_rows` vs. `rows_kept` in the collection log for every call, not just trusting a non-empty response.

## 3. UN Comtrade: USA and India Structurally Absent (Later Found to Also Include Belgium and Ethiopia, Then Resolved)

See `SOURCES.md` and `LIMITATIONS.md` item 1. Verified directly (bare total-query returns zero rows; confirmed other countries' data never lists either as a partner) rather than assumed to be a temporary gap.

**Extended after external review, before assuming the "57 of 59" framing was correct.** While building the OECD-based fix for USA and India specifically, this project checked its own claim against the raw collected data (`data/raw/comtrade_bilateral_trade_raw.csv`) instead of trusting the documentation: `comtrade["reporterCode"].nunique()` returned **55**, not 57. Two more countries, Belgium (Comtrade code 58) and Ethiopia (230), had zero rows as a reporter across every flow and period, exactly like USA and India, and, on further check, zero rows as a partner in any other country's data either, meaning both were 100% absent from the network, not merely under-documented. The original collection script's cached raw JSON responses for both (`data/raw/comtrade_network/r58_*.json`, `r230_*.json`) confirmed this was a real API response (`count: 0`, no error), not a collection bug: UN Comtrade's free tier genuinely never returns these two as a reporter.

**Fixed, not left as a bigger undocumented gap:** all four countries (USA, India, Belgium, Ethiopia) backfilled via OECD's Bilateral Trade in Goods database (see `SOURCES.md`), which needed only 16 additional API calls total and no API key. `python/cleaning/merge_bilateral_trade.py` resolves each directed edge to exactly one source, tagged, never blended: a backfilled country's own export report where it is the exporter, or its own import report (the mirror of the missing partner's export) where it is the importer. The resulting network genuinely covers all 59 target countries for the first time, and this fix changed several of the project's own downstream findings, most visibly the trade-network centrality gainers/losers list (India replaces the UAE as the biggest 2016-2023 gainer) and Malaysia's customer ranking (the United States is now visibly Malaysia's near-tied second-largest customer, previously entirely absent from that analysis). See `LIMITATIONS.md` items 1, 12, and 17 for what this fix does and does not fully resolve.

## 4. USGS: "World Total" Rows Mixed into the Country Column

11 distinct aggregate-label variants (`"World total (rounded)"`, `"World total (ilmenite and rutile, rounded)"`, `"Other countries (includes crude)"`, etc.) appear in the same COUNTRY column as genuine countries. An exact-match exclusion list missed most variants on the first pass; every material's computed "top producer" was wrongly "World total" at ~50% share. Caught because a ~50% share for an unnamed aggregate as literally every material's #1 producer was an obvious red flag; fixed with a substring-pattern exclusion (`"world total"`, `"other countr"`) that catches every variant actually present in the file.

## 5. World Bank LPI: Periodic, Not Annual, Publication

Logistics Performance Index is published roughly every 2 years, not annually. A naive "each country's literal latest row in the panel" join returns null LPI for every country if the panel's latest year happens to be a non-LPI year (which it was: 2025). Fixed with a dedicated "each country's own latest year WITH a non-null LPI value" snapshot (`data/processed/latest_lpi_snapshot.csv`), used specifically wherever LPI is needed rather than the general per-country-latest-year table.

## 6. DOSM BEC Dataset: Confirming the "Total" Row Convention

The `bec` code `"000"` was assumed (not just guessed) to represent the all-categories total per `end_use`/year, matching a convention seen elsewhere in DOSM data, verified by checking it is consistently the largest value across bec codes for each (year, end_use) group before relying on it for the vulnerability-index production-input-share calculation.

## 7. Currency/Classification Consistency

UN Comtrade's `classificationCode` field shows some data reported under HS revision H4 and other data under H6 depending on the year and reporter (visible directly in the raw JSON responses). This project uses `cmdCode=TOTAL` throughout, which is classification-revision-independent for the aggregate figure, avoiding the need to reconcile HS revisions row-by-row, a deliberate scope choice, not an oversight (a full HS-6-digit-level version of this project would need to handle H4/H5/H6 crosswalks explicitly).
