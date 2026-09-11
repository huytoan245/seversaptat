from pathlib import Path

p = Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
s = p.read_text(encoding='utf-8-sig')

# v2.8 removed the font-glyph arrows from rotate buttons and renamed Undo/Redo.
# Update only visible strings / smoke expectations; behavior and method names are unchanged.
s = s.replace('↶ Xoay trái 90°', 'Xoay trái 90°')
s = s.replace('↷ Xoay phải 90°', 'Xoay phải 90°')
s = s.replace('Làm lại', 'Tiến lại')
s = s.replace('Hoàn tác', 'Quay lại')

# Strengthen UI smoke so the new direct page tools must exist in the visible UI tree.
anchor = '''                            "Khôi phục PDF gốc",\n                            "Lên 1",'''
replacement = '''                            "Khôi phục PDF gốc",\n                            "Ghép thêm PDF",\n                            "Tách trang...",\n                            "Đảo ngược thứ tự",\n                            "Lên 1",'''
if anchor not in s:
    raise SystemExit('v280 smoke required-list anchor missing')
s = s.replace(anchor, replacement, 1)

# Also include new direct page tools in text-fit regression checks.
fit_anchor = '''"Khôi phục PDF gốc","Xoay trái 90°"'''
fit_replacement = '''"Khôi phục PDF gốc","Ghép thêm PDF","Tách trang...","Đảo ngược thứ tự","Xoay trái 90°"'''
if fit_anchor not in s:
    raise SystemExit('v280 smoke button-fit anchor missing')
s = s.replace(fit_anchor, fit_replacement, 1)

p.write_text(s, encoding='utf-8-sig')
print('PATCH_V280_SMOKE_LABELS_OK')
