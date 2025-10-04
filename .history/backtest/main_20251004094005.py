import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import itertools

# --- 単一バックテスト ---
def backtest_single_custom(df, ma_period=20, lookback=14, buy_method="median", sell_method="median", initial_cash=10000):
    """
    buy_method / sell_method: "median", "mean", "above_median_median", "above_median_mean", 
                              "above_mean_mean", "above_mean_median"
    """
    df = df.copy()
    df["MA"] = df["終値"].rolling(ma_period).mean()
    cash = initial_cash
    btc = 0
    records = []

    for i in range(1, len(df)):
        if i >= lookback:
            # 過去リターン
            buy_returns = df["安値"].iloc[i-lookback+1:i+1].values / df["終値"].iloc[i-lookback:i].values - 1
            sell_returns = df["高値"].iloc[i-lookback+1:i+1].values / df["終値"].iloc[i-lookback:i].values - 1

            # --- buy閾値 ---
            if buy_method == "mean":
                buy_thresh = buy_returns.mean()
            elif buy_method == "median":
                buy_thresh = np.median(buy_returns)
            elif buy_method == "above_median_median":
                buy_thresh = buy_returns[buy_returns <= np.median(buy_returns)].mean()
            elif buy_method == "above_median_mean":
                buy_thresh = buy_returns[buy_returns <= np.median(buy_returns)].mean()
            elif buy_method == "above_mean_mean":
                buy_thresh = buy_returns[buy_returns <= buy_returns.mean()].mean()
            elif buy_method == "above_mean_median":
                buy_thresh = np.median(buy_returns[buy_returns <= buy_returns.mean()])
            else:
                raise ValueError("invalid buy_method")

            # --- sell閾値 ---
            if sell_method == "mean":
                sell_thresh = sell_returns.mean()
            elif sell_method == "median":
                sell_thresh = np.median(sell_returns)
            elif sell_method == "above_median_median":
                sell_thresh = np.median(sell_returns[sell_returns >= np.median(sell_returns)])
            elif sell_method == "above_median_mean":
                sell_thresh = sell_returns[sell_returns >= np.median(sell_returns)].mean()
            elif sell_method == "above_mean_mean":
                sell_thresh = sell_returns[sell_returns >= sell_returns.mean()].mean()
            elif sell_method == "above_mean_median":
                sell_thresh = np.median(sell_returns[sell_returns >= sell_returns.mean()])
            else:
                raise ValueError("invalid sell_method")

            # --- 指値 ---
            target_buy_ma = df["MA"].iloc[i] * (1 + buy_thresh)
            target_buy_now = df["終値"].iloc[i-1] * (1 + buy_thresh)
            target_buy = min(target_buy_ma, target_buy_now)

            target_sell_ma = df["MA"].iloc[i] * (1 + sell_thresh)
            target_sell_now = df["終値"].iloc[i-1] * (1 + sell_thresh)
            target_sell = max(target_sell_ma, target_sell_now)

        else:
            target_buy = df["終値"].iloc[i-1]
            target_sell = df["終値"].iloc[i-1]

        # --- 売買 ---
        if cash > 0 and df["安値"].iloc[i] <= target_buy:
            btc = cash / target_buy
            cash = 0
        if btc > 0 and df["高値"].iloc[i] >= target_sell:
            cash = btc * target_sell
            btc = 0

        # --- 記録 ---
        records.append({
            "Date": df.index[i],
            "Close": df["終値"].iloc[i],
            "MA": df["MA"].iloc[i],
            "Buy_Target": target_buy,
            "Sell_Target": target_sell,
            "Cash": cash,
            "BTC": btc,
            "Portfolio_Value": cash + btc * df["終値"].iloc[i]
        })

    final_value = cash + btc * df["終値"].iloc[-1]
    profit_percent = (final_value - initial_cash) / initial_cash * 100
    return pd.DataFrame(records).set_index("Date"), final_value, profit_percent
