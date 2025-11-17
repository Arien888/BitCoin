import pandas as pd

# ------------------------------------
# MA
# ------------------------------------
def compute_ma(df, period=20):
    df[f"ma{period}"] = df["close"].rolling(period).mean()
    return df

# ------------------------------------
# Range
# ------------------------------------
def compute_range(df, lookback=24):
    df["range_high"] = df["high"].rolling(lookback).max()
    df["range_low"] = df["low"].rolling(lookback).min()
    df["range_pos"] = (df["close"] - df["range_low"]) / (df["range_high"] - df["range_low"])
    return df

# ------------------------------------
# Prev
# ------------------------------------
def compute_prev(df):
    df["prev_close"] = df["close"].shift(1)
    df["prev_dir"] = df["close"] > df["prev_close"]
    return df

# ------------------------------------
# Backtest
# ------------------------------------
def backtest(df, ma_period=20, range_lb=24):
    df = compute_ma(df, ma_period)
    df = compute_range(df, range_lb)
    df = compute_prev(df)

    position = 0
    entry_price = 0
    trades = []

    for i in range(1, len(df)):
        row = df.iloc[i]



        sell_signal = (
            row["close"] > row[f"ma{ma_period}"]
            or row["close"] >= entry_price * 1.005   # +0.5% 利確
            or row["close"] <= entry_price * 0.99    # -1% 損切り
        )


        if position == 0 and buy_signal:
            position = 1
            entry_price = row["close"]

        elif position == 1 and sell_signal:
            trades.append(row["close"] - entry_price)
            position = 0

    return sum(trades), trades

# ------------------------------------
# 実行部
# ------------------------------------
if __name__ == "__main__":
    df = pd.read_csv("btc_1h.csv")

    total_profit, trades = backtest(df)

    print("\n===== Backtest Result =====")
    print("Trade count:", len(trades))
    print("Total Profit:", total_profit)
    if trades:
        print("Average Profit:", total_profit / len(trades))
    else:
        print("Average Profit: 0")
