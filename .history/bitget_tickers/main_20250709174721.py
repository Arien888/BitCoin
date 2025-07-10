import requests

def test_bitget_tickers():
    url = "https://api.bitget.com/api/v2/mix/market/tickers"
    params = {"productType": "UMCBL"}
    response = requests.get(url, params=params)
    print("HTTPステータスコード:", response.status_code)
    print("レスポンスJSON:", response.json())

if __name__ == "__main__":
    test_bitget_tickers()
