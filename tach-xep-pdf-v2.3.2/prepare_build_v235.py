from pathlib import Path

p = Path('tach-xep-pdf-v2.3.2/build_v232.ps1')
s = p.read_text(encoding='utf-8-sig')

# This script runs after prepare_build_v234.py, so build script currently targets v2.3.4.
s = s.replace('release-v2.3.4', 'release-v2.3.5')
s = s.replace('v2.3.4', 'v2.3.5')
s = s.replace('2.3.4', '2.3.5')

# Keep physical working folder references unchanged.
s = s.replace('tach-xep-pdf-v2.3.5/rapid_orientation.onnx', 'tach-xep-pdf-v2.3.2/rapid_orientation.onnx')
s = s.replace('tach-xep-pdf-v2.3.5/test-images', 'tach-xep-pdf-v2.3.2/test-images')

needle = "try { & python (Join-Path $Project 'patch_v232.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v232.py failed' }; & python (Join-Path $Project 'patch_v233.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v233.py failed' }; & python (Join-Path $Project 'patch_v234.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v234.py failed' }; & python (Join-Path $Project 'patch_v234_verify.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v234_verify.py failed' }; & python (Join-Path $Project 'patch_v234_manual.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v234_manual.py failed' } }"
replacement = "try { & python (Join-Path $Project 'patch_v232.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v232.py failed' }; & python (Join-Path $Project 'patch_v233.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v233.py failed' }; & python (Join-Path $Project 'patch_v234.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v234.py failed' }; & python (Join-Path $Project 'patch_v234_verify.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v234_verify.py failed' }; & python (Join-Path $Project 'patch_v234_manual.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v234_manual.py failed' }; & python (Join-Path $Project 'patch_v235a.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v235a.py failed' }; & python (Join-Path $Project 'patch_v235b.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v235b.py failed' }; & python (Join-Path $Project 'patch_v235c.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v235c.py failed' }; & python (Join-Path $Project 'patch_v235d.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v235d.py failed' }; & python (Join-Path $Project 'patch_v235e.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v235e.py failed' } }"
if needle not in s:
    raise SystemExit('v2.3.4 combined patch invocation not found')
s = s.replace(needle, replacement, 1)

# regression_test.py is restored from the immutable old source AFTER the source patch chain.
# Patch the test expectation only after that copy so the release gate validates the new wording/features.
reg_copy = "Copy-Item (Join-Path $Old 'regression_test.py') (Join-Path $Project 'regression_test.py') -Force"
reg_call = reg_copy + "\n& python (Join-Path $Project 'patch_regression_v235.py')\nif ($LASTEXITCODE -ne 0) { throw 'patch_regression_v235.py failed' }"
if reg_copy not in s:
    raise SystemExit('regression_test copy marker not found')
s = s.replace(reg_copy, reg_call, 1)

# Include v2.3.5 patch chain in reproducible source snapshot.
needle_files = "(Join-Path $Project 'patch_v234.py'), (Join-Path $Project 'patch_v234_verify.py'), (Join-Path $Project 'patch_v234_manual.py'), (Join-Path $Project 'prepare_build_v234.py'),"
replace_files = "(Join-Path $Project 'patch_v234.py'), (Join-Path $Project 'patch_v234_verify.py'), (Join-Path $Project 'patch_v234_manual.py'), (Join-Path $Project 'prepare_build_v234.py'), (Join-Path $Project 'patch_v235a.py'), (Join-Path $Project 'patch_v235b.py'), (Join-Path $Project 'patch_v235c.py'), (Join-Path $Project 'patch_v235d.py'), (Join-Path $Project 'patch_v235e.py'), (Join-Path $Project 'patch_regression_v235.py'), (Join-Path $Project 'prepare_build_v235.py'),"
if needle_files not in s:
    raise SystemExit('source snapshot v234 helper list not found')
s = s.replace(needle_files, replace_files, 1)

# Add concrete handoff notes.
marker = 'Đã sửa v2.3.5:'
if marker in s:
    s = s.replace(marker, marker + "\n- Khôi phục thanh XEM TRƯỚC kiểu ổn định: ô phần trăm 50-300% và nút Vừa cửa sổ.\n- Preview và thumbnail luôn giữ đúng tỷ lệ gốc, không StretchImage làm méo tài liệu.\n- Cột HƯỚNG DẪN giữ khoảng 10-15% chiều rộng thay vì phình theo màn hình.\n- File đang mở được đặt ngay trên nút Mở PDF.\n- Làm lại đặt trước Hoàn tác; CHIỀU CẮT chuyển sang phía sau khu chỉnh tay.\n- Phím ↑/↓ nay chọn trang trước/sau và tải preview ngay; Ctrl+↑/↓ vẫn dùng để đổi thứ tự trang.\n- Giữ nguyên engine Auto Rotate offline, source_order, 50/50 và thuật toán sắp trang.", 1)

verify = '- Responsive UI smoke tại 1280x720, 1440x900, 1660x900 và 1920x1080: PASS.'
if verify in s:
    s = s.replace(verify, verify + "\n- UI smoke xác nhận có nút Vừa cửa sổ và cột hướng dẫn không vượt 17% cửa sổ: PASS.\n- Source regression xác nhận PictureBoxSizeMode.Zoom + thumbnail FitCanvas + SelectAdjacent: PASS.", 1)

p.write_text(s, encoding='utf-8-sig')
print('PREPARE_BUILD_V235_OK')
