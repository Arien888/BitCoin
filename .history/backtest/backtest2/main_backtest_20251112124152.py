import pandas as pd
from itertools import product
from concurrent.futures import ProcessPoolExecutor, as_completed
import matplotlib.pyplot as plt
from backtest_wrapper import backtest_wrapper
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Yu Gothic'  # Windows の場合

if __name__ == "__main__":
    symbol = "btc"
    df = pd.read_csv(f"{symbol}.csv")
    df["日付け"] = pd.to_datetime(df["日付け"])
    df.set_index("日付け", inplace=True)
    for col in ["終値","高値","安値"]:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors="coerce")

    ma_list = range(11, 14)
    lookback_list = range(11, 14)
    buy_methods = ["mean_above_mean", "median_above_mean"]   # 買い用ルール
    sell_methods = ["mean_below_mean", "median_below_mean"]  # 売り用ルール

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


    results = []
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(backtest_wrapper, p) for p in param_list]
        for f in as_completed(futures):
            results.append(f.result())

    result_df = pd.DataFrame(results)
    result_df.sort_values("profit_percent", ascending=False, inplace=True)

    print("\n=== 上位パラメータ ===")
    print(result_df.head(10)[["MA","Lookback","Buy_MA","Sell_MA","profit_percent","max_drawdown","trade_count","avg_trade_profit"]])

    plt.figure(figsize=(10,5))
    plt.scatter(result_df["MA"], result_df["profit_percent"], label="Profit%")
    plt.title("MA期間と利益率の関係")
    plt.xlabel("MA Period")
    plt.ylabel("Profit %")
    plt.grid(True)
    plt.legend()
    plt.show()
