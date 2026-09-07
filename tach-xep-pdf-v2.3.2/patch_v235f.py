from pathlib import Path

p = Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
s = p.read_text(encoding='utf-8-sig')

old = 'ConfigureRightPaneRatio(inner, 0.14, 170, 250)'
new = 'ConfigureRightPaneRatio(inner, 0.12, 130, 190)'
count = s.count(old)
if count != 2:
    raise SystemExit(f'expected two right-pane ratio calls, found {count}')
s = s.replace(old, new)

p.write_text(s, encoding='utf-8-sig')
print('PATCH_V235F_NARROW_GUIDE_OK')
