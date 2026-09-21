## Learned User Preferences
- Trả lời bằng tiếng Việt.
- Làm đặc tả và sơ đồ phần mềm kiosk: Use Case, Activity, state ORDER, sequence thanh toán, interlock, hoàn tiền, e-stop và ERD. Chỉ sơ đồ phần mềm; không thiết kế phần cứng, BOM, firmware hay khớp nối. Phần cứng chỉ là actor hoặc interface.
- Bỏ tab UseCase, ERD và DB của ví dụ xe điện. Tiếp tục ERD kiosk từ tab Trang-4.
- Gắn mọi transition và sơ đồ với mã BR, GR, PR, SR, TR của đặc tả MVP v2. Không thêm rule trái v2 và không thêm transition ORDER mà mục 10.2 không định nghĩa. NetworkDegraded có tên ở mục 10.1 nhưng không có transition 10.2. ManualRecovery không có lối ra Refunded trong 10.2; lỗi apply/QA giữ ManualRecovery và hoàn tiền là REFUND_REQUEST. Nếu đổi số có nhãn MVP-DEFAULT thì phải ghi chú, không sửa ngầm.

## Learned Workspace Facts
- Dự án SWD392 SE1927 Group 6: máy dán sticker điện thoại tự động. Phạm vi workspace là phần mềm.
- Nguồn sự thật nghiệp vụ là đặc tả MVP v2 (`DacTaNghiepVu_MVP_v2`, v2.0). Handoff nằm ở `attachments/CURSOR_HANDOFF_SWD392.md`. Tài liệu intent v1 chỉ để tham khảo lịch sử, không phải rule hiện tại.
- Sơ đồ canonical là `hoanhthanh1.json` và nguồn Mermaid ở `diagrams/mmd/`, cùng do `diagrams/build_hoanhthanh1.py` sinh. `diagrams/export_drawio.py` ghi `diagrams/kiosk.drawio` và tách `State-Ngat.mmd`. Trước khi xuất lại, xóa `diagrams/mmd/State-Ngat.mmd` kẻo exporter gộp cạnh cũ. Bản JSON xe điện cũ lưu ở `attachments/hoanhthanh1.xe-dien.json`.
- `ORDER.status` là nguồn sự thật nghiệp vụ. Local phụ trách an toàn máy, cloud phụ trách tiền. Mất mạng không được ghi Paid khi chưa có xác nhận thanh toán.
- BR-CUS-05 là lưu giữ ảnh, không phải rule QA đạt. Tiêu chí QA đạt là mục 9 bước 10.
- PR-03 từ chối webhook sai số tiền và giữ PaymentPending. BR-PAY-03 chỉ là lệch giữa webhook và inquiry.
