import requests
import csv

def get_futures_products():
    url = "https://api.bitget.com/api/mix/v1/market/contracts"
    params = {"productType": "umcbl"}  # USDT無期限契約
    res = requests.get(url, params=params)
    print("レスポンスJSON:", res.json())
    return res.json()

def save_to_csv(products, filename="bitget_futures_products.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # ヘッダー
        writer.writerow(["symbol", "pricePlace", "volumePlace"])
        for p in products:
            writer.writerow([p.get("symbol"), p.get("pricePlace"), p.get("volumePlace")])
    print(f"✅ CSV出力完了: {filename}")

def main():
    futures_products = get_futures_products()
    if futures_products.get("code") == "00000":
        products = futures_products.get("data", [])
        for product in products:
            print(product["symbol"], "pricePlace:", product.get("pricePlace"), "volumePlace:", product.get("volumePlace"))
        save_to_csv(products)
    else:
        print("API取得失敗:", futures_products.get("msg"))

if __name__ == "__main__":
    main()
