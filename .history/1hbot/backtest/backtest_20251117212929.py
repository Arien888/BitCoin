import pandas as pd
import itertools



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

        # ---- BUY（手動17回と完全一致） ----
        buy_signal = (
            position == 0
            and row["close"] < ma_value * 0.99     # -1%
            and row["range_pos"] < 0.3             # 0.3
            and (row["prev_dir_up"] == False)
        )

        if buy_signal:
            position = 1
            entry_price = row["close"]
            continue

        # ---- SELL ----
        if position == 1:
            pnl = (row["close"] - entry_price) / entry_price

            if pnl >= tp_pct or pnl <= -sl_pct:
                trades.append(pnl)
                position = 0

                cur_peak = max(cur_peak, 1 + pnl)
                max_dd = min(max_dd, (1 + pnl) / cur_peak - 1)

    # 結果
    if len(trades) == 0:
        return 0, 0.0, 0.0, 0.0, 0.0

    total = sum(trades)
    winrate = sum([1 for x in trades if x > 0]) / len(trades)
    avg = total / len(trades)

    return len(trades), total, winrate, avg, max_dd

# =========================
# パラメータ総当たり
# =========================
def optimize(df, top_n=20):

    ma_list    = [12, 16, 20]
    range_list = [24, 48, 72]
    tp_list    = [0.002, 0.004]
    sl_list    = [0.005, 0.01]

    results = []

    for ma_p in ma_list:
        for rng in range_list:
            for tp in tp_list:
                for sl in sl_list:

                    trades, total, winrate, avgp, max_dd = run_backtest_one(
                        df,
                        ma_p,
                        rng,
                        tp,
                        sl
                    )

                    results.append({
                        "ma": ma_p,
                        "range": rng,
                        "tp": tp,
                        "sl": sl,
                        "trades": trades,
                        "total": total,
                        "winrate": winrate,
                        "avg": avgp,
                        "max_dd": max_dd
                    })

    # 利益順にソート
    results.sort(key=lambda x: x["total"], reverse=True)

    print("\n===== TOP パラメータ候補 =====")
    for r in results[:top_n]:
        print(
            f"MA={r['ma']}, Range={r['range']}, TP={r['tp']}, SL={r['sl']} | "
            f"Trades={r['trades']}, P/L={r['total']:.2f}, Win={r['winrate']*100:.1f}%, "
            f"Avg={r['avg']:.2f}, MaxDD={r['max_dd']:.2f}"
        )



df = pd.read_csv("btc_1h_full.csv")
for col in ["open","high","low","close"]:
    df[col] = df[col].astype(float)

df = compute_ma(df, 12)
df = compute_range(df, 24)
df = compute_prev(df)
df = df.dropna()

cnt = 0
for i, row in df.iterrows():
    if (
        row["close"] < row["ma12"] * (1 - 0.01) and   # 1% below
        row["range_pos"] < 0.3 and
        not row["prev_dir_up"]
    ):
        cnt += 1

print("Buy signals:", cnt)


# =========================
# 実行部
# =========================
if __name__ == "__main__":
    # 1h データ読み込み（6ヶ月版）
    df = pd.read_csv("btc_1h_full.csv")

    # BitgetのCSVは文字列の可能性があるのでキャスト
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)

    optimize(df, top_n=20)

