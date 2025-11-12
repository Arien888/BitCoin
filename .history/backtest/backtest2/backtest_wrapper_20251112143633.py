# backtest_wrapper.py
import pandas as pd
import numpy as np
from backtest_functions import backtest_full_strategy_repeat

def backtest_wrapper(params):
    """
    params = (MA, Lookback, Buy_MA, Buy_Prev, Sell_MA, Sell_Prev, df)
    """
    ma, lb, bm, bp, sm, sp, df = params

    # --- ここで MA基準トリガー判定を反映 ---
    # backtest_full_strategy_repeat 内で、例えば以下のように判定
    # if current_price >= MA * 基準割合:
    #     指値 = current_price * 基準割合
    # （詳細は backtest_functions 内で処理）

    res = backtest_full_strategy_repeat(df, ma, lb, bm, bp, sm, sp)

    # パラメータ情報を追加
    res.update({
        "MA": ma,
        "Lookback": lb,
        "Buy_MA": bm,
        "Buy_Prev": bp,
        "Sell_MA": sm,
        "Sell_Prev": sp
    })
    return res
