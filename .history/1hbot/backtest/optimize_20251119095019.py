import pandas as pd
from technicals import run_backtest_one
import numpy as np
from multiprocessing import Pool, cpu_count


def worker(params):
    df, ma, rng, tp, sl, ma_ratio, range_thr = params
    trades, total, win, avg, dd = run_backtest_one(
        df.copy(),
        ma, rng, tp, sl,
        ma_ratio, range_thr
    )
    
    return {
        "ma": ma,
        "range": rng,
        "tp": tp,
        "sl": sl,
        "ma_ratio": ma_ratio,
        "range_thr": range_thr,
        "trades": trades,
        "total": total,
        "winrate": win,
        "avg": avg,
        "maxdd": dd
    }


def optimize(df, top_n=30):

    # --- 検索範囲 ---
    sl_list = [round(x, 4) for x in np.arange(0.001, 1.0001, 0.01)]
    tp_list = [round(x, 4) for x in np.arange(0.001, 1.0001, 0.01)]

    ma_list = list(range(1, 201, 20))
    range_list = list(range(1, 201, 20))

    buy_ma_ratio_list = [round(x, 1) for x in np.arange(0.1, 1.01, 0.1)]
    range_pos_thr_list = [round(x, 1) for x in np.arange(0.1, 1.01, 0.1)]

    # パラメータ組み合わせを作成
    params = []
    for ma in ma_list:
        for rng in range_list:
            for tp in tp_list:
                for sl in sl_list:
                    for ma_ratio in buy_ma_ratio_list:
                        for range_thr in range_pos_thr_list:
                            params.append((df, ma, rng, tp, sl, ma_ratio, range_thr))

    print(f"総パターン数: {len(params)}")
    print(f"CPU: {cpu_count()} cores → multiprocessing 開始...")

    # --- multiprocessing ---
    with Pool(cpu_count()) as p:
        results = p.map(worker, params)

    # --- sort ---
    results.sort(key=lambda x: x["total"], reverse=True)

    print("\n===== TOP パラメータ候補 =====")
    for r in results[:top_n]:
        print(
            f"MA={r['ma']}, Range={r['range']}, TP={r['tp']}, SL={r['sl']}, "
            f"MA_ratio={r['ma_ratio']}, range_thr={r['range_thr']} | "
            f"Trades={r['trades']}, P/L={r['total']:.3f}, "
            f"Win={r['winrate']*100:.1f}%, Avg={r['avg']:.3f}, "
            f"MaxDD={r['maxdd']:.3f}"
        )


if __name__ == "__main__":
    df = pd.read_csv("btc_1h_full.csv")
    for col in ["open","high","low","close"]:
        df[col] = df[col].astype(float)

    optimize(df)
