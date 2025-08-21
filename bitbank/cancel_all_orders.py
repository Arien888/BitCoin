import os
import yaml
import ccxt

# --- 設定ファイルのパス ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "config.yaml"))

# --- config.yaml 読み込み ---
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# --- Bitbank APIキーとシークレット取得 ---
api_key = config["bitbank"]["api_key"]
secret = config["bitbank"]["api_secret"]

# --- Bitbank クライアント作成 ---
bitbank = ccxt.bitbank({
    "apiKey": api_key,
    "secret": secret,
})

def cancel_all_orders():
    try:
        markets = bitbank.load_markets()
        for symbol in markets.keys():
            try:
                open_orders = bitbank.fetch_open_orders(symbol)
                if not open_orders:
                    continue
                for order in open_orders:
                    try:
                        bitbank.cancel_order(order["id"], symbol)
                        print(f"✅ キャンセル成功: {symbol} {order['id']}")
                    except Exception as e:
                        print(f"⚠ キャンセル失敗: {symbol} {order['id']} → {e}")
            except Exception as e:
                # このシンボルはオープン注文が取得できない場合
                print(f"⚠ {symbol} の注文取得エラー: {e}")
    except Exception as e:
        print("❌ 全注文キャンセル処理エラー:", e)

if __name__ == "__main__":
    cancel_all_orders()
