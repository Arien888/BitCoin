import pandas as pd
from buy_logic import buy_condition

# ----------------------------
# テクニカル計算
# ----------------------------
def compute_indicators(df, ma_period, range_lb):
    df[f"ma{ma_period}"] = df["close"].rolling(ma_period).mean()
    df["range_high"] = df["high"].rolling(range_lb).max()
    df["range_low"] = df["low"].rolling(range_lb).min()
    df["range_pos"] = (df["close"] - df["range_low"]) / (df["range_high"] - df["range_low"])
    df["prev_close"] = df["close"].shift(1)
    df["prev_dir_up"] = df["close"] > df["prev_close"]
    return df.dropna()

# ----------------------------
# 1セットのパラメータでバックテスト
# ----------------------------
def run_backtest_one(df, ma_period, range_lb, tp_pct, sl_pct):
    df = compute_indicators(df.copy(), ma_period, range_lb)

    position = 0
    entry = 0
    entry_time = None

    trades = []
    trades_log = []     # ★ログ追加（ここ重要）

    peak = 1.0
    max_dd = 0.0

    for i, row in df.iterrows():

        # BUY
        if position == 0 and buy_condition(row, ma_period, dc=0.01, range_thr=0.3):
            position = 1
            entry = row["close"]
            entry_time = row["ts"] if "ts" in row else i   # ★ts が無いCSV用フォールバック
            continue

        # SELL
        if position == 1:
            pnl = (row["close"] - entry) / entry

            if pnl >= tp_pct or pnl <= -sl_pct:

                trades.append(pnl)

                # ★ログを追加
                trades_log.append({
                    "entry_time": entry_time,
                    "exit_time": row["ts"] if "ts" in row else i,
                    "entry_price": entry,
                    "exit_price": row["close"],
                    "pnl": pnl,
                    "reason": "TP" if pnl >= tp_pct else "SL"
                })

                position = 0

                peak = max(peak, 1 + pnl)
                max_dd = min(max_dd, (1 + pnl) / peak - 1)

    # ★ログ保存（トレードがあれば保存）
    if len(trades_log) > 0:
        pd.DataFrame(trades_log).to_csv("backtest_log.csv", index=False)

    # 取引ゼロの場合
    if len(trades) == 0:
        return 0, 0, 0, 0, max_dd

    total = sum(trades)
    winrate = sum(1 for x in trades if x > 0) / len(trades)
    avg = total / len(trades)

    return len(trades), total, winrate, avg, max_dd

# ----------------------------
# 手動 BUY 判定
# ----------------------------
def count_buy_signals(df):
    df = compute_indicators(df.copy(), 12, 24)
    cnt = 0
    for _, row in df.iterrows():
        if buy_condition(row, 12, dc=0.01, range_thr=0.3):
            cnt += 1
    return cnt

# ----------------------------
# 実行部
# ----------------------------
if __name__ == "__main__":
    df = pd.read_csv("btc_1h_full.csv")

    # cast float
    for c in ["open","high","low","close"]:
        df[c] = df[c].astype(float)

    print("Buy signals:", count_buy_signals(df))  # → 17のはず

    trades, total, win, avg, dd = run_backtest_one(df, 12, 24, tp_pct=0.004, sl_pct=0.01)
    print("Trades:", trades, "P/L:", total)

    print("ログ保存済み： backtest_log.csv")
