import os
import yaml
import ccxt
import pandas as pd
from mexc_utils import save_positions_and_spot_to_excel  # 外部関数

# ─────────────────────────────────────
# config.yaml の読み込み（1つ上の階層）
# ─────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "config.yaml"))

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

api_key = config["mexc"]["apiKey"]
secret = config["mexc"]["secret"]
save_path = config["paths"]["asset_excel"]

# ─────────────────────────────────────
# CCXTインスタンスの準備
# ─────────────────────────────────────
exchange_spot = ccxt.mexc({
    "apiKey": api_key,
    "secret": secret,
    "enableRateLimit": True,
    "options": {"defaultType": "spot"},
})

exchange_swap = ccxt.mexc({
    "apiKey": api_key,
    "secret": secret,
    "enableRateLimit": True,
    "options": {"defaultType": "swap"},
})

# ─────────────────────────────────────
# 注文データ（ここで必要に応じて変更）
# ─────────────────────────────────────
# 例：現物で BTC/USDT を 0.001 BTC 買い注文（成行）
symbol = "BTC/USDT"
order_type = "market"   # "limit" または "market"
side = "buy"            # "buy" または "sell"
amount = 0.001
price = None            # 成行注文では price=None、指値なら指定

# ─────────────────────────────────────
# 実行ブロック
# ─────────────────────────────────────
try:
    # --- 発注 ---
    order = exchange_spot.create_order(
        symbol=symbol,
        type=order_type,
        side=side,
        amount=amount,
        price=price,  # 成行なら None、limit なら float
    )
    print(f"✅ 発注成功: {order}")

    # --- データ取得 ---
    positions = exchange_swap.fetch_positions()
    df_positions = pd.DataFrame(positions)

    balance = exchange_spot.fetch_balance()
    spot_balances = {k: v for k, v in balance["total"].items() if v and v > 0}
    df_spot = pd.DataFrame(spot_balances.items(), columns=["通貨", "保有量"])

    # --- 保存処理 ---
    save_positions_and_spot_to_excel(df_positions, df_spot, save_path)
    print(f"📊 データ保存完了: {save_path}")

except Exception as e:
    print(f"❌ エラー発生: {e}")
