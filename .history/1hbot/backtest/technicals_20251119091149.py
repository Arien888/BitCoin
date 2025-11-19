# technicals.py
import pandas as pd

# =========================
# テクニカル計算
# =========================
def compute_ma(df, period: int):
    df[f"ma{period}"] = df["close"].rolling(period).mean()
    return df

def compute_range(df, lookback: int):
    df["range_high"] = df["high"].rolling(lookback).max()
    df["range_low"] = df["low"].rolling(lookback).min()
    df["range_pos"] = (df["close"] - df["range_low"]) / (df["range_high"] - df["range_low"])
    return df

def compute_prev(df):
    df["prev_close"] = df["close"].shift(1)
    df["prev_dir_up"] = df["close"] > df["prev_close"]
    return df


# =========================
# 1セットのパラメータでバックテスト
# =========================
def run_backtest_one(df, ma_period, range_lb, tp_pct, sl_pct):

    df = df.copy()
    df[f"ma{ma_period}"] = df["close"].rolling(ma_period).mean()
    df["range_high"] = df["high"].rolling(range_lb).max()
    df["range_low"] = df["low"].rolling(range_lb).min()
    df["range_pos"] = (df["close"] - df["range_low"]) / (df["range_high"] - df["range_low"])
    df["prev_close"] = df["close"].shift(1)
    df["prev_dir_up"] = df["close"] > df["prev_close"]
    df = df.dropna()

    position = 0
    entry_price = 0
    trades = []
    max_dd = 0
    cur_peak = 1.0

    for i, row in df.iterrows():
        ma_value = row[f"ma{ma_period}"]

        # ---- BUY ----
        buy_signal = (
            position == 0
            and row["close"] < ma_value * 0.99
            and row["range_pos"] < 0.3
            and not row["prev_dir_up"]
        )

        if buy_signal:
            position = 1
            entry_price = row["close"]
            continue

        # ---- SELL with high/low TP/SL ----
        if position == 1:

            tp_price = entry_price * (1 + tp_pct)
            sl_price = entry_price * (1 - sl_pct)

            # 1) TP: high が TP に届いた
            if row["high"] >= tp_price:
                pnl = tp_pct
                position = 0
                trades.append(pnl)

            # 2) SL: low が SL を割った
            elif row["low"] <= sl_price:
                pnl = -sl_pct
                position = 0
                trades.append(pnl)

            # ポジション決済後はDD計算
            if position == 0 and len(trades) > 0:
                pnl_last = trades[-1]
                cur_peak = max(cur_peak, 1 + pnl_last)
                max_dd = min(max_dd, (1 + pnl_last) / cur_peak - 1)

    # ---- レポート ----
    if len(trades) == 0:
        return 0, 0.0, 0.0, 0.0, 0.0

    total = sum(trades)
    winrate = sum(x > 0 for x in trades) / len(trades)
    avg = total / len(trades)

    return len(trades), total, winrate, avg, max_dd
