import pandas as pd
from itertools import product
from datetime import timedelta

# データ読み込み
df = pd.read_excel("BTCUSDT_15m_1year.xlsx")
df["OpenTime"] = pd.to_datetime(df["OpenTime"])
df["Date"] = df["OpenTime"].dt.date
df["Time"] = df["OpenTime"].dt.time

# ユニークな時間（買い時間・売り時間候補）
times = sorted(df["Time"].unique())
total_days = df["Date"].nunique()

BUY_DISCOUNT = 0.9803  # 98.03%
HOURS_LIMIT = 24       # 24時間以内

results = []

# 買い時間 × 売り時間 の全組み合わせ
for buy_time, sell_time in product(times, times):

    total_profit = 0
    trade_count = 0

    for date, day_data in df.groupby("Date"):
        buy_row = day_data.loc[day_data["Time"] == buy_time]
        if buy_row.empty:
            continue

        buy_target_price = buy_row["Close"].values[0] * BUY_DISCOUNT
        start_time = buy_row["OpenTime"].values[0]
        end_time = pd.Timestamp(start_time) + timedelta(hours=HOURS_LIMIT)

        # 24時間ウィンドウ
        window_data = df[(df["OpenTime"] > start_time) & (df["OpenTime"] <= end_time)]

        # 24時間以内に指値成立
        if not window_data.empty and window_data["Low"].min() <= buy_target_price:
            # 売却時間がウィンドウ内に存在するか
            sell_row = window_data.loc[window_data["Time"] == sell_time]
            if not sell_row.empty:
                sell_price = sell_row.iloc[0]["Close"]
                total_profit += (sell_price - buy_target_price)
                trade_count += 1

    # 平均利益と成立率の計算
    avg_profit = total_profit / trade_count if trade_count > 0 else 0
    win_rate = (trade_count / total_days) * 100

    results.append((buy_time, sell_time, total_profit, trade_count, avg_profit, win_rate))

# DataFrame化
results_df = pd.DataFrame(results, columns=[
    "BuyTime", "SellTime", "TotalProfit", "Trades", "AvgProfit", "WinRate(%)"
])

# 利益高い順
results_df = results_df.sort_values(by="TotalProfit", ascending=False).reset_index(drop=True)

# トップ10
print("=== 利益が高い順 トップ10 ===")
print(results_df.head(10))

# Excel保存
results_df.to_excel("buy_sell_limit_order_within_24h_stats.xlsx", index=False)
print("✅ 結果を buy_sell_limit_order_within_24h_stats.xlsx に保存しました")
