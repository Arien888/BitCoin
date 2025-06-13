import backtrader as bt
import pandas as pd
from config import strategy_params
import utils  # ユーティリティ関数をインポート


class BuyOnlyStrategy(bt.Strategy):
    params = strategy_params

    def __init__(self):
        self.starting_cash = None

    def start(self):
        self.starting_cash = self.p.initial_cash

    def next(self):  # 1日ごとの処理

        # レバレッジ設定
        price = self.data.close[0]  # 今日の終値取得
        equity = self.broker.getvalue()  # 現在の資産額取得
        max_position_value = (
            equity * self.p.leverage
        )  # レバレッジを考慮した最大ポジション額
        max_size = max_position_value / price  # 購入可能なサイズ計算

        idx = len(self) - 1  # 現在のインデックス
        data_len = len(self.data)  # データの長さ

        if idx < 31 or idx > data_len - 1:  # 前後30日を除外
            return  # 前後30日を除外（1日ズレるので31必要）

        avg_rate = utils.get_change_rates_low(self)  # 平均変化率計算
        today = self.data.datetime.date(0)  # 今日の日付取得
        price = self.data.close[0]  # 今日の終値取得

        # 指値価格を計算
        limit_price = round(price * (1 + avg_rate), 2)

        # 資金の buy_ratio で購入サイズ計算
        cash = self.broker.get_cash() # 現在の現金残高取得
        buy_amount = cash * self.p.buy_ratio # 購入額計算
        buy_size = round(buy_amount / limit_price, 5)

        if buy_size > 0:
            self.buy(size=buy_size, price=limit_price, exectype=bt.Order.Limit)
            print(
                f"{today} 平均変化率: {avg_rate:.4%} → 指値買い {buy_size} BTC @ {limit_price}"
            )

        # 利確ロジック（元のまま）
        position_size = self.position.size  # 現在のポジションサイズ
        if position_size > 0:  # ポジションがある場合
            price = self.data.close[0]  # 現在の価格
            sell_amount = self.broker.get_value() * 0.01  # 利確額（資産の1%）
            sell_size = round(min(sell_amount / price, position_size), 5)  # 利確サイズ

            limit_price_sell = round(
                price * (1 - utils.get_change_rates_high(self)), 2
            )  # 利確指値価格

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
