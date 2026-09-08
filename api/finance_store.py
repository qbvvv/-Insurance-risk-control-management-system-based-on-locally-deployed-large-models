"""
财务管理 — 内存存储（无 DATABASE_URL 时使用）。
"""

from datetime import date
from typing import Any, Dict, List, Optional

PREMIUM_FLOWS: List[Dict[str, Any]] = [
    {"id": "1", "flowNo": "PF20260306001", "flowType": "首期", "policyNo": "P20260006", "amount": "8000", "payMethod": "银行代扣", "status": "成功", "remark": "年金险首期", "createdAt": "2026-03-06", "updatedAt": "2026-03-06"},
    {"id": "2", "flowNo": "PF20260306002", "flowType": "理赔赔款", "policyNo": "P20260001", "amount": "45000", "payMethod": "转账", "status": "已支付", "remark": "财产险结案赔款", "createdAt": "2026-03-06", "updatedAt": "2026-03-06"},
    {"id": "3", "flowNo": "PF20260306003", "flowType": "首期", "policyNo": "P20260001", "amount": "1680", "payMethod": "银行代扣", "status": "成功", "remark": "家财险首期", "createdAt": "2026-03-07", "updatedAt": "2026-03-07"},
    {"id": "4", "flowNo": "PF20260306004", "flowType": "续期", "policyNo": "P20260006", "amount": "8000", "payMethod": "银行代扣", "status": "成功", "remark": "年金险续期", "createdAt": "2026-03-07", "updatedAt": "2026-03-07"},
    {"id": "5", "flowNo": "PF20260306005", "flowType": "理赔赔款", "policyNo": "P20260008", "amount": "9800", "payMethod": "转账", "status": "已支付", "remark": "车险理赔", "createdAt": "2026-03-09", "updatedAt": "2026-03-09"},
    {"id": "6", "flowNo": "PF20260306006", "flowType": "首期", "policyNo": "P20260003", "amount": "365", "payMethod": "线上支付", "status": "成功", "remark": "百万医疗首期", "createdAt": "2026-03-08", "updatedAt": "2026-03-08"},
    {"id": "7", "flowNo": "PF20260306007", "flowType": "首期", "policyNo": "P20260005", "amount": "12000", "payMethod": "转账", "status": "成功", "remark": "终身寿险首期", "createdAt": "2026-03-09", "updatedAt": "2026-03-09"},
    {"id": "8", "flowNo": "PF20260306008", "flowType": "退费", "policyNo": "P20260012", "amount": "99", "payMethod": "原路退回", "status": "成功", "remark": "退货运费险退保", "createdAt": "2026-03-10", "updatedAt": "2026-03-10"},
    {"id": "9", "flowNo": "PF20260306009", "flowType": "理赔赔款", "policyNo": "P20260003", "amount": "24000", "payMethod": "转账", "status": "处理中", "remark": "医疗险批量打款队列中", "createdAt": "2026-03-11", "updatedAt": "2026-03-11"},
    {"id": "10", "flowNo": "PF20260306010", "flowType": "首期", "policyNo": "P20260010", "amount": "6800", "payMethod": "对公转账", "status": "成功", "remark": "雇主责任险首期", "createdAt": "2026-03-12", "updatedAt": "2026-03-12"},
]

COMMISSION_SETTLEMENTS: List[Dict[str, Any]] = [
    {"id": "1", "settlementNo": "CM20260306001", "channelName": "个人代理渠道", "channelCode": "AG001", "period": "2026-02", "commissionAmount": "12000", "reconcileStatus": "已对账", "remark": "", "createdAt": "2026-03-06", "updatedAt": "2026-03-06"},
    {"id": "2", "settlementNo": "CM20260306002", "channelName": "XX 银行保险部", "channelCode": "BN001", "period": "2026-02", "commissionAmount": "38000", "reconcileStatus": "对账中", "remark": "", "createdAt": "2026-03-06", "updatedAt": "2026-03-06"},
    {"id": "3", "settlementNo": "CM20260306003", "channelName": "网销直营旗舰店", "channelCode": "WS001", "period": "2026-03", "commissionAmount": "8600", "reconcileStatus": "待对账", "remark": "线上引流成本结算", "createdAt": "2026-03-10", "updatedAt": "2026-03-10"},
    {"id": "4", "settlementNo": "CM20260306004", "channelName": "XX 保险经纪公司", "channelCode": "BR001", "period": "2026-02", "commissionAmount": "22400", "reconcileStatus": "已对账", "remark": "经代渠道月度结算", "createdAt": "2026-03-08", "updatedAt": "2026-03-08"},
    {"id": "5", "settlementNo": "CM20260306005", "channelName": "电话销售中心", "channelCode": "TM001", "period": "2026-03", "commissionAmount": "5600", "reconcileStatus": "对账中", "remark": "电销坐席绩效提成", "createdAt": "2026-03-11", "updatedAt": "2026-03-11"},
    {"id": "6", "settlementNo": "CM20260306006", "channelName": "个人代理渠道", "channelCode": "AG001", "period": "2026-03", "commissionAmount": "15800", "reconcileStatus": "待对账", "remark": "跨月补录单并入", "createdAt": "2026-03-12", "updatedAt": "2026-03-12"},
]

_next_pf = 11
_next_cm = 7


def _allocate_pf_no(rows: List[Dict[str, Any]]) -> str:
    d = date.today().strftime("%Y%m%d")
    prefix = f"PF{d}"
    n = sum(1 for r in rows if str(r.get("flowNo", "")).startswith(prefix))
    return f"{prefix}{n + 1:04d}"


def _allocate_cm_no(rows: List[Dict[str, Any]]) -> str:
    d = date.today().strftime("%Y%m%d")
    prefix = f"CM{d}"
    n = sum(1 for r in rows if str(r.get("settlementNo", "")).startswith(prefix))
    return f"{prefix}{n + 1:04d}"


def allocate_premium_flow_no() -> str:
    return _allocate_pf_no(PREMIUM_FLOWS)


def allocate_commission_settlement_no() -> str:
    return _allocate_cm_no(COMMISSION_SETTLEMENTS)


def list_premium_flows() -> List[Dict[str, Any]]:
    return list(PREMIUM_FLOWS)


def get_premium_flow(flow_id: str) -> Optional[Dict[str, Any]]:
    for x in PREMIUM_FLOWS:
        if x.get("id") == flow_id:
            return x
    return None


def create_premium_flow(data: Dict[str, Any]) -> Dict[str, Any]:
    global _next_pf
    item = dict(data)
    item.setdefault("id", str(_next_pf))
    if not item.get("flowNo"):
        item["flowNo"] = allocate_premium_flow_no()
    item.setdefault("remark", "")
    today = date.today().isoformat()
    item.setdefault("createdAt", today)
    item.setdefault("updatedAt", today)
    _next_pf += 1
    PREMIUM_FLOWS.append(item)
    return item


def update_premium_flow(flow_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    for idx, x in enumerate(PREMIUM_FLOWS):
        if x.get("id") == flow_id:
            u = dict(x)
            u.update(data)
            u["id"] = flow_id
            u["updatedAt"] = date.today().isoformat()
            PREMIUM_FLOWS[idx] = u
            return u
    return None


def delete_premium_flow(flow_id: str) -> bool:
    for idx, x in enumerate(PREMIUM_FLOWS):
        if x.get("id") == flow_id:
            PREMIUM_FLOWS.pop(idx)
            return True
    return False


def list_commission_settlements() -> List[Dict[str, Any]]:
    return list(COMMISSION_SETTLEMENTS)


def get_commission_settlement(settlement_id: str) -> Optional[Dict[str, Any]]:
    for x in COMMISSION_SETTLEMENTS:
        if x.get("id") == settlement_id:
            return x
    return None


def create_commission_settlement(data: Dict[str, Any]) -> Dict[str, Any]:
    global _next_cm
    item = dict(data)
    item.setdefault("id", str(_next_cm))
    if not item.get("settlementNo"):
        item["settlementNo"] = allocate_commission_settlement_no()
    item.setdefault("channelCode", "")
    item.setdefault("remark", "")
    today = date.today().isoformat()
    item.setdefault("createdAt", today)
    item.setdefault("updatedAt", today)
    _next_cm += 1
    COMMISSION_SETTLEMENTS.append(item)
    return item


def update_commission_settlement(settlement_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    for idx, x in enumerate(COMMISSION_SETTLEMENTS):
        if x.get("id") == settlement_id:
            u = dict(x)
            u.update(data)
            u["id"] = settlement_id
            u["updatedAt"] = date.today().isoformat()
            COMMISSION_SETTLEMENTS[idx] = u
            return u
    return None


def delete_commission_settlement(settlement_id: str) -> bool:
    for idx, x in enumerate(COMMISSION_SETTLEMENTS):
        if x.get("id") == settlement_id:
            COMMISSION_SETTLEMENTS.pop(idx)
            return True
    return False

