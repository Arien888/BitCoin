# strategy.py
import os
from datetime import datetime
import pandas as pd


def compute_indicators(df: pd.DataFrame, params: dict) -> pd.DataFrame:
    """
    最適化で必要な最低限のインジケータだけを計算。
    （MA を使わないなら削除して良い）
    """
    range_lb = params["range_lb"]

    df["range_high"] = df["high"].rolling(range_lb).max()
    df["range_low"] = df["low"].rolling(range_lb).min()
    df["range_pos"] = (df["close"] - df["range_low"]) / (df["range_high"] - df["range_low"])

    df["prev_close"] = df["close"].shift(1)
    df["prev_dir_up"] = df["close"] > df["prev_close"]

    return df.dropna().reset_index(drop=True)


def decide_signal(df: pd.DataFrame, params: dict, has_position: bool, entry_price: float | None):
    """
    BUY / SELL / HOLD を返す。
    バックテスト（high/low 判定）と一致させたロジック。
    """

    # === パラメータ ===
    low_thr  = params.get("low_thr", 0.40)   # BUY条件
    high_thr = params.get("high_thr", 0.80)  # 決済条件（range上部）
    tp_pct   = params["tp_pct"]
    sl_pct   = params["sl_pct"]

    last = df.iloc[-1]

    # =======================================
    # ① 保有ポジションあり → 決済判定
    # =======================================
    if has_position and entry_price is not None:

        tp_price = entry_price * (1 + tp_pct)
        sl_price = entry_price * (1 - sl_pct)

        # ★ バックテストと同じ "ひげ判定"
        hit_tp  = last["high"] >= tp_price
        hit_sl  = last["low"]  <= sl_price

        # ★ range_pos が上部に来たら決済
        hit_top = last["range_pos"] > high_thr

        if hit_tp or hit_sl or hit_top:
            return "SELL"

        return "HOLD"

    # =======================================
    # ② ノーポジ → BUY判定（最適化済みロジック）
    # =======================================
    buy_signal = (
        (not has_position)
        and (last["range_pos"] < low_thr)      # 最適化された条件
        and (not last["prev_dir_up"])          # 前のローソク足が陰線
    )

    if buy_signal:
        return "BUY"

    return "HOLD"


def calc_order_size(cfg: dict, last_price: float) -> float:
    usdt = cfg["trade"]["order_size_usdt"]
    size = usdt / last_price
    return round(size, 4)


def append_trade_log(action: str, side: str, size: float, price: float, extra: str = ""):
    """
    取引ログ保存
    """
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
