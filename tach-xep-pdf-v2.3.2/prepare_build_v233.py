from pathlib import Path

p = Path('tach-xep-pdf-v2.3.2/build_v232.ps1')
s = p.read_text(encoding='utf-8-sig')

# Build/release/runtime version bump. Keep the physical project folder at tach-xep-pdf-v2.3.2.
s = s.replace('release-v2.3.2', 'release-v2.3.3')
s = s.replace('v2.3.2', 'v2.3.3')
s = s.replace('2.3.2', '2.3.3')

# The workflow intentionally reuses the existing build folder; these generated Python snippets
# must still address that physical folder.
s = s.replace("tach-xep-pdf-v2.3.3/rapid_orientation.onnx", "tach-xep-pdf-v2.3.2/rapid_orientation.onnx")
s = s.replace("tach-xep-pdf-v2.3.3/test-images", "tach-xep-pdf-v2.3.2/test-images")

# Apply the v2.3.3 source patch inside the existing try/finally block, immediately after patch_v232.
needle = "try { & python (Join-Path $Project 'patch_v232.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v232.py failed' } }"
replacement = "try { & python (Join-Path $Project 'patch_v232.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v232.py failed' }; & python (Join-Path $Project 'patch_v233.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v233.py failed' } }"
if needle not in s:
    raise SystemExit('patch_v232 invocation not found')
s = s.replace(needle, replacement, 1)

# Require the new startup regression marker.
s = s.replace("'--self-test','CreateSessionDirectory'", "'--self-test','--ui-smoke','CreateSessionDirectory'", 1)

# Run a real MainForm constructor/layout smoke test through the final portable launcher while outbound network is blocked.
needle2 = "    foreach ($t in $tests) {"
ui_block = '''    $p = Start-Process -FilePath $portable -ArgumentList '--ui-smoke' -PassThru -Wait\n    if ($p.ExitCode -ne 0) {\n        $l1=Join-Path $env:LOCALAPPDATA 'TachXepTrangPDF\\Logs\\launcher-v2.3.3.log'; if(Test-Path $l1){Get-Content $l1}\n        $l2=Join-Path $env:LOCALAPPDATA 'TachXepTrangPDF\\Logs\\startup-v2.3.3.log'; if(Test-Path $l2){Get-Content $l2}\n        throw "Firewall-blocked UI smoke test failed: $($p.ExitCode)"\n    }\n    foreach ($t in $tests) {'''
if needle2 not in s:
    raise SystemExit('orientation loop marker not found')
s = s.replace(needle2, ui_block, 1)

needle3 = "'OFFLINE_FIREWALL_SELFTEST=PASS' | Add-Content (Join-Path $Project 'offline-test.txt')"
if needle3 not in s:
    raise SystemExit('offline self-test marker not found')
s = s.replace(needle3, needle3 + "\n'OFFLINE_FIREWALL_UI_SMOKE=PASS' | Add-Content (Join-Path $Project 'offline-test.txt')", 1)

# Add v2.3.3 patch/build helpers to the source snapshot for reproducibility.
needle4 = "    (Join-Path $Project 'patch_v232.py'), (Join-Path $Project 'regression_test.py'),"
replacement4 = "    (Join-Path $Project 'patch_v232.py'), (Join-Path $Project 'patch_v233.py'), (Join-Path $Project 'prepare_build_v233.py'), (Join-Path $Project 'regression_test.py'),"
if needle4 in s:
    s = s.replace(needle4, replacement4, 1)

# Report the exact startup defect and verification added in this patch release.
report_marker = 'Đã sửa v2.3.3:'
if report_marker in s:
    s = s.replace(report_marker, report_marker + "\n- Fix NullReference khi khởi động: WinForms phát OnResize trong lúc constructor mới đặt Width/Height, trước khi BuildUi tạo _previewScroll/_preview/_zoom.\n- OnResize và ApplyZoom nay có lifecycle guard; thêm --ui-smoke để dựng MainForm thật trong CI.", 1)

verify_marker = '- Final PORTABLE self-test với outbound firewall block: PASS.'
if verify_marker in s:
    s = s.replace(verify_marker, verify_marker + "\n- Final PORTABLE MainForm constructor/layout UI smoke với outbound firewall block: PASS.", 1)

p.write_text(s, encoding='utf-8-sig')
print('PREPARE_BUILD_V233_OK')
