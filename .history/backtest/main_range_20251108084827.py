import pandas as pd
import numpy as np

# ----------------------------
# 閾値計算関数
# ----------------------------
def compute_threshold(values, base="median", direction="above", agg="mean"):
    arr = np.asarray(values)
    if arr.size == 0:
        return 0.0
    if base == "max":
        return np.max(arr)
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
        if m in ["median", "mean", "max"]:
            return m, m
        if "_above_" in m:
            base, agg = m.split("_above_")
            return base, agg
        raise ValueError("Unknown method: " + str(m))

    buy_base_ma, buy_agg_ma = parse_method(buy_method_ma)
    buy_base_prev, buy_agg_prev = parse_method(buy_method_prev)
    sell_base_ma, sell_agg_ma = parse_method(sell_method_ma)
    sell_base_prev, sell_agg_prev = parse_method(sell_method_prev)

    if buy_base_ma == "max":
        buy_thresh_ma = np.max(buy_returns)
    else:
        buy_thresh_ma = compute_threshold(buy_returns, base=buy_base_ma, direction="below", agg=buy_agg_ma)

    if sell_base_ma == "max":
        sell_thresh_ma = np.max(sell_returns)
    else:
        sell_thresh_ma = compute_threshold(sell_returns, base=sell_base_ma, direction="above", agg=sell_agg_ma)

    buy_thresh_prev = compute_threshold(buy_returns, base=buy_base_prev, direction="below", agg=buy_agg_prev)
    sell_thresh_prev = compute_threshold(sell_returns, base=sell_base_prev, direction="above", agg=sell_agg_prev)

    return buy_thresh_ma, buy_thresh_prev, sell_thresh_ma, sell_thresh_prev

# ----------------------------
# ナンピン＋一部売却バックテスト
# ----------------------------
def backtest_custom_nampin(df, ma_period, lookback,
                           buy_method_ma, buy_method_prev, sell_method_ma, sell_method_prev,
                           initial_cash=10000, range_period=30):
    df = df.copy()
    df["MA"] = df["終値"].rolling(ma_period).mean()
    cash = initial_cash
    asset = 0.0

    for i in range(1, len(df)):
        if pd.isna(df["MA"].iloc[i]):
            continue

        # --- 過去 lookback 日でのリターン計算 ---
        if i >= lookback:
            buy_returns = df["安値"].iloc[i-lookback+1:i+1].values / df["終値"].iloc[i-lookback:i].values - 1
            sell_returns = df["高値"].iloc[i-lookback+1:i+1].values / df["終値"].iloc[i-lookback:i].values - 1
            buy_thresh_ma, buy_thresh_prev, sell_thresh_ma, sell_thresh_prev = get_thresholds(
                buy_returns, sell_returns, buy_method_ma, buy_method_prev, sell_method_ma, sell_method_prev
            )
            target_buy_ma   = df["MA"].iloc[i] * (1 + buy_thresh_ma)
            target_buy_prev = df["終値"].iloc[i-1] * (1 + buy_thresh_prev)
            target_sell_ma  = df["MA"].iloc[i] * (1 + sell_thresh_ma)
            target_sell_prev = df["終値"].iloc[i-1] * (1 + sell_thresh_prev)
        else:
            target_buy_ma = target_buy_prev = df["終値"].iloc[i-1]
            target_sell_ma = target_sell_prev = df["終値"].iloc[i-1]

        # --- 過去 range_period 日の高値・安値レンジに応じて売買量調整 ---
        if i >= range_period:
            recent_high = df["高値"].iloc[i-range_period+1:i+1].max()
            recent_low  = df["安値"].iloc[i-range_period+1:i+1].min()
            range_mid = (recent_high + recent_low) / 2

            # 高値圏なら売却量を増やす、安値圏なら購入量を増やす
            if df["終値"].iloc[i] > range_mid:
                sell_ratio = 1.0  # 全部売る
                buy_ratio = 0.5   # 少なめ購入
            else:
                sell_ratio = 0.5  # 半分売却
                buy_ratio = 1.0   # フル購入
        else:
            sell_ratio = buy_ratio = 1.0

        # --- 買い処理（ナンピン） ---
        if df["安値"].iloc[i] <= target_buy_ma and cash > 0:
            purchase = cash * buy_ratio
            asset += purchase / target_buy_ma
            cash -= purchase
        elif df["安値"].iloc[i] <= target_buy_prev and cash > 0:
            purchase = cash * buy_ratio
            asset += purchase / target_buy_prev
            cash -= purchase

        # --- 売り処理（一部売却含む） ---
        if df["高値"].iloc[i] >= target_sell_ma and asset > 0:
            sell_amount = asset * sell_ratio
            cash += sell_amount * target_sell_ma
            asset -= sell_amount
        elif df["高値"].iloc[i] >= target_sell_prev and asset > 0:
            sell_amount = asset * sell_ratio
            cash += sell_amount * target_sell_prev
            asset -= sell_amount

    final_value = cash + asset * df["終値"].iloc[-1]
    profit_percent = (final_value - initial_cash) / initial_cash * 100
    return final_value, profit_percent

# ----------------------------
# メイン処理
# ----------------------------
if __name__ == "__main__":
    symbol = "btc"
    df = pd.read_csv(f"{symbol}.csv")
    df["日付け"] = pd.to_datetime(df["日付け"])
    df.set_index("日付け", inplace=True)
    for col in ["終値", "高値", "安値"]:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors="coerce")

    # 固定パラメータ
    MA_Period = 11
    Lookback = 13
    Buy_Method_MA = "mean_above_mean"
    Buy_Method_Prev = "median"
    Sell_Method_MA = "median"
    Sell_Method_Prev = "median"

    final_value, profit_percent = backtest_custom_nampin(
        df,
        MA_Period,
        Lookback,
        Buy_Method_MA,
        Buy_Method_Prev,
        Sell_Method_MA,
        Sell_Method_Prev,
        initial_cash=10000,
        range_period=30
    )

    print(f"最終資産: {final_value:.2f}円, 利益率: {profit_percent:.2f}%")
