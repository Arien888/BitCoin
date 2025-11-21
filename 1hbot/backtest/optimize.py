import pandas as pd
import numpy as np
from technicals import run_backtest_one


# ---------------------------------------------------------
# 期間分割
# ---------------------------------------------------------
def split_into_periods(df, months=3):
    df = df.sort_values("ts")
    rows = months * 30 * 24  # 720本 / 月

    periods = []
    for start in range(0, len(df), rows):
        chunk = df.iloc[start:start+rows].copy()
        if len(chunk) > 100:
            periods.append(chunk)

    return periods


# ---------------------------------------------------------
# 単期間最適化（高速バージョン）
# ---------------------------------------------------------
def optimize_fine(df, top_n=50):

    # ★ brute-force → 最適化済み範囲
    ma_list        = list(range(10, 120, 15))
    range_lb_list  = list(range(10, 120, 15))

    tp_list = [round(x, 4) for x in np.arange(0.002, 0.014, 0.002)]
    sl_list = [round(x, 4) for x in np.arange(0.004, 0.020, 0.002)]

    ma_dc_list   = [round(x, 3) for x in np.arange(0.005, 0.030, 0.005)]

    low_thr_list  = [round(x, 2) for x in np.linspace(0.10, 0.40, 7)]
    high_thr_list = [round(x, 2) for x in np.linspace(0.60, 0.90, 7)]

    results = []

    for ma in ma_list:
        for rng in range_lb_list:
            for tp in tp_list:
                for sl in sl_list:
                    for ma_dc in ma_dc_list:
                        for low_thr in low_thr_list:
                            for high_thr in high_thr_list:

                                # ★ df.copy() はしない（激速化）
                                trades, total, win, avg, dd = run_backtest_one(
                                    df, ma, rng, tp, sl, ma_dc, low_thr, high_thr
                                )

                                if trades < 25:
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

    # 利益順
    results.sort(key=lambda x: x["total"], reverse=True)

    # 表示
    print(f"\n=== {len(results)} 通りが有効 ===")
    print(f"=== TOP{top_n} ===")
    for r in results[:top_n]:
        print(
            f"MA={r['ma']:>3}, RNG={r['range']:>3}, TP={r['tp']}, SL={r['sl']}, "
            f"ma_dc={r['ma_dc']}, low={r['low_thr']}, high={r['high_thr']} | "
            f"Trades={r['trades']}, P/L={r['total']:.3f}, Win={r['winrate']*100:.1f}%, "
            f"DD={r['maxdd']:.3f}"
        )

    return results[:top_n]


# ---------------------------------------------------------
# 全期間の共通パラメータ抽出（修正版）
# ---------------------------------------------------------
def intersect_best(all_results):
    # 各期間のTOP50 → set にしやすい形に変換
    set_list = []
    for lst in all_results:
        s = set()
        for r in lst:
            key = (
                r["ma"], r["range"], r["tp"], r["sl"],
                r["ma_dc"], r["low_thr"], r["high_thr"]
            )
            s.add(key)
        set_list.append(s)

    # 共通
    common_keys = set.intersection(*set_list)

    # dictに戻す
    common = []
    for key in common_keys:
        ma, rng, tp, sl, ma_dc, low_thr, high_thr = key
        common.append({
            "ma": ma,
            "range": rng,
            "tp": tp,
            "sl": sl,
            "ma_dc": ma_dc,
            "low_thr": low_thr,
            "high_thr": high_thr
        })

    return common


# ---------------------------------------------------------
# マルチ期間最適化
# ---------------------------------------------------------
def optimize_multi_period(df, months=3):

    periods = split_into_periods(df, months)
    all_results = []

    print(f"=== {len(periods)} 個の期間で最適化 ===")

    for i, p in enumerate(periods):
        print(f"\n--- 期間 {i+1} ---")
        best = optimize_fine(p, top_n=50)
        all_results.append(best)

    # ★ 共通パラメータ
    print("\n=== 全期間で共通して強いパラメータ ===")
    robust = intersect_best(all_results)

    for r in robust[:20]:
        print(r)

    return robust


# ---------------------------------------------------------
# 実行部
# ---------------------------------------------------------
if __name__ == "__main__":
    df = pd.read_csv("btc_1h_full.csv")
    df["ts"] = pd.to_datetime(df["ts"])

    for col in ["open", "high", "low", "close"]:
        df[col] = df[col].astype(float)

    optimize_multi_period(df, months=3)
