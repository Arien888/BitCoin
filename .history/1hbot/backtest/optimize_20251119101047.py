import pandas as pd
import numpy as np
from technicals import run_backtest_one


def optimize_buy_conditions(df):

    # 探索範囲
    ma_list  = list(range(1, 201, 10))   # MA: 1,11,21,...191
    rng_list = list(range(1, 201, 10))   # Range: same

    tp_list =  [round(x, 3) for x in np.arange(0.001, 1.001, 0.001)]  # TP 0.001〜1.000
    sl_list =  [round(x, 3) for x in np.arange(0.001, 1.001, 0.001)]  # SL 0.001〜1.000

    range_pos_thr = 0.40   # 最強のBUY条件

    print("===== FULL BUY CONDITION OPTIMIZATION =====\n")
    print("ma | rng | tp | sl | trades | profit | winrate")

    print("-" * 70)

    best = None

    for ma in ma_list:
        for rng in rng_list:
            for tp in tp_list:
                for sl in sl_list:

                    trades, total, win, avg, dd = run_backtest_one(
                        df.copy(), ma, rng, tp, sl,
                        range_pos_thr=range_pos_thr
                    )

                    print(f"{ma:3d} | {rng:3d} | {tp:5.3f} | {sl:5.3f} | "
                          f"{trades:3d} | {total:7.3f} | {win*100:6.2f}%")

                    # ベスト保存
                    if best is None or total > best["total"]:
                        best = {
                            "ma": ma,
                            "rng": rng,
                            "tp": tp,
                            "sl": sl,
                            "total": total,
                            "win": win,
                            "trades": trades
                        }

    print("\n===== 最強パラメータ =====")
    print(best)


if __name__ == "__main__":
    df = pd.read_csv("btc_1h_full.csv")
    for col in ["open", "high", "low", "close"]:
        df[col] = df[col].astype(float)

    optimize_buy_conditions(df)
