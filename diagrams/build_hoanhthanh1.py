#!/usr/bin/env python3
"""Sinh hoanhthanh1.json (diagram Cursor) cho kiosk dán sticker. Nguồn: đặc tả MVP v2."""

import json
import secrets
from pathlib import Path

ROOT = Path("/Users/quantran/SWD")
OUT = ROOT / "hoanhthanh1.json"
MMD = ROOT / "diagrams" / "mmd"


def page_id():
    return secrets.token_hex(10)


def layer():
    return [{"id": "1", "type": "layer"}]


class Graph:
    def __init__(self):
        self.cells = layer()
        self.n = 0

    def nid(self, prefix):
        self.n += 1
        return f"{prefix}-{self.n}"

    def node(self, label, nid=None):
        cid = nid or self.nid("n")
        self.cells.append({"id": cid, "type": "node", "parent": "1", "label": label})
        return cid

    def child(self, parent, label=None):
        cid = self.nid("c")
        cell = {"id": cid, "type": "node", "parent": parent}
        if label is not None:
            cell["label"] = label
        self.cells.append(cell)
        return cid

    def edge(self, source, target, label):
        self.cells.append(
            {
                "id": self.nid("e"),
                "type": "edge",
                "parent": "1",
                "source": source,
                "target": target,
                "label": label,
            }
        )

    def mermaid(self, text, title):
        cid = self.nid("mmd")
        self.cells.append(
            {
                "id": cid,
                "type": "node",
                "parent": "1",
                "metadata": {
                    "mermaidTitle": title,
                    "mermaidData": json.dumps(
                        {"data": text, "config": None}, ensure_ascii=False
                    )
                },
            }
        )
        return cid


def table(g, name, rows):
    """rows: list of (badge, column). badge PK/FK/UK or ''."""
    tid = g.node(name)
    for badge, col in rows:
        rid = g.child(tid)
        g.child(rid, badge or " ")
        g.child(rid, col)
    return tid


def flowchart(title, nodes, edges, notes=None):
    """nodes: (id, label). edges: (a, b, label)."""
    g = Graph()
    ids = {}
    lines = ["flowchart TD"]
    for nid, label in nodes:
        ids[nid] = g.node(label)
        safe = label.replace('"', "'")
        lines.append(f'    {nid}["{safe}"]')
    for a, b, lab in edges:
        g.edge(ids[a], ids[b], lab)
        slab = lab.replace('"', "'")
        lines.append(f'    {a} -->|"{slab}"| {b}')
    for note in notes or []:
        g.node(note)
        safe = note.replace('"', "'")
        lines.append(f'    NOTE_{len(lines)}["{safe}"]')
    text = "\n".join(lines)
    g.mermaid(text, "Nguồn Mermaid — " + title)
    return g, text


def build_usecase():
    actors = [
        ("CUS", "CUS — Khách vãng lai"),
        ("SYS", "SYS — Hệ thống kiosk"),
        ("LOC", "LOC — Local controller"),
        ("CLD", "CLD — Cloud backend"),
        ("STF", "STF — Nhân viên hỗ trợ"),
        ("OPS", "OPS — Quản lý vận hành"),
        ("PAY", "PAY — Payment provider"),
    ]
    usecases = [
        ("UC01", "UC01 Bắt đầu phiên / chọn dịch vụ\nBR-CUS-01 · GR-01..GR-08"),
        ("UC02", "UC02 Chọn model\nBR-CAT-01 · BR-SEL-01"),
        ("UC03", "UC03 Chọn pattern / SKU\nBR-CAT-02 · BR-CAT-04"),
        ("UC04", "UC04 Xác nhận 4 điều kiện an toàn\nBR-SEL-02"),
        ("UC05", "UC05 Thanh toán QR\nBR-PAY-01 · BR-PAY-02 · PR-03 · PR-05"),
        ("UC06", "UC06 Hủy đơn chưa Paid\nBR-STK-02"),
        ("UC07", "UC07 Hủy đơn đã Paid, chưa khóa khay\nPR-06"),
        ("UC08", "UC08 Đặt máy / đặt lại tối đa 2 lần\nBR-PAY-01 · BR-DEV-02"),
        ("UC09", "UC09 Lấy máy\nmục 9 bước 11"),
        ("UC10", "UC10 Bấm e-stop vật lý\nSR-02"),
        ("UC20", "UC20 Reserve tồn + tạo QR\nBR-STK-01 · BR-STK-02 · GR-05 · GR-06"),
        ("UC21", "UC21 Nhận webhook / inquiry\nBR-PAY-02 · BR-PAY-03 · PR-02 · PR-04"),
        ("UC22", "UC22 Khớp template đã chọn, không AI\nBR-DEV-01 · BR-DEV-03"),
        ("UC23", "UC23 Khóa khay\nBR-LCK-01 · SR-01"),
        ("UC24", "UC24 Apply sticker đúng 1 lần\nBR-APL-01 · BR-APL-02 · SR-04 · SR-05"),
        ("UC25", "UC25 Quality check\nmục 9 bước 10. Fail: BR-INC-01"),
        ("UC26", "UC26 Hoàn tiền tự động theo ma trận\nPR-06 · PR-07"),
        ("UC27", "UC27 Timeout QR / Paid / pickup\nmục 12. Phiên đã Paid: TR-01. Quá 180 giây: TR-02"),
        ("UC28", "UC28 Queue event khi mất mạng\nSR-20 · SR-21 · SR-22 · SR-24"),
        ("UC29", "UC29 Kiosk SERVING hoặc OUT_OF_SERVICE\nGR-01..GR-08 · SR-23 · BR-OPS-04"),
        ("UC30", "UC30 Đăng nhập PIN / thẻ\nBR-ACL-01"),
        ("UC31", "UC31 ManualRecovery và mở khóa\nBR-ACL-01 · SR-03 · SR-12"),
        ("UC32", "UC32 Reset e-stop và về HOME\nSR-03 · GR-03"),
        ("UC33", "UC33 Nạp tồn đúng slot\nBR-STK-06 · BR-OPS-03"),
        ("UC34", "UC34 Checklist mở ca / đóng ca\nBR-OPS-01 · BR-OPS-02"),
        ("UC35", "UC35 Đề nghị hoặc duyệt hoàn tay\nPR-08 · BR-INC-02"),
        ("UC36", "UC36 Tắt model/SKU, sửa giá, ngưỡng\nBR-CAT-05 · GR-08 · BR-OPS-05"),
        ("UC37", "UC37 Xử lý UnclaimedDevice\nTR-02 · BR-INC-04"),
        ("UC38", "UC38 Xem INCIDENT và ảnh\nBR-INC-01 · BR-CUS-05 · BR-CUS-03"),
    ]
    primary = {
        "CUS": ["UC01", "UC02", "UC03", "UC04", "UC05", "UC06", "UC07", "UC08", "UC09", "UC10"],
        "SYS": ["UC20", "UC21", "UC22", "UC23", "UC25", "UC26", "UC27", "UC28", "UC29"],
        "STF": ["UC30", "UC31", "UC32", "UC33", "UC34", "UC37", "UC38"],
        "OPS": ["UC35", "UC36"],
        "PAY": ["UC21"],
        "LOC": ["UC22", "UC23", "UC24", "UC25", "UC28"],
        "CLD": ["UC20", "UC21", "UC26", "UC28"],
    }
    secondary = [
        ("PAY", "UC05", "tham gia · PR-03"),
        ("PAY", "UC26", "tham gia · PR-06"),
        ("LOC", "UC10", "tham gia · SR-02"),
        ("CLD", "UC27", "tham gia · TR-01"),
        ("OPS", "UC31", "tham gia · BR-ACL-01"),
        ("OPS", "UC32", "tham gia · SR-03"),
        ("STF", "UC35", "đề nghị · OPS duyệt"),
        ("STF", "UC10", "tham gia · SR-02"),
        ("SYS", "UC01", "tạo ORDER Created"),
    ]
    includes = [
        ("UC05", "UC20", "«include» · BR-STK-01"),
        ("UC05", "UC21", "«include» · BR-PAY-02"),
        ("UC08", "UC22", "«include» · BR-DEV-01"),
        ("UC23", "UC22", "«include» đo trước khi khóa · BR-DEV-01"),
        ("UC24", "UC23", "«include» khay locked trước motion · BR-LCK-01 · SR-01"),
        ("UC24", "UC25", "«include» QA sau apply_done · BR-APL-02"),
        ("UC07", "UC26", "«include» · PR-06"),
        ("UC26", "UC27", "«extend» khi timeout đã thu tiền · PR-06"),
        ("UC10", "UC24", "«extend» ngắt apply · SR-02"),
        ("UC32", "UC10", "«include» reset sau e-stop · SR-03"),
        ("UC28", "UC21", "«extend» mất mạng lúc Pending · SR-21"),
        ("UC37", "UC38", "«include» · BR-INC-01"),
        ("UC34", "UC29", "cổng SERVING · BR-OPS-01"),
        ("UC35", "UC26", "«extend» hoàn tay · PR-08"),
        ("UC33", "UC34", "cùng ca · BR-STK-06 · BR-OPS-01"),
    ]
    g = Graph()
    actor_ids = {k: g.node(label) for k, label in actors}
    uc_ids = {k: g.node(label) for k, label in usecases}
    lines = ["flowchart LR"]
    for k, label in actors:
        lines.append(f'    {k}(("{label.replace(chr(10), " / ")}"))')
    for k, label in usecases:
        one = label.replace("\n", " | ").replace('"', "'")
        lines.append(f'    {k}["{one}"]')
    for actor, ucs in primary.items():
        for uc in ucs:
            g.edge(actor_ids[actor], uc_ids[uc], "thực hiện")
            lines.append(f"    {actor} --> {uc}")
    for actor, uc, lab in secondary:
        g.edge(actor_ids[actor], uc_ids[uc], lab)
        lines.append(f'    {actor} -->|"{lab}"| {uc}')
    for a, b, lab in includes:
        g.edge(uc_ids[a], uc_ids[b], lab)
        lines.append(f'    {a} -->|"{lab}"| {b}')
    note = (
        "Ngoài hệ thống: TTTM, bảo hiểm, vendor robot. "
        "Không vẽ đăng ký tài khoản khách, AI nhận model, app điều khiển robot, BOM hay khớp tay máy."
    )
    g.node(note)
    lines.append(f'    NGOAI["{note}"]')
    ticks = (
        "UC04 — 4 ý bắt buộc: đúng model đã chọn; đã/sẽ tháo ốp và phụ kiện; "
        "lưng khô không nứt và sẽ lau; hiểu khay khóa, sự cố do nhân viên. BR-SEL-02."
    )
    g.node(ticks)
    lines.append(f'    TICK["{ticks}"]')
    text = "\n".join(lines)
    g.mermaid(text, "Nguồn Mermaid — Use Case")
    return g, text


def build_activity():
    nodes = [
        ("A0", "Bước 0 — Kiosk rảnh, chưa có ORDER"),
        ("D0", "Đủ GR-01 đến GR-08?"),
        ("OOS", "OUT_OF_SERVICE — không nhận đơn mới"),
        ("A1", "Bước 1 — CUS bắt đầu. ORDER = Created, origin = KIOSK, customer_id null"),
        ("D120", "Chọn xong trong 120 giây?"),
        ("CAN", "ORDER = Cancelled"),
        ("A2", "Bước 2 — Hiện model và pattern. Vị trí dán = template SKU, không chọn tự do"),
        ("DSTOCK", "Còn SKU active, stock_available > 0?"),
        ("HIDE", "Ẩn SKU, không tạo QR"),
        ("A3", "Bước 3 — Tick đủ 4 điều kiện. Thiếu thì khóa nút Thanh toán"),
        ("A4", "Bước 4 — Kiểm lại GR và tồn. PAYMENT Pending, reserve, QR 300 giây. Không mở khay"),
        ("DPAY", "Kết quả thanh toán"),
        ("PAID", "ORDER = Paid, started_insert_at = now. Cửa sổ đặt máy 300 giây"),
        ("PFAIL", "ORDER = PaymentFailed, nhả reserve, không giữ tiền"),
        ("PUNK", "ORDER = PaymentUnknown. Không dán. Giữ reserve tối đa 15 phút"),
        ("DREC", "Đối soát webhook và inquiry"),
        ("MAN", "ORDER = ManualRecovery. Chỉ STF hoặc OPS, có PIN"),
        ("DINS", "Có máy trong khay trước 300 giây, hay khách hủy?"),
        ("INS", "ORDER = DeviceInserted. Cảm biến có một máy và đã Paid"),
        ("REFP", "ORDER = RefundPending. Hoàn 100%"),
        ("A7", "Bước 7 — Đo so với template của phone_model_id. Không nhận diện model"),
        ("DDEV", "Kết quả đo"),
        ("MIS", "ORDER = DeviceMisaligned"),
        ("UNS", "ORDER = DeviceUnsupported. Cấm skip"),
        ("DTRY", "Còn lượt đặt lại? Chưa tới lần 3, mỗi lần 90 giây"),
        ("LOCK", "Bước 8 — ORDER = Locked chỉ khi cảm biến tray_locked"),
        ("DLCK", "BR-LCK-01 đủ để apply?"),
        ("NOAPP", "Không gửi apply"),
        ("APP", "Bước 9 — ORDER = Applying. Đúng 1 lần"),
        ("DAPP", "Kết quả apply"),
        ("QA", "Bước 10 — ORDER = QualityChecking"),
        ("APPF", "ORDER = ApplicationFailed. Giữ khóa. INCIDENT HIGH. Không retry"),
        ("ESTOP", "ORDER = EmergencyStopped. Khay giữ nguyên khóa"),
        ("DQA", "QA đạt?"),
        ("QAF", "ORDER = QualityCheckFailed. Giữ khóa. Không tự mở"),
        ("PICK", "Bước 11 — Mở khay. ORDER = ReadyForPickup, 180 giây"),
        ("DPICK", "Khay trống trong 180 giây?"),
        ("DONE", "ORDER = Completed"),
        ("UNCL", "ORDER = UnclaimedDevice. Không nhận đơn mới đến khi khay trống"),
        ("STFCHK", "STF xác nhận máy còn hay không, chụp ảnh, đóng phiên. Không sang status mới ngoài mục 10.2"),
        ("PWR", "ORDER = PowerLost. Không tự mở khay. Không tự resume"),
        ("REFD", "ORDER = Refunded"),
        ("REJECT", "Từ chối hoàn. Giữ Completed. Hiện lý do"),
        ("END", "Kết phiên. BR-STA-02: Completed, Refunded, Cancelled không chạy robot lại"),
    ]
    edges = [
        ("A0", "D0", "Kiểm cổng bán · GR-01 GR-02 GR-03 GR-04 GR-05 GR-06 GR-07 GR-08"),
        ("D0", "OOS", "Thiếu một cổng · GR-01..GR-08. Hết tem BR-OPS-04. Mất cloud quá 2 phút SR-23. Thiếu checklist BR-OPS-01"),
        ("D0", "A1", "Đủ cổng · CUS · BR-CUS-01"),
        ("A1", "D120", "Mục 12 [MVP-DEFAULT] 120 giây. 45 giây không chạm thì reset UI, chưa Paid"),
        ("D120", "CAN", "Khách rời, quá 120 giây, hoặc hết SERVING · GR-01"),
        ("D120", "A2", "Còn trong hạn · BR-CAT-01 BR-CAT-02 BR-SEL-01 BR-CAT-04"),
        ("A2", "DSTOCK", "Giá sẽ khóa lúc xác nhận · BR-CAT-03"),
        ("DSTOCK", "HIDE", "available = 0 hoặc SKU inactive · BR-CAT-02 BR-STK-05 BR-CAT-05"),
        ("DSTOCK", "A3", "Còn hàng · BR-SEL-02. Tick không thay được bước đo"),
        ("A3", "A4", "Đủ 4 tick · SYS kiểm lại GR và stock_available · BR-STK-01 BR-PAY-01 PR-03 PR-05"),
        ("A4", "DPAY", "QR hiện, khay không mở · BR-PAY-01 BR-PAY-02"),
        ("DPAY", "PAID", "PAY webhook success, amount khớp, đúng một Success · BR-PAY-02 PR-02 PR-03 PR-04"),
        ("DPAY", "PFAIL", "Provider fail hoặc QR hết 300 giây · BR-STK-02"),
        ("DPAY", "PUNK", "Webhook lệch inquiry · BR-PAY-03"),
        ("DPAY", "CAN", "CUS hủy khi chưa Paid, nhả reserve · BR-STK-02"),
        ("PFAIL", "CAN", "Không thu nên không hoàn · BR-STK-02"),
        ("PUNK", "DREC", "Không dán, không đoán Paid · BR-PAY-03 SR-21"),
        ("DREC", "PAID", "Đối soát trong 15 phút, có tiền · BR-PAY-03"),
        ("DREC", "PFAIL", "Đối soát không có tiền · BR-PAY-03"),
        ("DREC", "MAN", "Quá 15 phút vẫn unknown, không dán · BR-PAY-03"),
        ("PAID", "DINS", "Cửa sổ đặt máy 300 giây. Đã Paid thì không reset để phục vụ khách khác · TR-01"),
        ("DINS", "REFP", "Hết 300 giây không đặt, hoặc CUS hủy trước khóa · PR-06"),
        ("DINS", "INS", "Cảm biến có một máy. Chưa Paid thì không gán DeviceInserted · BR-PAY-01"),
        ("INS", "A7", "Đo template của model đã chọn · BR-DEV-01"),
        ("A7", "DDEV", "So template đã chọn. Cấm nút skip · BR-DEV-03"),
        ("DDEV", "A7", "Khay trống hoặc còn tay người: không đổi status, không khóa · BR-DEV-01"),
        ("DDEV", "MIS", "Nhiều vật, góc yaw trên 3 độ, hoặc lệch tâm trên 2 mm · BR-DEV-01"),
        ("DDEV", "UNS", "WxH lệch quá ±1.5 mm hoặc dày hơn template + 1.0 mm · BR-DEV-01 BR-DEV-03"),
        ("DDEV", "LOCK", "Khớp template và tray_locked · BR-DEV-01"),
        ("MIS", "DTRY", "Mỗi lần lệch tính 1 fail, hạn 90 giây · BR-DEV-02"),
        ("DTRY", "PAID", "Còn lượt, chưa tới lần 3. Về cửa sổ Paid, không apply · BR-DEV-02"),
        ("DTRY", "REFP", "Lần 3 fail, khay không khóa hoặc đã mở, cảm biến trống · BR-DEV-02"),
        ("UNS", "REFP", "Khay trống sau khi mở để rút · PR-06"),
        ("LOCK", "DLCK", "robot_enable cần Locked, tray_locked, e_stop false, Paid, sku reserved · BR-LCK-01 SR-01"),
        ("DLCK", "NOAPP", "Thiếu một điều kiện, kể cả cloud gửi nhầm · SR-01 SR-05"),
        ("DLCK", "APP", "Local chấp nhận. Tối đa 1 apply · BR-APL-02"),
        ("APP", "DAPP", "Lực không vượt max_force_n · SR-04"),
        ("DAPP", "QA", "apply_done, không fault. on_hand trừ 1, nhả reserve · BR-STK-03 BR-APL-02"),
        ("DAPP", "APPF", "Lực, mất bước, mở khay, mất sensor. Giữ khóa · BR-APL-01 SR-04 SR-05 BR-INC-01"),
        ("DAPP", "ESTOP", "E-stop. Một status EmergencyStopped, vẫn INCIDENT · SR-02 BR-APL-01 BR-INC-01"),
        ("APP", "PWR", "Mất điện khi đang có máy · SR-10 SR-11"),
        ("LOCK", "PWR", "Mất điện · SR-10 SR-11"),
        ("LOCK", "ESTOP", "E-stop, khay giữ khóa · SR-02"),
        ("QA", "DQA", "Cạnh tối đa 1.5 mm, xoay tối đa 1.5 độ, không đè mask, không bọt trên 3 mm, không hở góc · mục 9 bước 10"),
        ("DQA", "PICK", "QA Pass. Cạnh tối đa 1.5 mm, xoay tối đa 1.5 độ · mục 9 bước 10"),
        ("DQA", "QAF", "QA Fail · BR-INC-01"),
        ("QAF", "MAN", "Chỉ STF/OPS · BR-ACL-01 BR-INC-03"),
        ("APPF", "MAN", "Chỉ STF/OPS. Picker taken vẫn trừ on_hand · BR-ACL-01 BR-STK-04"),
        ("APPF", "ESTOP", "E-stop, khay giữ khóa · SR-02"),
        ("QAF", "ESTOP", "E-stop, khay giữ khóa · SR-02"),
        ("PICK", "DPICK", "Cửa sổ lấy máy 180 giây · mục 12"),
        ("DPICK", "DONE", "Khay trống · mục 9 bước 11"),
        ("DPICK", "UNCL", "Quá 180 giây · TR-02"),
        ("PICK", "PWR", "Mất điện · SR-11"),
        ("PWR", "MAN", "Có điện không tự resume. STF xác nhận máy · SR-12 BR-ACL-01"),
        ("ESTOP", "MAN", "Reset chỉ khi vùng trống, không có tay · SR-03 BR-ACL-01"),
        ("REFP", "REFD", "Provider refund success, đúng giao dịch, không tiền mặt · PR-06"),
        ("REFP", "MAN", "Refund fail 3 lần hoặc quá 24 giờ · PR-08"),
        ("DONE", "REJECT", "Khách đổi ý sau QA Pass · PR-07 BR-STA-02"),
        ("DONE", "END", "Kết · BR-STA-02"),
        ("REFD", "END", "Kết · BR-STA-02"),
        ("CAN", "END", "Kết · BR-STA-02"),
        ("UNCL", "STFCHK", "STF xác nhận, không đổi status ngoài mục 10.2 · TR-02 BR-INC-04"),
    ]
    notes = [
        "BR-STA-01: cấm nhảy cóc, ví dụ Paid sang Applying hoặc Created sang Locked. Activity đi đúng cổng mục 9.",
        "P4: local quyết định an toàn máy, cloud quyết định tiền. Mất mạng lúc Pending không bịa Paid · SR-20 SR-21.",
        "ApplicationFailed và QualityCheckFailed sang ManualRecovery theo mục 10.2. Hoàn 100% ghi ở REFUND_REQUEST theo mục 11, không thêm status ngoài bảng 10.2.",
        "4 tick: đúng model đã chọn; tháo ốp và phụ kiện; lưng khô không nứt sẽ lau; hiểu khay khóa và sự cố do nhân viên.",
    ]
    return flowchart("Activity", nodes, edges, notes)


def build_state():
    transitions = [
        ("[*]", "Created", "CUS", "Kiosk đang SERVING, bắt đầu phiên ẩn danh", "GR-01 BR-CUS-01"),
        ("Created", "PaymentPending", "SYS", "SKU hợp lệ, đủ 4 tick, còn hàng, tạo QR được", "BR-CAT-01 BR-CAT-02 BR-CAT-03 BR-STK-01 BR-SEL-02"),
        ("Created", "Cancelled", "SYS", "Khách rời, quá 120 giây không chọn, hoặc hết SERVING", "GR-01"),
        ("PaymentPending", "Paid", "PAY", "Webhook success, amount khớp, đúng order, chưa có Success khác", "BR-PAY-02 PR-02 PR-03 PR-04"),
        ("PaymentPending", "PaymentFailed", "PAY", "Provider fail hoặc QR hết 300 giây", "BR-STK-02"),
        ("PaymentPending", "PaymentUnknown", "CLD", "Webhook lệch inquiry, không dán", "BR-PAY-03"),
        ("PaymentPending", "Cancelled", "CUS", "Hủy khi chưa Paid, nhả reserve", "BR-STK-02"),
        ("PaymentUnknown", "Paid", "CLD", "Đối soát trong 15 phút, xác nhận có tiền", "BR-PAY-03"),
        ("PaymentUnknown", "PaymentFailed", "CLD", "Đối soát không có tiền", "BR-PAY-03"),
        ("PaymentUnknown", "ManualRecovery", "SYS", "Quá 15 phút vẫn unknown, không dán", "BR-PAY-03"),
        ("PaymentFailed", "Cancelled", "SYS", "Nhả reserve, không giữ tiền, không phát sinh hoàn", "BR-STK-02"),
        ("Paid", "DeviceInserted", "LOC", "Cảm biến có máy và payment đã Paid", "BR-PAY-01"),
        ("Paid", "RefundPending", "SYS", "Hết 300 giây không đặt máy, hoặc khách hủy trước khóa", "PR-06"),
        ("DeviceInserted", "Locked", "LOC", "Template Pass và tray_locked", "BR-DEV-01"),
        ("DeviceInserted", "DeviceMisaligned", "LOC", "Nhiều vật, góc lệch quá 3 độ, hoặc tâm lệch quá 2 mm", "BR-DEV-01"),
        ("DeviceInserted", "DeviceUnsupported", "LOC", "Kích thước hoặc độ dày không khớp, cấm skip", "BR-DEV-01 BR-DEV-03"),
        ("DeviceMisaligned", "Paid", "SYS", "Còn lượt đặt lại, chưa tới lần 3, không apply", "BR-DEV-02"),
        ("DeviceMisaligned", "RefundPending", "SYS", "Lần 3 fail, khay không khóa hoặc đã mở, rồi khay trống", "BR-DEV-02"),
        ("DeviceUnsupported", "RefundPending", "SYS", "Khay không khóa hoặc đã mở để rút, cảm biến trống", "PR-06"),
        ("Locked", "Applying", "LOC", "Đủ robot_enable và local không từ chối", "BR-LCK-01 SR-01 BR-APL-02"),
        ("Applying", "QualityChecking", "LOC", "apply_done, không fault", "BR-APL-02 BR-STK-03"),
        ("Applying", "ApplicationFailed", "LOC", "Lực, mất bước, mở khay hoặc mất sensor. Giữ khóa, không retry", "BR-APL-01 SR-04 SR-05 BR-INC-01"),
        ("Applying", "EmergencyStopped", "CUS STF OPS", "E-stop cắt motion. Một status, khay giữ khóa, có INCIDENT", "SR-02 BR-APL-01 BR-INC-01"),
        ("QualityChecking", "ReadyForPickup", "SYS", "QA Pass. Cạnh tối đa 1.5 mm, xoay tối đa 1.5 độ, không đè mask, không bọt trên 3 mm, không hở góc", "mục 9 bước 10"),
        ("QualityChecking", "QualityCheckFailed", "SYS", "QA Fail, giữ khóa, không tự mở", "BR-INC-01"),
        ("ReadyForPickup", "Completed", "LOC", "Khay trống sau khi mở", "mục 9 bước 11"),
        ("ReadyForPickup", "UnclaimedDevice", "SYS", "Quá 180 giây chưa lấy, không nhận đơn mới", "TR-02"),
        ("ApplicationFailed", "ManualRecovery", "STF", "Chỉ STF hoặc OPS, ghi actor và lý do", "BR-ACL-01 BR-INC-03"),
        ("QualityCheckFailed", "ManualRecovery", "STF", "Chỉ STF hoặc OPS", "BR-ACL-01 BR-INC-03"),
        ("PowerLost", "ManualRecovery", "STF", "Có điện thì không tự resume", "SR-12 BR-ACL-01"),
        ("EmergencyStopped", "ManualRecovery", "STF", "Vùng làm việc trống và không có tay", "SR-03 BR-ACL-01"),
        ("RefundPending", "Refunded", "PAY", "Refund success đúng giao dịch đã Success", "PR-06"),
        ("RefundPending", "ManualRecovery", "SYS", "Provider fail sau 3 lần hoặc quá 24 giờ", "PR-08"),
        ("Completed", "[*]", "SYS", "Trạng thái kết. OPS chỉ bút toán, không chạy robot", "BR-STA-02"),
        ("Refunded", "[*]", "SYS", "Trạng thái kết", "BR-STA-02"),
        ("Cancelled", "[*]", "SYS", "Trạng thái kết", "BR-STA-02"),
    ]
    power_from = [
        "DeviceInserted",
        "DeviceMisaligned",
        "DeviceUnsupported",
        "Locked",
        "Applying",
        "QualityChecking",
        "ReadyForPickup",
        "ApplicationFailed",
        "QualityCheckFailed",
        "UnclaimedDevice",
        "EmergencyStopped",
        "ManualRecovery",
    ]
    for src in power_from:
        transitions.append(
            (src, "PowerLost", "LOC", "Mất điện khi đang có máy trong khay. UPS ghi snapshot, không tự mở", "SR-10 SR-11")
        )
    estop_from = [
        "Created",
        "PaymentPending",
        "Paid",
        "DeviceInserted",
        "DeviceMisaligned",
        "DeviceUnsupported",
        "Locked",
        "QualityChecking",
        "ReadyForPickup",
        "UnclaimedDevice",
        "ApplicationFailed",
        "QualityCheckFailed",
    ]
    for src in estop_from:
        transitions.append(
            (src, "EmergencyStopped", "CUS STF OPS", "E-stop cắt motion, khay giữ nguyên khóa", "SR-02")
        )

    g = Graph()
    states = []
    for a, b, *_ in transitions:
        states.append(a)
        states.append(b)
    # giữ tên 10.1 dù không có mũi tên
    states.append("NetworkDegraded")
    ids = {}
    for name in dict.fromkeys(states):
        if name in ("[*]",):
            continue
        ids[name] = g.node(name)
    start = g.node("Bắt đầu")
    end = g.node("Kết")
    ids["[*]"] = None

    lines = [
        "stateDiagram-v2",
        "    direction TB",
        "    %% Nhãn trên sơ đồ là actor và mã. Câu điều kiện đầy đủ nằm trên cạnh trong hoanhthanh1.json.",
    ]
    for a, b, actor, cond, codes in transitions:
        label = f"{actor} - {cond} - {codes}"
        if a == "[*]":
            g.edge(start, ids[b], label)
        elif b == "[*]":
            g.edge(ids[a], end, label)
        else:
            g.edge(ids[a], ids[b], label)
        lines.append(f"    {a} --> {b}: {actor} / {cond} / {codes}")

    notes = [
        "BR-STA-01 cấm nhảy cóc: không có Paid sang Applying, không có Created sang Locked.",
        "NetworkDegraded có trong mục 10.1 nhưng mục 10.2 không định nghĩa transition của ORDER. Mất mạng xử lý bằng SR-21 SR-22 SR-23 GR-07 trên kiosk, không bịa Paid.",
        "Khay trống lúc Paid hoặc DeviceInserted: không đổi status. Có tay người: không khóa, quá 20 giây vẫn không khóa.",
        "Mục 10.2 không nối ApplicationFailed hay QualityCheckFailed sang RefundPending. Hoàn tiền mục 11 ghi REFUND_REQUEST khi STF đang ManualRecovery.",
        "Applying cộng e-stop: SR-02 đặt EmergencyStopped, BR-APL-01 cũng nêu e-stop. P3 chỉ một ORDER.status nên không vẽ thêm sang ApplicationFailed. Vẫn mở INCIDENT.",
    ]
    for note in notes:
        g.node(note)
    g.node(
        "ORDER.status đủ mục 10.1: Created, PaymentPending, Paid, DeviceInserted, Locked, Applying, "
        "QualityChecking, ReadyForPickup, Completed, PaymentFailed, PaymentUnknown, DeviceUnsupported, "
        "DeviceMisaligned, ApplicationFailed, QualityCheckFailed, PowerLost, NetworkDegraded, "
        "EmergencyStopped, ManualRecovery, RefundPending, Refunded, Cancelled, UnclaimedDevice."
    )
    text = "\n".join(lines)
    g.mermaid(text, "Nguồn Mermaid — State ORDER")
    return g, text, transitions


def build_sequence(title, steps, edges, notes):
    return flowchart(title, steps, edges, notes)


def build_pay_seq():
    steps = [
        ("S1", "CUS tick đủ 4 điều kiện trên kiosk"),
        ("S2", "SYS kiểm lại GR-01..GR-08, model, SKU, stock_available"),
        ("S3", "CLD giữ ORDER PaymentPending, price_snapshot, customer có thể null"),
        ("S4", "CLD reserve: available = on_hand trừ reserved. Giữ tối đa 7 phút"),
        ("S5", "PAY tạo QR. Amount bằng price_snapshot. Hết hạn 300 giây. Không phụ phí"),
        ("S6", "SYS hiện QR. Không mở khay. Không có nút Tôi đã trả. Điện thoại không điều khiển robot"),
        ("S7", "PAY gửi webhook tới CLD"),
        ("S8", "CLD đối amount, order_id, provider_payment_id"),
        ("S9", "Sai amount hoặc sai order: từ chối webhook. ORDER vẫn PaymentPending"),
        ("S9B", "Webhook khác inquiry: PaymentUnknown, không dán, giữ reserve"),
        ("S9C", "Đối soát trong 15 phút xác nhận có tiền: ORDER = Paid"),
        ("S10", "Trùng provider_payment_id: bỏ qua, không tạo Success thứ hai"),
        ("S11", "Khớp: một PAYMENT purpose CHARGE status Success. ORDER = Paid"),
        ("S12", "SYS hướng dẫn tháo ốp, lau, đặt máy. Không reset phiên"),
        ("S13", "Provider fail hoặc QR hết hạn: PaymentFailed rồi Cancelled, nhả reserve, không hoàn"),
        ("S14", "CUS hủy lúc Pending: Cancelled, hủy QR nếu provider hỗ trợ, nhả reserve"),
        ("S15", "Mất mạng lúc Pending: không đoán Paid. Xếp event, inquiry khi có mạng"),
        ("S16", "Vẫn unknown sau 15 phút: ManualRecovery, không dán"),
    ]
    edges = [
        ("S1", "S2", "BR-SEL-02"),
        ("S2", "S3", "GR-01..GR-08 · BR-CAT-01 · BR-CAT-02 · BR-CAT-03 · BR-CUS-01"),
        ("S3", "S4", "BR-STK-01 · BR-STK-02"),
        ("S4", "S5", "PR-03 · PR-05"),
        ("S5", "S6", "BR-PAY-01 · BR-PAY-02"),
        ("S6", "S7", "CUS quét QR · P6"),
        ("S7", "S8", "BR-PAY-02 · BR-CUS-04"),
        ("S8", "S9", "Từ chối webhook · PR-03"),
        ("S8", "S9B", "Webhook lệch inquiry · BR-PAY-03"),
        ("S9B", "S9C", "Đối soát có tiền · BR-PAY-03"),
        ("S9B", "S16", "Quá 15 phút vẫn unknown · BR-PAY-03"),
        ("S8", "S10", "Idempotent · PR-04 · PR-02"),
        ("S8", "S11", "Webhook là nguồn Paid · BR-PAY-02 · PR-02"),
        ("S11", "S12", "TR-01"),
        ("S6", "S13", "Hết 300 giây hoặc fail · BR-STK-02"),
        ("S6", "S14", "CUS hủy chưa Paid · BR-STK-02"),
        ("S6", "S15", "Đứt mạng · SR-20 · SR-21 · SR-24"),
        ("S15", "S8", "Có mạng thì inquiry, không đoán Paid · SR-21 SR-24"),
        ("S15", "S16", "Hết 15 phút vẫn unknown · BR-PAY-03"),
    ]
    notes = [
        "Ví dụ mục 20: iPhone 15 Pro Max, tem trong suốt, 199000, còn 8 tấm, Paid rồi mới đặt. Không phải rule mới.",
        "Kiosk không tự gán Paid. UI polling chỉ để hiển thị · BR-PAY-02.",
    ]
    return build_sequence("Sequence thanh toán", steps, edges, notes)


def build_interlock_seq():
    steps = [
        ("I0", "Sau Paid, cảm biến có một máy thì ORDER = DeviceInserted. Chưa Paid thì không"),
        ("I1", "LOC inspect_device theo template của model đã chọn"),
        ("I2", "LOC trả inspect_result. Chỉ khớp hoặc không khớp, không suy ra tên máy"),
        ("I3", "Khay trống: không đổi ORDER.status, yêu cầu đặt lại"),
        ("I4", "Còn tay: không lock_tray. Quá 20 giây vẫn có tay: vẫn không khóa"),
        ("I5", "Sai kích thước hoặc độ dày: DeviceUnsupported. Không có nút skip"),
        ("I6", "Lệch góc hoặc tâm: DeviceMisaligned. Còn lượt thì về Paid, không apply"),
        ("I7", "Pass: LOC lock_tray. ORDER = Locked chỉ khi cảm biến locked"),
        ("I8", "CLD gửi pick_sku(slot) và apply(template_id). Không gửi góc khớp"),
        ("I9", "LOC kiểm trước khi chuyển động. Thiếu điều kiện thì từ chối lệnh"),
        ("I10", "Apply đúng một lần, lực không quá max_force_n"),
        ("I11", "Fault: safe_halt, ApplicationFailed, giữ khóa, INCIDENT HIGH, không retry"),
        ("I12", "apply_failed mà picker_taken: vẫn trừ on_hand, không dùng lại tấm"),
        ("I13", "apply_success: on_hand trừ 1, nhả reserve, sang QualityChecking, qa_capture"),
        ("I14", "QA Pass: unlock_tray, ReadyForPickup 180 giây"),
        ("I15", "QA Fail: không unlock, QualityCheckFailed, INCIDENT"),
    ]
    edges = [
        ("I0", "I1", "BR-PAY-01"),
        ("I1", "I2", "BR-DEV-01"),
        ("I2", "I3", "Bước 7 khay trống"),
        ("I2", "I4", "Bước 7 tay người"),
        ("I2", "I5", "BR-DEV-01 · BR-DEV-03"),
        ("I2", "I6", "BR-DEV-01 · BR-DEV-02"),
        ("I2", "I7", "Pass và tray_locked · BR-DEV-01"),
        ("I7", "I8", "Lệnh nghiệp vụ, không phải quỹ đạo khớp"),
        ("I8", "I9", "BR-LCK-01 · SR-01 · SR-05"),
        ("I9", "I10", "Local cho phép · BR-APL-02 · SR-04"),
        ("I10", "I11", "BR-APL-01 · SR-04 · SR-05 · BR-INC-01"),
        ("I11", "I12", "BR-STK-04"),
        ("I10", "I13", "BR-STK-03"),
        ("I13", "I14", "QA Pass mục 9 bước 10"),
        ("I13", "I15", "BR-INC-01"),
    ]
    notes = [
        "robot_enable = ORDER Locked AND tray_locked AND e_stop false AND payment Paid AND sku reserved · BR-LCK-01.",
        "SR-01: firmware local chặn apply khi khay chưa locked, kể cả cloud gửi nhầm.",
    ]
    return build_sequence("Sequence interlock", steps, edges, notes)


def build_refund_seq():
    steps = [
        ("R0", "Có hay chưa có PAYMENT Success?"),
        ("R1", "QR hết hạn hoặc thanh toán fail: không thu, không tạo hoàn"),
        ("R2", "Paid, hủy trước khi khóa khay: tự động 100%"),
        ("R3", "Paid, hết 300 giây không đặt máy: tự động 100%"),
        ("R4", "DeviceUnsupported hoặc hết lượt lệch: tự động 100% sau khi khay trống"),
        ("R5", "PaymentUnknown rồi xác nhận không có tiền: không hoàn, Cancelled"),
        ("R5B", "Nếu sau đó provider báo đã có tiền: hoàn 100%"),
        ("R6", "ApplicationFailed, tem chưa chạm: tự động 100%, STF mở khóa"),
        ("R7", "ApplicationFailed, tem đã chạm: tự động 100%, INCIDENT, không tự gỡ tem"),
        ("R8", "QA fail, khách không nhận: tự động 100% sau khi STF xác nhận"),
        ("R9", "QA fail, khách vẫn nhận: tự động 100%. MVP không bán hàng lỗi"),
        ("R10", "Completed, QA pass, khách đổi ý: từ chối, hiện lý do"),
        ("R11", "Nghi hư máy, trầy, tranh chấp: OPS duyệt. Phần mềm không bồi thường máy"),
        ("R12", "Nghi gian lận: OPS khóa hoàn tự động, giữ ảnh"),
        ("R13", "CLD tạo REFUND_REQUEST và PAYMENT purpose REFUND. ORDER = RefundPending rồi Refunded khi provider success"),
        ("R14", "Provider success: ORDER = Refunded. Chỉ từ RefundPending"),
        ("R6M", "ORDER giữ ManualRecovery. REFUND_REQUEST ghi hoàn 100%. Không gán Refunded"),
        ("R15", "Fail 3 lần hoặc RefundPending quá 24 giờ: ManualRecovery, báo OPS, vẫn trả máy theo an toàn"),
    ]
    edges = [
        ("R0", "R1", "Chưa Success · BR-STK-02"),
        ("R0", "R2", "PR-06 · mục 11"),
        ("R0", "R3", "Hết 300 giây · PR-06"),
        ("R0", "R4", "Khay trống · BR-DEV-02 · PR-06"),
        ("R0", "R5", "BR-PAY-03"),
        ("R5", "R5B", "BR-PAY-03 · PR-06"),
        ("R0", "R6", "BR-APL-01 · PR-06 · BR-ACL-01"),
        ("R0", "R7", "BR-APL-01 · BR-INC-01 · BR-INC-02 · PR-06"),
        ("R0", "R8", "BR-INC-03 · PR-06"),
        ("R0", "R9", "PR-06 · BR-INC-03"),
        ("R0", "R10", "PR-07 · BR-STA-02"),
        ("R0", "R11", "BR-INC-02"),
        ("R0", "R12", "BR-INC-02 · BR-CUS-03"),
        ("R2", "R13", "AUTO · PR-06 · BR-CUS-04"),
        ("R3", "R13", "AUTO · PR-06"),
        ("R4", "R13", "AUTO sau khay trống · PR-06"),
        ("R5B", "R13", "AUTO · PR-06"),
        ("R6", "R6M", "Mục 10.2 giữ ManualRecovery · PR-06 · BR-ACL-01"),
        ("R7", "R6M", "Mục 10.2 giữ ManualRecovery · PR-06 · BR-INC-01"),
        ("R8", "R6M", "Mục 10.2 giữ ManualRecovery · PR-06 · BR-INC-03"),
        ("R9", "R6M", "Mục 10.2 giữ ManualRecovery · PR-06"),
        ("R11", "R6M", "OPS duyệt. Không tự Refunded · BR-INC-02 · PR-08"),
        ("R13", "R14", "PR-06"),
        ("R13", "R15", "PR-08"),
    ]
    notes = [
        "PR-07: mọi từ chối hoàn phải hiện lý do trên màn hình và trên phiếu sự cố.",
        "Mục 10.2 không có mũi tên ApplicationFailed sang RefundPending. Status an toàn là ManualRecovery; tiền đi theo REFUND_REQUEST.",
        "Không hoàn tiền mặt tại kiosk · PR-06. Không lưu PAN · BR-CUS-04.",
    ]
    return build_sequence("Sequence hoàn tiền", steps, edges, notes)


def build_estop_seq():
    steps = [
        ("E1", "CUS, STF hoặc OPS bấm e-stop vật lý"),
        ("E2", "LOC cắt chuyển động ngay: safe_halt và estop_ack"),
        ("E3", "Khay giữ đúng trạng thái khóa lúc nhấn. Không tự unlock"),
        ("E4", "ORDER = EmergencyStopped. Kiosk.mode = EMERGENCY_STOP"),
        ("E5", "Nếu đang Applying: không gán thêm ApplicationFailed. Mở INCIDENT HIGH"),
        ("E6", "LOC từ chối apply mới"),
        ("E7", "Chỉ STF hoặc OPS đã đăng nhập PIN được reset, khi vùng trống và không có tay"),
        ("E8", "LOC về HOME. ORDER = ManualRecovery. Không tự dán tiếp"),
        ("P1", "Nhánh mất điện, khác e-stop: UPS snapshot order_id rồi an toàn hóa"),
        ("P2", "ORDER = PowerLost. Không tự mở khay"),
        ("P3", "Có điện: không tự resume. STF ManualRecovery. Chưa dán thì hoàn 100%"),
    ]
    edges = [
        ("E1", "E2", "SR-02"),
        ("E2", "E3", "SR-02"),
        ("E3", "E4", "SR-02"),
        ("E4", "E5", "P3 một status · BR-APL-01 · BR-INC-01"),
        ("E4", "E6", "SR-01 · BR-LCK-01"),
        ("E6", "E7", "SR-03 · BR-ACL-01"),
        ("E7", "E8", "GR-03 · SR-03 · BR-ACL-01"),
        ("P1", "P2", "SR-10 · SR-11"),
        ("P2", "P3", "SR-12 · PR-06 · SR-13"),
    ]
    notes = [
        "SR-13: mục tiêu có thể mở khóa theo quy trình trong 2 phút sau khi có điện, không tính thời gian nhân viên đi tới.",
        "Không thiết kế UPS, tay máy hay sơ đồ điện. Sequence chỉ là contract an toàn phần mềm.",
    ]
    return build_sequence("Sequence e-stop và mất điện", steps, edges, notes)


def build_erd():
    entities = {
        "PHONE_MODEL": [
            ("PK", "phone_model_id"),
            ("", "name"),
            ("", "is_supported · BR-CAT-01"),
            ("", "width_mm"),
            ("", "height_mm"),
            ("", "thickness_mm"),
            ("", "camera_mask"),
            ("", "align_template_uri · BR-DEV-01"),
            ("", "qa_offset_max_mm · GR-08"),
        ],
        "STICKER_PATTERN": [
            ("PK", "sticker_pattern_id"),
            ("", "name"),
            ("", "preview_uri"),
        ],
        "STICKER_ITEM": [
            ("PK", "sticker_item_id"),
            ("FK", "sticker_pattern_id"),
            ("FK", "phone_model_id"),
            ("", "price · BR-CAT-03"),
            ("", "estimated_seconds · BR-CAT-04"),
            ("", "active · BR-CAT-05"),
            ("", "slot_code · mục 18"),
        ],
        "KIOSK": [
            ("PK", "kiosk_id"),
            ("", "mode · GR-01 SERVING OUT_OF_SERVICE MAINTENANCE EMERGENCY_STOP"),
            ("", "max_force_n · GR-08 SR-04"),
            ("", "align_tolerance_mm · GR-08"),
            ("", "qa_offset_max_mm · GR-08"),
            ("", "force_maintenance · BR-OPS-05"),
            ("", "last_heartbeat_at · GR-02"),
        ],
        "KIOSK_STOCK": [
            ("PK", "kiosk_stock_id"),
            ("FK", "kiosk_id"),
            ("FK", "sticker_item_id"),
            ("UK", "stock_natural_key · unique kiosk_id và sticker_item_id"),
            ("", "on_hand"),
            ("", "reserved · BR-STK-01"),
            ("", "reorder_threshold · BR-STK-05"),
            ("", "slot_code · BR-OPS-03"),
        ],
        "CUSTOMER": [
            ("PK", "customer_id"),
            ("", "phone_vn · nullable BR-CUS-02"),
        ],
        "KIOSK_SESSION": [
            ("PK", "session_id"),
            ("FK", "kiosk_id"),
            ("", "anonymous · BR-CUS-01"),
            ("", "started_at"),
            ("", "last_touch_at · mục 12"),
        ],
        "ORDER": [
            ("PK", "order_id"),
            ("", "status · enum mục 10.1 BR-STA-01"),
            ("FK", "kiosk_id"),
            ("FK", "phone_model_id"),
            ("FK", "sticker_item_id"),
            ("FK", "customer_id · nullable BR-CUS-01"),
            ("FK", "session_id"),
            ("", "price_snapshot · BR-CAT-03"),
            ("", "attempt_align_count · BR-DEV-02"),
            ("", "phone_optional · BR-CUS-02"),
            ("", "started_insert_at"),
            ("", "origin · KIOSK"),
        ],
        "PAYMENT": [
            ("PK", "payment_id"),
            ("FK", "order_id · PR-01"),
            ("UK", "provider_payment_id · PR-04"),
            ("", "provider"),
            ("", "amount · PR-03 PR-05"),
            ("", "status"),
            ("", "purpose · CHARGE hoặc REFUND"),
            ("", "paid_at · BR-CUS-04 không lưu PAN"),
        ],
        "PAYMENT_WEBHOOK_LOG": [
            ("PK", "webhook_id"),
            ("FK", "payment_id · nullable"),
            ("", "provider_payment_id"),
            ("", "amount"),
            ("", "accepted"),
            ("", "reason · BR-PAY-03"),
            ("", "received_at · BR-PAY-02"),
        ],
        "TRANSACTION_STATE_LOG": [
            ("PK", "log_id"),
            ("FK", "order_id"),
            ("FK", "kiosk_id · BR-ACL-01"),
            ("", "from_status"),
            ("", "to_status"),
            ("", "actor_type"),
            ("", "actor_id · BR-ACL-01"),
            ("", "reason"),
            ("", "rule_code"),
            ("", "at"),
        ],
        "DEVICE_INSPECTION": [
            ("PK", "inspection_id"),
            ("FK", "order_id"),
            ("", "attempt_no · BR-DEV-02"),
            ("", "result · PASS EMPTY MISALIGNED UNSUPPORTED HAND"),
            ("", "width_delta_mm"),
            ("", "yaw_deg"),
            ("", "center_offset_mm"),
            ("", "thickness_delta_mm"),
            ("", "photo_uri · BR-CUS-03"),
            ("", "at"),
        ],
        "QUALITY_CHECK": [
            ("PK", "quality_check_id"),
            ("FK", "order_id"),
            ("", "offset_mm"),
            ("", "rotation_deg"),
            ("", "camera_clear"),
            ("", "bubble_ok"),
            ("", "edge_ok"),
            ("", "sku_code_match"),
            ("", "pass"),
            ("", "photo_uri · BR-CUS-05"),
            ("", "checked_at"),
        ],
        "ROBOT_ARM": [
            ("PK", "robot_arm_id"),
            ("FK", "kiosk_id"),
            ("", "state"),
            ("", "at_home · GR-03"),
            ("", "fault · GR-03"),
            ("", "scope · chỉ interface local, không lưu góc khớp"),
        ],
        "ROBOT_EVENT_LOG": [
            ("PK", "event_id"),
            ("FK", "robot_arm_id"),
            ("FK", "kiosk_id"),
            ("FK", "order_id · nullable"),
            ("", "event_type"),
            ("", "force_n · SR-04"),
            ("", "sku_slot"),
            ("", "picker_taken · BR-STK-04"),
            ("", "tray_locked · SR-01"),
            ("", "e_stop · SR-02"),
            ("", "at"),
        ],
        "STAFF": [
            ("PK", "staff_id"),
            ("", "role · STF hoặc OPS"),
            ("", "pin_hash · BR-ACL-01"),
            ("", "display_name"),
        ],
        "STAFF_ACTION_LOG": [
            ("PK", "action_id"),
            ("FK", "staff_id"),
            ("FK", "kiosk_id"),
            ("FK", "order_id · nullable"),
            ("", "action"),
            ("", "reason · BR-ACL-01"),
            ("", "at"),
        ],
        "INCIDENT_REPORT": [
            ("PK", "incident_id"),
            ("FK", "order_id · BR-INC-01"),
            ("FK", "kiosk_id"),
            ("FK", "robot_arm_id · nullable"),
            ("FK", "staff_id · nullable"),
            ("", "level"),
            ("", "photo_uris · BR-CUS-05"),
            ("", "force_log_ref"),
            ("", "tray_has_device · BR-INC-03"),
            ("", "sticker_contacted · BR-INC-03"),
            ("", "customer_present · BR-INC-03"),
            ("", "handover_external · BR-INC-04"),
            ("", "opened_at"),
        ],
        "REFUND_REQUEST": [
            ("PK", "refund_request_id"),
            ("FK", "order_id"),
            ("FK", "payment_id · PR-06"),
            ("FK", "requested_by_staff_id · nullable"),
            ("FK", "approved_by_staff_id · nullable"),
            ("", "amount"),
            ("", "mode · AUTO hoặc MANUAL"),
            ("", "status"),
            ("", "reason_code"),
            ("", "reject_reason · PR-07"),
            ("", "attempt_count · PR-08"),
        ],
        "MAINTENANCE_LOG": [
            ("PK", "maintenance_id"),
            ("FK", "kiosk_id"),
            ("FK", "staff_id"),
            ("FK", "robot_arm_id · nullable"),
            ("FK", "kiosk_stock_id · nullable"),
            ("", "log_type · RESTOCK CLEAN CHECKLIST SERVICE"),
            ("", "note · BR-STK-06 BR-OPS-01"),
            ("", "at"),
        ],
    }
    rels = [
        ("PHONE_MODEL", "STICKER_ITEM", "||--o{", "mỗi model 0..* SKU · mỗi SKU đúng 1 model · BR-CAT-01"),
        ("STICKER_PATTERN", "STICKER_ITEM", "||--o{", "mỗi mẫu 0..* SKU · mỗi SKU đúng 1 mẫu"),
        ("KIOSK", "KIOSK_STOCK", "||--o{", "mỗi kiosk 0..* dòng tồn · BR-STK-01"),
        ("STICKER_ITEM", "KIOSK_STOCK", "||--o{", "mỗi SKU 0..* tồn theo kiosk · BR-STK-05"),
        ("CUSTOMER", "ORDER", "|o--o{", "mỗi đơn 0..1 khách · mỗi khách 0..* đơn · BR-CUS-01"),
        ("PHONE_MODEL", "ORDER", "||--o{", "mỗi đơn đúng 1 model đã chọn · BR-SEL-01"),
        ("STICKER_ITEM", "ORDER", "||--o{", "mỗi đơn đúng 1 SKU · giá chụp lúc tạo · BR-CAT-03"),
        ("KIOSK", "ORDER", "||--o{", "mỗi đơn đúng 1 kiosk"),
        ("KIOSK", "KIOSK_SESSION", "||--o{", "mỗi kiosk 0..* phiên · BR-CUS-01"),
        ("KIOSK_SESSION", "ORDER", "||--o|", "mỗi phiên 0..1 đơn · mỗi đơn đúng 1 phiên"),
        ("ORDER", "PAYMENT", "||--o{", "mỗi đơn 0..* payment · chỉ 1 Success · PR-01 PR-02"),
        ("PAYMENT", "PAYMENT_WEBHOOK_LOG", "|o--o{", "webhook có thể chưa ghép payment · BR-PAY-02 PR-04"),
        ("ORDER", "TRANSACTION_STATE_LOG", "||--o{", "vết status, không mâu ORDER.status · BR-STA-01"),
        ("KIOSK", "TRANSACTION_STATE_LOG", "||--o{", "log ghi kiosk_id · BR-ACL-01"),
        ("ORDER", "DEVICE_INSPECTION", "||--o{", "mỗi lần đo bước 7 · BR-DEV-01"),
        ("ORDER", "QUALITY_CHECK", "||--o{", "kết quả QA mục 9 bước 10"),
        ("KIOSK", "ROBOT_ARM", "||--|{", "mỗi kiosk 1..* tay qua interface · GR-03"),
        ("ROBOT_ARM", "ROBOT_EVENT_LOG", "||--o{", "sự kiện local"),
        ("KIOSK", "ROBOT_EVENT_LOG", "||--o{", "event tại kiosk"),
        ("ORDER", "ROBOT_EVENT_LOG", "|o--o{", "event có thể chưa gắn đơn"),
        ("STAFF", "STAFF_ACTION_LOG", "||--o{", "audit người dùng · BR-ACL-01"),
        ("ORDER", "STAFF_ACTION_LOG", "|o--o{", "thao tác có thể không gắn đơn"),
        ("KIOSK", "STAFF_ACTION_LOG", "||--o{", "thao tác tại kiosk · BR-ACL-01"),
        ("STAFF", "INCIDENT_REPORT", "|o--o{", "có thể chưa gán nhân viên · BR-INC-03"),
        ("ORDER", "INCIDENT_REPORT", "||--o{", "sự cố gắn đơn · BR-INC-01"),
        ("KIOSK", "INCIDENT_REPORT", "||--o{", "hiện trường"),
        ("ROBOT_ARM", "INCIDENT_REPORT", "|o--o{", "nguồn lực nếu có · BR-APL-01"),
        ("ORDER", "REFUND_REQUEST", "||--o{", "một đơn nhiều yêu cầu hoàn"),
        ("PAYMENT", "REFUND_REQUEST", "||--o{", "hoàn đúng giao dịch Success · PR-06"),
        ("STAFF", "REFUND_REQUEST", "|o--o{", "nhánh tay · PR-08"),
        ("STAFF", "MAINTENANCE_LOG", "||--o{", "người thực hiện · BR-OPS-01"),
        ("KIOSK", "MAINTENANCE_LOG", "||--o{", "BR-OPS-05"),
        ("ROBOT_ARM", "MAINTENANCE_LOG", "|o--o{", "bảo trì interface, không phải BOM"),
        ("KIOSK_STOCK", "MAINTENANCE_LOG", "|o--o{", "RESTOCK · BR-STK-06"),
    ]
    g = Graph()
    ids = {name: table(g, name, rows) for name, rows in entities.items()}
    mer_lines = ["erDiagram"]
    for name, rows in entities.items():
        mer_lines.append(f"    {name} {{")
        for badge, col in rows:
            fname = col.split(" · ")[0].replace(" ", "_").replace("+", "_")
            comment = col.split(" · ", 1)[1] if " · " in col else ""
            kind = {"PK": "PK", "FK": "FK", "UK": "UK"}.get(badge, "")
            suffix = f" {kind}" if kind else ""
            if comment:
                mer_lines.append(f'        string {fname}{suffix} "{comment}"')
            else:
                mer_lines.append(f"        string {fname}{suffix}")
        mer_lines.append("    }")
    for a, b, crow, label in rels:
        g.edge(ids[a], ids[b], label)
        mer_lines.append(f'    {a} {crow} {b} : "{label}"')
    notes = [
        "Sửa Trang-4 cũ: ORDER sang PAYMENT là 1-n theo PR-01, không còn 1-1.",
        "Bỏ KIOSK nối thẳng STICKER_ITEM. Tồn kho là KIOSK_STOCK, available = on_hand trừ reserved · BR-STK-01.",
        "Bỏ ROBOT_ARM nối thẳng ORDER. Đơn không có robot_arm_id. Việc dán ghi ở ROBOT_EVENT_LOG.",
        "Bỏ STAFF nối thẳng STICKER_ITEM. Nạp hàng là MAINTENANCE_LOG loại RESTOCK · BR-STK-06 BR-OPS-03.",
        "CUSTOMER tùy chọn. Không lưu khuôn mặt làm định danh · BR-CUS-03. Không lưu PAN · BR-CUS-04.",
        "ROBOT_ARM chỉ là interface local: state, at_home, fault. Không có khớp, BOM, hãng tay.",
    ]
    for note in notes:
        g.node(note)
    text = "\n".join(mer_lines)
    g.mermaid(text, "Nguồn Mermaid — ERD Trang-4")
    return g, text


def main():
    pages = []
    mmd_dir = MMD
    mmd_dir.mkdir(parents=True, exist_ok=True)
    builders = [
        ("UseCase", build_usecase),
        ("Activity", build_activity),
        ("State-ORDER", lambda: build_state()[:2]),
        ("Seq-ThanhToan", build_pay_seq),
        ("Seq-Interlock", build_interlock_seq),
        ("Seq-HoanTien", build_refund_seq),
        ("Seq-EStop", build_estop_seq),
        ("Trang-4", build_erd),
    ]
    for name, fn in builders:
        graph, text = fn()
        pages.append({"id": page_id(), "name": name, "cells": graph.cells})
        (mmd_dir / f"{name}.mmd").write_text(text + "\n", encoding="utf-8")
        print(f"{name}: cells={len(graph.cells)} mermaid_lines={text.count(chr(10))+1}")

    doc = {"version": "31.5.0", "pages": pages}
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", OUT, "bytes", OUT.stat().st_size)


if __name__ == "__main__":
    main()
