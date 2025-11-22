import pandas as pd


# ============================================================
# インジケータ（strategy.py と完全一致）
# ============================================================
def compute_indicators(df, ma_period, range_lb):
    df = df.copy()

    # MA
    df[f"ma{ma_period}"] = df["close"].rolling(ma_period).mean()

    # レンジ
    df["range_high"] = df["high"].rolling(range_lb).max()
    df["range_low"]  = df["low"].rolling(range_lb).min()
    df["range_pos"]  = (df["close"] - df["range_low"]) / (df["range_high"] - df["range_low"])

    # ヒゲ（strategy.py の定義と完全一致）
    df["lower_wick"] = df["close"] - df["low"]
    df["range_total"] = df["high"] - df["low"]
    df["wick_ratio"] = df["lower_wick"] / df["range_total"]

    # 前ローソク
    df["prev_close"] = df["close"].shift(1)
    df["prev_dir_up"] = df["close"] > df["prev_close"]

    return df.dropna().reset_index(drop=True)



# ============================================================
# ★ 完全同期バックテスト
# ============================================================
def run_backtest_one(
    df,
    ma_period,
    range_lb,
    tp_pct,
    sl_pct,
    ma_dc,
    low_thr,
    high_thr,
    wick_thr=0.55,
):
    df = compute_indicators(df.copy(), ma_period, range_lb)

    position = False
    entry_price = None
    entry_time = None

    trades = []
    trades_log = []

    equity = 1.0
    peak = 1.0
    max_dd = 0.0

    for i, row in df.iterrows():

        # ==================================================
        # 1) SELL ロジック（strategy.py と完全一致）
        # ==================================================
        if position:
            tp_price = entry_price * (1 + tp_pct)
            sl_price = entry_price * (1 - sl_pct)

            hit_tp = row["high"] >= tp_price
            hit_sl = row["low"]  <= sl_price
            hit_top = row["range_pos"] > high_thr

            if hit_tp or hit_sl or hit_top:
                pnl = (row["close"] - entry_price) / entry_price
                trades.append(pnl)

                trades_log.append({
                    "entry_time": entry_time,
                    "exit_time": row["ts"] if "ts" in row else i,
                    "entry_price": entry_price,
                    "exit_price": row["close"],
                    "pnl": pnl,
                    "reason": "TP" if hit_tp else ("SL" if hit_sl else "HighRange")
                })

                position = False
                entry_price = None

                equity *= (1 + pnl)
                peak = max(peak, equity)
                max_dd = min(max_dd, equity / peak - 1)

                continue

        # ==================================================
        # 2) BUY ロジック（strategy.py の BUY と完全一致）
        # ==================================================
        if not position:
            cond_wick = row["wick_ratio"] > wick_thr
            cond_ma = row["close"] < row[f"ma{ma_period}"] * (1 - ma_dc)
            cond_range = row["range_pos"] < low_thr
            cond_dir = (not row["prev_dir_up"])

            if cond_range and cond_wick and cond_ma and cond_dir:
                position = True
                entry_price = row["close"]
                entry_time = row["ts"] if "ts" in row else i
                continue

    # ==================================================
    # 出力
    # ==================================================
    if len(trades_log) > 0:
        pd.DataFrame(trades_log).to_csv("backtest_log.csv", index=False)

    if len(trades) == 0:
        return 0, 0, 0, 0, max_dd

    total = sum(trades)
    winrate = sum(1 for x in trades if x > 0) / len(trades)
    avg = total / len(trades)

    return len(trades), total, winrate, avg, max_dd
