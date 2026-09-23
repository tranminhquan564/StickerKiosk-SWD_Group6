# Kiến trúc phần mềm theo arc42 và C4

Cấu trúc chương lấy theo [arc42](https://arc42.org/) và mức trừu tượng lấy theo [C4](https://c4model.com/). Cách đóng gói tham khảo [bitsmuggler/arc42-c4](https://github.com/bitsmuggler/arc42-c4-software-architecture-documentation-example) và [milanm/architecture-docs](https://github.com/milanm/architecture-docs). Nội dung là kiosk sticker của nhóm, không dùng ví dụ ngân hàng của hai repo đó.

Nhóm xem tài liệu trên GitHub bằng Mermaid. Không dùng docToolchain, Structurizr hay Docker. Quyết định này là ADR-001 trong chương 9.

| Chương | Nội dung |
|---|---|
| [1. Giới thiệu và mục tiêu](01-introduction-and-goals.md) | Bài toán và chỉ tiêu |
| [2. Ràng buộc](02-constraints.md) | Những gì v2 cấm |
| [3. Bối cảnh](03-context-and-scope.md) | C4 Context |
| [4. Chiến lược](04-solution-strategy.md) | Tiền ở cloud, máy ở local |
| [5. Khối xây dựng](05-building-block-view.md) | C4 Container và Component |
| [6. Runtime](06-runtime-view.md) | Trỏ sang sequence và state đã có |
| [7. Triển khai](07-deployment-view.md) | C4 Deployment, một kiosk |
| [8. Xuyên suốt](08-crosscutting.md) | Audit, ảnh, mạng |
| [9. Quyết định](09-architecture-decisions.md) | ADR |
| [10. Chất lượng](10-quality-requirements.md) | Ngưỡng mục 16 và 17 |
| [11. Rủi ro](11-risks.md) | Việc v2 chưa khóa |
| [12. Thuật ngữ](12-glossary.md) | C4, status, refund |

Mức code của C4 chưa vẽ vì chưa có ứng dụng.
