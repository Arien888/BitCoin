from utils import (
    load_config,
    calc_order_size,
    append_trade_log,
    write_runtime_log,
    write_trade_log,
    write_error_log
)

from bitget_api import get_current_position, place_order
from data_fetch import fetch_1h_candles, compute_indicators
from strategy import decide_signal

import os

DEBUG_PRINT_DF = True


def get_dry_run_position_from_log():
    """
    DRY RUN 用:
    logs/trade_log.csv から最後の open_long / close_long を見て
    仮想ポジション状態 (has_pos, entry_price) を復元する。
    """
    log_dir = "logs"
    log_path = os.path.join(log_dir, "trade_log.csv")

    if not os.path.exists(log_path):
        return False, None  # ログがなければノーポジ

    last_side = None
    last_price = None

    with open(log_path, "r", encoding="utf-8") as f:
        # 1行目ヘッダーをスキップ
        header = f.readline()
        for line in f:
            parts = line.strip().split(",")
            if len(parts) < 6:
                continue
            # time,action,side,size,price,extra
            _, action, side, size, price, extra = parts
            if side in ("open_long", "close_long"):
                last_side = side
                try:
                    last_price = float(price)
                except ValueError:
                    last_price = None

    if last_side == "open_long" and last_price is not None:
        # 最後が open_long → まだクローズされてないロング持ち
        return True, last_price
    else:
        # 最後が close_long or そもそも open_long なし → ノーポジ扱い
        return False, None


def main():
    try:
        write_runtime_log("=== BOT START ===")

        cfg = load_config()
        print("BASE_URL:", cfg["bitget"]["base_url"])
        print("mode.dry_run =", cfg["mode"]["dry_run"])

        # ---- 1) データ取得 ----
        df = fetch_1h_candles(cfg, limit=200)

        if df is None or len(df) == 0:
            print("ERROR: 足データが取得できませんでした")
            return

        if DEBUG_PRINT_DF:
            print("FETCH DF ROWS:", len(df))
            print(df.head())
            print(df.tail())

        df = compute_indicators(df, cfg["strategy"])

        if len(df) == 0:
            print("ERROR: インジケータ計算後の df が空です")
            return

        if DEBUG_PRINT_DF:
            print("AFTER INDICATORS:", len(df))

        # ---- 2) 現在のポジション ----
        if cfg["mode"]["dry_run"]:
            # ★ ここが重要：ログから仮想ポジションを復元
            has_pos, entry_price = get_dry_run_position_from_log()
        else:
            has_pos, entry_price = get_current_position(cfg)

        print("has_position:", has_pos, "entry_price:", entry_price)

        # ---- 3) シグナル ----
        last = df.iloc[-1]
        signal = decide_signal(df, cfg["strategy"], has_pos, entry_price)
        print("last_close:", last["close"], "signal:", signal)
        write_runtime_log(f"close={last['close']} | signal={signal} | pos={has_pos}")

        # ---- 4) 売買実行 ----

        # BUY
        if signal == "BUY" and not has_pos:
            size = calc_order_size(cfg, last["close"])

            write_runtime_log(f"BUY | size={size} | price={last['close']}")
            write_trade_log("open_long", size, last["close"],
                            "DRY_RUN" if cfg["mode"]["dry_run"] else "ORDER")

            print(f"[SIGNAL] BUY size={size}")

            if not cfg["mode"]["dry_run"]:
                res = place_order(cfg, "open_long", size)
                print("ORDER RESPONSE:", res)
                append_trade_log("ORDER", "open_long", size, last["close"])
            else:
                append_trade_log("DRY_RUN", "open_long", size, last["close"])

        # SELL
        elif signal == "SELL" and has_pos:
            size = calc_order_size(cfg, last["close"])

            write_runtime_log(f"SELL | size={size} | price={last['close']}")
            write_trade_log("close_long", size, last["close"],
                            "DRY_RUN" if cfg["mode"]["dry_run"] else "ORDER")

            print(f"[SIGNAL] SELL size={size}")

            if not cfg["mode"]["dry_run"]:
                res = place_order(cfg, "close_long", size)
                print("ORDER RESPONSE:", res)
                append_trade_log("ORDER", "close_long", size, last["close"])
            else:
                append_trade_log("DRY_RUN", "close_long", size, last["close"])

        else:
            print("HOLD → 何もしない")
            write_runtime_log("HOLD")

    except Exception as e:
        write_error_log(str(e))
        print("ERROR:", e)


if __name__ == "__main__":
    main()
