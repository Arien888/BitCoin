import pandas as pd
import numpy as np

# ----------------------------
# 閾値計算関数
# ----------------------------
def compute_threshold(values, base="median", direction="above", agg="mean"):
    arr = np.asarray(values)
    if arr.size == 0:
        return 0.0
    if base == "max":
        return np.max(arr)
    ref = np.median(arr) if base == "median" else arr.mean()
    if direction == "above":
        filtered = arr[arr >= ref]
    else:
        filtered = arr[arr <= ref]
    if filtered.size == 0:
        return ref
    return filtered.mean() if agg == "mean" else np.median(filtered)

def get_thresholds(buy_returns, sell_returns, buy_method_ma, buy_method_prev, sell_method_ma, sell_method_prev):
    def parse_method(m):
        if m in ["median", "mean", "max"]:
            return m, m
        if "_above_" in m:
            base, agg = m.split("_above_")
            return base, agg
        raise ValueError("Unknown method: " + str(m))

    buy_base_ma, buy_agg_ma = parse_method(buy_method_ma)
    buy_base_prev, buy_agg_prev = parse_method(buy_method_prev)
    sell_base_ma, sell_agg_ma = parse_method(sell_method_ma)
    sell_base_prev, sell_agg_prev = parse_method(sell_method_prev)

    if buy_base_ma == "max":
        buy_thresh_ma = np.max(buy_returns)
    else:
        buy_thresh_ma = compute_threshold(buy_returns, base=buy_base_ma, direction="below", agg=buy_agg_ma)

    if sell_base_ma == "max":
        sell_thresh_ma = np.max(sell_returns)
    else:
        sell_thresh_ma = compute_threshold(sell_returns, base=sell_base_ma, direction="above", agg=sell_agg_ma)

    buy_thresh_prev = compute_threshold(buy_returns, base=buy_base_prev, direction="below", agg=buy_agg_prev)
    sell_thresh_prev = compute_threshold(sell_returns, base=sell_base_prev, direction="above", agg=sell_agg_prev)

    return buy_thresh_ma, buy_thresh_prev, sell_thresh_ma, sell_thresh_prev

# ----------------------------
# バックテスト関数：レンジ変動戦略（ナンピン＋一部売却）
# ----------------------------
def backtest_range_strategy(df, ma_period, lookback,
                            buy_method_ma, buy_method_prev, sell_method_ma, sell_method_prev,
                            initial_cash=10000, range_period=30):
    df = df.copy()
    df["MA"] = df["終値"].rolling(ma_period).mean()
    cash = initial_cash
    asset = 0.0

    for i in range(1, len(df)):
        if pd.isna(df["MA"].iloc[i]):
            continue

        # --- 過去 lookback 日リターンで閾値 ---
        if i >= lookback:
            buy_returns = df["安値"].iloc[i-lookback+1:i+1].values / df["終値"].iloc[i-lookback:i].values - 1
            sell_returns = df["高値"].iloc[i-lookback+1:i+1].values / df["終値"].iloc[i-lookback:i].values - 1
            buy_thresh_ma, buy_thresh_prev, sell_thresh_ma, sell_thresh_prev = get_thresholds(
                buy_returns, sell_returns, buy_method_ma, buy_method_prev, sell_method_ma, sell_method_prev
            )
            target_buy_ma   = df["MA"].iloc[i] * (1 + buy_thresh_ma)
            target_buy_prev = df["終値"].iloc[i-1] * (1 + buy_thresh_prev)
            target_sell_ma  = df["MA"].iloc[i] * (1 + sell_thresh_ma)
            target_sell_prev = df["終値"].iloc[i-1] * (1 + sell_thresh_prev)
        else:
            target_buy_ma = target_buy_prev = df["終値"].iloc[i-1]
            target_sell_ma = target_sell_prev = df["終値"].iloc[i-1]

        # --- 過去 range_period 日レンジに応じたポジション比率 ---
        if i >= range_period:
            recent_high = df["高値"].iloc[i-range_period+1:i+1].max()
            recent_low  = df["安値"].iloc[i-range_period+1:i+1].min()
            if recent_high > recent_low:
                range_ratio = (df["終値"].iloc[i] - recent_low) / (recent_high - recent_low)
            else:
                range_ratio = 0.5  # 高値=安値の場合
            # 現在レンジ比率に応じて保有比率を調整
            target_position_ratio = 1 - range_ratio  # 安値圏で多く、上値圏で少なく
        else:
            target_position_ratio = 0.5

        current_position_ratio = asset / (asset + cash / df["終値"].iloc[i]) if (asset + cash / df["終値"].iloc[i]) > 0 else 0
        delta_ratio = target_position_ratio - current_position_ratio

        # --- 売買量決定 ---
        if delta_ratio > 0 and cash > 0:
            purchase = cash * delta_ratio
            asset += purchase / df["終値"].iloc[i]
            cash -= purchase
        elif delta_ratio < 0 and asset > 0:
            sell_amount = asset * (-delta_ratio)
            cash += sell_amount * df["終値"].iloc[i]
            asset -= sell_amount

    final_value = cash + asset * df["終値"].iloc[-1]
    profit_percent = (final_value - initial_cash) / initial_cash * 100
    return final_value, profit_percent

# ----------------------------
# バックテスト関数：一括売買戦略
# ----------------------------
def backtest_full_strategy(df, ma_period, lookback,
                           buy_method_ma, buy_method_prev, sell_method_ma, sell_method_prev,
                           initial_cash=10000):
    df = df.copy()
    df["MA"] = df["終値"].rolling(ma_period).mean()
    cash = initial_cash
    asset = 0.0

    for i in range(1, len(df)):
        if pd.isna(df["MA"].iloc[i]):
            continue

        if i >= lookback:
            buy_returns = df["安値"].iloc[i-lookback+1:i+1].values / df["終値"].iloc[i-lookback:i].values - 1
            sell_returns = df["高値"].iloc[i-lookback+1:i+1].values / df["終値"].iloc[i-lookback:i].values - 1
            buy_thresh_ma, buy_thresh_prev, sell_thresh_ma, sell_thresh_prev = get_thresholds(
                buy_returns, sell_returns, buy_method_ma, buy_method_prev, sell_method_ma, sell_method_prev
            )
            target_buy_ma   = df["MA"].iloc[i] * (1 + buy_thresh_ma)
            target_buy_prev = df["終値"].iloc[i-1] * (1 + buy_thresh_prev)
            target_sell_ma  = df["MA"].iloc[i] * (1 + sell_thresh_ma)
            target_sell_prev = df["終値"].iloc[i-1] * (1 + sell_thresh_prev)
        else:
            target_buy_ma = target_buy_prev = df["終値"].iloc[i-1]
            target_sell_ma = target_sell_prev = df["終値"].iloc[i-1]

        # --- 買い（全額） ---
        if df["安値"].iloc[i] <= target_buy_ma and cash > 0:
            asset = cash / df["終値"].iloc[i]
            cash = 0
        elif df["安値"].iloc[i] <= target_buy_prev and cash > 0:
            asset = cash / df["終値"].iloc[i]
            cash = 0

        # --- 売り（全額） ---
        if df["高値"].iloc[i] >= target_sell_ma and asset > 0:
            cash = asset * df["終値"].iloc[i]
            asset = 0
        elif df["高値"].iloc[i] >= target_sell_prev and asset > 0:
            cash = asset * df["終値"].iloc[i]
            asset = 0

    final_value = cash + asset * df["終値"].iloc[-1]
    profit_percent = (final_value - initial_cash) / initial_cash * 100
    return final_value, profit_percent

# ----------------------------
# メイン処理
# ----------------------------
if __name__ == "__main__":
    symbol = "btc"
    df = pd.read_csv(f"{symbol}.csv")
    df["日付け"] = pd.to_datetime(df["日付け"])
    df.set_index("日付け", inplace=True)
    for col in ["終値", "高値", "安値"]:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors="coerce")

    # 固定パラメータ
    MA_Period = 12
    Lookback = 12
    Buy_Method_MA = "mean_above_mean"
    Buy_Method_Prev = "median"
    Sell_Method_MA = "median"
    Sell_Method_Prev = "median"

    # レンジ変動戦略
    rv_final, rv_profit = backtest_range_strategy(
        df, MA_Period, Lookback, Buy_Method_MA, Buy_Method_Prev, Sell_Method_MA, Sell_Method_Prev,
        initial_cash=10000, range_period=30
    )

    # 一括売買戦略
    fv_final, fv_profit = backtest_full_strategy(
        df, MA_Period, Lookback, Buy_Method_MA, Buy_Method_Prev, Sell_Method_MA, Sell_Method_Prev,
        initial_cash=10000
    )

    print(f"レンジ変動戦略 -> 最終資産: {rv_final:.2f}円, 利益率: {rv_profit:.2f}%")
    print(f"一括売買戦略 -> 最終資産: {fv_final:.2f}円, 利益率: {fv_profit:.2f}%")
