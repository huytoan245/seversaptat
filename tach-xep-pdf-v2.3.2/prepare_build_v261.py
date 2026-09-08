from pathlib import Path

p = Path('tach-xep-pdf-v2.3.2/build_v232.ps1')
s = p.read_text(encoding='utf-8-sig')

old = "& python (Join-Path $Project 'patch_v260.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v260.py failed' } }"
new = "& python (Join-Path $Project 'patch_v260.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v260.py failed' }; & python (Join-Path $Project 'patch_v261.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v261.py failed' } }"
if old not in s:
    raise SystemExit('v2.6.0 patch-chain marker missing')
s = s.replace(old, new, 1)

s = s.replace('release-v2.6.0', 'release-v2.6.1').replace('v2.6.0', 'v2.6.1').replace('2.6.0', '2.6.1')

old_req = "'SmoothPreviewPanel','atomic preview swap','Xoay trái 90°'"
new_req = "'SmoothPreviewPanel','atomic preview swap','PreviewPanMouseDown','PreviewPanMouseMove','SetPreviewPanPosition','CanPanPreview','AutoScroll = true','Xoay trái 90°'"
if old_req not in s:
    raise SystemExit('v2.6.0 preview regression marker missing')
s = s.replace(old_req, new_req, 1)

old_snapshot = "(Join-Path $Project 'patch_v260.py'), (Join-Path $Project 'prepare_build_v260.py'), (Join-Path $Project 'regression_test.py'),"
new_snapshot = "(Join-Path $Project 'patch_v260.py'), (Join-Path $Project 'prepare_build_v260.py'), (Join-Path $Project 'patch_v261.py'), (Join-Path $Project 'prepare_build_v261.py'), (Join-Path $Project 'regression_test.py'),"
if old_snapshot not in s:
    raise SystemExit('v2.6.0 source snapshot marker missing')
s = s.replace(old_snapshot, new_snapshot, 1)

marker = 'Đã sửa v2.6.1:'
if marker in s:
    s = s.replace(marker, marker + '\n- Bổ sung kéo chuột trực tiếp để pan trang PDF khi phóng to, dùng chính SmoothPreviewPanel/AutoScroll hiện có.\n- Pan chỉ thay đổi tọa độ viewport; không render lại PDF, không đổi trang, không sửa cache, history, source_order hay trạng thái tệp.\n- Giữ nguyên pipeline chuyển trang real-page cache + atomic preview swap của v2.6.0.\n- Nút Vừa cửa sổ đưa zoom về 100% và reset scroll viewport.\n- Regression smoke kiểm tra pan rồi chuyển trang lên/xuống vẫn hiển thị đúng trang, không blank/thumbnail trung gian.\n', 1)

p.write_text(s, encoding='utf-8-sig')
print('PREPARE_BUILD_V261_OK')
