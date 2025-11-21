# strategy.py
import os
from datetime import datetime
import pandas as pd


def compute_indicators(df: pd.DataFrame, params: dict) -> pd.DataFrame:
    range_lb = params["range_lb"]
    ma_period = params.get("ma_period", 12)

    # --- MA（逆張り判断） ---
    df[f"ma{ma_period}"] = df["close"].rolling(ma_period).mean()

    # --- Range（位置判定） ---
    df["range_high"] = df["high"].rolling(range_lb).max()
    df["range_low"]  = df["low"].rolling(range_lb).min()

    rng = df["range_high"] - df["range_low"]
    df["range_pos"] = (df["close"] - df["range_low"]) / (rng.replace(0, 1e-9))

    # ===== 下ヒゲ判定（陽線と陰線で正確に計算） =====
    # 下ヒゲ = ローソクの下端（min(open,close)) から low まで
    lower_end = df[["open", "close"]].min(axis=1)
    df["lower_wick"] = lower_end - df["low"]

    df["range_total"] = (df["high"] - df["low"]).replace(0, 1e-9)
    df["wick_ratio"] = df["lower_wick"] / df["range_total"]

    # 前の足
    df["prev_close"] = df["close"].shift(1)
    df["prev_dir_up"] = df["close"] > df["prev_close"]

    return df.dropna().reset_index(drop=True)



def decide_signal(df: pd.DataFrame, params: dict, has_position: bool, entry_price: float | None):

    low_thr  = params.get("low_thr", 0.30)
    high_thr = params.get("high_thr", 0.70)
    wick_thr = params.get("wick_thr", 0.55)
    ma_dc    = params.get("entry_ma_dc", 0.02)

    tp_pct   = params["tp_pct"]
    sl_pct   = params["sl_pct"]
    ma_period = params.get("ma_period", 12)

    last = df.iloc[-1]
    ma_value = last[f"ma{ma_period}"]

    # =====================================================
    # ① SELL （バックテストと完全一致）
    # =====================================================
    if has_position and entry_price is not None:

        tp_price = entry_price * (1 + tp_pct)
        sl_price = entry_price * (1 - sl_pct)

        # ひげ判定で TP / SL チェックする
        hit_tp  = last["high"] >= tp_price
        hit_sl  = last["low"]  <= sl_price
        hit_top = last["range_pos"] > high_thr

        if hit_tp:
            return "SELL"
        if hit_sl:
            return "SELL"
        if hit_top:
            return "SELL"

        return "HOLD"


    # =====================================================
    # ② BUY（最強版）
    # =====================================================

    cond_range = last["range_pos"] < low_thr
    cond_wick  = last["wick_ratio"] > wick_thr
    cond_ma    = last["close"] < ma_value * (1 - ma_dc)
    cond_dir   = (not last["prev_dir_up"])

    buy_signal = (
        (not has_position)
        and cond_range
        and cond_wick
        and cond_ma
        and cond_dir
    )

    if buy_signal:
        return "BUY"

    return "HOLD"



def calc_order_size(cfg: dict, last_price: float) -> float:
    usdt = cfg["trade"]["order_size_usdt"]
    size = usdt / last_price
    return round(size, 4)



def append_trade_log(action: str, side: str, size: float, price: float, extra: str = ""):
    os.makedirs("logs", exist_ok=True)
    path = os.path.join("logs", "trade_log.csv")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = f"{now},{action},{side},{size},{price},{extra}\n"

    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("time,action,side,size,price,extra\n")
            f.write(row)
    else:
        with open(path, "a", encoding="utf-8") as f:
            f.write(row)
