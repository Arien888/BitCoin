import numpy as np
import pandas as pd

# ==========================================================
# 閾値計算
# ==========================================================
def compute_threshold(values, base="median", direction="above", agg="mean"):
    arr = np.asarray(values)
    if arr.size == 0:
        return 0.01
    ref = np.median(arr) if base == "median" else (np.max(arr) if base == "max" else arr.mean())
    filtered = arr[arr >= ref] if direction == "above" else arr[arr <= ref]
    if filtered.size == 0:
        return max(abs(ref), 0.005)
    val = filtered.mean() if agg == "mean" else np.median(filtered)
    return max(abs(val), 0.005)

# ==========================================================
# メソッド解析
# ==========================================================
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
        raise ValueError(f"Unknown method: {m}")

# ==========================================================
# 閾値取得
# ==========================================================
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

# ==========================================================
# 単利運用・逆張りバックテスト
# ==========================================================
def backtest_full_strategy_repeat(df, ma_period, lookback,
                                  buy_method_ma, buy_method_prev, sell_method_ma, sell_method_prev,
                                  initial_cash=100000, trade_amount=10000):

    df = df.copy()
    df["MA"] = df["終値"].rolling(ma_period).mean()
    df = df.dropna(subset=["MA", "終値", "高値", "安値"])

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

        ma_val = df["MA"].iloc[i]
        prev_close = df["終値"].iloc[i - 1]
        cur_low = df["安値"].iloc[i]
        cur_high = df["高値"].iloc[i]

        # 逆張り条件
        buy_trigger = prev_close <= ma_val * (1 - abs(buy_thresh_ma))
        sell_trigger = prev_close >= ma_val * (1 + abs(sell_thresh_ma))

        # --- 買いトリガー ---
        if buy_trigger:
            buy_price = prev_close * (1 - abs(buy_thresh_prev))
            sell_target = prev_close * (1 + abs(sell_thresh_prev))

            if cur_low <= buy_price:
                if cur_high >= sell_target:
                    profit_pct = (sell_target - buy_price) / buy_price * 100
                else:
                    next_close = df["終値"].iloc[i] if i + 1 < len(df) else prev_close
                    profit_pct = (next_close - buy_price) / buy_price * 100

                total_profit += trade_amount * (profit_pct / 100)
                trade_profits.append(profit_pct)
                trade_count += 1

        # --- 売りトリガー ---
        elif sell_trigger:
            sell_price = prev_close * (1 + abs(sell_thresh_prev))
            buy_back = prev_close * (1 - abs(buy_thresh_prev))

            if cur_high >= sell_price:
                if cur_low <= buy_back:
                    profit_pct = (sell_price - buy_back) / sell_price * -100
                else:
                    next_close = df["終値"].iloc[i] if i + 1 < len(df) else prev_close
                    profit_pct = (sell_price - next_close) / sell_price * -100

                total_profit += trade_amount * (profit_pct / 100)
                trade_profits.append(profit_pct)
                trade_count += 1

        history.append(initial_cash + total_profit)

    total_values = np.array(history)
    if len(total_values) == 0:
        return {"final_value": initial_cash, "profit_percent": 0, "max_drawdown": 0, "trade_count": 0, "avg_trade_profit": 0}

    cum_max = np.maximum.accumulate(total_values)
    drawdown = (cum_max - total_values) / cum_max
    max_drawdown = drawdown.max() if len(drawdown) > 0 else 0

    profit_percent = (total_profit / initial_cash) * 100
    avg_trade_profit = np.mean(trade_profits) if trade_profits else 0

    print(f"[DEBUG] MA={ma_period}, LB={lookback}, Trades={trade_count}, Profit={profit_percent:.2f}%")

    return {
        "final_value": initial_cash + total_profit,
        "profit_percent": profit_percent,
        "max_drawdown": max_drawdown * 100,
        "trade_count": trade_count,
        "avg_trade_profit": avg_trade_profit
    }
