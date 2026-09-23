# 11. Rủi ro và nợ kỹ thuật

Các điểm sau được handoff ghi là chưa thành chương trong v2. Tài liệu này không biến chúng thành rule mới.

| Việc chưa khóa | Cách giữ trong thiết kế |
|---|---|
| Webhook Paid đến sau khi đơn đã Cancelled | Giữ decision table ở sequence hoàn tiền, không thêm transition 10.2 |
| QR hết hạn trùng lúc Paid | Payment đối chiếu amount và order trước khi ghi Paid |
| Tồn vật lý lệch `on_hand` | Chỉ STF hoặc OPS nhập tồn, có `MAINTENANCE_LOG` RESTOCK |
| Local đang Applying trong khi cloud vẫn Paid | Local là sự thật máy, cloud là sự thật tiền. Không tự bịa status bên kia |
| Chưa có code kiosk | Mức C4 code để trống. Repo này là tài liệu và backlog |

Nợ: sơ đồ C4 dùng nhãn không dấu trong một số cạnh Mermaid để renderer của GitHub ổn định. Nghĩa tiếng Việt nằm ở các chương arc42.
