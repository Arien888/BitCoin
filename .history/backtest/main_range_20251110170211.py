import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import product
from concurrent.futures import ProcessPoolExecutor, as_completed

# --- compute_threshold, get_thresholds, backtest_full_strategy_repeat はそのまま ---

# 並列実行用のラッパー関数
def backtest_wrapper(params):
    ma, lb, bm, bp, sm, sp, df = params
    res = backtest_full_strategy_repeat(df, ma, lb, bm, bp, sm, sp)
    res.update({
        "MA": ma,
        "Lookback": lb,
        "Buy_MA": bm,
        "Buy_Prev": bp,
        "Sell_MA": sm,
        "Sell_Prev": sp,
    })
    return res

if __name__ == "__main__":
    symbol = "btc"
    df = pd.read_csv(f"{symbol}.csv")
    df["日付け"] = pd.to_datetime(df["日付け"])
    df.set_index("日付け", inplace=True)
    for col in ["終値", "高値", "安値"]:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors="coerce")

    ma_list = range(11, 17)
    lookback_list = range(11, 17)
    methods = [
        "mean_above_mean", "median_above_mean",
        "mean_below_mean", "median_below_mean",
        "mean_above_median", "median_above_median",
        "mean_below_median", "median_below_median"
    ]

    # 全組み合わせ
    param_list = [(ma, lb, bm, bp, sm, sp, df) 
                  for ma, lb, bm, bp, sm, sp in product(ma_list, lookback_list, methods, methods, methods, methods)]

    results = []
    # CPUコア数を自動判定して並列処理
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(backtest_wrapper, p) for p in param_list]
        for f in as_completed(futures):
            results.append(f.result())

    result_df = pd.DataFrame(results)
    result_df.sort_values("profit_percent", ascending=False, inplace=True)

    print("\n=== 上位パラメータ ===")
    print(result_df.head(10)[["MA", "Lookback", "Buy_MA", "Sell_MA", "profit_percent", "max_drawdown", "trade_count", "avg_trade_profit"]])

    # --- 可視化 ---
    plt.figure(figsize=(10, 5))
    plt.scatter(result_df["MA"], result_df["profit_percent"], label="Profit%")
    plt.title("MA期間と利益率の関係")
    plt.xlabel("MA Period")
    plt.ylabel("Profit %")
    plt.grid(True)
    plt.legend()
    plt.show()
