# 3. Bối cảnh và phạm vi

Sơ đồ mức 1 của C4. Hệ thống phần mềm là một hộp. Người và payment provider đứng ngoài.

```mermaid
C4Context
    title System Context - phan mem kiosk dan sticker
    Person(cus, "Khach CUS", "Chon model, tra QR, dat va lay may, bam e-stop")
    Person(stf, "Nhan vien STF", "PIN, su co, nap tem, mo khoa")
    Person(ops, "Quan ly OPS", "Gia, model, nguong, duyet hoan tay")
    System(kiosk, "Phan mem kiosk sticker", "Don, thanh toan, an toan may, dan theo template")
    System_Ext(pay, "Payment provider", "VietQR, webhook Paid hoac Failed, refund. Khong luu PAN")
    Rel(cus, kiosk, "Thao tac tren man kiosk", "UI")
    Rel(stf, kiosk, "Mo khoa va xu ly su co", "PIN")
    Rel(ops, kiosk, "Cau hinh va duyet hoan", "Backoffice")
    Rel(kiosk, pay, "Tao QR va yeu cau hoan", "HTTPS")
    Rel(pay, kiosk, "Webhook ket qua tien", "HTTPS")
```

Nguồn: `diagrams/mmd/C4-Context.mmd`.

TTTM, bảo hiểm và vendor robot không nối vào hệ thống. Bàn giao máy thất lạc cho bảo vệ TTTM ghi `handover_external` (BR-INC-04), không có API điều khiển robot.

Trong phạm vi: UI kiosk, cloud đơn và tiền, local an toàn máy, cơ sở dữ liệu đơn.

Ngoài phạm vi: firmware khớp, cơ khí, bồi thường giá điện thoại.
