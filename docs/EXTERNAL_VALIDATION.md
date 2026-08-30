# External Validation

Added after external review, which flagged that this project's Supply Chain Risk Index was not benchmarked against any independent, published source, an internally-consistent index that agrees with nothing external is harder to trust. This document is a deliberately honest, limited cross-check, not a claim of full validation.

## What Was Compared

This project's Supply Chain Risk Index ranks Malaysia **30th of 59** economies on structural supply-chain risk (import dependency, logistics fragility, trade-partner concentration, commodity exposure), genuinely mid-pack. Two independent, publicly published indices were checked for directional consistency:

- **DHL Global Connectedness Report 2026** (NYU Stern / DHL): Malaysia ranks **16th of 180 countries** in global connectedness (depth and breadth of trade, capital, information, and people flows), 1st among middle-income economies, and 7th globally in improvement since 2019.
- **Agility Emerging Markets Logistics Index 2026**: Malaysia ranks **5th of 50** emerging markets on logistics, business fundamentals, and digital readiness, no change from the prior year. (Verified by fetching Agility's own rankings page directly; an earlier draft of this project cited a different, incorrect figure sourced from a secondary summary, corrected and documented in `docs/SOURCES.md`.)

## What This Comparison Does and Does Not Show

These are **different constructs**, not the same measurement twice. DHL's index measures how *connected* Malaysia is; Agility's measures emerging-market *logistics strength*; this project's index measures structural *risk exposure*. A country can be highly connected and moderately risk-exposed at the same time, connectivity and vulnerability are not opposites. Read together, the three are **directionally consistent, not contradictory**: Malaysia performs strongly on two independent, well-connected/strong-logistics measures (top-decile-to-top-quintile territory in both), while this project's own risk index places it mid-pack, not top-tier, on structural risk specifically. That is a coherent picture, not three numbers in tension: a well-integrated, well-connected trading economy can still carry real, moderate structural risk (rising trade-partner concentration, a mid-tier logistics-fragility score relative to the full 59-country network, meaningful import dependency), which is exactly the finding this project's own index reports.

**What this is not:** a claim that these three indices measure the same thing and therefore validate each other numerically, they use different countries, different pillars, and different weighting choices, so no formal correlation is computed here. It is a qualitative triangulation check: does this project's own novel index produce a country placement that at least does not contradict what independently-published, well-established indices say about the same country. It does not.

## Why a Fuller Quantitative Benchmark Was Not Built

A rigorous quantitative benchmark (e.g. computing rank correlation between this project's 59-country risk ranking and a published index's full country list) would need that published index's complete underlying country-level data, which is either commercial/licensed (Agility, DHL's full dataset) or not structured for direct pillar-by-pillar comparison against this project's own four pillars. Named here as a scope limitation, not an oversight; see `docs/LIMITATIONS.md`.
