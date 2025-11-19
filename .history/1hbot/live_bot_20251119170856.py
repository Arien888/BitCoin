from utils import (
    load_config,
    calc_order_size,
    append_trade_log,
    write_runtime_log,   # ★ 追加
    write_trade_log,     # ★ 追加
    write_error_log      # ★ 追加
)

from bitget_api import get_current_position, place_order
from data_fetch import fetch_1h_candles, compute_indicators
from strategy import decide_signal


# デバッグ用フラグ（行数や先頭・末尾表示したいとき True）
DEBUG_PRINT_DF = True


def main():
    try:
        write_runtime_log("=== BOT START ===")
        print("=== CONFIG PATH TEST ===")
        cfg = load_config()
        print("BASE_URL:", cfg["bitget"]["base_url"])

        print("=== 1h BTCUSDT BOT (MA+Range+Prev) ===")
        print("mode.dry_run =", cfg["mode"]["dry_run"])

        # 1) データ取得
        df = fetch_1h_candles(cfg, limit=200)

        if df is None or len(df) == 0:
            print("ERROR: 足データが取得できませんでした")
            return

        if DEBUG_PRINT_DF:
            print("FETCH DF ROWS:", len(df))
            print(df.head())
            print(df.tail())

        df = compute_indicators(df, cfg["strategy"])

        if df is None or len(df) == 0:
            print("ERROR: インジケータ計算後の df が空です")
            return

        if DEBUG_PRINT_DF:
            print("AFTER INDICATORS:", len(df))

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
        write_runtime_log(f"close={last['close']} | signal={signal} | pos={has_pos}")

        if signal == "BUY" and not has_pos:

            size = calc_order_size(cfg, last["close"])     # ← 先に size 定義

            write_runtime_log(f"BUY signal | size={size} | price={last['close']}")
            write_trade_log("open_long", size, last["close"], "DRY_RUN" if cfg["mode"]["dry_run"] else "ORDER")
            print(f"[SIGNAL] BUY size={size}")



    except Exception as e:
        write_error_log(str(e))
        print("ERROR:", e)

if __name__ == "__main__":
    main()
