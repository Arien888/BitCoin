import yaml
import pandas as pd
import time
from bitget.spot import SpotClient

# config.yamlがスクリプトの一つ上の階層にある場合
with open("../config.yaml", "r") as f:
    config = yaml.safe_load(f)["bitget"]

client = SpotClient(
    api_key=config["apiKey"],
    api_secret=config["secret"],
    passphrase=config["passphrase"]
)

df = pd.read_excel("orders.xlsx")  # スクリプトと同じ階層に orders.xlsx を置く

for _, row in df.iterrows():
    symbol = row["symbol"]
    price = str(row["price"])
    size = str(row["amount"])
    side = row["side"].lower()

    try:
        res = client.place_order(
            symbol=symbol,
            price=price,
            size=size,
            side=side,
            order_type="limit",
            time_in_force="GTC"
        )
        print(f"注文成功: {symbol} {side} {price} x {size}")
    except Exception as e:
        print(f"注文失敗: {symbol} - {e}")

    time.sleep(1)
