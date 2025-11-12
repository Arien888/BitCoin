import numpy as np
import pandas as pd

# ==========================================================
# 閾値計算（values の分布から乖離率を推定）
# ----------------------------------------------------------
# base（基準の取り方）: "median" / "mean" / "max"
# direction（基準より上/下どちらを見るか）: "above" / "below"
# agg（集約の取り方）: "mean" / "median"
# 戻り値は |乖離率|（正の実数）
# ==========================================================
def compute_threshold(values, base="median", direction="above", agg="mean"):
    arr = np.asarray(values, dtype=float)
    if arr.size == 0:
        return 0.01  # データ不足時のデフォルト乖離率（1%）
    ref = np.median(arr) if base == "median" else (np.max(arr) if base == "max" else np.mean(arr))
    filtered = arr[arr >= ref] if direction == "above" else arr[arr <= ref]
    if filtered.size == 0:
        val = ref
    else:
        val = np.mean(filtered) if agg == "mean" else np.median(filtered)
    return max(abs(float(val)), 0.005)  # 最小0.5%は確保

# ==========================================================
# メソッド名を分解（例: "median_above_mean"）
# ----------------------------------------------------------
# 戻り値: (base, direction, agg)
# ==========================================================
def parse_method(m):
    if "_above_" in m:
        base, agg = m.split("_above_")
        return base, "above", agg
    if "_below_" in m:
        base, agg = m.split("_below_")
        return base, "below", agg
    if m in ("mean", "median", "max"):
        return m, "above", m
    raise ValueError(f"Unknown method: {m}")

# ==========================================================
# 閾値セット取得
# ----------------------------------------------------------
# buy_method_ma（買いMA判定のメソッド: 乖離率の作り方）
# buy_method_prev（買い指値の乖離率メソッド）
# sell_method_ma（売りMA判定メソッド）
# sell_method_prev（売り指値の乖離率メソッド）
# ==========================================================
def get_thresholds(buy_returns, sell_returns,
                   buy_method_ma, buy_method_prev, sell_method_ma, sell_method_prev):
    b_base_ma, b_dir_ma, b_agg_ma = parse_method(buy_method_ma)
    b_base_pr, b_dir_pr, b_agg_pr = parse_method(buy_method_prev)
    s_base_ma, s_dir_ma, s_agg_ma = parse_method(sell_method_ma)
    s_base_pr, s_dir_pr, s_agg_pr = parse_method(sell_method_prev)

    return (
        compute_threshold(buy_returns, b_base_ma, b_dir_ma, b_agg_ma),  # buy_thresh_ma（買いMAトリガー乖離率）
        compute_threshold(buy_returns, b_base_pr, b_dir_pr, b_agg_pr),  # buy_thresh_prev（買い指値の乖離率）
        compute_threshold(sell_returns, s_base_ma, s_dir_ma, s_agg_ma),  # sell_thresh_ma（売りMAトリガー乖離率）
        compute_threshold(sell_returns, s_base_pr, s_dir_pr, s_agg_pr)  # sell_thresh_prev（売り指値の乖離率）
    )

# ==========================================================
# バックテスト本体（単利・指値完結・1日内完結 / 強制決済なし）
# ----------------------------------------------------------
# mode: "simple"（全売買: ポジション固定） or
#       "range"（30日レンジでポジション動的スケーリング）
# ma_period（移動平均期間）
# lookback（閾値計算期間）
# trade_amount（1トレード基本金額）
# range_days（レンジ計算日数）、max_lot/min_lot（逆張りスケーリング上限/下限）
# ==========================================================
def backtest_full_strategy_repeat(
    df,
    ma_period, lookback,
    buy_method_ma, buy_method_prev, sell_method_ma, sell_method_prev,
    mode="range",
    initial_cash=100000, trade_amount=10000,
    range_days=30, max_lot=1.0, min_lot=0.2
):
    # 前提列: "終値", "高値", "安値"
    dat = df.copy()
    dat["MA"] = dat["終値"].rolling(ma_period).mean()
    dat = dat.dropna(subset=["MA", "終値", "高値", "安値"]).copy()

    total_profit = 0.0                       # 総利益（JPYなど）
    trade_count = 0                          # トレード回数（約定→利確まで成立した件数）
    trade_profits_pct = []                   # 各トレードの利益率（%）
    equity_curve = []                        # 評価額推移（単利のため initial_cash + total_profit）

    start_idx = max(lookback, range_days if mode == "range" else 0)

    for i in range(start_idx, len(dat)):
        # --- 直近の変動率系列（買い=安値、売り=高値で同様に算出）---
        buy_returns = dat["安値"].iloc[i - lookback:i].pct_change().dropna().values
        sell_returns = dat["高値"].iloc[i - lookback:i].pct_change().dropna().values
        buy_thresh_ma, buy_thresh_prev, sell_thresh_ma, sell_thresh_prev = get_thresholds(
            buy_returns, sell_returns,
            buy_method_ma, buy_method_prev,
            sell_method_ma, sell_method_prev
        )

        # --- 本日のデータ ---
        ma_val = dat["MA"].iloc[i]                  # MA現在値
        prev_close = dat["終値"].iloc[i - 1]        # 現在価格（前日終値を基準）
        day_low = dat["安値"].iloc[i]               # 当日安値
        day_high = dat["高値"].iloc[i]              # 当日高値

        # --- ポジション金額（modeで分岐）---
        # trade_amount_dynamic（この日の発注金額）
        if mode == "range":
            # 30日レンジの位置％を用いて逆張りスケーリング
            hi_n = dat["高値"].iloc[i - range_days:i].max()
            lo_n = dat["安値"].iloc[i - range_days:i].min()
            if hi_n == lo_n:
                pos_scale = 1.0
            else:
                position_pct = (prev_close - lo_n) / (hi_n - lo_n)  # 0=レンジ安値, 1=レンジ高値
                # 逆張り: 安値に近いほど大きく（max_lot）、高値に近いほど小さく（min_lot）
                pos_scale = max_lot - (max_lot - min_lot) * position_pct
            trade_amount_dynamic = trade_amount * float(np.clip(pos_scale, min_lot, max_lot))
        else:
            # simple: 常に固定金額
            trade_amount_dynamic = float(trade_amount)

        # --- トリガー判定（逆張り）---
        # 買いトリガー: prev_close <= MA * (1 - buy_thresh_ma)
        # 売りトリガー: prev_close >= MA * (1 + sell_thresh_ma)
        buy_trigger = prev_close <= ma_val * (1 - abs(buy_thresh_ma))
        sell_trigger = prev_close >= ma_val * (1 + abs(sell_thresh_ma))

        # ======================================================
        # 買いロジック（buy_price と sell_target は current=prev_close 基準）
        # ------------------------------------------------------
        # buy_price = prev_close * (1 - buy_thresh_prev)   （買い指値の価格）
        # sell_target = prev_close * (1 + sell_thresh_prev)（利確指値の価格）
        # 当日の足で「安値≦買い指値」かつ「高値≧利確指値」なら同日完結とみなす
        # ※ 強制決済なし（未達成はノートレード扱い）
        # ======================================================
        if buy_trigger:
            buy_price = prev_close * (1 - abs(buy_thresh_prev))      # buy_price（買い指値の価格）
            sell_target = prev_close * (1 + abs(sell_thresh_prev))   # sell_target（売り指値の価格）
            if (day_low <= buy_price) and (day_high >= sell_target):
                profit_pct = (sell_target - buy_price) / buy_price * 100.0  # profit_pct（トレード利益率%）
                total_profit += trade_amount_dynamic * (profit_pct / 100.0)
                trade_profits_pct.append(profit_pct)
                trade_count += 1

        # ======================================================
        # 売りロジック（sell_price と buy_back は current=prev_close 基準）
        # ------------------------------------------------------
        # sell_price = prev_close * (1 + sell_thresh_prev)（売り指値の価格）
        # buy_back   = prev_close * (1 - buy_thresh_prev)（買戻し指値の価格）
        # 当日の足で「高値≧売り指値」かつ「安値≦買戻し指値」なら同日完結
        # ======================================================
        elif sell_trigger:
            sell_price = prev_close * (1 + abs(sell_thresh_prev))    # sell_price（売り指値の価格）
            buy_back = prev_close * (1 - abs(buy_thresh_prev))       # buy_back（買戻し指値の価格）
            if (day_high >= sell_price) and (day_low <= buy_back):
                # ショートの利益率は（売値 - 買戻し）/ 売値
                profit_pct = (sell_price - buy_back) / sell_price * 100.0
                total_profit += trade_amount_dynamic * (profit_pct / 100.0)
                trade_profits_pct.append(profit_pct)
                trade_count += 1

        # --- 評価額の推移（単利）---
        equity_curve.append(initial_cash + total_profit)

    # --- 集計 ---
    if len(equity_curve) == 0:
        return {
            "final_value": initial_cash,
            "profit_percent": 0.0,
            "max_drawdown": 0.0,
            "trade_count": 0,
            "avg_trade_profit": 0.0
        }

    eq = np.asarray(equity_curve, dtype=float)
    cummax = np.maximum.accumulate(eq)
    dd = (cummax - eq) / cummax
    max_dd = float(dd.max()) if dd.size else 0.0

    result = {
        "final_value": float(initial_cash + total_profit),
        "profit_percent": float((total_profit / initial_cash) * 100.0),
        "max_drawdown": float(max_dd * 100.0),
        "trade_count": int(trade_count),
        "avg_trade_profit": float(np.mean(trade_profits_pct) if trade_profits_pct else 0.0),
    }
    return result
