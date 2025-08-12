import pandas as pd
from itertools import combinations

# 15分足のデータを読み込み
df = pd.read_excel("BTCUSDT_15m_1year.xlsx")
df["OpenTime"] = pd.to_datetime(df["OpenTime"])

# 日付と時間に分割
df["Date"] = df["OpenTime"].dt.date
df["Time"] = df["OpenTime"].dt.time

# 1日あたりのユニークな時間
times = sorted(df["Time"].unique())

# 利益リストを格納
results = []

# 購入時間 < 売却時間の全組み合わせ
for buy_time, sell_time in combinations(times, 2):
    daily_profits = []
    for date, group in df.groupby("Date"):
        buy_price = group.loc[group["Time"] == buy_time, "Close"]
        sell_price = group.loc[group["Time"] == sell_time, "Close"]

        if not buy_price.empty and not sell_price.empty:
            daily_profits.append(sell_price.values[0] - buy_price.values[0])

    total_profit = sum(daily_profits)
    results.append((buy_time, sell_time, total_profit))

# DataFrame化して利益順にソート
results_df = pd.DataFrame(results, columns=["BuyTime", "SellTime", "TotalProfit"])
results_df = results_df.sort_values(by="TotalProfit", ascending=False).reset_index(drop=True)

# 上位10件を表示
print(results_df.head(10))

# 必要ならExcelに保存
results_df.to_excel("buy_sell_profit_ranking.xlsx", index=False)
print("✅ 全組み合わせの結果を buy_sell_profit_ranking.xlsx に保存しました")
