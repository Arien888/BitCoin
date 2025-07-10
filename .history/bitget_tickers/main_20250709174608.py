import requests

url = "https://api.bitget.com/api/v2/mix/market/tickers?productType=UMCBL"
response = requests.get(url)
print(response.status_code)
print(response.text)
