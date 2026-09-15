# StickerKiosk — SWD392 SE1927 Group 6

Kiosk tự phục vụ dán **sticker mặt lưng điện thoại**: khách chọn model trong whitelist, trả tiền QR, đặt máy vào khay; máy chỉ dán khi đơn **Paid** và khay **Locked**.

Đây là seed đồ án (blueprint + GitHub requirements), **không** phải ứng dụng kiosk đầy đủ.

## Chạy gì ở đây

| Việc | Lệnh |
|---|---|
| Xem kế hoạch Issue/Project (không gọi GitHub) | `python3 scripts/github-sync.py` |
| Tạo repo, label, issue, GitHub Project | Điền `.env` từ `.env.example`, đặt `GITHUB_PROJECT_DRY_RUN=false`, rồi `python3 scripts/github-sync.py` |

Cần GitHub CLI (`gh`) đã `gh auth login`, hoặc biến `GH_TOKEN` / `GITHUB_TOKEN`. Quyền tối thiểu: tạo repo, Issues, Projects. **Không** bịa organization — repo được tạo dưới tài khoản/org của token.

## Artefact

- [Software Development Blueprint](docs/blueprint/stickerkiosk-blueprint.md) — nguồn mô tả (status **Draft**)
- [Kế hoạch đồng bộ GitHub](docs/github/sync-plan.md)
- [Backlog có ID ổn định](requirements/backlog.py)
- [BA Blueprint Agent](BA-Blueprint-Agent/instructions.md) — skill lấy từ [WS_01_FU](https://github.com/Pen1112003/WS_01_FU)
- Issue templates: `.github/ISSUE_TEMPLATE/`
- Label chuẩn field Project: `.github/labels.yml`

## Quy ước delivery (WS_01_FU)

- Issue: `[FR-###] Tên ngắn` (cũng dùng `[NFR-###]`, `[SP-###]`)
- Body bắt buộc: Context, Scope, Acceptance criteria, Dependency, Risk, link blueprint
- Branch: `<type>/<issue-number>-<short-slug>`
- PR: `Closes #<n>` hoặc `Refs #<n>`
- Comment: Progress, Summary, Evidence, Branch/PR, Next, Blocker
- Chỉ `Done` khi AC có evidence và PR đã merge

## Phạm vi phần mềm (MVP)

UI kiosk tiếng Việt, cổng QR, máy trạng thái, lệnh an toàn tới module (`start` / `stop` / `status` / `locked` / `error`), console nhân viên, audit log.

Không in/cắt tại kiosk, không AI nhận diện model, không bảo hiểm giá trị máy (chỉ hoàn **phí dịch vụ**).

## Cấu hình GitHub

```bash
cp .env.example .env
# Điền GITHUB_OWNER, GITHUB_REPOSITORY, GITHUB_TOKEN
# GITHUB_PROJECT_DRY_RUN=false khi đã review mapping
python3 scripts/github-sync.py
```

Không commit `.env` hoặc token.
