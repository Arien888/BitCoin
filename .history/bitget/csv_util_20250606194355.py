def save_list_of_dict_to_csv(filename, data_list):
    if not data_list:
        print("データが空です。")
        return
    keys = data_list[0].keys()
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data_list)

# 使い方例
result = get_spot_accounts(api_key, api_secret, api_passphrase)
assets = result.get("data", [])
save_list_of_dict_to_csv("assets.csv", assets)
