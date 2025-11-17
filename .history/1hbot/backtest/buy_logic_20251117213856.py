# buy_logic.py

def buy_condition(row, ma_period, dc=0.01, range_thr=0.3):
    """
    BUY 条件（手動カウントと完全一致させるためのロジック）
    """
    ma_value = row[f"ma{ma_period}"]

    return (
        row["close"] < ma_value * (1 - dc)   # MA -1%
        and row["range_pos"] < range_thr     # レンジ下 30%
        and (row["prev_dir_up"] == False)    # 前足が陰線
    )
