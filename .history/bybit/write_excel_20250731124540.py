import pandas as pd

def write_to_excel_spot(data, file_path):
    try:
        account_data = data["result"]["list"][0]
        coin_list = account_data.pop("coin")
        
        # 基本情報
        account_info_df = pd.DataFrame([account_data])
        
        # コイン詳細
        coin_df = pd.DataFrame(coin_list)