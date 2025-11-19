import pandas as pd
import numpy as np
from joblib import Parallel, delayed
from technicals import run_backtest_one


def run_one(df, ma, rng, tp, sl, range_pos_thr):
    """1パターン実行（例外はログを返す）"""
    try:
        trades, total, win, avg, dd = run_backtest_one(
            df, ma, rng, tp, sl,
            range_pos_thr=range_pos_thr
        )
        return {
            "ma": ma, "rng": rng, "tp": tp, "sl": sl,
            "trades": trades, "total": total, "win": win
        }
    except Exception as e:
        return {
            "ma": ma, "rng": rng, "tp": tp, "sl": sl,
            "trades": 0, "total": -9999, "win": 0,
            "error": str(e)
        }


def optimize_buy_conditions(df):

    # 探索パラメータ
    ma_list  = list(range(1, 201, 20))
    rng_list = list(range(1, 201, 20))

    tp_list = [round(x, 3) for x in np.arange(0.001, 1.001, 0.01)]
    sl_list = [round(x, 3) for x in np.arange(0.001, 1.001, 0.01)]

    range_pos_thr = 0.40

    print("===== START OPTIMIZATION =====")

    # 並列実行
    results = Parallel(n_jobs=-1, backend="loky", verbose=10)(
        delayed(run_one)(df, ma, rng, tp, sl, range_pos_thr)
        for ma in ma_list
        for rng in rng_list
        for tp in tp_list
        for sl in sl_list
    )

    # DataFrame化（扱いやすい）
    df_res = pd.DataFrame(results)

    # 例外ログも保存できる
    df_res.to_csv("optimize_results.csv", index=False)

    # 最高利益の行を抽出
    best = df_res.loc[df_res["total"].idxmax()]

    print("\n===== 最強パラメータ =====")
    print(best)


if __name__ == "__main__":

    df = pd.read_csv("btc_1h_full.csv")
    for col in ["open", "high", "low", "close"]:
        df[col] = df[col].astype(float)

    optimize_buy_conditions(df)
