# -*- coding: utf-8 -*-
"""
Collects bilateral trade for every network country that UN Comtrade's free
tier never returns as a reporter, added after external review.

USA and India were already known and documented (UN Comtrade's free/
unauthenticated tier structurally excludes them entirely -- see
docs/LIMITATIONS.md item 1, docs/SOURCES.md). While building the fix for
those two, this script's development surfaced TWO MORE countries with the
same problem, previously undocumented: Belgium and Ethiopia returned zero
rows as a reporter for every flow/period in the original Comtrade collection
(count=0, no error, confirmed by inspecting the cached raw JSON responses
directly, data/raw/comtrade_network/r58_*.json and r230_*.json) -- and
critically, neither ever appears as a PARTNER in any other country's
reported data either, meaning they were 100% absent from the network, not
merely excluded from certain calculations the way USA/India's absence was
already known and documented. This was found by actually verifying the
"57 of 59" framing used throughout this project's docs against the raw
data, not by assuming it was correct.

REPORTERS below is therefore ["USA", "IND", "BEL", "ETH"] -- every country
in the 59-country target list with zero rows as a Comtrade reporter, found
by direct verification, not just the two that were already known about.

Source: OECD's Bilateral Trade in Goods by End-use (BTiGE) database, via
OECD's public SDMX API (sdmx.oecd.org). Requires NO API key and NO
registration (every query below returns HTTP 200 with no auth header).
BTiGE is built by OECD from UN Comtrade data using OECD's own institutional
access, then redistributed through OECD's own free public endpoint -- a
different door to substantially the same underlying data. See
docs/SOURCES.md for the real-world plausibility checks run on all four
countries before trusting this (USA and India checked against several
independently published bilateral figures; Belgium's exports to China and
Ethiopia's exports to China both checked as individually plausible given
each country's known total trade scale).

Endpoint: https://sdmx.oecd.org/sti-public/rest/data/OECD.STI.PIE,DSD_BTIGE@DF_BTIGE,1.0/...
Key structure (confirmed via the dataflow's own DSD, not guessed):
    FREQ.REF_AREA.TRADE_FLOW.END_USE.PRODUCT.COUNTERPART_AREA.UNIT_MEASURE
  - FREQ=A (annual), END_USE=TOTAL, PRODUCT=_T (all products), UNIT_MEASURE=USD
  - REF_AREA = the reporter being backfilled (USA, IND, BEL, or ETH)
  - COUNTERPART_AREA supports "+"-joined multi-value queries, confirmed to
    return all requested partners in ONE call, so this needs only
    4 reporters x 2 flows x 2 periods = 16 total API calls for full coverage
    against all other network countries.
  - UNIT_MULT is returned as an explicit series attribute (value "3" =
    Thousands, confirmed directly from the API response, not assumed), so
    every value is multiplied by 1,000 here to convert to raw USD, matching
    UN Comtrade's own primaryValue convention for schema compatibility.

Why this alone gives FULL bidirectional coverage for these four countries:
a reporter's own EXPORT data gives the reporter->partner edge directly;
that same reporter's own IMPORT data gives the partner->reporter edge (a
"mirror" statistic, but an authoritative one: sourced from the receiving
country's own customs records). So pulling both flows for all four
reporters, against every other network country, covers every directed edge
touching any of them, without needing anything from the other countries'
own Comtrade data.

Output is kept as a separate raw file (data/raw/oecd_missing_reporters_raw.
csv), NOT merged into comtrade_bilateral_trade_raw.csv, so that file stays
exactly what its name and the README's Reproducibility section describe:
the pure, unmodified output of comtrade_network.py. The merge into one
analysis-ready network file happens in python/cleaning/merge_bilateral_trade.py,
which tags every row with its source (UN_COMTRADE vs OECD_BTIGE) so the two
are never silently blended.
"""
import requests
import pandas as pd
import time
import os
import json

OUT_RAW_DIR = os.path.join("data", "raw", "oecd_missing_reporters")
os.makedirs(OUT_RAW_DIR, exist_ok=True)

BASE = "https://sdmx.oecd.org/sti-public/rest/data/OECD.STI.PIE,DSD_BTIGE@DF_BTIGE,1.0"
PERIODS = ["2016", "2023"]
FLOWS = {"X": "export", "M": "import"}
REPORTERS = ["USA", "IND", "BEL", "ETH"]  # ISO3 codes; every country with zero rows as a Comtrade reporter


def fetch(reporter_iso3, flow, period, partner_codes_csv):
    key = f"A.{reporter_iso3}.{flow}.TOTAL._T.{partner_codes_csv}.USD"
    url = f"{BASE}/{key}"
    params = {"startPeriod": period, "endPeriod": period, "format": "jsondata"}
    for attempt in range(6):
        try:
            resp = requests.get(url, params=params, timeout=60)
        except requests.exceptions.ConnectionError:
            time.sleep(3 + attempt * 2)
            continue
        if resp.status_code == 429:
            time.sleep(2 + attempt)
            continue
        if resp.status_code == 404:
            return None  # NoResultsFound for this exact key combination
        resp.raise_for_status()
        return resp.json()
    raise RuntimeError(f"Retries exhausted for reporter={reporter_iso3} flow={flow} period={period}")


def parse_response(payload, reporter_iso3, flow, period, iso3_to_comtrade_code):
    """Parses the SDMX-JSON response into (period, flow, reporterCode, partnerCode,
    primaryValue) rows, converting thousands -> raw USD via UNIT_MULT."""
    if payload is None:
        return []
    ds = payload["data"]["dataSets"][0]
    series_dict = ds["series"]
    structures = payload["data"]["structures"][0]
    dims = structures["dimensions"]["series"]
    counterpart_dim = next(d for d in dims if d["id"] == "COUNTERPART_AREA")
    counterpart_values = [v["id"] for v in counterpart_dim["values"]]
    counterpart_position = dims.index(counterpart_dim)

    reporter_code = iso3_to_comtrade_code.get(reporter_iso3)
    rows = []
    for series_key, series_val in series_dict.items():
        indices = [int(i) for i in series_key.split(":")]
        counterpart_iso3 = counterpart_values[indices[counterpart_position]]
        partner_code = iso3_to_comtrade_code.get(counterpart_iso3)
        if partner_code is None or partner_code == reporter_code:
            continue  # counterpart not in our 59-country network list, or self-pair, skip
        obs = series_val.get("observations", {})
        if not obs:
            continue
        value_thousands = list(obs.values())[0][0]
        if value_thousands is None:
            continue
        rows.append({
            "period": period, "flow": flow,
            "reporterCode": reporter_code, "partnerCode": partner_code,
            "primaryValue": value_thousands * 1000.0,  # UNIT_MULT=3 (Thousands), confirmed via API metadata
        })
    return rows


def main():
    countries = pd.read_csv("data/external/network_countries.csv")
    iso3_to_comtrade_code = dict(zip(countries["ISO3"], countries["comtradeReporterCode"]))
    all_iso3 = countries["ISO3"].tolist()

    all_rows = []
    total_calls = len(REPORTERS) * len(FLOWS) * len(PERIODS)
    call_n = 0
    for period in PERIODS:
        for flow in FLOWS:
            for reporter in REPORTERS:
                call_n += 1
                # Partner list = every other network country EXCEPT this one reporter
                # itself (not the other three REPORTERS too) -- so edges between the
                # four backfilled countries (e.g. USA<->India) are captured, rather
                # than silently dropped by treating all four as mutually excluded.
                partner_codes_csv = "+".join(c for c in all_iso3 if c != reporter)
                cache_path = os.path.join(OUT_RAW_DIR, f"{reporter}_{flow}_{period}.json")
                if os.path.exists(cache_path):
                    payload = json.load(open(cache_path, encoding="utf-8"))
                else:
                    payload = fetch(reporter, flow, period, partner_codes_csv)
                    with open(cache_path, "w", encoding="utf-8") as f:
                        json.dump(payload, f)
                    time.sleep(1.0)
                rows = parse_response(payload, reporter, flow, period, iso3_to_comtrade_code)
                all_rows.extend(rows)
                print(f"[{call_n}/{total_calls}] reporter={reporter} flow={flow} period={period} "
                      f"rows={len(rows)}", flush=True)

    df = pd.DataFrame(all_rows)
    df.to_csv("data/raw/oecd_missing_reporters_raw.csv", index=False)
    print(f"\nSaved data/raw/oecd_missing_reporters_raw.csv: {df.shape}")
    print(df.groupby(["period", "flow"]).size())
    print("\nReporters covered:", sorted(df["reporterCode"].unique().tolist()))


if __name__ == "__main__":
    main()
