import requests
import datetime as dt

symbols = [
    "btc_jpy",
    "eth_jpy",
    "xrp_jpy",
]

now = dt.datetime.now()
prices = []

for symbol in symbols:
    url = f"https://public.bitbank.cc/{symbol}/ticker"
    try:
        response = requests.get(url)
        res_json = response.json()
        if res_json.get("success", False):
            last_price = float(res_json["data"]["last"])
            prices.append((symbol.upper(), last_price))
        else:
            print(f"APIエラー: {symbol} - {res_json}")
    except Exception as e:
        print(f"取得失敗: {symbol} - {e}")

print(f"=== {now} 現在価格 ===")
for sym, price in prices:
    print(f"{sym}: {price}")
