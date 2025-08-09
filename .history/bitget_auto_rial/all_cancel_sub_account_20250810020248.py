import sys
import io
import os
import yaml
import time
from bitget_client import BitgetClient

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# 設定ファイルのパス
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.yaml")

# 設定読み込み
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# BitgetClient インスタンス
client = BitgetClient(
    key=config["bitget"]["api_key"],
    secret=config["bitget"]["api_secret"],
    passphrase=config["bitget"]["passphrase"],
    is_testnet=config["bitget"].get("is_testnet", False)
)
