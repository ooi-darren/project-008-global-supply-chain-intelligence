# Malaysia Analytical Framework

How Malaysia is treated as a dedicated strategic case study in this project (brief Sections 18-22), not an appendix.

## Data Layers Used

| Layer | Source | What it answers |
|---|---|---|
| National trade headline | DOSM `trade_headline` | Overall export/import/balance trend, 2001-2025 |
| Trade composition | DOSM `trade_sitc_1d` | What Malaysia actually exports (SITC sections) |
| Import composition by end use | DOSM `trade_enduse_bec` | How much of Malaysia's imports are production inputs (capital/intermediate goods) vs. final consumption |
| Bilateral trade | UN Comtrade (reporter 458, part of the 57/59-country network) | Who supplies Malaysia; who buys from Malaysia; concentration (HHI) on both sides |
| Logistics | World Bank LPI | Malaysia's position vs. ASEAN-6 peers |
| Critical minerals | USGS MCS 2025 | Malaysia's (small) share of global mine production for tracked materials |

## Vulnerability Index

Five dimensions, documented in full in `python/analysis/malaysia_vulnerability_opportunity.py`'s docstring: import dependency, supplier concentration, customer concentration, logistics fragility, and production-input import share (a Malaysia-specific proxy for commodity exposure. See `LIMITATIONS.md` item 7 for why this is a proxy rather than a direct measure).

## Opportunity Radar

Four hypotheses tested against evidence actually collected in this project, each explicitly graded by evidence strength (strong / weak-speculative / not evidenced) rather than presented as uniformly confident:

1. **Electronics & semiconductors**: strongly evidenced (Malaysia's largest real export category by SITC section, 50.3% of exports). Named, publicly reported companies behind this figure (added after external review, see `docs/SOURCES.md`): Infineon's RM30 billion Kulim investment (the world's largest 200mm silicon carbide power fab), Micron's Muar/Prai/Batu Kawan facilities, and ASE Technology's fifth Penang plant (opened February 2025). A genuine counter-signal from the same period: Intel paused its Penang wafer-fabrication and advanced-packaging project as of February 2025, a real, current reminder that this opportunity is not uniformly one-directional even among the companies most visibly present.
2. **Regional logistics hub**: strongly evidenced (2nd-highest LPI in ASEAN-6), and directly tied to a specific geographic asset previously missing from this project: the **Strait of Malacca**, the single largest oil-transit chokepoint in the world (23.2 million barrels/day, 29% of global maritime oil flows, EIA), runs along Malaysia's own coastline. Malaysia's own container-port traffic grew from 20.9 to 30.7 million TEU between 2013 and 2024 (World Bank), real, verifiable growth consistent with this positioning. See `docs/SCENARIO_METHODOLOGY.md` Scenario A/F for the risk side of the same geography.
3. **Critical-minerals processing**: weak/speculative (Malaysia's own production share is small for every tracked material; any opportunity would be processing imported feedstock, not a domestic resource advantage).
4. **Data centres / digital infrastructure**: not evidenced by this project (no direct dataset collected); named as a gap, not claimed either way.

## State/Cluster-Level Analysis

Not built. See `LIMITATIONS.md` item 5 for why (no sufficiently granular free dataset found; the brief's own instruction is not to assume regional importance without evidence, which cuts against forcing a weak sub-national analysis just to check the section off).

## ASEAN Comparison

Malaysia is benchmarked directly against Singapore, Indonesia, Thailand, the Philippines, and Vietnam on logistics performance (`data/processed/malaysia_asean_logistics_comparison.csv`); each country's own latest LPI-reporting year, since LPI is published periodically (not every year), so a naive "most recent calendar year" join would silently return nulls for every country (a real bug caught and fixed during this project's build. See `python/analysis/malaysia_deep_dive.py`).
