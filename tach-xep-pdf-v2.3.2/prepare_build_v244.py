from pathlib import Path
p = Path('tach-xep-pdf-v2.3.2/build_v232.ps1')
s = p.read_text(encoding='utf-8-sig')

# Release identity.
s = s.replace('release-v2.4.3', 'release-v2.4.4').replace('v2.4.3', 'v2.4.4').replace('2.4.3', '2.4.4')

# Apply v2.4.4 only after the verified v2.4.3 source has been reconstructed.
old = "Write-Host 'PATCH_V243_VERIFIED_SOURCE_WRITTEN=PASS' } }"
new = "Write-Host 'PATCH_V243_VERIFIED_SOURCE_WRITTEN=PASS' }; & python (Join-Path $Project 'patch_v244.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v244.py failed' } }"
if old not in s:
    raise SystemExit('v2.4.3 patch-chain tail missing')
s = s.replace(old, new, 1)

# Protect the smooth-preview implementation and requested labels in build-time source audit.
old = "'RunWorkflowSmoke','SetZoomPercent'"
new = "'RunWorkflowSmoke','SmoothPreviewPanel','atomic preview swap','Xoay trái 90°','Xoay phải 90°','Xóa trang PDF','SetZoomPercent'"
if old not in s:
    raise SystemExit('required source marker tail missing')
s = s.replace(old, new, 1)

# Include v2.4.4 patch/preparation in source handoff snapshot.
old = "(Join-Path $Project 'patch_v243.py'), (Join-Path $Project 'prepare_build_v243.py'), (Join-Path $Project 'regression_test.py'),"
new = "(Join-Path $Project 'patch_v243.py'), (Join-Path $Project 'prepare_build_v243.py'), (Join-Path $Project 'patch_v244.py'), (Join-Path $Project 'prepare_build_v244.py'), (Join-Path $Project 'regression_test.py'),"
if old not in s:
    raise SystemExit('source snapshot list marker missing')
s = s.replace(old, new, 1)

# Release report additions. Keep all existing v2.4.3 regression protections.
marker = 'Đã sửa v2.4.4:'
if marker in s:
    s = s.replace(marker, marker + '\n- Preview chuyển trang kiểu ổn định như v2.1.0: không xóa ảnh cũ trước khi ảnh mới sẵn sàng; bitmap được đổi atomically trên UI thread.\n- Bật double buffering riêng cho vùng Preview và cửa sổ để loại bỏ khung nền tối nhấp nháy khi đổi trang.\n- Khi người dùng bấm Lên/Xuống nhanh, HQ render được debounce 70 ms; trang đang chọn vẫn hiện ngay bằng cache/thumbnail và chỉ trang cuối cùng được nâng lên HQ.\n- Nếu render Preview hiếm khi lỗi, giữ ảnh đang hiển thị thay vì chớp về nền tối.\n- Đổi nhãn rõ nghĩa: Xoay trái 90°, Xoay phải 90°, Xóa trang PDF.\n', 1)

p.write_text(s, encoding='utf-8-sig')
print('PREPARE_BUILD_V244_OK')
