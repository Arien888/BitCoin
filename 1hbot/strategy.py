# strategy.py
import os
from datetime import datetime

import pandas as pd


def compute_indicators(df: pd.DataFrame, params: dict) -> pd.DataFrame:
    ma_period = params["ma_period"]
    range_lb = params["range_lb"]

    df[f"ma{ma_period}"] = df["close"].rolling(ma_period).mean()
    df["range_high"] = df["high"].rolling(range_lb).max()
    df["range_low"] = df["low"].rolling(range_lb).min()
    df["range_pos"] = (df["close"] - df["range_low"]) / (df["range_high"] - df["range_low"])
    df["prev_close"] = df["close"].shift(1)
    df["prev_dir_up"] = df["close"] > df["prev_close"]

    df = df.dropna().reset_index(drop=True)
    return df


def decide_signal(df: pd.DataFrame, params: dict, has_position: bool, entry_price: float | None):
    """
    戻り値: "BUY" / "SELL" / "HOLD"
    """
    ma_period   = params["ma_period"]
    low_thr     = params["low_thr"]
    high_thr    = params["high_thr"]
    entry_ma_dc = params["entry_ma_dc"]
    tp_pct      = params["tp_pct"]
    sl_pct      = params["sl_pct"]

    last = df.iloc[-1]
    ma_value = last[f"ma{ma_period}"]

    # すでにポジあり → 決済判定
    if has_position and entry_price is not None:
        hit_tp = last["close"] >= entry_price * (1.0 + tp_pct)
        hit_sl = last["close"] <= entry_price * (1.0 - sl_pct)
        ma_cross = last["close"] > ma_value
        range_top = last["range_pos"] > high_thr

        if hit_tp or hit_sl or ma_cross or range_top:
            return "SELL"
        return "HOLD"

    # ノーポジ → エントリー判定
    buy_signal = (
        (not has_position)
        and (last["close"] < ma_value * (1.0 - entry_ma_dc))
        and (last["range_pos"] < low_thr)
        and (last["prev_dir_up"] is False)
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
