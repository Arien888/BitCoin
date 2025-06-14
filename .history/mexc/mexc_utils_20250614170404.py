import pandas as pd

def save_positions_and_spot_to_excel(df_positions, df_spot, filepath):
    """
    先物ポジションと現物保有残高をExcelに保存（既存ファイルに上書き、他シートは保持）

    Parameters:
        df_positions: pd.DataFrame - 先物ポジションのデータ
        df_spot: pd.DataFrame - 現物保有残高のデータ
        filepath: str - 保存するExcelファイルのパス
    """
    with pd.ExcelWriter(filepath, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df_positions.to_excel(writer, sheet_name="mexc_futures", index=False)
        df_spot.to_excel(writer, sheet_name="mexc_spot", index=False)

    print(f"Excelファイルに上書き保存完了: {filepath}")
