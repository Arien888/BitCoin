import backtrader as bt
import pandas as pd
from calc_change_rate import calculate_avg_change_rate  # 外部ファイルからインポート
from config import strategy_params


class BuyOnlyStrategy(bt.Strategy):
    params = strategy_params

    def __init__(self):
        self.starting_cash = None

    def start(self):
        self.starting_cash = self.p.initial_cash

    def next(self):
        idx = len(self) - 1  # 現在のインデックス
        data_len = len(self.data)  # 全体の長さ

        # 前後30日は検証しない
        if idx < 30 or idx > data_len - 30:
            return

        # 過去30日のデータを取得して DataFrame にする
        closes = [self.data.close[-i] for i in range(29, -1, -1)]
        lows = [self.data.low[-i] for i in range(29, -1, -1)]
        dates = [self.data.datetime.date(-i) for i in range(29, -1, -1)]

        df = pd.DataFrame({"datetime": dates, "close": closes, "low": lows})

        avg_rate = calculate_avg_change_rate(df)
        today = self.data.datetime.date(0)
        print(f"{today} 過去30日変化率平均: {avg_rate:.4%}")

        # 閾値より悪化していたら買い戦略を発動（例：-2%以下）
        if avg_rate < -0.02:
            price = self.data.close[0]
            cash = self.broker.get_cash()
            buy_amount = cash * self.p.buy_ratio
            buy_size = round(buy_amount / price, 5)

            limit_price = price * self.p.buy_price_multiplier

            if buy_size > 0:
                self.buy(size=buy_size, price=limit_price, exectype=bt.Order.Limit)
                print(f"{today} 指値買い {buy_size} BTC @ {limit_price}")

        # 利確ロジック（元のまま）
        position_size = self.position.size
        if position_size > 0:
            price = self.data.close[0]
            sell_amount = self.broker.get_value() * 0.01
            sell_size = round(min(sell_amount / price, position_size), 5)
            limit_price_sell = price * self.p.sell_price_multiplier

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
