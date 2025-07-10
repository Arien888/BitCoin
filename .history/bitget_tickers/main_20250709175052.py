import requests
import csv

def get_ticker_list(product_type, symbols=None):
    url = "https://api.bitget.com/api/v2/mix/market/tickers"
    params = {"productType": product_type}
    if symbols:
        params["symbol"] = ",".join(symbols)
    response = requests.get(url, params=params)
    return response.json()

def save_tickers_to_csv(tickers, filename="bitget_tickers.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["symbol", "lastPrice", "high24h", "low24h", "quoteVolume", "baseVolume"])
        for ticker in tickers:
            writer.writerow([
                ticker.get("symbol"),
                ticker.get("lastPr"),
                ticker.get("high24h"),
                ticker.get("low24h"),
                ticker.get("quoteVolume"),
                ticker.get("baseVolume")
            ])
    print(f"✅ CSV出力完了: {filename}")

if __name__ == "__main__":
    product_type = "umcbl"  # USDT永続契約
    symbols = ["BTCUSDT", "ETHUSDT"]  # 取得したい取引ペア
    response = get_ticker_list(product_type, symbols)
    if response.get("code") == "00000":
        save_tickers_to_csv(response["data"])
    else:
        print(f"API取得失敗: {response.get('msg')}")
