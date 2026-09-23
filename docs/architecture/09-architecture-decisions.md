# 9. Quyết định kiến trúc

## ADR-001. Viết arc42 bằng Markdown và C4 bằng Mermaid

Hai mẫu [bitsmuggler/arc42-c4-software-architecture-documentation-example](https://github.com/bitsmuggler/arc42-c4-software-architecture-documentation-example) và [milanm/architecture-docs](https://github.com/milanm/architecture-docs) dựng Structurizr DSL, PlantUML, AsciiDoc, docToolchain và Docker. Nhóm lấy cấu trúc arc42 và bốn mức C4 từ đó, không lấy nội dung ngân hàng.

Đã chọn Markdown và Mermaid vì README GitHub đã vẽ Mermaid, repo chưa bật GitHub Pages, và nhóm không cần Docker để đọc tài liệu.

Hệ quả: không có site HTML riêng. Đọc trên GitHub. Bản draw.io vẫn là `diagrams/kiosk.drawio` cho sơ đồ UML. Sơ đồ C4 nằm ở `diagrams/mmd/C4-*.mmd`. `export_drawio.py` bỏ qua file C4 vì exporter chỉ dựng flowchart, state và ERD.

## ADR-002. Tách sự thật tiền và sự thật máy

Cloud ghi tiền và `ORDER.status`. Local quyết định robot có được chạy. Mất mạng lúc PaymentPending không ghi Paid.

## ADR-003. Không thêm transition ngoài mục 10.2

`NetworkDegraded` có tên ở mục 10.1 nhưng không có mũi tên trong 10.2. `ManualRecovery` không có lối sang `Refunded`. Hoàn sau apply fail hoặc QA fail nằm ở `REFUND_REQUEST`.

## ADR-004. Lệnh local là hợp đồng nghiệp vụ

Tên lệnh: `home`, `inspect_device`, `lock_tray`, `unlock_tray`, `pick_sku`, `apply`, `qa_capture`, `estop_ack`, `safe_halt`. Không có góc khớp trong mô hình phần mềm.
