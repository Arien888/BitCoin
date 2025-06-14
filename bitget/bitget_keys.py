# bitget_keys.py

spot_keys = [
    "coin", "available", "limitAvailable", "frozen", "locked", "uTime"
]

margin_keys = [
    "coin", "totalAmount", "available", "frozen", "borrow", "interest",
    "net", "coupon", "cTime", "uTime"
]

earn_keys = ["coin", "amount"]

futures_keys = [
    "coin", "equity", "available", "locked", "unrealizedPL",
    "initialMargin", "maintMargin", "marginRatio",
    "marginBalance", "maxWithdrawAmount"
]

futures_position_keys = [
    "symbol", "holdSide", "available", "locked", "total", "leverage",
    "achievedProfits", "openPriceAvg", "marginMode", "posMode",
    "unrealizedPL", "liquidationPrice", "keepMarginRate", "markPrice",
    "marginRatio", "breakEvenPrice", "totalFee", "takeProfit", "stopLoss",
    "takeProfitId", "stopLossId", "deductedFee", "cTime", "uTime"
]
