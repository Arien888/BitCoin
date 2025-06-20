import backtrader as bt


def get_change_rates_low(self):
    """前日終値 → 翌日安値の変化率を30日分計算する関数"""

    # 前日終値 → 翌日安値の変化率を30日分計算
    change_rates = []  # 前日終値から翌日安値の変化率を格納するリスト
    for i in range(30):  # 30日分のループ
        close_today = self.data.close[-i - 1]  # 今日の終値
        low_next = self.data.low[-i]  # 翌日の安値
        change = (low_next - close_today) / close_today  # 変化率計算
        change_rates.append(change)  # リストに追加

    avg_rate = sum(change_rates) / len(change_rates)  # 平均変化率計算
    return avg_rate


def get_change_rates_high(self):
    """前日終値 → 翌日高値の変化率を30日分計算する関数"""

    # 前日終値 → 翌日高値の変化率を30日分計算
    change_rates = []  # 前日終値から翌日高値の変化率を格納するリスト
    for i in range(30):  # 30日分のループ
        close_today = self.data.close[-i - 1]  # 今日の終値
        high_next = self.data.high[-i]  # 翌日の高値
        change = (high_next - close_today) / close_today  # 変化率計算
        change_rates.append(change)  # リストに追加

    avg_rate = sum(change_rates) / len(change_rates)  # 平均変化率計算
    return avg_rate


def check_force_liquidation(strategy, equity):  # 強制ロスカット判定関数
    if (
        strategy.position and equity < strategy.entry_value * strategy.p.stop_loss_ratio
    ):  # ストップロスの割合を超えた場合
        print(
            f"{strategy.data.datetime.date(0)} 強制ロスカット: 現在の資産額 {equity} < エントリー時の資産額 {strategy.entry_value * strategy.p.stop_loss_ratio}"
        )
        strategy.close()
        strategy.entry_value = None
        return True
    return False


def execute_sell_order(
    strategy, price, max_position_value
):  # 利確ロジックを実行する関数
    today = strategy.data.datetime.date(0)
    position_size = strategy.position.size
    sell_amount = max_position_value * strategy.p.sell_ratio
    sell_size = round(min(sell_amount / price, position_size), 5)

    limit_price_sell = round(price * (1 - get_change_rates_high(strategy)), 2)

    if sell_size > 0:
        strategy.sell(size=sell_size, price=limit_price_sell, exectype=bt.Order.Limit)
        print(f"{today} 指値売り {sell_size} BTC @ {limit_price_sell}")


def execute_buy_order(
    strategy, price, avg_rate, max_position_value, equity, today
):  # 注文実行関数
    limit_price = round(price * (1 + avg_rate), 2)
    buy_amount = max_position_value * strategy.p.buy_ratio
    buy_size = round(buy_amount / limit_price, 5)

    if buy_size > 0:
        strategy.buy(size=buy_size, price=limit_price, exectype=bt.Order.Limit)

        # 既存ポジションがあればentry_valueを加重平均で更新（ナンピン対応）
        if strategy.position:  # 現在ポジションがある場合
            current_size = strategy.position.size  # 現在のポジションサイズ
            current_entry_value = (
                strategy.entry_value if strategy.entry_value is not None else equity
            )  # 現在のエントリー時の資産額
            total_size = current_size + buy_size  # 合計サイズ
            weighted_entry_value = (
                (current_entry_value * current_size) + (equity * buy_size)
            ) / total_size  # 加重平均でエントリー時の資産額を更新
            strategy.entry_value = (
                weighted_entry_value  # 更新されたエントリー時の資産額を保存
            )
        else:
            strategy.entry_value = equity  # ポジションがない場合は現在の資産額を保存

        print(
            f"{today} 平均変化率: {avg_rate:.4%} → 指値買い {buy_size} BTC @ {limit_price}"
        )
    print(equity)


def calculate_leverage_info(strategy):  # レバレッジ情報を計算する関数
    price = strategy.data.close[0]
    equity = strategy.broker.getvalue()
    max_position_value = equity * strategy.p.leverage
    max_size = max_position_value / price
    return price, equity, max_position_value, max_size
