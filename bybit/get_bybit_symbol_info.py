import requests
import pandas as pd

def fetch_all_precision(category="linear"):
    url = "https://api.bybit.com/v5/market/instruments-info"
    params = {"category": category}
    res = requests.get(url, params=params)
    data = res.json()
    if "result" not in data or "list" not in data["result"]:
        return []
    return data["result"]["list"]

def get_symbols_info(target_symbols, category="linear"):
    all_items = fetch_all_precision(category)
    target_symbols = [s.lower() for s in target_symbols]
    rows = []
    for item in all_items:
        sym = item["symbol"].lower()
        if sym in target_symbols:
            rows.append({
                "symbol": item["symbol"],
                "min_qty": float(item["lotSizeFilter"]["minOrderQty"]),
                "qty_step": float(item["lotSizeFilter"]["qtyStep"]),
                "tick_size": float(item["priceFilter"]["tickSize"]),
            })
    return rows

if __name__ == "__main__":
    # ユーザー指定銘柄（USDTペアにする）
    base_symbols = [
        "doge","sol","dot","avax","eth","trx","btc","bnb","ada","pepe","shib","link",
        "xrp","sui","ltc","etc","hbar","xlm","bch","aave","usdt","weeth","xmr","susde",
        "bgb","uni","ton","near","leo","apt","icp","wbt","tao","ondo","cro","okb","pi",
        "jitosol","xrpjpy","trxjpy","tkx","ltcjpy","kas","dotjpy","buidl","avaxjpy"
    ]
    
    # USDTペア化（小文字で）
    target_symbols = [s.lower() + "usdt" for s in base_symbols if not s.lower().endswith("jpy")]
    
    # JPYn銘柄はAPIに存在しない可能性が高いので除外
    # もし必要ならAPIに存在するか別途チェックが必要

    results = get_symbols_info(target_symbols)
    df = pd.DataFrame(results)
    
    # Excelに書き込み
    output_file = "bybit_target_symbols_precision.xlsx"
    df.to_excel(output_file, index=False)
    
    print(f"取得件数: {len(df)} 件")
    print(f"ファイルを出力しました: {output_file}")
