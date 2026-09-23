#!/usr/bin/env python3
"""Kiểm tra tài liệu C4 và arc42. Thoát 0 khi đủ file và đúng loại sơ đồ."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

DIAGRAMS = {
    "diagrams/mmd/C4-Context.mmd": "C4Context",
    "diagrams/mmd/C4-Container.mmd": "C4Container",
    "diagrams/mmd/C4-Component-Cloud.mmd": "C4Component",
    "diagrams/mmd/C4-Component-Local.mmd": "C4Component",
    "diagrams/mmd/C4-Deployment.mmd": "C4Deployment",
}

CHAPTERS = [
    "docs/architecture/README.md",
    "docs/architecture/01-introduction-and-goals.md",
    "docs/architecture/02-constraints.md",
    "docs/architecture/03-context-and-scope.md",
    "docs/architecture/04-solution-strategy.md",
    "docs/architecture/05-building-block-view.md",
    "docs/architecture/06-runtime-view.md",
    "docs/architecture/07-deployment-view.md",
    "docs/architecture/08-crosscutting.md",
    "docs/architecture/09-architecture-decisions.md",
    "docs/architecture/10-quality-requirements.md",
    "docs/architecture/11-risks.md",
    "docs/architecture/12-glossary.md",
]


def main() -> int:
    errors = []
    for rel, kind in DIAGRAMS.items():
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"thieu {rel}")
            continue
        first = path.read_text(encoding="utf-8").splitlines()[0].strip()
        if first != kind:
            errors.append(f"{rel} bat dau bang {first}, can {kind}")
    for rel in CHAPTERS:
        if not (ROOT / rel).is_file():
            errors.append(f"thieu {rel}")
    readme = ROOT / "README.md"
    if not readme.is_file():
        errors.append("thieu README.md")
    else:
        text = readme.read_text(encoding="utf-8")
        for token in ("C4Context", "C4Container", "C4Component", "C4Deployment"):
            if token not in text:
                errors.append(f"README thieu {token}")
        if "docs/architecture/README.md" not in text:
            errors.append("README khong tro toi arc42")
    exporter = (ROOT / "diagrams/export_drawio.py").read_text(encoding="utf-8")
    if 'startswith("C4")' not in exporter:
        errors.append("export_drawio.py chua bo qua file C4")
    if errors:
        print("\n".join(errors))
        return 1
    print(f"ok diagrams={len(DIAGRAMS)} chapters={len(CHAPTERS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
