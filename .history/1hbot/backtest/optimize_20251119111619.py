import pandas as pd
import numpy as np
from technicals import run_backtest_one


def optimize(df, top_n=30):
    # ===== 探索範囲 =====
    # MA と Range は「フィルターとして意味がある」範囲だけ
    ma_list = list(range(5, 201, 10))    # 5, 15, 25, ..., 195
    range_list = list(range(10, 201, 10))  # 10, 20, ..., 200

    # TP / SL は現実的なリスクリワードに限定
    tp_list = [round(x, 3) for x in np.arange(0.002, 0.0201, 0.002)]  # 0.2%〜2.0%
    sl_list = [round(x, 3) for x in np.arange(0.004, 0.0301, 0.002)]  # 0.4%〜3.0%

    # BUY条件は最適化済みなので固定
    range_pos_thr = 0.40

    # 過剰フィット防止用：最低トレード数
    min_trades = 30

    results = []

    print("===== パラメータ探索開始 =====")
    print(f"MA候補: {ma_list}")
    print(f"Range候補: {range_list}")
    print(f"TP候補: {tp_list}")
    print(f"SL候補: {sl_list}")
    print(f"range_pos_thr: {range_pos_thr}, min_trades: {min_trades}")
    print("================================\n")

    for ma in ma_list:
        for rng in range_list:
            for tp in tp_list:
                for sl in sl_list:

                    trades, total, win, avg, dd = run_backtest_one(
                        df.copy(),
                        ma_period=ma,
                        range_lb=rng,
                        tp_pct=tp,
                        sl_pct=sl,
                        range_pos_thr=range_pos_thr,
                    )

                    # トレードが少なすぎるものは捨てる
                    if trades < min_trades:
                        continue

                    results.append({
                        "ma": ma,
                        "range": rng,
                        "tp": tp,
                        "sl": sl,
                        "trades": trades,
                        "total": total,
                        "winrate": win,
                        "avg": avg,
                        "maxdd": dd,
                    })

    if not results:
        print("有効な結果がありませんでした（min_trades が厳しすぎる可能性）")
        return

    # ===== ソート基準 =====
    # 1. 総利益 total が大きい
    # 2. 勝率 winrate が高い
    # 3. 最大DD が小さい（dd は負の値なので -dd を見る）
    results.sort(
        key=lambda x: (x["total"], x["winrate"], -x["maxdd"]),
        reverse=True
    )

    print("\n===== TOP パラメータ候補 =====")
    for r in results[:top_n]:
        print(
            f"MA={r['ma']:3d}, Range={r['range']:3d}, "
            f"TP={r['tp']:.3f}, SL={r['sl']:.3f} | "
            f"Trades={r['trades']:4d}, P/L={r['total']:.3f}, "
            f"Win={r['winrate']*100:5.1f}%, "
            f"Avg={r['avg']:.4f}, MaxDD={r['maxdd']:.3f}"
        )

    # 一番良かったやつを最後にまとめて表示
    best = results[0]
    print("\n===== 最強パラメータ（現実的フィルター後）=====")
    print(best)


if __name__ == "__main__":
    df = pd.read_csv("btc_1h_full.csv")
    for col in ["open", "high", "low", "close"]:
        df[col] = df[col].astype(float)

    optimize(df, top_n=20)
