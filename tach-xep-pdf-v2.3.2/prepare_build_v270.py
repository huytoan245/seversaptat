from pathlib import Path

p = Path('tach-xep-pdf-v2.3.2/build_v232.ps1')
s = p.read_text(encoding='utf-8-sig')

old = "& python (Join-Path $Project 'patch_v260.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v260.py failed' }; & python (Join-Path $Project 'patch_v261.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v261.py failed' }; & python (Join-Path $Project 'patch_v261_identity.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v261_identity.py failed' }; & python (Join-Path $Project 'patch_v261_scroll_extent.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v261_scroll_extent.py failed' } }"
new = "& python (Join-Path $Project 'patch_v260.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v260.py failed' }; & python (Join-Path $Project 'patch_v261.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v261.py failed' }; & python (Join-Path $Project 'patch_v261_identity.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v261_identity.py failed' }; & python (Join-Path $Project 'patch_v261_scroll_extent.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v261_scroll_extent.py failed' }; & python (Join-Path $Project 'patch_v270.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v270.py failed' }; & python (Join-Path $Project 'patch_v270b.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v270b.py failed' } }"
if old not in s:
    raise SystemExit('v2.6.1 final patch-chain marker missing')
s = s.replace(old, new, 1)

s = s.replace('release-v2.6.1', 'release-v2.7.0').replace('v2.6.1', 'v2.7.0').replace('2.6.1', '2.7.0')

old_req = "'PreviewPanMouseDown','PreviewPanMouseMove','SetPreviewPanPosition','CanPanPreview','AutoScroll = true','AutoScrollMinSize','Xoay trái 90°'"
new_req = "'PreviewPanMouseDown','PreviewPanMouseMove','SetPreviewPanPosition','CanPanPreview','AutoScroll = true','AutoScrollMinSize','PdfPageComposer','OriginalWorkPath','PrepareDocumentListForOpen','RemoveSelectedFileFromList','ClearAllDocumentsFromButton','RemoveDocumentWorkspace','ClearAllDocumentsCore','MergePdfIntoCurrentAsync','ExtractPagesAsync','ImportedFullPage','Xoay trái 90°'"
if old_req not in s:
    raise SystemExit('v2.6.1 protected preview marker missing')
s = s.replace(old_req, new_req, 1)

old_snapshot = "(Join-Path $Project 'patch_v260.py'), (Join-Path $Project 'prepare_build_v260.py'), (Join-Path $Project 'patch_v261.py'), (Join-Path $Project 'patch_v261_identity.py'), (Join-Path $Project 'patch_v261_scroll_extent.py'), (Join-Path $Project 'prepare_build_v261.py'), (Join-Path $Project 'regression_test.py'),"
new_snapshot = "(Join-Path $Project 'patch_v260.py'), (Join-Path $Project 'prepare_build_v260.py'), (Join-Path $Project 'patch_v261.py'), (Join-Path $Project 'patch_v261_identity.py'), (Join-Path $Project 'patch_v261_scroll_extent.py'), (Join-Path $Project 'prepare_build_v261.py'), (Join-Path $Project 'patch_v270.py'), (Join-Path $Project 'patch_v270b.py'), (Join-Path $Project 'prepare_build_v270.py'), (Join-Path $Project 'regression_test.py'),"
if old_snapshot not in s:
    raise SystemExit('v2.6.1 source snapshot marker missing')
s = s.replace(old_snapshot, new_snapshot, 1)

marker = 'Đã sửa v2.7.0:'
if marker in s:
    s = s.replace(marker, marker + '\n- Khi Mở PDF sang thư mục khác: nếu danh sách cũ đã hoàn thành thì tự dọn; nếu còn tệp chưa hoàn thành phải hỏi trước để tránh mất trạng thái phiên.\n- Cột TỆP ĐANG XỬ LÝ có nút Xóa tệp và Xóa tất cả; chỉ xóa khỏi phiên làm việc, không xóa PDF trên ổ đĩa.\n- Ghép thêm PDF dùng PDFsharp import/copy trang vào work-copy revision mới, không rasterize file nguồn và không chạm file gốc trước khi Lưu/Xuất.\n- Giữ OriginalWorkPath bất biến để backup/Khôi phục PDF gốc luôn quay về đúng file lúc mở, kể cả sau nhiều lần ghép/Undo/Redo.\n- Trang PDF ghép được đánh dấu ImportedFullPage và không bị chia đôi khi chạy TỰ CHIA & SẮP XẾP.\n- Tách trang hỗ trợ phạm vi 1-3,5,8-10; xuất đúng trạng thái chỉnh sửa hiện tại ra PDF mới và không thay đổi tài liệu đang làm.\n- Regression bổ sung xác minh Xóa tệp/Xóa tất cả chỉ dọn workspace, tuyệt đối không xóa PDF nguồn.\n- Bảo toàn Preview Pan, real-page cache/prefetch, atomic swap, source_order, multi-PDF, manual cut, rotate, Undo/Redo, export/backup hiện có.\n', 1)

p.write_text(s, encoding='utf-8-sig')
print('PREPARE_BUILD_V270_OK')
