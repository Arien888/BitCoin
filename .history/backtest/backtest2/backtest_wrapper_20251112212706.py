from backtest_functions import backtest_full_strategy_repeat

# ==========================================================
# ラッパー（並列実行用）
# ----------------------------------------------------------
# params = (ma, lb, bm, bp, sm, sp, df, mode)
# ma（MA期間）, lb（lookback期間）
# bm（Buy_MAメソッド）, bp（Buy_Prevメソッド）
# sm（Sell_MAメソッド）, sp（Sell_Prevメソッド）
# df（価格DataFrame）, mode（"simple" or "range"）
# ==========================================================
def backtest_wrapper(params):
    ma, lb, bm, bp, sm, sp, df, mode = params
    res = backtest_full_strategy_repeat(
        df=df,
        ma_period=ma,
        lookback=lb,
        buy_method_ma=bm,
        buy_method_prev=bp,
        sell_method_ma=sm,
        sell_method_prev=sp,
        mode=mode  # "simple"（全売買） / "range"（レンジ調整）
    )
    # 付随情報を付け足して返す
    res.update({
        "Mode": mode,       # Mode（戦略モード）
        "MA": ma,           # MA（移動平均期間）
        "Lookback": lb,     # Lookback（閾値算出期間）
        "Buy_MA": bm,       # Buy_MA（買いMAトリガーの方法名）
        "Buy_Prev": bp,     # Buy_Prev（買い指値の乖離率の方法名）
        "Sell_MA": sm,      # Sell_MA（売りMAトリガーの方法名）
        "Sell_Prev": sp,    # Sell_Prev（売り指値の乖離率の方法名）
    })
    return res
