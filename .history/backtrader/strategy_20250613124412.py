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

    def stop(self):
        final_value = self.broker.getvalue()
        final_profit = final_value - self.starting_cash
        with open("result.txt", "w") as f:
            f.write(f"最終資産額: {final_value}\n")
            f.write(f"最終利益: {final_profit}\n")
        print("結果をresult.txtに保存しました")
