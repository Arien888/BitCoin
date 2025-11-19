import pandas as pd
from technicals import run_backtest_one
import numpy as np


def optimize(df, top_n=20):

    # --- SL: 0.001 ~ 1.0 を 0.01刻み ---
    sl_list = [round(x, 4) for x in np.arange(0.001, 1.0001, 0.01)]

    # --- TP: 0.001 ~ 1.0 を 0.01刻み（※誤りを修正）---
    tp_list = [round(x, 4) for x in np.arange(0.001, 1.0001, 0.01)]

    # --- MA & Range ---
    ma_list = list(range(1, 201, 20))
    range_list = list(range(1, 201, 20))

    # --- BUY条件の最適化 ---
    buy_ma_ratio_list = [round(x, 1) for x in np.arange(0.1, 1.01, 0.1)]   # 0.1〜1.0
    range_pos_thr_list = [round(x, 1) for x in np.arange(0.1, 1.01, 0.1)]  # 0.1〜1.0

    results = []

    for ma in ma_list:
        for rng in range_list:
            for tp in tp_list:
                for sl in sl_list:
                    for ma_ratio in buy_ma_ratio_list:
                        for range_thr in range_pos_thr_list:

                            trades, total, win, avg, dd = run_backtest_one(
                                df.copy(),
                                ma,
                                rng,
                                tp,
                                sl,
                                ma_ratio,
                                range_thr
                            )

                            results.append({
                                "ma": ma,
                                "range": rng,
                                "tp": tp,
                                "sl": sl,
                                "ma_ratio": ma_ratio,
                                "range_thr": range_thr,
                                "trades": trades,
                                "total": total,
                                "winrate": win,
                                "avg": avg,
                                "maxdd": dd
                            })

    # ---- sort (P/L 優先) ----
    results.sort(key=lambda x: x["total"], reverse=True)

    print("\n===== TOP パラメータ候補 =====")
    for r in results[:top_n]:
        print(
            f"MA={r['ma']}, Range={r['range']}, TP={r['tp']}, SL={r['sl']}, "
            f"MA_ratio={r['ma_ratio']}, range_thr={r['range_thr']} | "
            f"Trades={r['trades']}, P/L={r['total']:.3f}, "
            f"Win={r['winrate']*100:.1f}%, Avg={r['avg']:.3f}, "
            f"MaxDD={r['maxdd']:.3f}"
        )


if __name__ == "__main__":
    df = pd.read_csv("btc_1h_full.csv")
    for col in ["open", "high", "low", "close"]:
        df[col] = df[col].astype(float)

    optimize(df, top_n=20)
