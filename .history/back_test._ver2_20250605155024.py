import backtrader as bt

# ✅ ここで初期設定を一か所にまとめる
strategy_params = {
    "initial_cash": 10000000,
    "sell_price_multiplier": 1.02,
    "buy_price_multiplier": 0.9,
}


class BuyOnlyStrategy(bt.Strategy):
    params = strategy_params  # ✅ 同じ辞書を使うので繰り返さない

    def __init__(self):
        self.buy_date = None  # 買った日の記憶用
        self.sell_date = None
        self.starting_cash = None

    def start(self):
        # ブローカーの現金は設定後なので、paramsで保持した値を使うだけでもOK
        self.starting_cash = self.p.initial_cash

    def next(self):
        today = self.data.datetime.date(0)  # 今日の日付取得
        price = self.data.close[0]
        cash = self.broker.get_cash()  # 今の現金残高を取得
        buy_amount = cash * 0.01  # 資金の1%分だけ買う

        buy_size = buy_amount / price  # 買うBTC量を計算
        buy_size = round(buy_size, 5)  # BTCは小数点切り捨て調整

        # 指値価格を現在価格の1%安に設定
        limit_price = price * self.p.buy_price_multiplier

        if buy_size > 0:
            self.buy(size=buy_size, price=limit_price, exectype=bt.Order.Limit)
            print(f"{today} 指値買い {buy_size} BTC @ {limit_price}")

        # 1%分の金額に相当する売る量
        position_size = self.position.size
        if position_size > 0:
            sell_amount = self.broker.get_value() * 0.01  # 総資産の1%分を売る
            sell_size = round(sell_amount / price, 5)

            limit_price_sell = sell_size * self.p.sell_price_multiplier

            # 持ちポジションより多く売らないように調整
            sell_size = min(sell_size, position_size)
            if sell_size > 0:
                self.sell(
                    size=sell_size, price=limit_price_sell, exectype=bt.Order.Limit
                )
            print(f"{today} 指値売り {sell_size} BTC @ {limit_price_sell}")

    def notify_order(self, order):
        if order.status in [order.Completed]:
            print(
                f"注文約定: {order.getordername()} {order.executed.price} {order.executed.size}"
            )
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            print(f"注文キャンセル・拒否: {order.getordername()}")

    def stop(self):
        final_value = self.broker.getvalue()
        final_profit = final_value - self.starting_cash
        with open("result.txt", "w") as f:
            f.write(f"最終資産額: {final_value}\n")
            f.write(f"最終利益: {final_profit}\n")
        print("結果をresult.txtに保存しました")


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
