"""
再保管理 — MySQL 版存储实现。
"""

from datetime import date
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from api.database import get_session_factory
from api.orm_models import ReinsuranceBill, ReinsuranceContract


def _session() -> Session:
    return get_session_factory()()


def allocate_reinsurance_contract_no() -> str:
    db = _session()
    try:
        d = date.today().strftime("%Y%m%d")
        prefix = f"RC{d}"
        cnt = int(
            db.scalar(
                select(func.count())
                .select_from(ReinsuranceContract)
                .where(ReinsuranceContract.contract_no.like(f"{prefix}%"))
            )
            or 0
        )
        return f"{prefix}{cnt + 1:04d}"
    finally:
        db.close()


def allocate_reinsurance_bill_no() -> str:
    db = _session()
    try:
        d = date.today().strftime("%Y%m%d")
        prefix = f"RB{d}"
        cnt = int(
            db.scalar(
                select(func.count())
                .select_from(ReinsuranceBill)
                .where(ReinsuranceBill.bill_no.like(f"{prefix}%"))
            )
            or 0
        )
        return f"{prefix}{cnt + 1:04d}"
    finally:
        db.close()


def _reinsurance_contract_to_dict(r: ReinsuranceContract) -> Dict[str, Any]:
    return {
        "id": str(r.id),
        "contractNo": r.contract_no,
        "contractType": r.contract_type,
        "cedent": r.cedent,
        "reinsurer": r.reinsurer,
        "status": r.status,
        "remark": r.remark,
        "createdAt": r.created_at or "",
        "updatedAt": r.updated_at or "",
    }


def list_reinsurance_contracts() -> List[Dict[str, Any]]:
    db = _session()
    try:
        rows = db.scalars(select(ReinsuranceContract).order_by(ReinsuranceContract.id.desc())).all()
        return [_reinsurance_contract_to_dict(r) for r in rows]
    finally:
        db.close()


def get_reinsurance_contract(contract_id: str) -> Optional[Dict[str, Any]]:
    db = _session()
    try:
        r = db.get(ReinsuranceContract, int(contract_id))
        return _reinsurance_contract_to_dict(r) if r else None
    except ValueError:
        return None
    finally:
        db.close()


def create_reinsurance_contract(data: Dict[str, Any]) -> Dict[str, Any]:
    db = _session()
    try:
        item = dict(data)
        today = date.today().isoformat()
        row = ReinsuranceContract(
            contract_no=item.get("contractNo") or allocate_reinsurance_contract_no(),
            contract_type=item.get("contractType") or "",
            cedent=item.get("cedent") or "",
            reinsurer=item.get("reinsurer") or "",
            status=item.get("status") or "生效",
            remark=item.get("remark") or "",
            created_at=item.get("createdAt") or today,
            updated_at=item.get("updatedAt") or today,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return _reinsurance_contract_to_dict(row)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def update_reinsurance_contract(contract_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    db = _session()
    try:
        r = db.get(ReinsuranceContract, int(contract_id))
        if not r:
            return None
        key_map = {
            "contractNo": "contract_no",
            "contractType": "contract_type",
            "cedent": "cedent",
            "reinsurer": "reinsurer",
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
                setattr(r, col, v)
        r.updated_at = date.today().isoformat()
        db.commit()
        db.refresh(r)
        return _reinsurance_contract_to_dict(r)
    except ValueError:
        return None
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def delete_reinsurance_contract(contract_id: str) -> bool:
    db = _session()
    try:
        r = db.get(ReinsuranceContract, int(contract_id))
        if not r:
            return False
        db.delete(r)
        db.commit()
        return True
    except ValueError:
        return False
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _reinsurance_bill_to_dict(b: ReinsuranceBill) -> Dict[str, Any]:
    return {
        "id": str(b.id),
        "billNo": b.bill_no,
        "kind": b.biz_kind,
        "period": b.period,
        "premium": b.premium_wan,
        "claimRecover": b.claim_recover_wan,
        "remark": b.remark,
        "createdAt": b.created_at or "",
        "updatedAt": b.updated_at or "",
    }


def list_reinsurance_bills() -> List[Dict[str, Any]]:
    db = _session()
    try:
        rows = db.scalars(select(ReinsuranceBill).order_by(ReinsuranceBill.id.desc())).all()
        return [_reinsurance_bill_to_dict(b) for b in rows]
    finally:
        db.close()


def get_reinsurance_bill(bill_id: str) -> Optional[Dict[str, Any]]:
    db = _session()
    try:
        b = db.get(ReinsuranceBill, int(bill_id))
        return _reinsurance_bill_to_dict(b) if b else None
    except ValueError:
        return None
    finally:
        db.close()


def create_reinsurance_bill(data: Dict[str, Any]) -> Dict[str, Any]:
    db = _session()
    try:
        item = dict(data)
        today = date.today().isoformat()
        row = ReinsuranceBill(
            bill_no=item.get("billNo") or allocate_reinsurance_bill_no(),
            biz_kind=item["kind"],
            period=item.get("period") or "",
            premium_wan=str(item.get("premium", "0")),
            claim_recover_wan=str(item.get("claimRecover", "0")),
            remark=item.get("remark") or "",
            created_at=item.get("createdAt") or today,
            updated_at=item.get("updatedAt") or today,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return _reinsurance_bill_to_dict(row)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def update_reinsurance_bill(bill_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    db = _session()
    try:
        b = db.get(ReinsuranceBill, int(bill_id))
        if not b:
            return None
        key_map = {
            "billNo": "bill_no",
            "kind": "biz_kind",
            "period": "period",
            "premium": "premium_wan",
            "claimRecover": "claim_recover_wan",
            "remark": "remark",
            "createdAt": "created_at",
            "updatedAt": "updated_at",
        }
        for k, v in data.items():
            if v is None:
                continue
            col = key_map.get(k)
            if col is not None:
                setattr(b, col, str(v) if k in ("premium", "claimRecover") else v)
        b.updated_at = date.today().isoformat()
        db.commit()
        db.refresh(b)
        return _reinsurance_bill_to_dict(b)
    except ValueError:
        return None
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def delete_reinsurance_bill(bill_id: str) -> bool:
    db = _session()
    try:
        b = db.get(ReinsuranceBill, int(bill_id))
        if not b:
            return False
        db.delete(b)
        db.commit()
        return True
    except ValueError:
        return False
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

