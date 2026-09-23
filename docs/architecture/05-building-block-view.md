# 5. Khối xây dựng

Mức 2 và mức 3 của C4. Mức 4 (lớp code) chưa có vì repo chưa chứa ứng dụng kiosk.

## 5.1 Container

```mermaid
C4Container
    title Container - phan mem kiosk sticker
    Person(cus, "Khach CUS", "Tu phuc vu tai may")
    System_Boundary(sw, "Phan mem kiosk") {
        Container(ui, "Kiosk UI", "Web", "Man hinh chon, QR, huong dan. Khong dieu khien robot")
        Container(cloud, "Cloud backend", "REST", "Order, catalog, payment, refund, staff. Nguon su that tien")
        Container(local, "Local controller", "MQTT hoac WS", "Khay, interlock, lenh nghiep vu. Nguon su that an toan may")
        ContainerDb(db, "Database", "SQL", "ORDER.status, payment, stock, audit")
    }
    System_Ext(pay, "Payment provider", "VietQR")
    Rel(cus, ui, "Chon va thanh toan")
    Rel(ui, cloud, "Don va catalog", "HTTPS REST")
    Rel(ui, local, "Lenh va su kien", "MQTT hoac WS")
    Rel(cloud, db, "Doc ghi trang thai don")
    Rel(cloud, pay, "Tao QR, hoan tien, nhan webhook", "HTTPS")
    Rel(local, cloud, "Day event khi co mang, khong bia Paid", "MQTT")
```

Nguồn: `diagrams/mmd/C4-Container.mmd`.

## 5.2 Component cloud

```mermaid
C4Component
    title Component - Cloud backend
    Container(ui, "Kiosk UI", "Web", "Goi REST")
    Container(local, "Local controller", "MQTT", "Gui event, nhan lenh")
    ContainerDb(db, "Database", "SQL", "ORDER.status la nguon su that nghiep vu")
    System_Ext(pay, "Payment provider", "Webhook")
    Container_Boundary(cloud, "Cloud backend") {
        Component(catalog, "Catalog", "Service", "BR-CAT va BR-STK. An SKU het hang")
        Component(order, "Order", "Service", "ORDER.status. Cam nhay coc BR-STA-01")
        Component(payment, "Payment", "Service", "Webhook la nguon Paid. PR-03 tu choi sai amount")
        Component(refund, "Refund", "Service", "REFUND_REQUEST. Khong tu Refunded tu ManualRecovery")
        Component(staff, "Staff", "Service", "PIN, BR-ACL-01, duyet hoan tay")
    }
    Rel(ui, catalog, "Lay model va SKU", "REST")
    Rel(ui, order, "Tao va huy don", "REST")
    Rel(ui, payment, "Xin QR", "REST")
    Rel(pay, payment, "Webhook", "HTTPS")
    Rel(payment, order, "Chi webhook hop le moi Paid", "BR-PAY-02")
    Rel(order, db, "Ghi status")
    Rel(payment, db, "Ghi PAYMENT, khong luu PAN")
    Rel(refund, payment, "Hoan dung giao dich Success", "PR-06")
    Rel(staff, order, "ManualRecovery", "BR-ACL-01")
    Rel(local, order, "Event may, khong sua tien", "MQTT")
```

Nguồn: `diagrams/mmd/C4-Component-Cloud.mmd`.

## 5.3 Component local

```mermaid
C4Component
    title Component - Local controller
    Container(cloud, "Cloud backend", "REST", "Gui lenh nghiep vu")
    Container_Boundary(local, "Local controller") {
        Component(gateway, "Command gateway", "MQTT", "home, inspect_device, lock_tray, unlock_tray, pick_sku, apply, qa_capture, estop_ack, safe_halt")
        Component(interlock, "Interlock", "Policy", "Tu choi apply neu thieu BR-LCK-01 hoac SR-01")
        Component(queue, "Event queue", "Store", "SR-24 dung thu tu, idempotent")
        Component(safety, "Safety", "Monitor", "SR-02 e-stop, SR-10 snapshot mat dien")
    }
    Rel(cloud, gateway, "Lenh nghiep vu, khong gui goc khop")
    Rel(gateway, interlock, "apply phai qua interlock")
    Rel(safety, interlock, "e-stop hoac mat sensor thi chan motion", "SR-02 SR-05")
    Rel(gateway, queue, "Xep heartbeat, inspect_result, apply_success, picker_taken, force_n")
    Rel(queue, cloud, "Gui lai khi co mang, khong doan Paid", "SR-21")
```

Nguồn: `diagrams/mmd/C4-Component-Local.mmd`.

ERD các bảng nằm ở `diagrams/mmd/Trang-4.mmd`, không lặp lại ở đây.
