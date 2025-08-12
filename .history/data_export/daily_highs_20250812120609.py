import pandas as pd

# Excel読み込み
df = pd.read_excel("BTCUSDT_1year.xlsx")

# 時刻をdatetime型に変換（すでにdatetimeなら不要）
df["OpenTime"] = pd.to_datetime(df["OpenTime"])

# 日付と時間を分ける
df["Date"] = df["OpenTime"].dt.date
df["Hour"] = df["OpenTime"].dt.hour

# 1日ごとの高値の行を取得
daily_highs = df.loc[df.groupby("Date")["High"].idxmax()]

# 高値をつけた時間帯の分布
hour_counts = daily_highs["Hour"].value_counts().sort_index()

# 割合に変換
hour_percentage = (hour_counts / hour_counts.sum() * 100).round(2)

# 結果表示
print("=== 高値をつけやすい時間帯（過去1年） ===")
print(hour_percentage)

# グラフ化
import matplotlib.pyplot as plt
plt.bar(hour_percentage.index, hour_percentage.values)
plt.xlabel("Hour of Day")
plt.ylabel("Percentage (%)")
plt.title("Hour of Day with Daily High Price Frequency")
plt.xticks(range(0, 24))
plt.grid(axis="y", linestyle="--", alpha=0.5)
plt.show()
