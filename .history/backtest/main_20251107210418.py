import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import itertools

# --- 閾値計算関数 ---
def compute_threshold(values, base="median", direction="above", agg="mean"):
    arr = np.asarray(values)
    if arr.size == 0:
        return 0.0

    ref = np.median(arr) if base == "median" else arr.mean()

    if direction == "above":
        filtered = arr[arr >= ref]
    else:
        filtered = arr[arr <= ref]

    if filtered.size == 0:
        return ref

    return filtered.mean() if agg == "mean" else np.median(filtered)


def get_thresholds(buy_returns, sell_returns, buy_method_ma, buy_method_prev, sell_method_ma, sell_method_prev):
    def parse_method(m):
        if m in ["median", "mean"]:
            return m, m
        if "_above_" in m:
            base, agg = m.split("_above_")
            return base, agg
        raise ValueError("Unknown method: " + str(m))

    # 買い
    buy_base_ma, buy_agg_ma = parse_method(buy_method_ma)
    buy_base_prev, buy_agg_prev = parse_method(buy_method_prev)
    buy_thresh_ma = compute_threshold(buy_returns, base=buy_base_ma, direction="below", agg=buy_agg_ma)
    buy_thresh_prev = compute_threshold(buy_returns, base=buy_base_prev, direction="below", agg=buy_agg_prev)

    # 売り
    sell_base_ma, sell_agg_ma = parse_method(sell_method_ma)
    sell_base_prev, sell_agg_prev = parse_method(sell_method_prev)
    sell_thresh_ma = compute_threshold(sell_returns, base=sell_base_ma, direction="above", agg=sell_agg_ma)
    sell_thresh_prev = compute_threshold(sell_returns, base=sell_base_prev, direction="above", agg=sell_agg_prev)

    return buy_thresh_ma, buy_thresh_prev, sell_thresh_ma, sell_thresh_prev


# --- バックテスト ---
def backtest_single_custom(df, ma_period=20, lookback=14,
                          buy_method_ma="median", buy_method_prev="median",
                          sell_method_ma="median", sell_method_prev="median",
                          initial_cash=10000):

    df = df.copy()
    df["MA"] = df["終値"].rolling(ma_period).mean()
    cash = initial_cash
    asset = 0.0
    records = []

    for i in range(1, len(df)):
        if pd.isna(df["MA"].iloc[i]):
            records.append({
                "Date": df.index[i],
                "Close": df["終値"].iloc[i],
                "MA": df["MA"].iloc[i],
                "Buy_Target_MA": np.nan,
                "Buy_Target_Prev": np.nan,
                "Sell_Target_MA": np.nan,
                "Sell_Target_Prev": np.nan,
                "Cash": cash,
                "Asset": asset,
                "Portfolio_Value": cash + asset * df["終値"].iloc[i]
            })
            continue

        if i >= lookback:
            buy_returns = df["安値"].iloc[i-lookback+1:i+1].values / df["終値"].iloc[i-lookback:i].values - 1
            sell_returns = df["高値"].iloc[i-lookback+1:i+1].values / df["終値"].iloc[i-lookback:i].values - 1

            buy_thresh_ma, buy_thresh_prev, sell_thresh_ma, sell_thresh_prev = get_thresholds(
                buy_returns, sell_returns, buy_method_ma, buy_method_prev, sell_method_ma, sell_method_prev
            )

            target_buy_ma   = df["MA"].iloc[i] * (1 + buy_thresh_ma)
            target_buy_prev = df["終値"].iloc[i-1] * (1 + buy_thresh_prev)
            target_sell_ma   = df["MA"].iloc[i] * (1 + sell_thresh_ma)
            target_sell_prev = df["終値"].iloc[i-1] * (1 + sell_thresh_prev)

        else:
            target_buy_ma = target_buy_prev = df["終値"].iloc[i-1]
            target_sell_ma = target_sell_prev = df["終値"].iloc[i-1]

        # --- 売買判定 ---
        if cash > 0 and df["安値"].iloc[i] <= target_buy_ma:
            asset = cash / target_buy_ma
            cash = 0
        elif cash > 0 and df["安値"].iloc[i] <= target_buy_prev:
            asset = cash / target_buy_prev
            cash = 0

        if asset > 0 and df["高値"].iloc[i] >= target_sell_ma:
            cash = asset * target_sell_ma
            asset = 0
        elif asset > 0 and df["高値"].iloc[i] >= target_sell_prev:
            cash = asset * target_sell_prev
            asset = 0

        # --- 記録 ---
        records.append({
            "Date": df.index[i],
            "Close": df["終値"].iloc[i],
            "MA": df["MA"].iloc[i],
            "Buy_Target_MA": target_buy_ma,
            "Buy_Target_Prev": target_buy_prev,
            "Sell_Target_MA": target_sell_ma,
            "Sell_Target_Prev": target_sell_prev,
            "Cash": cash,
            "Asset": asset,
            "Portfolio_Value": cash + asset * df["終値"].iloc[i]
        })

    final_value = cash + asset * df["終値"].iloc[-1]
    profit_percent = (final_value - initial_cash) / initial_cash * 100
    return pd.DataFrame(records).set_index("Date"), final_value, profit_percent


# --- メイン ---
if __name__ == "__main__":
    symbol = "btc"  # ← 銘柄名
    file = f"{symbol}.csv"
    df = pd.read_csv(file)
    df["日付け"] = pd.to_datetime(df["日付け"])
    df.set_index("日付け", inplace=True)

    for col in ["終値", "高値", "安値"]:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors="coerce")

    # パラメータ設定
    ma_periods = list(range(10, 31))
    lookbacks = list(range(10, 31))
    methods = ["median","mean","median_above_median","median_above_mean","mean_above_mean","mean_above_median"]

    results = []
    total_runs = len(ma_periods)*len(lookbacks)*len(methods)**4
    print(f"開始: {total_runs} パターンを検証します")

    for ma, lb, buy_ma, buy_prev, sell_ma, sell_prev in itertools.product(
        ma_periods, lookbacks, methods, methods, methods, methods
    ):
        records_df, final_value, profit_percent = backtest_single_custom(
            df, ma, lb, buy_ma, buy_prev, sell_ma, sell_prev
        )
        results.append({
            "MA_Period": ma,
            "Lookback": lb,
            "Buy_Method_MA": buy_ma,
            "Buy_Method_Prev": buy_prev,
            "Sell_Method_MA": sell_ma,
            "Sell_Method_Prev": sell_prev,
            "Final_Value": final_value,
            "Profit_%": profit_percent
        })

        # 個別CSVはオプション
        # records_df.to_csv(f"{symbol}_backtest_{ma}_{lb}_{buy_ma}_{buy_prev}_{sell_ma}_{sell_prev}.csv")

    results_df = pd.DataFrame(results)
    results_df.to_csv(f"{symbol}_backtest_summary.csv", index=False)
    print("検証完了: summary CSV を出力しました")
