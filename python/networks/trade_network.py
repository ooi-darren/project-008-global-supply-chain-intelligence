# -*- coding: utf-8 -*-
"""
Global trade network analysis for Project 008.

Builds a directed, weighted trade network from data/processed/
trade_network_edges_export.csv (2016 and 2023, one resolved export edge per
country pair): an export from A to B and an import by B from A are two
independently-reported observations of the same physical flow; using
exports as the edge weight avoids double reporting and is the more
commonly-audited direction in trade statistics.

Genuinely covers all 59 network countries as of the fix added after
external review: UN Comtrade's free tier never returns the United States,
India, Belgium, or Ethiopia as a reporter (nor, for these four, as a
partner in any other country's data either), so their edges are resolved
from OECD's Bilateral Trade in Goods database instead (their own export
report where they are the exporter; their own import report, used as a
mirror, where they are the importer and no other source exists) -- see
python/cleaning/merge_bilateral_trade.py's docstring for the exact
three-rule resolution and python/data_collection/oecd_missing_reporters_
trade.py for the collection itself. Before this fix, these four countries
were absent from this network entirely (docs/LIMITATIONS.md item 1
previously described only two of the four).

Computes, per country per year:
  - weighted in-degree / out-degree (total imports/exports within the network)
  - betweenness centrality (bridge/hub role -- does trade route "through" this
    country's relationships more than its raw volume would suggest)
  - eigenvector centrality (connected-to-important-countries importance)
  - PageRank (a directed-graph analogue, weighting by trading-partner importance)

Then compares 2016 vs 2023 to identify which countries gained or lost
network importance -- directly answering the brief's "who is becoming more
important, who is losing share" question with a network-science measure,
not just raw trade-value ranking (the brief explicitly warns against
equating "largest trader" with "most structurally important node").
"""
import pandas as pd
import networkx as nx
import os

EDGES = "data/processed/trade_network_edges_export.csv"
OUT_DIR = "data/processed"
os.makedirs(OUT_DIR, exist_ok=True)


def build_graph(df, period):
    g = nx.DiGraph()
    sub = df[df["period"].astype(str) == str(period)]
    for _, row in sub.iterrows():
        # edge A->B: A exports to B, weight = export value (USD)
        g.add_edge(int(row["exporterCode"]), int(row["importerCode"]), weight=row["primaryValue"])
    return g


def centrality_table(g, code_to_iso):
    bc = nx.betweenness_centrality(g, weight="weight", normalized=True)
    try:
        ec = nx.eigenvector_centrality(g, weight="weight", max_iter=1000)
    except nx.PowerIterationFailedConvergence:
        ec = {n: float("nan") for n in g.nodes}
    pr = nx.pagerank(g, weight="weight")
    out_deg = dict(g.out_degree(weight="weight"))
    in_deg = dict(g.in_degree(weight="weight"))

    rows = []
    for node in g.nodes:
        rows.append({
            "ISO3": code_to_iso.get(node, node),
            "comtradeCode": node,
            "total_exports_to_network_usd": out_deg.get(node, 0),
            "total_imports_from_network_usd": in_deg.get(node, 0),
            "betweenness_centrality": bc.get(node, 0),
            "eigenvector_centrality": ec.get(node, float("nan")),
            "pagerank": pr.get(node, 0),
        })
    return pd.DataFrame(rows)


def main():
    df = pd.read_csv(EDGES)
    countries = pd.read_csv("data/external/network_countries.csv")
    code_to_iso = dict(zip(countries["comtradeReporterCode"], countries["ISO3"]))
    code_to_name = dict(zip(countries["comtradeReporterCode"], countries["Country"]))

    all_tables = []
    for period in ["2016", "2023"]:
        g = build_graph(df, period)
        print(f"{period}: {g.number_of_nodes()} nodes, {g.number_of_edges()} edges, "
              f"density={nx.density(g):.3f}")
        tbl = centrality_table(g, code_to_iso)
        tbl["period"] = period
        tbl["Country"] = tbl["comtradeCode"].map(code_to_name)
        all_tables.append(tbl)

    combined = pd.concat(all_tables, ignore_index=True)
    combined.to_csv(os.path.join(OUT_DIR, "trade_network_centrality.csv"), index=False)
    print("\nsaved trade_network_centrality.csv:", combined.shape)

    # 2016 -> 2023 change in network importance (PageRank), the headline
    # "who's rising / who's falling" table
    piv = combined.pivot(index="Country", columns="period", values="pagerank")
    piv["pagerank_change"] = piv["2023"] - piv["2016"]
    piv["pagerank_change_pct"] = (piv["2023"] / piv["2016"] - 1) * 100
    piv = piv.sort_values("pagerank_change", ascending=False)
    piv.to_csv(os.path.join(OUT_DIR, "trade_network_pagerank_change.csv"))
    print("\nBiggest network-importance gainers (PageRank, 2016->2023):")
    print(piv.head(10).round(4))
    print("\nBiggest network-importance losers:")
    print(piv.tail(10).round(4))


if __name__ == "__main__":
    main()
