import pandas as pd

def compute_indicators(df, params):
    ma_period = params["ma_period"]
    range_lb = params["range_lb"]

    # MA
    df[f"ma{ma_period}"] = df["close"].rolling(ma_period).mean()

    # High/Low range
    df["range_high"] = df["high"].rolling(range_lb).max()
    df["range_low"]  = df["low"].rolling(range_lb).min()

    # Range position (0~1)
    df["range_pos"] = (df["close"] - df["range_low"]) / (
        df["range_high"] - df["range_low"]
    )

    # Previous close
    df["prev_close"] = df["close"].shift(1)
    df["prev_dir_up"] = df["close"] > df["prev_close"]

    return df.dropna().reset_index(drop=True)
