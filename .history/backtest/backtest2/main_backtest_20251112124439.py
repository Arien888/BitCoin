import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed
import matplotlib.pyplot as plt
from backtest_wrapper import backtest_wrapper

# --- パラメータ ---
buy_methods = ["mean_above_mean", "median_above_mean"]   # 買い用
sell_methods = ["mean_below_mean", "median_below_mean"]  # 売り用

param_list = [
    (ma, lb, bm, bp, sm, sp, df)
    for ma, lb, bm, bp, sm, sp in product(
        ma_list,           # MA期間
        lookback_list,     # Lookback期間
        buy_methods,       # Buy_MA
        buy_methods,       # Buy_Prev
        sell_methods,      # Sell_MA
        sell_methods       # Sell_Prev
    )
]

# --- 並列バックテスト実行 ---
results = []
with ProcessPoolExecutor() as executor:
    futures = [executor.submit(backtest_wrapper, p) for p in param_list]
    for f in as_completed(futures):
        res = f.result()
        if "profit_percent" in res:  # 念のためキー確認
            results.append(res)

# --- DataFrame化とソート ---
result_df = pd.DataFrame(results)
if not result_df.empty and "profit_percent" in result_df.columns:
    result_df.sort_values("profit_percent", ascending=False, inplace=True)

# --- 上位パラメータ表示 ---
print("\n=== 上位パラメータ ===")
print(result_df.head(10)[["MA","Lookback","Buy_MA","Sell_MA",
                          "profit_percent","max_drawdown",
                          "trade_count","avg_trade_profit"]])

# --- 可視化 ---
plt.figure(figsize=(10,5))
plt.scatter(result_df["MA"], result_df["profit_percent"], label="Profit%")
plt.title("MA期間と利益率の関係")
plt.xlabel("MA Period")
plt.ylabel("Profit %")
plt.grid(True)
plt.legend()
plt.show()
