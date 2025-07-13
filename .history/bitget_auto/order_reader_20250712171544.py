import xlwings as xw
from order_utils import is_valid_order, adjust_price, adjust_quantity
import os


def load_tick_sizes():
    # def load_tick_sizes(wb, sheet_name="bitget_futures_products"):
    price_places = {}
    volume_places = {}

    file_path = r"C:\Users\koichi\Documents\MyDocuments\My_work\My_Programing_work\BitCoin\bitget_auto\a.xlsx"

    wb = xw.Book(file_path)

    sheet_names = [s.name for s in wb.sheets]
    if sheet_name is None:
        sheet_name = sheet_names[0]

    # 以下続きの処理を書いてください

    print(f"[ERROR] 対応表シートが存在しません: {sheet_name}")
    print(f"[dEBUG] 利用可能なシート名: {sheet_names}")
    if sheet_name not in sheet_names:

        print(f"[WARN] 対応表シートがありません: {sheet_name}")
        return price_places, volume_places

    sheet = wb.sheets[sheet_name]
    last_row = sheet.api.UsedRange.Rows.Count

    for row in range(2, last_row + 1):
        symbol = sheet.range(f"A{row}").value
        price_place = sheet.range(f"B{row}").value
        volume_place = sheet.range(f"C{row}").value

        if not symbol:
            continue

        print(
            f"[DEBUG] 行{row}のシンボル: {symbol}, 価格丸め桁数: {price_place}, ボリューム丸め桁数: {volume_place}"
        )

        try:
            price_places[symbol] = int(price_place)
            volume_places[symbol] = int(volume_place)
        except Exception:
            print(f"[WARN] 行 {row} の丸め桁数変換エラー symbol:{symbol}")

    return price_places, volume_places


def read_orders_from_sheet(wb, sheet_name):
    sheet_names = [s.name for s in wb.sheets]
    if sheet_name not in sheet_names:
        print(f"[ERROR] シートが存在しません: {sheet_name}")
        return []

    sheet = wb.sheets[sheet_name]
    orders = []

    last_row = sheet.api.UsedRange.Rows.Count
    for row in range(2, last_row + 1):
        symbol = sheet.range(f"A{row}").value
        side = sheet.range(f"B{row}").value
        price = sheet.range(f"C{row}").value
        quantity = sheet.range(f"D{row}").value
        order_type = sheet.range(f"E{row}").value

        if not symbol:
            continue

        print(
            f"[DEBUG] Excel読み込み行{row}: {symbol}, {side}, {price}, {quantity}, {order_type}"
        )
        orders.append((symbol, side, price, quantity, order_type))

    return orders
