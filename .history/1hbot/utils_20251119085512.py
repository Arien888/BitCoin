import yaml
import os
from datetime import datetime

def load_config(path="config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def append_trade_log(action, side, size, price, extra=""):
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

# utils.py
import os
from datetime import datetime

# ==============================
# 注文サイズ計算
# ==============================
def calc_order_size(cfg, last_price):
    """
    USDT で何ドル使うか → size = USDT / price
    """
    usdt = cfg["trade"]["order_size_usdt"]
    size = usdt / last_price
    return round(size, 4)  # 小数4桁で十分


# ==============================
# ログ
# ==============================
def append_trade_log(action, side, size, price, extra=""):
    os.makedirs("logs", exist_ok=True)
    path = os.path.join("logs", "trade_log.csv")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = f"{now},{action},{side},{size},{price},{extra}\n"

    # 初回のみヘッダー付ける
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("time,action,side,size,price,extra\n")
            f.write(row)
    else:
        with open(path, "a", encoding="utf-8") as f:
            f.write(row)

# utils.py
def calc_order_size(cfg, last_price):
    """
    USDT指定 → BTC数量に変換
    """
    usdt = cfg["trade"]["order_size_usdt"]

    qty = usdt / last_price

    # Bitget futures BTC 最小注文量は 0.001
    qty = max(0.001, round(qty, 3))

    return qty


LOG_DIR = "log"
os.makedirs(LOG_DIR, exist_ok=True)