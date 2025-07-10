import requests
import csv

def get_spot_products():
    url = "https://api.bitget.com/api/spot/v1/public/products"
    res = requests.get(url)
    print("レスポンスJSON:", res.json())
    return res.json()

def save_to_csv(products, filename="bitget_spot_products.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # ヘッダー
        writer.writerow(["symbol", "priceScale", "quantityScale"])
        for p in products:
            writer.writerow([p.get("symbol"), p.get("priceScale"), p.get("quantityScale")])
    print(f"✅ CSV出力完了: {filename}")

def main():
    spot_products = get_spot_products()
    if spot_products.get("code") == "00000":
        products = spot_products.get("data", [])
        for product in products:
            print(product["symbol"], "priceScale:", product.get("priceScale"), "quantityScale:", product.get("quantityScale"))
        save_to_csv(products)
    else:
        print("API取得失敗:", spot_products.get("msg"))

if __name__ == "__main__":
    main()
