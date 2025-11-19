import pandas as pd
from technicals import run_backtest_one
import numpy as np
def optimize(df, top_n=20):

    sl_list = [0.010]
    tp_list = [round(x, 4) for x in np.arange(0.014, 0.017, 0.005)]
    ma_list = [12]
    range_list = [48]



    results = []

    for ma in ma_list:
        for rng in range_list:
            for tp in tp_list:
                for sl in sl_list:

                    trades, total, win, avg, dd = run_backtest_one(
                        df.copy(), ma, rng, tp, sl
                    )

                    results.append({
                        "ma": ma,
                        "range": rng,
                        "tp": tp,
                        "sl": sl,
                        "trades": trades,
                        "total": total,
                        "winrate": win,
                        "avg": avg,
                        "maxdd": dd
                    })

    # P/L 優先でソート
    results.sort(key=lambda x: x["total"], reverse=True)

    print("\n===== TOP パラメータ候補 =====")
    for r in results[:top_n]:
        print(
            f"MA={r['ma']}, Range={r['range']}, TP={r['tp']}, SL={r['sl']} | "
            f"Trades={r['trades']}, P/L={r['total']:.3f}, Win={r['winrate']*100:.1f}%, "
            f"Avg={r['avg']:.3f}, MaxDD={r['maxdd']:.3f}"
        )

if __name__ == "__main__":
    df = pd.read_csv("btc_1h_full.csv")
    for col in ["open","high","low","close"]:
        df[col] = df[col].astype(float)

    optimize(df, top_n=20)
