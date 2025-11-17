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

# =========================
# パラメータ総当たり
# =========================
def optimize(df: pd.DataFrame, top_n: int = 20):
    ma_list        = [12, 16, 20, 24]
    range_list     = [24, 48, 72, 120, 200, 300]     # 広げる
    low_thr_list   = [0.1, 0.2, 0.3, 0.4, 0.6]           # 緩める
    high_thr_list  = [0.6, 0.8, 1.0]                 # 上側も増やす
    entry_dc_list  = [0.002, 0.004, 0.006, 0.01]        # 緩める
    tp_list        = [0.002, 0.004, 0.006, 0.01]     # 多めに探索
    sl_list        = [0.005, 0.01, 0.02]             # 多め


    results = []

    for ma_p, rng, low_t, high_t, edc, tp, sl in itertools.product(
        ma_list, range_list, low_thr_list, high_thr_list, entry_dc_list, tp_list, sl_list
    ):
        params = {
            "ma_period": ma_p,
            "range_lb": rng,
            "low_thr": low_t,
            "high_thr": high_t,
            "entry_ma_dc": edc,
            "tp_pct": tp,
            "sl_pct": sl,
        }

        stats = run_backtest_one(df, params)

        # トレード回数が少なすぎるのは除外
        # if stats["trade_count"] < 5:
        #     continue

        # シンプルに「総利益が大きい順」でソート
        results.append({
            **params,
            **stats,
        })

    if not results:
        print("有効な結果がありません（トレード回数が少なすぎるなど）。")
        return

    # ソート基準：総利益（必要なら max_dd で調整してもOK）
    results.sort(key=lambda x: x["total_profit"], reverse=True)

    print("\n===== TOP パラメータ候補 =====")
    for r in results[:top_n]:
        print(
            f"MA={r['ma_period']:>2}, "
            f"Range={r['range_lb']:>3}, "
            f"low={r['low_thr']:.1f}, high={r['high_thr']:.1f}, "
            f"dc={r['entry_ma_dc']:.3f}, TP={r['tp_pct']:.3f}, SL={r['sl_pct']:.3f} | "
            f"Trades={r['trade_count']:>3}, "
            f"P/L={r['total_profit']:.2f}, "
            f"Win={r['win_rate']*100:5.1f}%, "
            f"Avg={r['avg_profit']:.2f}, "
            f"MaxDD={r['max_dd']:.2f}"
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

