import pandas as pd

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

# シグナル作成（買いのみ使用）
df["signal"] = 0
df.loc[df["MA_short"] > df["MA_long"], "signal"] = 1

# --- バックテスト計算 ---
initial_cash = 10000
cash = initial_cash
btc = 0

# 売り指値を設定するための過去30日間の変化率中央値を計算
lookback = 30
for i in range(1, len(df)):
    # 前日終値から当日高値の変化率
    if i >= lookback:
        past_returns = (df["高値"].iloc[i-lookback+1:i+1].values / df["終値"].iloc[i-lookback:i].values - 1)
        sell_threshold = pd.Series(past_returns).median()
    else:
        sell_threshold = 0.01  # データ不足時は1%に設定

    # 買い
    if df["signal"].iloc[i] == 1 and cash > 0:
        btc = cash / df["終値"].iloc[i]
        cash = 0

    # 売り指値判定
    if btc > 0:
        target_price = df["終値"].iloc[i] * (1 + sell_threshold)
        # 当日の高値が指値に到達したら売る
        if df["高値"].iloc[i] >= target_price:
            cash = btc * target_price
            btc = 0

# 最終ポートフォリオ価値
final_value = cash + btc * df["終値"].iloc[-1]
print("最終ポートフォリオ価値:", final_value)
print("利回り:", (final_value - initial_cash) / initial_cash * 100, "%")
