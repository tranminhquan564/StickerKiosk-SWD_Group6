#!/usr/bin/env python3
"""Đồng bộ backlog StickerKiosk lên GitHub Issues + Project (BA Blueprint Agent).

Đọc .env (không in token). Mặc định GITHUB_PROJECT_DRY_RUN=true.
Issue title: [FR-###] / [NFR-###] / [SP-###]
Body: Context, Scope, Acceptance criteria, Dependency, Risk, link blueprint.
Không tạo trùng theo Blueprint ID trong title.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from requirements.backlog import BLUEPRINT_PATH, ISSUES  # noqa: E402

STATUS_OPTIONS = [
    "Backlog",
    "Ready",
    "In Progress",
    "In Review",
    "Blocked",
    "Done",
    "Cancelled",
]
PRIORITY_OPTIONS = ["P0 Critical", "P1 High", "P2 Medium", "P3 Low"]
TYPE_OPTIONS = ["Feature", "Story", "Bug", "Task", "Spike"]
AREA_OPTIONS = [
    "kiosk-ui",
    "payment",
    "safety-controller",
    "apply-quality",
    "staff-console",
    "ledger-audit",
    "hardware-adapter",
    "privacy-ops",
]
RISK_OPTIONS = ["None", "Low", "Medium", "High", "Critical"]

LABEL_DEFS = [
    ("status:backlog", "BFD4F2", "Status = Backlog"),
    ("status:ready", "0E8A16", "Status = Ready"),
    ("status:in-progress", "1D76DB", "Status = In Progress"),
    ("status:in-review", "5319E7", "Status = In Review"),
    ("status:blocked", "B60205", "Status = Blocked"),
    ("status:done", "0E8A16", "Status = Done"),
    ("status:cancelled", "FFFFFF", "Status = Cancelled"),
    ("priority:p0-critical", "B60205", "Priority = P0 Critical"),
    ("priority:p1-high", "D93F0B", "Priority = P1 High"),
    ("priority:p2-medium", "FBCA04", "Priority = P2 Medium"),
    ("priority:p3-low", "C2E0C6", "Priority = P3 Low"),
    ("type:feature", "1D76DB", "Type = Feature"),
    ("type:story", "0052CC", "Type = Story"),
    ("type:bug", "D73A4A", "Type = Bug"),
    ("type:task", "C5DEF5", "Type = Task"),
    ("type:spike", "D4C5F9", "Type = Spike"),
    ("area:kiosk-ui", "0075CA", "Area = kiosk-ui"),
    ("area:payment", "006B75", "Area = payment"),
    ("area:safety-controller", "B60205", "Area = safety-controller"),
    ("area:apply-quality", "BFDAD6", "Area = apply-quality"),
    ("area:staff-console", "C2E0C6", "Area = staff-console"),
    ("area:ledger-audit", "F9D0C4", "Area = ledger-audit"),
    ("area:hardware-adapter", "FEF2C0", "Area = hardware-adapter"),
    ("area:privacy-ops", "EDEDED", "Area = privacy-ops"),
    ("risk:none", "FFFFFF", "Risk = None"),
    ("risk:low", "C2E0C6", "Risk = Low"),
    ("risk:medium", "FBCA04", "Risk = Medium"),
    ("risk:high", "D93F0B", "Risk = High"),
    ("risk:critical", "B60205", "Risk = Critical"),
]


def load_env(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not path.exists():
        return env
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def merge_config() -> dict[str, str]:
    file_env = load_env(ROOT / ".env")
    cfg = {
        "GITHUB_OWNER": os.environ.get("GITHUB_OWNER") or file_env.get("GITHUB_OWNER", ""),
        "GITHUB_REPOSITORY": os.environ.get("GITHUB_REPOSITORY")
        or file_env.get("GITHUB_REPOSITORY", "StickerKiosk-SWD_Group6"),
        "GITHUB_PROJECT_NUMBER": os.environ.get("GITHUB_PROJECT_NUMBER")
        or file_env.get("GITHUB_PROJECT_NUMBER", ""),
        "GITHUB_PROJECT_URL": os.environ.get("GITHUB_PROJECT_URL")
        or file_env.get("GITHUB_PROJECT_URL", ""),
        "GITHUB_PROJECT_TITLE": os.environ.get("GITHUB_PROJECT_TITLE")
        or file_env.get("GITHUB_PROJECT_TITLE", "StickerKiosk Delivery"),
        "GITHUB_PROJECT_DRY_RUN": os.environ.get("GITHUB_PROJECT_DRY_RUN")
        or file_env.get("GITHUB_PROJECT_DRY_RUN", "true"),
        "GITHUB_DEFAULT_BRANCH": os.environ.get("GITHUB_DEFAULT_BRANCH")
        or file_env.get("GITHUB_DEFAULT_BRANCH", "main"),
        "GITHUB_REPO_VISIBILITY": os.environ.get("GITHUB_REPO_VISIBILITY")
        or file_env.get("GITHUB_REPO_VISIBILITY", "private"),
        "GITHUB_TOKEN": os.environ.get("GITHUB_TOKEN")
        or os.environ.get("GH_TOKEN")
        or file_env.get("GITHUB_TOKEN", ""),
    }
    return cfg


def is_dry_run(cfg: dict[str, str]) -> bool:
    return cfg["GITHUB_PROJECT_DRY_RUN"].lower() in {"1", "true", "yes"}


def issue_labels(item: dict) -> list[str]:
    prio = {
        "P0 Critical": "priority:p0-critical",
        "P1 High": "priority:p1-high",
        "P2 Medium": "priority:p2-medium",
        "P3 Low": "priority:p3-low",
    }[item["priority"]]
    typ = {
        "Feature": "type:feature",
        "Story": "type:story",
        "Bug": "type:bug",
        "Task": "type:task",
        "Spike": "type:spike",
    }[item["type"]]
    risk = {
        "None": "risk:none",
        "Low": "risk:low",
        "Medium": "risk:medium",
        "High": "risk:high",
        "Critical": "risk:critical",
    }[item["risk"]]
    return [
        "status:backlog",
        prio,
        typ,
        f"area:{item['area']}",
        risk,
    ]


def render_body(item: dict, repo_url: str) -> str:
    ac = "\n".join(f"- {line}" for line in item["acceptance"])
    blueprint_url = f"{repo_url}/blob/main/{BLUEPRINT_PATH}"
    return f"""## Context

{item["context"]}

## Scope

{item["scope"]}

## Acceptance criteria

{ac}

## Dependency

{item["dependency"]}

## Risk

{item["risk_detail"]}

## Blueprint

- Blueprint ID: `{item["id"]}`
- Type: {item["type"]}
- Priority: {item["priority"]}
- Area: {item["area"]}
- Iteration: {item["iteration"]}
- Risk field: {item["risk"]}
- Link: {blueprint_url}

## Delivery

- Status: Backlog
- Owner: unassigned (gán khi Ready)
- Target date: chưa cam kết (blueprint Draft)
- Branch: `<type>/<issue-number>-<short-slug>`
- PR phải `Closes #<number>` hoặc `Refs #<number>`
- Không đóng issue khi acceptance criteria chưa có evidence test/review

### Comment bắt buộc khi cập nhật tiến độ

```
Progress: [Not started|In progress|Blocked|Ready for review|Done]
Summary: <đã hoàn thành hoặc đang xử lý>
Evidence: <commit, PR, test hoặc tài liệu>
Branch/PR: <branch và PR>
Next: <bước tiếp theo>
Blocker: <None hoặc blocker + owner + expected resolution>
```
"""


def run_gh(args: list[str], token: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    if token:
        env["GH_TOKEN"] = token
        env["GITHUB_TOKEN"] = token
    return subprocess.run(
        ["gh", *args],
        check=check,
        text=True,
        capture_output=True,
        env=env,
    )


def gh_json(args: list[str], token: str):
    proc = run_gh(args, token)
    return json.loads(proc.stdout) if proc.stdout.strip() else None


def assert_auth(token: str) -> dict:
    try:
        return gh_json(["api", "user"], token)
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        raise SystemExit(
            "BLOCKER: GitHub CLI chưa xác thực.\n"
            "Cần `gh auth login` trên máy có trình duyệt, hoặc gán GH_TOKEN/GITHUB_TOKEN "
            "với quyền repo, project, read:org (classic) — hoặc fine-grained: "
            "Administration (tạo repo), Contents, Issues, Metadata, Projects.\n"
            "Không dùng org bịa. Tạo repo dưới tài khoản/org mà token thuộc về.\n"
            f"Chi tiết: {exc}"
        ) from exc


def ensure_repo(cfg: dict[str, str], user_login: str) -> tuple[str, str]:
    owner = cfg["GITHUB_OWNER"] if cfg["GITHUB_OWNER"] not in {"", "OWNER"} else user_login
    name = cfg["GITHUB_REPOSITORY"]
    repo = f"{owner}/{name}"
    vis = cfg["GITHUB_REPO_VISIBILITY"]
    probe = run_gh(["repo", "view", repo, "--json", "url,nameWithOwner"], cfg["GITHUB_TOKEN"], check=False)
    if probe.returncode == 0:
        data = json.loads(probe.stdout)
        return data["nameWithOwner"], data["url"]
    args = [
        "repo",
        "create",
        repo,
        f"--{vis}" if vis in {"public", "private"} else "--private",
        "--description",
        "StickerKiosk — SWD392 SE1927 Group 6. Kiosk tự phục vụ dán sticker mặt lưng.",
        "--disable-wiki",
    ]
    created = gh_json([*args, "--json", "url,nameWithOwner"], cfg["GITHUB_TOKEN"])
    # older gh may not support --json on create
    if not created:
        run_gh(args, cfg["GITHUB_TOKEN"])
        viewed = gh_json(["repo", "view", repo, "--json", "url,nameWithOwner"], cfg["GITHUB_TOKEN"])
        return viewed["nameWithOwner"], viewed["url"]
    return created["nameWithOwner"], created["url"]


def ensure_labels(repo: str, token: str) -> None:
    existing = gh_json(["label", "list", "--repo", repo, "--limit", "200", "--json", "name"], token) or []
    names = {row["name"] for row in existing}
    for name, color, desc in LABEL_DEFS:
        if name in names:
            run_gh(
                ["label", "edit", name, "--repo", repo, "--color", color, "--description", desc],
                token,
                check=False,
            )
            continue
        run_gh(
            ["label", "create", name, "--repo", repo, "--color", color, "--description", desc],
            token,
        )


def existing_issue_titles(repo: str, token: str) -> dict[str, int]:
    rows = gh_json(
        ["issue", "list", "--repo", repo, "--state", "all", "--limit", "200", "--json", "number,title"],
        token,
    ) or []
    found: dict[str, int] = {}
    for row in rows:
        title = row["title"]
        for item in ISSUES:
            if title.startswith(f"[{item['id']}]"):
                found[item["id"]] = row["number"]
    return found


def create_issues(repo: str, repo_url: str, token: str) -> dict[str, int]:
    mapping = existing_issue_titles(repo, token)
    for item in ISSUES:
        if item["id"] in mapping:
            continue
        body = render_body(item, repo_url)
        labels = ",".join(issue_labels(item))
        proc = run_gh(
            [
                "issue",
                "create",
                "--repo",
                repo,
                "--title",
                item["title"],
                "--body",
                body,
                "--label",
                labels,
            ],
            token,
        )
        # gh prints URL; parse number from last path segment
        url = proc.stdout.strip().splitlines()[-1]
        number = int(url.rstrip("/").split("/")[-1])
        mapping[item["id"]] = number
    return mapping


def graphql(token: str, query: str, variables: dict) -> dict:
    payload = json.dumps({"query": query, "variables": variables})
    env = os.environ.copy()
    if token:
        env["GH_TOKEN"] = token
        env["GITHUB_TOKEN"] = token
    proc = subprocess.run(
        ["gh", "api", "graphql", "--input", "-"],
        input=payload,
        check=True,
        text=True,
        capture_output=True,
        env=env,
    )
    data = json.loads(proc.stdout)
    if data.get("errors"):
        raise RuntimeError(data["errors"])
    return data["data"]


def ensure_project(owner: str, title: str, token: str) -> tuple[str, int, str]:
    query = """
    query($login: String!) {
      user(login: $login) {
        id
        projectsV2(first: 50) { nodes { id number title url } }
      }
      organization(login: $login) {
        id
        projectsV2(first: 50) { nodes { id number title url } }
      }
    }
    """
    env = os.environ.copy()
    env["GH_TOKEN"] = token
    env["GITHUB_TOKEN"] = token
    payload = json.dumps({"query": query, "variables": {"login": owner}})
    proc = subprocess.run(
        ["gh", "api", "graphql", "--input", "-"],
        input=payload,
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )
    data = json.loads(proc.stdout) if proc.stdout else {"data": None, "errors": proc.stderr}
    root = data.get("data") or {}
    container = root.get("user") or root.get("organization")
    if not container:
        # try user then org via gh project list
        listed = run_gh(["project", "list", "--owner", owner, "--limit", "50", "--format", "json"], token, check=False)
        nodes = []
        if listed.returncode == 0 and listed.stdout.strip():
            parsed = json.loads(listed.stdout)
            nodes = parsed if isinstance(parsed, list) else parsed.get("projects", [])
        for node in nodes:
            if node.get("title") == title:
                return str(node["id"]), int(node["number"]), node.get("url", "")
        created = run_gh(
            ["project", "create", "--owner", owner, "--title", title, "--format", "json"],
            token,
        )
        node = json.loads(created.stdout)
        return str(node["id"]), int(node["number"]), node.get("url", "")

    for node in container.get("projectsV2", {}).get("nodes") or []:
        if node["title"] == title:
            return node["id"], int(node["number"]), node["url"]
    owner_id = container["id"]
    mutation = """
    mutation($ownerId: ID!, $title: String!) {
      createProjectV2(input: {ownerId: $ownerId, title: $title}) {
        projectV2 { id number url title }
      }
    }
    """
    created = graphql(token, mutation, {"ownerId": owner_id, "title": title})
    proj = created["createProjectV2"]["projectV2"]
    return proj["id"], int(proj["number"]), proj["url"]


def ensure_project_fields(project_id: str, token: str) -> dict[str, dict]:
    query = """
    query($id: ID!) {
      node(id: $id) {
        ... on ProjectV2 {
          fields(first: 50) {
            nodes {
              ... on ProjectV2Field { id name dataType }
              ... on ProjectV2SingleSelectField {
                id name dataType
                options { id name }
              }
              ... on ProjectV2IterationField { id name dataType }
            }
          }
        }
      }
    }
    """
    data = graphql(token, query, {"id": project_id})
    fields = {}
    for node in data["node"]["fields"]["nodes"]:
        if node:
            fields[node["name"]] = node

    def create_select(name: str, options: list[str]) -> None:
        if name in fields:
            return
        mutation = """
        mutation($projectId: ID!, $name: String!, $options: [ProjectV2SingleSelectFieldOptionInput!]!) {
          createProjectV2Field(input: {
            projectId: $projectId
            dataType: SINGLE_SELECT
            name: $name
            singleSelectOptions: $options
          }) {
            projectV2Field {
              ... on ProjectV2SingleSelectField { id name options { id name } }
            }
          }
        }
        """
        opts = [{"name": opt, "color": "GRAY", "description": opt} for opt in options]
        graphql(token, mutation, {"projectId": project_id, "name": name, "options": opts})

    def create_text(name: str) -> None:
        if name in fields:
            return
        mutation = """
        mutation($projectId: ID!, $name: String!) {
          createProjectV2Field(input: {projectId: $projectId, dataType: TEXT, name: $name}) {
            projectV2Field { ... on ProjectV2Field { id name } }
          }
        }
        """
        graphql(token, mutation, {"projectId": project_id, "name": name})

    def create_date(name: str) -> None:
        if name in fields:
            return
        mutation = """
        mutation($projectId: ID!, $name: String!) {
          createProjectV2Field(input: {projectId: $projectId, dataType: DATE, name: $name}) {
            projectV2Field { ... on ProjectV2Field { id name } }
          }
        }
        """
        graphql(token, mutation, {"projectId": project_id, "name": name})

    # Status often exists as built-in; still ensure custom names from operating model
    create_select("Priority", PRIORITY_OPTIONS)
    create_select("Type", TYPE_OPTIONS)
    create_select("Area", AREA_OPTIONS)
    create_select("Risk", RISK_OPTIONS)
    create_text("Blueprint ID")
    create_text("Iteration")
    create_date("Target date")
    # Owner uses GitHub assignee; Iteration text is enough for MVP
    refreshed = graphql(token, query, {"id": project_id})
    out = {}
    for node in refreshed["node"]["fields"]["nodes"]:
        if node:
            out[node["name"]] = node
    return out


def set_item_fields(
    project_id: str,
    owner: str,
    repo: str,
    mapping: dict[str, int],
    fields: dict[str, dict],
    token: str,
    project_number: int,
) -> None:
    item_list = run_gh(
        [
            "project",
            "item-list",
            str(project_number),
            "--owner",
            owner,
            "--format",
            "json",
            "--limit",
            "200",
        ],
        token,
        check=False,
    )
    if item_list.returncode != 0:
        sys.stderr.write(f"WARN: item-list failed: {item_list.stderr}\n")
        return
    items = json.loads(item_list.stdout)
    nodes = items if isinstance(items, list) else items.get("items", [])
    by_title = {n.get("title"): n for n in nodes}
    id_by_name = {item["id"]: item["title"] for item in ISSUES}

    def option_id(field_name: str, option_name: str) -> str | None:
        field = fields.get(field_name) or {}
        for opt in field.get("options") or []:
            if opt["name"] == option_name:
                return opt["id"]
        return None

    def mutate_select(item_id: str, field_id: str, option: str) -> None:
        mutation = """
        mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
          updateProjectV2ItemFieldValue(input: {
            projectId: $projectId
            itemId: $itemId
            fieldId: $fieldId
            value: { singleSelectOptionId: $optionId }
          }) { projectV2Item { id } }
        }
        """
        graphql(token, mutation, {
            "projectId": project_id,
            "itemId": item_id,
            "fieldId": field_id,
            "optionId": option,
        })

    def mutate_text(item_id: str, field_id: str, text: str) -> None:
        mutation = """
        mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $text: String!) {
          updateProjectV2ItemFieldValue(input: {
            projectId: $projectId
            itemId: $itemId
            fieldId: $fieldId
            value: { text: $text }
          }) { projectV2Item { id } }
        }
        """
        graphql(token, mutation, {
            "projectId": project_id,
            "itemId": item_id,
            "fieldId": field_id,
            "text": text,
        })

    for item in ISSUES:
        node = by_title.get(item["title"])
        if not node:
            continue
        item_id = str(node.get("id") or node.get("itemId") or "")
        if not item_id:
            continue
        for field_name, value in (
            ("Priority", item["priority"]),
            ("Type", item["type"]),
            ("Area", item["area"]),
            ("Risk", item["risk"]),
        ):
            field = fields.get(field_name)
            opt = option_id(field_name, value)
            if field and opt:
                try:
                    mutate_select(item_id, field["id"], opt)
                except RuntimeError as exc:
                    sys.stderr.write(f"WARN: field {field_name} on {item['id']}: {exc}\n")
        bp = fields.get("Blueprint ID")
        it = fields.get("Iteration")
        if bp:
            try:
                mutate_text(item_id, bp["id"], item["id"])
            except RuntimeError as exc:
                sys.stderr.write(f"WARN: Blueprint ID {item['id']}: {exc}\n")
        if it:
            try:
                mutate_text(item_id, it["id"], item["iteration"])
            except RuntimeError as exc:
                sys.stderr.write(f"WARN: Iteration {item['id']}: {exc}\n")
    _ = repo, id_by_name


def print_dry_run(cfg: dict[str, str]) -> None:
    print("GITHUB_PROJECT_DRY_RUN=true — không tạo repo/issue/project.")
    print(f"Planned repository: {cfg['GITHUB_OWNER'] or '<authenticated user>'}/{cfg['GITHUB_REPOSITORY']}")
    print(f"Planned project title: {cfg['GITHUB_PROJECT_TITLE']}")
    print(f"Visibility: {cfg['GITHUB_REPO_VISIBILITY']}")
    print(f"Issues planned: {len(ISSUES)}")
    print("")
    print("| Blueprint ID | Type | Priority | Area | Risk | Iteration | Title |")
    print("|---|---|---|---|---|---|---|")
    for item in ISSUES:
        print(
            f"| {item['id']} | {item['type']} | {item['priority']} | {item['area']} | "
            f"{item['risk']} | {item['iteration']} | {item['title']} |"
        )
    print("")
    print("Project fields to ensure: Status, Priority, Type, Area, Owner (assignee),")
    print("Iteration, Target date, Blueprint ID, Risk.")
    print("Labels: see .github/labels.yml")
    print("Gate 5 blocked until GH_TOKEN or gh auth login.")


def main() -> None:
    cfg = merge_config()
    if is_dry_run(cfg) and not os.environ.get("GITHUB_SYNC_FORCE"):
        print_dry_run(cfg)
        return

    token = cfg["GITHUB_TOKEN"]
    if not token:
        # gh might still have auth
        try:
            user = gh_json(["api", "user"], "")
        except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
            assert_auth("")
            return
    else:
        user = assert_auth(token)

    login = user["login"]
    print(f"Authenticated GitHub user: {login}")
    name_with_owner, repo_url = ensure_repo(cfg, login)
    owner, repo_name = name_with_owner.split("/", 1)
    print(f"Repository: {repo_url}")
    ensure_labels(name_with_owner, cfg["GITHUB_TOKEN"])
    mapping = create_issues(name_with_owner, repo_url, cfg["GITHUB_TOKEN"])
    print(f"Issues upserted: {len(mapping)}")
    project_id, project_number, project_url = ensure_project(
        owner, cfg["GITHUB_PROJECT_TITLE"], cfg["GITHUB_TOKEN"]
    )
    print(f"Project: {project_url or project_id} (#{project_number})")
    fields = ensure_project_fields(project_id, cfg["GITHUB_TOKEN"])
    for blueprint_id, number in mapping.items():
        issue_url = f"https://github.com/{name_with_owner}/issues/{number}"
        add = run_gh(
            [
                "project",
                "item-add",
                str(project_number),
                "--owner",
                owner,
                "--url",
                issue_url,
            ],
            cfg["GITHUB_TOKEN"],
            check=False,
        )
        if add.returncode != 0:
            sys.stderr.write(f"WARN: item-add {blueprint_id}: {add.stderr}\n")
    set_item_fields(
        project_id,
        owner,
        repo_name,
        mapping,
        fields,
        cfg["GITHUB_TOKEN"],
        project_number,
    )
    print("Sync complete.")
    print(f"REPO_URL={repo_url}")
    print(f"PROJECT_URL={project_url}")
    print(f"ISSUE_COUNT={len(mapping)}")
    for blueprint_id, number in sorted(mapping.items()):
        print(f"  {blueprint_id} -> #{number}")


if __name__ == "__main__":
    main()
