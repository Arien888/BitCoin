import pandas as pd
import matplotlib.pyplot as plt

# CSV読み込み
df = pd.read_csv("btc_1y.csv")

# 日付列をdatetime型に変換してインデックスに設定
df["日付け"] = pd.to_datetime(df["日付け"])
df.set_index("日付け", inplace=True)

# 終値・高値・安値のカンマを削除してfloatに変換
for col in ["終値", "高値", "安値"]:
    df[col] = df[col].str.replace(",", "").astype(float)

# --- シンプル戦略：短期MAと長期MAのクロス ---
short_window = 10
long_window = 20
df["MA_short"] = df["終値"].rolling(short_window).mean()
df["MA_long"] = df["終値"].rolling(long_window).mean()

# シグナル作成（売買指値で使用するため1で統一）
df["signal"] = 1  # 常に購入チャンスありとして指値で売買を判断

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
        # 過去30日間の売り変化率（前日終値→翌日高値）
        sell_returns = (df["高値"].iloc[i-lookback+1:i+1].values / df["終値"].iloc[i-lookback:i].values - 1)
        sell_threshold = pd.Series(sell_returns).median()
        # 過去30日間の買い変化率（前日終値→翌日安値）
        buy_returns = (df["安値"].iloc[i-lookback+1:i+1].values / df["終値"].iloc[i-lookback:i].values - 1)
        buy_threshold = pd.Series(buy_returns).median()
    else:
        sell_threshold = 0.01
        buy_threshold = -0.01

    # 買い指値判定
    if cash > 0:
        target_buy = df["終値"].iloc[i-1] * (1 + buy_threshold)
        if df["安値"].iloc[i] <= target_buy:
            btc = cash / target_buy
            cash = 0
            buy_dates.append(df.index[i])
            buy_prices.append(target_buy)

    # 売り指値判定
    if btc > 0:
        target_sell = df["終値"].iloc[i-1] * (1 + sell_threshold)
        if df["高値"].iloc[i] >= target_sell:
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
plt.scatter(buy_dates, buy_prices, marker="^", color="green", s=100, label="Buy")
plt.scatter(sell_dates, sell_prices, marker="v", color="red", s=100, label="Sell")
plt.title("BTC 1-Year Backtest with Median Buy/Sell Targets")
plt.xlabel("Date")
plt.ylabel("Price (USDT)")
plt.legend()
plt.show()
