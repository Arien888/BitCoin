import pandas as pd
import numpy as np
from technicals import run_backtest_one


# -----------------------------------------
# 期間分割（変えなくてOK）
# -----------------------------------------
def split_into_periods(df, months=3):
    df = df.sort_values("ts")
    rows = months * 30 * 24

    periods = []
    for start in range(0, len(df), rows):
        chunk = df.iloc[start:start+rows].copy()
        if len(chunk) > 200:
            periods.append(chunk)

    return periods


# -----------------------------------------
# 高速・少数精鋭パラメータセット
# -----------------------------------------
MA_LIST       = [21, 33, 48, 60, 72, 84]
RANGE_LIST    = [24, 36, 48, 60, 72, 84, 96]

TP_LIST       = [0.004, 0.006, 0.008]
SL_LIST       = [0.008, 0.012, 0.016]

MA_DC_LIST    = [0.01, 0.02]
LOW_THR_LIST  = [0.20, 0.30, 0.40]
HIGH_THR_LIST = [0.60, 0.75, 0.90]


# -----------------------------------------
# 1期間最適化（爆速版）
# -----------------------------------------
def optimize_fine(df, top_n=20):

    results = []

    for ma in MA_LIST:
        for rng in RANGE_LIST:
            for tp in TP_LIST:
                for sl in SL_LIST:
                    for ma_dc in MA_DC_LIST:
                        for low_thr in LOW_THR_LIST:
                            for high_thr in HIGH_THR_LIST:

                                trades, total, win, avg, dd = run_backtest_one(
                                    df, ma, rng, tp, sl, ma_dc, low_thr, high_thr
                                )

                                if trades < 20:
                                    continue

                                results.append({
                                    "ma": ma,
                                    "range": rng,
                                    "tp": tp,
                                    "sl": sl,
                                    "ma_dc": ma_dc,
                                    "low_thr": low_thr,
                                    "high_thr": high_thr,
                                    "trades": trades,
                                    "total": total,
                                    "winrate": win,
                                    "avg": avg,
                                    "maxdd": dd
                                })

    results.sort(key=lambda x: x["total"], reverse=True)

    print(f"\n=== {len(results)} 通りが有効 ===")
    for r in results[:top_n]:
        print(r)

    return results[:top_n]


# -----------------------------------------
# 共通パラメータ抽出
# -----------------------------------------
def intersect_best(all_results):

    sets = []
    for period in all_results:
        s = {
            (r["ma"], r["range"], r["tp"], r["sl"], r["ma_dc"], r["low_thr"], r["high_thr"])
            for r in period
        }
        sets.append(s)

    common = set.intersection(*sets)

    final = []
    for ma, rng, tp, sl, ma_dc, low_thr, high_thr in common:
        final.append({
            "ma": ma,
            "range": rng,
            "tp": tp,
            "sl": sl,
            "ma_dc": ma_dc,
            "low_thr": low_thr,
            "high_thr": high_thr
        })

    return final


# -----------------------------------------
# マルチ期間最適化
# -----------------------------------------
def optimize_multi_period(df, months=3):

    periods = split_into_periods(df, months)
    all_results = []

    for i, p in enumerate(periods):
        print(f"\n--- 期間 {i+1}/{len(periods)} ---")
        best = optimize_fine(p)
        all_results.append(best)

    print("\n=== 全期間共通パラメータ ===")
    robust = intersect_best(all_results)
    for r in robust:
        print(r)

    return robust


# -----------------------------------------
# 実行
# -----------------------------------------
if __name__ == "__main__":
    df = pd.read_csv("btc_1h_full.csv")
    df["ts"] = pd.to_datetime(df["ts"])

    for c in ["open", "high", "low", "close"]:
        df[c] = df[c].astype(float)

    optimize_multi_period(df, months=3)
