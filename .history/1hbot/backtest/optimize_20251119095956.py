import pandas as pd
import numpy as np
from technicals import run_backtest_one


def print_buy_condition_table(df):

    # 固定（まずは BUY 条件だけ評価）
    ma = 48
    rng = 48
    tp = 0.01
    sl = 0.01

    # BUY条件の検索範囲
    buy_ma_ratio_list = [round(x, 2) for x in np.arange(0.7, 1.01, 0.05)]
    range_pos_thr_list = [round(x, 2) for x in np.arange(0.1, 0.51, 0.05)]

    print("===== BUY Condition Optimization (profit table) =====\n")

    # 上部ヘッダー
    header = "ma_ratio \\ range_pos | " + " | ".join([f"{thr:.2f}" for thr in range_pos_thr_list])
    print(header)
    print("-" * len(header))

    # 表本体
    for ma_ratio in buy_ma_ratio_list:

        row_str = f"{ma_ratio:.2f}".ljust(22)

        for range_thr in range_pos_thr_list:

            trades, total, win, avg, dd = run_backtest_one(
                df.copy(), ma, rng, tp, sl, ma_ratio, range_thr
            )

            row_str += f"{total:6.3f} | "

        print(row_str)

    print("\n===== 完了 =====")


if __name__ == "__main__":
    df = pd.read_csv("btc_1h_full.csv")
    for col in ["open", "high", "low", "close"]:
        df[col] = df[col].astype(float)

    print_buy_condition_table(df)
