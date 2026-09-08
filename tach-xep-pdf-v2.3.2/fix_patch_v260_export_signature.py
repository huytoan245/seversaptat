from pathlib import Path

p = Path('tach-xep-pdf-v2.3.2/patch_v260.py')
s = p.read_text(encoding='utf-8-sig')
old = '''export_sig = '        private async Task ExportPdfAsync(bool saveToOriginal)\\n'\nexport_start = s.find(export_sig)\nif export_start < 0:\n    raise SystemExit('ExportPdfAsync signature missing')\n'''
new = '''export_match = re.search(r'(?m)^[ \\t]*private[ \\t]+(?:async[ \\t]+)?Task[ \\t]+ExportPdfAsync[ \\t]*\\([ \\t]*bool[ \\t]+[A-Za-z_][A-Za-z0-9_]*[ \\t]*\\)', s)\nif export_match is None:\n    candidates = [x.strip() for x in s.splitlines() if 'ExportPdfAsync' in x]\n    raise SystemExit('ExportPdfAsync method signature missing. Seen: ' + ' || '.join(candidates[:20]))\nexport_start = export_match.start()\n'''
if old not in s:
    raise SystemExit('old v260 exact export signature block not found')
s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8-sig')
print('FIX_PATCH_V260_EXPORT_SIGNATURE_OK')
