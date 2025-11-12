import numpy as np
import pandas as pd

# ==========================================================
# 閾値計算（データの変動幅から基準乖離率を算出）
# ==========================================================
def compute_threshold(values, base="median", direction="above", agg="mean"):
    arr = np.asarray(values)
    if arr.size == 0:
        return 0.01  # データ不足時のデフォルト乖離率（1%）
    
    # --- 基準値を計算 ---
    ref = np.median(arr) if base == "median" else (np.max(arr) if base == "max" else arr.mean())
    filtered = arr[arr >= ref] if direction == "above" else arr[arr <= ref]
    if filtered.size == 0:
        return abs(ref)
    
    val = filtered.mean() if agg == "mean" else np.median(filtered)
    return max(abs(val), 0.005)  # 最小乖離率0.5%を保証


# ==========================================================
# メソッド解析（例："mean_above_mean" → base=mean, direction=above, agg=mean）
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
# 閾値セット取得（買い・売り用のMA閾値と指値閾値をまとめて返す）
# ==========================================================
def get_thresholds(buy_returns, sell_returns, buy_method_ma, buy_method_prev, sell_method_ma, sell_method_prev):
    buy_base_ma, buy_dir_ma, buy_agg_ma = parse_method(buy_method_ma)
    buy_base_prev, buy_dir_prev, buy_agg_prev = parse_method(buy_method_prev)
    sell_base_ma, sell_dir_ma, sell_agg_ma = parse_method(sell_method_ma)
    sell_base_prev, sell_dir_prev, sell_agg_prev = parse_method(sell_method_prev)

    return (
        compute_threshold(buy_returns, buy_base_ma, buy_dir_ma, buy_agg_ma),   # buy_thresh_ma（買いトリガー閾値）
        compute_threshold(buy_returns, buy_base_prev, buy_dir_prev, buy_agg_prev),  # buy_thresh_prev（買い指値乖離率）
        compute_threshold(sell_returns, sell_base_ma, sell_dir_ma, sell_agg_ma),    # sell_thresh_ma（売りトリガー閾値）
        compute_threshold(sell_returns, sell_base_prev, sell_dir_prev, sell_agg_prev)  # sell_thresh_prev（売り指値乖離率）
    )


# ==========================================================
# 単利運用型・逆張りバックテスト（MA基準トリガー＋現在価格ベース指値）
# ==========================================================
def backtest_full_strategy_repeat(df, ma_period, lookback,
                                  buy_method_ma, buy_method_prev, sell_method_ma, sell_method_prev,
                                  initial_cash=100000, trade_amount=10000):

    df = df.copy()
    df["MA"] = df["終値"].rolling(ma_period).mean()
    df = df.dropna(subset=["MA", "終値", "高値", "安値"])

    total_profit = 0.0               # 総利益
    trade_count = 0                  # トレード回数（約定ベース）
    trade_profits = []               # 各トレード利益率履歴
    history = []                     # 損益履歴（評価額推移）

    for i in range(lookback, len(df)):
        # --- 過去データから閾値計算 ---
        buy_returns = df["安値"].iloc[i - lookback:i].pct_change().dropna().values
        sell_returns = df["高値"].iloc[i - lookback:i].pct_change().dropna().values
        buy_thresh_ma, buy_thresh_prev, sell_thresh_ma, sell_thresh_prev = get_thresholds(
            buy_returns, sell_returns, buy_method_ma, buy_method_prev, sell_method_ma, sell_method_prev
        )

        # --- 現在値 ---
        ma_val = df["MA"].iloc[i]
        current_price = df["終値"].iloc[i - 1]  # 現在価格（＝前日終値）
        cur_low = df["安値"].iloc[i]
        cur_high = df["高値"].iloc[i]

        # --- トリガー条件（逆張り）---
        # MA × (1 - buy_thresh_ma) <= 現在価格 → 指値を出す
        buy_trigger = ma_val * (1 - abs(buy_thresh_ma)) <= current_price
        sell_trigger = ma_val * (1 + abs(sell_thresh_ma)) >= current_price

        # --- 買い指値 ---
        if buy_trigger:
            # 現在価格を基準に買い指値を設定
            buy_price = current_price * (1 - abs(buy_thresh_prev))  # ← 修正ポイント（あなたの定義に準拠）
            sell_target = current_price * (1 + abs(sell_thresh_prev))
            
            if cur_low <= buy_price and cur_high >= sell_target:
                # その日の中で買い→売りが成立
                profit_pct = (sell_target - buy_price) / buy_price * 100
                profit = trade_amount * (profit_pct / 100)
                total_profit += profit
                trade_profits.append(profit_pct)
                trade_count += 1

        # --- 売り指値 ---
        elif sell_trigger:
            sell_price = current_price * (1 + abs(sell_thresh_prev))
            buy_back = current_price * (1 - abs(buy_thresh_prev))

            if cur_high >= sell_price and cur_low <= buy_back:
                profit_pct = (sell_price - buy_back) / sell_price * -100
                profit = trade_amount * (profit_pct / 100)
                total_profit += profit
                trade_profits.append(profit_pct)
                trade_count += 1

        # --- 損益履歴更新 ---
        history.append(initial_cash + total_profit)

    # --- ドローダウン計算 ---
    total_values = np.array(history)
    if len(total_values) == 0:
        return {
            "final_value": initial_cash,
            "profit_percent": 0,
            "max_drawdown": 0,
            "trade_count": 0,
            "avg_trade_profit": 0
        }

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
