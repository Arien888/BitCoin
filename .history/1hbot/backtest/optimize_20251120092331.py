import pandas as pd
import numpy as np
from technicals import run_backtest_one


# ---------------------------------------------------------
# 期間分割
# ---------------------------------------------------------
def split_into_periods(df, months=3):
    df = df.sort_values("ts")
    rows_per_period = months * 30 * 24  # 1h足 = 720行/月

    periods = []
    for start in range(0, len(df), rows_per_period):
        end = start + rows_per_period
        chunk = df.iloc[start:end].copy()
        if len(chunk) > 100:     # 小さすぎる期間は除外
            periods.append(chunk)

    return periods


# ---------------------------------------------------------
# 単期間の詳細最適化（戻り値あり）
# ---------------------------------------------------------
def optimize_fine(df, top_n=50):

    ma_list        = list(range(5, 205, 20))
    range_lb_list  = list(range(10, 210, 20))

    tp_list = [round(x, 4) for x in np.arange(0.001, 0.021, 0.002)]
    sl_list = [round(x, 4) for x in np.arange(0.002, 0.031, 0.002)]

    ma_dc_list   = [round(x, 3) for x in np.arange(0.003, 0.051, 0.005)]

    low_thr_list  = [round(x, 2) for x in np.linspace(0.10, 0.50, 9)]
    high_thr_list = [round(x, 2) for x in np.linspace(0.50, 0.90, 9)]


    results = []

    for ma in ma_list:
        for rng in range_lb_list:
            for tp in tp_list:
                for sl in sl_list:
                    for ma_dc in ma_dc_list:
                        for low_thr in low_thr_list:
                            for high_thr in high_thr_list:

                                trades, total, win, avg, dd = run_backtest_one(
                                    df,
                                    ma, rng, tp, sl,
                                    ma_dc, low_thr, high_thr
                                )

                                if trades < 30:
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

    # ソート（利益順）
    results = sorted(results, key=lambda x: x["total"], reverse=True)

    # print表示
    print(f"\n=== {len(results)} 通りが有効 ===")
    print(f"=== 最強パラメータ TOP{top_n} ===")

    for r in results[:top_n]:
        print(
            f"MA={r['ma']:>2}, RNG={r['range']:<3}, TP={r['tp']}, SL={r['sl']}, "
            f"ma_dc={r['ma_dc']}, low_thr={r['low_thr']}, high_thr={r['high_thr']} | "
            f"Trades={r['trades']}, P/L={r['total']:.3f}, Win={r['winrate']*100:.1f}%, "
            f"DD={r['maxdd']:.3f}"
        )

    return results[:top_n]   # ← ★ 必ず上位パラメータを返す


# ---------------------------------------------------------
# 共通強パラメータ抽出
# ---------------------------------------------------------
def intersect_best(all_results):

    # set に変換
    sets = [
        set(tuple(sorted(r.items())) for r in period)
        for period in all_results
    ]

    # すべての期間の共通集合
    common = set.intersection(*sets)

    # dict に戻す
    result = [dict(items) for items in common]

    # 利益順で並べる
    return sorted(result, key=lambda x: x["total"], reverse=True)


# ---------------------------------------------------------
# マルチ期間最適化
# ---------------------------------------------------------
def optimize_multi_period(df, months=3):

    periods = split_into_periods(df, months)
    all_results = []

    print(f"=== {len(periods)} 個の期間で最適化 ===")

    for idx, p in enumerate(periods):
        print(f"\n--- 期間 {idx+1} ---")
        best = optimize_fine(p, top_n=50)
        all_results.append(best)

    print("\n=== 全期間で共通の強パラメータ ===")
    robust = intersect_best(all_results)

    if not robust:
        print("共通して強いパラメータはありませんでした")
    else:
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
