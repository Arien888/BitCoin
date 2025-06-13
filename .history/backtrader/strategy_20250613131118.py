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
        idx = len(self) - 1
        data_len = len(self.data)

        if idx < 31 or idx > data_len - 1:
            return  # 前後30日を除外（1日ズレるので31必要）

        # 前日終値 → 翌日安値の変化率を30日分計算
        change_rates = []
        for i in range(30):
            close_today = self.data.close[-i - 1]
            low_next = self.data.low[-i]
            change = (low_next - close_today) / close_today
            change_rates.append(change)

        avg_rate = sum(change_rates) / len(change_rates)
        today = self.data.datetime.date(0)
        price = self.data.close[0]

        # 指値価格を計算
        limit_price = round(price * (1 + avg_rate), 2)

        # 資金の buy_ratio で購入サイズ計算
        cash = self.broker.get_cash()
        buy_amount = cash * self.p.buy_ratio
        buy_size = round(buy_amount / limit_price, 5)

        if buy_size > 0:
            self.buy(size=buy_size, price=limit_price, exectype=bt.Order.Limit)
            print(
                f"{today} 平均変化率: {avg_rate:.4%} → 指値買い {buy_size} BTC @ {limit_price}"
            )

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
