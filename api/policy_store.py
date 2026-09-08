"""
保单管理模块的简易内存存储（内存版）。
"""

from typing import Any, Dict, List, Optional

POLICIES: List[Dict[str, Any]] = [
    {"id": "1", "policyNo": "P20260001", "customerNo": "C20260001", "productName": "家庭财产综合险A", "premium": "1680", "coverageAmount": "500000", "startDate": "2026-01-01", "endDate": "2026-12-31", "status": "生效中"},
    {"id": "2", "policyNo": "P20260002", "customerNo": "C20260002", "productName": "城市家庭责任险B", "premium": "620", "coverageAmount": "1000000", "startDate": "2026-01-15", "endDate": "2027-01-14", "status": "生效中"},
    {"id": "3", "policyNo": "P20260003", "customerNo": "C20260003", "productName": "健康无忧百万医疗险", "premium": "365", "coverageAmount": "6000000", "startDate": "2026-02-01", "endDate": "2027-01-31", "status": "生效中"},
    {"id": "4", "policyNo": "P20260004", "customerNo": "C20260004", "productName": "安行无忧综合意外险", "premium": "299", "coverageAmount": "1000000", "startDate": "2026-02-08", "endDate": "2027-02-07", "status": "生效中"},
    {"id": "5", "policyNo": "P20260005", "customerNo": "C20260005", "productName": "安心一生终身寿险", "premium": "12000", "coverageAmount": "1000000", "startDate": "2026-02-18", "endDate": "2046-02-17", "status": "生效中"},
    {"id": "6", "policyNo": "P20260006", "customerNo": "C20260006", "productName": "金盈年金养老计划", "premium": "8000", "coverageAmount": "3000000", "startDate": "2026-03-01", "endDate": "2046-02-28", "status": "生效中"},
    {"id": "7", "policyNo": "P20260007", "customerNo": "C20260007", "productName": "悦享高端门急诊医疗险", "premium": "2500", "coverageAmount": "2000000", "startDate": "2026-03-05", "endDate": "2027-03-04", "status": "生效中"},
    {"id": "8", "policyNo": "P20260008", "customerNo": "C20260008", "productName": "车辆综合保险标准版", "premium": "3600", "coverageAmount": "2000000", "startDate": "2026-03-12", "endDate": "2027-03-11", "status": "生效中"},
    {"id": "9", "policyNo": "P20260009", "customerNo": "C20260009", "productName": "商户营业中断保障险", "premium": "4200", "coverageAmount": "1500000", "startDate": "2026-03-18", "endDate": "2027-03-17", "status": "生效中"},
    {"id": "10", "policyNo": "P20260010", "customerNo": "C20260010", "productName": "雇主责任保障计划", "premium": "6800", "coverageAmount": "3000000", "startDate": "2026-03-21", "endDate": "2027-03-20", "status": "生效中"},
    {"id": "11", "policyNo": "P20260011", "customerNo": "C20260011", "productName": "跨境差旅意外保障", "premium": "499", "coverageAmount": "800000", "startDate": "2026-03-25", "endDate": "2027-03-24", "status": "生效中"},
    {"id": "12", "policyNo": "P20260012", "customerNo": "C20260012", "productName": "电商退货运费保障险", "premium": "99", "coverageAmount": "50000", "startDate": "2026-03-28", "endDate": "2027-03-27", "status": "生效中"},
    {"id": "13", "policyNo": "P20260013", "customerNo": "C20260013", "productName": "家庭财产综合险A", "premium": "1750", "coverageAmount": "550000", "startDate": "2026-04-01", "endDate": "2027-03-31", "status": "生效中"},
    {"id": "14", "policyNo": "P20260014", "customerNo": "C20260014", "productName": "城市家庭责任险B", "premium": "640", "coverageAmount": "1000000", "startDate": "2026-04-05", "endDate": "2027-04-04", "status": "生效中"},
    {"id": "15", "policyNo": "P20260015", "customerNo": "C20260015", "productName": "健康无忧百万医疗险", "premium": "420", "coverageAmount": "6000000", "startDate": "2026-04-10", "endDate": "2027-04-09", "status": "生效中"},
    {"id": "16", "policyNo": "P20260016", "customerNo": "C20260016", "productName": "安行无忧综合意外险", "premium": "330", "coverageAmount": "1000000", "startDate": "2026-04-12", "endDate": "2027-04-11", "status": "生效中"},
    {"id": "17", "policyNo": "P20260017", "customerNo": "C20260017", "productName": "安心一生终身寿险", "premium": "13500", "coverageAmount": "1200000", "startDate": "2026-04-18", "endDate": "2046-04-17", "status": "生效中"},
    {"id": "18", "policyNo": "P20260018", "customerNo": "C20260018", "productName": "金盈年金养老计划", "premium": "9200", "coverageAmount": "3200000", "startDate": "2026-04-20", "endDate": "2046-04-19", "status": "生效中"},
    {"id": "19", "policyNo": "P20260019", "customerNo": "C20260019", "productName": "悦享高端门急诊医疗险", "premium": "2780", "coverageAmount": "2200000", "startDate": "2026-04-25", "endDate": "2027-04-24", "status": "生效中"},
    {"id": "20", "policyNo": "P20260020", "customerNo": "C20260020", "productName": "车辆综合保险标准版", "premium": "3890", "coverageAmount": "2000000", "startDate": "2026-04-28", "endDate": "2027-04-27", "status": "生效中"},
    {"id": "21", "policyNo": "P20260021", "customerNo": "C20260021", "productName": "商户营业中断保障险", "premium": "4500", "coverageAmount": "1500000", "startDate": "2026-05-01", "endDate": "2027-04-30", "status": "生效中"},
    {"id": "22", "policyNo": "P20260022", "customerNo": "C20260022", "productName": "雇主责任保障计划", "premium": "7050", "coverageAmount": "3000000", "startDate": "2026-05-05", "endDate": "2027-05-04", "status": "生效中"},
    {"id": "23", "policyNo": "P20260023", "customerNo": "C20260023", "productName": "跨境差旅意外保障", "premium": "580", "coverageAmount": "900000", "startDate": "2026-05-09", "endDate": "2027-05-08", "status": "生效中"},
    {"id": "24", "policyNo": "P20260024", "customerNo": "C20260024", "productName": "电商退货运费保障险", "premium": "120", "coverageAmount": "50000", "startDate": "2026-05-12", "endDate": "2027-05-11", "status": "生效中"},
    {"id": "25", "policyNo": "P20260025", "customerNo": "C20260025", "productName": "家庭财产综合险A", "premium": "1690", "coverageAmount": "520000", "startDate": "2026-05-15", "endDate": "2027-05-14", "status": "生效中"},
    {"id": "26", "policyNo": "P20260026", "customerNo": "C20260026", "productName": "城市家庭责任险B", "premium": "610", "coverageAmount": "1000000", "startDate": "2026-05-18", "endDate": "2027-05-17", "status": "生效中"},
    {"id": "27", "policyNo": "P20260027", "customerNo": "C20260027", "productName": "健康无忧百万医疗险", "premium": "398", "coverageAmount": "6000000", "startDate": "2026-05-22", "endDate": "2027-05-21", "status": "生效中"},
    {"id": "28", "policyNo": "P20260028", "customerNo": "C20260028", "productName": "安行无忧综合意外险", "premium": "315", "coverageAmount": "1000000", "startDate": "2026-05-25", "endDate": "2027-05-24", "status": "生效中"},
    {"id": "29", "policyNo": "P20260029", "customerNo": "C20260029", "productName": "安心一生终身寿险", "premium": "12800", "coverageAmount": "1000000", "startDate": "2026-05-28", "endDate": "2046-05-27", "status": "生效中"},
    {"id": "30", "policyNo": "P20260030", "customerNo": "C20260030", "productName": "金盈年金养老计划", "premium": "8600", "coverageAmount": "3000000", "startDate": "2026-05-30", "endDate": "2046-05-29", "status": "生效中"}
    ,
    # 用于触发「同一卡/同客户多保单」类预设规则（card_policy_count > 3）
    {"id": "31", "policyNo": "P20260101", "customerNo": "C20260009", "productName": "安行无忧综合意外险", "premium": "299", "coverageAmount": "1000000", "startDate": "2026-03-20", "endDate": "2027-03-19", "status": "生效中"},
    {"id": "32", "policyNo": "P20260102", "customerNo": "C20260009", "productName": "跨境差旅意外保障", "premium": "199", "coverageAmount": "800000", "startDate": "2026-03-22", "endDate": "2027-03-21", "status": "生效中"},
    {"id": "33", "policyNo": "P20260103", "customerNo": "C20260009", "productName": "电商退货运费保障险", "premium": "99", "coverageAmount": "50000", "startDate": "2026-03-24", "endDate": "2027-03-23", "status": "生效中"}
]

_next_policy_id = 34


def list_policies() -> List[Dict[str, Any]]:
    return list(POLICIES)


def get_policy(policy_id: str) -> Optional[Dict[str, Any]]:
    for p in POLICIES:
        if p.get("id") == policy_id:
            return p
    return None


def create_policy(data: Dict[str, Any]) -> Dict[str, Any]:
    global _next_policy_id
    item = dict(data)
    item.setdefault("id", str(_next_policy_id))
    item.setdefault("status", "生效中")
    _next_policy_id += 1
    POLICIES.append(item)
    return item


def update_policy(policy_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    for idx, p in enumerate(POLICIES):
        if p.get("id") == policy_id:
            updated = dict(p)
            updated.update(data)
            updated["id"] = policy_id
            POLICIES[idx] = updated
            return updated
    return None


def delete_policy(policy_id: str) -> bool:
    for idx, p in enumerate(POLICIES):
        if p.get("id") == policy_id:
            POLICIES.pop(idx)
            return True
    return False
