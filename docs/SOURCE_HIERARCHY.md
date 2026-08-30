# Source Hierarchy

How sources were evaluated and prioritised in this project, per the brief's Section 30.

## Tier 1 (used as primary sources)

1. **UN Comtrade**: the only source with genuine bilateral (country-pair) trade flow data at the coverage this project needed; no substitute considered for the trade network.
2. **World Bank Open Data**: selected as the primary macro/logistics/GDP source for the same reason it was selected in this portfolio's Project 007: single consistent source across the full country panel avoids cross-source definitional mismatches, direct API access, no authentication required.
3. **USGS Mineral Commodity Summaries**: the standard, authoritative, annually-updated source for global mineral production statistics; no free alternative offers comparable country-level production breakdowns for 90+ commodities in one place.
4. **DOSM (Department of Statistics Malaysia)**; Malaysia's own national statistical agency; used in preference to any secondary/aggregated Malaysia figure wherever DOSM publishes the series directly.

## Tier 2 (used to fill a specific gap Tier 1 could not)

5. **World Bank Commodity Markets (Pink Sheet)**: Tier 1-equivalent in authority (same publisher), used specifically because none of the above four sources publish commodity price time series.

## Evaluated, Not Used

- **WTO tariff-line data**: real Tier 1 authority, but not pursued given the time budget already spent resolving UN Comtrade's undocumented data-quality quirks; named as a scope decision in `SOURCES.md`, not a quality judgment against WTO data.
- **AIS/satellite data**: would be Tier 1 if freely and legitimately accessible, but genuine feeds are commercial/restricted, so not used, per the brief's own instruction to only use legitimately accessible data.
- **Industry/consultancy reports** (e.g. shipping-line freight-rate commentary): the brief permits these to supplement, not replace, official statistical evidence. None were used as a primary quantitative input in this project; where a "why is this happening" narrative draws on such sources for context, it is kept separate from the PUBLIC/DERIVED quantitative classification, following the same convention as the rest of this portfolio.

## Decision Rule Applied Throughout

When two Tier 1 sources could plausibly answer the same question (e.g. World Bank vs. IMF for trade statistics), the source already validated and in active use elsewhere in this project was preferred over introducing a second source with its own definitional quirks to reconcile, the same "one consistent source, not multiple partially-overlapping ones" principle Project 007 established for this portfolio.
