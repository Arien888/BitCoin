import requests

def get_spot_products():
    url = "https://api.bitget.com/api/spot/v1/public/products"
    res = requests.get(url)
    print("レスポンスJSON:", res.json())
    return res.json()

def main():
    spot_products = get_spot_products()
    if spot_products.get("code") == "00000":
        for product in spot_products.get("data", []):
            print(product["symbol"], "priceScale:", product.get("priceScale"))
    else:
        print("API取得失敗:", spot_products.get("msg"))

if __name__ == "__main__":
    main()
