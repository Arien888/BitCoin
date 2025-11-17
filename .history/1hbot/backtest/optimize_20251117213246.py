# optimize.py
import pandas as pd
from technicals import compute_ma, compute_range, compute_prev, run_backtest_one


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

    results.sort(key=lambda x: x["total"], reverse=True)

    print("\n===== TOP パラメータ候補 =====")
    for r in results[:top_n]:
        print(
            f"MA={r['ma']}, Range={r['range']}, TP={r['tp']}, SL={r['sl']} | "
            f"Trades={r['trades']}, P/L={r['total']:.2f}, Win={r['winrate']*100:.1f}%, "
            f"Avg={r['avg']:.2f}, MaxDD={r['max_dd']:.2f}"
        )


# =========================
# メイン
# =========================
if __name__ == "__main__":

    # データ読み込み
    df = pd.read_csv("btc_1h_full.csv")

    # キャスト
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)

    # インジケータ準備
    df = compute_ma(df, 12)
    df = compute_range(df, 24)
    df = compute_prev(df)
    df = df.dropna()

    # BUY シグナル確認（手動一致用）
    cnt = 0
    for i, row in df.iterrows():
        if (
            row["close"] < row["ma12"] * 0.99 and
            row["range_pos"] < 0.3 and
            not row["prev_dir_up"]
        ):
            cnt += 1

    print("Buy signals:", cnt)

    # 最適化
    optimize(df, top_n=20)
