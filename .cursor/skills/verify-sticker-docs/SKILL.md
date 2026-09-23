---
name: verify-sticker-docs
description: Kiểm tra tài liệu kiến trúc Sticker Kiosk (C4 Mermaid và chương arc42) bằng script read-only. Dùng khi sửa README, diagrams/mmd/C4-*.mmd hoặc docs/architecture.
---

# Kiểm tra tài liệu kiosk

Repo này không có ứng dụng kiosk để bấm. Bề mặt kiểm được là tài liệu: README, sơ đồ C4, mười hai chương arc42. Script không gọi mạng và không ghi file trong repo.

## Launch

Không có server.

```bash
python3 diagrams/check_c4_docs.py
```

Chạy từ thư mục gốc repo. Sẵn sàng khi dòng đầu là `ok diagrams=5 chapters=13` và exit code 0.

## Doctor

```bash
test -f diagrams/check_c4_docs.py && test -f README.md && test -f docs/architecture/README.md
```

Cả ba file phải tồn tại trước khi chạy script.

## Drive

Harness là Python, không phải trình duyệt.

1. `python3 diagrams/check_c4_docs.py`
2. Đọc stdout. Thành công in một dòng `ok`.
3. Thất bại in từng đường dẫn thiếu và exit 1.

## Evidence

Ghi stdout và exit code ra `/tmp/verify-sticker-docs/last-run.txt`. File này nằm ngoài repo.

Bằng chứng phải là kết quả script trên cây file thật, không sửa expected cho khớp. Script chỉ đọc.

## Cleanup

Script không tạo process nền và không sửa repo. Không xóa `/tmp/verify-sticker-docs/last-run.txt`.

## Helpers

Lệnh duy nhất: `python3 diagrams/check_c4_docs.py`.
