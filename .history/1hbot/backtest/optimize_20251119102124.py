import pandas as pd
import numpy as np
from joblib import Parallel, delayed
from technicals import run_backtest_one

def optimize_buy_conditions(df):

    ma_list  = list(range(1, 201, 20))
    rng_list = list(range(1, 201, 20))

    tp_list =  [round(x, 3) for x in np.arange(0.001, 1.001, 0.01)]
    sl_list =  [round(x, 3) for x in np.arange(0.001, 1.001, 0.01)]

    range_pos_thr = 0.40

    print("===== START OPTIMIZATION =====")

    # 並列実行
    def run_one(ma, rng, tp, sl):
        trades, total, win, avg, dd = run_backtest_one(
            df, ma, rng, tp, sl,
            range_pos_thr=range_pos_thr
        )
        return {
            "ma": ma, "rng": rng, "tp": tp, "sl": sl,
            "trades": trades, "total": total, "win": win
        }

    results = Parallel(n_jobs=-1, backend="loky", verbose=10)(
        delayed(run_one)(ma, rng, tp, sl)
        for ma in ma_list
        for rng in rng_list
        for tp in tp_list
        for sl in sl_list
    )

    best = max(results, key=lambda x: x["total"])

    print("\n===== 最強パラメータ =====")
    print(best)
