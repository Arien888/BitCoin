def export_values_only(src_file, sheet_names, dst_file):
    src_wb = load_workbook(src_file, data_only=True)
    new_wb = Workbook()
    first = True

    for name in sheet_names:
        if name not in src_wb.sheetnames:
            print(f"⚠ シート '{name}' は存在しません。スキップします。")
            continue

        src_ws = src_wb[name]
        if first:
            new_ws = new_wb.active
            new_ws.title = name
            first = False
        else:
            new_ws = new_wb.create_sheet(title=name)

        for row in src_ws.iter_rows():
            for cell in row:
                v = cell.value
                # 数値変換を試みる
                if isinstance(v, str):
                    try:
                        # 文字列ならfloatに変換可能か試す
                        v_num = float(v)
                        v = v_num
                    except ValueError:
                        pass  # 変換できなければそのまま文字列
                new_ws[cell.coordinate].value = v

    new_wb.save(dst_file)
    print(f"✅ エクスポート完了: {dst_file}")
