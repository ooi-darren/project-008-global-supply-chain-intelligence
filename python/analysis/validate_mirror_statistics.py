# -*- coding: utf-8 -*-
"""
Quantifies the mirror-statistic discrepancy that LIMITATIONS.md item 17
previously named only qualitatively ("mirror and direct reports of the same
physical flow do not always match exactly"). Added after a second external
review pass specifically challenged that softness: the data to measure it
directly was already collected and sitting unused.

Method: OECD's BTiGE data gives each of the four backfilled countries
(USA, IND, BEL, ETH) BOTH their own export report and their own import
report. For every ordered pair among these four, that means a genuine,
independent direct-vs-mirror comparison is available for the SAME physical
trade flow: country A's own export report to B, versus country B's own
import report from A. This is exactly the mechanism used to resolve every
MIRROR_IMPORT_OECD edge elsewhere in the network (e.g. Malaysia's exports to
the US, which has no direct source and is resolved from the US's own import
report), so measuring the discrepancy on these 24 known pairs (4 countries
x 3 other partners x 2 periods) is a real, in-sample validation of that
exact resolution mechanism, not an external guess.

Finding: discrepancy is strongly size-dependent (Spearman rho approx -0.45
between trade value and discrepancy %). Large bilateral relationships
(>=$10B, comparable in scale to Malaysia's ~$47B trade with the US) show a
median discrepancy of 14.4% (mean 17.2%, n=8); mid-size ($1-10B) and small
(<$1B) relationships are far noisier (median 42.1% and 43.4% respectively),
consistent with rounding/classification/timing differences mattering more
relative to a smaller base. The overall 24-pair range is 3.3% to 241.8%.

Direct consequence for this project's own findings: Malaysia's export
figure to the US ($47.3B, 2023) is a MIRROR_IMPORT_OECD edge, the same
mechanism validated here. At the large-relationship discrepancy band
(14-17%), the true figure plausibly lies in a ~$39-55B range, wide enough
to span both Singapore's directly-reported $48.1B (Malaysia's #1 customer)
and China's directly-reported $42.1B (#3), meaning this project cannot
support a precise "Singapore edges out the US by 0.2 percentage points"
ranking claim; see the softened claim in the README and
python/analysis/malaysia_deep_dive.py's docstring.
"""
import pandas as pd
import itertools
import os

OUT_DIR = "data/processed"
BACKFILLED = {841: "USA", 356: "IND", 58: "BEL", 230: "ETH"}


def main():
    full = pd.read_csv(os.path.join(OUT_DIR, "bilateral_trade_network_full.csv"))
    oecd = full[full["source"] == "OECD_BTIGE"]

    rows = []
    for period in [2016, 2023]:
        for a, b in itertools.permutations(BACKFILLED.keys(), 2):
            exp = oecd[(oecd["reporterCode"] == a) & (oecd["partnerCode"] == b) &
                       (oecd["flow"] == "X") & (oecd["period"] == period)]
            imp = oecd[(oecd["reporterCode"] == b) & (oecd["partnerCode"] == a) &
                       (oecd["flow"] == "M") & (oecd["period"] == period)]
            if len(exp) and len(imp):
                v1, v2 = exp["primaryValue"].values[0], imp["primaryValue"].values[0]
                rows.append({
                    "period": period, "exporter": BACKFILLED[a], "importer": BACKFILLED[b],
                    "export_report_usd": v1, "mirror_import_report_usd": v2,
                    "avg_value_usd": (v1 + v2) / 2,
                    "discrepancy_pct": abs(v1 - v2) / v1 * 100,
                })

    df = pd.DataFrame(rows).sort_values("avg_value_usd", ascending=False)
    df.to_csv(os.path.join(OUT_DIR, "mirror_statistic_validation.csv"), index=False)

    large = df[df["avg_value_usd"] >= 10e9]
    mid = df[(df["avg_value_usd"] >= 1e9) & (df["avg_value_usd"] < 10e9)]
    small = df[df["avg_value_usd"] < 1e9]

    print(f"Saved mirror_statistic_validation.csv: {df.shape}")
    print(f"\nOverall (n={len(df)}): mean={df['discrepancy_pct'].mean():.1f}%, "
          f"median={df['discrepancy_pct'].median():.1f}%, "
          f"range={df['discrepancy_pct'].min():.1f}%-{df['discrepancy_pct'].max():.1f}%")
    print(f"Large (>=$10B, n={len(large)}): mean={large['discrepancy_pct'].mean():.1f}%, "
          f"median={large['discrepancy_pct'].median():.1f}%")
    print(f"Mid ($1-10B, n={len(mid)}): mean={mid['discrepancy_pct'].mean():.1f}%, "
          f"median={mid['discrepancy_pct'].median():.1f}%")
    print(f"Small (<$1B, n={len(small)}): mean={small['discrepancy_pct'].mean():.1f}%, "
          f"median={small['discrepancy_pct'].median():.1f}%")
    print(f"\nSpearman correlation (value vs. discrepancy): "
          f"{df['avg_value_usd'].corr(df['discrepancy_pct'], method='spearman'):.3f}")
    print(f"\nMalaysia-US edge ($47.3B, 2023) falls in the 'large' band: "
          f"expect ~{large['discrepancy_pct'].median():.0f}% typical discrepancy, "
          f"not the full 3-242% range seen in small flows.")


if __name__ == "__main__":
    main()
