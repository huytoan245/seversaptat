from pathlib import Path

p = Path('tach-xep-pdf-v2.3.2/build_v232.ps1')
s = p.read_text(encoding='utf-8-sig')

# Chain v2.5.0 after the fully reconstructed and regression-proven v2.4.5 source.
old = "& python (Join-Path $Project 'patch_v245e.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v245e.py failed' } }"
new = "& python (Join-Path $Project 'patch_v245e.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v245e.py failed' }; & python (Join-Path $Project 'patch_v250.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v250.py failed' }; & python (Join-Path $Project 'patch_v250b.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v250b.py failed' } }"
if old not in s:
    raise SystemExit('v2.4.5 final patch-chain marker missing')
s = s.replace(old, new, 1)

# Release/build/launcher identity.
s = s.replace('release-v2.4.5', 'release-v2.5.0').replace('v2.4.5', 'v2.5.0').replace('2.4.5', '2.5.0')

# Preserve the preview/order safety guards but replace the old fixed cut-pane ratio marker
# with the new DPI-safe multi-file workspace contract.
old_marker = "'ConfigureRightPaneRatio(inner, 0.14, 215, 260)'"
new_marker = "'DocumentWorkspace','TỆP ĐANG XỬ LÝ','dlg.Multiselect = true','PersistActiveDocumentState','ActivateDocument','ClampSplitterForResize','AssertButtonTextFits'"
if old_marker not in s:
    raise SystemExit('v2.4.5 regression marker missing')
s = s.replace(old_marker, new_marker, 1)

# Include v2.5.0 patch and preparation files in the source handoff ZIP.
old_snapshot = "(Join-Path $Project 'patch_v245e.py'), (Join-Path $Project 'prepare_build_v245.py'), (Join-Path $Project 'regression_test.py'),"
new_snapshot = "(Join-Path $Project 'patch_v245e.py'), (Join-Path $Project 'prepare_build_v245.py'), (Join-Path $Project 'patch_v250.py'), (Join-Path $Project 'patch_v250b.py'), (Join-Path $Project 'prepare_build_v250.py'), (Join-Path $Project 'regression_test.py'),"
if old_snapshot not in s:
    raise SystemExit('v2.4.5 source snapshot marker missing')
s = s.replace(old_snapshot, new_snapshot, 1)

marker = 'Đã sửa v2.5.0:'
if marker in s:
    s = s.replace(marker, marker + '\n- Sửa lỗi chữ/nút bị cắt trên máy có DPI/font scaling khác: nút đo kích thước chữ thực tế tại runtime, thanh lệnh tự wrap thay vì ẩn/tràn.\n- Bổ sung AutoScaleMode.Dpi trên nền PerMonitorV2 để Windows 10/11 125%-200% scaling ổn định hơn.\n- Bổ sung cột TỆP ĐANG XỬ LÝ ở ngoài cùng bên trái; Mở PDF hỗ trợ chọn nhiều tệp cùng lúc.\n- Mỗi tệp có work-copy, trạng thái trang, Undo/Redo, zoom, trạng thái ghi đè và backup riêng; chuyển tệp không làm lẫn dữ liệu.\n- Bố cục 4 cột: Tệp PDF | Thứ tự trang | Xem trước | Chỉnh đường cắt.\n- Ba thanh chia dọc đều kéo được bằng chuột; tỷ lệ mặc định chỉ áp dụng lúc đầu, resize không ghi đè độ rộng người dùng đã kéo.\n- Chỉ giữ runtime/preview cache của tệp đang hoạt động để tránh RAM tăng theo số lượng PDF.\n- Workflow smoke kiểm tra chuyển 2 PDF và xác nhận split/cut/order của từng tệp được giữ độc lập.\n', 1)

p.write_text(s, encoding='utf-8-sig')
print('PREPARE_BUILD_V250_OK')
