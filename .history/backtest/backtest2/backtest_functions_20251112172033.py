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

# --- バックテスト（単利運用） ---
def backtest_full_strategy_repeat(df, ma_period, lookback,
                                  buy_method_ma, buy_method_prev, sell_method_ma, sell_method_prev,
                                  initial_cash=10000, trade_risk=10000):
    df = df.copy()
    df["MA"] = df["終値"].rolling(ma_period).mean()
    df = df.dropna(subset=["MA", "終値", "高値", "安値"])

    cash = initial_cash
    total_profit = 0
    trade_count = 0
    trade_profits = []
    history = []

    for i in range(lookback, len(df)):
        buy_returns = df["安値"].iloc[i - lookback:i].pct_change().dropna().values
        sell_returns = df["高値"].iloc[i - lookback:i].pct_change().dropna().values
        buy_thresh_ma, buy_thresh_prev, sell_thresh_ma, sell_thresh_prev = get_thresholds(
            buy_returns, sell_returns, buy_method_ma, buy_method_prev, sell_method_ma, sell_method_prev
        )

        # --- トリガー条件（MA基準） ---
        ma_val = df["MA"].iloc[i]
        prev_close = df["終値"].iloc[i - 1]
        cur_low = df["安値"].iloc[i]
        cur_high = df["高値"].iloc[i]

        buy_trigger = prev_close <= ma_val * (1 - abs(buy_thresh_ma))
        sell_trigger = prev_close >= ma_val * (1 + abs(sell_thresh_ma))

        # --- 買いトリガー成立時 ---
        if buy_trigger:
            buy_price = prev_close * (1 - abs(buy_thresh_prev))
            if cur_low <= buy_price:
                sell_target = prev_close * (1 + abs(sell_thresh_prev))
                if cur_high >= sell_target:
                    profit = trade_risk * ((sell_target - buy_price) / buy_price)
                    total_profit += profit
                    trade_profits.append((sell_target - buy_price) / buy_price * 100)
                    trade_count += 1

        # --- 売りトリガー成立時 ---
        elif sell_trigger:
            sell_price = prev_close * (1 + abs(sell_thresh_prev))
            if cur_high >= sell_price:
                buy_back = prev_close * (1 - abs(buy_thresh_prev))
                if cur_low <= buy_back:
                    profit = trade_risk * ((sell_price - buy_back) / sell_price) * -1
                    total_profit += profit
                    trade_profits.append((buy_back - sell_price) / sell_price * 100)
                    trade_count += 1

        history.append(initial_cash + total_profit)

    total_values = np.array(history)
    cum_max = np.maximum.accumulate(total_values)
    drawdown = (cum_max - total_values) / cum_max
    max_drawdown = drawdown.max() if len(drawdown) > 0 else 0

    profit_percent = (total_profit / initial_cash) * 100
    avg_trade_profit = np.mean(trade_profits) if trade_profits else 0

    return {
        "final_value": initial_cash + total_profit,
        "profit_percent": profit_percent,
        "max_drawdown": max_drawdown * 100,
        "trade_count": trade_count,
        "avg_trade_profit": avg_trade_profit
    }
