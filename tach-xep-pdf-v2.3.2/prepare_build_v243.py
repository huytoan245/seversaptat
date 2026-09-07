from pathlib import Path
p=Path('tach-xep-pdf-v2.3.2/build_v232.ps1')
s=p.read_text(encoding='utf-8-sig')

# Advance the whole release identity after v2.4.2 preparation.
s=s.replace('release-v2.4.2','release-v2.4.3').replace('v2.4.2','v2.4.3').replace('2.4.2','2.4.3')

# Apply v2.4.3 only after the complete v2.4.2 patch chain.
old="& python (Join-Path $Project 'patch_v242.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v242.py failed' } }"
new="& python (Join-Path $Project 'patch_v242.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v242.py failed' }; & python (Join-Path $Project 'patch_v243.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v243.py failed' } }"
if old not in s: raise SystemExit('v242 patch-chain marker missing')
s=s.replace(old,new,1)

old="& python (Join-Path $Project 'patch_regression_v242.py')\nif ($LASTEXITCODE -ne 0) { throw 'patch_regression_v242.py failed' }"
new="& python (Join-Path $Project 'patch_regression_v242.py')\nif ($LASTEXITCODE -ne 0) { throw 'patch_regression_v242.py failed' }\n& python (Join-Path $Project 'patch_regression_v243.py')\nif ($LASTEXITCODE -ne 0) { throw 'patch_regression_v243.py failed' }"
if old not in s: raise SystemExit('v242 regression-chain marker missing')
s=s.replace(old,new,1)

# Replace the obsolete 'third pane must be collapsed' contract with the restored v2.1 interaction contract.
s=s.replace("'Panel2Collapsed = true',", "'PreviewZoomSlider','ManualCutSlider','Áp dụng đường cắt','ApplyManualCut','EnsureListSelectionVisible','ShowImmediatePreviewFromThumbnail','SemaphoreSlim _previewRenderGate','--workflow-smoke','RunWorkflowSmoke','Lên 1','Xuống 1','Lên đầu','Xuống cuối',")

# Run an end-to-end interaction smoke through the final portable while outbound network is blocked.
anchor='''    foreach ($t in $tests) {\n'''
workflow='''    $p = Start-Process -FilePath $portable -ArgumentList '--workflow-smoke' -PassThru -Wait\n    if($p.ExitCode -ne 0) {\n        $l1=Join-Path $env:LOCALAPPDATA 'TachXepTrangPDF\\Logs\\launcher-v2.4.3.log'; if(Test-Path $l1){Get-Content $l1}\n        $l2=Join-Path $env:LOCALAPPDATA 'TachXepTrangPDF\\Logs\\startup-v2.4.3.log'; if(Test-Path $l2){Get-Content $l2}\n        throw \"Firewall-blocked workflow smoke test failed: $($p.ExitCode)\"\n    }\n'''
if anchor not in s: raise SystemExit('orientation-loop anchor missing')
s=s.replace(anchor,workflow+anchor,1)

s=s.replace("'OFFLINE_FIREWALL_UI_SMOKE=PASS' | Add-Content (Join-Path $Project 'offline-test.txt')", "'OFFLINE_FIREWALL_UI_SMOKE=PASS' | Add-Content (Join-Path $Project 'offline-test.txt')\n'OFFLINE_FIREWALL_WORKFLOW_SMOKE=PASS' | Add-Content (Join-Path $Project 'offline-test.txt')")

# Source handoff must include the patch and release preparation that actually produced this build.
old="(Join-Path $Project 'patch_v242.py'), (Join-Path $Project 'patch_regression_v241.py'), (Join-Path $Project 'patch_regression_v242.py'), (Join-Path $Project 'prepare_build_v240.py'), (Join-Path $Project 'prepare_build_v241.py'), (Join-Path $Project 'prepare_build_v242.py'), (Join-Path $Project 'regression_test.py'),"
new="(Join-Path $Project 'patch_v242.py'), (Join-Path $Project 'patch_v243.py'), (Join-Path $Project 'patch_regression_v241.py'), (Join-Path $Project 'patch_regression_v242.py'), (Join-Path $Project 'patch_regression_v243.py'), (Join-Path $Project 'prepare_build_v240.py'), (Join-Path $Project 'prepare_build_v241.py'), (Join-Path $Project 'prepare_build_v242.py'), (Join-Path $Project 'prepare_build_v243.py'), (Join-Path $Project 'regression_test.py'),"
if old not in s: raise SystemExit('source handoff list marker missing')
s=s.replace(old,new,1)

# Keep handoff notes aligned with what v2.4.3 actually restores.
s=s.replace('- Giao diện hai cột hiện đại: THỨ TỰ TRANG + XEM TRƯỚC; bỏ hẳn cột thứ ba.', '- Khôi phục bố cục làm việc đã chứng minh ở v2.1.0: THỨ TỰ TRANG + XEM TRƯỚC + CHỈNH ĐƯỜNG CẮT bên phải.')
s=s.replace('- Mở PDF mặc định Vừa cửa sổ; bổ sung thu phóng +/- và nhanh 125%/150%/200%.', '- Mở PDF mặc định Vừa cửa sổ; TrackBar thu phóng liên tục 50%-250%, hiển thị % hiện tại.')
s=s.replace('- Bỏ hoàn toàn cột HƯỚNG DẪN thứ ba; phần xem PDF dùng toàn bộ chiều rộng còn lại.', '- Khôi phục cột CHỈNH ĐƯỜNG CẮT để chỉnh riêng từng mặt cả trước và sau khi chia; mặc định vẫn đúng 50/50.')
s=s.replace('- Khu chỉnh tay và tỷ lệ cắt được tách thành 2 hàng layout riêng, tránh đè nhau ở DPI/cửa sổ khác nhau.', '- Tỷ lệ cắt thủ công dùng thanh trượt 30%-70% và nút Áp dụng đường cắt, không tự thay đổi khi chỉ kéo thử.')
s=s.replace('- Cột trái, preview và hướng dẫn dùng hàng layout riêng nên không còn bị control Fill đè lên header.', '- Cột trái giữ trang 1 nhìn thấy khi chọn trang 2; Preview toolbar dùng SplitContainer hàng ngang riêng để không bị viewport che.')
s=s.replace('- UI smoke xác nhận cột thứ ba bị ẩn hoàn toàn; Vừa cửa sổ + 125%/150%/200% đều hiện: PASS.', '- UI smoke xác nhận TrackBar 50%-250%, Vừa cửa sổ, cột chỉnh đường cắt và 4 nút Lên/Xuống đều thực sự nằm trong viewport: PASS.\n- Workflow smoke thực hiện chia trang, chọn trang 2 vẫn thấy trang 1, preview theo trang ngay, chỉnh cắt sau chia 53.5%, Xuống 1/Lên 1 và zoom 90%→100%: PASS.')

p.write_text(s,encoding='utf-8-sig')
print('PREPARE_BUILD_V243_OK')
