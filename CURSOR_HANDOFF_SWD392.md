# HANDOFF CHO CURSOR — SWD392 SE1927 Group 6

**Dự án:** Máy Dán Sticker Điện Thoại Tự Động (Automatic Phone Sticker Kiosk)  
**Ngày bàn giao:** 2026-09-21  
**Nguồn sự thật nghiệp vụ:** `artifacts/DacTaNghiepVu_MVP_v2.docx` (v2.0)  
**Lệnh cho Cursor:** triển khai sơ đồ + đặc tả hệ thống/phần mềm. **Bỏ qua phần cứng vật lý** (không thiết kế BOM, không chọn tay robot trong tài liệu SW). Phần cứng chỉ xuất hiện như *actor/interface* (Local Controller, sensor events, lệnh nghiệp vụ).

Mọi Use Case, Activity, State, Sequence, ERD, API, test case **bắt buộc map được sang mã BR-/GR-/PR-/SR-/TR-** trong v2. Không bịa rule mới trái v2. Số có nhãn `[MVP-DEFAULT]` đổi thì phải ghi chú, không sửa ngầm.

---

## 0. Việc Cursor phải làm (ưu tiên)

1. Use Case diagram đúng actor sticker-kiosk (không copy tab xe điện).
2. Activity / BPMN happy path + nhánh lỗi theo cổng mục 9 v2.
3. State machine ORDER đúng mục 10 v2 (cấm nhảy cóc).
4. ERD hoàn thiện từ tab Trang-4 (đang vẽ) + entity bắt buộc mục 18 v2.
5. Sequence: tạo QR → webhook Paid; interlock apply; refund; e-stop.
6. Đặc tả API / contract local↔cloud (MQTT + REST) mức phần mềm.
7. Test case nghiệm thu mục 17 v2.

**Không làm lúc này:** bản vẽ cơ khí, BOM gantry/Dobot/RoArm, firmware chi tiết stepper.

---

## 1. File nguồn trong project

| File | Vai trò |
|---|---|
| `attachments/SWD392_SE1927_Group 6 (1).pdf` | Intent **v1** — hướng ban đầu, còn lỗ hổng. Tham khảo lịch sử, **không** là rule hiện tại. |
| `artifacts/DacTaNghiepVu_MVP_v2.docx` | **Đặc tả nghiệp vụ đã khóa.** Mọi thiết kế SW bám file này. |
| `attachments/hoànhthanh1.json` | diagrams.net. Tab **UseCase / ERD / DB = ví dụ xe điện**, bỏ. Tab **Trang-4 = ERD kiosk đang vẽ** — tiếp tục từ đây. |

### Tab JSON

- `UseCase`, `ERD`, (và tab DB nếu có): template Dealer / EV Brand / Vehicle — **không dùng**.
- `Trang-4`: Mermaid `erDiagram` sticker kiosk. Đang có hướng đúng nhưng thiếu so với v2 (chưa đủ KIOSK_STOCK, QUALITY_CHECK, STAFF_ACTION_LOG, session, snapshot giá, attempt_align_count, purpose CHARGE/REFUND…).

---

## 2. Sản phẩm MVP (phần mềm)

- 01 kiosk tự phục vụ tại điểm thử (mall). Khách chọn model + mẫu sticker cắt sẵn → trả QR → **mới** được đặt máy → local khóa khay → dán theo **template kích thước** (không AI) → QA camera → trả máy.
- 3–5 model lưng phẳng, catalog hữu hạn, 01 cổng VietQR, UI chính = màn kiosk.
- Data model thiết kế đa kiosk; vận hành MVP = 1 máy.

### Ngoài phạm vi MVP (cấm)

- In/cắt tem tại chỗ; thiết kế tùy ý.
- AI nhận model / ốp / trầy.
- Máy gắn ốp, lưng cong, nứt, ướt, ngoài danh sách.
- App khách đặt xa / điều khiển robot.
- Cash, thẻ, trả góp, nhiều PSP.
- Hệ thống tự bồi thường giá điện thoại.

---

## 3. Nguyên tắc P1–P6

- **P1** An toàn trước doanh thu.
- **P2** Không lấy tiền nếu không bán được dịch vụ; lỗi hệ thống phải có đường hoàn.
- **P3** `ORDER.status` là nguồn sự thật nghiệp vụ. Log không mâu status.
- **P4** **Local = an toàn máy. Cloud = tiền.** Robot không nhận lệnh từ ĐT khách. Mất mạng không bịa Paid.
- **P5** Khách ẩn danh mặc định. SĐT tùy chọn.
- **P6** UI chính = kiosk. ĐT chỉ quét QR.

---

## 4. Actor

| Ký hiệu | Tên | Việc |
|---|---|---|
| CUS | Khách vãng lai | Chọn, tick điều kiện, trả QR, tháo ốp, lau, đặt/lấy máy. Bấm e-stop vật lý. |
| SYS | Hệ thống kiosk (UI + orchestration) | Cổng bán, UI, gọi cloud/local. |
| LOC | Local controller | Khay, robot, sensor, e-stop. Quyết định được phép chạy robot. |
| CLD | Cloud backend | Order, payment, refund, báo cáo, sync. |
| STF | Nhân viên hỗ trợ | PIN mở khóa, sự cố, nạp tem, xác nhận hoàn tranh chấp. |
| OPS | Quản lý vận hành | Giá/model/ngưỡng, duyệt hoàn tay, KPI, phân quyền. |
| PAY | Payment provider | QR, Paid/Failed, refund. Không lưu PAN. |

TTTM / bảo hiểm / vendor robot = ngoài hệ thống.

---

## 5. Use case cần vẽ (gợi ý pack)

**CUS trên kiosk**

- UC01 Bắt đầu phiên / chọn dịch vụ
- UC02 Chọn model
- UC03 Chọn pattern/SKU
- UC04 Xác nhận 4 điều kiện an toàn
- UC05 Thanh toán QR
- UC06 Hủy đơn chưa Paid
- UC07 Hủy đơn đã Paid chưa khóa khay
- UC08 Đặt máy / đặt lại (max 2)
- UC09 Lấy máy
- UC10 Bấm e-stop vật lý

**SYS/LOC**

- UC20 Reserve tồn + tạo QR
- UC21 Nhận webhook / inquiry thanh toán
- UC22 Kiểm tra khớp template (không AI)
- UC23 Khóa khay
- UC24 Apply sticker (1 lần / đơn)
- UC25 Quality check
- UC26 Hoàn tiền tự động theo ma trận PR
- UC27 Timeout Paid / QR / pickup
- UC28 Queue event khi mất mạng
- UC29 Đưa kiosk SERVING / OUT_OF_SERVICE theo GR

**STF/OPS backoffice**

- UC30 Đăng nhập PIN/thẻ
- UC31 ManualRecovery + mở khóa
- UC32 Reset e-stop + HOME
- UC33 Nạp tồn đúng slot
- UC34 Checklist mở/đóng ca
- UC35 Đề nghị / duyệt hoàn tay
- UC36 Tắt model/SKU, sửa giá, ngưỡng an toàn
- UC37 Xử lý UnclaimedDevice
- UC38 Xem INCIDENT + ảnh

**Không** vẽ use case “đăng ký tài khoản khách”, “AI nhận model”, “app điều khiển robot”.

---

## 6. Happy path + cổng (Activity)

0. Kiosk rảnh — cần **GR-01…GR-08**
1. CUS bắt đầu → ORDER `Created` (anonymous, origin=KIOSK)
2. Chọn model + pattern theo **BR-CAT-01/02**; giá khóa **BR-CAT-03**; vị trí = template SKU **BR-SEL-01**
3. Tick đủ 4 điều kiện; SYS vẫn tự đo ở bước 7 **BR-SEL-02**
4. Thanh toán: reserve + QR 5 phút; **cấm đặt máy trước Paid** **BR-PAY-01**; webhook mới là Paid **BR-PAY-02**
5. Paid → cửa sổ đặt máy 5 phút. Fail/hết hạn QR → `PaymentFailed` → `Cancelled`, nhả reserve
6. Tháo ốp, lau, đặt theo silhouette
7. Đo vs template model đã chọn (không nhận diện model)
8. Pass → khóa khay → `Locked`
9. Apply chỉ khi **BR-LCK-01**. Một đơn một lần apply **BR-APL-02**
10. QA overlay
11. Pass → mở khay `ReadyForPickup` (3 phút) → khay trống `Completed`

4 tick bắt buộc: đúng model đã chọn; đã/sẽ tháo ốp và phụ kiện; lưng khô không nứt sẽ lau; hiểu khay khóa / sự cố do nhân viên.

---

## 7. Kiểm tra thiết bị (bước 7) — không AI

| Tiêu chí | Fail |
|---|---|
| Khay trống | Không đổi status, yêu cầu đặt |
| Nhiều vật | `DeviceMisaligned` |
| WxH lệch > ±1.5 mm so template | `DeviceUnsupported` |
| \|yaw\| > 3° | `DeviceMisaligned`, cho đặt lại |
| Offset tâm > 2 mm | `DeviceMisaligned` |
| Dày hơn template + 1.0 mm | `DeviceUnsupported` (nghi ốp) |
| Tay người | Không khóa; >20s vẫn có tay → không khóa |

- **BR-DEV-01** Chỉ khớp / không khớp template đã chọn.
- **BR-DEV-02** Đặt lại tối đa **2** lần trên đơn Paid. Lần 3 → hoàn.
- **BR-DEV-03** Cấm nút skip.

---

## 8. QA (bước 10)

Pass nếu: mọi cạnh lệch ≤ 1.5 mm (Z); xoay ≤ 1.5°; không đè camera bump (mask model); không bọt > 3 mm; không hở góc/nhăn; mã tem khớp SKU nếu có.

Fail → `QualityCheckFailed`, **giữ khóa**, INCIDENT, không tự mở.

---

## 9. State machine ORDER

**Happy:**  
`Created → PaymentPending → Paid → DeviceInserted → Locked → Applying → QualityChecking → ReadyForPickup → Completed`

**Kết / lỗi:**  
`PaymentFailed`, `PaymentUnknown`, `DeviceUnsupported`, `DeviceMisaligned`, `ApplicationFailed`, `QualityCheckFailed`, `PowerLost`, `NetworkDegraded`, `EmergencyStopped`, `ManualRecovery`, `RefundPending`, `Refunded`, `Cancelled`, `UnclaimedDevice`

Chuyển hợp lệ — copy đúng bảng mục 10.2 v2. Lưu ý:

- `DeviceMisaligned` còn lượt → quay hướng dẫn đặt lại (về cửa sổ Paid / DeviceInserted, không apply).
- `DeviceUnsupported` / hết lượt lệch → mở cho rút máy rồi `RefundPending`.
- `*Failed` / PowerLost / E-stop → `ManualRecovery` chỉ STF/OPS.
- `RefundPending` → `Refunded` hoặc fail 3 lần/24h → `ManualRecovery`.

**BR-STA-01** Cấm nhảy cóc (`Paid→Applying`, `Created→Locked`, …).  
**BR-STA-02** `Completed` / `Refunded` / `Cancelled` là kết. OPS chỉ bút toán, không chạy robot lại.

---

## 10. Rule bắt buộc (index)

### Catalog / stock
- **BR-CAT-01** Model hiện khi `is_supported` AND còn SKU active còn hàng tại kiosk này.
- **BR-CAT-02** Pattern hiện khi có SKU khớp model + `stock_available > 0`.
- **BR-CAT-03** Giá snapshot lúc xác nhận; không đổi sau tạo order.
- **BR-CAT-04** `estimated_seconds` làm tròn lên phút — không phải SLA pháp lý.
- **BR-CAT-05** OPS tắt catalog: đơn Paid không hủy vì tắt; đơn chưa trả thì không cho trả tiếp.
- **BR-STK-01** `available = on_hand − reserved`. Reserve khi tạo QR thành công.
- **BR-STK-02** Reserve tối đa 7 phút hoặc fail/timeout/cancel → nhả.
- **BR-STK-03** `apply_success` → `on_hand -= 1`, nhả reserve.
- **BR-STK-04** Apply fail nhưng picker = taken → vẫn trừ, không dùng lại tấm.
- **BR-STK-05** ≤ threshold → cảnh báo STF; =0 → ẩn SKU.
- **BR-STK-06** Chỉ STF/OPS nhập tồn + `MAINTENANCE_LOG RESTOCK`.

### Khách
- **BR-CUS-01** Không bắt login.
- **BR-CUS-02** SĐT tùy chọn, 10 số VN.
- **BR-CUS-03** Không lưu face ID. Camera = căn chỉnh + chứng cứ sự cố.
- **BR-CUS-04** Chỉ `payment_id`, amount, status, paid_at.
- **BR-CUS-05** Ảnh QA pass giữ 24h; ảnh sự cố/QA fail 30 ngày hoặc đến đóng INCIDENT.

### Cổng kiosk SERVING (GR)
- **GR-01** mode SERVING (không OOS / MAINTENANCE / EMERGENCY_STOP)
- **GR-02** heartbeat local < 5s, sensor healthy
- **GR-03** robot HOME, không job dở, không fault
- **GR-04** khay trống, mở, không khóa
- **GR-05** còn ≥1 SKU
- **GR-06** payment provider healthy
- **GR-07** cloud reachable; mất cloud >2 phút khi chưa có đơn → OOS (MVP)
- **GR-08** đủ cấu hình `max_force_n`, `align_tolerance_mm`, `qa_offset_max_mm`

### Thanh toán
- **BR-PAY-01** Không `DeviceInserted` nếu chưa Paid.
- **BR-PAY-02** Webhook = nguồn Paid. Cấm nút “Tôi đã trả”.
- **BR-PAY-03** Webhook ≠ inquiry → `PaymentUnknown`, không dán, giữ reserve tối đa 15 phút.
- **PR-01** Một ORDER nhiều PAYMENT (thử QR, đối soát, hoàn).
- **PR-02** Chỉ 01 PAYMENT Success / ORDER.
- **PR-03** Amount QR = SKU.price lúc Created; sai amount → từ chối webhook.
- **PR-04** Idempotent `provider_payment_id`.
- **PR-05** Không phụ phí / tip / bán kèm.
- **PR-06** Hoàn đúng số Success, về đúng giao dịch PSP. Không hoàn tiền mặt.
- **PR-07** Từ chối hoàn phải hiện lý do.
- **PR-08** RefundPending >24h → escalate OPS; vẫn trả máy theo an toàn.

### Máy / apply
- **BR-LCK-01** `robot_enable = (ORDER=Locked) AND tray_locked AND e_stop=false AND payment=Paid AND sku reserved`
- **BR-APL-01** Lực / mất bước / mở khay / e-stop / mất sensor → halt, `ApplicationFailed`, giữ khóa, INCIDENT HIGH
- **BR-APL-02** Không auto-retry apply. Max 1 apply / order
- **SR-01** Firmware/local chặn robot nếu khay chưa locked, kể cả cloud gửi nhầm
- **SR-02** E-stop cắt motion ngay; `EmergencyStopped`; khay giữ nguyên khóa
- **SR-03** Chỉ STF/OPS reset e-stop khi vùng trống
- **SR-04** Lực > `max_force_n` → halt. Đề xuất 15 N (đo prototype)
- **SR-05** Cấm apply khi camera/sensor timeout

### Điện / mạng
- **SR-10…13** UPS snapshot; `PowerLost`; không tự mở khay; **không tự resume**; STF ManualRecovery; chưa dán → hoàn 100%; mục tiêu an toàn ≤2 phút sau có điện
- **SR-20** Local = khay/robot; Cloud = tiền
- **SR-21** Pending + mất mạng: không đoán Paid
- **SR-22** Sau Paid + snapshot local: được tiếp bước máy; cấm tạo payment mới
- **SR-23** Mất cloud >2 phút, chưa đơn → OOS
- **SR-24** Queue event, đúng thứ tự, idempotent

### Timeout [MVP-DEFAULT]
| Cửa sổ | Giá trị | Hết hạn |
|---|---|---|
| Created không chọn xong | 120s | Cancelled |
| QR | 300s | PaymentFailed, nhả reserve |
| Paid → phải có máy | 300s | RefundPending |
| Đặt lại khi lệch | 90s / lần | tính 1 fail; hết 2 lần → hoàn |
| ReadyForPickup | 180s | UnclaimedDevice, không nhận đơn mới |
| PaymentUnknown đối soát | 15 phút | ManualRecovery, không dán |
| Màn không chạm (chưa Paid) | 45s | Reset UI |
| Reserve stock | 7 phút | nhả |

**TR-01** Đã Paid: không reset phiên để phục vụ khách khác.  
**TR-02** UnclaimedDevice: STF xác nhận; 24h không người → OPS ngoài hệ thống.

### Quyền
- **BR-ACL-01** Mọi đổi state do người: `actor_id`, lý do, thời điểm, kiosk_id, order_id. Cấm PIN dùng chung dán tem.

CUS không mở khóa Locked/Applying. SYS không tự ManualRecovery. STF đề nghị hoàn tay; OPS duyệt. OPS đổi giá/model/ngưỡng.

### Sự cố / ca
- **BR-INC-01…04** Incident khi fail/e-stop/powerlost có máy trong khay; phần mềm không tự bồi thường máy; STF tick hiện trường; không đưa máy người lạ trừ bảo vệ TTTM (`handover_external`).
- **BR-OPS-01…05** Checklist mở ca; không tắt nguồn nếu còn đơn sống; nạp đúng slot; hết giấy lau vẫn SERVING; hết tem → OOS; quá hạn BT cảnh báo, không tự tắt trừ `force_maintenance`.

---

## 11. Ma trận hoàn tiền (vẽ thành decision table)

| Tình huống | Hoàn |
|---|---|
| QR hết hạn / pay fail | Không thu → không hoàn |
| Paid, hủy trước khóa khay | Tự động 100% trong 15 phút |
| Paid, timeout không đặt | Tự động 100% |
| Unsupported / hết lượt lệch | 100% sau cảm biến khay trống |
| PaymentUnknown rồi xác nhận không có tiền | Không hoàn. Nếu PSP sau báo có tiền → hoàn 100% |
| ApplyFailed tem chưa chạm | 100% + staff mở khóa |
| ApplyFailed tem đã chạm | 100% + incident; không tự gỡ tem |
| QA fail, khách không nhận | 100% sau STF xác nhận |
| QA fail, khách vẫn nhận | 100% (MVP không bán hàng lỗi) |
| Completed QA pass, đổi ý | **Từ chối** |
| Hư máy / trầy / tranh chấp | OPS duyệt; SW không tự bồi thường thiết bị |
| Nghi gian lận | OPS; khóa hoàn tự động; giữ camera |

---

## 12. ERD — entity bắt buộc (mục 18 v2)

Bắt buộc:  
`PHONE_MODEL`, `STICKER_PATTERN`, `STICKER_ITEM`, `KIOSK`, `KIOSK_STOCK`, `ORDER`, `PAYMENT`, `TRANSACTION_STATE_LOG`, `QUALITY_CHECK`, `ROBOT_ARM`, `ROBOT_EVENT_LOG`, `STAFF`, `STAFF_ACTION_LOG`, `INCIDENT_REPORT`, `REFUND_REQUEST`, `MAINTENANCE_LOG`  
`CUSTOMER` tùy chọn.

Gợi ý bổ sung phần mềm: `KIOSK_SESSION`, `DEVICE_INSPECTION` (kết quả đo bước 7), `PAYMENT_WEBHOOK_LOG`.

### Field tối thiểu

- `PHONE_MODEL`: id, name, is_supported, width_mm, height_mm, thickness_mm, camera_mask, align_template_uri, qa_offset_max_mm override?
- `STICKER_PATTERN`: id, name, preview_uri
- `STICKER_ITEM`: pattern_id, phone_model_id, price, estimated_seconds, active, slot_code
- `KIOSK`: id, mode ∈ {SERVING, OUT_OF_SERVICE, MAINTENANCE, EMERGENCY_STOP}, config JSON (max_force_n, align_tolerance_mm, qa_offset_max_mm)
- `KIOSK_STOCK`: kiosk_id, sticker_item_id, on_hand, reserved, reorder_threshold
- `ORDER`: status ∈ tập 10.1, kiosk_id, phone_model_id, sticker_item_id, price_snapshot, attempt_align_count, customer_id nullable, phone_optional, started_insert_at, origin=KIOSK
- `PAYMENT`: order_id, provider, provider_payment_id, amount, status, purpose ∈ {CHARGE, REFUND}, paid_at
- `QUALITY_CHECK`: order_id, offset_mm, rotation_deg, pass, photo_uri
- `TRANSACTION_STATE_LOG`: order_id, from_status, to_status, actor, reason, at
- `ROBOT_ARM`: kiosk_id, state, home, fault
- `ROBOT_EVENT_LOG`: raw events, force, sku_slot, picker_taken
- `INCIDENT_REPORT`: order_id, level, photos, force_log, tray_has_device, sticker_contacted, customer_present
- `REFUND_REQUEST`: payment_id, amount, auto/manual, status
- `STAFF` + `STAFF_ACTION_LOG`
- `MAINTENANCE_LOG`: RESTOCK / CLEAN / CHECKLIST / SERVICE

### Cardinality gợi ý

- PHONE_MODEL 1—N STICKER_ITEM  
- STICKER_PATTERN 1—N STICKER_ITEM  
- KIOSK 1—N ORDER, 1—N KIOSK_STOCK, 1—1..N ROBOT_ARM  
- STICKER_ITEM 1—N KIOSK_STOCK  
- CUSTOMER 0..1—N ORDER  
- ORDER 1—N PAYMENT  
- ORDER 1—N TRANSACTION_STATE_LOG  
- ORDER 0..1—N QUALITY_CHECK  
- ORDER 0..1—N INCIDENT_REPORT  
- ORDER 0..N REFUND_REQUEST  
- PAYMENT 0..N REFUND_REQUEST  

Trang-4 cũ có `ORDER ||--|| PAYMENT` — **sai so với PR-01**. Sửa thành 1—N.

---

## 13. Kiến trúc phần mềm (không cần chọn hãng tay)

```
[Kiosk UI web]
    REST → [Cloud: Order, Catalog, Payment, Refund, Staff]
    MQTT/WS → [Local Controller]
                    ← sensor events
                    → commands nghiệp vụ (không phải joint angle)
[Payment Provider] webhook → Cloud
```

### Lệnh local (contract Cursor nên spec)

Cloud/SYS → LOC: `home`, `inspect_device`, `lock_tray`, `unlock_tray`, `pick_sku(slot)`, `apply(template_id)`, `qa_capture`, `estop_ack`, `safe_halt`

LOC → Cloud: `heartbeat`, `tray_empty|occupied|locked`, `inspect_result`, `apply_success|apply_failed`, `picker_taken`, `force_n`, `estop`, `sensor_fault`, `power_lost`

Local tự từ chối `apply` nếu thiếu BR-LCK-01 / SR-01.

Khi chưa có máy thật: **Robot Mock** cùng contract MQTT.

---

## 14. KPI / nghiệm thu SW (mục 16–17)

- X: Paid → ReadyForPickup ≤ 5 phút (không tính khách lau lâu)
- Y: QA pass lần đầu lab ≥ 90%
- Z: lệch ≤ 1.5 mm
- Lab: 0 sự cố trầy ở kịch bản chuẩn
- A: ≥80% GD không cần STF
- B: STF nhận incident ≤ 5 phút
- C: an toàn sau có điện ≤ 2 phút

Test bắt buộc: giả lệnh apply khi chưa Paid/chưa lock; sai model/ốp không skip; timeout Paid có refund hết reserve; hết hàng không ra QR; e-stop không tự mở khay; cắt mạng lúc Pending không ra Paid giả; cắt điện không auto-resume; QA fail không Completed; Completed đổi ý không hoàn; STF không PIN không mở khóa; không lưu PAN.

---

## 15. Quyết định đã nói trong hội thoại — phần mềm vs cứng

**Phần mềm / nghiệp vụ:** khóa ở v2. Cursor làm sơ đồ + spec SW từ đây.

**Phần cứng (để sau, không nhét vào UC/ERD chi tiết):**

- Kiến trúc sản phẩm đúng bài dán: gantry XYZ + hút + lăn.
- Lab IoT/open source nếu làm sau: Waveshare **RoArm-M2-S SKU 29152** (ESP32) hoặc gantry + FluidNC (~7–12 triệu VNĐ mức 2).
- Không lấy myCobot làm kiến trúc sản phẩm.
- Dobot Magician Lite `1100000080` / MG400 `DT-MG400-4R075-01` chỉ nếu đổi sang kit đóng, ít custom.

Trong tài liệu SW ghi robot như thiết bị sau interface. Không vẽ 6 khớp servo vào ERD.

**Race chưa viết thành chương v2** (nếu Cursor thêm mục “ngoại lệ” thì thêm decision table, không sửa rule đã chốt): webhook Paid sau Cancel; QR hết hạn trùng Paid; cảm biến khay debounce; lệch tồn vật lý vs on_hand; thứ tự mở khay vs refund; split-brain local Applying / cloud Paid.

---

## 16. Ví dụ khép kín (dùng cho sequence)

Happy: iPhone 15 Pro Max + tem trong suốt, 199.000đ, còn 8 tấm. Tick 4 ý. Paid 21:01. Đặt lệch lần 1 → không khóa. Lần 2 khớp, khóa 21:03. QA lệch 0.8 mm Pass. Lấy máy 21:05. Completed. Tồn 7.

Lỗi: lần 2 còn dày +1.4 mm (ốp). Không dán. Rút máy. Hoàn 199.000đ khi khay trống. Refunded. Không incident máy.

---

## 17. Quy tắc vẽ cho Cursor

- Tiếng Việt trên diagram (đúng đồ án nhóm); mã trạng thái / mã rule giữ English identifier như v2.
- Không copy actor Dealer Staff / EV Brand từ tab mẫu.
- Mỗi transition state ghi actor + điều kiện + mã rule.
- ERD: khóa `ORDER.status` enum đúng 10.1; PAYMENT.purpose; stock reserved.
- Sequence thanh toán: kiosk không tự set Paid.
- Sequence apply: local check BR-LCK-01 trước motion.
- Khi conflict JSON Trang-4 vs v2 → **thắng = v2**.

Hết handoff.
`
