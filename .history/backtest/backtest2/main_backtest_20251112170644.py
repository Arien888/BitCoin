import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed
import matplotlib.pyplot as plt
from itertools import product
from backtest_wrapper import backtest_wrapper

# ==========================================================
# 逆張り型バックテスト・メインスクリプト
# ==========================================================
if __name__ == "__main__":
    # --- 対象銘柄 ---
    symbol = "btc"
    file_path = f"{symbol}.csv"

    # --- CSV読み込み ---
    print(f"Loading data from {file_path} ...")
    df = pd.read_csv(file_path)

    # --- 日付をDatetimeに変換してインデックスに設定 ---
    df["日付け"] = pd.to_datetime(df["日付け"], errors="coerce")
    df.set_index("日付け", inplace=True)

    # --- 数値列をfloat型に変換（カンマ除去） ---
    numeric_cols = ["終値", "高値", "安値"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors="coerce")

    # --- 欠損値除去 ---
    df.dropna(subset=numeric_cols, inplace=True)

    # ==========================================================
    # パラメータ設定
    # ==========================================================
    ma_list = range(8, 12)        # MA期間
    lookback_list = range(8, 12)  # 閾値計算期間
    buy_methods = ["median", "mean", "median_above_mean"]
    sell_methods = ["median", "mean", "median_below_mean"]

    # --- すべての組み合わせを生成 ---
    param_list = [
        (ma, lb, bm, bp, sm, sp, df)
        for ma, lb, bm, bp, sm, sp in product(
            ma_list,        # MA期間
            lookback_list,  # Lookback期間
            buy_methods,    # Buy_MA
            buy_methods,    # Buy_Prev
            sell_methods,   # Sell_MA
            sell_methods    # Sell_Prev
        )
    ]

    print(f"Total parameter combinations: {len(param_list)}")

    # ==========================================================
    # 並列バックテスト実行
    # ==========================================================
    results = []
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(backtest_wrapper, p) for p in param_list]

        for i, f in enumerate(as_completed(futures), 1):
            try:
                res = f.result()
                if isinstance(res, dict) and "profit_percent" in res:
                    results.append(res)
            except Exception as e:
                print(f"[Error] #{i}: {e}")

    # ==========================================================
    # 結果整理
    # ==========================================================
    if not results:
        print("No valid results.")
        exit()

    result_df = pd.DataFrame(results)

    # --- 利益率でソート ---
    result_df.sort_values("profit_percent", ascending=False, inplace=True)

    # --- 表示設定（省略されないように）---
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)

    # ==========================================================
    # 上位10パラメータ表示
    # ==========================================================
    print("\n=== 上位パラメータ（逆張り） ===")
    show_cols = [
        "MA", "Lookback", "Buy_MA", "Buy_Prev",
        "Sell_MA", "Sell_Prev",
        "profit_percent", "max_drawdown",
        "trade_count", "avg_trade_profit"
    ]
    print(result_df.head(10)[show_cols])

    # ==========================================================
    # 可視化
    # ==========================================================
    plt.figure(figsize=(10, 5))
    plt.scatter(result_df["MA"], result_df["profit_percent"], label="Profit%")
    plt.title("MA期間と利益率の関係（逆張り）", fontname="MS Gothic")
    plt.xlabel("MA期間", fontname="MS Gothic")
    plt.ylabel("利益率 (%)", fontname="MS Gothic")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
