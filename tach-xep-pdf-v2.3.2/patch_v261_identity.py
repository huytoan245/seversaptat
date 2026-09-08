from pathlib import Path
p = Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
s = p.read_text(encoding='utf-8-sig')
if 'internal const string Version = "2.6.0";' not in s:
    raise SystemExit('AppDiagnostics v2.6.0 version marker missing')
if 'startup-v2.6.0.log' not in s:
    raise SystemExit('startup-v2.6.0.log marker missing')
s = s.replace('internal const string Version = "2.6.0";', 'internal const string Version = "2.6.1";', 1)
s = s.replace('startup-v2.6.0.log', 'startup-v2.6.1.log')
p.write_text(s, encoding='utf-8-sig')
print('PATCH_V261_IDENTITY_OK')
