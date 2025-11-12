import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed
import matplotlib.pyplot as plt
from backtest_wrapper import backtest_wrapper
from itertools import product   # これを追加

# --- パラメータ ---
buy_methods = ["mean_above_mean", "median_above_mean"]   # 買い用
sell_methods = ["mean_below_mean", "median_below_mean"]  # 売り用

# --- MA期間とLookback期間のリスト ---
ma_list = range(11, 13)       # 例: 11～12まで
lookback_list = range(11, 13) # 例: 11～12まで

# --- CSV読み込み ---
symbol = "btc"  # 対象の銘柄名
df = pd.read_csv(f"{symbol}.csv")

# --- 日付をDatetimeに変換してインデックスに設定 ---
df["日付け"] = pd.to_datetime(df["日付け"])
df.set_index("日付け", inplace=True)

# --- 数値列をfloat型に変換（カンマ除去） ---
for col in ["終値", "高値", "安値"]:
    df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors="coerce")


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
