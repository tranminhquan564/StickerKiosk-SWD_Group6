# Software Development Blueprint — StickerKiosk

**Status:** Draft  
**Version:** 0.1  
**Owner:** SWD392 SE1927 Group 6  
**Last updated:** 2026-09-15  
**Nguồn:** Intent StickerKiosk (EN), 2026-09-15  
**Phương pháp:** BA Blueprint Agent (WS_01_FU) — 10 bước Discover → GitHub Project Sync

## 1. Executive Summary

- **Business problem:** Dán sticker mặt lưng điện thoại tại quầy vẫn phụ thuộc tay nghề nhân viên. Cùng một mẫu có thể lệch camera, thiếu mép, hoặc đầy bọt. Khách chờ. Chủ quầy không đo được chất lượng giữa các ca. Kiosk dán cường lực tự phục vụ đã có; máy in-cắt skin thường vẫn cần nhân viên. Chưa có mô hình tự phục vụ ổn định cho **dán sticker mặt lưng**: khách chọn mẫu, trả tiền, đặt máy vào khay, nhận lại đã dán — tại mall, không cần kỹ thuật viên cầm máy.
- **Desired outcome:** Kiosk mall (thử nghiệm đầu có thể là lab/sảnh campus). Khách chọn model trong whitelist và sticker pre-cut, xem preview (giá, thời lượng, cảnh báo an toàn), thanh toán QR, đặt máy **đã tháo ốp** vào khay. Máy dán **chỉ chạy khi đơn Paid và khay Locked**. Cảm biến/camera **so khớp profile model khách đã chọn** — không đoán model. Pass thì mở khay. Fail/fault thì giữ máy an toàn, màn hình bảo chờ nhân viên, mở yêu cầu hỗ trợ / hoàn **phí dịch vụ** theo chính sách đã công bố.
- **Success metrics (ngưỡng lab, Assumption — không phải SLA thương mại):** chu kỳ ≤ 5 phút; lệch sticker ≤ 1.5 mm trên mẫu lab; first-pass ≥ 80% trên ≥ 20 lần dán nội bộ mỗi model; **0** sự cố xước / nứt / kẹt không lấy được máy ở bước nghiệm thu lab; luôn có nhân viên tại chỗ khi dùng máy thật của tình nguyện viên.
- **Recommended direction:** MVP phần mềm khóa UI kiosk (tiếng Việt), cổng QR, máy trạng thái giao dịch, lệnh an toàn tới module phần cứng tối thiểu (`start` / `stop` / `status` / `locked` / `error`), console nhân viên, và nhật ký audit. Không thiết kế robot công nghiệp trong 10–12 tuần. Không apply khi chưa Paid. App điện thoại của khách (nếu có sau này) **không** được lệnh trực tiếp tới applicator.

Ba giả thuyết MVP: (1) **An toàn** — không lực nghiền, khay luôn mở được bằng E-stop / mở thủ công ủy quyền sau mất điện; (2) **Chất lượng** — đạt ngưỡng team khóa trước trial công khai; (3) **Tự phục vụ** — người lạ hoàn thành chọn → trả tiền → đặt máy → lấy máy mà không cần nhân viên đứng suốt bước.

## 2. Scope

### In scope

- UI kiosk khách (tiếng Việt): chọn model whitelist (3–5 máy lưng phẳng), chọn sticker pre-cut khớp template, preview giá / thời lượng / hướng dẫn / cảnh báo an toàn **trước khi** máy vào khay.
- Một rail thanh toán: QR. Charge trước, rồi mới cho đặt máy. Trạng thái cổng: `paid` / `failed` / `unknown`.
- Controller kiosk **local**: logic an toàn thời gian thực; **lớp duy nhất** được phép lệnh applicator. Chỉ `start` khi Paid + Locked.
- So khớp vị trí/kích thước với **profile model đã chọn** (lệch, sai size, còn ốp, vật cản → từ chối). Không nhận diện model bằng AI.
- Ảnh sau dán (QC) — hành vi auto pass/fail vẫn là Open Question; intent yêu cầu có camera/cảm biến.
- Khóa khay, nút E-stop, mở thủ công ủy quyền (luôn ghi log).
- Console nhân viên: sự cố, mở khóa thủ công, xác nhận hoàn phí dịch vụ, restock, vệ sinh.
- Sổ cái giao dịch và log chuyển trạng thái (kiosk id, transaction/order id, timestamp, reason).
- Ledger nghiệp vụ đồng bộ backend khi có mạng; an toàn máy chạy local.
- Chính sách hoàn **phí dịch vụ** khi dán thất bại (không bảo hiểm giá trị máy).

### Out of scope

- In / cắt tại kiosk; artwork tùy biến phong phú do khách thiết kế.
- AI nhận diện model.
- Máy còn ốp, lưng cong, vỏ nứt, foldable, model ngoài whitelist.
- Đa kiosk rollout, nhiều rail thanh toán, tài khoản / loyalty.
- App native điều khiển máy.
- Bảo hiểm tự động / bồi thường giá trị thiết bị.
- Tích hợp POS / hệ thống thuê mặt bằng mall.
- Vận hành mall 24/7 không người trực.

## 3. Stakeholders and Users

| ID | Role | Responsibility | Decision/approval |
|---|---|---|---|
| ST-001 | Khách kiosk | Chọn model/sticker, thanh toán, đặt/lấy máy theo hướng dẫn; không giả định kiến thức kỹ thuật | Không phê duyệt sản phẩm |
| ST-002 | Nhân viên tại quầy (operator) | E-stop watch, mở khóa ủy quyền, xử lý fault, xác nhận hoàn phí dịch vụ, restock, vệ sinh | Xác nhận sự cố / hoàn phí trên console |
| ST-003 | Chủ dịch vụ (service owner) | Doanh thu, fault, sức khỏe máy, chính sách hoàn phí | Phê duyệt chính sách hoàn và ngưỡng chất lượng lab |
| ST-004 | Ban quản lý mall / site (nếu đặt mall) | An toàn, lối đi, diện mạo, giấy phép | Có thể chặn đặt máy — ngoài client khóa học |
| ST-005 | Nhóm 6 + giảng viên | “Client” của đồ án; đề xuất thanh acceptance, giảng viên duyệt | Giảng viên duyệt thanh nghiệm thu |
| ST-006 | Cổng QR (chọn lúc spec) | `paid` / `failed` / `unknown` theo giao dịch | Quyết định nhà cung cấp = Open Question |
| ST-007 | Module applicator / fixture | `start` / `stop` / `status` / `locked` / `error` | Chọn module trước khi khóa spec |

## 4. Assumptions, Constraints and Open Questions

| ID | Type | Statement | Owner | Status |
|---|---|---|---|---|
| A-001 | Assumption | Nửa đầu kỳ có applicator/fixture cho 3–5 model, nhận `start` / `stop` / `status` | Group 6 | Unconfirmed |
| A-002 | Assumption | Mua được lô nhỏ sticker pre-cut đúng template model | Group 6 | Unconfirmed |
| A-003 | Assumption | Có ít nhất một cổng QR Việt Nam với sandbox theo giao dịch | Group 6 | Unconfirmed |
| A-004 | Assumption | Site thử (lab/sảnh/quầy) có điện và người trực khi dùng máy thật | Group 6 | Unconfirmed |
| A-005 | Assumption | Khách tháo ốp và lau lưng theo hướng dẫn trên màn hình | Group 6 | Unconfirmed |
| A-006 | Assumption | Hoàn phí dịch vụ khi dán fail là đủ cho MVP; không giả định bảo hiểm máy | Group 6 + lecturer | Unconfirmed |
| A-007 | Assumption | Client đồ án là nhóm + giảng viên, không phải BQL mall | Group 6 | Confirmed in intent |
| C-001 | Constraint | MVP 3–5 model lưng phẳng whitelist; model mới = fixture/profile mới | Group 6 | Confirmed |
| C-002 | Constraint | Chỉ sticker pre-cut, dán trực tiếp lưng trần; không dán lên ốp; không in/cắt tại kiosk | Group 6 | Confirmed |
| C-003 | Constraint | Cảm biến/camera chỉ so khớp profile đã chọn; không AI detect model | Group 6 | Confirmed |
| C-004 | Constraint | Một rail QR; charge trước rồi mới insert; không mô tả hold/auth nếu cổng không hỗ trợ | Group 6 | Confirmed |
| C-005 | Constraint | Preview/giá/thời lượng/hướng dẫn/cảnh báo an toàn trước khi máy vào khay | Group 6 | Confirmed |
| C-006 | Constraint | Khay đóng-khóa trước khi dán; E-stop cắt chuyển động; mất tín hiệu an toàn thì dừng; mở thủ công chỉ nhân viên ủy quyền và luôn log | Group 6 | Confirmed |
| C-007 | Constraint | Mất điện / mất mạng / UI treo: máy không bị kẹp, không mất order id, không double charge. Chi tiết recovery nằm ở spec; intent bắt test trước acceptance | Group 6 | Confirmed |
| C-008 | Constraint | UI khách và copy lỗi bằng tiếng Việt, người lạ dùng được | Group 6 | Confirmed |
| C-009 | Constraint | Không hồ sơ khách, không dữ liệu thẻ. Định danh giao dịch = order id. Ảnh camera (nếu lưu) chỉ phục vụ sự cố, có retention, không nhận diện người | Group 6 | Confirmed |
| C-010 | Constraint | Lệnh máy và an toàn chạy local. Ledger sync backend khi có mạng. Controller local chỉ nhận start từ flow kiosk đã Paid+Locked | Group 6 | Confirmed |
| C-011 | Constraint | Phải chọn module phần cứng điều khiển được trước khi khóa spec; không phụ thuộc tự chế robot cả kỳ | Group 6 | Confirmed |
| Q-001 | Open Question | Module phần cứng MVP (kit tự lắp, applicator có sẵn, đối tác gia công) và hạn đóng băng API `start`/`stop`/`locked`/`error`? | Group 6 | Open |
| Q-002 | Open Question | Chính xác 3–5 model whitelist? (iPhone Pro Max chỉ là ví dụ) | Group 6 | Open |
| Q-003 | Open Question | Camera sau dán tự pass/fail theo ngưỡng, hay chỉ lưu ảnh cho nhân viên? | Group 6 | Open |
| Q-004 | Open Question | Payment `unknown`: giữ khay để đối soát, hay từ chối dán đến khi cổng xác nhận? | Group 6 | Open |
| Q-005 | Open Question | Fail dán: nhân viên bấm hoàn sau khi đọc log, hay mã lỗi hoàn tự động? | Group 6 | Open |
| Q-006 | Open Question | Ảnh QC giữ bao lâu, local hay cloud, xóa thế nào khi hết hạn? | Group 6 | Open |
| Q-007 | Open Question | Site thử đầu tiên, và ai trực E-stop/unlock trong giờ hoạt động? | Group 6 | Open |

## 5. Process Analysis

| Step | Current state | Future state | Actor/system | Rule or exception |
|---|---|---|---|---|
| 1. Chọn mẫu | Nhân viên/khách chọn sticker bằng mắt; model điện thoại không được khóa bằng profile | Khách chọn **model whitelist** rồi **SKU sticker** khớp template | Khách, kiosk UI | Model ngoài list → dừng, không đoán AI |
| 2. Báo giá / an toàn | Thường nói miệng; khách đưa máy trước khi hiểu rủi ro | Preview giá, thời lượng dự kiến, hướng dẫn tháo ốp/lau, cảnh báo an toàn **trước insert** | Khách, kiosk UI | Không mở khay nhận máy trước bước này |
| 3. Thanh toán | Tiền mặt/POS nhân viên; chất lượng không gắn order | Tạo order id, hiện QR, chờ `paid`. Chỉ Paid mới được insert | Khách, cổng QR, ledger | `failed` → không insert; `unknown` → Q-004 |
| 4. Đặt máy | Nhân viên cầm máy, canh tay | Khách tháo ốp, đặt vào khay theo hình; khay **Lock** | Khách, tray, controller | Còn ốp / lệch / sai size / vật cản → reject, mở khay trả máy |
| 5. Dán | Phụ thuộc tay nghề; không log | Controller local `start` chỉ khi Paid+Locked; applicator chạy chu kỳ | Controller, applicator | Mọi lệnh máy không đi từ app khách hay backend thuần |
| 6. QC | Nhân viên nhìn qua | Cảm biến/camera so profile; ảnh QC theo Q-003 | Camera/sensor, kiosk | Pass → mở khay; fail → giữ máy, gọi staff |
| 7. Kết thúc / sự cố | Tranh cãi miệng khi xước/kẹt | Log chuyển trạng thái; hoàn **phí dịch vụ** theo chính sách; không tự bồi thường máy | Operator, ledger | E-stop / mất tín hiệu an toàn → dừng chuyển động |
| 8. Mất điện/mạng | Máy có thể kẹt; đơn mất | Khay không kẹp; order id còn; không double charge; mở thủ công ủy quyền | Controller, operator | Test bắt buộc trước acceptance |

**Bottleneck hiện tại:** kỹ năng nhân viên + không đo được chất lượng + khách ngần ngại giao máy.  
**Control point tương lai:** Paid, Locked, E-stop, so khớp profile, audit log, hoàn phí dịch vụ.

## 6. Requirements

| ID | Type | Requirement | Priority | Source | Status |
|---|---|---|---|---|---|
| BR-001 | Business | Hệ thống phải chứng minh giả thuyết an toàn trước trial máy thật của tình nguyện viên | Must | Intent hypotheses | Draft |
| BR-002 | Business | Hệ thống phải chứng minh giả thuyết chất lượng trên model whitelist theo ngưỡng lab đã khóa | Must | Intent hypotheses | Draft |
| BR-003 | Business | Người lạ phải hoàn thành chọn → trả tiền → đặt máy → lấy máy không cần nhân viên đứng suốt bước | Must | Intent hypotheses | Draft |
| BR-004 | Business | Không dán sticker khi chưa xác nhận Paid | Must | Intent payment | Draft |
| BR-005 | Business | Khi dán fail/fault, giữ máy an toàn và hoàn **phí dịch vụ** theo chính sách; không bảo hiểm giá trị máy | Must | Intent refund | Draft |
| FR-001 | Functional | Hệ thống phải cho khách chọn đúng một model trong whitelist 3–5 máy và một SKU sticker pre-cut khớp template model đó | Must | Intent scope | Draft |
| FR-002 | Functional | Hệ thống phải hiện preview tiếng Việt gồm giá, thời lượng dự kiến, hướng dẫn đặt máy (tháo ốp, lau lưng) và cảnh báo an toàn **trước khi** cho máy vào khay | Must | C-005, C-008 | Draft |
| FR-003 | Functional | Hệ thống phải tạo order id, hiển thị QR, và ghi nhận cổng `paid` / `failed` / `unknown` — charge trước, chưa Paid thì chưa insert | Must | C-004 | Draft |
| FR-004 | Functional | Hệ thống phải chặn mở khay nhận máy cho đến khi order ở trạng thái Paid | Must | BR-004 | Draft |
| FR-005 | Functional | Hệ thống phải đóng và khóa khay trước khi gửi lệnh apply; trạng thái `locked` do controller local xác nhận | Must | C-006 | Draft |
| FR-006 | Functional | Hệ thống phải so khớp vị trí/kích thước với profile model **đã chọn**; từ chối nếu lệch, sai size, còn ốp, hoặc có vật cản — không đoán model | Must | C-002, C-003 | Draft |
| FR-007 | Functional | Controller local chỉ chấp nhận `start` khi order Paid **và** khay Locked; applicator không nhận lệnh từ app khách hay backend thuần | Must | C-010 | Draft |
| FR-008 | Functional | Khi apply + QC đạt, hệ thống mở khay và hướng dẫn khách lấy máy, đóng order Completed | Must | Intent pass path | Draft |
| FR-009 | Functional | Khi fail/fault, khay giữ máy an toàn, UI bảo chờ nhân viên, và mở yêu cầu hỗ trợ / hoàn phí dịch vụ theo chính sách | Must | BR-005 | Draft |
| FR-010 | Functional | E-stop và mất tín hiệu an toàn phải cắt chuyển động ngay; UI + log ghi lý do; không resume apply tự động | Must | C-006 | Draft |
| FR-011 | Functional | Mở khóa thủ công chỉ nhân viên ủy quyền; mọi lần mở phải ghi audit (ai, khi nào, order id, lý do) | Must | C-006 | Draft |
| FR-012 | Functional | Mất điện, mất mạng, hoặc UI treo phải để máy/khay an toàn: không kẹp, không mất order id, không double charge | Must | C-007 | Draft |
| FR-013 | Functional | Console nhân viên cho phép xem fault, xác nhận hoàn phí dịch vụ, restock, đánh dấu vệ sinh, và kích hoạt mở khóa ủy quyền | Must | Intent staff | Draft |
| FR-014 | Functional | Sổ cái và log chuyển trạng thái phải lưu kiosk id, order id, timestamp, actor/system, from-state, to-state, reason; không sửa im lặng | Must | Intent ledger | Draft |
| FR-015 | Functional | Mọi màn khách và copy lỗi trên kiosk bằng tiếng Việt, đủ để người lạ xử lý empty/loading/error/wait-for-staff | Must | C-008 | Draft |
| FR-016 | Functional | Yêu cầu hoàn phí dịch vụ gắn order id và mã sự cố; MVP mặc định nhân viên xác nhận sau khi đọc log (tự động = Q-005) | Must | BR-005, Q-005 | Draft |
| FR-017 | Functional | Chủ dịch vụ xem được giao dịch, fault, doanh thu dịch vụ, và sức khỏe máy (online, lỗi, khay) — không cần PII khách | Should | Intent owner | Draft |
| FR-018 | Functional | Adapter phần cứng phải lộ `start` / `stop` / `status` / `locked` / `error` cho controller local; simulator bắt buộc khi hardware chưa sẵn | Must | C-011, A-001 | Draft |
| NFR-001 | Non-functional | Chu kỳ chọn→lấy máy (lab) ≤ 5 phút trên đường thành công | Should | Lab thresholds | Draft |
| NFR-002 | Non-functional | Lệch sticker ≤ 1.5 mm trên mẫu lab của model whitelist | Should | Lab thresholds | Draft |
| NFR-003 | Non-functional | First-pass ≥ 80% trên ≥ 20 lần dán nội bộ mỗi model trước trial công khai | Should | Lab thresholds | Draft |
| NFR-004 | Non-functional | 0 sự cố xước / nứt / kẹt không lấy được máy ở nghiệm thu lab | Must | Lab thresholds | Draft |
| NFR-005 | Non-functional | Luôn có nhân viên tại chỗ trong mọi session dùng máy thật của tình nguyện viên | Must | Lab thresholds | Draft |
| NFR-006 | Non-functional | Không lưu hồ sơ khách hay dữ liệu thẻ; định danh = order id | Must | C-009 | Draft |
| NFR-007 | Non-functional | Ảnh lưng máy (nếu lưu) chỉ phục vụ sự cố, có retention/xóa, không dùng nhận diện người | Must | C-009, Q-006 | Draft |
| NFR-008 | Non-functional | An toàn máy chạy local không phụ thuộc mạng; ledger sync khi mạng lên, idempotent | Must | C-010, C-007 | Draft |

## 7. Use Cases and User Stories

### UC-001: Chọn model và sticker

- **Actor:** Khách kiosk
- **Trigger:** Khách bắt đầu session trên màn hình kiosk
- **Preconditions:** Kiosk online về catalog local; whitelist và SKU còn hàng được cấu hình
- **Main flow:** 1) Khách xem danh sách model whitelist. 2) Chọn một model. 3) Xem sticker pre-cut khớp model. 4) Chọn một SKU. 5) Hệ thống khóa cặp model+SKU vào draft order.
- **Alternate/error flows:** Model/SKU hết hàng → báo tiếng Việt, không tạo QR. Khách đổi model → xóa SKU không khớp.
- **Postconditions:** Draft order có model profile id và sticker SKU.
- **Related:** FR-001, FR-015, US-001

### UC-002: Xem preview và cảnh báo rồi thanh toán QR

- **Actor:** Khách kiosk
- **Trigger:** Cặp model+SKU đã chọn
- **Preconditions:** Giá và thời lượng cấu hình cho SKU
- **Main flow:** 1) Hiện preview, giá, thời lượng, hướng dẫn tháo ốp/lau, cảnh báo an toàn. 2) Khách xác nhận. 3) Tạo order id, hiện QR. 4) Cổng trả `paid`. 5) Order → Paid.
- **Alternate/error flows:** `failed` → không insert, cho thử lại hoặc hủy. `unknown` → không apply (hành vi khay = Q-004). Timeout QR → hết hạn order, không charge kép.
- **Postconditions:** Order Paid hoặc Failed/Expired/Unknown đã log.
- **Related:** FR-002, FR-003, FR-004, NFR-006

### UC-003: Đặt máy, khóa khay, so khớp profile, dán

- **Actor:** Khách; Supporting: controller, applicator, sensors
- **Trigger:** Order Paid
- **Preconditions:** Paid; khay trống; E-stop không active
- **Main flow:** 1) UI cho phép mở khay nhận máy. 2) Khách đặt máy lưng trần theo hình. 3) Khách xác nhận. 4) Khay đóng, Lock. 5) So khớp profile. 6) Pass → `start`. 7) Applicator chạy. 8) QC.
- **Alternate/error flows:** Chưa Paid → không mở nhận máy. So khớp fail → mở khay trả máy, không `start`. E-stop / error → FR-010. Mất mạng sau Paid → vẫn cho phép chu kỳ local nếu Paid đã ghi local (NFR-008).
- **Postconditions:** ApplyJob Success hoặc FailedHold hoặc RejectedPreApply.
- **Related:** FR-004–FR-008, FR-018

### UC-004: Fail / fault — giữ máy và gọi nhân viên

- **Actor:** Khách, operator
- **Trigger:** Apply/QC fail, kẹt, hoặc fault phần cứng
- **Preconditions:** Máy đang trong khay
- **Main flow:** 1) Dừng chuyển động. 2) Khay giữ an toàn (không kẹp phá máy). 3) UI khách: chờ nhân viên, không tự mở. 4) Tạo support/refund request. 5) Operator xem log, mở khóa ủy quyền, xử lý hoàn phí.
- **Alternate/error flows:** Q-005 auto-refund nếu được quyết định sau.
- **Postconditions:** Máy trả khách bởi staff; order FailedHold / Refunded đã log.
- **Related:** FR-009, FR-011, FR-013, FR-016

### UC-005: E-stop và mở khóa khẩn

- **Actor:** Bất kỳ người tại kiosk; operator cho unlock
- **Trigger:** Nhấn E-stop hoặc mất tín hiệu an toàn
- **Preconditions:** Có chuyển động hoặc khay đang khóa
- **Main flow:** 1) Cắt motion. 2) Không resume tự động. 3) Log. 4) Operator ủy quyền mở khóa và lấy máy.
- **Alternate/error flows:** Mất điện — mở thủ công cơ khí ủy quyền, vẫn ghi log khi hệ thống lên (FR-012).
- **Postconditions:** Máy lấy ra được; ApplyJob không Completed.
- **Related:** FR-010, FR-011, FR-012, NFR-004, NFR-005

### US-001: Chọn model whitelist

Là khách kiosk, tôi muốn chọn model điện thoại trong danh sách cố định, để máy chỉ dán đúng profile đã được lab kiểm.

**Acceptance criteria**

- Given whitelist 3–5 model, when tôi chọn một model, then kiosk chỉ hiện sticker khớp template model đó.
- Given model không nằm trong list, when tôi tìm model đó, then hệ thống từ chối và không gọi nhận diện AI.
- Priority: P1. Dependency: Q-002. Source: FR-001.

### US-002: Thanh toán QR trước khi đưa máy

Là khách kiosk, tôi muốn trả tiền bằng QR và thấy trạng thái rõ, để máy không dán khi tôi chưa trả.

**Acceptance criteria**

- Given tôi đã xác nhận preview, when QR được tạo, then order có id ổn định và trạng thái AwaitingPayment.
- Given cổng `paid`, when kiosk nhận sự kiện, then mới cho insert.
- Given `failed` hoặc hết hạn, when tôi chưa Paid, then khay không nhận máy và không `start`.
- Given `unknown`, when chưa có quyết định Q-004, then **không** `start` (Assumption vận hành an toàn).
- Priority: P0. Dependency: A-003. Source: FR-003, FR-004, FR-007.

### US-003: An toàn khay và E-stop

Là khách hoặc người đi đường, tôi muốn thấy khay khóa, E-stop, và đường lấy máy khi có sự cố, để tôi dám đặt điện thoại vào kiosk.

**Acceptance criteria**

- Given order Paid và so khớp pass, when apply bắt đầu, then khay Locked và `start` chỉ từ controller local.
- Given E-stop hoặc mất safety signal, when đang chuyển động, then motion dừng, không resume tự động.
- Given mất điện, when hệ thống chết, then máy lấy ra được bằng mở thủ công ủy quyền; không kẹp.
- Priority: P0. Dependency: FR-018, Q-007. Source: FR-005, FR-010, FR-011, FR-012.

### US-004: Nhân viên xử lý fault và hoàn phí dịch vụ

Là operator, tôi muốn xem log, mở khóa, và xác nhận hoàn phí dịch vụ, để khách không bị kẹt máy và tranh cãi miệng.

**Acceptance criteria**

- Given FailedHold, when tôi đăng nhập console ủy quyền, then tôi xem order id, from/to state, reason, và (nếu có) ảnh QC.
- Given tôi xác nhận hoàn phí dịch vụ, when cổng hoàn thành refund, then ledger ghi Refunded, không double refund (idempotent).
- Given tôi mở khóa thủ công, when khay mở, then audit ghi actor, timestamp, reason.
- Priority: P1. Dependency: Q-005. Source: FR-013, FR-016, FR-011.

### US-005: Chủ dịch vụ xem sức khỏe máy không PII

Là service owner, tôi muốn xem giao dịch, fault và sức khỏe kiosk, để biết máy có chạy được ca không.

**Acceptance criteria**

- Given các order đã đóng, when tôi mở console owner, then thấy đếm giao dịch, doanh thu phí dịch vụ, fault — không tên/SĐT/ảnh mặt khách.
- Priority: P2. Dependency: FR-014. Source: FR-017, NFR-006.

## 8. Data Model

| Entity | Key fields | Relationships | Lifecycle | Classification | Owner |
|---|---|---|---|---|---|
| Kiosk | kioskId, siteId, softwareVersion, controllerHealth | 1—* Order | Active / Maintenance / Offline | Operational | Service owner |
| DeviceModel | modelId, displayNameVi, profileGeometry, fixtureId, whitelistFlag | 1—* StickerSku; 1—* Order | Draft / Whitelisted / Retired | Operational | Group 6 |
| StickerSku | skuId, modelId, designNameVi, price, expectedDurationSec, stockQty | *—1 DeviceModel | Active / OutOfStock / Retired | Operational | Operator restock |
| Order | orderId (business id), kioskId, modelId, skuId, state, amounts | 1—0..1 Payment; 1—0..1 ApplyJob | Created → … → Completed/Refunded/Cancelled | Transaction | Ledger |
| Payment | paymentId, orderId, provider, qrPayloadRef, providerStatus, localStatus | *—1 Order | Pending / Paid / Failed / Unknown / Expired | Payment metadata, **no PAN/card** | Payment adapter |
| ApplyJob | jobId, orderId, lockedFlag, start/stop timestamps, result | *—1 Order | NotStarted / Running / Passed / Failed / Aborted | Operational | Controller |
| SensorCheck | checkId, jobId, type (pose/size/case/obstruction), passFail, measured | *—1 ApplyJob | Recorded | Operational | Controller |
| QcImage | imageId, orderId, storedUntil, storageLocation, purpose=incident | 0..* —1 Order | Captured / Retained / Purged | Restricted incident media | Privacy owner (Q-006) |
| FaultEvent | faultId, kioskId, orderId?, code, severity, safetyStop | *—0..1 Order | Open / Acked / Closed | Operational | Operator |
| RefundRequest | refundId, orderId, amount, mode=service-fee, status | *—1 Order | Open / Confirmed / Paid / Rejected | Transaction | Operator / owner |
| AuditLog | auditId, at, actor, action, entityRef, fromState, toState, reason | append-only | Immutable | Audit | System |
| StaffAccount | staffId, role (operator/owner), credentialRef | authorize unlock/refund | Active / Revoked | Staff credential | Service owner |

**Source of truth:** Order state machine + AuditLog (append-only). Sensor pass/fail là dữ liệu đo, không suy ra model. QcImage không phải danh tính người.

**Order states:** `Created` → `AwaitingPayment` → `Paid` \| `PaymentFailed` \| `PaymentUnknown` \| `Expired` → (từ Paid) `AwaitingInsert` → `Locked` → `Applying` → `QcPending` → `Completed` \| `FailedHold` → `StaffReview` → `Refunded` \| `ReleasedWithoutApply`. Safety: `Estopped` / `SafeHold` từ hầu hết trạng thái sau insert.

## 9. API and Integration Contract

API là **hợp đồng logic** (không khóa framework). Auth: kiosk service principal cho lệnh máy; staff session cho console. Idempotency key bắt buộc với payment và refund.

| API/Event ID | Method/path | Purpose | Auth | Request/response | Errors |
|---|---|---|---|---|---|
| API-001 | POST /orders | Tạo draft order model+SKU | Kiosk | {kioskId, modelId, skuId} → {orderId, state} | 409 SKU mismatch / out of stock |
| API-002 | POST /orders/{id}/preview-ack | Khách đã xem giá/an toàn | Kiosk | {accepted:true} → {state} | 422 chưa đủ copy bắt buộc |
| API-003 | POST /orders/{id}/payments/qr | Tạo QR, state AwaitingPayment | Kiosk | {} → {qrDisplay, expiresAt} | 409 không đúng state |
| EVT-001 | Payment webhook/poll | Cổng `paid`/`failed`/`unknown` | Provider signature | {orderId, providerRef, status} | Unknown → không start |
| API-004 | POST /orders/{id}/insert-ready | Cho phép mở khay nhận máy | Kiosk + Paid check | {} → {allowed} | 403 chưa Paid |
| API-005 | GET /controller/status | locked, error, motion, eStop | Local only | {locked, error, eStop, motion} | timeout → SafeHold |
| API-006 | POST /controller/lock | Đóng khóa khay | Local, order Paid | {orderId} → {locked:true} | 409 safety |
| API-007 | POST /controller/start | Bắt đầu apply | Local, Paid+Locked | {orderId, idempotencyKey} | 403 thiếu Paid/Lock; 409 eStop |
| API-008 | POST /controller/stop | Dừng motion | Local / E-stop path | {reason} → {motion:false} | — |
| API-009 | POST /staff/unlock | Mở thủ công ủy quyền | Staff operator | {orderId, reason} → {unlocked} + audit | 403 |
| API-010 | POST /staff/refunds | Xác nhận hoàn phí dịch vụ | Staff operator | {orderId, amount, idempotencyKey} | 409 already refunded |
| API-011 | GET /orders/{id}/ledger | Lịch sử state | Staff / kiosk | append-only events | 404 |
| API-012 | POST /qc-images | Lưu ảnh sự cố + expiry | Local/backend | {orderId, bytesRef, storedUntil} | 400 thiếu retention |
| EVT-002 | AuditAppend | Mọi chuyển state | System | {from,to,reason,actor,at} | never mutate |

**Quy tắc:** Backend **không** gọi API-007. App khách **không** tồn tại trong MVP và sẽ bị cấm gọi controller nếu thêm sau.

## 10. Non-Functional Requirements

| ID | Category | Target | Measurement | Priority | Owner |
|---|---|---|---|---|---|
| NFR-001 | Performance | Chu kỳ thành công ≤ 5 phút (lab) | 20 run nội bộ / model, percentile tường thuật | Should | Group 6 |
| NFR-002 | Quality | Offset ≤ 1.5 mm | Đo mẫu lab vs profile | Should | Group 6 |
| NFR-003 | Quality | First-pass ≥ 80% | ≥ 20 apply nội bộ / model | Should | Group 6 |
| NFR-004 | Safety | 0 xước/nứt/kẹt không lấy được máy ở lab acceptance | Checklist nghiệm thu + log E-stop/unlock | Must | Group 6 |
| NFR-005 | Operability | Có người trực khi máy tình nguyện viên | Roster ca (Q-007) | Must | Group 6 |
| NFR-006 | Privacy | Không PII khách, không card data | Review data model + storage | Must | Group 6 |
| NFR-007 | Privacy | Ảnh QC có retention và purge | Job xóa theo storedUntil (Q-006) | Must | Group 6 |
| NFR-008 | Availability | An toàn local khi mất mạng; sync ledger idempotent | Test mất mạng/mất điện trước acceptance | Must | Group 6 |
| NFR-009 | Accessibility | Copy tiếng Việt rõ, contrast đọc được trên kiosk đứng | Review UI người lạ | Must | Group 6 |
| NFR-010 | Security | Lệnh máy chỉ local controller; staff unlock có authz | Threat review + test negative | Must | Group 6 |

## 11. Security, Privacy and Compliance

- **Authentication and authorization:** Không tài khoản khách. Kiosk app + controller = trusted local. Console nhân viên: vai trò operator vs owner. Unlock và refund là hành động đặc quyền, luôn audit.
- **Sensitive data and classification:** Order id, số tiền, SKU — transactional. QcImage — restricted incident. Cấm nhận diện người. Cấm lưu thẻ.
- **Audit and traceability:** Mọi chuyển Order/Payment/ApplyJob/Unlock/Refund → AuditLog append-only (FR-014).
- **Retention/deletion:** QcImage theo Q-006; cho đến khi chốt, **Assumption:** không upload cloud công cộng; lưu local có hạn mặc định đề xuất 14 ngày (nhãn Assumption, chưa Decision).
- **Applicable policy:** Chính sách hoàn **phí dịch vụ** do nhóm công bố trước trial. Không cam kết bảo hiểm thiết bị. Mall fire/walkway/liability = rủi ro site (R-006), ngoài MVP phần mềm nhưng chặn trial mall.

## 12. Delivery Plan and Dependencies

| Increment | Scope | Dependency | Exit criteria | Risk |
|---|---|---|---|---|
| 0. Discover/Define | Intent → blueprint → GitHub issues/project | GitHub auth (hiện **blocked**) | Issue theo FR/NFR/SP, Project fields chuẩn | Auth |
| 1. Simulator + UI | Catalog, preview VN, state machine, simulator `start/stop/status/locked/error` | FR-018 simulator | Người lạ đi hết flow trên simulator | Hardware muộn (R-003) |
| 2. Payment sandbox | QR sandbox, Paid gate, unknown handling policy | A-003, Q-004 | Không start khi chưa Paid; test double-charge | Cổng `unknown` (R-002) |
| 3. Safety | Lock, E-stop, unlock ủy quyền, mất điện/mạng | Module thật hoặc harness | NFR-004 trên harness | Hardware muộn |
| 4. Apply quality lab | Profile check, apply trên 3–5 model, ngưỡng lab | Q-001, Q-002, A-001, A-002 | NFR-001–003 nội bộ | Chất lượng (R-005) |
| 5. Staff + refund | Console, refund dịch vụ, audit evidence | Q-005 | UC-004 có bằng chứng test | Tranh chấp xước máy (R-001) |
| 6. Trial có người trực | Site lab/sảnh, roster E-stop | Q-007, NFR-005 | BR-001–003 có evidence | Site owner (R-006) |

**Branch/PR (khi có GitHub):** `<type>/<issue-number>-<short-slug>`; PR `Closes #n` / `Refs #n`. Comment bắt buộc: Progress, Summary, Evidence, Branch/PR, Next, Blocker.

## 13. Traceability Matrix

| Business goal | Requirement | Use case/story | API/data/NFR | Test evidence |
|---|---|---|---|---|
| An toàn, máy lấy ra được | BR-001, FR-005, FR-010, FR-011, FR-012 | UC-005, US-003 | API-005–009, NFR-004, NFR-005, NFR-008, NFR-010 | Chưa — lab acceptance |
| Chất lượng đo được | BR-002, FR-006, FR-008 | UC-003 | SensorCheck, QcImage, NFR-001–003 | Chưa — 20 run/model |
| Tự phục vụ người lạ | BR-003, FR-001, FR-002, FR-015 | UC-001, UC-002, US-001 | API-001–004, NFR-009 | Chưa — trial người lạ |
| Không dán khi chưa Paid | BR-004, FR-003, FR-004, FR-007 | UC-002, US-002 | EVT-001, API-007, Payment | Chưa — sandbox QR |
| Fail → giữ máy + hoàn phí dịch vụ | BR-005, FR-009, FR-016 | UC-004, US-004 | API-010, RefundRequest, AuditLog | Chưa — fault drill |
| Chủ dịch vụ vận hành | FR-013, FR-014, FR-017 | US-005 | API-011, ledger | Chưa |
| Hardware thay được | FR-018 | UC-003 | API-005–008 | Simulator bắt buộc Increment 1 |

## 14. Risks and Decisions

| ID | Risk/decision | Impact | Likelihood | Owner | Mitigation/status |
|---|---|---|---|---|---|
| R-001 | Khách cáo buộc xước/nứt/kẹt máy | Critical | Medium | Group 6 | Khay an toàn, E-stop, unlock, audit, hoàn phí dịch vụ thôi; nhân viên trực (NFR-005) |
| R-002 | Cổng QR `unknown` sau khi khách quét | High | Medium | Group 6 | Cấm `start` đến khi chốt Q-004; đối soát thủ công |
| R-003 | Hardware muộn, chỉ còn UI giả lập | High | Medium | Group 6 | Simulator Increment 1; không nhận đã test BR-001/002 nếu chỉ UI |
| R-004 | Không có staff khi khay kẹt | Critical | Medium | Group 6 | Không trial máy thật khi thiếu roster (Q-007) |
| R-005 | Lệch/bọt hệ thống → hoàn hàng loạt, gãy giả thuyết chất lượng | High | Medium | Group 6 | Khóa ngưỡng trước trial công khai; 20 run/model |
| R-006 | Site owner chặn đặt máy (điện, PCCC, lối đi, bảo hiểm) | High | Medium | Group 6 | Trial lab/sảnh trước mall |
| R-007 | Ảnh lưng máy không retention → rủi ro dữ liệu | Medium | Medium | Group 6 | NFR-007; không bật lưu ảnh đến khi Q-006 chốt |
| D-001 | Decision | MVP hoàn **phí dịch vụ**, không bảo hiểm máy | — | Intent | Confirmed |
| D-002 | Decision | Không AI detect model | — | Intent | Confirmed |
| D-003 | Decision | Charge QR trước, rồi insert | — | Intent | Confirmed |
| D-004 | Decision | Controller local là nơi duy nhất lệnh applicator | — | Intent | Confirmed |

## 15. Quality Review

- **Quality gate:** Gate 1–4 **In progress / Passed ở mức Draft**. Gate 5 **Failed** — chưa tạo GitHub repo/Issue/Project vì `gh` không có token (`GH_TOKEN` / `gh auth login`).
- **Unresolved questions:** Q-001 … Q-007 (phần 4).
- **Reviewers:** Group 6; giảng viên (ST-005) khi Ready for Review.
- **Approval decision:** **Draft** — đủ để tạo backlog GitHub; chưa Approved. Không đánh Ready for Review cho đến khi Q-001/Q-002 có hướng và Gate 5 chạy được.

### Checklist (rút từ governance/review-checklist.md)

- [x] Vấn đề và outcome đo được (ngưỡng lab = Assumption, không SLA).
- [x] In/out of scope rõ.
- [x] Stakeholder; decision maker đồ án = nhóm + giảng viên.
- [x] Happy / alternate / error path (Paid, unknown, fail, E-stop, mất điện).
- [x] Story có AC Given/When/Then.
- [x] Data ownership, retention (ảnh = Open Question).
- [x] API có auth/error/idempotency ở mức hợp đồng.
- [x] NFR có metric.
- [ ] Assumption quan trọng đã owner **xác nhận** — chưa.
- [ ] Gate 5 GitHub Delivery — blocked auth.
