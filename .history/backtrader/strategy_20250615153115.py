import backtrader as bt
import pandas as pd
from config import strategy_params
import utils  # ユーティリティ関数をインポート
import backtrader as bt


class BuyOnlyStrategy(bt.Strategy):
    params = strategy_params  # 設定をパラメータとして受け取る

    def __init__(self):
        self.starting_cash = None  # 初期資産額を保存する変数
        self.entry_value = None  # エントリー時の資産額を保存する変数

    def start(self):
        self.starting_cash = self.p.initial_cash  # 初期資産額を保存

    def next(self):  # 1日ごとの処理

        price, equity, max_position_value, _ = utils.calculate_leverage_info(
            self
        )  # レバレッジ情報を計算

        # 強制ロスカット判定
        if utils.check_force_liquidation(self, equity):
            return

        idx = len(self) - 1  # 現在のインデックス
        data_len = len(self.data)  # データの長さ

        if idx < 31 or idx > data_len - 1:  # 前後30日を除外
            return  # 前後30日を除外（1日ズレるので31必要）

        avg_rate = utils.get_change_rates_low(self)  # 平均変化率計算
        today = self.data.datetime.date(0)  # 今日の日付取得

        # 買い注文実行
        utils.execute_buy_order(
            self, price, avg_rate, max_position_value, equity, today
        )  # 注文実行

        # 利確ロジック
        if self.position:
            utils.execute_sell_order(self, price, max_position_value)

    def notify_order(self, order):  # 注文の状態を通知するメソッド
        if order.status in [order.Completed]:  # 注文が完了した場合
            print(
                f"注文約定: {order.getordername()} {order.executed.price} {order.executed.size}"
            )
        elif order.status in [
            order.Canceled,
            order.Margin,
            order.Rejected,
        ]:  # 注文がキャンセル、マージン不足、拒否された場合
            print(f"注文キャンセル・拒否: {order.getordername()}")

    def stop(self):
        final_value = self.broker.getvalue()
        final_profit = final_value - self.starting_cash
        with open("result.txt", "w") as f:
            f.write(f"最終資産額: {final_value}\n")
            f.write(f"最終利益: {final_profit}\n")
        print("結果をresult.txtに保存しました")
