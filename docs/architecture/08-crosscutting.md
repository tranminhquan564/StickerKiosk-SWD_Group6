# 8. Khái niệm xuyên suốt

| Khái niệm | Quy tắc |
|---|---|
| Định danh khách | Không bắt login (BR-CUS-01). SĐT tùy chọn (BR-CUS-02). Không lưu mặt (BR-CUS-03) |
| Tiền | Không lưu PAN (BR-CUS-04). Idempotent theo `provider_payment_id` (PR-04) |
| Ảnh | QA đạt giữ 24 giờ. Ảnh sự cố giữ 30 ngày hoặc đến khi đóng incident (BR-CUS-05) |
| Audit | Mọi đổi trạng thái do người ghi actor, lý do, thời điểm, kiosk, đơn (BR-ACL-01) |
| Mạng | Local xếp event đúng thứ tự (SR-24). Pending mà mất mạng thì không đoán Paid (SR-21) |
| An toàn | E-stop cắt motion, khay giữ khóa (SR-02). Mất điện không tự resume (SR-12) |
