# Kế hoạch đồng bộ GitHub — StickerKiosk

**Nguồn:** [Software Development Blueprint](../blueprint/stickerkiosk-blueprint.md)  
**Skill:** `BA-Blueprint-Agent/skills/github-project-sync` (WS_01_FU)  
**Chế độ hiện tại:** `GITHUB_PROJECT_DRY_RUN=true` — **chưa tạo** repo/issue/project trên github.com  
**Lệnh:** `python3 scripts/github-sync.py`

## Repo và Project dự kiến

| Hạng mục | Giá trị |
|---|---|
| Tên repo | `StickerKiosk-SWD_Group6` |
| Owner | Tài khoản GitHub sau khi `gh auth login` — **không** bịa org |
| Visibility | `private` (đổi trong `.env` nếu nhóm muốn public) |
| Project | `StickerKiosk Delivery` |
| Số issue | **29** (18 FR + 4 NFR + 7 spike) |

## Field Project bắt buộc

Status, Priority, Type, Area, Owner (assignee), Iteration, Target date, Blueprint ID, Risk.

View khi Project đã tạo: Team Board, Priority Queue, Sprint View, Blocked Work, Delivery Traceability — theo `BA-Blueprint-Agent/governance/github-project-operating-model.md`.

## Mapping issue

| Blueprint ID | Type | Priority | Area | Risk | Iteration | Title |
|---|---|---|---|---|---|---|
| FR-001 | Feature | P1 High | kiosk-ui | Low | MVP-1 | [FR-001] Chọn model whitelist và sticker pre-cut |
| FR-002 | Feature | P1 High | kiosk-ui | Medium | MVP-1 | [FR-002] Preview giá, thời lượng và cảnh báo an toàn trước khi insert |
| FR-003 | Feature | P0 Critical | payment | High | MVP-2 | [FR-003] Thanh toán QR paid/failed/unknown — charge trước |
| FR-004 | Feature | P0 Critical | payment | High | MVP-2 | [FR-004] Chặn đưa máy vào khay khi đơn chưa Paid |
| FR-005 | Feature | P0 Critical | safety-controller | Critical | MVP-3 | [FR-005] Đóng và khóa khay trước khi apply |
| FR-006 | Feature | P1 High | apply-quality | High | MVP-4 | [FR-006] So khớp profile model đã chọn — không AI detect |
| FR-007 | Feature | P0 Critical | safety-controller | Critical | MVP-3 | [FR-007] Controller local chỉ start khi Paid và Locked |
| FR-008 | Feature | P1 High | apply-quality | Medium | MVP-4 | [FR-008] Pass QC thì mở khay và hoàn tất đơn |
| FR-009 | Feature | P0 Critical | safety-controller | Critical | MVP-3 | [FR-009] Fail/fault: giữ máy an toàn và gọi nhân viên |
| FR-010 | Feature | P0 Critical | safety-controller | Critical | MVP-3 | [FR-010] E-stop và mất tín hiệu an toàn cắt chuyển động |
| FR-011 | Feature | P0 Critical | staff-console | Critical | MVP-3 | [FR-011] Mở khóa thủ công ủy quyền và luôn ghi audit |
| FR-012 | Feature | P0 Critical | safety-controller | Critical | MVP-3 | [FR-012] Recovery mất điện, mất mạng, UI treo — không kẹp, không mất order, không double charge |
| FR-013 | Feature | P1 High | staff-console | Medium | MVP-5 | [FR-013] Console nhân viên: fault, unlock, hoàn phí, restock, vệ sinh |
| FR-014 | Feature | P1 High | ledger-audit | High | MVP-1 | [FR-014] Sổ cái giao dịch và log chuyển trạng thái append-only |
| FR-015 | Feature | P1 High | kiosk-ui | Medium | MVP-1 | [FR-015] UI khách và copy lỗi tiếng Việt cho người lạ |
| FR-016 | Feature | P1 High | staff-console | High | MVP-5 | [FR-016] Hoàn phí dịch vụ theo chính sách — staff xác nhận (mặc định) |
| FR-017 | Feature | P2 Medium | staff-console | Low | MVP-5 | [FR-017] Console chủ dịch vụ: giao dịch, fault, doanh thu, sức khỏe máy |
| FR-018 | Feature | P0 Critical | hardware-adapter | High | MVP-1 | [FR-018] Adapter phần cứng start/stop/status/locked/error và simulator |
| NFR-004 | Task | P0 Critical | safety-controller | Critical | MVP-4 | [NFR-004] Nghiệm thu lab: 0 xước/nứt/kẹt không lấy được máy |
| NFR-006 | Task | P1 High | privacy-ops | Medium | MVP-2 | [NFR-006] Không hồ sơ khách, không dữ liệu thẻ — định danh = order id |
| NFR-007 | Task | P1 High | privacy-ops | High | MVP-4 | [NFR-007] Ảnh QC có retention, chỉ phục vụ sự cố, không nhận diện người |
| NFR-008 | Task | P0 Critical | ledger-audit | High | MVP-3 | [NFR-008] An toàn chạy local khi mất mạng; ledger sync idempotent |
| SP-001 | Spike | P0 Critical | hardware-adapter | High | MVP-0 | [SP-001] Chốt module phần cứng và đóng băng API start/stop/locked/error |
| SP-002 | Spike | P1 High | apply-quality | Medium | MVP-0 | [SP-002] Chốt 3–5 model whitelist lưng phẳng phổ biến tại Việt Nam |
| SP-003 | Spike | P2 Medium | apply-quality | Medium | MVP-4 | [SP-003] Camera sau dán: auto pass/fail hay chỉ lưu ảnh cho staff |
| SP-004 | Spike | P0 Critical | payment | High | MVP-2 | [SP-004] Payment unknown: giữ đối soát hay từ chối apply |
| SP-005 | Spike | P1 High | staff-console | Medium | MVP-5 | [SP-005] Hoàn phí: nhân viên xác nhận hay tự động theo mã lỗi |
| SP-006 | Spike | P1 High | privacy-ops | High | MVP-4 | [SP-006] Chính sách lưu/xóa ảnh QC (thời hạn, local/cloud) |
| SP-007 | Spike | P1 High | privacy-ops | High | MVP-0 | [SP-007] Chốt site thử và roster trực E-stop/unlock |

## Blocker Gate 5

Cloud agent không có `GH_TOKEN` và `gh auth status` = chưa login. Cần người dùng đăng nhập GitHub trên môi trường agent hoặc gắn token, rồi chạy lại sync với `GITHUB_PROJECT_DRY_RUN=false`.
