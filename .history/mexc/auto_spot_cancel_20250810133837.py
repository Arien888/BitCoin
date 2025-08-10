import os, yaml, ccxt, time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "config.yaml"))

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

mexc = ccxt.mexc({
    "apiKey": config["mexc"]["api_key"],
    "secret": config["mexc"]["api_secret"],
    "enableRateLimit": True,
})

markets = mexc.load_markets()
spot_symbols = [s for s, m in markets.items() if m['spot']]

for symbol in spot_symbols:
    try:
        orders = mexc.fetch_open_orders(symbol)
        if not orders:
            continue
        for o in orders:
            try:
                mexc.cancel_order(o['id'], symbol)
                print(f"Cancelled {o['id']} @ {symbol}")
                time.sleep(0.1)
            except Exception as e:
                print(f"Cancel failed {o['id']} @ {symbol}: {e}")
    except Exception as e:
        print(f"Fetch failed @ {symbol}: {e}")
