import pandas as pd
from itertools import combinations

# 15分足のデータを読み込み (datetime列: OpenTime, 終値: Close)
df = pd.read_excel("15min_1year.xlsx")
df["OpenTime"] = pd.to_datetime(df["OpenTime"])

# 日本時間に変換済みならばそのまま、なければ変換すること
# df["OpenTime"] = df["OpenTime"].dt.tz_convert('Asia/Tokyo')

# 日付だけ抽出
df["Date"] = df["OpenTime"].dt.date
# 時間だけ抽出（HH:MM:SS）
df["Time"] = df["OpenTime"].dt.time

# 1日あたりのユニークな時間を取得
times = sorted(df["Time"].unique())

# 利益を記録する辞書
profit_dict = {}

# 購入時間 < 売却時間の全組み合わせ
for buy_time, sell_time in combinations(times, 2):
    daily_profits = []
    for date, group in df.groupby("Date"):
        # その日の購入時間の終値
        buy_price = group[group["Time"] == buy_time]["Close"]
        # その日の売却時間の終値
        sell_price = group[group["Time"] == sell_time]["Close"]

        if not buy_price.empty and not sell_price.empty:
            profit = sell_price.values[0] - buy_price.values[0]
            daily_profits.append(profit)

    # 1年分の日利益合計
    total_profit = sum(daily_profits)
    profit_dict[(buy_time, sell_time)] = total_profit

# 最も利益が大きい組み合わせ
best_pair = max(profit_dict, key=profit_dict.get)
print(f"最も利益が大きい購入時間と売却時間の組み合わせ: {best_pair} 利益: {profit_dict[best_pair]:.2f}")
