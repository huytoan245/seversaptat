from pathlib import Path

p = Path('tach-xep-pdf-v2.3.2/build_v232.ps1')
s = p.read_text(encoding='utf-8-sig')

old = "& python (Join-Path $Project 'patch_v260.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v260.py failed' }; & python (Join-Path $Project 'patch_v261.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v261.py failed' }; & python (Join-Path $Project 'patch_v261_identity.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v261_identity.py failed' }; & python (Join-Path $Project 'patch_v261_scroll_extent.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v261_scroll_extent.py failed' } }"
chain = ['patch_v270_model.py','patch_v270_ui.py','patch_v270_compact_top.py','patch_v270_list.py','patch_v270_merge_extract.py','patch_v270_merge_safety.py','patch_v270_merge_trace.py','patch_v270_tests.py','patch_v270_preview_smoke.py','patch_v270_restore_safe.py','patch_v270_launcher.py']
extra = ''.join("; & python (Join-Path $Project '%s'); if ($LASTEXITCODE -ne 0) { throw '%s failed' }" % (name,name) for name in chain)
new = old[:-2] + extra + ' }'
if old not in s:
    raise SystemExit('v2.6.1 final patch-chain marker missing')
s = s.replace(old, new, 1)

s = s.replace('release-v2.6.1', 'release-v2.7.0').replace('v2.6.1', 'v2.7.0').replace('2.6.1', '2.7.0')

project_write = "Set-Content (Join-Path $Project 'TachXepTrangPDF.csproj') $proj -Encoding UTF8"
if project_write not in s:
    raise SystemExit('generated csproj write marker missing')
pdfsharp_line = "$proj = $proj.Replace('<PackageReference Include=\"Microsoft.ML.OnnxRuntime\" Version=\"1.22.1\" />', '<PackageReference Include=\"Microsoft.ML.OnnxRuntime\" Version=\"1.22.1\" />' + [Environment]::NewLine + '    <PackageReference Include=\"PDFsharp\" Version=\"6.2.4\" />')"
s = s.replace(project_write, pdfsharp_line + "\n" + project_write, 1)

old_req = "'PreviewPanMouseDown','PreviewPanMouseMove','SetPreviewPanPosition','CanPanPreview','AutoScroll = true','AutoScrollMinSize','Xoay trái 90°'"
new_req = "'PreviewPanMouseDown','PreviewPanMouseMove','SetPreviewPanPosition','CanPanPreview','AutoScroll = true','AutoScrollMinSize','UiTheme','PageRangeDialog','PdfPageComposer','OriginalWorkPath','PrepareDocumentListForOpen','RemoveSelectedFileFromList','ClearAllDocumentsFromButton','MergePdfFilesCoreAsync','ExtractSelectedPageAsync','ExtractRangeWithDialogAsync','ExtractPagesToPathAsync','ImportedFullPage','Ghép thêm PDF','Tách trang','Xóa tệp','Xóa tất cả','.restore.rollback','.replace.rollback','work-merged-','PREVIEW_PREFETCH_SCHEDULE_FAIL','MERGE_CORE','Xoay trái 90°'"
if old_req not in s:
    raise SystemExit('v2.6.1 protected preview marker missing')
s = s.replace(old_req, new_req, 1)

old_snapshot = "(Join-Path $Project 'patch_v260.py'), (Join-Path $Project 'prepare_build_v260.py'), (Join-Path $Project 'patch_v261.py'), (Join-Path $Project 'patch_v261_identity.py'), (Join-Path $Project 'patch_v261_scroll_extent.py'), (Join-Path $Project 'prepare_build_v261.py'), (Join-Path $Project 'regression_test.py'),"
new_snapshot = "(Join-Path $Project 'patch_v260.py'), (Join-Path $Project 'prepare_build_v260.py'), (Join-Path $Project 'patch_v261.py'), (Join-Path $Project 'patch_v261_identity.py'), (Join-Path $Project 'patch_v261_scroll_extent.py'), (Join-Path $Project 'prepare_build_v261.py'), (Join-Path $Project 'patch_v270_model.py'), (Join-Path $Project 'patch_v270_ui.py'), (Join-Path $Project 'patch_v270_compact_top.py'), (Join-Path $Project 'patch_v270_list.py'), (Join-Path $Project 'patch_v270_merge_extract.py'), (Join-Path $Project 'patch_v270_merge_safety.py'), (Join-Path $Project 'patch_v270_merge_trace.py'), (Join-Path $Project 'patch_v270_tests.py'), (Join-Path $Project 'patch_v270_preview_smoke.py'), (Join-Path $Project 'patch_v270_restore_safe.py'), (Join-Path $Project 'patch_v270_launcher.py'), (Join-Path $Project 'prepare_build_v270.py'), (Join-Path $Project 'regression_test.py'),"
if old_snapshot not in s:
    raise SystemExit('v2.6.1 source snapshot marker missing')
s = s.replace(old_snapshot, new_snapshot, 1)

marker = 'Đã sửa v2.7.0:'
if marker in s:
    notes = ('\n- Mở PDF ở thư mục mới: tự dọn danh sách cũ khi tất cả tệp đã hoàn thành; nếu còn tệp chưa hoàn thành sẽ hỏi trước, không xóa PDF nguồn.'
        '\n- Thêm Xóa tệp / Xóa tất cả chỉ xóa workspace khỏi phiên.'
        '\n- Ghép PDF được cả trước khi chia và sau khi chia: trước khi chia trở thành trang nguồn bình thường; sau khi chia giữ nguyên trang đầy đủ.'
        '\n- Ghép dùng work-copy revision mới, không replace work.pdf đang có thể bị Preview/Prefetch giữ handle; bản work cũ là rollback an toàn.'
        '\n- Prefetch được cô lập như tối ưu nền; race session/list không được phép làm hỏng Preview chính.'
        '\n- Ghép ở bản gốc rồi bấm Lưu vào file gốc sẽ ghi đúng kết quả hiện tại vào PDF nguồn, sau khi đã tạo bản gốc bất biến an toàn.'
        '\n- Khôi phục PDF gốc dùng original-at-open bất biến và replace rollback-safe cho cả file nguồn lẫn work-copy.'
        '\n- Tách riêng một trang đang chọn và tách dải trang liên tục bao gồm cả hai đầu, ví dụ 4-8 tạo đúng 5 trang.'
        '\n- Menu chuột phải trên tệp và trên từng trang: ghép, tách, xoay, xóa, di chuyển.'
        '\n- Giao diện Fluent-like trên .NET 8 WinForms, Segoe UI Variable Text fallback, đo kích thước chữ DPI-safe; cột chỉnh đường cắt hẹp hơn.'
        '\n- Thanh trên giữ compact; ghép/tách nằm trong menu ngữ cảnh để tránh chiếm chiều cao Preview.'
        '\n- Portable launcher dùng runtime cache riêng v2.7.0 để không tái sử dụng payload v2.6.1.'
        '\n- Bảo toàn source_order, Preview Pan, real-page cache/prefetch, atomic swap, multi-PDF, manual cut, rotate, Undo/Redo, backup/restore.')
    s = s.replace(marker, marker + notes + '\n', 1)

p.write_text(s, encoding='utf-8-sig')
print('PREPARE_BUILD_V270_OK')