import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from technicals import run_backtest_one


def make_buy_heatmap(df):

    # 固定パラメータ（まずは BUY条件の強さだけを見る）
    ma = [round(x, 1) for x in np.arange(0.9, 2, 0.05)]
    rng = [round(x, 1) for x in np.arange(0.9, 2, 0.05)]
    tp = 0.01      # 固定
    sl = 0.01      # 固定

    buy_ma_ratio_list = [round(x, 1) for x in np.arange(0.9, 2, 0.05)]
    range_pos_thr_list = [round(x, 1) for x in np.arange(0.3, 0.6, 0.05)]

    # 成績を格納する行列
    profit_matrix = np.zeros((len(buy_ma_ratio_list), len(range_pos_thr_list)))

    for i, ma_ratio in enumerate(buy_ma_ratio_list):
        for j, range_thr in enumerate(range_pos_thr_list):

            trades, total, win, avg, dd = run_backtest_one(
                df.copy(), ma, rng, tp, sl, ma_ratio, range_thr
            )

            # 利益で評価
            profit_matrix[i][j] = total

    # ヒートマップ描画
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        profit_matrix,
        annot=True,
        fmt=".3f",
        cmap="coolwarm",
        xticklabels=range_pos_thr_list,
        yticklabels=buy_ma_ratio_list
    )
    plt.title("BUY Condition Heatmap (profit)")
    plt.xlabel("range_pos_thr")
    plt.ylabel("buy_ma_ratio")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    df = pd.read_csv("btc_1h_full.csv")
    for col in ["open", "high", "low", "close"]:
        df[col] = df[col].astype(float)

    make_buy_heatmap(df)
