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

# v2.8 intentionally shows Quay lại (Undo) before Tiến lại (Redo), which is the
# natural left-to-right order for back/forward history. Migrate the legacy v2.7
# geometry assertion instead of reverting the new UI layout.
old_order = '''                            Control redo = FindControlByText(form, "Tiến lại"); Control undo = FindControlByText(form, "Quay lại");\n                            if (redo == null || undo == null || redo.RectangleToScreen(redo.ClientRectangle).Left >= undo.RectangleToScreen(undo.ClientRectangle).Left)\n                                throw new InvalidOperationException("Redo/Undo order is incorrect.");'''
new_order = '''                            Control redo = FindControlByText(form, "Tiến lại"); Control undo = FindControlByText(form, "Quay lại");\n                            if (redo == null || undo == null || undo.RectangleToScreen(undo.ClientRectangle).Left >= redo.RectangleToScreen(redo.ClientRectangle).Left)\n                                throw new InvalidOperationException("Quay lại/Tiến lại order is incorrect.");'''
if old_order not in s:
    raise SystemExit('v280 legacy redo/undo geometry assertion missing')
s = s.replace(old_order, new_order, 1)

p.write_text(s, encoding='utf-8-sig')
print('PATCH_V280_SMOKE_LABELS_OK')
