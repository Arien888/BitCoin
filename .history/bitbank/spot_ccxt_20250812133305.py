import ccxt

# APIキー・シークレットを設定
api_key = 'YOUR_API_KEY'
api_secret = 'YOUR_SECRET'

exchange = ccxt.bitbank({
    'apiKey': api_key,
    'secret': api_secret,
})

# 残高取得
balance = exchange.fetch_balance()
print(balance)

# 買い注文（例：BTC/JPYの現物を0.001BTC購入）
symbol = 'btc/jpy'
order = exchange.create_market_buy_order(symbol, 0.001)
print(order)

# 売り注文（例：BTC/JPYを0.001BTC売る）
order = exchange.create_market_sell_order(symbol, 0.001)
print(order)
