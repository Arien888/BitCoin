import pandas as pd
import matplotlib.pyplot as plt

# Excel読み込み
df = pd.read_excel("BTCUSDT_30m_1year.xlsx")

# OpenTimeはUTC datetimeなので、日本時間(JST)に変換
df["OpenTime"] = pd.to_datetime(df["OpenTime"], utc=True).dt.tz_convert("Asia/Tokyo")

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
print("=== 高値をつけやすい時間帯（過去1年・JST） ===")
print(hour_percentage)

# グラフ化
plt.bar(hour_percentage.index, hour_percentage.values)
plt.xlabel("Hour of Day (JST)")
plt.ylabel("Percentage (%)")
plt.title("Hour of Day with Daily High Price Frequency (JST)")
plt.xticks(range(0, 24))
plt.grid(axis="y", linestyle="--", alpha=0.5)
plt.show()
