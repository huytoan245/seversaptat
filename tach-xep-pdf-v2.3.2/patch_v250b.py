from pathlib import Path

p = Path('tach-xep-pdf-v2.3.2/TachXepTrangPDF.cs')
s = p.read_text(encoding='utf-8-sig')
before = s
s = s.replace('v2.4.5', 'v2.5.0').replace('2.4.5', '2.5.0')
if s == before:
    print('PATCH_V250B_VERSION_LITERALS_ALREADY_NORMALIZED')
else:
    p.write_text(s, encoding='utf-8-sig')
    print('PATCH_V250B_VERSION_LITERALS_OK')
