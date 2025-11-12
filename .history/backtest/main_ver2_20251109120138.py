import pandas as pd
import numpy as np

# CSV読み込み
df = pd.read_csv("btc.csv")
df["日付け"] = pd.to_datetime(df["日付け"])
df.set_index("日付け", inplace=True)

# 数値変換
for col in ["終値", "始値", "高値", "安値"]:
    df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors="coerce")

# 初期資金
cash = 10000
asset = 0
trade_count = 0
profits = []

for i in range(1, len(df)):
    price = df["終値"].iloc[i]
    prev_price = df["終値"].iloc[i-1]

    # 買い
    if price < prev_price and cash > 0:
        asset = cash / price
        cash = 0
        trade_count += 1
        buy_price = price

    # 売り
    elif price > prev_price and asset > 0:
        cash = asset * price
        asset = 0
        trade_count += 1
        sell_price = price
        profits.append((sell_price - buy_price) / buy_price * 100)

# 最終資産・利益
final_asset = cash + asset * df["終値"].iloc[-1]
avg_profit = np.mean(profits) if profits else 0

# 結果表示
print(f"最終資産: {final_asset:.2f}")
print(f"トレード回数: {trade_count}")
print(f"平均利益(%): {avg_profit:.2f}")
