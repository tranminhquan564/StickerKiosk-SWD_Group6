# 4. Chiến lược giải pháp

| Quyết định | Cách làm |
|---|---|
| Sự thật nghiệp vụ | `ORDER.status` trên cloud |
| Sự thật an toàn máy | Local controller |
| Tiền | Chỉ webhook payment provider đặt Paid (BR-PAY-02) |
| Sai số tiền | Từ chối webhook, đơn giữ PaymentPending (PR-03) |
| Webhook lệch inquiry | PaymentUnknown, không dán (BR-PAY-03) |
| Lệnh máy | Tên nghiệp vụ: `inspect_device`, `lock_tray`, `apply(template_id)`. Không gửi góc khớp |
| Khi chưa có máy thật | Robot mock cùng contract MQTT |
| Tài liệu kiến trúc | arc42 viết Markdown, C4 vẽ Mermaid để GitHub render |

Hai repo mẫu [bitsmuggler/arc42-c4](https://github.com/bitsmuggler/arc42-c4-software-architecture-documentation-example) và [milanm/architecture-docs](https://github.com/milanm/architecture-docs) dùng Structurizr, AsciiDoc và docToolchain. Nhóm không dựng toolchain đó. Lý do nằm ở quyết định ADR-001.
