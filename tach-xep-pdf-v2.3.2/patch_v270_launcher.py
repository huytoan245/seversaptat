from pathlib import Path
root=Path('tach-xep-pdf-v2.3.2')
p=root/'launcher.cpp'
s=p.read_text(encoding='utf-8-sig')
if 'v2.6.1' not in s:
    raise SystemExit('v2.7.0 launcher expected v2.6.1 identity marker missing')
s=s.replace('v2.6.1','v2.7.0')
required=['Runtime" / L"v2.7.0','Tach_Xep_Trang_PDF_v2.7.0.exe','launcher-v2.7.0.log','Launcher v2.7.0 start','PDF v2.7.0']
for marker in required:
    if marker not in s:
        raise SystemExit('v2.7.0 launcher identity marker missing: '+marker)
p.write_text(s,encoding='utf-8-sig')
print('PATCH_V270_LAUNCHER_IDENTITY_OK')
