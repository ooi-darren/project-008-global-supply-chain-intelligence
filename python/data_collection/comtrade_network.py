# -*- coding: utf-8 -*-
"""
UN Comtrade bilateral trade collection for Project 008.

Source: UN Comtrade "preview" API (comtradeapi.un.org/public/v1/preview/...),
which is queryable without an API key/subscription, unlike the full data API
(comtradeapi.un.org/data/v1/...) which returns HTTP 401 without one. This is
a real, documented distinction discovered during data discovery, not an
assumption -- see docs/SOURCES.md.

Rate limit: empirically ~1 request/second (HTTP 429 "Rate limit is exceeded.
Try again in 1 seconds." observed on faster polling).

Network scope: 59 major economies (see data/external/network_countries.csv,
built as the top-10-by-GDP economies per Project 007 region, minus small
non-sovereign/negligible-trade entities, to keep the network analytically
meaningful rather than exhaustively covering all ~200 UN Comtrade reporters).
For each reporter, ONE API call per (flow, period) requests all 58 other
network members as comma-separated partners simultaneously -- verified to
work in one call rather than 58 separate calls (see discovery notes).

CRITICAL DATA-QUALITY FIX (two independent double-counting traps found and
fixed during discovery, verified against each other, not assumed):
  1. Each row also carries a `motCode` (transport mode) dimension, where
     motCode=0 is the AGGREGATE across all transport modes and motCode in
     {1000, 2000, 3200, ...} are its breakdown -- confirmed by checking that
     the motCode=0 value equals the sum of the non-zero motCode rows almost
     exactly for a test case (Malaysia->China 2023).
  2. Independently, rows also carry a `partner2Code` (re-export/transit
     country) dimension for reporters with detailed re-export tracking (e.g.
     China): partner2Code=0 is the direct/aggregate total, and non-zero
     partner2Code rows are a breakdown by transit country that would also
     double-count if summed. Confirmed by inspecting China->Argentina 2016,
     which returned 13 rows for one partner -- one large value at
     partner2Code=0 and twelve small residual values at specific transit
     partner2Codes.
A THIRD, independent breakdown dimension was found after the first two:
`customsCode` (customs procedure regime), where C00 is the general/aggregate
total and C01/C02/C04/C06/C20 etc. are its breakdown by specific customs
procedure -- verified the same way as the other two (Spain's 2016 imports
from partner 124 showed C00=1,440,995,000 which equals the sum of its five
non-C00 rows to within rounding). Only detailed reporters (Spain, China,
Germany...) report this breakdown at all; most reporters only ever return
C00, which is why the bug was invisible until a mid-sized reporter surfaced
266 rows for 58 possible partners partway through a collection run.

Rather than requesting everything and filtering client-side (which silently
truncates for high-volume reporters like China, whose combined motCode +
partner2Code breakdown rows for 58 partners exceed the API's ~500-row page
cap, crowding out the very aggregate rows needed -- verified: China's 2016
imports returned exactly 500 rows with ZERO surviving a motCode/partner2Code-
only client-side filter), motCode=0, partner2Code=0, AND customsCode=C00 are
all passed as explicit server-side query parameters, confirmed to return
exactly one clean row per partner with no breakdown noise at all.

Periods: 2016 (pre-COVID baseline) and 2023 (most recent complete year with
good reporting coverage) -- supports the structural-change-since-2016
analysis without needing every intermediate year for the network itself
(intermediate years are pulled separately, aggregated/world-total level only,
for time-series/structural-break analysis -- see world_trade_timeseries.py).
"""
import requests
import pandas as pd
import time
import os
import json

OUT_RAW = os.path.join("data", "raw", "comtrade_network")
os.makedirs(OUT_RAW, exist_ok=True)

BASE = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"
PERIODS = ["2016", "2023"]
FLOWS = {"X": "export", "M": "import"}


def fetch_reporter(reporter_code, partner_codes_csv, period, flow):
    params = {
        "reporterCode": reporter_code,
        "period": period,
        "partnerCode": partner_codes_csv,
        "cmdCode": "TOTAL",
        "flowCode": flow,
        "motCode": 0,
        "partner2Code": 0,
        "customsCode": "C00",
    }
    session = requests.Session()
    for attempt in range(8):
        try:
            resp = session.get(BASE, params=params, timeout=60)
        except requests.exceptions.ConnectionError:
            time.sleep(3 + attempt * 2)
            continue
        if resp.status_code == 429:
            time.sleep(2 + attempt)
            continue
        resp.raise_for_status()
        return resp.json()
    raise RuntimeError(f"Retries exhausted for reporter={reporter_code} period={period} flow={flow}")


def main():
    countries = pd.read_csv("data/external/network_countries.csv")
    codes = countries["comtradeReporterCode"].astype(int).tolist()
    codes_csv = ",".join(str(c) for c in codes)

    all_rows = []
    total_calls = len(codes) * len(PERIODS) * len(FLOWS)
    call_n = 0
    for period in PERIODS:
        for flow in FLOWS:
            for reporter in codes:
                call_n += 1
                cache_path = os.path.join(OUT_RAW, f"r{reporter}_{flow}_{period}.json")
                if os.path.exists(cache_path):
                    payload = json.load(open(cache_path, encoding="utf-8"))
                else:
                    payload = fetch_reporter(reporter, codes_csv, period, flow)
                    with open(cache_path, "w", encoding="utf-8") as f:
                        json.dump(payload, f)
                    time.sleep(1.1)
                data = payload.get("data", [])
                kept = 0
                for row in data:
                    if row.get("motCode") != 0 or row.get("partner2Code") != 0 or row.get("customsCode") != "C00":
                        continue  # skip transport-mode, re-export/transit, and customs-procedure breakdown rows
                    kept += 1
                    all_rows.append({
                        "period": period,
                        "flow": flow,
                        "reporterCode": row["reporterCode"],
                        "partnerCode": row["partnerCode"],
                        "primaryValue": row["primaryValue"],
                    })
                print(f"[{call_n}/{total_calls}] reporter={reporter} flow={flow} period={period} "
                      f"raw_rows={len(data)} rows_kept={kept}", flush=True)

    df = pd.DataFrame(all_rows)
    df = df[df["partnerCode"] != 0]  # drop any accidental world-total rows
    df.to_csv("data/raw/comtrade_bilateral_trade_raw.csv", index=False)
    print(f"\nSaved data/raw/comtrade_bilateral_trade_raw.csv: {df.shape}")
    print(df.groupby(["period", "flow"]).size())


if __name__ == "__main__":
    main()
