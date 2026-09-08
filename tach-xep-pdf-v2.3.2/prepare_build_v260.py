from pathlib import Path
import subprocess
import sys

# Normalize the v2.6 patch itself before it is called by the reconstructed build script.
# These two small preparation steps make the patch tolerant of the established export signature
# and provide a MainForm-local control finder for the new responsive navigation layout.
for fixer_name in ['fix_patch_v260_export_signature.py', 'fix_patch_v260_findcontrol.py']:
    fixer = Path('tach-xep-pdf-v2.3.2') / fixer_name
    subprocess.run([sys.executable, str(fixer)], check=True)

p = Path('tach-xep-pdf-v2.3.2/build_v232.ps1')
s = p.read_text(encoding='utf-8-sig')

# Chain v2.6.0 on top of the fully reconstructed/tested v2.5.0 source.
old = "& python (Join-Path $Project 'patch_v250b.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v250b.py failed' } }"
new = "& python (Join-Path $Project 'patch_v250b.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v250b.py failed' }; & python (Join-Path $Project 'patch_v260.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v260.py failed' } }"
if old not in s:
    raise SystemExit('v2.5.0 final patch-chain marker missing')
s = s.replace(old, new, 1)

# Release/build identity. Managed/launcher identity is also patched in patch_v260.py.
s = s.replace('release-v2.5.0', 'release-v2.6.0').replace('v2.5.0', 'v2.6.0').replace('2.5.0', '2.6.0')

# Preserve every v2.5 safety contract and add the new workflow-status/navigation guards.
old_marker = "'DocumentWorkspace','TỆP ĐANG XỬ LÝ','dlg.Multiselect = true','PersistActiveDocumentState','ActivateDocument','ClampSplitterForResize','AssertButtonTextFits'"
new_marker = "'DocumentWorkspace','DocumentProcessingState','TỆP ĐANG XỬ LÝ','Trạng thái','Chưa xử lý','Đang xử lý','Đã hoàn thành','MarkActiveDocumentCompleted','dlg.Multiselect = true','PersistActiveDocumentState','ActivateDocument','ClampSplitterForResize','LayoutPageNavigationButtons','AssertButtonTextFits'"
if old_marker not in s:
    raise SystemExit('v2.5.0 multi-file regression marker missing')
s = s.replace(old_marker, new_marker, 1)

# Include v2.6.0 patch/preparation in source handoff. patch_v260.py has already been normalized
# in this build workspace, so the handed-off patch is directly reusable without the fixers.
old_snapshot = "(Join-Path $Project 'patch_v250.py'), (Join-Path $Project 'patch_v250b.py'), (Join-Path $Project 'prepare_build_v250.py'), (Join-Path $Project 'regression_test.py'),"
new_snapshot = "(Join-Path $Project 'patch_v250.py'), (Join-Path $Project 'patch_v250b.py'), (Join-Path $Project 'prepare_build_v250.py'), (Join-Path $Project 'patch_v260.py'), (Join-Path $Project 'prepare_build_v260.py'), (Join-Path $Project 'regression_test.py'),"
if old_snapshot not in s:
    raise SystemExit('v2.5.0 source snapshot marker missing')
s = s.replace(old_snapshot, new_snapshot, 1)

marker = 'Đã sửa v2.6.0:'
if marker in s:
    s = s.replace(marker, marker + '\n- Cột TỆP ĐANG XỬ LÝ có cột Trạng thái riêng: Chưa xử lý / Đang xử lý / Đã hoàn thành.\n- Tệp vừa thêm nhưng chưa mở giữ Chưa xử lý; khi bắt đầu làm chuyển Đang xử lý; chỉ sau khi xuất/lưu PDF thành công mới chuyển Đã hoàn thành.\n- Nếu chỉnh sửa lại một tệp đã hoàn thành, trạng thái tự quay về Đang xử lý để tránh báo hoàn thành sai.\n- Bổ sung kiểm soát layout cho đủ bốn nút Lên 1 / Xuống 1 / Lên đầu / Xuống cuối; khi cột hẹp hàng nút tự tăng chiều cao thay vì cắt mất Xuống cuối.\n- Không thay đổi thuật toán chia/sắp xếp, source_order, xoay, xóa, Undo/Redo, preview, Auto Rotate, backup/restore hoặc engine xuất PDF.\n', 1)

p.write_text(s, encoding='utf-8-sig')
print('PREPARE_BUILD_V260_OK')
