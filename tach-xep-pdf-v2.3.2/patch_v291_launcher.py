from pathlib import Path
root=Path('tach-xep-pdf-v2.3.2')
launcher=root/'launcher.cpp'
if not launcher.exists():
    raise SystemExit('v291 launcher.cpp missing')
s=launcher.read_text(encoding='utf-8-sig')
if 'v2.9.0' not in s:
    raise SystemExit('v291 launcher v2.9.0 marker missing')
launcher.write_text(s.replace('v2.9.0','v2.9.1'),encoding='utf-8-sig')
print('PATCH_V291_LAUNCHER_OK')
