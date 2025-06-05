import requests
import pandas as pd
from time import sleep

# 1. トップ50銘柄の基本情報を取得
def fetch_top50_markets():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 50,
        "page": 1,
        "sparkline": False
    }
    res = requests.get(url, params=params)
    return res.json()

# 2. 詳細情報取得
def fetch_coin_detail(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    res = requests.get(url)
    if res.status_code == 200:
        return res.json()
    else:
        return None

# メイン処理
def main():
    markets = fetch_top50_markets()

    # 収集する数値指標の初期化
    data = []
    for coin in markets:
        coin_id = coin["id"]
        detail = fetch_coin_detail(coin_id)
        if not detail:
            print(f"Failed to get detail for {coin_id}")
            continue
        
        md = detail.get("market_data", {})
        dd = detail.get("developer_data", {})
        cd = detail.get("community_data", {})
        
        # 数値項目を取得
        record = {
            "id": coin_id,
            "name": coin["name"],
            "current_price": md.get("current_price", {}).get("usd", None),
            "market_cap": md.get("market_cap", {}).get("usd", None),
            "total_volume": md.get("total_volume", {}).get("usd", None),
            "high_24h": md.get("high_24h", {}).get("usd", None),
            "low_24h": md.get("low_24h", {}).get("usd", None),
            "ath": md.get("ath", {}).get("usd", None),
            "atl": md.get("atl", {}).get("usd", None),
            "circulating_supply": md.get("circulating_supply", None),
            "total_supply": md.get("total_supply", None),
            "max_supply": md.get("max_supply", None),
            "forks": dd.get("forks", None),
            "stars": dd.get("stars", None),
            "subscribers": dd.get("subscribers", None),
            "total_issues": dd.get("total_issues", None),
            "closed_issues": dd.get("closed_issues", None),
            "pull_requests_merged": dd.get("pull_requests_merged", None),
            "twitter_followers": cd.get("twitter_followers", None),
            "reddit_subscribers": cd.get("reddit_subscribers", None),
            "telegram_channel_user_count": cd.get("telegram_channel_user_count", None),
        }
        data.append(record)
        sleep(1)  # API負荷軽減のため1秒待機

    df = pd.DataFrame(data)

    # 4. 順位付け（market_capは大きいほど良いので降順）
    # 例：市場規模は大きい方が順位高いので ascending=False
    rank_cols = [
        "current_price", "market_cap", "total_volume", "high_24h", "low_24h",
        "ath", "atl", "circulating_supply", "total_supply", "max_supply",
        "forks", "stars", "subscribers", "total_issues", "closed_issues",
        "pull_requests_merged", "twitter_followers", "reddit_subscribers", "telegram_channel_user_count"
    ]

    # 順位付けの方針：
    # ほとんどは数値が大きい方が良い → ascending=False
    # ただし、low_24h, atl（過去最安値）は小さい方が良い（値としては低いほうが目立つ）
    # ここではわかりやすく全部大きい方が良い前提で順位付けします。必要に応じて調整してください。

    for col in rank_cols:
        if col in df.columns:
            df[col + "_rank"] = df[col].rank(ascending=False, method='min')

    # 5. 順位の合計を計算（nullを除外するためにfillna最大順位＋1などでもOK）
    rank_cols_names = [c + "_rank" for c in rank_cols if c + "_rank" in df.columns]

    # 欠損値は最大順位+1で扱う（ペナルティ）
    max_rank = len(df) + 1
    df[rank_cols_names] = df[rank_cols_names].fillna(max_rank)

    df["rank_sum"] = df[rank_cols_names].sum(axis=1)

    # 6. 総合順位でソート
    df = df.sort_values("rank_sum")

    # 結果を表示または保存
    print(df[["id", "name", "rank_sum"] + rank_cols_names])

    df.to_csv("crypto_top50_ranked.csv", index=False)
    print("ランキング結果をcrypto_top50_ranked.csvに保存しました。")

if __name__ == "__main__":
    main()
