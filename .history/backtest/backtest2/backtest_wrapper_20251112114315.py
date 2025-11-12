# backtest_wrapper.py
from backtest_functions import backtest_full_strategy_repeat

def backtest_wrapper(params):
    ma, lb, bm, bp, sm, sp, df = params
    try:
        # バックテスト実行
        res = backtest_full_strategy_repeat(df, ma, lb, bm, bp, sm, sp)
        if not isinstance(res, dict):
            # 万が一戻り値が dict でない場合の保険
            res = {}
    except Exception as e:
        # バックテスト中に例外が出ても止めない
        print(f"バックテストエラー MA={ma}, LB={lb}: {e}")
        res = {}

    # 必須の列を最低限埋める
    res.setdefault("profit_percent", 0.0)
    res.setdefault("final_value", 0.0)
    res.setdefault("max_drawdown", 0.0)
    res.setdefault("trade_count", 0)
    res.setdefault("avg_trade_profit", 0.0)

    # パラメータ情報も追加
    res.update({
        "MA": ma,
        "Lookback": lb,
        "Buy_MA": bm,
        "Buy_Prev": bp,
        "Sell_MA": sm,
        "Sell_Prev": sp
    })

    return res
