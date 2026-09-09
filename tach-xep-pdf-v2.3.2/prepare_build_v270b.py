from pathlib import Path

p = Path('tach-xep-pdf-v2.3.2/build_v232.ps1')
s = p.read_text(encoding='utf-8-sig')

old_chain = "& python (Join-Path $Project 'patch_v270_tests.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v270_tests.py failed' }; & python (Join-Path $Project 'patch_v270_restore_safe.py')"
new_chain = "& python (Join-Path $Project 'patch_v270_tests.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v270_tests.py failed' }; & python (Join-Path $Project 'patch_v270_preview_smoke.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v270_preview_smoke.py failed' }; & python (Join-Path $Project 'patch_v270_restore_safe.py')"
if old_chain not in s:
    raise SystemExit('v2.7.0 patch chain marker missing for preview smoke sync')
s = s.replace(old_chain, new_chain, 1)

old_snapshot = "(Join-Path $Project 'patch_v270_tests.py'), (Join-Path $Project 'patch_v270_restore_safe.py')"
new_snapshot = "(Join-Path $Project 'patch_v270_tests.py'), (Join-Path $Project 'patch_v270_preview_smoke.py'), (Join-Path $Project 'patch_v270_restore_safe.py')"
if old_snapshot not in s:
    raise SystemExit('v2.7.0 snapshot marker missing for preview smoke sync')
s = s.replace(old_snapshot, new_snapshot, 1)

p.write_text(s, encoding='utf-8-sig')
print('PREPARE_BUILD_V270B_OK')
