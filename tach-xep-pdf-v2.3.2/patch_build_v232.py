from pathlib import Path

p = Path('tach-xep-pdf-v2.3.2/build_v232.ps1')
s = p.read_text(encoding='utf-8-sig')

old_path = "    $path = $f.FullName.Replace('\"','\"\"')"
new_path = "    $path = $f.FullName.Replace('\\','\\\\').Replace('\"','\"\"')"
old_icon = "$icon = (Resolve-Path (Join-Path $Project 'TachXepTrangPDF.ico')).Path.Replace('\"','\"\"')"
new_icon = "$icon = (Resolve-Path (Join-Path $Project 'TachXepTrangPDF.ico')).Path.Replace('\\','\\\\').Replace('\"','\"\"')"

if old_path not in s:
    raise SystemExit('Expected payload path line not found')
if old_icon not in s:
    raise SystemExit('Expected icon path line not found')

s = s.replace(old_path, new_path, 1)
s = s.replace(old_icon, new_icon, 1)
p.write_text(s, encoding='utf-8-sig')
print('PATCH_BUILD_RC_PATHS_OK')
