import requests
import csv

def get_ticker_list_v2():
    url = "https://api.bitget.com/api/v2/mix/market/tickers"
    params = {
        "productType": "umcbl"  # ← ここは文字列で、キーが "productType"
    }
    response = requests.get(url, params=params)
    data = response.json()

    if data.get("code") != "00000":
        print("API取得失敗:", data)
        return []

    return [item["symbol"] for item in data.get("data", []) if "symbol" in item]

def save_tickers_to_csv(tickers, filename="bitget_tickers_v2.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["symbol"])
        for t in tickers:
            writer.writerow([t])
    print(f"✅ CSV出力完了: {filename}")

if __name__ == "__main__":
    tickers = get_ticker_list_v2()
    print("取得したティッカー数:", len(tickers))
    for t in tickers:
        print(t)
    save_tickers_to_csv(tickers)
