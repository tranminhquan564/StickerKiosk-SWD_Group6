#!/usr/bin/env python3
"""Đọc diagrams/mmd/*.mmd và ghi diagrams/kiosk.drawio."""

import re
from pathlib import Path
from xml.sax.saxutils import escape

MMD = Path("/Users/quantran/SWD/diagrams/mmd")
OUT = Path("/Users/quantran/SWD/diagrams/kiosk.drawio")

NODE_RE = re.compile(
    r"""^\s*([A-Za-z0-9_]+)\s*(?:\[\s*"(.*)"\s*\]|\(\(\s*"(.*)"\s*\)\))\s*$"""
)
EDGE_RE = re.compile(
    r"""^\s*([A-Za-z0-9_]+)\s+-->\s*(?:\|"(.*)"\|\s*)?([A-Za-z0-9_]+)\s*$"""
)
STATE_RE = re.compile(r"""^\s*(\[\*\]|[A-Za-z0-9_]+)\s+-->\s*(\[\*\]|[A-Za-z0-9_]+)\s*:\s*(.*)$""")
REL_RE = re.compile(r"""^\s*([A-Z0-9_]+)\s+(\S+)\s+([A-Z0-9_]+)\s*:\s*"(.*)"\s*$""")
FIELD_RE = re.compile(r"""^\s*string\s+(\S+)(?:\s+(PK|FK|UK))?(?:\s+"(.*)")?\s*$""")


def parse_flowchart(text):
    direction = "TD"
    nodes = {}
    edges = []
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("flowchart "):
            direction = line.split()[1]
            continue
        if not line or line.startswith("%%"):
            continue
        m = NODE_RE.match(line)
        if m:
            label = m.group(2) if m.group(2) is not None else m.group(3)
            kind = "actor" if m.group(3) is not None else "step"
            if label.endswith("?"):
                kind = "decision"
            if m.group(1).startswith("NOTE"):
                kind = "note"
            nodes[m.group(1)] = {"label": label, "kind": kind}
            continue
        m = EDGE_RE.match(line)
        if m:
            edges.append((m.group(1), m.group(3), m.group(2) or ""))
    return direction, nodes, edges


def parse_state(text):
    edges = []
    seen = set()
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("%%") or line.startswith("stateDiagram") or line.startswith("direction"):
            continue
        m = STATE_RE.match(line)
        if m:
            item = (m.group(1), m.group(2), m.group(3).strip())
            if item in seen:
                continue
            seen.add(item)
            edges.append(item)
    nodes = {}
    for a, b, _ in edges:
        for name in (a, b):
            if name == "[*]":
                continue
            nodes.setdefault(name, {"label": name, "kind": "state"})
    return nodes, edges


def parse_er(text):
    entities = {}
    current = None
    rels = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("erDiagram") or line.startswith("%%"):
            continue
        if line.endswith("{") and current is None:
            current = line.split()[0]
            entities[current] = []
            continue
        if line == "}":
            current = None
            continue
        if current:
            m = FIELD_RE.match(line)
            if m:
                badge = m.group(2) or ""
                comment = m.group(3) or ""
                entities[current].append((badge, m.group(1), comment))
            continue
        m = REL_RE.match(line)
        if m:
            rels.append((m.group(1), m.group(3), m.group(4)))
    return entities, rels


class Xml:
    def __init__(self, name):
        self.name = name
        self.n = 1
        self.parts = [
            f'<diagram id="{escape(name)}" name="{escape(name)}">',
            '<mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="2400" pageHeight="1600" math="0" shadow="0">',
            "<root>",
            '<mxCell id="0"/>',
            '<mxCell id="1" parent="0"/>',
        ]
        self.ids = {}

    def cell(self, value, style, x, y, w, h):
        self.n += 1
        cid = str(self.n)
        self.parts.append(
            f'<mxCell id="{cid}" value="{escape(value)}" style="{style}" vertex="1" parent="1">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>'
            f"</mxCell>"
        )
        return cid

    def edge(self, src, tgt, label, style):
        self.n += 1
        cid = str(self.n)
        self.parts.append(
            f'<mxCell id="{cid}" value="{escape(label)}" style="{style}" edge="1" parent="1" source="{src}" target="{tgt}">'
            f'<mxGeometry relative="1" as="geometry"/>'
            f"</mxCell>"
        )
        return cid

    def close(self):
        self.parts.append("</root></mxGraphModel></diagram>")
        return "\n".join(self.parts)


STEP = "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#666666;fontSize=12;"
DECISION = "rhombus;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;"
ACTOR = "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;fontSize=12;"
NOTE = "shape=note;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;size=14;fontSize=12;align=left;spacingLeft=8;"
STATE = "rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;fontSize=13;"
TERM = "ellipse;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontStyle=1;fontSize=12;"
UC = "ellipse;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=11;"
EDGE = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;endFill=1;fontSize=11;"
ASSOC = "endArrow=none;html=1;fontSize=11;edgeStyle=orthogonalEdgeStyle;"


def ranks(nodes, edges):
    incoming = {k: 0 for k in nodes}
    outs = {k: [] for k in nodes}
    for a, b, _ in edges:
        if a in nodes and b in nodes and a != b:
            outs[a].append(b)
            incoming[b] += 1
    level = {k: 0 for k in nodes}
    queue = [k for k, n in incoming.items() if n == 0] or list(nodes)
    seen = set()
    while queue:
        cur = queue.pop(0)
        if cur in seen:
            continue
        seen.add(cur)
        for nxt in outs[cur]:
            level[nxt] = max(level[nxt], level[cur] + 1)
            incoming[nxt] -= 1
            if incoming[nxt] <= 0:
                queue.append(nxt)
    for k in nodes:
        if k not in seen:
            level[k] = max(level.values(), default=0) + 1
    return level


def layout_flow(name, direction, nodes, edges):
    doc = Xml(name)
    level = ranks(nodes, edges)
    buckets = {}
    for k, lv in level.items():
        buckets.setdefault(lv, []).append(k)
    for lv in buckets:
        buckets[lv].sort()
    horizontal = direction == "LR"
    for lv, keys in buckets.items():
        for i, key in enumerate(keys):
            info = nodes[key]
            label = info["label"]
            if info["kind"] == "actor":
                style, w, h = ACTOR, 50, 80
            elif info["kind"] == "note":
                style, w, h = NOTE, 280, 90
            elif info["kind"] == "decision":
                style, w, h = DECISION, 200, 110
            elif key.startswith("UC"):
                style, w, h = UC, 210, 80
            else:
                style, w, h = STEP, 230, 90
            if horizontal:
                x, y = 40 + lv * 280, 40 + i * 120
            else:
                x, y = 40 + i * 260, 40 + lv * 150
            doc.ids[key] = doc.cell(label, style, x, y, w, h)
    style_edge = ASSOC if name == "UseCase" else EDGE
    for a, b, label in edges:
        if a in doc.ids and b in doc.ids:
            extra = "endArrow=open;dashed=1;" if "include" in label or "extend" in label or "«" in label else ""
            doc.edge(doc.ids[a], doc.ids[b], label, style_edge + extra)
    return doc.close()


CORE_STATES = [
    "Created",
    "PaymentPending",
    "PaymentFailed",
    "PaymentUnknown",
    "Cancelled",
    "Paid",
    "DeviceInserted",
    "DeviceMisaligned",
    "DeviceUnsupported",
    "Locked",
    "Applying",
    "ApplicationFailed",
    "QualityChecking",
    "QualityCheckFailed",
    "ReadyForPickup",
    "Completed",
    "UnclaimedDevice",
    "RefundPending",
    "Refunded",
    "ManualRecovery",
    "PowerLost",
    "EmergencyStopped",
]


def is_fan(a, b):
    if b == "PowerLost" and a not in ("PowerLost",):
        return a != "Applying"
    if b == "EmergencyStopped" and a not in ("Applying",):
        return True
    return False


def layout_state(name, nodes, edges, fan):
    doc = Xml(name)
    columns = [
        ["Created", "PaymentPending", "PaymentFailed", "PaymentUnknown", "Cancelled"],
        ["Paid", "DeviceInserted", "DeviceMisaligned", "DeviceUnsupported"],
        ["Locked", "Applying", "ApplicationFailed"],
        ["QualityChecking", "QualityCheckFailed", "ReadyForPickup", "Completed", "UnclaimedDevice"],
        ["RefundPending", "Refunded", "ManualRecovery", "PowerLost", "EmergencyStopped"],
    ]
    shown = set()
    for col, names in enumerate(columns):
        for row, state in enumerate(names):
            if state not in nodes and state not in CORE_STATES:
                continue
            terminal = state in ("Completed", "Refunded", "Cancelled")
            doc.ids[state] = doc.cell(state, TERM if terminal else STATE, 40 + col * 230, 80 + row * 110, 190, 60)
            shown.add(state)
    start = doc.cell("Bắt đầu", TERM, 40, 10, 80, 40)
    end = doc.cell("Kết", TERM, 40 + 4 * 230, 10, 80, 40)
    doc.ids["[*]-in"] = start
    doc.ids["[*]-out"] = end
    for a, b, label in edges:
        fan_edge = is_fan(a, b)
        if fan != fan_edge:
            continue
        src = doc.ids.get(a) if a != "[*]" else start
        tgt = doc.ids.get(b) if b != "[*]" else end
        if a == "[*]":
            src = start
        if b == "[*]":
            tgt = end
        if src and tgt:
            doc.edge(src, tgt, label, EDGE)
    return doc.close()


ENTITY_POS = {
    "PHONE_MODEL": (40, 40),
    "STICKER_PATTERN": (360, 40),
    "STICKER_ITEM": (680, 40),
    "KIOSK_STOCK": (1040, 40),
    "KIOSK": (40, 420),
    "KIOSK_SESSION": (360, 420),
    "ORDER": (680, 420),
    "CUSTOMER": (1100, 420),
    "PAYMENT": (40, 860),
    "PAYMENT_WEBHOOK_LOG": (360, 860),
    "REFUND_REQUEST": (720, 860),
    "TRANSACTION_STATE_LOG": (1080, 860),
    "DEVICE_INSPECTION": (40, 1280),
    "QUALITY_CHECK": (400, 1280),
    "ROBOT_ARM": (760, 1280),
    "ROBOT_EVENT_LOG": (1080, 1280),
    "STAFF": (40, 1720),
    "STAFF_ACTION_LOG": (360, 1720),
    "INCIDENT_REPORT": (720, 1720),
    "MAINTENANCE_LOG": (1120, 1720),
}


def layout_er(name, entities, rels):
    doc = Xml(name)
    for ename, fields in entities.items():
        lines = [f"<b>{ename}</b>"]
        for badge, field, comment in fields:
            bit = f"{badge} {field}".strip()
            if comment:
                bit = f"{bit} · {comment}"
            lines.append(bit)
        value = "<br>".join(lines)
        x, y = ENTITY_POS.get(ename, (40, 2100))
        h = 28 + 16 * max(len(fields), 1)
        doc.ids[ename] = doc.cell(value, "text;html=1;strokeColor=#6c8ebf;fillColor=#dae8fc;align=left;verticalAlign=top;spacingLeft=6;spacingTop=4;whiteSpace=wrap;fontSize=11;", x, y, 300, h)
    for a, b, label in rels:
        if a in doc.ids and b in doc.ids:
            doc.edge(doc.ids[a], doc.ids[b], label, EDGE)
    return doc.close()


def split_state_mmd(text):
    core = ["stateDiagram-v2", "    direction TB"]
    fan = ["stateDiagram-v2", "    direction TB", "    %% Cùng máy trạng thái ORDER. Trang này chỉ ngắt điện và e-stop hàng loạt."]
    seen = set()
    for raw in text.splitlines():
        m = STATE_RE.match(raw.strip())
        if not m:
            if raw.strip().startswith("stateDiagram") or raw.strip().startswith("direction") or raw.strip().startswith("%%"):
                continue
            continue
        a, b, label = m.group(1), m.group(2), m.group(3).strip()
        item = (a, b, label)
        if item in seen:
            continue
        seen.add(item)
        line = f"    {a} --> {b}: {label}"
        (fan if is_fan(a, b) else core).append(line)
    return "\n".join(core) + "\n", "\n".join(fan) + "\n"


def load_state_text():
    order = (MMD / "State-ORDER.mmd").read_text(encoding="utf-8")
    extra = MMD / "State-Ngat.mmd"
    if extra.exists():
        order = order + "\n" + extra.read_text(encoding="utf-8")
    return order


def main():
    pages = {}
    for path in sorted(MMD.glob("*.mmd")):
        if path.name in ("State-ORDER.mmd", "State-Ngat.mmd"):
            continue
        text = path.read_text(encoding="utf-8")
        if text.startswith("C4"):
            continue
        if text.startswith("erDiagram"):
            entities, rels = parse_er(text)
            pages[path.stem] = layout_er(path.stem, entities, rels)
        elif text.startswith("flowchart"):
            direction, nodes, edges = parse_flowchart(text)
            pages[path.stem] = layout_flow(path.stem, direction, nodes, edges)
        else:
            raise SystemExit(f"Không đọc được {path.name}")
    state_text = load_state_text()
    nodes, edges = parse_state(state_text)
    pages["State-ORDER"] = layout_state("State-ORDER", nodes, edges, fan=False)
    pages["State-Ngat"] = layout_state("State-Ngat", nodes, edges, fan=True)
    core, interrupt = split_state_mmd(state_text)
    (MMD / "State-ORDER.mmd").write_text(core, encoding="utf-8")
    (MMD / "State-Ngat.mmd").write_text(interrupt, encoding="utf-8")
    order = [
        "UseCase",
        "Activity",
        "State-ORDER",
        "State-Ngat",
        "Seq-ThanhToan",
        "Seq-Interlock",
        "Seq-HoanTien",
        "Seq-EStop",
        "Trang-4",
    ]
    body = "\n".join(pages[name] for name in order)
    xml = (
        '<mxfile host="app.diagrams.net" agent="SWD392" version="22.1.0">\n'
        + body
        + "\n</mxfile>\n"
    )
    OUT.write_text(xml, encoding="utf-8")
    print(f"pages={len(pages)} bytes={OUT.stat().st_size}")


if __name__ == "__main__":
    main()
