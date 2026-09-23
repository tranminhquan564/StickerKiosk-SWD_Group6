# Bộ sơ đồ C4

Context, container, component cloud, component local, deployment.

## Sub-features

- Context có người và payment provider ngoài hệ thống.
- Container tách UI, cloud, local, database.
- Local không có lệnh góc khớp.

## How to get to it (user POV)

Mở `diagrams/mmd/C4-Context.mmd` hoặc mục Kiến trúc C4 trên README GitHub.

## Driving it with python

`python3 diagrams/check_c4_docs.py` kiểm tra dòng đầu của năm file.

## Gotchas

Exporter draw.io bỏ qua file bắt đầu bằng `C4`. Không chạy export với kỳ vọng ra trang C4 trong `kiosk.drawio`.
