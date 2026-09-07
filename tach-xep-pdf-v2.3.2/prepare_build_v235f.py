from pathlib import Path

p = Path('tach-xep-pdf-v2.3.2/build_v232.ps1')
s = p.read_text(encoding='utf-8-sig')

old = "& python (Join-Path $Project 'patch_v235e.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v235e.py failed' } }"
new = "& python (Join-Path $Project 'patch_v235e.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v235e.py failed' }; & python (Join-Path $Project 'patch_v235f.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v235f.py failed' } }"
if old not in s:
    raise SystemExit('v2.3.5 patch_v235e tail not found')
s = s.replace(old, new, 1)

old_files = "(Join-Path $Project 'patch_v235e.py'), (Join-Path $Project 'patch_regression_v235.py'), (Join-Path $Project 'prepare_build_v235.py'),"
new_files = "(Join-Path $Project 'patch_v235e.py'), (Join-Path $Project 'patch_v235f.py'), (Join-Path $Project 'patch_regression_v235.py'), (Join-Path $Project 'prepare_build_v235.py'), (Join-Path $Project 'prepare_build_v235f.py'),"
if old_files not in s:
    raise SystemExit('v2.3.5 source helper tail not found')
s = s.replace(old_files, new_files, 1)

p.write_text(s, encoding='utf-8-sig')
print('PREPARE_BUILD_V235F_OK')
