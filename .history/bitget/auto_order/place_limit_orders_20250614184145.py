import yaml
import pandas as pd
from bitget import BitgetApi
from time import sleep

# API情報の読み込み
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)["bitget"]

# APIクライアントの初期化
client = bitget(
    api_key=config["apiKey"],
    api_secret=config["secret"],
    passphrase=config["passphrase"],
)

# 注文データ読み込み
df = pd.read_excel("orders.xlsx")

# 指値注文ループ
for _, row in df.iterrows():
    try:
        symbol = row["symbol"]
        price = str(row["price"])
        size = str(row["amount"])

        response = client.order.place_order(
            symbol=symbol,
            marginCoin="USDT",
            size=size,
            price=price,
            side="buy",  # 必要に応じて "sell"
            orderType="limit",
            timeInForceValue="normal",
        )
        print(f"✅ 注文成功: {symbol} @ {price} x {size}")
        sleep(1)

    except Exception as e:
        print(f"❌ 注文失敗: {row['symbol']} - {e}")
