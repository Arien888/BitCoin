import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

try:
    import cudf
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

# --- 閾値計算 ---
def calc_thresholds(buy_returns, sell_returns, method="median_avg"):
    if method == "mean":
        return buy_returns.mean(), sell_returns.mean()
    elif method == "median":
        return buy_returns.median(), sell_returns.median()
    elif method == "median_avg":
        buy_thresh = buy_returns[buy_returns <= buy_returns.median()].mean()
        sell_thresh = sell_returns[sell_returns >= sell_returns.median()].mean()
        return buy_thresh, sell_thresh
    else:
        return 0.0, 0.0

# --- バックテスト ---
def backtest_single(args):
    df, buy_method, sell_method, lookback, rule_type = args
    initial_cash = 10000
    cash = initial_cash
    btc = 0
    records = []

    for i in range(1, len(df)):
        target_buy = df["終値"].iloc[i - 1]
        target_sell = df["終値"].iloc[i - 1]

        # 過去lookback日でリターン計算
        if i >= lookback:
            buy_returns = df["安値"].iloc[i - lookback + 1:i + 1].values / df["終値"].iloc[i - lookback:i].values - 1
            sell_returns = df["高値"].iloc[i - lookback + 1:i + 1].values / df["終値"].iloc[i - lookback:i].values - 1

            if buy_method.startswith("ma_based"):
                base_method = buy_method.replace("ma_based_", "")
                buy_threshold, _ = calc_thresholds(pd.Series(buy_returns), pd.Series(sell_returns), base_method)
            else:
                buy_threshold, _ = calc_thresholds(pd.Series(buy_returns), pd.Series(sell_returns), buy_method)

            if sell_method.startswith("ma_based"):
                base_method = sell_method.replace("ma_based_", "")
                _, sell_threshold = calc_thresholds(pd.Series(buy_returns), pd.Series(sell_returns), base_method)
            else:
                _, sell_threshold = calc_thresholds(pd.Series(buy_returns), pd.Series(sell_returns), sell_method)
        else:
            buy_threshold = 0.0
            sell_threshold = 0.0

        # --- 指値計算 ---
        if rule_type == "threshold_capped":
            # 計算値をMAで上限・下限
            if buy_method.startswith("ma_based"):
                target_buy = df["MA"].iloc[i] * (1 + buy_threshold)
                if df["終値"].iloc[i - 1] < target_buy:
                    target_buy = df["終値"].iloc[i - 1]
            else:
                target_buy = df["終値"].iloc[i - 1] * (1 + buy_threshold)
                if target_buy > df["MA"].iloc[i]:
                    target_buy = df["MA"].iloc[i]

            if sell_method.startswith("ma_based"):
                target_sell = df["MA"].iloc[i] * (1 + sell_threshold)
                if df["終値"].iloc[i - 1] > target_sell:
                    target_sell = df["終値"].iloc[i - 1]
            else:
                target_sell = df["終値"].iloc[i - 1] * (1 + sell_threshold)
                if target_sell < df["MA"].iloc[i]:
                    target_sell = df["MA"].iloc[i]

        elif rule_type == "current_vs_ma":
            # 現在価格をMAと比較して購入/売却可否
            target_buy = df["終値"].iloc[i - 1] if df["終値"].iloc[i - 1] <= df["MA"].iloc[i] else np.nan
            target_sell = df["終値"].iloc[i - 1] if df["終値"].iloc[i - 1] >= df["MA"].iloc[i] else np.nan

        # --- 売買 ---
        if cash > 0 and not np.isnan(target_buy) and df["安値"].iloc[i] <= target_buy:
            btc = cash / target_buy
            cash = 0
        if btc > 0 and not np.isnan(target_sell) and df["高値"].iloc[i] >= target_sell:
            cash = btc * target_sell
            btc = 0

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

# --- GPU対応 ---
def to_gpu(df):
    if GPU_AVAILABLE:
        return cudf.DataFrame.from_pandas(df)
    return df

# ==============================
# main
# ==============================
if __name__ == "__main__":
    multiprocessing.freeze_support()

    symbols = ["doge","btc","dot","avax","eth","trx","ada","pepe","shib","hype","sol","xrp"]
    csv_files = [f"{s}.csv" for s in symbols]

    ma_periods = list(range(15, 26))
    methods = ["mean","median","median_avg","ma_based_mean","ma_based_median","ma_based_median_avg","ma_simple"]
    lookbacks = list(range(10, 25))
    rule_types = ["threshold_capped","current_vs_ma"]

    results_all = {}
    records_all = {}
    one_year_ago = datetime.today() - timedelta(days=365)

    for file in csv_files:
        df = pd.read_csv(file)
        df["日付け"] = pd.to_datetime(df["日付け"])
        df.set_index("日付け", inplace=True)
        df = df[df.index >= one_year_ago]

        for col in ["終値","高値","安値"]:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors="coerce")

        results_opt = {}
        records_opt = {}
        tasks = []

        for ma in ma_periods:
            df["MA"] = df["終値"].rolling(ma).mean()
            for buy_method in methods:
                for sell_method in methods:
                    for lookback in lookbacks:
                        for rule_type in rule_types:
                            tasks.append((to_gpu(df.copy()), buy_method, sell_method, lookback, rule_type))

        with ProcessPoolExecutor() as executor:
            futures = {executor.submit(backtest_single, t): t for t in tasks}
            for future in as_completed(futures):
                t = futures[future]
                df_record, final_value, profit_percent = future.result()
                results_opt[(t[1], t[2], t[3], t[4])] = (final_value, profit_percent)
                records_opt[(t[1], t[2], t[3], t[4])] = df_record

        results_all[file] = results_opt
        records_all[file] = records_opt

    # --- 集計 ---
    summary_list = []
    for file, result in results_all.items():
        for (buy_method, sell_method, lookback, rule_type), (final_value, profit) in result.items():
            summary_list.append({
                "銘柄": file.replace(".csv",""),
                "買いルール": buy_method,
                "売りルール": sell_method,
                "Lookback日数": lookback,
                "ルールタイプ": rule_type,
                "最終資産": final_value,
                "利益率(%)": profit
            })

    summary_df = pd.DataFrame(summary_list)
    summary_df_sorted = summary_df.sort_values(by="利益率(%)", ascending=False)
    summary_df_sorted.to_csv("backtest_summary_1year_parallel_gpu.csv", index=False)

    print("1年以内のバックテスト結果（改良版）を保存しました。")
    print("個別結果: 'backtest_summary_1year_parallel_gpu.csv'")
