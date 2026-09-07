from pathlib import Path

p = Path('tach-xep-pdf-v2.3.2/build_v232.ps1')
s = p.read_text(encoding='utf-8-sig')

# Advance release identity after prepare_build_v241 has produced the v2.4.1 build script.
s = s.replace('release-v2.4.1', 'release-v2.4.2').replace('v2.4.1', 'v2.4.2').replace('2.4.1', '2.4.2')

# Apply the v2.4.2 source patch after all v2.4.1 hardening patches.
old = "& python (Join-Path $Project 'patch_v241d.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v241d.py failed' } }"
new = "& python (Join-Path $Project 'patch_v241d.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v241d.py failed' }; & python (Join-Path $Project 'patch_v242.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v242.py failed' } }"
if old not in s:
    raise SystemExit('v241d invocation marker missing')
s = s.replace(old, new, 1)

# Run v2.4.2 regression normalization AFTER v2.4.1 regression patch, because v2.4.1 intentionally
# changed the old label away from "Vừa cửa sổ".
old = "& python (Join-Path $Project 'patch_regression_v241.py')\nif ($LASTEXITCODE -ne 0) { throw 'patch_regression_v241.py failed' }"
new = "& python (Join-Path $Project 'patch_regression_v241.py')\nif ($LASTEXITCODE -ne 0) { throw 'patch_regression_v241.py failed' }\n& python (Join-Path $Project 'patch_regression_v242.py')\nif ($LASTEXITCODE -ne 0) { throw 'patch_regression_v242.py failed' }"
if old not in s:
    raise SystemExit('v241 regression invocation marker missing')
s = s.replace(old, new, 1)

# The old slider workflow is now the required regression contract again.
s = s.replace("'Vừa màn hình'", "'Vừa cửa sổ'")
# v2.4.1 source audit required the three preset buttons. They are intentionally removed in v2.4.2.
for obsolete in ("'125%',", "'150%',", "'200%',"):
    s = s.replace(obsolete, '')
old = "'PDF preview aspect ratio mismatch','.restore.rollback','Vừa cửa sổ','Rotated PDF preview was stretched','startup-v2.4.2.log')"
new = "'PDF preview aspect ratio mismatch','.restore.rollback','Vừa cửa sổ','Thu phóng:','TrackBar _zoom','Visible PDF preview zoom slider missing','Rotated PDF preview was stretched','startup-v2.4.2.log')"
if old not in s:
    raise SystemExit('required marker tail missing')
s = s.replace(old, new, 1)

# Include v2.4.2 patch/build scripts in source handoff.
old = "(Join-Path $Project 'patch_v241d.py'), (Join-Path $Project 'patch_regression_v241.py'), (Join-Path $Project 'prepare_build_v240.py'), (Join-Path $Project 'prepare_build_v241.py'), (Join-Path $Project 'regression_test.py'),"
new = "(Join-Path $Project 'patch_v241d.py'), (Join-Path $Project 'patch_v242.py'), (Join-Path $Project 'patch_regression_v241.py'), (Join-Path $Project 'patch_regression_v242.py'), (Join-Path $Project 'prepare_build_v240.py'), (Join-Path $Project 'prepare_build_v241.py'), (Join-Path $Project 'prepare_build_v242.py'), (Join-Path $Project 'regression_test.py'),"
if old not in s:
    raise SystemExit('source snapshot marker missing')
s = s.replace(old, new, 1)

# Handoff notes: explicitly record the root cause and the intentionally restored behavior.
s = s.replace(
    '- Thanh XEM TRƯỚC nay nằm trong layout thật, không dùng overlay: Vừa màn hình, +/- và 125%/150%/200% luôn hiển thị.',
    '- Thanh XEM TRƯỚC nằm trong layout thật, không dùng overlay. v2.4.2 khôi phục đúng kiểu điều khiển cũ đã hoạt động tốt: Thu phóng bằng thanh trượt liên tục, hiển thị % hiện tại và nút Vừa cửa sổ.\n- 100% = vừa cửa sổ; có thể kéo chính xác 90%, 110%... trong khoảng 50%-250%. Khi kéo chỉ thay đổi kích thước preview đã render, không render lại PDF liên tục nên thao tác nhẹ và ít nhấp nháy.'
)
s = s.replace(
    '- Nút được làm lại theo phong cách phẳng hiện đại, tương phản rõ và có trạng thái hover/down.',
    '- Nút được làm lại theo phong cách phẳng hiện đại, tương phản rõ và có trạng thái hover/down.\n- Regression UI bắt buộc kiểm tra TrackBar thu phóng thực sự hiển thị, chọn được 90%, và nút Vừa cửa sổ hoạt động.'
)

p.write_text(s, encoding='utf-8-sig')
print('PREPARE_BUILD_V242_OK')
