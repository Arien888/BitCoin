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
    filtered = arr[arr >= ref] if direction == "above" else arr[arr <= ref]
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

    buy_thresh_ma = compute_threshold(buy_returns, base=buy_base_ma, direction="below", agg=buy_agg_ma)
    sell_thresh_ma = compute_threshold(sell_returns, base=sell_base_ma, direction="above", agg=sell_agg_ma)
    buy_thresh_prev = compute_threshold(buy_returns, base=buy_base_prev, direction="below", agg=buy_agg_prev)
    sell_thresh_prev = compute_threshold(sell_returns, base=sell_base_prev, direction="above", agg=sell_agg_prev)

    return buy_thresh_ma, buy_thresh_prev, sell_thresh_ma, sell_thresh_prev

# ----------------------------
# バックテスト：レンジ変動戦略（ナンピン＋一部売却）
# ----------------------------
def backtest_range_strategy(df, ma_period, lookback,
                            buy_method_ma, buy_method_prev, sell_method_ma, sell_method_prev,
                            initial_cash=10000, range_period=30):
    df = df.copy()
    df["MA"] = df["終値"].rolling(ma_period).mean()
    df = df.dropna(subset=["MA", "終値", "高値", "安値"])
    cash = initial_cash
    asset = 0.0
    history = []

    for i in range(lookback, len(df)):
        # 過去リターン計算
        buy_returns = df["安値"].iloc[i-lookback:i].pct_change().dropna().values
        sell_returns = df["高値"].iloc[i-lookback:i].pct_change().dropna().values
        buy_thresh_ma, buy_thresh_prev, sell_thresh_ma, sell_thresh_prev = get_thresholds(
            buy_returns, sell_returns, buy_method_ma, buy_method_prev, sell_method_ma, sell_method_prev
        )

        target_buy_ma = df["MA"].iloc[i] * (1 - abs(buy_thresh_ma))
        target_buy_prev = df["終値"].iloc[i-1] * (1 - abs(buy_thresh_prev))
        target_sell_ma = df["MA"].iloc[i] * (1 + abs(sell_thresh_ma))
        target_sell_prev = df["終値"].iloc[i-1] * (1 + abs(sell_thresh_prev))

        # レンジ比率（逆張り）
        if i >= range_period:
            recent_high = df["高値"].iloc[i-range_period+1:i+1].max()
            recent_low = df["安値"].iloc[i-range_period+1:i+1].min()
            if recent_high > recent_low:
                target_position_ratio = (recent_high - df["終値"].iloc[i]) / (recent_high - recent_low)
            else:
                target_position_ratio = 0.5
            target_position_ratio = np.clip(target_position_ratio, 0, 1)
        else:
            target_position_ratio = 0.5

        total_value = cash + asset * df["終値"].iloc[i]
        current_position_ratio = asset * df["終値"].iloc[i] / total_value if total_value > 0 else 0
        delta_ratio = target_position_ratio - current_position_ratio

        # 売買
        if delta_ratio > 0 and cash > 0:
            purchase = cash * delta_ratio
            asset += purchase / df["終値"].iloc[i]
            cash -= purchase
        elif delta_ratio < 0 and asset > 0:
            sell_amount = asset * (-delta_ratio)
            cash += sell_amount * df["終値"].iloc[i]
            asset -= sell_amount

        # 履歴
        history.append({
            "date": df.index[i],
            "price": df["終値"].iloc[i],
            "cash": cash,
            "asset": asset,
            "total_value": cash + asset * df["終値"].iloc[i],
            "position_ratio": asset * df["終値"].iloc[i] / (cash + asset * df["終値"].iloc[i])
        })

    # 最大ドローダウン
    total_values = [h["total_value"] for h in history]
    cum_max = np.maximum.accumulate(total_values)
    drawdown = [(cum_max[i] - total_values[i]) / cum_max[i] for i in range(len(total_values))]
    max_drawdown = max(drawdown) if drawdown else 0

    final_value = cash + asset * df["終値"].iloc[-1]
    profit_percent = (final_value - initial_cash) / initial_cash * 100
    return final_value, profit_percent, max_drawdown, history

# ----------------------------
# バックテスト：一括買い戦略
# ----------------------------
def backtest_full_strategy(df, ma_period, lookback,
                           buy_method_ma, buy_method_prev, sell_method_ma, sell_method_prev,
                           initial_cash=10000):
    df = df.copy()
    df["MA"] = df["終値"].rolling(ma_period).mean()
    df = df.dropna(subset=["MA", "終値", "高値", "安値"])
    cash = initial_cash
    asset = 0.0
    history = []

    for i in range(lookback, len(df)):
        buy_returns = df["安値"].iloc[i-lookback:i].pct_change().dropna().values
        sell_returns = df["高値"].iloc[i-lookback:i].pct_change().dropna().values
        buy_thresh_ma, buy_thresh_prev, sell_thresh_ma, sell_thresh_prev = get_thresholds(
            buy_returns, sell_returns, buy_method_ma, buy_method_prev, sell_method_ma, sell_method_prev
        )

        target_buy_ma = df["MA"].iloc[i] * (1 - abs(buy_thresh_ma))
        target_buy_prev = df["終値"].iloc[i-1] * (1 - abs(buy_thresh_prev))
        target_sell_ma = df["MA"].iloc[i] * (1 + abs(sell_thresh_ma))
        target_sell_prev = df["終値"].iloc[i-1] * (1 + abs(sell_thresh_prev))

        # 買い
        if df["安値"].iloc[i] <= target_buy_ma and cash > 0:
            asset = cash / df["安値"].iloc[i]
            cash = 0
        elif df["安値"].iloc[i] <= target_buy_prev and cash > 0:
            asset = cash / df["安値"].iloc[i]
            cash = 0

        # 売り
        if df["高値"].iloc[i] >= target_sell_ma and asset > 0:
            cash = asset * df["高値"].iloc[i]
            asset = 0
        elif df["高値"].iloc[i] >= target_sell_prev and asset > 0:
            cash = asset * df["高値"].iloc[i]
            asset = 0

        total_value = cash + asset * df["終値"].iloc[i]
        history.append({
            "date": df.index[i],
            "price": df["終値"].iloc[i],
            "cash": cash,
            "asset": asset,
            "total_value": total_value,
            "position_ratio": asset * df["終値"].iloc[i] / total_value if total_value > 0 else 0
        })

    total_values = [h["total_value"] for h in history]
    cum_max = np.maximum.accumulate(total_values)
    drawdown = [(cum_max[i] - total_values[i]) / cum_max[i] for i in range(len(total_values))]
    max_drawdown = max(drawdown) if drawdown else 0

    final_value = cash + asset * df["終値"].iloc[-1]
    profit_percent = (final_value - initial_cash) / initial_cash * 100
    return final_value, profit_percent, max_drawdown, history

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
    df = df.dropna(subset=["終値", "高値", "安値"])

    MA_Period = 11
    Lookback = 13
    Buy_Method_MA = "mean_above_mean"
    Buy_Method_Prev = "median"
    Sell_Method_MA = "median"
    Sell_Method_Prev = "median"
    initial_cash = 10000

    # レンジ戦略：レンジ期間 30～120 日で比較
    results_range = []
    for range_period in range(30, 121, 10):
        final, profit, max_dd, history = backtest_range_strategy(
            df, MA_Period, Lookback,
            Buy_Method_MA, Buy_Method_Prev, Sell_Method_MA, Sell_Method_Prev,
            initial_cash=initial_cash, range_period=range_period
        )
        avg_position = np.mean([h["position_ratio"] for h in history]) if history else 0
        results_range.append((range_period, final, profit, max_dd, avg_position))

    # 一括買い戦略
    final_full, profit_full, max_dd_full, history_full = backtest_full_strategy(
        df, MA_Period, Lookback, Buy_Method_MA, Buy_Method_Prev, Sell_Method_MA, Sell_Method_Prev, initial_cash
    )
    avg_position_full = np.mean([h["position_ratio"] for h in history_full]) if history_full else 0

    # 結果表示
    print("=== レンジ戦略（ナンピン＋一部売却） ===")
    print("RangePeriod\tFinalAsset\tProfit%\tMaxDrawdown%\tAvgPosition")
    for r, f, p, dd, pos in results_range:
        print(f"{r}\t{f:.2f}\t{p:.2f}\t{dd*100:.2f}\t{pos:.2f}")

    print("\n=== 一括買い戦略 ===")
    print(f"FinalAsset: {final_full:.2f}, Profit%: {profit_full:.2f}, MaxDrawdown%: {max_dd_full*100:.2f}, AvgPosition: {avg_position_full:.2f}")
