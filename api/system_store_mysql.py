"""
系统管理 — MySQL 版存储实现。
"""

from datetime import date
from typing import Any, Dict, List, Optional

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from api.database import get_session_factory
from api.orm_models import SystemLog, SystemParam, SystemUser


def _session() -> Session:
    return get_session_factory()()


def seed_system_demo_data_if_empty() -> None:
    db = _session()
    try:
        cnt = int(db.scalar(select(func.count()).select_from(SystemUser)) or 0)
        if cnt > 0:
            return
        today = date.today().isoformat()
        db.add_all(
            [
                SystemUser(username="admin", role="系统管理员", status="启用", created_at=today, updated_at=today),
                SystemUser(username="uw_user", role="承保岗", status="启用", created_at=today, updated_at=today),
                SystemParam(
                    param_key="nl_prompt_variant",
                    param_value="json_only",
                    description="自然语言解析 prompt 版本默认值",
                    created_at=today,
                    updated_at=today,
                ),
                SystemParam(
                    param_key="risk_default_level",
                    param_value="高",
                    description="风险等级默认值",
                    created_at=today,
                    updated_at=today,
                ),
                SystemLog(log_type="login", actor="admin", action="登录系统", created_at=today),
            ]
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def list_system_users() -> List[Dict[str, Any]]:
    db = _session()
    try:
        rows = db.scalars(select(SystemUser).order_by(SystemUser.id.desc())).all()
        return [
            {
                "id": str(u.id),
                "username": u.username,
                "role": u.role,
                "status": u.status,
                "createdAt": u.created_at or "",
                "updatedAt": u.updated_at or "",
            }
            for u in rows
        ]
    finally:
        db.close()


def get_system_user(user_id: str) -> Optional[Dict[str, Any]]:
    db = _session()
    try:
        u = db.get(SystemUser, int(user_id))
        if not u:
            return None
        return {
            "id": str(u.id),
            "username": u.username,
            "role": u.role,
            "status": u.status,
            "createdAt": u.created_at or "",
            "updatedAt": u.updated_at or "",
        }
    except ValueError:
        return None
    finally:
        db.close()


def create_system_user(data: Dict[str, Any]) -> Dict[str, Any]:
    db = _session()
    try:
        today = date.today().isoformat()
        row = SystemUser(
            username=data["username"],
            role=data.get("role") or "",
            status=data.get("status") or "启用",
            created_at=data.get("createdAt") or today,
            updated_at=data.get("updatedAt") or today,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return get_system_user(str(row.id)) or {}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def update_system_user(user_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    db = _session()
    try:
        u = db.get(SystemUser, int(user_id))
        if not u:
            return None
        for k in ("role", "status"):
            if k in data and data[k] is not None:
                setattr(u, k, data[k])
        u.updated_at = date.today().isoformat()
        db.commit()
        db.refresh(u)
        return get_system_user(user_id)
    except ValueError:
        return None
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def delete_system_user(user_id: str) -> bool:
    db = _session()
    try:
        u = db.get(SystemUser, int(user_id))
        if not u:
            return False
        db.delete(u)
        db.commit()
        return True
    except ValueError:
        return False
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def list_system_params() -> List[Dict[str, Any]]:
    db = _session()
    try:
        rows = db.scalars(select(SystemParam).order_by(SystemParam.id.desc())).all()
        return [
            {
                "id": str(p.id),
                "paramKey": p.param_key,
                "paramValue": p.param_value,
                "description": p.description,
                "createdAt": p.created_at or "",
                "updatedAt": p.updated_at or "",
            }
            for p in rows
        ]
    finally:
        db.close()


def get_system_param(param_id: str) -> Optional[Dict[str, Any]]:
    db = _session()
    try:
        p = db.get(SystemParam, int(param_id))
        if not p:
            return None
        return {
            "id": str(p.id),
            "paramKey": p.param_key,
            "paramValue": p.param_value,
            "description": p.description,
            "createdAt": p.created_at or "",
            "updatedAt": p.updated_at or "",
        }
    except ValueError:
        return None
    finally:
        db.close()


def create_system_param(data: Dict[str, Any]) -> Dict[str, Any]:
    db = _session()
    try:
        today = date.today().isoformat()
        row = SystemParam(
            param_key=data["paramKey"],
            param_value=data.get("paramValue") or "",
            description=data.get("description") or "",
            created_at=data.get("createdAt") or today,
            updated_at=data.get("updatedAt") or today,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return get_system_param(str(row.id)) or {}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def update_system_param(param_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    db = _session()
    try:
        p = db.get(SystemParam, int(param_id))
        if not p:
            return None
        if data.get("paramValue") is not None:
            p.param_value = data["paramValue"]
        if data.get("description") is not None:
            p.description = data["description"]
        p.updated_at = date.today().isoformat()
        db.commit()
        db.refresh(p)
        return get_system_param(param_id)
    except ValueError:
        return None
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def delete_system_param(param_id: str) -> bool:
    db = _session()
    try:
        p = db.get(SystemParam, int(param_id))
        if not p:
            return False
        db.delete(p)
        db.commit()
        return True
    except ValueError:
        return False
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def list_system_logs(limit: int = 100) -> List[Dict[str, Any]]:
    db = _session()
    try:
        rows = db.scalars(select(SystemLog).order_by(SystemLog.id.desc()).limit(int(limit))).all()
        return [
            {
                "id": str(l.id),
                "logType": l.log_type,
                "actor": l.actor,
                "action": l.action,
                "createdAt": l.created_at or "",
            }
            for l in rows
        ]
    finally:
        db.close()


def create_system_log(data: Dict[str, Any]) -> Dict[str, Any]:
    db = _session()
    try:
        today = date.today().isoformat()
        row = SystemLog(
            log_type=data.get("logType") or "info",
            actor=data.get("actor") or "system",
            action=data.get("action") or "",
            created_at=data.get("createdAt") or today,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return {
            "id": str(row.id),
            "logType": row.log_type,
            "actor": row.actor,
            "action": row.action,
            "createdAt": row.created_at or "",
        }
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

