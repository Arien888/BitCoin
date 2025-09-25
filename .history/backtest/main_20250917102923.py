import pandas as pd

# CSV読み込み
df = pd.read_csv("btc_1y.csv")

# 日付列をdatetime型に変換してインデックスに設定
df["日付け"] = pd.to_datetime(df["日付け"])
df.set_index("日付け", inplace=True)

# 終値のカンマを削除してfloatに変換
df["終値"] = df["終値"].str.replace(",", "").astype(float)


# --- シンプル戦略：短期MAと長期MAのクロス ---
short_window = 10
long_window = 20

df["MA_short"] = df["終値"].rolling(short_window).mean()
df["MA_long"] = df["終値"].rolling(long_window).mean()

# シグナル作成
df["signal"] = 0
df.loc[df["MA_short"] > df["MA_long"], "signal"] = 1  # 買い
df.loc[df["MA_short"] < df["MA_long"], "signal"] = -1  # 売り

# --- バックテスト計算 ---
initial_cash = 10000
cash = initial_cash
btc = 0

for i in range(1, len(df)):
    if df["signal"].iloc[i] == 1 and cash > 0:  # 買い
        btc = cash / df["終値"].iloc[i]
        cash = 0
    elif df["signal"].iloc[i] == -1 and btc > 0:  # 売り
        cash = btc * df["終値"].iloc[i]
        btc = 0

        # データ確認
    print(df[["終値", "MA_short", "MA_long", "signal"]].tail(10))


# 最終ポートフォリオ価値
final_value = cash + btc * df["終値"].iloc[-1]
print("最終ポートフォリオ価値:", final_value)
print("利回り:", (final_value - initial_cash) / initial_cash * 100, "%")
