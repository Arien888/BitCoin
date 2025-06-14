import pandas as pd


def save_positions_and_spot_to_excel(df_positions, df_spot, filepath):
    """
    先物ポジションと現物保有残高をExcelに保存（別シートに出力）

    Parameters:
        df_positions: pd.DataFrame - 先物ポジションのデータ
        df_spot: pd.DataFrame - 現物保有残高のデータ
        filepath: str - 保存するExcelファイルのフルパスまたはファイル名
    """
    with pd.ExcelWriter(filepath) as writer:
        df_positions.to_excel(writer, sheet_name="mexc_", index=False)
        df_spot.to_excel(writer, sheet_name="現物保有残高", index=False)

    print(f"Excelファイルに保存完了: {filepath}")
