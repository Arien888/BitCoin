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
    cash = initial_cash
    asset = 0.0
    history = []

    for i in range(1, len(df)):
        if pd.isna(df["MA"].iloc[i]):
            continue

        # --- 閾値計算 ---
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
            range_ratio = (df["終値"].iloc[i] - recent_low) / (recent_high - recent_low) if recent_high > recent_low else 0.5
            target_position_ratio = min(max(1 - range_ratio, 0), 1)
        else:
            target_position_ratio = 0.5

        total_value = cash + asset * df["終値"].iloc[i]
        current_position_ratio = asset * df["終値"].iloc[i] / total_value if total_value > 0 else 0
        delta_ratio = target_position_ratio - current_position_ratio

        # --- 売買 ---
        if delta_ratio > 0 and cash > 0:
            purchase = cash * delta_ratio
            asset += purchase / df["終値"].iloc[i]
            cash -= purchase
        elif delta_ratio < 0 and asset > 0:
            sell_amount = asset * (-delta_ratio)
            cash += sell_amount * df["終値"].iloc[i]
            asset -= sell_amount

        history.append({
            "date": df.index[i],
            "price": df["終値"].iloc[i],
            "cash": cash,
            "asset": asset,
            "total_value": cash + asset * df["終値"].iloc[i],
            "position_ratio": asset * df["終値"].iloc[i] / (cash + asset * df["終値"].iloc[i])
        })

    total_values = [h["total_value"] for h in history]
    cum_max = np.maximum.accumulate(total_values)
    drawdown = [(cum_max[i] - total_values[i]) / cum_max[i] for i in range(len(total_values))]
    max_drawdown = max(drawdown) if drawdown else 0

    final_value = cash + asset * df["終値"].iloc[-1]
    profit_percent = (final_value - initial_cash) / initial_cash * 100

    return final_value, profit_percent, max_drawdown, history

# ----------------------------
# バックテスト：一括買い・一括売り
# ----------------------------
def backtest_lump_strategy(df, initial_cash=10000):
    df = df.copy()
    cash = initial_cash
    asset = 0.0
    history = []

    for i in range(len(df)):
        # 一括買い：最初の日に全額購入
        if i == 0:
            asset = cash / df["終値"].iloc[i]
            cash = 0
        # 一括売り：最後の日に全て売却
        if i == len(df) - 1:
            cash = asset * df["終値"].iloc[i]
            asset = 0

        history.append({
            "date": df.index[i],
            "price": df["終値"].iloc[i],
            "cash": cash,
            "asset": asset,
            "total_value": cash + asset * df["終値"].iloc[i],
            "position_ratio": asset * df["終値"].iloc[i] / (cash + asset * df["終値"].iloc[i]) if (cash+asset*df["終値"].iloc[i])>0 else 0
        })

    total_values = [h["total_value"] for h in history]
    cum_max = np.maximum.accumulate(total_values)
    drawdown = [(cum_max[i] - total_values[i]) / cum_max[i] for i in range(len(total_values))]
    max_drawdown = max(drawdown) if drawdown else 0

    final_value = cash + asset * df["終値"].iloc[-1]
    profit_percent = (final_value - initial_cash) / initial_cash * 100

    return final_value, profit_percent, max_drawdown, history

# ----------------------------
# メイン処理：比較
# ----------------------------
if __name__ == "__main__":
    symbol = "btc"
    df = pd.read_csv(f"{symbol}.csv")
    df["日付け"] = pd.to_datetime(df["日付け"])
    df.set_index("日付け", inplace=True)
    for col in ["終値", "高値", "安値"]:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors="coerce")

    MA_Period = 11
    Lookback = 13
    Buy_Method_MA = "mean_above_mean"
    Buy_Method_Prev = "median"
    Sell_Method_MA = "median"
    Sell_Method_Prev = "median"
    initial_cash = 10000

    # レンジ戦略
    range_results = []
    for range_period in range(30, 121, 10):
        final, profit, max_dd, history = backtest_range_strategy(
            df, MA_Period, Lookback,
            Buy_Method_MA, Buy_Method_Prev, Sell_Method_MA, Sell_Method_Prev,
            initial_cash=initial_cash, range_period=range_period
        )
        avg_position = np.mean([h["position_ratio"] for h in history]) if history else 0
        range_results.append((range_period, final, profit, max_dd, avg_position))

    # 一括買い戦略
    lump_final, lump_profit, lump_dd, lump_history = backtest_lump_strategy(df, initial_cash=initial_cash)

    # 結果表示
    print("レンジ期間別バックテスト結果（レンジ戦略）")
    print("RangePeriod\tFinalAsset\tProfit%\tMaxDrawdown%\tAvgPosition")
    for r, f, p, dd, pos in range_results:
        print(f"{r}\t{f:.2f}\t{p:.2f}\t{dd*100:.2f}\t{pos:.2f}")

    print("\n一括買い戦略結果")
    print(f"FinalAsset: {lump_final:.2f}, Profit%: {lump_profit:.2f}, MaxDrawdown%: {lump_dd*100:.2f}")
