import pandas as pd
import matplotlib.pyplot as plt

# Excel読み込み
df = pd.read_excel("BTCUSDT_30m_1year.xlsx")

# OpenTimeはUTC datetimeなので、日本時間(JST)に変換
df["OpenTime"] = pd.to_datetime(df["OpenTime"], utc=True).dt.tz_convert("Asia/Tokyo")

# 日付と時間・分を分ける
df["Date"] = df["OpenTime"].dt.date
df["Hour"] = df["OpenTime"].dt.hour
df["Minute"] = df["OpenTime"].dt.minute

# 30分足なので「時:分」で時間帯のグループを作成（例："14:30"）
df["TimeSlot"] = df["OpenTime"].dt.strftime("%H:%M")

# 1日ごとの高値の行を取得
daily_highs = df.loc[df.groupby("Date")["High"].idxmax()]

# 高値をつけた時間帯の分布（TimeSlotごとにカウント）
time_counts = daily_highs["TimeSlot"].value_counts().sort_index()

# 割合に変換
time_percentage = (time_counts / time_counts.sum() * 100).round(2)

# 結果表示
print("=== 高値をつけやすい30分足時間帯（過去1年・JST） ===")
print(time_percentage)

# グラフ化
plt.figure(figsize=(12,6))
plt.bar(time_percentage.index, time_percentage.values)
plt.xlabel("Time of Day (JST)")
plt.ylabel("Percentage (%)")
plt.title("30-Minute Time Slot with Daily High Price Frequency (JST)")
plt.xticks(rotation=90)  # ラベル縦表示で見やすく
plt.grid(axis="y", linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()
