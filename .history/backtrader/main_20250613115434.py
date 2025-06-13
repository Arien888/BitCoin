import backtrader as bt
from config import strategy_params
from backtrader.strategy import BuyOnlyStrategy


cerebro = bt.Cerebro()
cerebro.broker.setcash(strategy_params["initial_cash"])
cerebro.addstrategy(BuyOnlyStrategy, **strategy_params)

data = bt.feeds.GenericCSVData(
    dataname="binance_btc.csv",
    dtformat="%Y-%m-%d %H:%M:%S",
    datetime=0,
    open=1,
    high=2,
    low=3,
    close=4,
    volume=5,
    openinterest=-1,
)

cerebro.adddata(data)

print(f"開始資金: {cerebro.broker.getvalue():.2f}")

cerebro.run()
cerebro.plot()  # チャートを表示
