from backtest_functions import backtest_full_strategy_repeat

def backtest_wrapper(params):
    ma, lookback, buy_ma, buy_prev, sell_ma, sell_prev, df = params
    try:
        result = backtest_full_strategy_repeat(
            df, ma, lookback, buy_ma, buy_prev, sell_ma, sell_prev
        )
        result.update({
            "MA": ma,
            "Lookback": lookback,
            "Buy_MA": buy_ma,
            "Buy_Prev": buy_prev,
            "Sell_MA": sell_ma,
            "Sell_Prev": sell_prev
        })
        return result
    except Exception as e:
        return {"error": str(e)}
