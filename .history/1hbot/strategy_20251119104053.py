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

    return df.dropna().reset_index(drop=True)


def decide_signal(df: pd.DataFrame, params: dict, has_position: bool, entry_price: float | None):
    """
    戻り値: "BUY" / "SELL" / "HOLD"
    """

    # 固定した最強BUY条件の値
    range_pos_thr = params.get("low_thr", 0.40)     # default 0.40
    high_thr = params.get("high_thr", 0.80)         # 利確や反発検知に使う

    tp_pct = params["tp_pct"]
    sl_pct = params["sl_pct"]

    last = df.iloc[-1]

    # ===== SELL条件 =====
    if has_position and entry_price is not None:

        hit_tp = last["high"] >= entry_price * (1.0 + tp_pct)
        hit_sl = last["low"] <= entry_price * (1.0 - sl_pct)
        range_top = last["range_pos"] > high_thr

        if hit_tp or hit_sl or range_top:
            return "SELL"

        return "HOLD"

    # ===== BUY条件（最強版）=====
    buy_signal = (
        (not has_position)
        and (last["range_pos"] < range_pos_thr)     # ★ 最適化された条件
        and (not last["prev_dir_up"])               # ★ 陰線のあと
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
