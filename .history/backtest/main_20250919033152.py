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

# --- バックテスト用関数 ---
def calc_thresholds(buy_returns, sell_returns, method="median_avg"):
    if method == "mean":
        return buy_returns.mean(), sell_returns.mean()
    elif method == "median":
        return buy_returns.median(), sell_returns.median()
    elif method == "median_avg":
        buy_thresh = buy_returns[buy_returns <= buy_returns.median()].mean()
        sell_thresh = sell_returns[sell_returns >= sell_returns.median()].mean()
        return buy_thresh, sell_thresh
    elif method == "close":
        return 0.0, 0.0

def backtest_single(args):
    df, buy_method, sell_method, lookback = args
    initial_cash = 10000
    cash = initial_cash
    btc = 0
    records = []

    for i in range(1, len(df)):
        target_buy = df["終値"].iloc[i-1]
        target_sell = df["終値"].iloc[i-1]

        # --- 過去lookback日でのリターン計算 ---
        if i >= lookback:
            buy_returns = df["安値"].iloc[i-lookback+1:i+1].values / df["終値"].iloc[i-lookback:i].values - 1
            sell_returns = df["高値"].iloc[i-lookback+1:i+1].values / df["終値"].iloc[i-lookback:i].values - 1

            # 買い閾値
            if buy_method.startswith("ma_based"):
                base_method = buy_method.replace("ma_based_", "")
                buy_threshold, _ = calc_thresholds(pd.Series(buy_returns), pd.Series(sell_returns), base_method)
            elif buy_method not in ["close", "ma_simple"]:
                buy_threshold, _ = calc_thresholds(pd.Series(buy_returns), pd.Series(sell_returns), buy_method)
            else:
                buy_threshold = 0.0

            # 売り閾値
            if sell_method.startswith("ma_based"):
                base_method = sell_method.replace("ma_based_", "")
                _, sell_threshold = calc_thresholds(pd.Series(buy_returns), pd.Series(sell_returns), base_method)
            elif sell_method not in ["close", "ma_simple"]:
                _, sell_threshold = calc_thresholds(pd.Series(buy_returns), pd.Series(sell_returns), sell_method)
            else:
                sell_threshold = 0.0
        else:
            buy_threshold = 0.0
            sell_threshold = 0.0

        # --- 指値計算 ---
        if buy_method == "close":
            target_buy = df["終値"].iloc[i-1]
        elif buy_method.startswith("ma_based"):
            target_buy = df["MA"].iloc[i] * (1 + buy_threshold)
            if df["終値"].iloc[i-1] < target_buy:
                target_buy = df["終値"].iloc[i-1]
        elif buy_method == "ma_simple":
            target_buy = df["MA"].iloc[i]
        else:
            target_buy = df["終値"].iloc[i-1] * (1 + buy_threshold)

        if sell_method == "close":
            target_sell = df["終値"].iloc[i-1]
        elif sell_method.startswith("ma_based"):
            target_sell = df["MA"].iloc[i] * (1 + sell_threshold)
            if df["終値"].iloc[i-1] > target_sell:
                target_sell = df["終値"].iloc[i-1]
        elif sell_method == "ma_simple":
            target_sell = df["MA"].iloc[i]
        else:
            target_sell = df["終値"].iloc[i-1] * (1 + sell_threshold)

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

def to_gpu(df):
    if GPU_AVAILABLE:
        return cudf.DataFrame.from_pandas(df)
    return df

# ==============================
# main
# ==============================
if __name__ == "__main__":
    multiprocessing.freeze_support()  # Windows対応

    symbols = ["doge","btc","dot","avax","eth","trx","ada","pepe","shib","hype","sol","xrp"]
    csv_files = [f"{s}.csv" for s in symbols]

    ma_periods = list(range(15, 26))
    methods = ["mean","median","median_avg","close","ma_based_mean","ma_based_median","ma_based_median_avg","ma_simple"]
    lookbacks = list(range(10, 25))

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
                        tasks.append((to_gpu(df.copy()), buy_method, sell_method, lookback, ma))

        with ProcessPoolExecutor() as executor:
            futures = {executor.submit(backtest_single, (t[0], t[1], t[2], t[3])): t for t in tasks}
            for future in as_completed(futures):
                t = futures[future]
                ma, buy_method, sell_method, lookback = t[4], t[1], t[2], t[3]
                df_record, final_value, profit_percent = future.result()
                results_opt[(ma, buy_method, sell_method, lookback)] = (final_value, profit_percent)
                records_opt[(ma, buy_method, sell_method, lookback)] = df_record

        results_all[file] = results_opt
        records_all[file] = records_opt

    # --- 集計 ---
    summary_list = []
    for file, result in results_all.items():
        for (ma, buy_method, sell_method, lookback), (final_value, profit) in result.items():
            summary_list.append({
                "銘柄": file.replace(".csv",""),
                "MA期間": ma,
                "買いルール": buy_method,
                "売りルール": sell_method,
                "Lookback日数": lookback,
                "最終資産": final_value,
                "利益率(%)": profit
            })

    summary_df = pd.DataFrame(summary_list)
    summary_df_sorted = summary_df.sort_values(by="利益率(%)", ascending=False)
    summary_df_sorted.to_csv("backtest_summary_1year_parallel_gpu.csv", index=False)

    # --- 各銘柄の最適条件 ---
    best_list = []
    for file in csv_files:
        symbol_name = file.replace(".csv","")
        df_symbol = summary_df[summary_df["銘柄"]==symbol_name]
        best_row = df_symbol.loc[df_symbol["利益率(%)"].idxmax()]
        best_list.append({
            "銘柄": symbol_name,
            "最適MA期間": best_row["MA期間"],
            "最適買いルール": best_row["買いルール"],
            "最適売りルール": best_row["売りルール"],
            "最適Lookback日数": best_row["Lookback日数"],
            "最大利益率(%)": best_row["利益率(%)"]
        })

    best_df = pd.DataFrame(best_list)
    best_df.to_csv("backtest_best_1year_parallel_gpu.csv", index=False)

    avg_lookback = round(best_df["最適Lookback日数"].mean())
    pd.DataFrame([{"全銘柄平均Lookback日数": avg_lookback}]).to_csv(
        "backtest_best_lookback_avg_parallel_gpu.csv", index=False
    )

    print("1年以内のバックテスト結果（並列・GPU対応）を保存しました。")
    print("個別結果: 'backtest_summary_1year_parallel_gpu.csv'")
    print("最適条件: 'backtest_best_1year_parallel_gpu.csv'")
    print("全銘柄共通平均Lookback日数:", avg_lookback)
