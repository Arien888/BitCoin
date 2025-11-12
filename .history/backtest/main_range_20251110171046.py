import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import product
from concurrent.futures import ProcessPoolExecutor, as_completed

# ==========================================================
# 閾値計算関数
# ==========================================================
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

# ==========================================================
# 閾値セット取得
# ==========================================================
def get_thresholds(buy_returns, sell_returns, buy_method_ma, buy_method_prev, sell_method_ma, sell_method_prev):
    def parse_method(m):
        if "_above_" in m:
            base, agg = m.split("_above_")
            return base, "above", agg
        elif "_below_" in m:
            base, agg = m.split("_below_")
            return base, "below", agg
        elif m in ["mean", "median", "max"]:
            return m, "above", m
        else:
            raise ValueError("Unknown method: " + str(m))

    buy_base_ma, buy_dir_ma, buy_agg_ma = parse_method(buy_method_ma)
    buy_base_prev, buy_dir_prev, buy_agg_prev = parse_method(buy_method_prev)
    sell_base_ma, sell_dir_ma, sell_agg_ma = parse_method(sell_method_ma)
    sell_base_prev, sell_dir_prev, sell_agg_prev = parse_method(sell_method_prev)

    buy_thresh_ma = compute_threshold(buy_returns, base=buy_base_ma, direction=buy_dir_ma, agg=buy_agg_ma)
    sell_thresh_ma = compute_threshold(sell_returns, base=sell_base_ma, direction=sell_dir_ma, agg=sell_agg_ma)
    buy_thresh_prev = compute_threshold(buy_returns, base=buy_base_prev, direction=buy_dir_prev, agg=buy_agg_prev)
    sell_thresh_prev = compute_threshold(sell_returns, base=sell_base_prev, direction=sell_dir_prev, agg=sell_agg_prev)

    return buy_thresh_ma, buy_thresh_prev, sell_thresh_ma, sell_thresh_prev

# ==========================================================
# 一括買い戦略（何度も売買可能）
# ==========================================================
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

        # --- 買い ---
        if df["安値"].iloc[i] <= target_buy_price and cash > 0:
            purchase = cash
            asset += purchase / df["安値"].iloc[i]
            trades.append({'type': 'buy', 'price': df["安値"].iloc[i]})
            cash = 0
            entry_price = df["安値"].iloc[i]
            position = asset

        # --- 売り ---
        if df["高値"].iloc[i] >= target_sell_price and asset > 0:
            cash += asset * df["高値"].iloc[i]
            profit_pct = (df["高値"].iloc[i] - entry_price) / entry_price * 100
            trades.append({'type': 'sell', 'price': df["高値"].iloc[i], 'profit_pct': profit_pct})
            asset = 0
            position = 0
            entry_price = 0

        total_value = cash + asset * df["終値"].iloc[i]
        history.append(total_value)

    total_values = np.array(history)
    cum_max = np.maximum.accumulate(total_values)
    drawdown = (cum_max - total_values) / cum_max
    max_drawdown = drawdown.max() if len(drawdown) > 0 else 0

    final_value = cash + asset * df["終値"].iloc[-1]
    profit_percent = (final_value - initial_cash) / initial_cash * 100
    trade_profits = [t['profit_pct'] for t in trades if 'profit_pct' in t]
    avg_trade_profit = np.mean(trade_profits) if trade_profits else 0

    return {
        "final_value": final_value,
        "profit_percent": profit_percent,
        "max_drawdown": max_drawdown * 100,
        "trade_count": len(trade_profits),
        "avg_trade_profit": avg_trade_profit
    }

# ==========================================================
# 並列化ラッパー
# ==========================================================
def backtest_wrapper(params):
    ma, lb, bm, bp, sm, sp, df = params  # dfを引数で受け取る
    res = backtest_full_strategy_repeat(df, ma, lb, bm, bp, sm, sp)
    res.update({
        "MA": ma,
        "Lookback": lb,
        "Buy_MA": bm,
        "Buy_Prev": bp,
        "Sell_MA": sm,
        "Sell_Prev": sp,
    })
    return res

# ==========================================================
# メイン処理
# ==========================================================
if __name__ == "__main__":
    symbol = "btc"
    df = pd.read_csv(f"{symbol}.csv")
    df["日付け"] = pd.to_datetime(df["日付け"])
    df.set_index("日付け", inplace=True)
    for col in ["終値", "高値", "安値"]:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors="coerce")

    ma_list = range(11, 17)
    lookback_list = range(11, 17)
    methods = [
        "mean_above_mean", "median_above_mean",
        "mean_below_mean", "median_below_mean",
        "mean_above_median", "median_above_median",
        "mean_below_median", "median_below_median"
    ]

    # DataFrame を各パラメータと一緒に渡す
    param_list = [(ma, lb, bm, bp, sm, sp, df) 
                  for ma, lb, bm, bp, sm, sp in product(ma_list, lookback_list, methods, methods, methods, methods)]

    results = []
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(backtest_wrapper, p) for p in param_list]
        for f in as_completed(futures):
            results.append(f.result())

    result_df = pd.DataFrame(results)
    result_df.sort_values("profit_percent", ascending=False, inplace=True)

    print("\n=== 上位パラメータ ===")
    print(result_df.head(10)[["MA", "Lookback", "Buy_MA", "Sell_MA", "profit_percent", "max_drawdown", "trade_count", "avg_trade_profit"]])

    # --- 可視化 ---
    plt.figure(figsize=(10, 5))
    plt.scatter(result_df["MA"], result_df["profit_percent"], label="Profit%")
    plt.title("MA期間と利益率の関係")
    plt.xlabel("MA Period")
    plt.ylabel("Profit %")
    plt.grid(True)
    plt.legend()
    plt.show()
