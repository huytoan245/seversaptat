from pathlib import Path

p = Path('tach-xep-pdf-v2.3.2/build_v232.ps1')
s = p.read_text(encoding='utf-8-sig')

old = "; & python (Join-Path $Project 'patch_v270_launcher.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v270_launcher.py failed' } }"
new = "; & python (Join-Path $Project 'patch_v270_launcher.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v270_launcher.py failed' }; & python (Join-Path $Project 'patch_v280.py'); if ($LASTEXITCODE -ne 0) { throw 'patch_v280.py failed' } }"
if old not in s:
    raise SystemExit('v2.7 final patch-chain marker missing')
s = s.replace(old, new, 1)

s = s.replace('release-v2.7.0', 'release-v2.8.0').replace('v2.7.0', 'v2.8.0').replace('2.7.0', '2.8.0')

old_snapshot = "(Join-Path $Project 'patch_v270_launcher.py'), (Join-Path $Project 'prepare_build_v270.py'), (Join-Path $Project 'regression_test.py'),"
new_snapshot = "(Join-Path $Project 'patch_v270_launcher.py'), (Join-Path $Project 'prepare_build_v270.py'), (Join-Path $Project 'patch_v280.py'), (Join-Path $Project 'prepare_build_v280.py'), (Join-Path $Project 'regression_test.py'),"
if old_snapshot not in s:
    raise SystemExit('v2.7 source snapshot marker missing')
s = s.replace(old_snapshot, new_snapshot, 1)

contract_anchor = "'RunWorkflowSmokeAsync','Application.Run();','Xoay trái 90°'"
contract_new = "'RunWorkflowSmokeAsync','Application.Run();','HistoryLimit = 10','ReversePageOrder','Đảo ngược thứ tự trang','Quay lại','Tiến lại','CanUseLosslessFullPageExport','WriteLosslessFullPagePdf','CanUseLosslessForIndexes','WriteLosslessSelectedPages','BackupCleanupEverySessions = 3','BackupMaxBytes','RegisterClosedSessionAndMaybeCleanupBackups','doc.WorkPath = doc.OriginalWorkPath','CreateHistoryIcon','100%','125%','150%','200%','UiTheme.Completed','Xoay trái 90°'"
if contract_anchor not in s:
    raise SystemExit('v2.7 protected-contract marker missing')
s = s.replace(contract_anchor, contract_new, 1)

marker = 'Đã sửa v2.8.0:'
if marker in s:
    notes = ('\n- Đưa Ghép PDF, Tách trang và Đảo ngược thứ tự lên trực tiếp vùng công cụ dưới nhóm xoay; menu trang ưu tiên Lên đầu/Xuống cuối/Lên 1/Xuống 1.'
        '\n- Đảo ngược toàn bộ thứ tự trang trước hoặc sau khi chia và lưu đúng vào PDF nguồn khi dùng Lưu vào file gốc.'
        '\n- Đổi Hoàn tác/Làm lại thành Quay lại/Tiến lại, icon mũi tên vòng tự vẽ, tối đa 10 bước cho cả Undo và Redo.'
        '\n- Preview có lựa chọn nhanh 100/125/150/200%, nút +/- và Vừa cửa sổ; Pan vẫn chỉ thay viewport.'
        '\n- Trạng thái Đã hoàn thành hiển thị xanh; khi chuyển thư mục tự loại tệp hoàn thành trước, còn tệp chưa hoàn thành thì cảnh báo trước khi bỏ khỏi workspace.'
        '\n- Session dùng copy-on-write: lúc mở chỉ tạo một original-at-open bất biến; work revision riêng chỉ sinh khi ghép vật lý.'
        '\n- Backup dọn tự động sau mỗi 3 phiên hoặc khi vượt 2GB; giữ bản mới nhất; session rác cũ được dọn an toàn.'
        '\n- Xuất/tách full-page dùng đường lossless PDFsharp: giữ nguyên content/vector/image, chỉ đổi thứ tự/góc xoay; trang cắt dùng fallback v2.7 để tránh regression chất lượng.'
        '\n- Tự xoay giữ nguyên RenderPageMax 1700 để không đổi độ chính xác, tái sử dụng ONNX session và chỉ bỏ 2 inference vùng phụ khi toàn trang cực kỳ chắc chắn.')
    s = s.replace(marker, marker + notes + '\n', 1)

p.write_text(s, encoding='utf-8-sig')
print('PREPARE_BUILD_V280_OK')
