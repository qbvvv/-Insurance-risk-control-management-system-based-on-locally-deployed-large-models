"""
再保管理 — 内存存储（无 DATABASE_URL 时使用）。
"""

from datetime import date
from typing import Any, Dict, List, Optional

REINSURANCE_CONTRACTS: List[Dict[str, Any]] = [
    {
        "id": "1",
        "contractNo": "RC20260306001",
        "contractType": "比例再保",
        "cedent": "本公司",
        "reinsurer": "XX 再保险公司",
        "status": "生效",
        "remark": "",
        "createdAt": "2026-03-06",
        "updatedAt": "2026-03-06",
    },
    {
        "id": "2",
        "contractNo": "RC20260306002",
        "contractType": "溢额再保",
        "cedent": "本公司",
        "reinsurer": "YY 再保险公司",
        "status": "生效",
        "remark": "",
        "createdAt": "2026-03-06",
        "updatedAt": "2026-03-06",
    },
]

REINSURANCE_BILLS: List[Dict[str, Any]] = [
    {
        "id": "1",
        "billNo": "RB20260306001",
        "kind": "分出",
        "period": "2026Q1",
        "premium": "260",
        "claimRecover": "30",
        "remark": "",
        "createdAt": "2026-03-06",
        "updatedAt": "2026-03-06",
    },
    {
        "id": "2",
        "billNo": "RB20260306002",
        "kind": "分入",
        "period": "2026Q1",
        "premium": "120",
        "claimRecover": "8",
        "remark": "",
        "createdAt": "2026-03-06",
        "updatedAt": "2026-03-06",
    },
]

_next_rc = 3
_next_rb = 3


def _allocate_rc_no(rows: List[Dict[str, Any]]) -> str:
    d = date.today().strftime("%Y%m%d")
    prefix = f"RC{d}"
    n = sum(1 for r in rows if str(r.get("contractNo", "")).startswith(prefix))
    return f"{prefix}{n + 1:04d}"


def _allocate_rb_no(rows: List[Dict[str, Any]]) -> str:
    d = date.today().strftime("%Y%m%d")
    prefix = f"RB{d}"
    n = sum(1 for r in rows if str(r.get("billNo", "")).startswith(prefix))
    return f"{prefix}{n + 1:04d}"


def allocate_reinsurance_contract_no() -> str:
    return _allocate_rc_no(REINSURANCE_CONTRACTS)


def allocate_reinsurance_bill_no() -> str:
    return _allocate_rb_no(REINSURANCE_BILLS)


def list_reinsurance_contracts() -> List[Dict[str, Any]]:
    return list(REINSURANCE_CONTRACTS)


def get_reinsurance_contract(contract_id: str) -> Optional[Dict[str, Any]]:
    for x in REINSURANCE_CONTRACTS:
        if x.get("id") == contract_id:
            return x
    return None


def create_reinsurance_contract(data: Dict[str, Any]) -> Dict[str, Any]:
    global _next_rc
    item = dict(data)
    item.setdefault("id", str(_next_rc))
    if not item.get("contractNo"):
        item["contractNo"] = allocate_reinsurance_contract_no()
    item.setdefault("status", "生效")
    item.setdefault("remark", "")
    today = date.today().isoformat()
    item.setdefault("createdAt", today)
    item.setdefault("updatedAt", today)
    _next_rc += 1
    REINSURANCE_CONTRACTS.append(item)
    return item


def update_reinsurance_contract(contract_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    for idx, x in enumerate(REINSURANCE_CONTRACTS):
        if x.get("id") == contract_id:
            u = dict(x)
            u.update(data)
            u["id"] = contract_id
            u["updatedAt"] = date.today().isoformat()
            REINSURANCE_CONTRACTS[idx] = u
            return u
    return None


def delete_reinsurance_contract(contract_id: str) -> bool:
    for idx, x in enumerate(REINSURANCE_CONTRACTS):
        if x.get("id") == contract_id:
            REINSURANCE_CONTRACTS.pop(idx)
            return True
    return False


def list_reinsurance_bills() -> List[Dict[str, Any]]:
    return list(REINSURANCE_BILLS)


def get_reinsurance_bill(bill_id: str) -> Optional[Dict[str, Any]]:
    for x in REINSURANCE_BILLS:
        if x.get("id") == bill_id:
            return x
    return None


def create_reinsurance_bill(data: Dict[str, Any]) -> Dict[str, Any]:
    global _next_rb
    item = dict(data)
    item.setdefault("id", str(_next_rb))
    if not item.get("billNo"):
        item["billNo"] = allocate_reinsurance_bill_no()
    item.setdefault("remark", "")
    today = date.today().isoformat()
    item.setdefault("createdAt", today)
    item.setdefault("updatedAt", today)
    _next_rb += 1
    REINSURANCE_BILLS.append(item)
    return item


def update_reinsurance_bill(bill_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    for idx, x in enumerate(REINSURANCE_BILLS):
        if x.get("id") == bill_id:
            u = dict(x)
            u.update(data)
            u["id"] = bill_id
            u["updatedAt"] = date.today().isoformat()
            REINSURANCE_BILLS[idx] = u
            return u
    return None


def delete_reinsurance_bill(bill_id: str) -> bool:
    for idx, x in enumerate(REINSURANCE_BILLS):
        if x.get("id") == bill_id:
            REINSURANCE_BILLS.pop(idx)
            return True
    return False

