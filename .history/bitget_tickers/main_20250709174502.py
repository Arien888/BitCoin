import requests

url = "https://api.bitget.com/api/v2/mix/market/tickers?productType=umcbl"
response = requests.get(url)
print(response.json())
