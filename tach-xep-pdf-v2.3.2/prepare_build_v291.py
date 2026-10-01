from pathlib import Path
p=Path('tach-xep-pdf-v2.3.2/build_v232.ps1')
s=p.read_text(encoding='utf-8-sig')

old="; & python (Join-Path $Project 'patch_v290_layout_fix.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v290_layout_fix.py failed' } }"
new="; & python (Join-Path $Project 'patch_v290_layout_fix.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v290_layout_fix.py failed' }; & python (Join-Path $Project 'patch_v291.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v291.py failed' }; & python (Join-Path $Project 'patch_v291_launcher.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v291_launcher.py failed' } }"
if old not in s: raise SystemExit('v2.9 final patch-chain marker missing')
s=s.replace(old,new,1)

s=s.replace('release-v2.9.0','release-v2.9.1').replace('v2.9.0','v2.9.1').replace('2.9.0','2.9.1')

old_snapshot="(Join-Path $Project 'patch_v290.py'), (Join-Path $Project 'patch_v290_layout_fix.py'), (Join-Path $Project 'prepare_build_v290.py'), (Join-Path $Project 'regression_test.py'),"
new_snapshot="(Join-Path $Project 'patch_v290.py'), (Join-Path $Project 'patch_v290_layout_fix.py'), (Join-Path $Project 'prepare_build_v290.py'), (Join-Path $Project 'patch_v291.py'), (Join-Path $Project 'patch_v291_launcher.py'), (Join-Path $Project 'prepare_build_v291.py'), (Join-Path $Project 'regression_test.py'),"
if old_snapshot not in s: raise SystemExit('v2.9 source snapshot marker missing')
s=s.replace(old_snapshot,new_snapshot,1)

s=s.replace("'Lưu tất cả gốc'", "'Lưu tất cả vào file gốc'")
s=s.replace("'Tiến lại'", "'Tiến lên'")

marker='Đã sửa v2.9.1:'
if marker in s:
    notes=('\n- Đưa Lưu tất cả vào file gốc lên ngay sát Lưu vào file gốc; hàng nút trên dùng kích thước compact riêng để vẫn vừa ở cửa sổ tối thiểu.'
           '\n- Bốn nút Lên 1, Xuống 1, Lên đầu, Xuống cuối luôn nằm cùng một hàng trong cột Thứ tự trang.'
           '\n- Đổi Tiến lại thành Tiến lên; Quay lại/Tiến lên giữ nhãn cố định và dùng icon mũi tên vòng 24px nét đậm, dễ nhận biết hơn.'
           '\n- Không thay đổi engine PDF, backup, lossless export, AI, multi-file hay Save All của v2.9.0.')
    s=s.replace(marker,marker+notes+'\n',1)

p.write_text(s,encoding='utf-8-sig')
print('PREPARE_BUILD_V291_OK')
