import pandas as pd

# ------------------------------
# 移動平均 (MA)
# ------------------------------
def compute_ma(df, period=20):
    df[f"ma{period}"] = df["close"].rolling(period).mean()
    return df

# ------------------------------
# レンジ（過去 lookback の高値安値）
# ------------------------------
def compute_range(df, lookback=24):
    df["range_high"] = df["high"].rolling(lookback).max()
    df["range_low"] = df["low"].rolling(lookback).min()
    df["range_pos"] = (df["close"] - df["range_low"]) / (df["range_high"] - df["range_low"])
    return df

# ------------------------------
# Prev（反転方向判断）
# ------------------------------
def compute_prev(df):
    df["prev_close"] = df["close"].shift(1)
    df["prev_dir"] = df["close"] > df["prev_close"]
    return df

# ------------------------------
# バックテスト本体（叩き台）
# ------------------------------
def backtest(df, ma_period=20, range_lb=24):
    df = compute_ma(df, ma_period)
    df = compute_range(df, range_lb)
    df = compute_prev(df)

    position = 0  # 0:ノーポジ, 1:ロング保持
    entry_price = 0
    profits = []

    for i in range(1, len(df)):
        row = df.iloc[i]

        # ▼ 仮ロジック（あなたの方向性を維持しつつ）
        buy_signal = (
            row["close"] < row[f"ma{ma_period}"]
            and row["range_pos"] < 0.1
            and row["prev_dir"] == False
        )

        sell_signal = (
            row["close"] > row[f"ma{ma_period}"]
            and row["range_pos"] > 0.9
        )

        # ▼ エントリー
        if position == 0 and buy_signal:
            position = 1
            entry_price = row["close"]

        # ▼ クローズ（利確 or 手仕舞い）
        elif position == 1 and sell_signal:
            profits.append(row["close"] - entry_price)
            position = 0

    total_profit = sum(profits)
    return total_profit, profits
