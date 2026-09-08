"""
财务管理 — MySQL 版存储实现。
"""

from datetime import date
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from api.database import get_session_factory
from api.orm_models import CommissionSettlement, PremiumFlow


def _session() -> Session:
    return get_session_factory()()


def allocate_premium_flow_no() -> str:
    db = _session()
    try:
        d = date.today().strftime("%Y%m%d")
        prefix = f"PF{d}"
        cnt = int(
            db.scalar(
                select(func.count()).select_from(PremiumFlow).where(PremiumFlow.flow_no.like(f"{prefix}%"))
            )
            or 0
        )
        return f"{prefix}{cnt + 1:04d}"
    finally:
        db.close()


def allocate_commission_settlement_no() -> str:
    db = _session()
    try:
        d = date.today().strftime("%Y%m%d")
        prefix = f"CM{d}"
        cnt = int(
            db.scalar(
                select(func.count())
                .select_from(CommissionSettlement)
                .where(CommissionSettlement.settlement_no.like(f"{prefix}%"))
            )
            or 0
        )
        return f"{prefix}{cnt + 1:04d}"
    finally:
        db.close()


def _premium_flow_to_dict(p: PremiumFlow) -> Dict[str, Any]:
    return {
        "id": str(p.id),
        "flowNo": p.flow_no,
        "flowType": p.flow_type,
        "policyNo": p.policy_no,
        "amount": p.amount,
        "payMethod": p.pay_method,
        "status": p.status,
        "remark": p.remark,
        "createdAt": p.created_at or "",
        "updatedAt": p.updated_at or "",
    }


def list_premium_flows() -> List[Dict[str, Any]]:
    db = _session()
    try:
        rows = db.scalars(select(PremiumFlow).order_by(PremiumFlow.id.desc())).all()
        return [_premium_flow_to_dict(p) for p in rows]
    finally:
        db.close()


def get_premium_flow(flow_id: str) -> Optional[Dict[str, Any]]:
    db = _session()
    try:
        p = db.get(PremiumFlow, int(flow_id))
        return _premium_flow_to_dict(p) if p else None
    except ValueError:
        return None
    finally:
        db.close()


def create_premium_flow(data: Dict[str, Any]) -> Dict[str, Any]:
    db = _session()
    try:
        item = dict(data)
        today = date.today().isoformat()
        row = PremiumFlow(
            flow_no=item.get("flowNo") or allocate_premium_flow_no(),
            flow_type=item["flowType"],
            policy_no=item["policyNo"],
            amount=str(item.get("amount", "0")),
            pay_method=item.get("payMethod") or "",
            status=item.get("status") or "",
            remark=item.get("remark") or "",
            created_at=item.get("createdAt") or today,
            updated_at=item.get("updatedAt") or today,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return _premium_flow_to_dict(row)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def update_premium_flow(flow_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    db = _session()
    try:
        p = db.get(PremiumFlow, int(flow_id))
        if not p:
            return None
        key_map = {
            "flowNo": "flow_no",
            "flowType": "flow_type",
            "policyNo": "policy_no",
            "amount": "amount",
            "payMethod": "pay_method",
            "status": "status",
            "remark": "remark",
            "createdAt": "created_at",
            "updatedAt": "updated_at",
        }
        for k, v in data.items():
            if v is None:
                continue
            col = key_map.get(k)
            if col is not None:
                setattr(p, col, str(v) if k == "amount" else v)
        p.updated_at = date.today().isoformat()
        db.commit()
        db.refresh(p)
        return _premium_flow_to_dict(p)
    except ValueError:
        return None
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def delete_premium_flow(flow_id: str) -> bool:
    db = _session()
    try:
        p = db.get(PremiumFlow, int(flow_id))
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


def _commission_settlement_to_dict(c: CommissionSettlement) -> Dict[str, Any]:
    return {
        "id": str(c.id),
        "settlementNo": c.settlement_no,
        "channelName": c.channel_name,
        "channelCode": c.channel_code,
        "period": c.period,
        "commissionAmount": c.commission_amount,
        "reconcileStatus": c.reconcile_status,
        "remark": c.remark,
        "createdAt": c.created_at or "",
        "updatedAt": c.updated_at or "",
    }


def list_commission_settlements() -> List[Dict[str, Any]]:
    db = _session()
    try:
        rows = db.scalars(select(CommissionSettlement).order_by(CommissionSettlement.id.desc())).all()
        return [_commission_settlement_to_dict(c) for c in rows]
    finally:
        db.close()


def get_commission_settlement(settlement_id: str) -> Optional[Dict[str, Any]]:
    db = _session()
    try:
        c = db.get(CommissionSettlement, int(settlement_id))
        return _commission_settlement_to_dict(c) if c else None
    except ValueError:
        return None
    finally:
        db.close()


def create_commission_settlement(data: Dict[str, Any]) -> Dict[str, Any]:
    db = _session()
    try:
        item = dict(data)
        today = date.today().isoformat()
        row = CommissionSettlement(
            settlement_no=item.get("settlementNo") or allocate_commission_settlement_no(),
            channel_name=item["channelName"],
            channel_code=item.get("channelCode") or "",
            period=item.get("period") or "",
            commission_amount=str(item.get("commissionAmount", "0")),
            reconcile_status=item.get("reconcileStatus") or "",
            remark=item.get("remark") or "",
            created_at=item.get("createdAt") or today,
            updated_at=item.get("updatedAt") or today,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return _commission_settlement_to_dict(row)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def update_commission_settlement(settlement_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    db = _session()
    try:
        c = db.get(CommissionSettlement, int(settlement_id))
        if not c:
            return None
        key_map = {
            "settlementNo": "settlement_no",
            "channelName": "channel_name",
            "channelCode": "channel_code",
            "period": "period",
            "commissionAmount": "commission_amount",
            "reconcileStatus": "reconcile_status",
            "remark": "remark",
            "createdAt": "created_at",
            "updatedAt": "updated_at",
        }
        for k, v in data.items():
            if v is None:
                continue
            col = key_map.get(k)
            if col is not None:
                setattr(c, col, str(v) if k == "commissionAmount" else v)
        c.updated_at = date.today().isoformat()
        db.commit()
        db.refresh(c)
        return _commission_settlement_to_dict(c)
    except ValueError:
        return None
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def delete_commission_settlement(settlement_id: str) -> bool:
    db = _session()
    try:
        c = db.get(CommissionSettlement, int(settlement_id))
        if not c:
            return False
        db.delete(c)
        db.commit()
        return True
    except ValueError:
        return False
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

