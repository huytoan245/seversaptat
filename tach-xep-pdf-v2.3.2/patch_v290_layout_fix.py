from pathlib import Path
p=Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
s=p.read_text(encoding='utf-8-sig')

def rep(old,new,label,count=1):
    global s
    if old not in s:
        raise SystemExit('v290 layout marker missing: '+label)
    s=s.replace(old,new,count)

# Keep the v2.8 top action row exactly as before; move batch-save to the page-tools row.
top='''            _btnSaveAllOriginal = MakeButton("Lưu tất cả vào bản gốc", 188, false); _btnSaveAllOriginal.Margin = new Padding(0, 0, 8, 0); _btnSaveAllOriginal.Click += async delegate { await SaveAllModifiedToOriginalAsync(); }; actions.Controls.Add(_btnSaveAllOriginal); StyleGroupedButton(_btnSaveAllOriginal, UiTheme.Save);\n'''
rep(top,'','remove top save-all')

anchor='''            Button reverseDirect = MakeButton("Đảo ngược thứ tự", 152, false); reverseDirect.Margin = new Padding(0,0,5,0); reverseDirect.Click += delegate { ReversePageOrder(); }; pageTools.Controls.Add(reverseDirect); StyleGroupedButton(reverseDirect, UiTheme.PageTools);\n'''
insert=anchor+'''            _btnSaveAllOriginal = MakeButton("Lưu tất cả gốc", 138, false); _btnSaveAllOriginal.Margin = new Padding(0,0,5,0); _btnSaveAllOriginal.Click += async delegate { await SaveAllModifiedToOriginalAsync(); }; pageTools.Controls.Add(_btnSaveAllOriginal); StyleGroupedButton(_btnSaveAllOriginal, UiTheme.Save); _toolTip.SetToolTip(_btnSaveAllOriginal, "Lưu tất cả PDF đã chỉnh sửa vào chính các tệp PDF gốc.");\n'''
rep(anchor,insert,'page tools save-all')

# UI smoke: require the compact direct button in the second row, not in the already-full top row.
rep('''                            "Lưu vào file gốc",\n                            "Lưu tất cả vào bản gốc",\n                            "TỆP ĐANG XỬ LÝ",\n''','''                            "Lưu vào file gốc",\n                            "TỆP ĐANG XỬ LÝ",\n''','smoke top remove')
rep('''                            "Đảo ngược thứ tự",\n                            "Lên 1",\n''','''                            "Đảo ngược thứ tự",\n                            "Lưu tất cả gốc",\n                            "Lên 1",\n''','smoke second-row add')
rep('''"Xuất PDF","Lưu vào file gốc","Lưu tất cả vào bản gốc","Khôi phục PDF gốc"''','''"Xuất PDF","Lưu vào file gốc","Khôi phục PDF gốc"''','fit top remove')
rep('''"Ghép thêm PDF","Tách trang...","Đảo ngược thứ tự","Xoay trái 90°"''','''"Ghép thêm PDF","Tách trang...","Đảo ngược thứ tự","Lưu tất cả gốc","Xoay trái 90°"''','fit second-row add')

p.write_text(s,encoding='utf-8-sig')
print('PATCH_V290_LAYOUT_FIX_OK')
