import pandas as pd
import matplotlib.pyplot as plt

# CSV読み込み
df = pd.read_csv("btc.csv")
df["日付け"] = pd.to_datetime(df["日付け"])
df.set_index("日付け", inplace=True)
for col in ["終値", "高値", "安値"]:
    df[col] = df[col].str.replace(",", "").astype(float)

initial_cash = 10000
lookback = 30
methods = ["mean", "median", "median_avg"]
ma_periods = [10, 15, 20, 25, 30]
colors = {"mean": "orange", "median": "purple", "median_avg": "green"}

def calc_thresholds(buy_returns, sell_returns, method="median_avg"):
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

        # 買い条件（指値がMAより下）
        if cash > 0 and df["安値"].iloc[i] <= target_buy and target_buy < df["MA"].iloc[i]:
            btc = cash / target_buy
            cash = 0
            buy_dates.append(df.index[i])
            buy_prices.append(target_buy)

        # 売り条件（指値がMAより上）
        if btc > 0 and df["高値"].iloc[i] >= target_sell and target_sell > df["MA"].iloc[i]:
            cash = btc * target_sell
            btc = 0
            sell_dates.append(df.index[i])
            sell_prices.append(target_sell)

        records.append({
            "Date": df.index[i],
            "Close": df["終値"].iloc[i],
            "MA": df["MA"].iloc[i],
            "Buy_Target": target_buy,
            "Sell_Target": target_sell,
            "Buy_Executed": cash==0 and btc>0,
            "Sell_Executed": cash>0 and btc==0,
            "Cash": cash,
            "BTC": btc,
            "Portfolio_Value": cash + btc * df["終値"].iloc[i]
        })

    final_value = cash + btc * df["終値"].iloc[-1]
    profit_percent = (final_value - initial_cash) / initial_cash * 100
    return pd.DataFrame(records).set_index("Date"), buy_dates, buy_prices, sell_dates, sell_prices, final_value, profit_percent

# 最適化と結果比較
results_opt = {}

plt.figure(figsize=(16,8))
plt.plot(df.index, df["終値"], label="Close", color="black")

for ma in ma_periods:
    df["MA"] = df["終値"].rolling(ma).mean()
    plt.plot(df.index, df["MA"], alpha=0.3, label=f"MA{ma}")  # すべてのMAラインを薄く描画
    for method in methods:
        backtest_df, buy_dates, buy_prices, sell_dates, sell_prices, final_value, profit_percent = backtest(df, method=method)
        results_opt[(ma, method)] = profit_percent
        plt.scatter(buy_dates, buy_prices, marker="^", color=colors[method], s=40, alpha=0.5)
        plt.scatter(sell_dates, sell_prices, marker="v", color=colors[method], s=40, alpha=0.5)

plt.title("BTC Backtest: MA Period Optimization & Buy/Sell Points")
plt.xlabel("Date")
plt.ylabel("Price (USDT)")
plt.legend()
plt.show()

# 結果表示
for (ma, method), profit in results_opt.items():
    print(f"MA{ma}, {method}: 利益率 {profit:.2f}%")

best_combo = max(results_opt, key=lambda x: results_opt[x])
print(f"\n最適: MA{best_combo[0]}, {best_combo[1]} 利益率: {results_opt[best_combo]:.2f}%")
