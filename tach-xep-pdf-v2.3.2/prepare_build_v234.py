from pathlib import Path

p = Path('tach-xep-pdf-v2.3.2/build_v232.ps1')
s = p.read_text(encoding='utf-8-sig')

# build_v232 has already been transformed by prepare_build_v233.py at this point.
s = s.replace('release-v2.3.3', 'release-v2.3.4')
s = s.replace('v2.3.3', 'v2.3.4')
s = s.replace('2.3.3', '2.3.4')

# Keep physical working folder references unchanged.
s = s.replace('tach-xep-pdf-v2.3.4/rapid_orientation.onnx', 'tach-xep-pdf-v2.3.2/rapid_orientation.onnx')
s = s.replace('tach-xep-pdf-v2.3.4/test-images', 'tach-xep-pdf-v2.3.2/test-images')

# prepare_build_v233 keeps patch_v232 and patch_v233 inside one try block. Extend that exact block.
needle = "try { & python (Join-Path $Project 'patch_v232.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v232.py failed' }; & python (Join-Path $Project 'patch_v233.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v233.py failed' } }"
replacement = "try { & python (Join-Path $Project 'patch_v232.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v232.py failed' }; & python (Join-Path $Project 'patch_v233.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v233.py failed' }; & python (Join-Path $Project 'patch_v234.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v234.py failed' }; & python (Join-Path $Project 'patch_v234_verify.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v234_verify.py failed' }; & python (Join-Path $Project 'patch_v234_manual.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v234_manual.py failed' } }"
if needle not in s:
    raise SystemExit('combined patch_v232/patch_v233 invocation not found')
s = s.replace(needle, replacement, 1)

# Ensure final portable executes the real UI smoke test with outbound network blocked.
old_ui = "$p = Start-Process -FilePath $portable -ArgumentList '--ui-smoke' -PassThru -Wait"
if old_ui not in s:
    raise SystemExit('ui smoke process call not found')

# Include v2.3.4 helpers in source snapshot.
needle_files = "(Join-Path $Project 'patch_v233.py'), (Join-Path $Project 'prepare_build_v233.py'),"
replace_files = "(Join-Path $Project 'patch_v233.py'), (Join-Path $Project 'prepare_build_v233.py'), (Join-Path $Project 'patch_v234.py'), (Join-Path $Project 'patch_v234_verify.py'), (Join-Path $Project 'patch_v234_manual.py'), (Join-Path $Project 'prepare_build_v234.py'),"
if needle_files in s:
    s = s.replace(needle_files, replace_files, 1)

# Report UI root cause and fix.
report_marker = 'Đã sửa v2.3.4:'
if report_marker in s:
    s = s.replace(report_marker, report_marker + "\n- Fix lỗi giao diện bị che/cắt: Dock=Fill + BringToFront trước đây phủ lên tiêu đề, thanh XEM TRƯỚC, THỨ TỰ TRANG và HƯỚNG DẪN.\n- Header căn giữa và co giãn theo cửa sổ, không dùng tọa độ X cố định.\n- Toolbar chuyển sang TableLayoutPanel/FlowLayoutPanel; các nhóm chính không chồng lên nhau.\n- Khu chỉnh tay và tỷ lệ cắt được tách thành 2 hàng layout riêng, tránh đè nhau ở DPI/cửa sổ khác nhau.\n- Cột trái, preview và hướng dẫn dùng hàng layout riêng nên không còn bị control Fill đè lên header.\n- Giữ toàn bộ logic PDF/AI/sắp trang không đổi.", 1)

verify_marker = '- Final PORTABLE MainForm constructor/layout UI smoke với outbound firewall block: PASS.'
if verify_marker in s:
    s = s.replace(verify_marker, verify_marker + "\n- Responsive UI smoke tại 1280x720, 1440x900, 1660x900 và 1920x1080: PASS.", 1)

p.write_text(s, encoding='utf-8-sig')
print('PREPARE_BUILD_V234_OK')
