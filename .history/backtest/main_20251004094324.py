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


def get_thresholds(buy_returns, sell_returns, buy_method, sell_method):
    def parse_method(m):
        if m in ["median", "mean"]:
            return m, m  # base=agg
        if "_above_" in m:
            base, agg = m.split("_above_")
            return base, agg
        raise ValueError("Unknown method: " + str(m))
    
    buy_base, buy_agg = parse_method(buy_method)
    sell_base, sell_agg = parse_method(sell_method)

    buy_thresh = compute_threshold(buy_returns, base=buy_base, direction="below", agg=buy_agg)
    sell_thresh = compute_threshold(sell_returns, base=sell_base, direction="above", agg=sell_agg)
    return buy_thresh, sell_thresh


# --- バックテスト ---
def backtest_single_custom(df, ma_period=20, lookback=14, buy_method="median", sell_method="median", initial_cash=10000):
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
                "Buy_Target": np.nan,
                "Sell_Target": np.nan,
                "Cash": cash,
                "Asset": asset,
                "Portfolio_Value": cash + asset * df["終値"].iloc[i]
            })
            continue

        if i >= lookback:
            buy_returns = df["安値"].iloc[i-lookback+1:i+1].values / df["終値"].iloc[i-lookback:i].values - 1
            sell_returns = df["高値"].iloc[i-lookback+1:i+1].values / df["終値"].iloc[i-lookback:i].values - 1

            buy_thresh, sell_thresh = get_thresholds(buy_returns, sell_returns, buy_method, sell_method)

            target_buy_ma = df["MA"].iloc[i] * (1 + buy_thresh)
            target_buy_now = df["終値"].iloc[i-1] * (1 + buy_thresh)
            target_buy = min(target_buy_ma, target_buy_now)

            target_sell_ma = df["MA"].iloc[i] * (1 + sell_thresh)
            target_sell_now = df["終値"].iloc[i-1] * (1 + sell_thresh)
            target_sell = max(target_sell_ma, target_sell_now)
        else:
            target_buy = df["終値"].iloc[i-1]
            target_sell = df["終値"].iloc[i-1]

        if cash > 0 and df["安値"].iloc[i] <= target_buy:
            asset = cash / target_buy
            cash = 0
        if asset > 0 and df["高値"].iloc[i] >= target_sell:
            cash = asset * target_sell
            asset = 0

        records.append({
            "Date": df.index[i],
            "Close": df["終値"].iloc[i],
            "MA": df["MA"].iloc[i],
            "Buy_Target": target_buy,
            "Sell_Target": target_sell,
            "Cash": cash,
            "Asset": asset,
            "Portfolio_Value": cash + asset * df["終値"].iloc[i]
        })

    final_value = cash + asset * df["終値"].iloc[-1]
    profit_percent = (final_value - initial_cash) / initial_cash * 100
    return pd.DataFrame(records).set_index("Date"), final_value, profit_percent


# --- メイン ---
if __name__ == "__main__":
    symbol = "pepe"  # ← 銘柄名を変更
    file = f"{symbol}.csv"
    df = pd.read_csv(file)
    df["日付け"] = pd.to_datetime(df["日付け"])
    df.set_index("日付け", inplace=True)
        
        # ← ここから検証期間制限を入れる
    use_recent_days = 365*2  # 例：直近1年だけ
    if use_recent_days:
        start_date = datetime.today() - timedelta(days=use_recent_days)
        df = df[df.index >= start_date]

    for col in ["終値", "高値", "安値"]:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors="coerce")

    ma_periods = list(range(10, 31))
    lookbacks = list(range(10, 31))
    methods = ["median","mean","median_above_median","median_above_mean","mean_above_mean","mean_above_median"]

    results = []
    total_runs = len(ma_periods)*len(lookbacks)*len(methods)*len(methods)
    print(f"開始: {total_runs} パターンを検証します")

    for ma, lb, buy_m, sell_m in itertools.product(ma_periods, lookbacks, methods, methods):
        records_df, final_value, profit_percent = backtest_single_custom(df, ma, lb, buy_m, sell_m)
        results.append({
            "MA_Period": ma,
            "Lookback": lb,
            "Buy_Method": buy_m,
            "Sell_Method": sell_m,
            "Final_Value": final_value,
            "Profit_%": profit_percent
        })
        # 個別CSV保存（大量になる場合はコメントアウトしてもOK）
        # records_df.to_csv(f"{symbol}_backtest_{ma}_{lb}_{buy_m}_{sell_m}.csv")

    results_df = pd.DataFrame(results)
    results_df.to_csv(f"{symbol}_backtest_summary.csv", index=False)
    print("検証完了: summary CSV を出力しました")
