# 1. Giới thiệu và mục tiêu

Phần mềm kiosk dán sticker điện thoại cho đồ án SWD392 SE1927 Group 6. Khách chọn model trong danh sách, trả QR, đặt máy vào khay. Hệ thống chỉ dán khi `ORDER` đã Paid và khay Locked.

## Mục tiêu

- Chạy an toàn theo interlock (P1).
- Không thu tiền nếu không bán được dịch vụ (P2).
- `ORDER.status` là nguồn sự thật nghiệp vụ (P3).

## Bên liên quan

| Bên | Quan tâm |
|---|---|
| CUS | Tự dán sticker, biết khi nào máy khóa |
| STF | Mở khóa, sự cố, nạp tem |
| OPS | Giá, duyệt hoàn, KPI |
| PAY | QR và webhook, không giữ PAN trong hệ thống này |

Chỉ tiêu phần mềm lấy từ mục 16 đặc tả: Paid đến ReadyForPickup tối đa 5 phút (không tính khách lau), lệch QA tối đa 1.5 mm, STF nhận incident tối đa 5 phút, khôi phục an toàn sau có điện tối đa 2 phút.
