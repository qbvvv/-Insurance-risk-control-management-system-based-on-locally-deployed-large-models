"""
系统管理 — 内存存储（无 DATABASE_URL 时使用）。
"""

from datetime import date
from typing import Any, Dict, List, Optional

SYSTEM_USERS: List[Dict[str, Any]] = [
    {
        "id": "1",
        "username": "admin",
        "role": "系统管理员",
        "status": "启用",
        "createdAt": "2026-03-06",
        "updatedAt": "2026-03-06",
    },
    {
        "id": "2",
        "username": "uw_user",
        "role": "承保岗",
        "status": "启用",
        "createdAt": "2026-03-06",
        "updatedAt": "2026-03-06",
    },
]

SYSTEM_PARAMS: List[Dict[str, Any]] = [
    {
        "id": "1",
        "paramKey": "nl_prompt_variant",
        "paramValue": "json_only",
        "description": "自然语言解析 prompt 版本默认值",
        "createdAt": "2026-03-06",
        "updatedAt": "2026-03-06",
    },
    {
        "id": "2",
        "paramKey": "risk_default_level",
        "paramValue": "高",
        "description": "风险等级默认值",
        "createdAt": "2026-03-06",
        "updatedAt": "2026-03-06",
    },
]

SYSTEM_LOGS: List[Dict[str, Any]] = [
    {"id": "1", "logType": "login", "actor": "admin", "action": "登录系统", "createdAt": "2026-03-06"}
]

_next_user_id = 3
_next_param_id = 3
_next_log_id = 2


def list_system_users() -> List[Dict[str, Any]]:
    return list(SYSTEM_USERS)


def get_system_user(user_id: str) -> Optional[Dict[str, Any]]:
    for u in SYSTEM_USERS:
        if str(u.get("id")) == str(user_id):
            return u
    return None


def create_system_user(data: Dict[str, Any]) -> Dict[str, Any]:
    global _next_user_id
    un = (data.get("username") or "").strip()
    if not un:
        raise ValueError("用户名不能为空")
    if any((u.get("username") or "").strip() == un for u in SYSTEM_USERS):
        raise ValueError("用户名已存在")
    item = dict(data)
    item["username"] = un
    item.setdefault("id", str(_next_user_id))
    today = date.today().isoformat()
    item.setdefault("createdAt", item.get("createdAt") or today)
    item.setdefault("updatedAt", item.get("updatedAt") or today)
    SYSTEM_USERS.append(item)
    _next_user_id += 1
    return item


def update_system_user(user_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    for idx, u in enumerate(SYSTEM_USERS):
        if str(u.get("id")) == str(user_id):
            updated = dict(u)
            updated.update(data)
            updated["id"] = str(user_id)
            updated["updatedAt"] = date.today().isoformat()
            SYSTEM_USERS[idx] = updated
            return updated
    return None


def delete_system_user(user_id: str) -> bool:
    for idx, u in enumerate(SYSTEM_USERS):
        if str(u.get("id")) == str(user_id):
            SYSTEM_USERS.pop(idx)
            return True
    return False


def list_system_params() -> List[Dict[str, Any]]:
    return list(SYSTEM_PARAMS)


def get_system_param(param_id: str) -> Optional[Dict[str, Any]]:
    for p in SYSTEM_PARAMS:
        if str(p.get("id")) == str(param_id):
            return p
    return None


def create_system_param(data: Dict[str, Any]) -> Dict[str, Any]:
    global _next_param_id
    key = (data.get("paramKey") or "").strip()
    if not key:
        raise ValueError("参数键不能为空")
    if any((p.get("paramKey") or "").strip() == key for p in SYSTEM_PARAMS):
        raise ValueError("参数键已存在")
    item = dict(data)
    item["paramKey"] = key
    item.setdefault("id", str(_next_param_id))
    today = date.today().isoformat()
    item.setdefault("createdAt", item.get("createdAt") or today)
    item.setdefault("updatedAt", item.get("updatedAt") or today)
    SYSTEM_PARAMS.append(item)
    _next_param_id += 1
    return item


def update_system_param(param_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    for idx, p in enumerate(SYSTEM_PARAMS):
        if str(p.get("id")) == str(param_id):
            updated = dict(p)
            updated.update(data)
            updated["id"] = str(param_id)
            updated["updatedAt"] = date.today().isoformat()
            SYSTEM_PARAMS[idx] = updated
            return updated
    return None


def delete_system_param(param_id: str) -> bool:
    for idx, p in enumerate(SYSTEM_PARAMS):
        if str(p.get("id")) == str(param_id):
            SYSTEM_PARAMS.pop(idx)
            return True
    return False


def list_system_logs(limit: int = 100) -> List[Dict[str, Any]]:
    rows = list(SYSTEM_LOGS)
    return rows[: max(0, int(limit))]


def create_system_log(data: Dict[str, Any]) -> Dict[str, Any]:
    global _next_log_id
    item = dict(data)
    item.setdefault("id", str(_next_log_id))
    item.setdefault("logType", item.get("logType") or "info")
    item.setdefault("actor", item.get("actor") or "system")
    item.setdefault("action", item.get("action") or "")
    item.setdefault("createdAt", item.get("createdAt") or date.today().isoformat())
    SYSTEM_LOGS.insert(0, item)
    _next_log_id += 1
    return item

