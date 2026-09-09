from pathlib import Path
p=Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
s=p.read_text(encoding='utf-8-sig')
start=s.find('        private void RestoreOriginalPdf()\n')
end=s.find('        private void PushHistory()\n', start)
if start < 0 or end < 0:
    raise SystemExit('RestoreOriginalPdf boundary missing')
print('---RESTORE_METHOD_BEGIN---')
print(s[start:end])
print('---RESTORE_METHOD_END---')
print('PATCH_V270_RESTORE_DIAG_OK')
