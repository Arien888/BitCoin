import requests

url = "https://api.bitget.com/api/v2/mix/market/tickers"
params = {"productType": "UMCBL"}  # 大文字で試す
response = requests.get(url, params=params)
print(response.json())

