from pathlib import Path
p=Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
s=p.read_text(encoding='utf-8-sig')
block='''            Button mergeTop = MakeButton("Ghép thêm PDF", 126, false); mergeTop.Margin = new Padding(0,0,8,0); mergeTop.Click += async delegate { await MergePdfIntoCurrentAsync(-1); }; actions.Controls.Add(mergeTop);\n            Button extractTop = MakeButton("Tách trang...", 112, false); extractTop.Margin = new Padding(0,0,8,0); extractTop.Click += delegate { ShowExtractChoiceMenu(extractTop); }; actions.Controls.Add(extractTop);\n'''
if block not in s:
    raise SystemExit('v2.7.0 compact top action block missing')
s=s.replace(block,'',1)
# The features stay available from both file and page context menus; do not weaken discoverability markers.
for marker in ['Ghép thêm PDF vào tệp này...','Ghép thêm PDF sau trang này...','Tách trang từ tệp này...','Tách riêng trang đang chọn...','Tách nhiều trang...']:
    if marker not in s:
        raise SystemExit('v2.7.0 compact context action missing: '+marker)
p.write_text(s,encoding='utf-8-sig')
print('PATCH_V270_COMPACT_TOP_OK')
