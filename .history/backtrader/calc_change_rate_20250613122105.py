import pandas as pd


def calculate_avg_change_rate(df, days=30):
    """
    過去days日分の前日終値から翌日安値への変化率の平均を計算する。

    Args:
        df (pd.DataFrame): 日付昇順で並んだデータフレーム。 'close', 'low' カラムが必要。
        days (int): 過去何日分のデータを使うか。

    Returns:
        float: 変化率の平均（小数、%なら100倍して使う）
    """
    df_ = df.tail(days).copy()
    df_["prev_close"] = df_["close"].shift(1)
    df_["next_low"] = df_["low"].shift(-1)
    df_["change_rate"] = (df_["next_low"] - df_["prev_close"]) / df_["prev_close"]

    avg_rate = df_["change_rate"].dropna().mean()
    return avg_rate


if __name__ == "__main__":
    # テスト用: CSVファイル読み込み例（ファイル名は適宜変更）
    df = pd.read_csv("binance_btc.csv", parse_dates=["datetime"])
    df = df.sort_values("datetime")

    avg_change = calculate_avg_change_rate(df)
    print(f"過去30日分の変化率平均: {avg_change:.4%}")
