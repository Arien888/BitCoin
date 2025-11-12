import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed
from itertools import product
import matplotlib.pyplot as plt

from backtest_wrapper import backtest_wrapper

if __name__ == "__main__":  # ★ Windows 並列実行に必須

    # ==============================
    # 1) データ読み込み
    # ==============================
    symbol = "btc"
    file_path = f"{symbol}.csv"
    print(f"[INFO] Loading: {file_path}")
    df = pd.read_csv(file_path)

    # 必須列: 日付け, 終値, 高値, 安値（文字→数値へ）
    df["日付け"] = pd.to_datetime(df["日付け"], errors="coerce")
    df.set_index("日付け", inplace=True)
    for col in ["終値", "高値", "安値"]:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors="coerce")
    df.dropna(subset=["終値", "高値", "安値"], inplace=True)

    # ==============================
    # 2) パラメータ
    # ==============================
    ma_list = range(7, 9)          # 例: 7〜8
    lookback_list = range(12, 14)  # 例: 12〜13

    # メソッドは代表的なものを列挙（必要に応じて増減OK）
    methods = [
        "median",
        "mean",
        "median_above_mean",
        "median_below_mean",
        "mean_above_mean",
        "mean_below_mean",
    ]

    buy_methods = methods
    sell_methods = methods

    # 戦略モード: "simple"（全売買）と "range"（レンジ調整）を比較
    modes = ["simple", "range"]

    # ==============================
    # 3) パラメータ全組み合わせ
    # ==============================
    param_list = [
        (ma, lb, bm, bp, sm, sp, df, mode)
        for ma, lb, bm, bp, sm, sp, mode in product(
            ma_list,
            lookback_list,
            buy_methods,   # Buy_MA
            buy_methods,   # Buy_Prev
            sell_methods,  # Sell_MA
            sell_methods,  # Sell_Prev
            modes
        )
    ]
    print(f"[INFO] Total combinations: {len(param_list)}")

    # ==============================
    # 4) 並列実行
    # ==============================
    results = []
    with ProcessPoolExecutor() as ex:
        futures = [ex.submit(backtest_wrapper, p) for p in param_list]
        for f in as_completed(futures):
            try:
                res = f.result()
                if isinstance(res, dict) and "profit_percent" in res:
                    results.append(res)
            except Exception as e:
                print(f"[ERROR] {e}")

    if not results:
        print("[WARN] No results.")
        raise SystemExit

    # ==============================
    # 5) 集計と表示
    # ==============================
    result_df = pd.DataFrame(results)
    result_df.sort_values(["Mode", "profit_percent"], ascending=[True, False], inplace=True)

    # 表示省略を防ぐ
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)
    pd.set_option("display.max_colwidth", None)

    print("\n=== 上位パラメータ（Mode別） ===")
    cols = [
        "Mode", "MA", "Lookback",
        "Buy_MA", "Buy_Prev", "Sell_MA", "Sell_Prev",
        "profit_percent", "max_drawdown", "trade_count", "avg_trade_profit"
    ]
    # 各モード上位5件
    for mode in modes:
        sub = result_df[result_df["Mode"] == mode].head(5)
        print(f"\n[Mode: {mode}]")
        print(sub[cols])

    # ==============================
    # 6) 可視化（参考）
    # ==============================
    try:
        plt.figure(figsize=(10, 5))
        for mode in modes:
            sub = result_df[result_df["Mode"] == mode]
            plt.scatter(sub["MA"], sub["profit_percent"], label=f"{mode}")
        plt.title("MA期間と利益率（Mode比較）")
        plt.xlabel("MA")
        plt.ylabel("Profit %")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"[PLOT WARN] {e}")
