import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed
import matplotlib.pyplot as plt
from itertools import product
from backtest_wrapper import backtest_wrapper

if __name__ == "__main__":
    symbol = "btc"
    df = pd.read_csv(f"{symbol}.csv")

    df["日付け"] = pd.to_datetime(df["日付け"])
    df.set_index("日付け", inplace=True)

    for col in ["終値", "高値", "安値"]:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors="coerce")

    ma_list = range(7, 9)
    lookback_list = range(12, 14)
    buy_methods = ["median","mean", "mean_below_mean", "median_below_mean"]
    sell_methods = ["median","mean", "mean_below_mean", "median_below_mean"]

    param_list = [
        (ma, lb, bm, bp, sm, sp, df)
        for ma, lb, bm, bp, sm, sp in product(
            ma_list, lookback_list, buy_methods, buy_methods, sell_methods, sell_methods
        )
    ]

    print(f"Total parameter combinations: {len(param_list)}")

    results = []
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(backtest_wrapper, p) for p in param_list]
        for f in as_completed(futures):
            res = f.result()
            if "profit_percent" in res:
                results.append(res)

    result_df = pd.DataFrame(results)
    result_df.sort_values("profit_percent", ascending=False, inplace=True)

    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)

    print("\n=== 上位パラメータ（MA×比率ロジック搭載・逆張り） ===")
    print(result_df.head(10)[[
        "MA", "Lookback", "Buy_MA", "Buy_Prev",
        "Sell_MA", "Sell_Prev",
        "profit_percent", "max_drawdown",
        "trade_count", "avg_trade_profit"
    ]])

    plt.figure(figsize=(10,5))
    plt.scatter(result_df["MA"], result_df["profit_percent"], label="Profit%")
    plt.title("MA期間と利益率の関係（MA比率ロジック搭載）", fontname="MS Gothic")
    plt.xlabel("MA期間", fontname="MS Gothic")
    plt.ylabel("利益率 (%)", fontname="MS Gothic")
    plt.grid(True)
    plt.legend()
    plt.show()
