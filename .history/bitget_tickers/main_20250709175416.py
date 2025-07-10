import requests

url = "https://api.bitget.com/api/mix/v1/market/contracts"
response = requests.get(url)
data = response.json()

if data.get("code") == "00000":
    for contract in data.get("data", []):
        symbol = contract.get("symbol")
        price_scale = contract.get("priceScale")
        quantity_scale = contract.get("quantityScale")
        print(f"銘柄: {symbol}, 価格小数点桁数: {price_scale}, 数量小数点桁数: {quantity_scale}")
else:
    print("API取得失敗:", data)
