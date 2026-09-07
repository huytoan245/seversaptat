from pathlib import Path

p = Path('tach-xep-pdf-v2.3.2/regression_test.py')
s = p.read_text(encoding='utf-8-sig')

if "'File đang xử lý:'" not in s:
    raise SystemExit('old filename regression expectation not found')
s = s.replace("'File đang xử lý:'", "'File đang mở:'", 1)

needle = "    'TỰ CHIA & SẮP XẾP',\n"
extras = "    'Vừa cửa sổ',\n    'PictureBoxSizeMode.Zoom',\n    'FitCanvas',\n    'SelectAdjacent',\n    'ConfigureRightPaneRatio',\n    'NumericUpDown _zoom',\n"
if needle not in s:
    raise SystemExit('required-list insertion marker not found')
s = s.replace(needle, needle + extras, 1)

p.write_text(s, encoding='utf-8-sig')
print('PATCH_REGRESSION_V235_OK')
