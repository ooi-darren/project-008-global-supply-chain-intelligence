# -*- coding: utf-8 -*-
"""
Merges UN Comtrade's bilateral network (data/raw/comtrade_bilateral_
trade_raw.csv, which turned out to genuinely cover only 55 of the 59 target
reporters, not 57 as originally documented -- see below) with the
OECD-sourced backfill for all four missing reporters (data/raw/
oecd_missing_reporters_raw.csv, see that script's docstring) into one
analysis-ready, genuinely-59-country network, added after external review
identified the missing US/India as the project's single most visible gap.

USA and India were already known and documented as absent (UN Comtrade's
free tier structurally excludes them). Verifying that "57 of 59" framing
against the raw data while building this fix surfaced two more countries
with zero rows as a Comtrade reporter, previously undocumented: Belgium and
Ethiopia, each 100% absent from the network (not even present as a
partner in another country's data) -- confirmed by inspecting the cached
raw JSON responses directly (count=0, no error). See docs/DATA_QUALITY.md
for the full account of finding this.

data/raw/comtrade_bilateral_trade_raw.csv is deliberately left untouched by
this script (and by every other script in this project) -- it stays exactly
what its name and the README's Reproducibility section describe: the pure,
unmodified output of comtrade_network.py. This script only READS it, then
writes a separate, clearly-derived output.

Every row is tagged with its source (UN_COMTRADE or OECD_BTIGE) so the two
are never silently blended -- a reader can always tell which of the two
different underlying pipelines a given edge came from, the same labeling
discipline already applied to Malaysia's DOSM data throughout this project.
See docs/DATA_QUALITY.md and docs/LIMITATIONS.md for the documented
methodological difference between the two sources.

Overlap check: UN Comtrade and OECD_BTIGE should have ZERO overlapping
(reporter, partner, period, flow) combinations by construction (Comtrade
never returns the four backfilled countries as a reporter at all) --
verified explicitly below, not assumed, and the script fails loudly if that
assumption is ever violated by a future data refresh.

SECOND OUTPUT -- resolved export edges (data/processed/trade_network_edges_
export.csv): python/networks/trade_network.py (and everything downstream of
it) deliberately uses ONLY export-flow rows as edges, since an export report
from country A and an import report from B of that same physical flow are
two independent observations of one flow, and using only exports avoids
double-counting. That convention breaks for the four backfilled countries:
UN Comtrade never has ANY other country's own export report where the
partner is one of these four (confirmed directly, e.g. China's own export
data never lists USA as a partner), so an edge INTO one of the four (e.g.
France->USA) has no export-side source anywhere in this project's data.
Its only available source is the mirror: the four countries' own OECD-
sourced IMPORT report (USA reporting "imports from France"). This script
resolves that explicitly, one source per edge, never both:
  - If the exporter (A) is one of the four backfilled countries: use that
    country's own OECD export report (flow=X, reporter=A, partner=B).
  - Else if the importer (B) is one of the four: use that country's own
    OECD import report (flow=M, reporter=B, partner=A) as the mirror for
    A's export to B, since A's own export report to B does not exist
    anywhere in this project's data.
  - Else (neither A nor B is one of the four): use UN Comtrade's own export
    report (flow=X, reporter=A, partner=B), exactly as before this fix.
Each resolved row is tagged with which of the three rules produced it
(edge_source column: DIRECT_EXPORT_COMTRADE, DIRECT_EXPORT_OECD, or
MIRROR_IMPORT_OECD) so this substitution is never silently invisible to a
reader of the output file.
"""
import pandas as pd
import os

OUT_PATH = os.path.join("data", "processed", "bilateral_trade_network_full.csv")
EDGES_OUT_PATH = os.path.join("data", "processed", "trade_network_edges_export.csv")
BACKFILLED_REPORTER_CODES = {841, 356, 58, 230}  # USA, IND, BEL, ETH


def build_resolved_export_edges(full):
    """One row per (period, exporter, importer): the best available source
    for that directed export edge, per the three-rule resolution above."""
    direct_export = full[full["flow"] == "X"].copy()
    direct_export["edge_source"] = direct_export["source"].map(
        {"UN_COMTRADE": "DIRECT_EXPORT_COMTRADE", "OECD_BTIGE": "DIRECT_EXPORT_OECD"})
    direct_export = direct_export.rename(columns={"reporterCode": "exporterCode", "partnerCode": "importerCode"})

    # Mirror rows: importer's own OECD import report, reinterpreted as the
    # exporter's edge. Only needed where the exporter is NOT one of the four
    # (if it were, DIRECT_EXPORT_OECD above already covers it) and the
    # importer IS one of the four (the only case with no export-side source).
    mirror_candidates = full[(full["flow"] == "M") & (full["source"] == "OECD_BTIGE")].copy()
    mirror_candidates = mirror_candidates.rename(
        columns={"reporterCode": "importerCode", "partnerCode": "exporterCode"})
    mirror_candidates = mirror_candidates[~mirror_candidates["exporterCode"].isin(BACKFILLED_REPORTER_CODES)]
    mirror_candidates["edge_source"] = "MIRROR_IMPORT_OECD"

    keep_cols = ["period", "exporterCode", "importerCode", "primaryValue", "edge_source"]
    combined = pd.concat([direct_export[keep_cols], mirror_candidates[keep_cols]], ignore_index=True)

    dupes = combined.duplicated(subset=["period", "exporterCode", "importerCode"], keep=False)
    if dupes.any():
        raise RuntimeError(
            f"Found {dupes.sum()} duplicate (period, exporter, importer) edges after resolution -- "
            "the three-rule resolution should produce exactly one source per edge. Investigate."
        )
    return combined.sort_values(["period", "exporterCode", "importerCode"]).reset_index(drop=True)


def main():
    comtrade = pd.read_csv("data/raw/comtrade_bilateral_trade_raw.csv")
    comtrade["source"] = "UN_COMTRADE"

    oecd = pd.read_csv("data/raw/oecd_missing_reporters_raw.csv")
    oecd["source"] = "OECD_BTIGE"

    key_cols = ["period", "flow", "reporterCode", "partnerCode"]
    overlap = comtrade.merge(oecd, on=key_cols, how="inner")
    if len(overlap) > 0:
        raise RuntimeError(
            f"Found {len(overlap)} overlapping (reporter, partner, period, flow) rows "
            "between UN Comtrade and OECD_BTIGE -- this should be impossible by "
            "construction (Comtrade never returns the four backfilled countries as a "
            "reporter). Investigate before merging; do not silently sum or prefer one source."
        )

    full = pd.concat([comtrade, oecd], ignore_index=True)
    full = full.sort_values(["period", "flow", "reporterCode", "partnerCode"]).reset_index(drop=True)
    full.to_csv(OUT_PATH, index=False)

    print(f"Saved {OUT_PATH}: {full.shape}")
    print("\nRows by source:")
    print(full.groupby("source").size())
    print("\nReporters now covered (should be 59):", full["reporterCode"].nunique())
    print("\nRows by period/flow/source:")
    print(full.groupby(["period", "flow", "source"]).size())

    edges = build_resolved_export_edges(full)
    edges.to_csv(EDGES_OUT_PATH, index=False)
    print(f"\nSaved {EDGES_OUT_PATH}: {edges.shape}")
    print("\nResolved export edges by source rule:")
    print(edges.groupby(["period", "edge_source"]).size())
    exporters_2023 = edges[edges["period"] == 2023]["exporterCode"].nunique()
    print(f"\nUnique exporters with at least one resolved edge, 2023: {exporters_2023} (target: 59)")


if __name__ == "__main__":
    main()
