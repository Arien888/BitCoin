from utils import load_config
from bitget_api import get_current_position, place_order
from data_fetch import fetch_1h_candles
from data_fetch import compute_indicators

from strategy import decide_signal
from utils import calc_order_size, append_trade_log
from data_fetch import fetch_1h_candles, compute_indicators

def main():
    print("=== CONFIG PATH TEST ===")
    cfg = load_config()
    print("BASE_URL:", cfg["bitget"]["base_url"])

    print("=== 1h BTCUSDT_UMCBL BOT (MA+Range+Prev) ===")
    print("mode.dry_run =", cfg["mode"]["dry_run"])

    # 1) データ取得
    df = fetch_1h_candles(cfg, limit=300)
    df = compute_indicators(df, cfg["strategy"])

    # 2) 現在のポジション確認
    if cfg["mode"]["dry_run"]:
        # 本番キー不要、常にノーポジとして扱う
        has_pos = False
        entry_price = None
    else:
        has_pos, entry_price = get_current_position(cfg)
        
    print("has_position:", has_pos, "entry_price:", entry_price)

    # 3) シグナル判定
    last = df.iloc[-1]
    signal = decide_signal(df, cfg["strategy"], has_pos, entry_price)
    print("last_close:", last["close"], "signal:", signal)

    # 4) シグナルに応じて注文 or 何もしない
    if signal == "BUY" and not has_pos:
        size = calc_order_size(cfg, last["close"])
        print(f"[SIGNAL] BUY size={size}")

        if cfg["mode"]["dry_run"]:
            print("DRY RUN → 注文は出さずログのみ")
            append_trade_log("DRY_RUN", "open_long", size, last["close"])
        else:
            res = place_order(cfg, "open_long", size)
            print("ORDER RESPONSE:", res)
            append_trade_log("ORDER", "open_long", size, last["close"])

    elif signal == "SELL" and has_pos:
        size = calc_order_size(cfg, last["close"])
        print(f"[SIGNAL] SELL size={size}")

        if cfg["mode"]["dry_run"]:
            print("DRY RUN → 決済せずログのみ")
            append_trade_log("DRY_RUN", "close_long", size, last["close"])
        else:
            res = place_order(cfg, "close_long", size)
            print("ORDER RESPONSE:", res)
            append_trade_log("ORDER", "close_long", size, last["close"])

    df = fetch_1h_candles(cfg, limit=300)
    print("FETCH DF ROWS:", len(df))
    print(df.head())
    print(df.tail())
    df = compute_indicators(df, cfg["strategy"])
    print("AFTER INDICATORS:", len(df))



if __name__ == "__main__":
    main()
