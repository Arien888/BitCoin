import requests

# 取得設定
symbol = "BTCUSDT"  # 通貨ペア
interval = "1h"     # 時間足
limit = 10          # 本数（最大1000）

# Binance APIエンドポイント
url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"

# データ取得
response = requests.get(url)
data = response.json()

# 表示
print("時間, 始値, 高値, 安値, 終値, 出来高")
for candle in data:
    open_time = candle[0]
    open_price = candle[1]
    high_price = candle[2]
    low_price = candle[3]
    close_price = candle[4]
    volume = candle[5]
    print(open_time, open_price, high_price, low_price, close_price, volume)

