import os
import yaml
import ccxt
import time

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
    "secret": secret,
    "enableRateLimit": True,  # レート制限対策
})

def cancel_all_open_orders_for_all_symbols():
    try:
        # 全マーケット取得
        markets = mexc.load_markets()
        print(f"全マーケット数: {len(markets)}")

        # スポット（現物）市場のシンボルだけ抽出
        spot_symbols = [symbol for symbol, market in markets.items() if market['spot']]
        print(f"スポットマーケット数: {len(spot_symbols)}")

        # 各シンボルの未約定注文をキャンセル
        for symbol in spot_symbols:
            try:
                open_orders = mexc.fetch_open_orders(symbol)
                if not open_orders:
                    continue
                print(f"{symbol} の未約定注文 {len(open_orders)} 件をキャンセルします")
                for order in open_orders:
                    try:
                        mexc.cancel_order(order['id'], symbol)
                        print(f"キャンセル成功: 注文ID {order['id']} シンボル {symbol}")
                        time.sleep(0.2)  # APIレート制限対策にスリープ
                    except Exception as e:
                        print(f"キャンセル失敗: 注文ID {order['id']} シンボル {symbol} エラー: {e}")
            except Exception as e:
                print(f"{symbol} の未約定注文取得失敗: {e}")

    except Exception as e:
        print(f"マーケット取得失敗: {e}")

# 実行
cancel_all_open_orders_for_all_symbols()
