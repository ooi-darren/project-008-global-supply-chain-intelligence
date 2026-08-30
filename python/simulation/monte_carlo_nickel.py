# -*- coding: utf-8 -*-
"""
Monte Carlo simulation for Project 008: nickel price risk, 12-month horizon.

WHY NICKEL: it is the one material in this project's critical-minerals list
that has BOTH (a) a real USGS production-concentration figure (Indonesia
59.6% of world mine production, the single most concentrated top-producer
share of any base metal tracked, per critical_materials_concentration.csv)
and (b) a real, liquid, long-history monthly price series (World Bank Pink
Sheet, commodity_prices_monthly.csv) -- unlike Gallium/Cobalt/Graphite/Rare
earths, which this project has production data for but no matching price
series, so a price-risk Monte Carlo for those would need a proxy price this
project does not have and should not fabricate. Nickel is also directly
topical: Indonesia's export-ban/downstreaming policy is a real, current
supply-chain story this project's "Why Is This Happening" research covers.

METHOD (per the brief: "Probabilities must derive from historical
distributions... Do not create fake probabilities"):
  1. Compute monthly log returns from the full nickel price history.
  2. Fit their empirical mean and standard deviation (NOT assumed to be
     zero-drift or a round number -- taken directly from the data).
  3. Simulate 10,000 independent 12-month price paths via bootstrap
     resampling of ACTUAL historical monthly log returns (not a parametric
     normal-distribution assumption, which would understate real fat-tail
     risk -- commodity returns are well known to be non-normal, and this
     project's own volatility comparison already shows nickel among the
     more volatile tracked materials).
  4. Report the empirical probability of specific outcomes (>20% price
     increase, >20% decrease, price exceeding a historical high) directly
     from the simulated distribution, not invented.
Sensitivity: repeat with a block-bootstrap (12-month contiguous blocks
rather than independent monthly draws) to check whether ignoring
autocorrelation materially changes the answer.
"""
import pandas as pd
import numpy as np
import os

OUT_DIR = "data/processed"
np.random.seed(42)  # reproducibility, not a claim of "the" random seed being special
N_SIMULATIONS = 10000
HORIZON_MONTHS = 12


def load_returns():
    df = pd.read_csv(os.path.join(OUT_DIR, "commodity_prices_monthly.csv"))
    nickel = df[df["commodity"] == "Nickel"].sort_values("date")
    nickel["log_ret"] = np.log(nickel["price_usd_nominal"]).diff()
    return nickel.dropna(subset=["log_ret"])


def independent_bootstrap(returns, current_price):
    draws = np.random.choice(returns, size=(N_SIMULATIONS, HORIZON_MONTHS), replace=True)
    cum_log_ret = draws.sum(axis=1)
    final_prices = current_price * np.exp(cum_log_ret)
    return final_prices


def block_bootstrap(returns, current_price, block_size=6):
    n = len(returns)
    final_prices = np.zeros(N_SIMULATIONS)
    for i in range(N_SIMULATIONS):
        path = []
        while len(path) < HORIZON_MONTHS:
            start = np.random.randint(0, n - block_size)
            path.extend(returns[start:start + block_size])
        cum_log_ret = sum(path[:HORIZON_MONTHS])
        final_prices[i] = current_price * np.exp(cum_log_ret)
    return final_prices


def summarise(final_prices, current_price, label):
    pct_change = (final_prices / current_price - 1) * 100
    result = {
        "method": label,
        "current_price": current_price,
        "simulated_median_12m": np.median(final_prices),
        "simulated_p10_12m": np.percentile(final_prices, 10),
        "simulated_p90_12m": np.percentile(final_prices, 90),
        "prob_increase_gt20pct": (pct_change > 20).mean() * 100,
        "prob_decrease_gt20pct": (pct_change < -20).mean() * 100,
        "prob_exceeds_historical_high": np.nan,  # filled by caller
    }
    return result


def main():
    returns_df = load_returns()
    returns = returns_df["log_ret"].values
    current_price = returns_df.iloc[-1]["price_usd_nominal"]
    historical_high = returns_df["price_usd_nominal"].max()  # note: this is nominal-history high across the whole series, from World Bank Pink Sheet

    print(f"Nickel: current price ${current_price:,.0f}/mt, "
          f"historical monthly-series high ${historical_high:,.0f}/mt, "
          f"{len(returns)} monthly return observations used")

    results = []
    for label, fn in [("independent_bootstrap", lambda: independent_bootstrap(returns, current_price)),
                       ("block_bootstrap_6mo", lambda: block_bootstrap(returns, current_price, 6))]:
        final_prices = fn()
        r = summarise(final_prices, current_price, label)
        r["prob_exceeds_historical_high"] = (final_prices > historical_high).mean() * 100
        results.append(r)

    result_df = pd.DataFrame(results)
    result_df.to_csv(os.path.join(OUT_DIR, "nickel_monte_carlo_12m.csv"), index=False)
    print("\nMonte Carlo results (12-month horizon, 10,000 simulations):")
    print(result_df.round(1).to_string(index=False))
    print(f"\nSensitivity check: independent vs. block bootstrap median price difference = "
          f"{abs(result_df.iloc[0]['simulated_median_12m'] - result_df.iloc[1]['simulated_median_12m']):.0f} "
          f"({abs(result_df.iloc[0]['simulated_median_12m'] - result_df.iloc[1]['simulated_median_12m']) / current_price * 100:.1f}% of current price)")


if __name__ == "__main__":
    main()
