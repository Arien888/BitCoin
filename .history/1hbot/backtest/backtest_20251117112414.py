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
def run_backtest_one(df_raw: pd.DataFrame, params: dict):
    df = df_raw.copy()

    ma_period   = params["ma_period"]
    range_lb    = params["range_lb"]
    low_thr     = params["low_thr"]      # 0.0〜0.5くらい
    high_thr    = params["high_thr"]     # 0.5〜1.0くらい
    entry_ma_dc = params["entry_ma_dc"]  # MA 乖離（例: 0.003 → 0.3% 下で買う）
    tp_pct      = params["tp_pct"]       # 利確幅
    sl_pct      = params["sl_pct"]       # 損切り幅

    df = compute_ma(df, ma_period)
    df = compute_range(df, range_lb)
    df = compute_prev(df)

    # 先頭のNaN区間を飛ばす
    df = df.dropna().reset_index(drop=True)

    position = 0  # 0: ノーポジ, 1: ロング
    entry_price = 0.0
    equity = 0.0
    equity_curve = [equity]
    trades = []

    for i in range(1, len(df)):
        row = df.iloc[i]

        ma_value = row[f"ma{ma_period}"]

        # --- シグナル ---
        # エントリー: MAより一定割合下 + レンジ下側 + 直前は下方向（Prevで反転狙い）
        buy_signal = (
            position == 0
            and row["close"] < ma_value * (1.0 - entry_ma_dc)
            and row["range_pos"] < low_thr
            and row["prev_dir_up"] is False
        )

        # イグジット: MA上抜け or 利確 or 損切り or レンジ上側
        sell_signal = (
            position == 1
            and (
                row["close"] > ma_value            # MA超え
                or row["close"] >= entry_price * (1.0 + tp_pct)  # 利確
                or row["close"] <= entry_price * (1.0 - sl_pct)  # 損切り
                or row["range_pos"] > high_thr    # レンジ上側
            )
        )

        # --- 実行 ---
        if buy_signal:
            position = 1
            entry_price = row["close"]

        elif sell_signal:
            profit = row["close"] - entry_price
            equity += profit
            trades.append(profit)
            position = 0
            entry_price = 0.0

        equity_curve.append(equity)

    # 最後まで決済しないポジは無視（保守的）
    if not trades:
        return {
            "total_profit": 0.0,
            "trade_count": 0,
            "win_rate": 0.0,
            "avg_profit": 0.0,
            "max_dd": 0.0,
        }

    # 最大ドローダウン（簡易）
    ec_series = pd.Series(equity_curve)
    running_max = ec_series.cummax()
    drawdown = ec_series - running_max
    max_dd = drawdown.min()  # マイナス値

    total_profit = sum(trades)
    trade_count = len(trades)
    win_rate = sum(1 for p in trades if p > 0) / trade_count
    avg_profit = total_profit / trade_count

    return {
        "total_profit": total_profit,
        "trade_count": trade_count,
        "win_rate": win_rate,
        "avg_profit": avg_profit,
        "max_dd": max_dd,
    }

# =========================
# パラメータ総当たり
# =========================
def optimize(df: pd.DataFrame, top_n: int = 20):
    ma_list        = [12, 16, 20, 24]
    range_list     = [24, 48, 72, 120, 200, 300]     # 広げる
    low_thr_list   = [0.0, 0.2, 0.4, 0.6]            # 緩める
    high_thr_list  = [0.6, 0.8, 1.0]                 # 上側も増やす
    entry_dc_list  = [0.001, 0.002, 0.004]          # 緩める
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

