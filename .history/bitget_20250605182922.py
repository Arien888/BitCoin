import time
import hmac
import hashlib
import requests
import yaml


# 設定を読み込む
def load_config(path="config.yaml"):
    with open(path, "r") as file:
        return yaml.safe_load(file)


config = load_config()
API_KEY = config["bitget"]["api_key"]
API_SECRET = config["bitget"]["api_secret"]
API_PASSPHRASE = config["bitget"]["passphrase"]
BASE_URL = "https://api.bitget.com"


# タイムスタンプ生成
def get_timestamp():
    return str(int(time.time() * 1000))
