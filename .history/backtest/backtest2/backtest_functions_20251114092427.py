import numpy as np
import pandas as pd

# ==========================================================
# helper: second-level statistics
# ==========================================================
def second_level_stat(arr, base_stat="median", mode="below"):
    """
    arr: numpy array
    base_stat: "median" / "mean"
    mode:
        below → arr <= 基準値
        above → arr >= 基準値
    """
    if arr.size == 0:
        return 0.01

    base = np.median(arr) if base_stat == "median" else np.mean(arr)

    if mode == "below":
        sub = arr[arr <= base]
    else:
        sub = arr[arr >= base]

    if sub.size == 0:
        return base

    return np.median(sub)


# ==========================================================
# 閾値計算（あなた仕様）
# ==========================================================
def compute_threshold(values, method, side):
    """
    values: 過去n日間のリターン
    method:
        mean
        median
        median_in_mean
        median_in_median
        mean_in_mean
    side:
        "buy"  → LOW returns を分析（逆張り → below 方向）
        "sell" → HIGH returns を分析（逆張り → above 方向）
    """

    arr = np.asarray(values)
    if arr.size == 0:
        return 0.01

    # --- 基本統計量 ---
    med = np.median(arr)
    avg = np.mean(arr)

    # --- 方向（重要）---
    # 買い：基準値以下
    # 売り：基準値以上
    dir_map = {
        "buy": "below",
        "sell": "above"
    }
    mode = dir_map[side]

    # -----------------------------
    # メソッド別の内部ロジック
    # -----------------------------
    if method == "mean":
        return max(abs(avg), 0.005)

    elif method == "median":
        return max(abs(med), 0.005)

    elif method == "median_in_mean":
        # 平均 → その方向の subset → その中央値
        base = avg
        sub = arr[arr <= base] if mode == "below" else arr[arr >= base]
        if sub.size == 0:
            return abs(base)
        return max(abs(np.median(sub)), 0.005)

    elif method == "median_in_median":
        # 中央値 → その方向の subset → その中央値
        base = med
        sub = arr[arr <= base] if mode == "below" else arr[arr >= base]
        if sub.size == 0:
            return abs(base)
        return max(abs(np.median(sub)), 0.005)

    elif method == "mean_in_mean":
        # 平均 → その方向の subset → その平均
        base = avg
        sub = arr[arr <= base] if mode == "below" else arr[arr >= base]
        if sub.size == 0:
            return abs(base)
        return max(abs(np.mean(sub)), 0.005)

    else:
        raise ValueError(f"Unknown threshold method: {method}")


# ==========================================================
# 閾値セット取得
# ==========================================================
def get_thresholds(buy_returns, sell_returns,
                   buy_method_ma, buy_method_prev,
                   sell_method_ma, sell_method_prev):

    # それぞれ別々の returns（買いはLOW, 売りはHIGH）
    buy_thresh_ma   = compute_threshold(buy_returns, buy_method_ma,   side="buy")
    buy_thresh_prev = compute_threshold(buy_returns, buy_method_prev, side="buy")
    sell_thresh_ma  = compute_threshold(sell_returns, sell_method_ma, side="sell")
    sell_thresh_prev= compute_threshold(sell_returns, sell_method_prev,side="sell")

    return buy_thresh_ma, buy_thresh_prev, sell_thresh_ma, sell_thresh_prev


# ==========================================================
# 逆張りロジック（指値到達のみ約定）
# ==========================================================
def backtest_full_strategy_repeat(df, ma_period, lookback,
                                  buy_method_ma, buy_method_prev,
                                  sell_method_ma, sell_method_prev,
                                  initial_cash=100000, leverage=1.0):

    df = df.copy()
    df["MA"] = df["終値"].rolling(ma_period).mean()
    df = df.dropna(subset=["MA", "終値", "高値", "安値"])

    amount = initial_cash * leverage
    balance = initial_cash
    trade_count = 0
    trade_profits = []
    history = []

    for i in range(lookback, len(df)):

        # 過去リターン（BUY→安値, SELL→高値）
        buy_ret = df["安値"].iloc[i - lookback:i].pct_change().dropna().values
        sell_ret = df["高値"].iloc[i - lookback:i].pct_change().dropna().values

        buy_th_ma, buy_th_prev, sell_th_ma, sell_th_prev = get_thresholds(
            buy_ret, sell_ret,
            buy_method_ma, buy_method_prev,
            sell_method_ma, sell_method_prev
        )

        ma_val = df["MA"].iloc[i]
        prev_close = df["終値"].iloc[i - 1]
        cur_low = df["安値"].iloc[i]
        cur_high = df["高値"].iloc[i]

        # =====================
        # 買い判定
        # =====================
        buy_trigger = prev_close <= ma_val * (1 - buy_th_ma)

        if buy_trigger:
            buy_price = prev_close * (1 - buy_th_prev)
            sell_target = prev_close * (1 + sell_th_prev)

            if cur_low <= buy_price and cur_high >= sell_target:
                profit_pct = (sell_target - buy_price) / buy_price
                profit = amount * profit_pct
                balance += profit
                trade_profits.append(profit_pct * 100)
                trade_count += 1

        # =====================
        # 売り判定
        # =====================
        sell_trigger = prev_close >= ma_val * (1 + sell_th_ma)

        if sell_trigger:
            sell_price = prev_close * (1 + sell_th_prev)
            buy_target = prev_close * (1 - buy_th_prev)

            if cur_high >= sell_price and cur_low <= buy_target:
                profit_pct = (sell_price - buy_target) / sell_price
                profit = amount * profit_pct
                balance += profit
                trade_profits.append(profit_pct * 100)
                trade_count += 1

        history.append(balance)

    # Drawdown
    hist_arr = np.array(history)
    cummax = np.maximum.accumulate(hist_arr)
    dd = (cummax - hist_arr) / cummax
    max_dd = dd.max() * 100 if len(dd) else 0

    final_profit_pct = (balance - initial_cash) / initial_cash * 100
    avg_profit = np.mean(trade_profits) if trade_profits else 0

    return {
        "MA": ma_period,
        "Lookback": lookback,
        "Buy_MA": buy_method_ma,
        "Buy_Prev": buy_method_prev,
        "Sell_MA": sell_method_ma,
        "Sell_Prev": sell_method_prev,
        "profit_percent": final_profit_pct,
        "max_drawdown": max_dd,
        "trade_count": trade_count,
        "avg_trade_profit": avg_profit
    }
