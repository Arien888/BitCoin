import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- 単一バックテスト ---
def backtest_single_custom(df, ma_period=20, lookback=14, initial_cash=10000):
    df = df.copy()
    df["MA"] = df["終値"].rolling(ma_period).mean()
    cash = initial_cash
    btc = 0
    records = []

    for i in range(1, len(df)):
        if i >= lookback:
            # 過去リターン
            buy_returns = df["安値"].iloc[i-lookback+1:i+1].values / df["終値"].iloc[i-lookback:i].values - 1
            sell_returns = df["高値"].iloc[i-lookback+1:i+1].values / df["終値"].iloc[i-lookback:i].values - 1

            # 閾値計算
            buy_thresh_ma = buy_returns[buy_returns <= np.median(buy_returns)].mean()
            buy_thresh_now = buy_returns.mean()
            sell_thresh_ma = sell_returns[sell_returns >= np.median(sell_returns)].mean()
            sell_thresh_now = sell_returns.mean()

            # 購入指値（MAベース or 現在価格ベース平均で低い方）
            target_buy_ma = df["MA"].iloc[i] * (1 + buy_thresh_ma)
            target_buy_now = df["終値"].iloc[i-1] * (1 + buy_thresh_now)
            target_buy = min(target_buy_ma, target_buy_now)

            # 売却指値（MAベース or 現在価格ベース平均で高い方）
            target_sell_ma = df["MA"].iloc[i] * (1 + sell_thresh_ma)
            target_sell_now = df["終値"].iloc[i-1] * (1 + sell_thresh_now)
            target_sell = max(target_sell_ma, target_sell_now)

        else:
            target_buy = df["終値"].iloc[i-1]
            target_sell = df["終値"].iloc[i-1]

        # --- 売買 ---
        if cash > 0 and df["安値"].iloc[i] <= target_buy:
            btc = cash / target_buy
            cash = 0
        if btc > 0 and df["高値"].iloc[i] >= target_sell:
            cash = btc * target_sell
            btc = 0

        # --- 記録 ---
        records.append({
            "Date": df.index[i],
            "Close": df["終値"].iloc[i],
            "MA": df["MA"].iloc[i],
            "Buy_Target": target_buy,
            "Sell_Target": target_sell,
            "Cash": cash,
            "BTC": btc,
            "Portfolio_Value": cash + btc * df["終値"].iloc[i]
        })

    final_value = cash + btc * df["終値"].iloc[-1]
    profit_percent = (final_value - initial_cash) / initial_cash * 100
    return pd.DataFrame(records).set_index("Date"), final_value, profit_percent


# ==============================
# main
# ==============================
if __name__ == "__main__":
    symbol = "pepe"  # ← ここを 'pepe' に固定する
    file = f"{symbol}.csv"

    df = pd.read_csv(file)
    df["日付け"] = pd.to_datetime(df["日付け"])
    df.set_index("日付け", inplace=True)

    one_year_ago = datetime.today() - timedelta(days=365)
    df = df[df.index >= one_year_ago]

    for col in ["終値","高値","安値"]:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors="coerce")

    # --- バックテスト実行 ---
    ma_period = 20
    lookback = 14
    records_df, final_value, profit_percent = backtest_single_custom(df, ma_period, lookback)

    # --- 結果保存 ---
    records_df.to_csv(f"{symbol}_backtest_1year.csv")
    print(f"最終資産: {final_value:.2f}, 利益率: {profit_percent:.2f}%")
    print(f"個別結果: '{symbol}_backtest_1year.csv'")
