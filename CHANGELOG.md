# Changelog

This project was built, then substantially revised twice after external review. Every substantive correction is recorded here, once, so the rest of the documentation can state its current findings directly rather than repeatedly narrating its own revision history. Git history carries the full detail; this is the reader-facing summary.

## Round 3 (current): Mirror-statistic quantification, review-driven fixes

- **Quantified the mirror-statistic caveat instead of only naming it.** `python/analysis/validate_mirror_statistics.py` measures the real discrepancy between direct export reports and mirror import reports for the same physical flow, using data already collected for the four backfilled countries. Result: median 14.4% for large (≥$10B) relationships, much noisier for smaller ones. Applied this to soften the Malaysia customer-ranking claim (see below).
- **Corrected an overclaimed ranking.** Malaysia's export-to-US figure is a mirror-statistic edge; at its size, the measured uncertainty band (~$39-55 billion against a reported $47.3 billion) spans both Singapore's and China's directly-reported customer figures. The README, notebook 08, and `malaysia_deep_dive.py` no longer claim a precise "Singapore edges out the US" ranking, instead stating that Malaysia's #1-vs-#2 customer is genuinely undetermined by this project's data.
- **Consolidated repeated revision narration.** Earlier drafts of the README and several docs repeated "added after external review" and "an earlier version of this project" as qualifiers on nearly every finding (36 instances project-wide). That history now lives here, once; the rest of the documentation states current findings as itself.
- **Rewrote the Recommendation section**, which had gone stale after Round 2's network fix (it no longer reflected the flat customer-concentration finding or the new US-Malaysia relationship).

## Round 2: Genuinely complete 59-country network

- **Found and fixed a bigger gap than documented.** UN Comtrade's free tier was known to exclude the United States and India entirely. Verifying that "57 of 59" claim against the raw data (rather than trusting it) surfaced two more countries with zero rows as a Comtrade reporter: Belgium and Ethiopia, previously undocumented. The network was genuinely 55 of 59 countries, not 57.
- **Backfilled all four** from OECD's Bilateral Trade in Goods (BTiGE) database, a free, no-API-key public source, verified against known real-world figures before trusting it. Considered and rejected the US Census API (requires a registered key) and India's DGCIS/TRADESTAT (no API, doesn't cover 2016).
- **This changed real findings, reported honestly:** the network's biggest 2016-2023 gainer became India (+44% PageRank), not the UAE (previously reported +29%); Malaysia's second-largest customer became a live question involving the US, not a settled "China, second behind Singapore"; Malaysia's customer-concentration trend flattened rather than continuing to rise; Mexico became newly visible as a top-10 highest-risk economy.
- **Fixed a broken visualization** (the original global trade network chart): force-directed layout on a 75%-dense, degree-heterogeneous graph flung sparsely-connected countries to arbitrary positions and crushed labels together. Restricted the illustrative chart to the top 25 economies by volume with a Kamada-Kawai layout; the full 59-country network remains what the actual centrality analysis is computed on.
- **Fact-checked every external claim** added in Round 1 against primary sources rather than trusting search summaries. Found and corrected two real errors: the Agility Emerging Markets Logistics Index figure (was citing the wrong year/rank), and Intel's Penang project status (was described as an open-ended pause; the facility is actually 99% complete and resuming operations).

## Round 1: External review response (MBB/logistics-CEO/consultant/professor lens)

- Added a governing Recommendation section (Answer First structure).
- Named the Strait of Malacca explicitly (previously absent despite being Malaysia's most directly relevant piece of geography for this project's own logistics-hub claim).
- Named real companies (Infineon, Micron, ASE Technology, Intel) behind Malaysia's electronics export figure, sourced from public reporting.
- Added a real, historically-anchored stress test connecting the Malaysia export forecast to the shock-scenario layer (previously kept permanently separate).
- Upgraded the risk index's sensitivity check from a single alternative weighting to a 1,000-draw weight-sensitivity Monte Carlo, which surfaced a more honest finding: Malaysia's risk rank is far less stable than the single point estimate suggested.
- Added qualitative likelihood tags to the shock-scenario table.
- Added a qualitative external cross-check of the risk index against two independent published indices (DHL Global Connectedness Report, Agility Emerging Markets Logistics Index).
- Added academic grounding (a Related Work note) citing the literature this project's methods sit within.

## Initial build

See the initial commit message and `docs/DATA_QUALITY.md` for the real data-quality bugs found and fixed during the original build (UN Comtrade's triple double-counting trap, USGS's "World total" aggregate-label exclusion, DOSM's BEC double-counting, a recurring pandas dtype round-trip bug).
