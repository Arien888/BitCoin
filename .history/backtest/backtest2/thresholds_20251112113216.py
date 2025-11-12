# thresholds.py
import numpy as np

def compute_threshold(values, base="median", direction="above", agg="mean"):
    arr = np.asarray(values)
    if arr.size == 0:
        return 0.0
    ref = np.median(arr) if base == "median" else (np.max(arr) if base == "max" else arr.mean())
    filtered = arr[arr >= ref] if direction == "above" else arr[arr <= ref]
    if filtered.size == 0:
        return ref
    return filtered.mean() if agg == "mean" else np.median(filtered)

def parse_method(m):
    if "_above_" in m:
        base, agg = m.split("_above_")
        return base, "above", agg
    elif "_below_" in m:
        base, agg = m.split("_below_")
        return base, "below", agg
    elif m in ["mean", "median", "max"]:
        return m, "above", m
    else:
        raise ValueError("Unknown method: " + str(m))

def get_thresholds(buy_returns, sell_returns, buy_method_ma, buy_method_prev, sell_method_ma, sell_method_prev):
    buy_base_ma, buy_dir_ma, buy_agg_ma = parse_method(buy_method_ma)
    buy_base_prev, buy_dir_prev, buy_agg_prev = parse_method(buy_method_prev)
    sell_base_ma, sell_dir_ma, sell_agg_ma = parse_method(sell_method_ma)
    sell_base_prev, sell_dir_prev, sell_agg_prev = parse_method(sell_method_prev)

    return (
        compute_threshold(buy_returns, buy_base_ma, buy_dir_ma, buy_agg_ma),
        compute_threshold(buy_returns, buy_base_prev, buy_dir_prev, buy_agg_prev),
        compute_threshold(sell_returns, sell_base_ma, sell_dir_ma, sell_agg_ma),
        compute_threshold(sell_returns, sell_base_prev, sell_dir_prev, sell_agg_prev)
    )
