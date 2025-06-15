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


def check_force_liquidation(self, equity):  # 強制ロスカット判定関数
    if self.position and equity < self.entry_value * self.p.stop_loss_ratio:
        print(
            f"{self.data.datetime.date(0)} 強制ロスカット: 現在の資産額 {equity} < エントリー時の資産額 {self.entry_value * self.p.stop_loss_ratio}"
        )
        self.close()
        self.entry_value = None
        return True
    return False
