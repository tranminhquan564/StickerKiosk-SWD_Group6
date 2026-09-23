# 6. Góc nhìn runtime

C4 không thay các sơ đồ nghiệp vụ. Runtime đi theo sequence và state đã có.

| Tình huống | Sơ đồ |
|---|---|
| Khách đi hết phiên | `diagrams/mmd/Activity.mmd` |
| Đổi `ORDER.status` | `diagrams/mmd/State-ORDER.mmd` và `diagrams/mmd/State-Ngat.mmd` |
| Tạo QR đến webhook Paid | `diagrams/mmd/Seq-ThanhToan.mmd` |
| Đo, khóa, apply | `diagrams/mmd/Seq-Interlock.mmd` |
| Hoàn tiền | `diagrams/mmd/Seq-HoanTien.mmd` |
| E-stop và mất điện | `diagrams/mmd/Seq-EStop.mmd` |

Điểm neo:

- Cảm biến có máy mới sang `DeviceInserted` (BR-PAY-01).
- Local từ chối `apply` khi thiếu BR-LCK-01 hoặc SR-01.
- Apply fail và QA fail giữ `ManualRecovery`. Tiền ghi `REFUND_REQUEST`.
- `Refunded` chỉ đi từ `RefundPending`.
