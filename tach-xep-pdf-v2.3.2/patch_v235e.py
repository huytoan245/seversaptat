from pathlib import Path

p = Path('tach-xep-pdf-v2.3.2/launcher.cpp')
s = p.read_text(encoding='utf-8-sig')
s = s.replace('2.3.4', '2.3.5')
p.write_text(s, encoding='utf-8-sig')
print('PATCH_V235E_LAUNCHER_VERSION_OK')
