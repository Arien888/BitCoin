import pandas as pd
import matplotlib.pyplot as plt

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

def backtest(df, method="median_avg"):
    initial_cash = 10000
    cash = initial_cash
    btc = 0
    lookback = 30
    records = []

    for i in range(1, len(df)):
        if i >= lookback and method != "close":
            buy_returns = (df["安値"].iloc[i-lookback+1:i+1].values / df["終値"].iloc[i-lookback:i].values - 1)
            sell_returns = (df["高値"].iloc[i-lookback+1:i+1].values / df["終値"].iloc[i-lookback:i].values - 1)
            buy_threshold, sell_threshold = calc_thresholds(pd.Series(buy_returns), pd.Series(sell_returns), method)
        else:
            buy_threshold, sell_threshold = 0.0, 0.0

        # 指値計算
        if method == "close":
            target_buy = df["終値"].iloc[i-1]
            target_sell = df["終値"].iloc[i-1]
        else:
            target_buy = df["終値"].iloc[i-1] * (1 + buy_threshold)
            target_sell = df["終値"].iloc[i-1] * (1 + sell_threshold)

        # 買い条件（指値がMAより下）
        if cash > 0 and df["安値"].iloc[i] <= target_buy and target_buy < df["MA"].iloc[i]:
            btc = cash / target_buy
            cash = 0

        # 売り条件（指値がMAより上）
        if btc > 0 and df["高値"].iloc[i] >= target_sell and target_sell > df["MA"].iloc[i]:
            cash = btc * target_sell
            btc = 0

        # 記録
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

# --- CSVファイルリスト ---
symbols = ["doge","btc","dot","avax","eth","trx","ada","pepe","shib","hype","sol","xrp"]
csv_files = [f"{s}.csv" for s in symbols]

# MA期間と指値ルール
ma_periods = list(range(15, 26))  # 15～25
methods = ["mean", "median", "median_avg", "close"]

results_all = {}
records_all = {}

# --- 一括バックテスト ---
for file in csv_files:
    df = pd.read_csv(file)
    df["日付け"] = pd.to_datetime(df["日付け"])
    df.set_index("日付け", inplace=True)

    for col in ["終値","高値","安値"]:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors='coerce')

    results_opt = {}
    records_opt = {}

    for ma in ma_periods:
        df["MA"] = df["終値"].rolling(ma).mean()
        for method in methods:
            df_record, final_value, profit_percent = backtest(df, method=method)
            results_opt[(ma, method)] = profit_percent
            # 個別履歴も保存（後でCSVに）
            records_opt[(ma, method)] = df_record

    results_all[file] = results_opt
    records_all[file] = records_opt

# --- 利益率結果をCSVにまとめる ---
summary_list = []
for file, result in results_all.items():
    for (ma, method), profit in result.items():
        summary_list.append({
            "銘柄": file.replace(".csv",""),
            "MA期間": ma,
            "指値ルール": method,
            "利益率(%)": profit
        })
summary_df = pd.DataFrame(summary_list)
summary_df.to_csv("backtest_summary_all.csv", index=False)

# --- 各銘柄の最適条件を抽出 ---
best_list = []
for file in csv_files:
    symbol_name = file.replace(".csv","")
    df_symbol = summary_df[summary_df["銘柄"]==symbol_name]
    best_row = df_symbol.loc[df_symbol["利益率(%)"].idxmax()]
    best_list.append({
        "銘柄": symbol_name,
        "最適MA期間": best_row["MA期間"],
        "最適指値ルール": best_row["指値ルール"],
        "最大利益率(%)": best_row["利益率(%)"]
    })
best_df = pd.DataFrame(best_list)
best_df.to_csv("backtest_best_all.csv", index=False)

print("バックテスト結果を 'backtest_summary_all.csv'、最適条件を 'backtest_best_all.csv' に保存しました。")
