# StickerKiosk — SWD392 SE1927 Group 6

Kiosk tự phục vụ dán **sticker mặt lưng điện thoại**: khách chọn model trong whitelist, trả QR, đặt máy vào khay. Máy chỉ dán khi đơn **Paid** và khay **Locked**.

Trang này render đặc tả đã khóa (MVP v2) và các sơ đồ Mermaid. Bản vẽ cùng nội dung để mở bằng diagrams.net: [`diagrams/kiosk.drawio`](diagrams/kiosk.drawio). File Word gốc: [`DacTaNghiepVu_MVP_v2.docx`](DacTaNghiepVu_MVP_v2.docx).

Đây là seed đồ án (đặc tả, sơ đồ, backlog), không phải ứng dụng kiosk đang chạy.

## Mục lục

- [Phạm vi](#phạm-vi)
- [Nguyên tắc](#nguyên-tắc)
- [Actor](#actor)
- [Cổng được bán](#cổng-được-bán)
- [Luồng chuẩn](#luồng-chuẩn)
- [Trạng thái ORDER](#trạng-thái-order)
- [Thanh toán và hoàn tiền](#thanh-toán-và-hoàn-tiền)
- [Timeout](#timeout)
- [An toàn máy](#an-toàn-máy)
- [Sơ đồ](#sơ-đồ)
- [Backlog GitHub](#backlog-github)

## Phạm vi

Trong MVP: 3–5 model lưng phẳng, sticker cắt sẵn, một cổng VietQR, UI chính là màn kiosk, đo theo template kích thước đã chọn, khay khóa, e-stop, mở khóa bằng PIN nhân viên.

Ngoài MVP: in hoặc cắt tại chỗ, AI nhận model, máy có ốp hoặc lưng cong, app khách điều khiển robot, tiền mặt, thẻ, trả góp, phần mềm tự bồi thường giá điện thoại.

`ORDER.status` là nguồn sự thật nghiệp vụ. Local quyết định an toàn máy. Cloud quyết định tiền. Mất mạng không được ghi Paid khi chưa có xác nhận thanh toán.

## Nguyên tắc

| Mã | Nội dung |
|---|---|
| P1 | An toàn trước doanh thu |
| P2 | Không lấy tiền nếu không bán được dịch vụ. Lỗi hệ thống phải có đường hoàn |
| P3 | `ORDER.status` là trạng thái nghiệp vụ duy nhất |
| P4 | Local = an toàn máy. Cloud = tiền. Robot không nhận lệnh từ điện thoại khách |
| P5 | Khách ẩn danh là mặc định. SĐT tùy chọn, 10 số VN |
| P6 | UI chính là kiosk. Điện thoại chỉ quét QR |

## Actor

| Ký hiệu | Tên | Việc |
|---|---|---|
| CUS | Khách vãng lai | Chọn, tick 4 điều kiện, trả QR, đặt và lấy máy, bấm e-stop |
| SYS | Hệ thống kiosk | Cổng bán, UI, gọi cloud và local |
| LOC | Local controller | Khay, robot, cảm biến. Quyết định có được chạy robot |
| CLD | Cloud | Order, payment, refund, báo cáo |
| STF | Nhân viên hỗ trợ | PIN, sự cố, nạp tem, mở khóa |
| OPS | Quản lý vận hành | Giá, model, ngưỡng, duyệt hoàn tay |
| PAY | Payment provider | QR, Paid hoặc Failed, refund. Không lưu PAN |

## Cổng được bán

Kiosk chỉ `SERVING` khi đủ GR-01 đến GR-08. Thiếu một cổng thì `OUT_OF_SERVICE`, không nhận đơn mới.

| Mã | Điều kiện |
|---|---|
| GR-01 | `mode = SERVING` |
| GR-02 | Heartbeat local dưới 5 giây, cảm biến healthy |
| GR-03 | Robot ở HOME, không job dở, không fault |
| GR-04 | Khay trống, mở, không khóa |
| GR-05 | Còn ít nhất một SKU |
| GR-06 | Payment provider healthy |
| GR-07 | Cloud reachable. Mất cloud quá 2 phút khi chưa có đơn thì OOS |
| GR-08 | Đủ `max_force_n`, `align_tolerance_mm`, `qa_offset_max_mm` |

Catalog: BR-CAT-01 đến BR-CAT-05. Tồn: `available = on_hand - reserved` (BR-STK-01). Reserve khi tạo QR, giữ tối đa 7 phút (BR-STK-02).

## Luồng chuẩn

1. Khách bắt đầu. `ORDER = Created`, `origin = KIOSK`, không bắt buộc khách (BR-CUS-01).
2. Chọn model và pattern còn hàng (BR-CAT-01, BR-CAT-02). Giá khóa lúc xác nhận (BR-CAT-03). Vị trí dán là template SKU (BR-SEL-01).
3. Tick đủ 4 điều kiện. Hệ thống vẫn tự đo ở bước 7 (BR-SEL-02).
4. Reserve tồn và hiện QR 5 phút. Cấm đặt máy trước Paid (BR-PAY-01). Webhook mới là nguồn Paid (BR-PAY-02).
5. Paid thì mở cửa sổ đặt máy 5 phút. Sai số tiền thì từ chối webhook, đơn vẫn PaymentPending (PR-03). Webhook lệch inquiry thì PaymentUnknown (BR-PAY-03).
6. Cảm biến có máy thì `DeviceInserted`.
7. Đo theo template đã chọn, không nhận diện model (BR-DEV-01). Đặt lại tối đa 2 lần (BR-DEV-02). Cấm nút skip (BR-DEV-03).
8. Pass và `tray_locked` thì `Locked`.
9. Apply một lần khi đủ BR-LCK-01. Local từ chối nếu khay chưa khóa (SR-01).
10. QA Pass theo mục 9 bước 10 thì mở khay. `BR-CUS-05` chỉ là thời hạn giữ ảnh, không phải tiêu chí Pass.
11. Khay trống thì `Completed`. Quá 3 phút thì `UnclaimedDevice` (TR-02).

Bốn tick: đúng model đã chọn; đã hoặc sẽ tháo ốp và phụ kiện; lưng khô, không nứt, sẽ lau; hiểu khay khóa và sự cố do nhân viên mở.

## Trạng thái ORDER

Nhánh chính: `Created → PaymentPending → Paid → DeviceInserted → Locked → Applying → QualityChecking → ReadyForPickup → Completed`.

Nhánh kết hoặc lỗi: `PaymentFailed`, `PaymentUnknown`, `DeviceUnsupported`, `DeviceMisaligned`, `ApplicationFailed`, `QualityCheckFailed`, `PowerLost`, `NetworkDegraded`, `EmergencyStopped`, `ManualRecovery`, `RefundPending`, `Refunded`, `Cancelled`, `UnclaimedDevice`.

`NetworkDegraded` có tên ở mục 10.1 nhưng mục 10.2 không có transition của đơn. Mất mạng xử lý bằng SR-21, SR-22, SR-23, GR-07.

`Completed`, `Refunded`, `Cancelled` là trạng thái kết (BR-STA-02). Cấm nhảy cóc, ví dụ Paid sang Applying (BR-STA-01).

`ApplicationFailed` và `QualityCheckFailed` sang `ManualRecovery`. Hoàn 100% ghi ở `REFUND_REQUEST`, không gán `Refunded` từ hai trạng thái đó. Mục 10.2 không có lối `ManualRecovery → Refunded`.

## Thanh toán và hoàn tiền

Một đơn có nhiều `PAYMENT` (PR-01). Chỉ một bản ghi Success cho lần thu (PR-02). Amount QR bằng giá đã khóa (PR-03). Trùng `provider_payment_id` thì bỏ qua (PR-04). Không phụ phí (PR-05). Hoàn đúng giao dịch Success, không tiền mặt (PR-06). Từ chối hoàn phải hiện lý do (PR-07). `RefundPending` quá 24 giờ thì escalate OPS (PR-08).

| Tình huống | Kết quả |
|---|---|
| QR hết hạn hoặc thanh toán fail | Không thu, không hoàn |
| Paid, hủy trước khi khóa khay | Tự động 100% |
| Paid, hết 5 phút không đặt máy | Tự động 100% |
| Sai kích thước, còn ốp, hoặc hết lượt lệch | 100% sau khi khay trống |
| PaymentUnknown rồi xác nhận không có tiền | Không hoàn. Nếu sau đó provider báo có tiền thì hoàn 100% |
| Apply fail, tem chưa chạm hoặc đã chạm | 100% trên `REFUND_REQUEST`, đơn giữ `ManualRecovery` |
| QA fail | 100% trên `REFUND_REQUEST`, đơn giữ `ManualRecovery` |
| Completed, khách đổi ý | Từ chối |
| Hư máy, trầy, tranh chấp, nghi gian lận | OPS duyệt. Phần mềm không bồi thường máy |

## Timeout

Số trong bảng là `[MVP-DEFAULT]`. Đổi số thì phải sửa đặc tả, không sửa ngầm.

| Cửa sổ | Hết hạn |
|---|---|
| Created không chọn xong, 120 giây | Cancelled |
| QR, 300 giây | PaymentFailed, nhả reserve |
| Paid mà chưa có máy, 300 giây | RefundPending |
| Đặt lại khi lệch, 90 giây mỗi lần | Tính 1 lần fail. Hết 2 lần thì hoàn |
| ReadyForPickup, 180 giây | UnclaimedDevice |
| PaymentUnknown, 15 phút | ManualRecovery, không dán |
| Màn không chạm khi chưa Paid, 45 giây | Reset UI. Đã Paid thì không reset (TR-01) |
| Reserve tồn, 7 phút | Nhả reserve |

## An toàn máy

`robot_enable` khi đơn đang Locked, khay locked, e-stop tắt, payment Paid, và SKU còn reserve (BR-LCK-01). Local chặn apply nếu khay chưa khóa, kể cả cloud gửi nhầm (SR-01). E-stop cắt motion ngay, đơn `EmergencyStopped`, khay giữ nguyên khóa (SR-02). Chỉ STF hoặc OPS reset khi vùng trống (SR-03). Lực vượt `max_force_n` thì dừng (SR-04). Cấm apply khi camera hoặc cảm biến timeout (SR-05).

Mất điện: UPS ghi snapshot, `PowerLost`, không tự mở khay, không tự dán tiếp (SR-10, SR-11, SR-12).

## Sơ đồ

Mỗi cạnh state ghi `actor / điều kiện / mã`. Trang mất điện và e-stop là cùng một máy trạng thái, tách riêng cho dễ đọc.

### Use Case

Nguồn: `diagrams/mmd/UseCase.mmd`

```mermaid
flowchart LR
    CUS(("CUS — Khách vãng lai"))
    SYS(("SYS — Hệ thống kiosk"))
    LOC(("LOC — Local controller"))
    CLD(("CLD — Cloud backend"))
    STF(("STF — Nhân viên hỗ trợ"))
    OPS(("OPS — Quản lý vận hành"))
    PAY(("PAY — Payment provider"))
    UC01["UC01 Bắt đầu phiên / chọn dịch vụ | BR-CUS-01 · GR-01..GR-08"]
    UC02["UC02 Chọn model | BR-CAT-01 · BR-SEL-01"]
    UC03["UC03 Chọn pattern / SKU | BR-CAT-02 · BR-CAT-04"]
    UC04["UC04 Xác nhận 4 điều kiện an toàn | BR-SEL-02"]
    UC05["UC05 Thanh toán QR | BR-PAY-01 · BR-PAY-02 · PR-03 · PR-05"]
    UC06["UC06 Hủy đơn chưa Paid | BR-STK-02"]
    UC07["UC07 Hủy đơn đã Paid, chưa khóa khay | PR-06"]
    UC08["UC08 Đặt máy / đặt lại tối đa 2 lần | BR-PAY-01 · BR-DEV-02"]
    UC09["UC09 Lấy máy | mục 9 bước 11"]
    UC10["UC10 Bấm e-stop vật lý | SR-02"]
    UC20["UC20 Reserve tồn + tạo QR | BR-STK-01 · BR-STK-02 · GR-05 · GR-06"]
    UC21["UC21 Nhận webhook / inquiry | BR-PAY-02 · BR-PAY-03 · PR-02 · PR-04"]
    UC22["UC22 Khớp template đã chọn, không AI | BR-DEV-01 · BR-DEV-03"]
    UC23["UC23 Khóa khay | BR-LCK-01 · SR-01"]
    UC24["UC24 Apply sticker đúng 1 lần | BR-APL-01 · BR-APL-02 · SR-04 · SR-05"]
    UC25["UC25 Quality check | mục 9 bước 10. Fail: BR-INC-01"]
    UC26["UC26 Hoàn tiền tự động theo ma trận | PR-06 · PR-07"]
    UC27["UC27 Timeout QR / Paid / pickup | mục 12. Phiên đã Paid: TR-01. Quá 180 giây: TR-02"]
    UC28["UC28 Queue event khi mất mạng | SR-20 · SR-21 · SR-22 · SR-24"]
    UC29["UC29 Kiosk SERVING hoặc OUT_OF_SERVICE | GR-01..GR-08 · SR-23 · BR-OPS-04"]
    UC30["UC30 Đăng nhập PIN / thẻ | BR-ACL-01"]
    UC31["UC31 ManualRecovery và mở khóa | BR-ACL-01 · SR-03 · SR-12"]
    UC32["UC32 Reset e-stop và về HOME | SR-03 · GR-03"]
    UC33["UC33 Nạp tồn đúng slot | BR-STK-06 · BR-OPS-03"]
    UC34["UC34 Checklist mở ca / đóng ca | BR-OPS-01 · BR-OPS-02"]
    UC35["UC35 Đề nghị hoặc duyệt hoàn tay | PR-08 · BR-INC-02"]
    UC36["UC36 Tắt model/SKU, sửa giá, ngưỡng | BR-CAT-05 · GR-08 · BR-OPS-05"]
    UC37["UC37 Xử lý UnclaimedDevice | TR-02 · BR-INC-04"]
    UC38["UC38 Xem INCIDENT và ảnh | BR-INC-01 · BR-CUS-05 · BR-CUS-03"]
    CUS --> UC01
    CUS --> UC02
    CUS --> UC03
    CUS --> UC04
    CUS --> UC05
    CUS --> UC06
    CUS --> UC07
    CUS --> UC08
    CUS --> UC09
    CUS --> UC10
    SYS --> UC20
    SYS --> UC21
    SYS --> UC22
    SYS --> UC23
    SYS --> UC25
    SYS --> UC26
    SYS --> UC27
    SYS --> UC28
    SYS --> UC29
    STF --> UC30
    STF --> UC31
    STF --> UC32
    STF --> UC33
    STF --> UC34
    STF --> UC37
    STF --> UC38
    OPS --> UC35
    OPS --> UC36
    PAY --> UC21
    LOC --> UC22
    LOC --> UC23
    LOC --> UC24
    LOC --> UC25
    LOC --> UC28
    CLD --> UC20
    CLD --> UC21
    CLD --> UC26
    CLD --> UC28
    PAY -->|"tham gia · PR-03"| UC05
    PAY -->|"tham gia · PR-06"| UC26
    LOC -->|"tham gia · SR-02"| UC10
    CLD -->|"tham gia · TR-01"| UC27
    OPS -->|"tham gia · BR-ACL-01"| UC31
    OPS -->|"tham gia · SR-03"| UC32
    STF -->|"đề nghị · OPS duyệt"| UC35
    STF -->|"tham gia · SR-02"| UC10
    SYS -->|"tạo ORDER Created"| UC01
    UC05 -->|"«include» · BR-STK-01"| UC20
    UC05 -->|"«include» · BR-PAY-02"| UC21
    UC08 -->|"«include» · BR-DEV-01"| UC22
    UC23 -->|"«include» đo trước khi khóa · BR-DEV-01"| UC22
    UC24 -->|"«include» khay locked trước motion · BR-LCK-01 · SR-01"| UC23
    UC24 -->|"«include» QA sau apply_done · BR-APL-02"| UC25
    UC07 -->|"«include» · PR-06"| UC26
    UC26 -->|"«extend» khi timeout đã thu tiền · PR-06"| UC27
    UC10 -->|"«extend» ngắt apply · SR-02"| UC24
    UC32 -->|"«include» reset sau e-stop · SR-03"| UC10
    UC28 -->|"«extend» mất mạng lúc Pending · SR-21"| UC21
    UC37 -->|"«include» · BR-INC-01"| UC38
    UC34 -->|"cổng SERVING · BR-OPS-01"| UC29
    UC35 -->|"«extend» hoàn tay · PR-08"| UC26
    UC33 -->|"cùng ca · BR-STK-06 · BR-OPS-01"| UC34
    NGOAI["Ngoài hệ thống: TTTM, bảo hiểm, vendor robot. Không vẽ đăng ký tài khoản khách, AI nhận model, app điều khiển robot, BOM hay khớp tay máy."]
    TICK["UC04 — 4 ý bắt buộc: đúng model đã chọn; đã/sẽ tháo ốp và phụ kiện; lưng khô không nứt và sẽ lau; hiểu khay khóa, sự cố do nhân viên. BR-SEL-02."]
```

### Activity — luồng mục 9

Nguồn: `diagrams/mmd/Activity.mmd`

```mermaid
flowchart TD
    A0["Bước 0 — Kiosk rảnh, chưa có ORDER"]
    D0["Đủ GR-01 đến GR-08?"]
    OOS["OUT_OF_SERVICE — không nhận đơn mới"]
    A1["Bước 1 — CUS bắt đầu. ORDER = Created, origin = KIOSK, customer_id null"]
    D120["Chọn xong trong 120 giây?"]
    CAN["ORDER = Cancelled"]
    A2["Bước 2 — Hiện model và pattern. Vị trí dán = template SKU, không chọn tự do"]
    DSTOCK["Còn SKU active, stock_available > 0?"]
    HIDE["Ẩn SKU, không tạo QR"]
    A3["Bước 3 — Tick đủ 4 điều kiện. Thiếu thì khóa nút Thanh toán"]
    A4["Bước 4 — Kiểm lại GR và tồn. PAYMENT Pending, reserve, QR 300 giây. Không mở khay"]
    DPAY["Kết quả thanh toán"]
    PAID["ORDER = Paid, started_insert_at = now. Cửa sổ đặt máy 300 giây"]
    PFAIL["ORDER = PaymentFailed, nhả reserve, không giữ tiền"]
    PUNK["ORDER = PaymentUnknown. Không dán. Giữ reserve tối đa 15 phút"]
    DREC["Đối soát webhook và inquiry"]
    MAN["ORDER = ManualRecovery. Chỉ STF hoặc OPS, có PIN"]
    DINS["Có máy trong khay trước 300 giây, hay khách hủy?"]
    INS["ORDER = DeviceInserted. Cảm biến có một máy và đã Paid"]
    REFP["ORDER = RefundPending. Hoàn 100%"]
    A7["Bước 7 — Đo so với template của phone_model_id. Không nhận diện model"]
    DDEV["Kết quả đo"]
    MIS["ORDER = DeviceMisaligned"]
    UNS["ORDER = DeviceUnsupported. Cấm skip"]
    DTRY["Còn lượt đặt lại? Chưa tới lần 3, mỗi lần 90 giây"]
    LOCK["Bước 8 — ORDER = Locked chỉ khi cảm biến tray_locked"]
    DLCK["BR-LCK-01 đủ để apply?"]
    NOAPP["Không gửi apply"]
    APP["Bước 9 — ORDER = Applying. Đúng 1 lần"]
    DAPP["Kết quả apply"]
    QA["Bước 10 — ORDER = QualityChecking"]
    APPF["ORDER = ApplicationFailed. Giữ khóa. INCIDENT HIGH. Không retry"]
    ESTOP["ORDER = EmergencyStopped. Khay giữ nguyên khóa"]
    DQA["QA đạt?"]
    QAF["ORDER = QualityCheckFailed. Giữ khóa. Không tự mở"]
    PICK["Bước 11 — Mở khay. ORDER = ReadyForPickup, 180 giây"]
    DPICK["Khay trống trong 180 giây?"]
    DONE["ORDER = Completed"]
    UNCL["ORDER = UnclaimedDevice. Không nhận đơn mới đến khi khay trống"]
    STFCHK["STF xác nhận máy còn hay không, chụp ảnh, đóng phiên. Không sang status mới ngoài mục 10.2"]
    PWR["ORDER = PowerLost. Không tự mở khay. Không tự resume"]
    REFD["ORDER = Refunded"]
    REJECT["Từ chối hoàn. Giữ Completed. Hiện lý do"]
    END["Kết phiên. BR-STA-02: Completed, Refunded, Cancelled không chạy robot lại"]
    A0 -->|"Kiểm cổng bán · GR-01 GR-02 GR-03 GR-04 GR-05 GR-06 GR-07 GR-08"| D0
    D0 -->|"Thiếu một cổng · GR-01..GR-08. Hết tem BR-OPS-04. Mất cloud quá 2 phút SR-23. Thiếu checklist BR-OPS-01"| OOS
    D0 -->|"Đủ cổng · CUS · BR-CUS-01"| A1
    A1 -->|"Mục 12 [MVP-DEFAULT] 120 giây. 45 giây không chạm thì reset UI, chưa Paid"| D120
    D120 -->|"Khách rời, quá 120 giây, hoặc hết SERVING · GR-01"| CAN
    D120 -->|"Còn trong hạn · BR-CAT-01 BR-CAT-02 BR-SEL-01 BR-CAT-04"| A2
    A2 -->|"Giá sẽ khóa lúc xác nhận · BR-CAT-03"| DSTOCK
    DSTOCK -->|"available = 0 hoặc SKU inactive · BR-CAT-02 BR-STK-05 BR-CAT-05"| HIDE
    DSTOCK -->|"Còn hàng · BR-SEL-02. Tick không thay được bước đo"| A3
    A3 -->|"Đủ 4 tick · SYS kiểm lại GR và stock_available · BR-STK-01 BR-PAY-01 PR-03 PR-05"| A4
    A4 -->|"QR hiện, khay không mở · BR-PAY-01 BR-PAY-02"| DPAY
    DPAY -->|"PAY webhook success, amount khớp, đúng một Success · BR-PAY-02 PR-02 PR-03 PR-04"| PAID
    DPAY -->|"Provider fail hoặc QR hết 300 giây · BR-STK-02"| PFAIL
    DPAY -->|"Webhook lệch inquiry · BR-PAY-03"| PUNK
    DPAY -->|"CUS hủy khi chưa Paid, nhả reserve · BR-STK-02"| CAN
    PFAIL -->|"Không thu nên không hoàn · BR-STK-02"| CAN
    PUNK -->|"Không dán, không đoán Paid · BR-PAY-03 SR-21"| DREC
    DREC -->|"Đối soát trong 15 phút, có tiền · BR-PAY-03"| PAID
    DREC -->|"Đối soát không có tiền · BR-PAY-03"| PFAIL
    DREC -->|"Quá 15 phút vẫn unknown, không dán · BR-PAY-03"| MAN
    PAID -->|"Cửa sổ đặt máy 300 giây. Đã Paid thì không reset để phục vụ khách khác · TR-01"| DINS
    DINS -->|"Hết 300 giây không đặt, hoặc CUS hủy trước khóa · PR-06"| REFP
    DINS -->|"Cảm biến có một máy. Chưa Paid thì không gán DeviceInserted · BR-PAY-01"| INS
    INS -->|"Đo template của model đã chọn · BR-DEV-01"| A7
    A7 -->|"So template đã chọn. Cấm nút skip · BR-DEV-03"| DDEV
    DDEV -->|"Khay trống hoặc còn tay người: không đổi status, không khóa · BR-DEV-01"| A7
    DDEV -->|"Nhiều vật, góc yaw trên 3 độ, hoặc lệch tâm trên 2 mm · BR-DEV-01"| MIS
    DDEV -->|"WxH lệch quá ±1.5 mm hoặc dày hơn template + 1.0 mm · BR-DEV-01 BR-DEV-03"| UNS
    DDEV -->|"Khớp template và tray_locked · BR-DEV-01"| LOCK
    MIS -->|"Mỗi lần lệch tính 1 fail, hạn 90 giây · BR-DEV-02"| DTRY
    DTRY -->|"Còn lượt, chưa tới lần 3. Về cửa sổ Paid, không apply · BR-DEV-02"| PAID
    DTRY -->|"Lần 3 fail, khay không khóa hoặc đã mở, cảm biến trống · BR-DEV-02"| REFP
    UNS -->|"Khay trống sau khi mở để rút · PR-06"| REFP
    LOCK -->|"robot_enable cần Locked, tray_locked, e_stop false, Paid, sku reserved · BR-LCK-01 SR-01"| DLCK
    DLCK -->|"Thiếu một điều kiện, kể cả cloud gửi nhầm · SR-01 SR-05"| NOAPP
    DLCK -->|"Local chấp nhận. Tối đa 1 apply · BR-APL-02"| APP
    APP -->|"Lực không vượt max_force_n · SR-04"| DAPP
    DAPP -->|"apply_done, không fault. on_hand trừ 1, nhả reserve · BR-STK-03 BR-APL-02"| QA
    DAPP -->|"Lực, mất bước, mở khay, mất sensor. Giữ khóa · BR-APL-01 SR-04 SR-05 BR-INC-01"| APPF
    DAPP -->|"E-stop. Một status EmergencyStopped, vẫn INCIDENT · SR-02 BR-APL-01 BR-INC-01"| ESTOP
    APP -->|"Mất điện khi đang có máy · SR-10 SR-11"| PWR
    LOCK -->|"Mất điện · SR-10 SR-11"| PWR
    LOCK -->|"E-stop, khay giữ khóa · SR-02"| ESTOP
    QA -->|"Cạnh tối đa 1.5 mm, xoay tối đa 1.5 độ, không đè mask, không bọt trên 3 mm, không hở góc · mục 9 bước 10"| DQA
    DQA -->|"QA Pass. Cạnh tối đa 1.5 mm, xoay tối đa 1.5 độ · mục 9 bước 10"| PICK
    DQA -->|"QA Fail · BR-INC-01"| QAF
    QAF -->|"Chỉ STF/OPS · BR-ACL-01 BR-INC-03"| MAN
    APPF -->|"Chỉ STF/OPS. Picker taken vẫn trừ on_hand · BR-ACL-01 BR-STK-04"| MAN
    APPF -->|"E-stop, khay giữ khóa · SR-02"| ESTOP
    QAF -->|"E-stop, khay giữ khóa · SR-02"| ESTOP
    PICK -->|"Cửa sổ lấy máy 180 giây · mục 12"| DPICK
    DPICK -->|"Khay trống · mục 9 bước 11"| DONE
    DPICK -->|"Quá 180 giây · TR-02"| UNCL
    PICK -->|"Mất điện · SR-11"| PWR
    PWR -->|"Có điện không tự resume. STF xác nhận máy · SR-12 BR-ACL-01"| MAN
    ESTOP -->|"Reset chỉ khi vùng trống, không có tay · SR-03 BR-ACL-01"| MAN
    REFP -->|"Provider refund success, đúng giao dịch, không tiền mặt · PR-06"| REFD
    REFP -->|"Refund fail 3 lần hoặc quá 24 giờ · PR-08"| MAN
    DONE -->|"Khách đổi ý sau QA Pass · PR-07 BR-STA-02"| REJECT
    DONE -->|"Kết · BR-STA-02"| END
    REFD -->|"Kết · BR-STA-02"| END
    CAN -->|"Kết · BR-STA-02"| END
    UNCL -->|"STF xác nhận, không đổi status ngoài mục 10.2 · TR-02 BR-INC-04"| STFCHK
    NOTE_108["BR-STA-01: cấm nhảy cóc, ví dụ Paid sang Applying hoặc Created sang Locked. Activity đi đúng cổng mục 9."]
    NOTE_109["P4: local quyết định an toàn máy, cloud quyết định tiền. Mất mạng lúc Pending không bịa Paid · SR-20 SR-21."]
    NOTE_110["ApplicationFailed và QualityCheckFailed sang ManualRecovery theo mục 10.2. Hoàn 100% ghi ở REFUND_REQUEST theo mục 11, không thêm status ngoài bảng 10.2."]
    NOTE_111["4 tick: đúng model đã chọn; tháo ốp và phụ kiện; lưng khô không nứt sẽ lau; hiểu khay khóa và sự cố do nhân viên."]
```

### State ORDER — nhánh mục 10.2

Nguồn: `diagrams/mmd/State-ORDER.mmd`

```mermaid
stateDiagram-v2
    direction TB
    [*] --> Created: CUS / Kiosk đang SERVING, bắt đầu phiên ẩn danh / GR-01 BR-CUS-01
    Created --> PaymentPending: SYS / SKU hợp lệ, đủ 4 tick, còn hàng, tạo QR được / BR-CAT-01 BR-CAT-02 BR-CAT-03 BR-STK-01 BR-SEL-02
    Created --> Cancelled: SYS / Khách rời, quá 120 giây không chọn, hoặc hết SERVING / GR-01
    PaymentPending --> Paid: PAY / Webhook success, amount khớp, đúng order, chưa có Success khác / BR-PAY-02 PR-02 PR-03 PR-04
    PaymentPending --> PaymentFailed: PAY / Provider fail hoặc QR hết 300 giây / BR-STK-02
    PaymentPending --> PaymentUnknown: CLD / Webhook lệch inquiry, không dán / BR-PAY-03
    PaymentPending --> Cancelled: CUS / Hủy khi chưa Paid, nhả reserve / BR-STK-02
    PaymentUnknown --> Paid: CLD / Đối soát trong 15 phút, xác nhận có tiền / BR-PAY-03
    PaymentUnknown --> PaymentFailed: CLD / Đối soát không có tiền / BR-PAY-03
    PaymentUnknown --> ManualRecovery: SYS / Quá 15 phút vẫn unknown, không dán / BR-PAY-03
    PaymentFailed --> Cancelled: SYS / Nhả reserve, không giữ tiền, không phát sinh hoàn / BR-STK-02
    Paid --> DeviceInserted: LOC / Cảm biến có máy và payment đã Paid / BR-PAY-01
    Paid --> RefundPending: SYS / Hết 300 giây không đặt máy, hoặc khách hủy trước khóa / PR-06
    DeviceInserted --> Locked: LOC / Template Pass và tray_locked / BR-DEV-01
    DeviceInserted --> DeviceMisaligned: LOC / Nhiều vật, góc lệch quá 3 độ, hoặc tâm lệch quá 2 mm / BR-DEV-01
    DeviceInserted --> DeviceUnsupported: LOC / Kích thước hoặc độ dày không khớp, cấm skip / BR-DEV-01 BR-DEV-03
    DeviceMisaligned --> Paid: SYS / Còn lượt đặt lại, chưa tới lần 3, không apply / BR-DEV-02
    DeviceMisaligned --> RefundPending: SYS / Lần 3 fail, khay không khóa hoặc đã mở, rồi khay trống / BR-DEV-02
    DeviceUnsupported --> RefundPending: SYS / Khay không khóa hoặc đã mở để rút, cảm biến trống / PR-06
    Locked --> Applying: LOC / Đủ robot_enable và local không từ chối / BR-LCK-01 SR-01 BR-APL-02
    Applying --> QualityChecking: LOC / apply_done, không fault / BR-APL-02 BR-STK-03
    Applying --> ApplicationFailed: LOC / Lực, mất bước, mở khay hoặc mất sensor. Giữ khóa, không retry / BR-APL-01 SR-04 SR-05 BR-INC-01
    Applying --> EmergencyStopped: CUS STF OPS / E-stop cắt motion. Một status, khay giữ khóa, có INCIDENT / SR-02 BR-APL-01 BR-INC-01
    QualityChecking --> ReadyForPickup: SYS / QA Pass. Cạnh tối đa 1.5 mm, xoay tối đa 1.5 độ, không đè mask, không bọt trên 3 mm, không hở góc / mục 9 bước 10
    QualityChecking --> QualityCheckFailed: SYS / QA Fail, giữ khóa, không tự mở / BR-INC-01
    ReadyForPickup --> Completed: LOC / Khay trống sau khi mở / mục 9 bước 11
    ReadyForPickup --> UnclaimedDevice: SYS / Quá 180 giây chưa lấy, không nhận đơn mới / TR-02
    ApplicationFailed --> ManualRecovery: STF / Chỉ STF hoặc OPS, ghi actor và lý do / BR-ACL-01 BR-INC-03
    QualityCheckFailed --> ManualRecovery: STF / Chỉ STF hoặc OPS / BR-ACL-01 BR-INC-03
    PowerLost --> ManualRecovery: STF / Có điện thì không tự resume / SR-12 BR-ACL-01
    EmergencyStopped --> ManualRecovery: STF / Vùng làm việc trống và không có tay / SR-03 BR-ACL-01
    RefundPending --> Refunded: PAY / Refund success đúng giao dịch đã Success / PR-06
    RefundPending --> ManualRecovery: SYS / Provider fail sau 3 lần hoặc quá 24 giờ / PR-08
    Completed --> [*]: SYS / Trạng thái kết. OPS chỉ bút toán, không chạy robot / BR-STA-02
    Refunded --> [*]: SYS / Trạng thái kết / BR-STA-02
    Cancelled --> [*]: SYS / Trạng thái kết / BR-STA-02
    Applying --> PowerLost: LOC / Mất điện khi đang có máy trong khay. UPS ghi snapshot, không tự mở / SR-10 SR-11
```

### State ORDER — mất điện và e-stop

Nguồn: `diagrams/mmd/State-Ngat.mmd`

```mermaid
stateDiagram-v2
    direction TB
    %% Cùng máy trạng thái ORDER. Trang này chỉ ngắt điện và e-stop hàng loạt.
    DeviceInserted --> PowerLost: LOC / Mất điện khi đang có máy trong khay. UPS ghi snapshot, không tự mở / SR-10 SR-11
    DeviceMisaligned --> PowerLost: LOC / Mất điện khi đang có máy trong khay. UPS ghi snapshot, không tự mở / SR-10 SR-11
    DeviceUnsupported --> PowerLost: LOC / Mất điện khi đang có máy trong khay. UPS ghi snapshot, không tự mở / SR-10 SR-11
    Locked --> PowerLost: LOC / Mất điện khi đang có máy trong khay. UPS ghi snapshot, không tự mở / SR-10 SR-11
    QualityChecking --> PowerLost: LOC / Mất điện khi đang có máy trong khay. UPS ghi snapshot, không tự mở / SR-10 SR-11
    ReadyForPickup --> PowerLost: LOC / Mất điện khi đang có máy trong khay. UPS ghi snapshot, không tự mở / SR-10 SR-11
    ApplicationFailed --> PowerLost: LOC / Mất điện khi đang có máy trong khay. UPS ghi snapshot, không tự mở / SR-10 SR-11
    QualityCheckFailed --> PowerLost: LOC / Mất điện khi đang có máy trong khay. UPS ghi snapshot, không tự mở / SR-10 SR-11
    UnclaimedDevice --> PowerLost: LOC / Mất điện khi đang có máy trong khay. UPS ghi snapshot, không tự mở / SR-10 SR-11
    EmergencyStopped --> PowerLost: LOC / Mất điện khi đang có máy trong khay. UPS ghi snapshot, không tự mở / SR-10 SR-11
    ManualRecovery --> PowerLost: LOC / Mất điện khi đang có máy trong khay. UPS ghi snapshot, không tự mở / SR-10 SR-11
    Created --> EmergencyStopped: CUS STF OPS / E-stop cắt motion, khay giữ nguyên khóa / SR-02
    PaymentPending --> EmergencyStopped: CUS STF OPS / E-stop cắt motion, khay giữ nguyên khóa / SR-02
    Paid --> EmergencyStopped: CUS STF OPS / E-stop cắt motion, khay giữ nguyên khóa / SR-02
    DeviceInserted --> EmergencyStopped: CUS STF OPS / E-stop cắt motion, khay giữ nguyên khóa / SR-02
    DeviceMisaligned --> EmergencyStopped: CUS STF OPS / E-stop cắt motion, khay giữ nguyên khóa / SR-02
    DeviceUnsupported --> EmergencyStopped: CUS STF OPS / E-stop cắt motion, khay giữ nguyên khóa / SR-02
    Locked --> EmergencyStopped: CUS STF OPS / E-stop cắt motion, khay giữ nguyên khóa / SR-02
    QualityChecking --> EmergencyStopped: CUS STF OPS / E-stop cắt motion, khay giữ nguyên khóa / SR-02
    ReadyForPickup --> EmergencyStopped: CUS STF OPS / E-stop cắt motion, khay giữ nguyên khóa / SR-02
    UnclaimedDevice --> EmergencyStopped: CUS STF OPS / E-stop cắt motion, khay giữ nguyên khóa / SR-02
    ApplicationFailed --> EmergencyStopped: CUS STF OPS / E-stop cắt motion, khay giữ nguyên khóa / SR-02
    QualityCheckFailed --> EmergencyStopped: CUS STF OPS / E-stop cắt motion, khay giữ nguyên khóa / SR-02
```

### Sequence thanh toán

Nguồn: `diagrams/mmd/Seq-ThanhToan.mmd`

```mermaid
flowchart TD
    S1["CUS tick đủ 4 điều kiện trên kiosk"]
    S2["SYS kiểm lại GR-01..GR-08, model, SKU, stock_available"]
    S3["CLD giữ ORDER PaymentPending, price_snapshot, customer có thể null"]
    S4["CLD reserve: available = on_hand trừ reserved. Giữ tối đa 7 phút"]
    S5["PAY tạo QR. Amount bằng price_snapshot. Hết hạn 300 giây. Không phụ phí"]
    S6["SYS hiện QR. Không mở khay. Không có nút Tôi đã trả. Điện thoại không điều khiển robot"]
    S7["PAY gửi webhook tới CLD"]
    S8["CLD đối amount, order_id, provider_payment_id"]
    S9["Sai amount hoặc sai order: từ chối webhook. ORDER vẫn PaymentPending"]
    S9B["Webhook khác inquiry: PaymentUnknown, không dán, giữ reserve"]
    S9C["Đối soát trong 15 phút xác nhận có tiền: ORDER = Paid"]
    S10["Trùng provider_payment_id: bỏ qua, không tạo Success thứ hai"]
    S11["Khớp: một PAYMENT purpose CHARGE status Success. ORDER = Paid"]
    S12["SYS hướng dẫn tháo ốp, lau, đặt máy. Không reset phiên"]
    S13["Provider fail hoặc QR hết hạn: PaymentFailed rồi Cancelled, nhả reserve, không hoàn"]
    S14["CUS hủy lúc Pending: Cancelled, hủy QR nếu provider hỗ trợ, nhả reserve"]
    S15["Mất mạng lúc Pending: không đoán Paid. Xếp event, inquiry khi có mạng"]
    S16["Vẫn unknown sau 15 phút: ManualRecovery, không dán"]
    S1 -->|"BR-SEL-02"| S2
    S2 -->|"GR-01..GR-08 · BR-CAT-01 · BR-CAT-02 · BR-CAT-03 · BR-CUS-01"| S3
    S3 -->|"BR-STK-01 · BR-STK-02"| S4
    S4 -->|"PR-03 · PR-05"| S5
    S5 -->|"BR-PAY-01 · BR-PAY-02"| S6
    S6 -->|"CUS quét QR · P6"| S7
    S7 -->|"BR-PAY-02 · BR-CUS-04"| S8
    S8 -->|"Từ chối webhook · PR-03"| S9
    S8 -->|"Webhook lệch inquiry · BR-PAY-03"| S9B
    S9B -->|"Đối soát có tiền · BR-PAY-03"| S9C
    S9B -->|"Quá 15 phút vẫn unknown · BR-PAY-03"| S16
    S8 -->|"Idempotent · PR-04 · PR-02"| S10
    S8 -->|"Webhook là nguồn Paid · BR-PAY-02 · PR-02"| S11
    S11 -->|"TR-01"| S12
    S6 -->|"Hết 300 giây hoặc fail · BR-STK-02"| S13
    S6 -->|"CUS hủy chưa Paid · BR-STK-02"| S14
    S6 -->|"Đứt mạng · SR-20 · SR-21 · SR-24"| S15
    S15 -->|"Có mạng thì inquiry, không đoán Paid · SR-21 SR-24"| S8
    S15 -->|"Hết 15 phút vẫn unknown · BR-PAY-03"| S16
    NOTE_38["Ví dụ mục 20: iPhone 15 Pro Max, tem trong suốt, 199000, còn 8 tấm, Paid rồi mới đặt. Không phải rule mới."]
    NOTE_39["Kiosk không tự gán Paid. UI polling chỉ để hiển thị · BR-PAY-02."]
```

### Sequence interlock

Nguồn: `diagrams/mmd/Seq-Interlock.mmd`

```mermaid
flowchart TD
    I0["Sau Paid, cảm biến có một máy thì ORDER = DeviceInserted. Chưa Paid thì không"]
    I1["LOC inspect_device theo template của model đã chọn"]
    I2["LOC trả inspect_result. Chỉ khớp hoặc không khớp, không suy ra tên máy"]
    I3["Khay trống: không đổi ORDER.status, yêu cầu đặt lại"]
    I4["Còn tay: không lock_tray. Quá 20 giây vẫn có tay: vẫn không khóa"]
    I5["Sai kích thước hoặc độ dày: DeviceUnsupported. Không có nút skip"]
    I6["Lệch góc hoặc tâm: DeviceMisaligned. Còn lượt thì về Paid, không apply"]
    I7["Pass: LOC lock_tray. ORDER = Locked chỉ khi cảm biến locked"]
    I8["CLD gửi pick_sku(slot) và apply(template_id). Không gửi góc khớp"]
    I9["LOC kiểm trước khi chuyển động. Thiếu điều kiện thì từ chối lệnh"]
    I10["Apply đúng một lần, lực không quá max_force_n"]
    I11["Fault: safe_halt, ApplicationFailed, giữ khóa, INCIDENT HIGH, không retry"]
    I12["apply_failed mà picker_taken: vẫn trừ on_hand, không dùng lại tấm"]
    I13["apply_success: on_hand trừ 1, nhả reserve, sang QualityChecking, qa_capture"]
    I14["QA Pass: unlock_tray, ReadyForPickup 180 giây"]
    I15["QA Fail: không unlock, QualityCheckFailed, INCIDENT"]
    I0 -->|"BR-PAY-01"| I1
    I1 -->|"BR-DEV-01"| I2
    I2 -->|"Bước 7 khay trống"| I3
    I2 -->|"Bước 7 tay người"| I4
    I2 -->|"BR-DEV-01 · BR-DEV-03"| I5
    I2 -->|"BR-DEV-01 · BR-DEV-02"| I6
    I2 -->|"Pass và tray_locked · BR-DEV-01"| I7
    I7 -->|"Lệnh nghiệp vụ, không phải quỹ đạo khớp"| I8
    I8 -->|"BR-LCK-01 · SR-01 · SR-05"| I9
    I9 -->|"Local cho phép · BR-APL-02 · SR-04"| I10
    I10 -->|"BR-APL-01 · SR-04 · SR-05 · BR-INC-01"| I11
    I11 -->|"BR-STK-04"| I12
    I10 -->|"BR-STK-03"| I13
    I13 -->|"QA Pass mục 9 bước 10"| I14
    I13 -->|"BR-INC-01"| I15
    NOTE_32["robot_enable = ORDER Locked AND tray_locked AND e_stop false AND payment Paid AND sku reserved · BR-LCK-01."]
    NOTE_33["SR-01: firmware local chặn apply khi khay chưa locked, kể cả cloud gửi nhầm."]
```

### Sequence hoàn tiền

Nguồn: `diagrams/mmd/Seq-HoanTien.mmd`

```mermaid
flowchart TD
    R0["Có hay chưa có PAYMENT Success?"]
    R1["QR hết hạn hoặc thanh toán fail: không thu, không tạo hoàn"]
    R2["Paid, hủy trước khi khóa khay: tự động 100%"]
    R3["Paid, hết 300 giây không đặt máy: tự động 100%"]
    R4["DeviceUnsupported hoặc hết lượt lệch: tự động 100% sau khi khay trống"]
    R5["PaymentUnknown rồi xác nhận không có tiền: không hoàn, Cancelled"]
    R5B["Nếu sau đó provider báo đã có tiền: hoàn 100%"]
    R6["ApplicationFailed, tem chưa chạm: tự động 100%, STF mở khóa"]
    R7["ApplicationFailed, tem đã chạm: tự động 100%, INCIDENT, không tự gỡ tem"]
    R8["QA fail, khách không nhận: tự động 100% sau khi STF xác nhận"]
    R9["QA fail, khách vẫn nhận: tự động 100%. MVP không bán hàng lỗi"]
    R10["Completed, QA pass, khách đổi ý: từ chối, hiện lý do"]
    R11["Nghi hư máy, trầy, tranh chấp: OPS duyệt. Phần mềm không bồi thường máy"]
    R12["Nghi gian lận: OPS khóa hoàn tự động, giữ ảnh"]
    R13["CLD tạo REFUND_REQUEST và PAYMENT purpose REFUND. ORDER = RefundPending rồi Refunded khi provider success"]
    R14["Provider success: ORDER = Refunded. Chỉ từ RefundPending"]
    R6M["ORDER giữ ManualRecovery. REFUND_REQUEST ghi hoàn 100%. Không gán Refunded"]
    R15["Fail 3 lần hoặc RefundPending quá 24 giờ: ManualRecovery, báo OPS, vẫn trả máy theo an toàn"]
    R0 -->|"Chưa Success · BR-STK-02"| R1
    R0 -->|"PR-06 · mục 11"| R2
    R0 -->|"Hết 300 giây · PR-06"| R3
    R0 -->|"Khay trống · BR-DEV-02 · PR-06"| R4
    R0 -->|"BR-PAY-03"| R5
    R5 -->|"BR-PAY-03 · PR-06"| R5B
    R0 -->|"BR-APL-01 · PR-06 · BR-ACL-01"| R6
    R0 -->|"BR-APL-01 · BR-INC-01 · BR-INC-02 · PR-06"| R7
    R0 -->|"BR-INC-03 · PR-06"| R8
    R0 -->|"PR-06 · BR-INC-03"| R9
    R0 -->|"PR-07 · BR-STA-02"| R10
    R0 -->|"BR-INC-02"| R11
    R0 -->|"BR-INC-02 · BR-CUS-03"| R12
    R2 -->|"AUTO · PR-06 · BR-CUS-04"| R13
    R3 -->|"AUTO · PR-06"| R13
    R4 -->|"AUTO sau khay trống · PR-06"| R13
    R5B -->|"AUTO · PR-06"| R13
    R6 -->|"Mục 10.2 giữ ManualRecovery · PR-06 · BR-ACL-01"| R6M
    R7 -->|"Mục 10.2 giữ ManualRecovery · PR-06 · BR-INC-01"| R6M
    R8 -->|"Mục 10.2 giữ ManualRecovery · PR-06 · BR-INC-03"| R6M
    R9 -->|"Mục 10.2 giữ ManualRecovery · PR-06"| R6M
    R11 -->|"OPS duyệt. Không tự Refunded · BR-INC-02 · PR-08"| R6M
    R13 -->|"PR-06"| R14
    R13 -->|"PR-08"| R15
    NOTE_43["PR-07: mọi từ chối hoàn phải hiện lý do trên màn hình và trên phiếu sự cố."]
    NOTE_44["Mục 10.2 không có mũi tên ApplicationFailed sang RefundPending. Status an toàn là ManualRecovery; tiền đi theo REFUND_REQUEST."]
    NOTE_45["Không hoàn tiền mặt tại kiosk · PR-06. Không lưu PAN · BR-CUS-04."]
```

### Sequence e-stop và mất điện

Nguồn: `diagrams/mmd/Seq-EStop.mmd`

```mermaid
flowchart TD
    E1["CUS, STF hoặc OPS bấm e-stop vật lý"]
    E2["LOC cắt chuyển động ngay: safe_halt và estop_ack"]
    E3["Khay giữ đúng trạng thái khóa lúc nhấn. Không tự unlock"]
    E4["ORDER = EmergencyStopped. Kiosk.mode = EMERGENCY_STOP"]
    E5["Nếu đang Applying: không gán thêm ApplicationFailed. Mở INCIDENT HIGH"]
    E6["LOC từ chối apply mới"]
    E7["Chỉ STF hoặc OPS đã đăng nhập PIN được reset, khi vùng trống và không có tay"]
    E8["LOC về HOME. ORDER = ManualRecovery. Không tự dán tiếp"]
    P1["Nhánh mất điện, khác e-stop: UPS snapshot order_id rồi an toàn hóa"]
    P2["ORDER = PowerLost. Không tự mở khay"]
    P3["Có điện: không tự resume. STF ManualRecovery. Chưa dán thì hoàn 100%"]
    E1 -->|"SR-02"| E2
    E2 -->|"SR-02"| E3
    E3 -->|"SR-02"| E4
    E4 -->|"P3 một status · BR-APL-01 · BR-INC-01"| E5
    E4 -->|"SR-01 · BR-LCK-01"| E6
    E6 -->|"SR-03 · BR-ACL-01"| E7
    E7 -->|"GR-03 · SR-03 · BR-ACL-01"| E8
    P1 -->|"SR-10 · SR-11"| P2
    P2 -->|"SR-12 · PR-06 · SR-13"| P3
    NOTE_21["SR-13: mục tiêu có thể mở khóa theo quy trình trong 2 phút sau khi có điện, không tính thời gian nhân viên đi tới."]
    NOTE_22["Không thiết kế UPS, tay máy hay sơ đồ điện. Sequence chỉ là contract an toàn phần mềm."]
```

### ERD Trang-4

Nguồn: `diagrams/mmd/Trang-4.mmd`

```mermaid
erDiagram
    PHONE_MODEL {
        string phone_model_id PK
        string name
        string is_supported "BR-CAT-01"
        string width_mm
        string height_mm
        string thickness_mm
        string camera_mask
        string align_template_uri "BR-DEV-01"
        string qa_offset_max_mm "GR-08"
    }
    STICKER_PATTERN {
        string sticker_pattern_id PK
        string name
        string preview_uri
    }
    STICKER_ITEM {
        string sticker_item_id PK
        string sticker_pattern_id FK
        string phone_model_id FK
        string price "BR-CAT-03"
        string estimated_seconds "BR-CAT-04"
        string active "BR-CAT-05"
        string slot_code "mục 18"
    }
    KIOSK {
        string kiosk_id PK
        string mode "GR-01 SERVING OUT_OF_SERVICE MAINTENANCE EMERGENCY_STOP"
        string max_force_n "GR-08 SR-04"
        string align_tolerance_mm "GR-08"
        string qa_offset_max_mm "GR-08"
        string force_maintenance "BR-OPS-05"
        string last_heartbeat_at "GR-02"
    }
    KIOSK_STOCK {
        string kiosk_stock_id PK
        string kiosk_id FK
        string sticker_item_id FK
        string stock_natural_key UK "unique kiosk_id và sticker_item_id"
        string on_hand
        string reserved "BR-STK-01"
        string reorder_threshold "BR-STK-05"
        string slot_code "BR-OPS-03"
    }
    CUSTOMER {
        string customer_id PK
        string phone_vn "nullable BR-CUS-02"
    }
    KIOSK_SESSION {
        string session_id PK
        string kiosk_id FK
        string anonymous "BR-CUS-01"
        string started_at
        string last_touch_at "mục 12"
    }
    ORDER {
        string order_id PK
        string status "enum mục 10.1 BR-STA-01"
        string kiosk_id FK
        string phone_model_id FK
        string sticker_item_id FK
        string customer_id FK "nullable BR-CUS-01"
        string session_id FK
        string price_snapshot "BR-CAT-03"
        string attempt_align_count "BR-DEV-02"
        string phone_optional "BR-CUS-02"
        string started_insert_at
        string origin "KIOSK"
    }
    PAYMENT {
        string payment_id PK
        string order_id FK "PR-01"
        string provider_payment_id UK "PR-04"
        string provider
        string amount "PR-03 PR-05"
        string status
        string purpose "CHARGE hoặc REFUND"
        string paid_at "BR-CUS-04 không lưu PAN"
    }
    PAYMENT_WEBHOOK_LOG {
        string webhook_id PK
        string payment_id FK "nullable"
        string provider_payment_id
        string amount
        string accepted
        string reason "BR-PAY-03"
        string received_at "BR-PAY-02"
    }
    TRANSACTION_STATE_LOG {
        string log_id PK
        string order_id FK
        string kiosk_id FK "BR-ACL-01"
        string from_status
        string to_status
        string actor_type
        string actor_id "BR-ACL-01"
        string reason
        string rule_code
        string at
    }
    DEVICE_INSPECTION {
        string inspection_id PK
        string order_id FK
        string attempt_no "BR-DEV-02"
        string result "PASS EMPTY MISALIGNED UNSUPPORTED HAND"
        string width_delta_mm
        string yaw_deg
        string center_offset_mm
        string thickness_delta_mm
        string photo_uri "BR-CUS-03"
        string at
    }
    QUALITY_CHECK {
        string quality_check_id PK
        string order_id FK
        string offset_mm
        string rotation_deg
        string camera_clear
        string bubble_ok
        string edge_ok
        string sku_code_match
        string pass
        string photo_uri "BR-CUS-05"
        string checked_at
    }
    ROBOT_ARM {
        string robot_arm_id PK
        string kiosk_id FK
        string state
        string at_home "GR-03"
        string fault "GR-03"
        string scope "chỉ interface local, không lưu góc khớp"
    }
    ROBOT_EVENT_LOG {
        string event_id PK
        string robot_arm_id FK
        string kiosk_id FK
        string order_id FK "nullable"
        string event_type
        string force_n "SR-04"
        string sku_slot
        string picker_taken "BR-STK-04"
        string tray_locked "SR-01"
        string e_stop "SR-02"
        string at
    }
    STAFF {
        string staff_id PK
        string role "STF hoặc OPS"
        string pin_hash "BR-ACL-01"
        string display_name
    }
    STAFF_ACTION_LOG {
        string action_id PK
        string staff_id FK
        string kiosk_id FK
        string order_id FK "nullable"
        string action
        string reason "BR-ACL-01"
        string at
    }
    INCIDENT_REPORT {
        string incident_id PK
        string order_id FK "BR-INC-01"
        string kiosk_id FK
        string robot_arm_id FK "nullable"
        string staff_id FK "nullable"
        string level
        string photo_uris "BR-CUS-05"
        string force_log_ref
        string tray_has_device "BR-INC-03"
        string sticker_contacted "BR-INC-03"
        string customer_present "BR-INC-03"
        string handover_external "BR-INC-04"
        string opened_at
    }
    REFUND_REQUEST {
        string refund_request_id PK
        string order_id FK
        string payment_id FK "PR-06"
        string requested_by_staff_id FK "nullable"
        string approved_by_staff_id FK "nullable"
        string amount
        string mode "AUTO hoặc MANUAL"
        string status
        string reason_code
        string reject_reason "PR-07"
        string attempt_count "PR-08"
    }
    MAINTENANCE_LOG {
        string maintenance_id PK
        string kiosk_id FK
        string staff_id FK
        string robot_arm_id FK "nullable"
        string kiosk_stock_id FK "nullable"
        string log_type "RESTOCK CLEAN CHECKLIST SERVICE"
        string note "BR-STK-06 BR-OPS-01"
        string at
    }
    PHONE_MODEL ||--o{ STICKER_ITEM : "mỗi model 0..* SKU · mỗi SKU đúng 1 model · BR-CAT-01"
    STICKER_PATTERN ||--o{ STICKER_ITEM : "mỗi mẫu 0..* SKU · mỗi SKU đúng 1 mẫu"
    KIOSK ||--o{ KIOSK_STOCK : "mỗi kiosk 0..* dòng tồn · BR-STK-01"
    STICKER_ITEM ||--o{ KIOSK_STOCK : "mỗi SKU 0..* tồn theo kiosk · BR-STK-05"
    CUSTOMER |o--o{ ORDER : "mỗi đơn 0..1 khách · mỗi khách 0..* đơn · BR-CUS-01"
    PHONE_MODEL ||--o{ ORDER : "mỗi đơn đúng 1 model đã chọn · BR-SEL-01"
    STICKER_ITEM ||--o{ ORDER : "mỗi đơn đúng 1 SKU · giá chụp lúc tạo · BR-CAT-03"
    KIOSK ||--o{ ORDER : "mỗi đơn đúng 1 kiosk"
    KIOSK ||--o{ KIOSK_SESSION : "mỗi kiosk 0..* phiên · BR-CUS-01"
    KIOSK_SESSION ||--o| ORDER : "mỗi phiên 0..1 đơn · mỗi đơn đúng 1 phiên"
    ORDER ||--o{ PAYMENT : "mỗi đơn 0..* payment · chỉ 1 Success · PR-01 PR-02"
    PAYMENT |o--o{ PAYMENT_WEBHOOK_LOG : "webhook có thể chưa ghép payment · BR-PAY-02 PR-04"
    ORDER ||--o{ TRANSACTION_STATE_LOG : "vết status, không mâu ORDER.status · BR-STA-01"
    KIOSK ||--o{ TRANSACTION_STATE_LOG : "log ghi kiosk_id · BR-ACL-01"
    ORDER ||--o{ DEVICE_INSPECTION : "mỗi lần đo bước 7 · BR-DEV-01"
    ORDER ||--o{ QUALITY_CHECK : "kết quả QA mục 9 bước 10"
    KIOSK ||--|{ ROBOT_ARM : "mỗi kiosk 1..* tay qua interface · GR-03"
    ROBOT_ARM ||--o{ ROBOT_EVENT_LOG : "sự kiện local"
    KIOSK ||--o{ ROBOT_EVENT_LOG : "event tại kiosk"
    ORDER |o--o{ ROBOT_EVENT_LOG : "event có thể chưa gắn đơn"
    STAFF ||--o{ STAFF_ACTION_LOG : "audit người dùng · BR-ACL-01"
    ORDER |o--o{ STAFF_ACTION_LOG : "thao tác có thể không gắn đơn"
    KIOSK ||--o{ STAFF_ACTION_LOG : "thao tác tại kiosk · BR-ACL-01"
    STAFF |o--o{ INCIDENT_REPORT : "có thể chưa gán nhân viên · BR-INC-03"
    ORDER ||--o{ INCIDENT_REPORT : "sự cố gắn đơn · BR-INC-01"
    KIOSK ||--o{ INCIDENT_REPORT : "hiện trường"
    ROBOT_ARM |o--o{ INCIDENT_REPORT : "nguồn lực nếu có · BR-APL-01"
    ORDER ||--o{ REFUND_REQUEST : "một đơn nhiều yêu cầu hoàn"
    PAYMENT ||--o{ REFUND_REQUEST : "hoàn đúng giao dịch Success · PR-06"
    STAFF |o--o{ REFUND_REQUEST : "nhánh tay · PR-08"
    STAFF ||--o{ MAINTENANCE_LOG : "người thực hiện · BR-OPS-01"
    KIOSK ||--o{ MAINTENANCE_LOG : "BR-OPS-05"
    ROBOT_ARM |o--o{ MAINTENANCE_LOG : "bảo trì interface, không phải BOM"
    KIOSK_STOCK |o--o{ MAINTENANCE_LOG : "RESTOCK · BR-STK-06"
```

## Backlog GitHub

| Việc | Lệnh |
|---|---|
| Xem kế hoạch issue, không gọi GitHub | `python3 scripts/github-sync.py` |
| Tạo issue và Project | Điền `.env` từ `.env.example`, đặt `GITHUB_PROJECT_DRY_RUN=false`, rồi chạy lại script |

Script mặc định chỉ in kế hoạch. Không commit `.env` hoặc token.

- [Blueprint](docs/blueprint/stickerkiosk-blueprint.md)
- [Kế hoạch đồng bộ](docs/github/sync-plan.md)
- [Backlog](requirements/backlog.py)
- [Handoff](CURSOR_HANDOFF_SWD392.md)
