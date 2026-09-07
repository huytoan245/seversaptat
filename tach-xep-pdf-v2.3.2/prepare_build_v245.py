from pathlib import Path
p = Path('tach-xep-pdf-v2.3.2/build_v232.ps1')
s = p.read_text(encoding='utf-8-sig')

# Release identity.
s = s.replace('release-v2.4.4', 'release-v2.4.5').replace('v2.4.4', 'v2.4.5').replace('2.4.4', '2.4.5')

# Apply v2.4.5 after v2.4.4 source has been reconstructed, then harden the
# compact cut pane, preserve geometry diagnostics and make the workflow smoke
# accurately test the async real-page-preview contract.
old = "& python (Join-Path $Project 'patch_v244.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v244.py failed' } }"
new = "& python (Join-Path $Project 'patch_v244.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v244.py failed' }; & python (Join-Path $Project 'patch_v245.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v245.py failed' }; & python (Join-Path $Project 'patch_v245b.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v245b.py failed' }; & python (Join-Path $Project 'patch_v245c.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v245c.py failed' }; & python (Join-Path $Project 'patch_v245d.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v245d.py failed' }; & python (Join-Path $Project 'patch_v245e.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v245e.py failed' } }"
if old not in s:
    raise SystemExit('v2.4.4 patch-chain marker missing')
s = s.replace(old, new, 1)

# The old tiny-thumbnail preview is intentionally retired. Protect the new real-page cache/prefetch path instead.
old = "'EnsureListSelectionVisible','ShowImmediatePreviewFromThumbnail','SemaphoreSlim _previewRenderGate'"
new = "'EnsureListSelectionVisible','PreviewCacheKey','SchedulePreviewPrefetch','PreviewCacheCapacity','TryGetCachedPreview','SemaphoreSlim _previewRenderGate','ConfigureRightPaneRatio(inner, 0.14, 215, 260)','cutPanel.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100))','cached real preview did not switch immediately'"
if old not in s:
    raise SystemExit('v2.4.4 preview regression marker missing')
s = s.replace(old, new, 1)

# Include the v2.4.5 patch/preparation in the source handoff snapshot.
old = "(Join-Path $Project 'patch_v244.py'), (Join-Path $Project 'prepare_build_v244.py'), (Join-Path $Project 'regression_test.py'),"
new = "(Join-Path $Project 'patch_v244.py'), (Join-Path $Project 'prepare_build_v244.py'), (Join-Path $Project 'patch_v245.py'), (Join-Path $Project 'patch_v245b.py'), (Join-Path $Project 'patch_v245c.py'), (Join-Path $Project 'patch_v245d.py'), (Join-Path $Project 'patch_v245e.py'), (Join-Path $Project 'prepare_build_v245.py'), (Join-Path $Project 'regression_test.py'),"
if old not in s:
    raise SystemExit('v2.4.4 source snapshot marker missing')
s = s.replace(old, new, 1)

marker = 'Đã sửa v2.4.5:'
if marker in s:
    s = s.replace(marker, marker + '\n- Bỏ hoàn toàn ảnh thumbnail 104x78 làm Preview trung gian; mỗi lần đổi trang chỉ có một lần đổi bitmap thật.\n- Thêm Preview cache LRU 7 trang và prefetch các trang lân cận bằng PdfSession riêng để phím Lên/Xuống phản hồi nhanh mà không chặn render trang đang chọn.\n- Cache key chứa rotation/cut/half nên chỉnh xoay hoặc đường cắt không tái dùng ảnh cũ.\n- Giữ nguyên trang cũ cho tới khi trang mới render xong nếu cache chưa có; không chen frame trắng/xám hay thumbnail méo.\n- Thu gọn top chrome ở cửa sổ rộng xuống khoảng 184 px; cửa sổ thường tự tăng chiều cao toolbar và cho các nút chỉnh tay wrap để không bị cắt.\n- Sửa nguyên nhân cột CHỈNH ĐƯỜNG CẮT tràn: ép TableLayoutPanel dùng đúng 100% chiều rộng cột thay vì AutoSize theo tiêu đề, đồng thời giữ cột đủ rộng ở màn hình hẹp/DPI scaling.\n- Workflow smoke phân biệt đúng hai trường hợp: trang chưa cache được phép render nền nhưng không được chớp trắng/thumbnail; trang đã cache phải đổi ngay lập tức.\n- UI smoke được siết chặt: control phải nằm trọn trong cửa sổ, không chỉ giao nhau một phần.\n', 1)

p.write_text(s, encoding='utf-8-sig')
print('PREPARE_BUILD_V245_OK')
