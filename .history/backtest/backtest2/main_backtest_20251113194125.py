import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed
import matplotlib.pyplot as plt
from itertools import product
from backtest_wrapper import backtest_wrapper

# ==========================================================
# 分析モード選択："full", "buy_ma", "buy_prev", "sell_ma", "sell_prev"
# ==========================================================
analysis_mode = "full"

if __name__ == "__main__":
    symbol = "btc"
    file_path = f"{symbol}.csv"

    df = pd.read_csv(file_path)
    df["日付け"] = pd.to_datetime(df["日付け"], errors="coerce")
    df.set_index("日付け", inplace=True)

    for col in ["終値", "高値", "安値"]:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors="coerce")

    df.dropna(subset=["終値", "高値", "安値"], inplace=True)

    ma_list = range(12, 13)
    lookback_list = range(8, 9)
    methods = [
        "median",
        "mean",
        "median_above_mean",
        "mean_above_mean",
    ]

    # ==========================================================
    # モード別パラメータ生成
    # ==========================================================
    if analysis_mode == "buy_ma":
        fixed = ("median", "median", "median", "median")
        param_list = [(ma, lb, bm, fixed[1], fixed[2], fixed[3], df)
                      for ma, lb, bm in product(ma_list, lookback_list, methods)]
    elif analysis_mode == "buy_prev":
        fixed = ("median", "median", "median", "median")
        param_list = [(ma, lb, fixed[0], bp, fixed[2], fixed[3], df)
                      for ma, lb, bp in product(ma_list, lookback_list, methods)]
    elif analysis_mode == "sell_ma":
        fixed = ("median", "median", "median", "median")
        param_list = [(ma, lb, fixed[0], fixed[1], sm, fixed[3], df)
                      for ma, lb, sm in product(ma_list, lookback_list, methods)]
    elif analysis_mode == "sell_prev":
        fixed = ("median", "median", "median", "median")
        param_list = [(ma, lb, fixed[0], fixed[1], fixed[2], sp, df)
                      for ma, lb, sp in product(ma_list, lookback_list, methods)]
    else:
        param_list = [(ma, lb, bm, bp, sm, sp, df)
                      for ma, lb, bm, bp, sm, sp in product(
                          ma_list, lookback_list, methods, methods, methods, methods
                      )]

    print(f"Total combinations: {len(param_list)}")

    # ==========================================================
    # 並列実行
    # ==========================================================
    results = []
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(backtest_wrapper, p) for p in param_list]
        for f in as_completed(futures):
            res = f.result()
            if "profit_percent" in res:
                results.append(res)

    result_df = pd.DataFrame(results)
    result_df.sort_values("profit_percent", ascending=False, inplace=True)

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)
    pd.set_option("display.max_colwidth", None)

    print(f"\n=== 上位パラメータ ({analysis_mode}) ===")
    cols = ["MA", "Lookback", "Buy_MA", "Buy_Prev",
            "Sell_MA", "Sell_Prev", "profit_percent",
            "max_drawdown", "trade_count", "avg_trade_profit"]
    print(result_df.head(10)[cols])

    plt.figure(figsize=(10, 5))
    plt.scatter(result_df["MA"], result_df["profit_percent"], label="Profit%")
    plt.title(f"MA期間と利益率 ({analysis_mode})", fontname="MS Gothic")
    plt.xlabel("MA期間", fontname="MS Gothic")
    plt.ylabel("利益率 (%)", fontname="MS Gothic")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
