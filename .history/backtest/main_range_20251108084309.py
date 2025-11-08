import pandas as pd
import numpy as np
from datetime import datetime

# --- 閾値計算 ---
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


# --- バックテスト（ナンピン＋一部売却） ---
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

        # 過去 lookback 期間のリターンで閾値計算
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

        # 過去 range_period 日の高値・安値でポジション調整
        start_idx = max(0, i - range_period + 1)
        recent_high = df["高値"].iloc[start_idx:i+1].max()
        recent_low  = df["安値"].iloc[start_idx:i+1].min()
        recent_range = recent_high - recent_low
        if recent_range == 0:
            range_ratio = 0.5
        else:
            range_ratio = (df["終値"].iloc[i] - recent_low) / recent_range  # 0=安値圏, 1=高値圏

        # --- 買い判定 ---
        buy_fraction = (1 - range_ratio)  # 安値圏ほど多く買う
        buy_price_candidates = [target_buy_ma, target_buy_prev]
        buy_price = min(buy_price_candidates)
        if cash > 0 and df["安値"].iloc[i] <= buy_price:
            buy_amount = cash * buy_fraction
            asset += buy_amount / buy_price
            cash -= buy_amount

        # --- 売り判定 ---
        sell_fraction = range_ratio  # 高値圏ほど多く売る
        sell_price_candidates = [target_sell_ma, target_sell_prev]
        sell_price = max(sell_price_candidates)
        if asset > 0 and df["高値"].iloc[i] >= sell_price:
            sell_amount = asset * sell_fraction
            cash += sell_amount * sell_price
            asset -= sell_amount

    final_value = cash + asset * df["終値"].iloc[-1]
    profit_percent = (final_value - initial_cash) / initial_cash * 100
    return final_value, profit_percent
