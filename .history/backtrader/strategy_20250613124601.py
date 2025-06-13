import backtrader as bt
from config import strategy_params
from calc_change_rate import calculate_avg_change_rate  # ここで外部関数をインポート
import pandas as pd


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
        idx = len(self) - 1  # 現在のバーのインデックス
        data_len = len(self.data)  # 全データ長

        # 前後30日は処理しない（範囲外ならスキップ）
        if idx < 30 or idx >= data_len - 30:
            return

        # 過去30日分の過去データをリストで取る例
        closes = [
            self.data.close[-i] for i in range(29, -1, -1)
        ]  # 過去29日から今日まで
        lows = [self.data.low[-i] for i in range(29, -1, -1)]

        # 日付のリストもほしい場合
        dates = [self.data.datetime.date(-i) for i in range(29, -1, -1)]

        # DataFrameなどにまとめたいならpandas利用（任意）
        import pandas as pd

        df = pd.DataFrame(
            {
                "datetime": dates,
                "close": closes,
                "low": lows,
            }
        )

        # ここでcalc_change_rate関数を呼ぶなどの処理を書く
        avg_rate = calculate_avg_change_rate(df, days=30)
        print(f"{dates[-1]} 過去30日変化率平均: {avg_rate:.4%}")

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

    def stop(self):
        final_value = self.broker.getvalue()
        final_profit = final_value - self.starting_cash
        with open("result.txt", "w") as f:
            f.write(f"最終資産額: {final_value}\n")
            f.write(f"最終利益: {final_profit}\n")
        print("結果をresult.txtに保存しました")
