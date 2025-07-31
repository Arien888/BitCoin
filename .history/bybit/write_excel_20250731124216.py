import pandas as pd

def write_to_excel_spot(data, file_path):
    try:
        account_data = data["result"]["list"][0]
        coin_list = account_data.pop["coin_list"]