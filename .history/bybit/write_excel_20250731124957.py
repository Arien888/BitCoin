import pandas as pd

def write_to_excel(data, file_path):
    try:
        account_data = data["result"]["list"][0]
        coin_list = account_data.pop("coin")
        
        # 基本情報
        account_info_df = pd.DataFrame([account_data])
        
        # コイン詳細
        coin_df = pd.DataFrame(coin_list)
        
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            account_info_df.to_excel(writer, sheet_name='Account Info', index=False)
            coin_df.to_excel(writer, sheet_name='Coin Details', index=False)