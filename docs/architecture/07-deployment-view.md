# 7. Triển khai

Một điểm thử, một máy. Sơ đồ này là nút phần mềm, không phải bản vẽ cơ khí.

```mermaid
C4Deployment
    title Deployment - mot kiosk MVP, khong ve phan cung
    Deployment_Node(site, "Diem thu", "1 may") {
        Deployment_Node(kiosk_node, "May kiosk", "Phan mem tai cho") {
            Container(ui, "Kiosk UI", "Web", "Man hinh khach")
            Container(local, "Local controller", "MQTT", "An toan may")
        }
    }
    Deployment_Node(cloud_node, "Cloud", "Dat ten nha cung cap sau") {
        Container(cloud, "Cloud backend", "REST", "Tien va don")
        ContainerDb(db, "Database", "SQL", "ORDER.status")
    }
    Deployment_Node(pay_node, "Nha cung cap thanh toan", "Ngoai he thong") {
        System_Ext(pay, "Payment provider", "VietQR")
    }
    Rel(ui, cloud, "REST", "HTTPS")
    Rel(local, cloud, "MQTT", "Event va lenh")
    Rel(cloud, pay, "Webhook", "HTTPS")
```

Nguồn: `diagrams/mmd/C4-Deployment.mmd`.

UI và local cùng một máy kiosk để mất mạng vẫn giữ an toàn máy (SR-20, SR-22). Cloud và database ở ngoài máy. Payment provider là hệ thống ngoài.
