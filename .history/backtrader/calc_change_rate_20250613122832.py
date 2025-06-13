import pandas as pd


def calculate_avg_change_rate_by_date(df, base_date, days=30):
    """
    base_date 以前の直近 days 日分で変化率平均を計算する。
    """
    df_ = (
        df[df["datetime"] < base_date].tail(days).copy()
    )  # base_date より前のデータを取得
    if len(df_) < days:
        # データ不足の場合はNoneや0を返すなど対応可能
        return None

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
