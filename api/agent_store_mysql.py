"""
代理人/团队管理 — MySQL 版存储实现。
"""

from datetime import date
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from api.database import get_session_factory
from api.orm_models import Agent, AgentPerformance, AgentTeam


def _session() -> Session:
    return get_session_factory()()


def seed_agent_demo_data_if_empty() -> None:
    db = _session()
    try:
        team_cnt = db.scalar(select(func.count()).select_from(AgentTeam)) or 0
        if int(team_cnt) > 0:
            return

        today = date.today().isoformat()
        teams = [
            AgentTeam(team_no="TM20260306001", name="王总监团队", title="营销总监", parent_team_no="", created_at=today, updated_at=today),
            AgentTeam(team_no="TM20260306002", name="李经理团队", title="营业部经理", parent_team_no="TM20260306001", created_at=today, updated_at=today),
            AgentTeam(team_no="TM20260306003", name="张主管", title="营业部主管", parent_team_no="TM20260306002", created_at=today, updated_at=today),
        ]
        db.add_all(teams)
        db.commit()

        agents = [
            Agent(agent_no="AG20260306001", name="王总监", id_no="", phone="", team_no="TM20260306001", title="营销总监", status="在职", created_at=today, updated_at=today),
            Agent(agent_no="AG20260306002", name="李经理", id_no="", phone="", team_no="TM20260306002", title="营业部经理", status="在职", created_at=today, updated_at=today),
            Agent(agent_no="AG20260306003", name="张主管", id_no="", phone="", team_no="TM20260306003", title="营业部主管", status="在职", created_at=today, updated_at=today),
        ]
        db.add_all(agents)
        db.commit()

        perfs = [
            AgentPerformance(perf_no="AP20260306001", owner_type="team", owner_no="TM20260306001", period="2026Q1", premium_wan="580", kpi_rate="112%", created_at=today, updated_at=today),
            AgentPerformance(perf_no="AP20260306002", owner_type="team", owner_no="TM20260306002", period="2026Q1", premium_wan="320", kpi_rate="96%", created_at=today, updated_at=today),
            AgentPerformance(perf_no="AP20260306003", owner_type="agent", owner_no="AG20260306003", period="2026Q1", premium_wan="120", kpi_rate="88%", created_at=today, updated_at=today),
        ]
        db.add_all(perfs)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def allocate_agent_team_no() -> str:
    db = _session()
    try:
        d = date.today().strftime("%Y%m%d")
        prefix = f"TM{d}"
        cnt = int(db.scalar(select(func.count()).select_from(AgentTeam).where(AgentTeam.team_no.like(f"{prefix}%"))) or 0)
        return f"{prefix}{cnt + 1:04d}"
    finally:
        db.close()


def allocate_agent_no() -> str:
    db = _session()
    try:
        d = date.today().strftime("%Y%m%d")
        prefix = f"AG{d}"
        cnt = int(db.scalar(select(func.count()).select_from(Agent).where(Agent.agent_no.like(f"{prefix}%"))) or 0)
        return f"{prefix}{cnt + 1:04d}"
    finally:
        db.close()


def allocate_agent_performance_no() -> str:
    db = _session()
    try:
        d = date.today().strftime("%Y%m%d")
        prefix = f"AP{d}"
        cnt = int(db.scalar(select(func.count()).select_from(AgentPerformance).where(AgentPerformance.perf_no.like(f"{prefix}%"))) or 0)
        return f"{prefix}{cnt + 1:04d}"
    finally:
        db.close()


def list_agent_teams() -> List[Dict[str, Any]]:
    db = _session()
    try:
        rows = db.scalars(select(AgentTeam).order_by(AgentTeam.id.desc())).all()
        team_no_to_name = {t.team_no: t.name for t in rows}
        out: List[Dict[str, Any]] = []
        for t in rows:
            parent_no = t.parent_team_no or ""
            parent_name = team_no_to_name.get(parent_no, "-") if parent_no else "-"
            out.append(
                {
                    "id": str(t.id),
                    "teamNo": t.team_no,
                    "name": t.name,
                    "title": t.title,
                    "parentTeamNo": parent_no,
                    "parent": parent_name,
                    "createdAt": t.created_at or "",
                    "updatedAt": t.updated_at or "",
                }
            )
        return out
    finally:
        db.close()


def get_agent_team(team_id: str) -> Optional[Dict[str, Any]]:
    db = _session()
    try:
        t = db.get(AgentTeam, int(team_id))
        if not t:
            return None
        team_rows = db.scalars(select(AgentTeam)).all()
        team_no_to_name = {x.team_no: x.name for x in team_rows}
        parent_no = t.parent_team_no or ""
        parent_name = team_no_to_name.get(parent_no, "-") if parent_no else "-"
        return {
            "id": str(t.id),
            "teamNo": t.team_no,
            "name": t.name,
            "title": t.title,
            "parentTeamNo": parent_no,
            "parent": parent_name,
            "createdAt": t.created_at or "",
            "updatedAt": t.updated_at or "",
        }
    except ValueError:
        return None
    finally:
        db.close()


def create_agent_team(data: Dict[str, Any]) -> Dict[str, Any]:
    db = _session()
    try:
        today = date.today().isoformat()
        row = AgentTeam(
            team_no=(data.get("teamNo") or "").strip() or allocate_agent_team_no(),
            name=data["name"],
            title=data.get("title") or "",
            parent_team_no=data.get("parentTeamNo") or "",
            created_at=data.get("createdAt") or today,
            updated_at=data.get("updatedAt") or today,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return get_agent_team(str(row.id)) or {}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def update_agent_team(team_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    db = _session()
    try:
        t = db.get(AgentTeam, int(team_id))
        if not t:
            return None
        key_map = {
            "teamNo": "team_no",
            "name": "name",
            "title": "title",
            "parentTeamNo": "parent_team_no",
            "createdAt": "created_at",
            "updatedAt": "updated_at",
        }
        for k, v in data.items():
            if v is None:
                continue
            col = key_map.get(k)
            if col is not None:
                setattr(t, col, v)
        t.updated_at = date.today().isoformat()
        db.commit()
        db.refresh(t)
        return get_agent_team(team_id)
    except ValueError:
        return None
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def delete_agent_team(team_id: str) -> bool:
    db = _session()
    try:
        t = db.get(AgentTeam, int(team_id))
        if not t:
            return False
        db.delete(t)
        db.commit()
        return True
    except ValueError:
        return False
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def list_agents() -> List[Dict[str, Any]]:
    db = _session()
    try:
        rows = db.scalars(select(Agent).order_by(Agent.id.desc())).all()
        return [
            {
                "id": str(a.id),
                "agentNo": a.agent_no,
                "name": a.name,
                "idNo": a.id_no,
                "phone": a.phone,
                "teamNo": a.team_no,
                "title": a.title,
                "status": a.status,
                "createdAt": a.created_at or "",
                "updatedAt": a.updated_at or "",
            }
            for a in rows
        ]
    finally:
        db.close()


def get_agent(agent_id: str) -> Optional[Dict[str, Any]]:
    db = _session()
    try:
        a = db.get(Agent, int(agent_id))
        if not a:
            return None
        return {
            "id": str(a.id),
            "agentNo": a.agent_no,
            "name": a.name,
            "idNo": a.id_no,
            "phone": a.phone,
            "teamNo": a.team_no,
            "title": a.title,
            "status": a.status,
            "createdAt": a.created_at or "",
            "updatedAt": a.updated_at or "",
        }
    except ValueError:
        return None
    finally:
        db.close()


def create_agent(data: Dict[str, Any]) -> Dict[str, Any]:
    db = _session()
    try:
        today = date.today().isoformat()
        row = Agent(
            agent_no=(data.get("agentNo") or "").strip() or allocate_agent_no(),
            name=data["name"],
            id_no=data.get("idNo") or "",
            phone=data.get("phone") or "",
            team_no=data.get("teamNo") or "",
            title=data.get("title") or "",
            status=data.get("status") or "在职",
            created_at=data.get("createdAt") or today,
            updated_at=data.get("updatedAt") or today,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return get_agent(str(row.id)) or {}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def update_agent(agent_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    db = _session()
    try:
        a = db.get(Agent, int(agent_id))
        if not a:
            return None
        key_map = {
            "agentNo": "agent_no",
            "name": "name",
            "idNo": "id_no",
            "phone": "phone",
            "teamNo": "team_no",
            "title": "title",
            "status": "status",
            "createdAt": "created_at",
            "updatedAt": "updated_at",
        }
        for k, v in data.items():
            if v is None:
                continue
            col = key_map.get(k)
            if col is not None:
                setattr(a, col, v)
        a.updated_at = date.today().isoformat()
        db.commit()
        db.refresh(a)
        return get_agent(agent_id)
    except ValueError:
        return None
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def delete_agent(agent_id: str) -> bool:
    db = _session()
    try:
        a = db.get(Agent, int(agent_id))
        if not a:
            return False
        db.delete(a)
        db.commit()
        return True
    except ValueError:
        return False
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_agent_performance_summary(period: str = "") -> List[Dict[str, Any]]:
    db = _session()
    try:
        if not period:
            period = db.scalar(select(func.max(AgentPerformance.period)).where(AgentPerformance.period != "")) or ""
        if not period:
            return []

        teams = db.scalars(select(AgentTeam)).all()
        agents = db.scalars(select(Agent)).all()
        team_map = {t.team_no: t.name for t in teams}
        agent_map = {a.agent_no: a.name for a in agents}

        perf_rows = db.scalars(select(AgentPerformance).where(AgentPerformance.period == period).order_by(AgentPerformance.id.desc())).all()
        out: List[Dict[str, Any]] = []
        for p in perf_rows:
            if p.owner_type == "agent":
                name = agent_map.get(p.owner_no, p.owner_no)
            else:
                name = team_map.get(p.owner_no, p.owner_no)
            out.append({"name": name, "premium": p.premium_wan, "rate": p.kpi_rate, "period": p.period})
        return out
    finally:
        db.close()

