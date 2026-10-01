from pathlib import Path
p=Path('tach-xep-pdf-v2.3.2/build_v232.ps1')
s=p.read_text(encoding='utf-8-sig')

old="; & python (Join-Path $Project 'patch_v280_smoke_labels.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v280_smoke_labels.py failed' } }"
new="; & python (Join-Path $Project 'patch_v280_smoke_labels.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v280_smoke_labels.py failed' }; & python (Join-Path $Project 'patch_v290.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v290.py failed' } }"
if old not in s: raise SystemExit('v2.8 final patch-chain marker missing')
s=s.replace(old,new,1)

s=s.replace('release-v2.8.0','release-v2.9.0').replace('v2.8.0','v2.9.0').replace('2.8.0','2.9.0')

old_snapshot="(Join-Path $Project 'patch_v280.py'), (Join-Path $Project 'patch_v280_smoke_labels.py'), (Join-Path $Project 'prepare_build_v280.py'), (Join-Path $Project 'regression_test.py'),"
new_snapshot="(Join-Path $Project 'patch_v280.py'), (Join-Path $Project 'patch_v280_smoke_labels.py'), (Join-Path $Project 'prepare_build_v280.py'), (Join-Path $Project 'patch_v290.py'), (Join-Path $Project 'prepare_build_v290.py'), (Join-Path $Project 'regression_test.py'),"
if old_snapshot not in s: raise SystemExit('v2.8 source snapshot marker missing')
s=s.replace(old_snapshot,new_snapshot,1)

contract="'RunWorkflowSmokeAsync','Application.Run();','HistoryLimit = 10'"
contract_new="'RunWorkflowSmokeAsync','Application.Run();','SaveAllModifiedToOriginalAsync','SaveCurrentToOriginalBatchCoreAsync','HasUnsavedChanges','Lưu tất cả vào bản gốc','HistoryLimit = 10'"
if contract not in s: raise SystemExit('v2.8 protected-contract anchor missing')
s=s.replace(contract,contract_new,1)

marker='Đã sửa v2.9.0:'
if marker in s:
    notes=('\n- Bổ sung nút Lưu tất cả vào bản gốc, cùng nhóm màu xanh với Lưu vào file gốc.'
           '\n- Chỉ các PDF thực sự có thay đổi chưa lưu mới được xử lý; file chỉ mở/xem được bỏ qua.'
           '\n- Mỗi PDF dùng nguyên cơ chế backup, ValidateGeneratedPdf và rollback an toàn của v2.8; một file lỗi không làm dừng các file còn lại.'
           '\n- Sau khi lưu thành công, trạng thái file chuyển Đã hoàn thành và cờ thay đổi chưa lưu được xóa; file lỗi vẫn giữ trạng thái để xử lý lại.')
    s=s.replace(marker,marker+notes+'\n',1)

p.write_text(s,encoding='utf-8-sig')
print('PREPARE_BUILD_V290_OK')
