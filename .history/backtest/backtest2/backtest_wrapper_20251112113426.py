from backtest_functions import backtest_full_strategy_repeat

def backtest_wrapper(params):
    ma, lb, bm, bp, sm, sp, df = params
    res = backtest_full_strategy_repeat(df, ma, lb, bm, bp, sm, sp)
    res.update({
        "MA": ma,
        "Lookback": lb,
        "Buy_MA": bm,
        "Buy_Prev": bp,
        "Sell_MA": sm,
        "Sell_Prev": sp
    })
    return res
