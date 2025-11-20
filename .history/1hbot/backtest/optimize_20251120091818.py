import pandas as pd
import numpy as np
from technicals import run_backtest_one

def optimize_fine(df, top_n=20):

    ma_list        = list(range(5, 36, 1))
    range_lb_list  = list(range(8, 16, 1))

    tp_list = [round(x, 4) for x in np.arange(0.0020, 0.0061, 0.0005)]
    sl_list = [round(x, 4) for x in np.arange(0.0020, 0.0061, 0.0005)]

    ma_dc_list  = [round(x, 3) for x in np.arange(0.002, 0.016, 0.001)]
    low_thr_list  = [round(x, 2) for x in np.arange(0.20, 0.46, 0.05)]
    high_thr_list = [round(x, 2) for x in np.arange(0.55, 0.86, 0.05)]

    results = []
    count = 0

    for ma in ma_list:
        for rng in range_lb_list:
            for tp in tp_list:
                for sl in sl_list:
                    for ma_dc in ma_dc_list:
                        for low_thr in low_thr_list:
                            for high_thr in high_thr_list:

                                trades, total, win, avg, dd = run_backtest_one(
                                    df.copy(),
                                    ma, rng, tp, sl,
                                    ma_dc, low_thr, high_thr
                                )

                                count += 1

                                # tradeが少なすぎるパラメータはスキップ
                                if trades < 30:
                                    continue

                                results.append({
                                    "ma": ma,
                                    "range": rng,
                                    "tp": tp,
                                    "sl": sl,
                                    "ma_dc": ma_dc,
                                    "low_thr": low_thr,
                                    "high_thr": high_thr,
                                    "trades": trades,
                                    "total": total,
                                    "winrate": win,
                                    "avg": avg,
                                    "maxdd": dd
                                })

    # P/Lでソート
    results.sort(key=lambda x: x["total"], reverse=True)

    print(f"\n===== 完了：{len(results)} 通りが有効 =====")
    print("===== 最強パラメータ TOP20 =====")

    for r in results[:top_n]:
        print(
            f"MA={r['ma']:>2}, RNG={r['range']:<3}, TP={r['tp']}, SL={r['sl']}, "
            f"ma_dc={r['ma_dc']}, low_thr={r['low_thr']}, high_thr={r['high_thr']} | "
            f"Trades={r['trades']}, P/L={r['total']:.3f}, Win={r['winrate']*100:.1f}%, "
            f"DD={r['maxdd']:.3f}"
        )

if __name__ == "__main__":
    df = pd.read_csv("btc_1h_full.csv")
    for col in ["open","high","low","close"]:
        df[col] = df[col].astype(float)
    optimize_fine(df, top_n=20)


def split_into_periods(df, months=3):
    df = df.sort_values("ts")
    rows_per_period = months * 30 * 24  # 1h足 = 720本/月

    periods = []
    for start in range(0, len(df), rows_per_period):
        end = start + rows_per_period
        periods.append(df.iloc[start:end].copy())

    return periods
