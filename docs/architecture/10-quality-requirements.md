# 10. Yêu cầu chất lượng

Số lấy từ mục 16 và 17 của đặc tả. Nhãn `[MVP-DEFAULT]` nếu đổi phải sửa đặc tả.

| Mã | Ngưỡng | Kiểm bằng |
|---|---|---|
| X | Paid đến ReadyForPickup tối đa 5 phút, không tính lúc khách lau | Đo log trạng thái |
| Z | Lệch QA tối đa 1.5 mm | Mục 9 bước 10 |
| B | STF nhận incident tối đa 5 phút | Thời điểm INCIDENT đến lúc staff nhận |
| C | Có đường mở khóa an toàn trong 2 phút sau khi có điện | SR-13, không tính thời gian người đi tới máy |

Kịch bản phải chặn được: apply khi chưa Paid hoặc chưa lock; skip máy sai hoặc còn ốp; hết hàng vẫn ra QR; e-stop tự mở khay; mất mạng lúc Pending mà thành Paid; mất điện rồi tự dán tiếp; QA fail thành Completed; Completed đổi ý vẫn hoàn; mở khóa không PIN; lưu PAN.
