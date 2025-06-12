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


# 署名作成（HMAC-SHA256）
def generate_signature(timestamp, method, path, body=""):
    message = timestamp + method.upper() + path + body
    signature = hmac.new(
        API_SECRET.encode(), msg=message.encode(), digestmod=hashlib.sha256
    ).hexdigest()
    return signature


# 資産データ取得（現物）
def get_spot_assets():
    path = "/api/spot/v1/account/assets"
    url = BASE_URL + path
    timestamp = get_timestamp()
    signature = generate_signature(timestamp, "GET", path)

    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": API_PASSPHRASE,
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers)
    return response.json()


# 実行
if __name__ == "__main__":
    data = get_spot_assets()
    if data.get("code") == "00000":
        for asset in data["data"]:
            coin = asset["coin"]
            available = asset["available"]
            frozen = asset["frozen"]
            print(f"{coin}: {available} (frozen: {frozen})")
    else:
        print("取得失敗:", data)
