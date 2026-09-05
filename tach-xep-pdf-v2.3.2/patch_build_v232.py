from pathlib import Path

p = Path('tach-xep-pdf-v2.3.2/build_v232.ps1')
s = p.read_text(encoding='utf-8-sig')

old_path = "    $path = $f.FullName.Replace('\"','\"\"')"
new_path = "    $path = $f.FullName.Replace('\\','\\\\').Replace('\"','\"\"')"
old_icon = "$icon = (Resolve-Path (Join-Path $Project 'TachXepTrangPDF.ico')).Path.Replace('\"','\"\"')"
new_icon = "$icon = (Resolve-Path (Join-Path $Project 'TachXepTrangPDF.ico')).Path.Replace('\\','\\\\').Replace('\"','\"\"')"
old_link = "payload.res shell32.lib /link /SUBSYSTEM:WINDOWS"
new_link = "payload.res shell32.lib user32.lib /link /SUBSYSTEM:WINDOWS"

for needle, label in ((old_path, 'payload path'), (old_icon, 'icon path'), (old_link, 'launcher linker')):
    if needle not in s:
        raise SystemExit(f'Expected {label} line not found')

s = s.replace(old_path, new_path, 1)
s = s.replace(old_icon, new_icon, 1)
s = s.replace(old_link, new_link, 1)
p.write_text(s, encoding='utf-8-sig')
print('PATCH_BUILD_RC_PATHS_AND_USER32_OK')
