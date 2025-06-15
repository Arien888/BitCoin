import yaml
import pandas as pd
import time
from bitget.rest import RestClient

# 設定読み込み
with open("../config.yaml", "r") as f:
    config = yaml.safe_load(f)

# APIクライアント初期化
client = RestClient(
    api_key=config["apiKey"],
    api_secret=config["secret"],
    passphrase=config["passphrase"],
)

# 注文データ読み込み
df = pd.read_excel("orders.xlsx")

for i, row in df.iterrows():
    symbol = row["symbol"]
    price = str(row["price"])
    size = str(row["amount"])
    side = row["side"].lower()  # 'buy' or 'sell'

    try:
        res = client.place_order(
            symbol=symbol,
            marginCoin="USDT",  # ここは固定 or 変えたいなら変えてOK
            size=size,
            price=price,
            side=side,
            orderType="limit",
            timeInForceValue="normal",
        )
        print(f"注文成功: {symbol} {side} {price} x {size}")
    except Exception as e:
        print(f"注文失敗: {symbol} - {e}")

    time.sleep(1)  # API制限に注意して1秒あける
