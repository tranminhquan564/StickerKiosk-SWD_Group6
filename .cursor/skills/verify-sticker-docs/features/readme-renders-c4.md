# README nhúng C4

Trang GitHub chính phải chứa bốn loại sơ đồ.

## Sub-features

- Có `C4Context`, `C4Container`, `C4Component`, `C4Deployment`.
- Có link `docs/architecture/README.md`.

## How to get to it (user POV)

Mở README của repo trên GitHub, mục Kiến trúc C4.

## Driving it with python

`python3 diagrams/check_c4_docs.py` tìm bốn token trong `README.md`.

## Gotchas

Script không mở trình duyệt nên không chứng minh GitHub đã vẽ hình. Nó chứng minh Markdown có đúng khối Mermaid.
