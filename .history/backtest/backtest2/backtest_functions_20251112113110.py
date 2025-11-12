# backtest_functions.py
import numpy as np
import pandas as pd

# --- 閾値計算 ---
def compute_threshold(values, base="median", direction="above", agg="mean"):
    arr = np.asarray(values)
    if arr.size == 0:
        return 0.0
    ref = np.median(arr) if base == "median" else (np.max(arr) if base == "max" else arr.mean())
    filtered = arr[arr >= ref] if direction == "above" else arr[arr <= ref]
    if filtered.size == 0:
        return ref
    return filtered.mean() if agg == "mean" else np.median(filtered)

# --- メソッド解析 ---
def parse_method(m):
    if "_above_" in m:
        base, agg = m.split("_above_")
        return base, "above", agg
    elif "_below_" in m:
        base, agg = m.split("_below_")
        return base, "below", agg
    elif m in ["mean", "median", "max"]:
        return m, "above", m
    else:
        raise ValueError("Unknown method: " + str(m))

# --- 閾値取得 ---
def get_thresholds(buy_returns, sell_returns, buy_method_ma, buy_method_prev, sell_method_ma, sell_method_prev):
    buy_base_ma, buy_dir_ma, buy_agg_ma = parse_method(buy_method_ma)
    buy_base_prev, buy_dir_prev, buy_agg_prev = parse_method(buy_method_prev)
    sell_base_ma, sell_dir_ma, sell_agg_ma = parse_method(sell_method_ma)
    sell_base_prev, sell_dir_prev, sell_agg_prev = parse_method(sell_method_prev)

    return (
        compute_threshold(buy_returns, buy_base_ma, buy_dir_ma, buy_agg_ma),
        compute_threshold(buy_returns, buy_base_prev, buy_dir_prev, buy_agg_prev),
        compute_threshold(sell_returns, sell_base_ma, sell_dir_ma, sell_agg_ma),
        compute_threshold(sell_returns, sell_base_prev, sell_dir_prev, sell_agg_prev)
    )

# --- バックテスト ---
def backtest_full_strategy_repeat(df, ma_period, lookback,
                                  buy_method_ma, buy_method_prev, sell_method_ma, sell_method_prev,
                                  initial_cash=10000):
    df = df.copy()
    df["MA"] = df["終値"].rolling(ma_period).mean()
    df = df.dropna(subset=["MA", "終値", "高値", "安値"])
    
    cash, asset = initial_cash, 0
    history, trades = [], []
    position, entry_price = 0, 0

    for i in range(lookback, len(df)):
        buy_returns = df["安値"].iloc[i-lookback:i].pct_change().dropna().values
        sell_returns = df["高値"].iloc[i-lookback:i].pct_change().dropna().values
        buy_thresh_ma, buy_thresh_prev, sell_thresh_ma, sell_thresh_prev = get_thresholds(
            buy_returns, sell_returns, buy_method_ma, buy_method_prev, sell_method_ma, sell_method_prev
        )

        target_buy_price = min(df["MA"].iloc[i]*(1-abs(buy_thresh_ma)),
                               df["終値"].iloc[i-1]*(1-abs(buy_thresh_prev)))
        target_sell_price = max(df["MA"].iloc[i]*(1+abs(sell_thresh_ma)),
                                df["終値"].iloc[i-1]*(1+abs(sell_thresh_prev)))

        # 買い
        if df["安値"].iloc[i] <= target_buy_price and cash > 0:
            asset += cash / df["安値"].iloc[i]
            trades.append({'type':'buy','price':df["安値"].iloc[i]})
            entry_price = df["安値"].iloc[i]
            cash = 0
            position = asset

        # 売り
        if df["高値"].iloc[i] >= target_sell_price and asset > 0:
            cash += asset * df["高値"].iloc[i]
            trades.append({'type':'sell','price':df["高値"].iloc[i],
                           'profit_pct':(df["高値"].iloc[i]-entry_price)/entry_price*100})
            asset, position, entry_price = 0, 0, 0

        history.append(cash + asset * df["終値"].iloc[i])

    total_values = np.array(history)
    cum_max = np.maximum.accumulate(total_values)
    drawdown = (cum_max - total_values) / cum_max
    max_drawdown = drawdown.max() if len(drawdown) > 0 else 0
    final_value = cash + asset * df["終値"].iloc[-1]
    profit_percent = (final_value - initial_cash) / initial_cash * 100
    trade_profits = [t['profit_pct'] for t in trades if 'profit_pct' in t]
    avg_trade_profit = np.mean(trade_profits) if trade_profits else 0

    return {
        "final_value": final_value,
        "profit_percent": profit_percent,
        "max_drawdown": max_drawdown*100,
        "trade_count": len(trade_profits),
        "avg_trade_profit": avg_trade_profit
    }
