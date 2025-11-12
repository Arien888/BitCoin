import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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
# 一括買い戦略（何度も売買可能）
# ----------------------------
def backtest_full_strategy_repeat(df, ma_period, lookback,
                                  buy_method_ma, buy_method_prev, sell_method_ma, sell_method_prev,
                                  initial_cash=10000):
    df = df.copy()
    df["MA"] = df["終値"].rolling(ma_period).mean()
    df = df.dropna(subset=["MA", "終値", "高値", "安値"])
    cash = initial_cash
    asset = 0.0
    history = []
    trades = []

    position = 0
    entry_price = 0

    for i in range(lookback, len(df)):
        buy_returns = df["安値"].iloc[i-lookback:i].pct_change().dropna().values
        sell_returns = df["高値"].iloc[i-lookback:i].pct_change().dropna().values
        buy_thresh_ma, buy_thresh_prev, sell_thresh_ma, sell_thresh_prev = get_thresholds(
            buy_returns, sell_returns, buy_method_ma, buy_method_prev, sell_method_ma, sell_method_prev
        )

        target_buy_price = min(df["MA"].iloc[i] * (1 - abs(buy_thresh_ma)),
                               df["終値"].iloc[i-1] * (1 - abs(buy_thresh_prev)))
        target_sell_price = max(df["MA"].iloc[i] * (1 + abs(sell_thresh_ma)),
                                df["終値"].iloc[i-1] * (1 + abs(sell_thresh_prev)))

        # --- 売買判定 ---
        # 買い
        if df["安値"].iloc[i] <= target_buy_price and cash > 0:
            purchase = cash
            asset += purchase / df["安値"].iloc[i]
            trades.append({'type': 'buy', 'price': df["安値"].iloc[i], 'amount': purchase})
            cash = 0
            entry_price = df["安値"].iloc[i]
            position = asset
        # 売り
        elif df["高値"].iloc[i] >= target_sell_price and asset > 0:
            sell_amount = asset
            cash += sell_amount * df["高値"].iloc[i]
            trades.append({'type': 'sell', 'price': df["高値"].iloc[i], 'amount': sell_amount * df["高値"].iloc[i]})
            asset = 0
            if position > 0:
                trades[-1]['profit_pct'] = (df["高値"].iloc[i] - entry_price) / entry_price * 100
            position = 0
            entry_price = 0

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

    trade_profits = [t['profit_pct'] for t in trades if 'profit_pct' in t]
    trade_count = len(trade_profits)
    avg_trade_profit = np.mean(trade_profits) if trade_profits else 0

    return final_value, profit_percent, max_drawdown, history, trade_count, avg_trade_profit

# ----------------------------
# 実行部分
# ----------------------------
if __name__ == "__main__":
    symbol = "btc"
    df = pd.read_csv(f"{symbol}.csv")
    df["日付け"] = pd.to_datetime(df["日付け"])
    df.set_index("日付け", inplace=True)
    for col in ["終値", "高値", "安値"]:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors="coerce")

    fv_final, fv_profit, fv_dd, fv_history, fv_trade_count, fv_avg_trade_profit = backtest_full_strategy_repeat(
        df,
        ma_period=11,
        lookback=13,
        buy_method_ma="mean_above_mean",
        buy_method_prev="median",
        sell_method_ma="median",
        sell_method_prev="median",
        initial_cash=10000
    )

    print("\n=== 一括買い戦略（何度も売買可能） ===")
    print(f"FinalAsset: {fv_final:.2f}, Profit%: {fv_profit:.2f}, MaxDrawdown%: {fv_dd*100:.2f}, "
          f"TradeCount: {fv_trade_count}, AvgTradeProfit%: {fv_avg_trade_profit:.2f}")

    plt.figure(figsize=(12,6))
    plt.plot([h["date"] for h in fv_history], [h["total_value"] for h in fv_history],
             label="一括買い戦略", linewidth=2, color="black")
    plt.title("一括買い戦略資産推移")
    plt.xlabel("Date")
    plt.ylabel("Total Value")
    plt.legend()
    plt.show()
