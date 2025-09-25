import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- 単一バックテスト ---
def backtest_single_custom(df, ma_period=20, lookback=14, initial_cash=10000, mode="median_avg"):
    """
    mode: 'median', 'mean', 'median_avg' のいずれか
    """
    df = df.copy()
    df["MA"] = df["終値"].rolling(ma_period).mean()
    cash = initial_cash
    btc = 0
    records = []

    for i in range(1, len(df)):
        if i >= lookback:
            # --- 過去リターン ---
            buy_returns = df["安値"].iloc[i - lookback + 1:i + 1].values / df["終値"].iloc[i - lookback:i].values - 1
            sell_returns = df["高値"].iloc[i - lookback + 1:i + 1].values / df["終値"].iloc[i - lookback:i].values - 1

            # --- 閾値計算（モード別） ---
            if mode == "median":
                buy_thresh = np.median(buy_returns)
                sell_thresh = np.median(sell_returns)
            elif mode == "mean":
                buy_thresh = buy_returns.mean()
                sell_thresh = sell_returns.mean()
            elif mode == "median_avg":
                buy_thresh = buy_returns[buy_returns <= np.median(buy_returns)].mean()
                sell_thresh = sell_returns[sell_returns >= np.median(sell_returns)].mean()
            else:
                raise ValueError("mode must be 'median', 'mean', or 'median_avg'")

            # --- 指値計算（単純に直近終値ベース） ---
            target_buy = df["終値"].iloc[i - 1] * (1 + buy_thresh)
            target_sell = df["終値"].iloc[i - 1] * (1 + sell_thresh)

        else:
            target_buy = df["終値"].iloc[i - 1]
            target_sell = df["終値"].iloc[i - 1]

        # --- 売買ルール ---
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

    # --- 最終結果 ---
    final_value = cash + btc * df["終値"].iloc[-1]
    profit_percent = (final_value - initial_cash) / initial_cash * 100
    return pd.DataFrame(records).set_index("Date"), final_value, profit_percent


# ==============================
# main
# ==============================
if __name__ == "__main__":
    symbol = "pepe"  # ← ここを固定
    file = f"{symbol}.csv"

    # --- データ読み込み ---
    df = pd.read_csv(file)
    df["日付け"] = pd.to_datetime(df["日付け"])
    df.set_index("日付け", inplace=True)

    # 過去1年間に絞り込み
    one_year_ago = datetime.today() - timedelta(days=365)
    df = df[df.index >= one_year_ago]

    # 数値変換
    for col in ["終値", "高値", "安値"]:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors="coerce")

    # --- 3種類の戦略を検証 ---
    ma_period = 20
    lookback = 14
    modes = ["median", "mean", "median_avg"]

    for mode in modes:
        records_df, final_value, profit_percent = backtest_single_custom(df, ma_period, lookback, 10000, mode=mode)
        records_df.to_csv(f"{symbol}_backtest_{mode}.csv")
        print(f"[{mode}] 最終資産: {final_value:.2f}, 利益率: {profit_percent:.2f}%")
        print(f"個別結果: '{symbol}_backtest_{mode}.csv'")
