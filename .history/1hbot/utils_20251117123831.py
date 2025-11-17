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
