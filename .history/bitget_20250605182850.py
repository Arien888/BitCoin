import time
import hmac
import hashlib
import requests
import yaml


# 設定を読み込む
def load_config(path="config.yaml"):
    with open(path, "r") as file:
        return yaml.safe_load(file)

