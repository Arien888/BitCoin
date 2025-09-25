import pandas as pd
import matplotlib.pyplot as plt

# CSV読み込み
df = pd.read_csv("btc_1y.csv")

# 日付列をdatetime型に変換してインデックスに設定
df["日付け"] = pd.to_datetime(df["日付け"])
df.set_index("日付け", inplace=True)

# 終値・高値のカンマを削除してfloatに変換
for col in ["終値", "高値"]:
    df[col] = df[col].str.replace(",", "").astype(float)

# --- シンプル戦略：短期MAと長期MAのクロス ---
short_window = 10
long_window = 20
df["MA_short"] = df["終値"].rolling(short_window).mean()
df["MA_long"] = df["終値"].rolling(long_window).mean()

# シグナル作成（買いのみ）
df["signal"] = 0
df.loc[df["MA_short"] > df["MA_long"], "signal"] = 1

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
    # 過去30日間の変化率中央値
    if i >= lookback:
        past_returns = (df["高値"].iloc[i-lookback+1:i+1].values / df["終値"].iloc[i-lookback:i].values - 1)
        sell_threshold = pd.Series(past_returns).median()
    else:
        sell_threshold = 0.01  # 初期値

    # 買い
    if df["signal"].iloc[i] == 1 and cash > 0:
        btc = cash / df["終値"].iloc[i]
        cash = 0
        buy_dates.append(df.index[i])
        buy_prices.append(df["終値"].iloc[i])

    # 売り指値判定
    if btc > 0:
        target_price = df["終値"].iloc[i] * (1 + sell_threshold)
        if df["高値"].iloc[i] >= target_price:
            cash = btc * target_price
            btc = 0
            sell_dates.append(df.index[i])
            sell_prices.append(target_price)

# 最終ポートフォリオ価値
final_value = cash + btc * df["終値"].iloc[-1]
print("最終ポートフォリオ価値:", final_value)
print("利回り:", (final_value - initial_cash) / initial_cash * 100, "%")

# --- グラフ描画 ---
plt.figure(figsize=(14,6))
plt.plot(df.index, df["終値"], label="Close", color="black")
plt.plot(df.index, df["MA_short"], label="MA_short", color="blue", alpha=0.6)
plt.plot(df.index, df["MA_long"], label="MA_long", color="orange", alpha=0.6)
plt.scatter(buy_dates, buy_prices, marker="^", color="green", s=100, label="Buy")
plt.scatter(sell_dates, sell_prices, marker="v", color="red", s=100, label="Sell")
plt.title("BTC 1-Year Backtest")
plt.xlabel("Date")
plt.ylabel("Price (USDT)")
plt.legend()
plt.show()
