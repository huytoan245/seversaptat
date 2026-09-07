from pathlib import Path
p=Path('tach-xep-pdf-v2.3.2/build_v232.ps1')
s=p.read_text(encoding='utf-8-sig')

s=s.replace('release-v2.3.5','release-v2.4.0').replace('v2.3.5','v2.4.0').replace('2.3.5','2.4.0')

old="& python (Join-Path $Project 'patch_v235g.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v235g.py failed' } }"
new="& python (Join-Path $Project 'patch_v235g.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v235g.py failed' }; & python (Join-Path $Project 'patch_v240.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v240.py failed' } }"
if old not in s: raise SystemExit('v235g invocation marker missing')
s=s.replace(old,new,1)

old="'ConfigureRightPaneRatio')"
new="'ConfigureRightPaneRatio','Khôi phục PDF gốc','RESTORE_ORIGINAL_FAIL','Panel2Collapsed = true','125%','150%','200%','SetZoomPercent','PDF preview aspect ratio mismatch')"
if old not in s: raise SystemExit('required marker tail missing')
s=s.replace(old,new,1)

old="(Join-Path $Project 'prepare_build_v235f.py'), (Join-Path $Project 'regression_test.py'),"
new="(Join-Path $Project 'prepare_build_v235f.py'), (Join-Path $Project 'patch_v240.py'), (Join-Path $Project 'prepare_build_v240.py'), (Join-Path $Project 'regression_test.py'),"
if old not in s: raise SystemExit('source list marker missing')
s=s.replace(old,new,1)

s=s.replace('- Cột HƯỚNG DẪN giữ khoảng 10-15% chiều rộng thay vì phình theo màn hình.','- Bỏ hoàn toàn cột HƯỚNG DẪN thứ ba; phần xem PDF dùng toàn bộ chiều rộng còn lại.')
s=s.replace('- Làm lại đặt trước Hoàn tác; CHIỀU CẮT chuyển sang phía sau khu chỉnh tay.','- Làm lại vẫn là Redo; Khôi phục PDF gốc là chức năng riêng. CHIỀU CẮT nằm sát nhóm Hoàn tác/Làm lại.')
s=s.replace('- UI smoke xác nhận có nút Vừa cửa sổ và cột hướng dẫn không vượt 17% cửa sổ: PASS.','- UI smoke xác nhận cột thứ ba bị ẩn hoàn toàn; Vừa cửa sổ + 125%/150%/200% đều hiện: PASS.')
s=s.replace('- Source regression xác nhận PictureBoxSizeMode.Zoom + thumbnail FitCanvas + SelectAdjacent: PASS.','- Source/runtime regression xác nhận PictureBoxSizeMode.Zoom + thumbnail FitCanvas + SelectAdjacent + restore-original + aspect-ratio guard: PASS.')
marker='Đã sửa v2.4.0:'
if marker in s:
    s=s.replace(marker,marker+'\n- Giao diện hai cột hiện đại: THỨ TỰ TRANG + XEM TRƯỚC; bỏ hẳn cột thứ ba.\n- Mở PDF mặc định Vừa cửa sổ; bổ sung thu phóng +/- và nhanh 125%/150%/200%.\n- Renderer preview tăng độ phân giải nhưng khóa đúng tỷ lệ MediaBox; thêm self-test chống méo.\n- Khôi phục PDF gốc được khôi phục đúng nghĩa và tách biệt với Làm lại/Redo.\n- Trước lần lưu đè đầu tiên chỉ giữ một bản gốc an toàn của phiên; không tạo backup lặp mỗi lần lưu.\n',1)

p.write_text(s,encoding='utf-8-sig')
print('PREPARE_BUILD_V240_OK')