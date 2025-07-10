import requests
import csv

def get_ticker_list_v2():
    url = "https://api.bitget.com/api/v2/mix/market/tickers"
    resp = requests.get(url)
    data = resp.json()

    if data.get("code") != "00000":
        print("API取得失敗:", data)
        return []

    return [item["symbol"] for item in data.get("data", []) if "symbol" in item]

def save_tickers_to_csv(tickers, filename="bitget_tickers_v2.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["symbol"])
        for t in tickers:
            w.writerow([t])
    print(f"✅ CSV出力完了: {filename}")

if __name__ == "__main__":
    tickers = get_ticker_list_v2()
    print("取得したティッカー数:", len(tickers))
    save_tickers_to_csv(tickers)
