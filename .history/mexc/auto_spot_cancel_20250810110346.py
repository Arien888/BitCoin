import os
import yaml
import ccxt

# 設定ファイルのパスを組み立て
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "config.yaml"))

# config.yaml 読み込み
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

api_key = config["mexc"]["api_key"]
secret = config["mexc"]["api_secret"]

# MEXC クライアント作成
mexc = ccxt.mexc({
    "apiKey": api_key,
    "secret": secret
})

def cancel_all_open_orders(symbol):
    """指定シンボルの未約定注文を全てキャンセル"""
    try:
        open_orders = mexc.fetch_open_orders(symbol)
        print(f"{len(open_orders)} 件の未約定注文を取得しました（{symbol}）")
        for order in open_orders:
            try:
                mexc.cancel_order(order['id'], symbol)
                print(f"キャンセル成功: 注文ID {order['id']}")
            except Exception as e:
                print(f"キャンセル失敗: 注文ID {order['id']} エラー: {e}")
    except Exception as e:
        print(f"未約定注文の取得に失敗: {e}")

# --- 実行例 ---
symbol = "DOGE/USDT"
cancel_all_open_orders(symbol)
