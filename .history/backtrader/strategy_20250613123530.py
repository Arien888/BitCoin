import backtrader as bt
from config import strategy_params
from calc_change_rate import calculate_avg_change_rate  # ここで外部関数をインポート


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
        idx = len(self) - 1
        if idx < 30:
            return

        data_slice = self.datas[0]
        dates = [data_slice.datetime.date(i) for i in range(idx - 29, idx + 1)]
        closes = [data_slice.close[i] for i in range(idx - 29, idx + 1)]
        lows = [data_slice.low[i] for i in range(idx - 29, idx + 1)]

        df_30 = pd.DataFrame(
            {
                "datetime": pd.to_datetime(dates),
                "close": closes,
                "low": lows,
            }
        )

        avg_change_rate = calculate_avg_change_rate(df_30)

        # 以下、avg_change_rateを使って戦略ロジックを実装
        # 例：
        today = self.data.datetime.date(0)
        print(f"{today} 過去30日変化率平均: {avg_change_rate:.4%}")

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
