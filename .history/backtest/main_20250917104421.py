import pandas as pd
import matplotlib.pyplot as plt

# CSV読み込み
df = pd.read_csv("btc.csv")

# 日付列をdatetime型に変換してインデックスに設定
df["日付け"] = pd.to_datetime(df["日付け"])
df.set_index("日付け", inplace=True)

# 終値・高値・安値のカンマを削除してfloatに変換
for col in ["終値", "高値", "安値"]:
    df[col] = df[col].str.replace(",", "").astype(float)

# 15日MA（フィルター用）
ma_filter = 15
df["MA15"] = df["終値"].rolling(ma_filter).mean()

# --- バックテスト計算 ---
initial_cash = 10000
cash = initial_cash
btc = 0

lookback = 30
buy_dates = []
buy_prices = []
sell_dates = []
sell_prices = []

for i in range(1, len(df)):
    if i >= lookback:
        # 過去30日間の変化率中央値
        sell_returns = (df["高値"].iloc[i-lookback+1:i+1].values / df["終値"].iloc[i-lookback:i].values - 1)
        sell_threshold = pd.Series(sell_returns).median()
        buy_returns = (df["安値"].iloc[i-lookback+1:i+1].values / df["終値"].iloc[i-lookback:i].values - 1)
        buy_threshold = pd.Series(buy_returns).median()
    else:
        sell_threshold = 0.01
        buy_threshold = -0.01

    # 買い条件（2つとも満たす）
    target_buy = df["終値"].iloc[i-1] * (1 + buy_threshold)
    if cash > 0 and df["安値"].iloc[i] <= target_buy and df["終値"].iloc[i] <= df["MA15"].iloc[i]:
        btc = cash / target_buy
        cash = 0
        buy_dates.append(df.index[i])
        buy_prices.append(target_buy)

    # 売り条件（2つとも満たす）
    target_sell = df["終値"].iloc[i-1] * (1 + sell_threshold)
    if btc > 0 and df["高値"].iloc[i] >= target_sell and df["終値"].iloc[i] >= df["MA15"].iloc[i]:
        cash = btc * target_sell
        btc = 0
        sell_dates.append(df.index[i])
        sell_prices.append(target_sell)

# 最終ポートフォリオ価値
final_value = cash + btc * df["終値"].iloc[-1]
print("最終ポートフォリオ価値:", final_value)
print("利回り:", (final_value - initial_cash) / initial_cash * 100, "%")

# --- グラフ描画 ---
plt.figure(figsize=(14,6))
plt.plot(df.index, df["終値"], label="Close", color="black")
plt.plot(df.index, df["MA15"], label="MA15", color="blue", alpha=0.5)
plt.scatter(buy_dates, buy_prices, marker="^", color="green", s=100, label="Buy")
plt.scatter(sell_dates, sell_prices, marker="v", color="red", s=100, label="Sell")
plt.title("BTC 1-Year Backtest with Median Buy/Sell & MA15 Filter")
plt.xlabel("Date")
plt.ylabel("Price (USDT)")
plt.legend()
plt.show()
