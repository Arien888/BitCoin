import pandas as pd
import matplotlib.pyplot as plt

# CSV読み込み
df = pd.read_csv("btc.csv")
df["日付け"] = pd.to_datetime(df["日付け"])
df.set_index("日付け", inplace=True)
for col in ["終値", "高値", "安値"]:
    df[col] = df[col].str.replace(",", "").astype(float)
df["MA15"] = df["終値"].rolling(15).mean()

initial_cash = 10000
lookback = 30

def calc_thresholds(buy_returns, sell_returns, method="median_avg"):
    """指値計算ルール
    method: 'mean', 'median', 'median_avg'
    """
    if method == "mean":
        return buy_returns.mean(), sell_returns.mean()
    elif method == "median":
        return buy_returns.median(), sell_returns.median()
    elif method == "median_avg":
        buy_thresh = buy_returns[buy_returns <= buy_returns.median()].mean()
        sell_thresh = sell_returns[sell_returns >= sell_returns.median()].mean()
        return buy_thresh, sell_thresh

def backtest(df, method="median_avg"):
    cash = initial_cash
    btc = 0
    records = []
    buy_dates, buy_prices, sell_dates, sell_prices = [], [], [], []

    for i in range(1, len(df)):
        if i >= lookback:
            buy_returns = (df["安値"].iloc[i-lookback+1:i+1].values / df["終値"].iloc[i-lookback:i].values - 1)
            sell_returns = (df["高値"].iloc[i-lookback+1:i+1].values / df["終値"].iloc[i-lookback:i].values - 1)
            buy_threshold, sell_threshold = calc_thresholds(pd.Series(buy_returns), pd.Series(sell_returns), method)
        else:
            buy_threshold, sell_threshold = -0.01, 0.01

        target_buy = df["終値"].iloc[i-1] * (1 + buy_threshold)
        target_sell = df["終値"].iloc[i-1] * (1 + sell_threshold)

        buy_exec = False
        sell_exec = False

        if cash > 0 and df["安値"].iloc[i] <= target_buy and target_buy < df["MA15"].iloc[i]:
            btc = cash / target_buy
            cash = 0
            buy_exec = True
            buy_dates.append(df.index[i])
            buy_prices.append(target_buy)

        if btc > 0 and df["高値"].iloc[i] >= target_sell and target_sell > df["MA15"].iloc[i]:
            cash = btc * target_sell
            btc = 0
            sell_exec = True
            sell_dates.append(df.index[i])
            sell_prices.append(target_sell)

        records.append({
            "Date": df.index[i],
            "Close": df["終値"].iloc[i],
            "MA15": df["MA15"].iloc[i],
            "Buy_Target": target_buy,
            "Sell_Target": target_sell,
            "Buy_Executed": buy_exec,
            "Sell_Executed": sell_exec,
            "Cash": cash,
            "BTC": btc,
            "Portfolio_Value": cash + btc * df["終値"].iloc[i]
        })

    return pd.DataFrame(records).set_index("Date"), final_value

# 3パターンでバックテスト
methods = ["mean", "median", "median_avg"]
results = {}
for m in methods:
    backtest_df, final_value = backtest(df, method=m)
    results[m] = final_value
    backtest_df.to_csv(f"btc_backtest_{m}.csv")
    print(f"{m} 最終ポートフォリオ価値:", final_value)

# グラフ描画例（単純化）
plt.figure(figsize=(14,6))
plt.plot(df.index, df["終値"], label="Close", color="black")
plt.plot(df.index, df["MA15"], label="MA15", color="blue", alpha=0.5)
plt.title("BTC Backtest Comparison")
plt.legend()
plt.show()
