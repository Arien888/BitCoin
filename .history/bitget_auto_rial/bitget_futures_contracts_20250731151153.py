import requests
import pandas as pd

def fetch_bitget_futures_contracts(product_type="USDT-FUTURES"):
    url = "https://api.bitget.com/api/v2/mix/market/contracts"
    params = {"productType": product_type}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json().get("data", [])

def save_to_excel(contracts, filename="bitget_futures_contracts.xlsx"):
    rows = []
    for c in contracts:
        rows.append({
            "symbol": c.get("symbol"),
            "baseCoin": c.get("baseCoin"),
            "quoteCoin": c.get("quoteCoin"),
            "symbolType": c.get("symbolType"),
            "minTradeNum": c.get("minTradeNum"),
            "minTradeUSDT": c.get("minTradeUSDT"),
            "sizeMultiplier": c.get("sizeMultiplier"),
            "pricePlace": c.get("pricePlace"),
            "volumePlace": c.get("volumePlace"),
        })
    df = pd.DataFrame(rows)
    df.to_excel(filename, index=False)
    print("✅ 保存完了:", filename)

if __name__ == "__main__":
    data = fetch_bitget_futures_contracts()
    save_to_excel(data)
