import requests

# 例：資産情報取得
def get_assets(api_key, api_secret, api_passphrase, path):
    # 認証処理を含むリクエスト送信（省略）
    # ここでは認証不要の公開API想定で簡略化
    url = f"https://api.bitget.com{path}"
    response = requests.get(url)
    return response.json()

# 取引ペア詳細取得（スポット例）
def get_spot_products():
    url = "https://api.bitget.com/api/spot/v1/public/products"
    res = requests.get(url)
    return res.json()

# 取引ペア詳細取得（永続契約例）
def get_mix_contracts():
    url = "https://api.bitget.com/api/mix/v1/market/contracts"
    res = requests.get(url)
    return res.json()

def main():
    # 1. 資産取得
    spot_assets = get_assets(None, None, None, "/api/v2/spot/account/assets")
    # 2. 保有銘柄シンボル抽出
    symbols = [asset["coin"] for asset in spot_assets.get("data", [])]

    # 3. 銘柄詳細取得
    spot_products = get_spot_products()
    product_map = {}
    if spot_products.get("code") == "00000":
        for product in spot_products.get("data", []):
            product_map[product["symbol"]] = product

    # 4. 保有資産×詳細情報を結合
    for symbol in symbols:
        detail = product_map.get(symbol)
        if detail:
            print(symbol, "priceScale:", detail.get("priceScale"), "quantityScale:", detail.get("quantityScale"))
        else:
            print(symbol, "の詳細情報なし")

if __name__ == "__main__":
    main()
