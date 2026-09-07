from pathlib import Path
p=Path('tach-xep-pdf-v2.3.2/build_v232.ps1')
s=p.read_text(encoding='utf-8-sig')

s=s.replace('release-v2.4.0','release-v2.4.1').replace('v2.4.0','v2.4.1').replace('2.4.0','2.4.1')

old="& python (Join-Path $Project 'patch_v240b.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v240b.py failed' } }"
new="& python (Join-Path $Project 'patch_v240b.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v240b.py failed' }; & python (Join-Path $Project 'patch_v241.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v241.py failed' }; & python (Join-Path $Project 'patch_v241b.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v241b.py failed' }; & python (Join-Path $Project 'patch_v241c.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v241c.py failed' } }"
if old not in s: raise SystemExit('v240b invocation marker missing')
s=s.replace(old,new,1)

old="'PDF preview aspect ratio mismatch','.restore.rollback')"
new="'PDF preview aspect ratio mismatch','.restore.rollback','Vừa màn hình','Rotated PDF preview was stretched','startup-v2.4.1.log')"
if old not in s: raise SystemExit('required marker tail missing')
s=s.replace(old,new,1)

old="(Join-Path $Project 'patch_v240b.py'), (Join-Path $Project 'prepare_build_v240.py'), (Join-Path $Project 'regression_test.py'),"
new="(Join-Path $Project 'patch_v240b.py'), (Join-Path $Project 'patch_v241.py'), (Join-Path $Project 'patch_v241b.py'), (Join-Path $Project 'patch_v241c.py'), (Join-Path $Project 'prepare_build_v240.py'), (Join-Path $Project 'prepare_build_v241.py'), (Join-Path $Project 'regression_test.py'),"
if old not in s: raise SystemExit('source list marker missing')
s=s.replace(old,new,1)

# Dump both canonical and any legacy startup log if UI smoke fails.
old="""        $l2=Join-Path $env:LOCALAPPDATA 'TachXepTrangPDF\\Logs\\startup-v2.4.1.log'; if(Test-Path $l2){Get-Content $l2}\n        throw \"Firewall-blocked UI smoke test failed: $($p.ExitCode)\""""
new="""        $l2=Join-Path $env:LOCALAPPDATA 'TachXepTrangPDF\\Logs\\startup-v2.4.1.log'; if(Test-Path $l2){Get-Content $l2}\n        Get-ChildItem (Join-Path $env:LOCALAPPDATA 'TachXepTrangPDF\\Logs\\startup-v*.log') -ErrorAction SilentlyContinue | ForEach-Object { Write-Host \"DIAG_LOG=$($_.FullName)\"; Get-Content $_.FullName }\n        $smoke=Join-Path $runtimeRoot 'ui-smoke-failure.txt'; if(Test-Path $smoke){Write-Host 'UI_SMOKE_FAILURE_FILE:'; Get-Content $smoke}\n        throw \"Firewall-blocked UI smoke test failed: $($p.ExitCode)\""""
if old not in s: raise SystemExit('ui-smoke failure log marker missing')
s=s.replace(old,new,1)

s=s.replace('- Giao diện hai cột hiện đại: THỨ TỰ TRANG + XEM TRƯỚC; bỏ hẳn cột thứ ba.','- Giao diện hai cột hiện đại: THỨ TỰ TRANG + XEM TRƯỚC; bỏ hẳn cột thứ ba.\n- Thanh XEM TRƯỚC nay nằm trong layout thật, không dùng overlay: Vừa màn hình, +/- và 125%/150%/200% luôn hiển thị.')
s=s.replace('- Renderer preview tăng độ phân giải nhưng khóa đúng tỷ lệ MediaBox; thêm self-test chống méo.','- Renderer Windows.Data.Pdf không còn ép đồng thời DestinationWidth + DestinationHeight. Chỉ truyền chiều rộng để Windows tự giữ aspect ratio, kể cả PDF có /Rotate 90/180/270.\n- GetPageDipSize dùng PdfPage.Size (kích thước hiển thị hiệu lực) thay vì MediaBox thô. Có regression PDF /Rotate 90 để chống tái phát méo hình.')
s=s.replace('- Khôi phục file vật lý dùng atomic replace; fallback có rollback an toàn nếu thao tác thay thế lỗi.','- Khôi phục file vật lý dùng atomic replace; fallback có rollback an toàn nếu thao tác thay thế lỗi.\n- Thanh thao tác bỏ cột trống 285px và nhãn Chỉnh tay bị cắt; Chiều cắt chuyển thành inline control DPI-safe.\n- Nút được làm lại theo phong cách phẳng hiện đại, tương phản rõ và có trạng thái hover/down.')

p.write_text(s,encoding='utf-8-sig')
print('PREPARE_BUILD_V241_OK')