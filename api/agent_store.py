"""
代理人/团队管理 — 内存存储（无 DATABASE_URL 时使用）。
"""

from datetime import date
from typing import Any, Dict, List, Optional

AGENT_TEAMS: List[Dict[str, Any]] = [
    {
        "id": "1",
        "teamNo": "TM20260306001",
        "name": "王总监团队",
        "title": "营销总监",
        "parentTeamNo": "",
        "createdAt": "2026-03-06",
        "updatedAt": "2026-03-06",
    },
    {
        "id": "2",
        "teamNo": "TM20260306002",
        "name": "李经理团队",
        "title": "营业部经理",
        "parentTeamNo": "TM20260306001",
        "createdAt": "2026-03-06",
        "updatedAt": "2026-03-06",
    },
    {
        "id": "3",
        "teamNo": "TM20260306003",
        "name": "张主管",
        "title": "营业部主管",
        "parentTeamNo": "TM20260306002",
        "createdAt": "2026-03-06",
        "updatedAt": "2026-03-06",
    },
]

AGENTS: List[Dict[str, Any]] = [
    {
        "id": "1",
        "agentNo": "AG20260306001",
        "name": "王总监",
        "idNo": "110101198401012026",
        "phone": "13800012026",
        "teamNo": "TM20260306001",
        "title": "营销总监",
        "status": "在职",
        "createdAt": "2026-03-06",
        "updatedAt": "2026-03-06",
    },
    {
        "id": "2",
        "agentNo": "AG20260306002",
        "name": "李经理",
        "idNo": "310101198503022026",
        "phone": "13900022026",
        "teamNo": "TM20260306002",
        "title": "营业部经理",
        "status": "在职",
        "createdAt": "2026-03-06",
        "updatedAt": "2026-03-06",
    },
    {
        "id": "3",
        "agentNo": "AG20260306003",
        "name": "张主管",
        "idNo": "440106198612032026",
        "phone": "13700032026",
        "teamNo": "TM20260306003",
        "title": "营业部主管",
        "status": "在职",
        "createdAt": "2026-03-06",
        "updatedAt": "2026-03-06",
    },
]

AGENT_PERFORMANCES: List[Dict[str, Any]] = [
    {
        "id": "1",
        "perfNo": "AP20260306001",
        "ownerType": "team",
        "ownerNo": "TM20260306001",
        "period": "2026Q1",
        "premiumWan": "580",
        "kpiRate": "112%",
        "createdAt": "2026-03-06",
        "updatedAt": "2026-03-06",
    },
    {
        "id": "2",
        "perfNo": "AP20260306002",
        "ownerType": "team",
        "ownerNo": "TM20260306002",
        "period": "2026Q1",
        "premiumWan": "320",
        "kpiRate": "96%",
        "createdAt": "2026-03-06",
        "updatedAt": "2026-03-06",
    },
    {
        "id": "3",
        "perfNo": "AP20260306003",
        "ownerType": "agent",
        "ownerNo": "AG20260306003",
        "period": "2026Q1",
        "premiumWan": "120",
        "kpiRate": "88%",
        "createdAt": "2026-03-06",
        "updatedAt": "2026-03-06",
    },
]

_next_team_id = 4
_next_agent_id = 4


def _allocate_team_no(rows: List[Dict[str, Any]]) -> str:
    d = date.today().strftime("%Y%m%d")
    prefix = f"TM{d}"
    n = sum(1 for r in rows if str(r.get("teamNo", "")).startswith(prefix))
    return f"{prefix}{n + 1:04d}"


def _allocate_agent_no(rows: List[Dict[str, Any]]) -> str:
    d = date.today().strftime("%Y%m%d")
    prefix = f"AG{d}"
    n = sum(1 for r in rows if str(r.get("agentNo", "")).startswith(prefix))
    return f"{prefix}{n + 1:04d}"


def _team_no_to_name() -> Dict[str, str]:
    return {str(t["teamNo"]): str(t["name"]) for t in AGENT_TEAMS}


def allocate_agent_team_no() -> str:
    return _allocate_team_no(AGENT_TEAMS)


def allocate_agent_no() -> str:
    return _allocate_agent_no(AGENTS)


def allocate_agent_performance_no() -> str:
    d = date.today().strftime("%Y%m%d")
    prefix = f"AP{d}"
    n = sum(1 for r in AGENT_PERFORMANCES if str(r.get("perfNo", "")).startswith(prefix))
    return f"{prefix}{n + 1:04d}"


def list_agent_teams() -> List[Dict[str, Any]]:
    m = _team_no_to_name()
    out: List[Dict[str, Any]] = []
    for t in AGENT_TEAMS:
        parent_no = t.get("parentTeamNo", "") or ""
        parent_name = m.get(parent_no, "-") if parent_no else "-"
        out.append({**t, "parent": parent_name})
    return out


def get_agent_team(team_id: str) -> Optional[Dict[str, Any]]:
    m = _team_no_to_name()
    for t in AGENT_TEAMS:
        if str(t.get("id")) == str(team_id):
            parent_no = t.get("parentTeamNo", "") or ""
            parent_name = m.get(parent_no, "-") if parent_no else "-"
            return {**t, "parent": parent_name}
    return None


def create_agent_team(data: Dict[str, Any]) -> Dict[str, Any]:
    global _next_team_id
    item = dict(data)
    item.setdefault("id", str(_next_team_id))
    if not (item.get("teamNo") or "").strip():
        item["teamNo"] = allocate_agent_team_no()
    item.setdefault("title", "")
    item.setdefault("parentTeamNo", "")
    today = date.today().isoformat()
    item.setdefault("createdAt", today)
    item.setdefault("updatedAt", today)
    _next_team_id += 1
    AGENT_TEAMS.append(item)
    return get_agent_team(item["id"]) or item


def update_agent_team(team_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    for idx, t in enumerate(AGENT_TEAMS):
        if str(t.get("id")) == str(team_id):
            updated = dict(t)
            updated.update(data)
            updated["id"] = str(team_id)
            updated["updatedAt"] = date.today().isoformat()
            AGENT_TEAMS[idx] = updated
            return get_agent_team(team_id)
    return None


def delete_agent_team(team_id: str) -> bool:
    for idx, t in enumerate(AGENT_TEAMS):
        if str(t.get("id")) == str(team_id):
            AGENT_TEAMS.pop(idx)
            return True
    return False


def list_agents() -> List[Dict[str, Any]]:
    return list(AGENTS)


def get_agent(agent_id: str) -> Optional[Dict[str, Any]]:
    for a in AGENTS:
        if str(a.get("id")) == str(agent_id):
            return a
    return None


def create_agent(data: Dict[str, Any]) -> Dict[str, Any]:
    global _next_agent_id
    item = dict(data)
    item.setdefault("id", str(_next_agent_id))
    if not (item.get("agentNo") or "").strip():
        item["agentNo"] = allocate_agent_no()
    item.setdefault("idNo", "")
    item.setdefault("phone", "")
    item.setdefault("teamNo", "")
    item.setdefault("title", "")
    item.setdefault("status", "在职")
    today = date.today().isoformat()
    item.setdefault("createdAt", today)
    item.setdefault("updatedAt", today)
    _next_agent_id += 1
    AGENTS.append(item)
    return item


def update_agent(agent_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    for idx, a in enumerate(AGENTS):
        if str(a.get("id")) == str(agent_id):
            updated = dict(a)
            updated.update(data)
            updated["id"] = str(agent_id)
            updated["updatedAt"] = date.today().isoformat()
            AGENTS[idx] = updated
            return updated
    return None


def delete_agent(agent_id: str) -> bool:
    for idx, a in enumerate(AGENTS):
        if str(a.get("id")) == str(agent_id):
            AGENTS.pop(idx)
            return True
    return False


def get_agent_performance_summary(period: str = "") -> List[Dict[str, Any]]:
    if not period:
        ps = [p.get("period", "") for p in AGENT_PERFORMANCES if p.get("period")]
        period = max(ps) if ps else ""

    team_map = _team_no_to_name()
    agent_map = {str(a["agentNo"]): str(a["name"]) for a in AGENTS}

    rows = [p for p in AGENT_PERFORMANCES if p.get("period") == period]
    out: List[Dict[str, Any]] = []
    for r in rows:
        owner_type = r.get("ownerType", "team")
        owner_no = r.get("ownerNo", "")
        if owner_type == "agent":
            name = agent_map.get(owner_no, owner_no)
        else:
            name = team_map.get(owner_no, owner_no)
        out.append(
            {
                "name": name,
                "premium": r.get("premiumWan", "0"),
                "rate": r.get("kpiRate", "0%"),
                "period": r.get("period", ""),
            }
        )
    return out

