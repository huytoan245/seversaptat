TÁCH & XẾP TRANG PDF v2.3.1 – OFFLINE AI AUTO ROTATE

Mục tiêu của v2.3.1:
1. Sửa lỗi v2.3.0 không khởi động do biên dịch C# tại máy người dùng thiếu System.Runtime facade.
2. Không biên dịch ứng dụng trên máy người dùng nữa. Bản phát hành được biên dịch sẵn và đóng gói self-contained.
3. Nhúng trực tiếp model ONNX chuyên nhận hướng tài liệu 0/90/180/270 vào app; không tải model khi chạy, không cần Internet.
4. Tự xoay kết hợp model AI + phân tích bố cục + đồng thuận toàn file; trang không đủ chắc chắn sẽ giữ nguyên và gắn CẦN KIỂM TRA.
5. Sau Xoay trái/Xoay phải/Xoay 180, focus trả lại cột THỨ TỰ TRANG. Có thêm xử lý phím toàn Form để ↑/↓ vẫn di chuyển được ngay sau khi bấm toolbar.
6. Hiển thị “File đang xử lý: <tên file>”.
7. Giữ nguyên nguyên tắc source_order tách biệt rotation, chia mặc định 50/50, 2 chế độ scan và 2 chiều cắt.

Model:
- RapidOrientation / rapid_orientation.onnx, Apache-2.0.
- 4 hướng: 0, 90, 180, 270.
- Model được nhúng trong assembly, ONNX Runtime CPU được đóng gói cùng EXE self-contained.

Lưu ý kiểm thử:
- Build CI phải chạy smoke-test model cho đủ 4 hướng trước khi tạo artifact.
- Kiểm thử trên Windows thật với PDF thực tế vẫn cần thiết trước khi coi Auto Rotate đạt trên mọi loại tài liệu.
