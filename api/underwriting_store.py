"""
承保案件 — 内存存储（无 DATABASE_URL 时使用）。
"""

from datetime import date
from typing import Any, Dict, List, Optional

UNDERWRITING_CASES: List[Dict[str, Any]] = [
    {"id": "1", "caseNo": "UW2026030601", "customerNo": "C20260001", "applicantName": "张伟", "idNo": "110101199001012026", "productName": "健康无忧百万医疗险", "premium": "365", "coverageAmount": "6000000", "channel": "线上直销", "status": "自动通过", "riskScore": "低", "decisionNote": "规则引擎未命中高风险，自动核保通过。", "policyNo": "", "createdAt": "2026-03-06", "updatedAt": "2026-03-06"},
    {"id": "2", "caseNo": "UW2026030602", "customerNo": "C20260005", "applicantName": "陈杰", "idNo": "330103199307172026", "productName": "安心一生终身寿险", "premium": "12000", "coverageAmount": "1000000", "channel": "银行渠道", "status": "待人工核保", "riskScore": "中", "decisionNote": "高额寿险需人工复核与体检材料。", "policyNo": "", "createdAt": "2026-03-06", "updatedAt": "2026-03-06"},
    {"id": "3", "caseNo": "UW2026030603", "customerNo": "C20260007", "applicantName": "赵磊", "idNo": "510104198912052026", "productName": "悦享高端门急诊医疗险", "premium": "2500", "coverageAmount": "2000000", "channel": "个人代理", "status": "人工通过", "riskScore": "中", "decisionNote": "补充既往病史说明后人工通过。", "policyNo": "P20260007", "createdAt": "2026-03-07", "updatedAt": "2026-03-08"},
    {"id": "4", "caseNo": "UW2026030604", "customerNo": "C20260008", "applicantName": "上官婉儿", "idNo": "120105199605262026", "productName": "车辆综合保险标准版", "premium": "3600", "coverageAmount": "2000000", "channel": "网销平台", "status": "自动通过", "riskScore": "低", "decisionNote": "车险标准核保规则通过。", "policyNo": "P20260008", "createdAt": "2026-03-07", "updatedAt": "2026-03-07"},
    {"id": "5", "caseNo": "UW2026030605", "customerNo": "C20260015", "applicantName": "高梓轩", "idNo": "500103198706282026", "productName": "健康无忧百万医疗险", "premium": "420", "coverageAmount": "6000000", "channel": "线下网点", "status": "待补件", "riskScore": "中", "decisionNote": "需补充门急诊病历与体检报告。", "policyNo": "", "createdAt": "2026-03-08", "updatedAt": "2026-03-08"},
    {"id": "6", "caseNo": "UW2026030606", "customerNo": "C20260021", "applicantName": "梁晨曦", "idNo": "450103198312302026", "productName": "商户营业中断保障险", "premium": "4500", "coverageAmount": "1500000", "channel": "个人代理", "status": "拒保", "riskScore": "高", "decisionNote": "近12个月出险频率偏高，暂不承保。", "policyNo": "", "createdAt": "2026-03-08", "updatedAt": "2026-03-09"},
    {"id": "7", "caseNo": "UW2026030607", "customerNo": "C20260009", "applicantName": "周强", "idNo": "350203198710192026", "productName": "安行无忧综合意外险", "premium": "299", "coverageAmount": "1000000", "channel": "线上直销", "status": "自动通过", "riskScore": "低", "decisionNote": "职业类别与告知一致，自动通过。", "policyNo": "P20260004", "createdAt": "2026-03-09", "updatedAt": "2026-03-09"},
    {"id": "8", "caseNo": "UW2026030608", "customerNo": "C20260011", "applicantName": "徐鹏", "idNo": "230103198403112026", "productName": "金盈年金养老计划", "premium": "8000", "coverageAmount": "3000000", "channel": "银保渠道", "status": "人工通过", "riskScore": "中", "decisionNote": "财务审查与反洗钱筛查通过。", "policyNo": "P20260006", "createdAt": "2026-03-10", "updatedAt": "2026-03-10"},
    {"id": "9", "caseNo": "UW2026030609", "customerNo": "C20260003", "applicantName": "李娜", "idNo": "440106198806222026", "productName": "城市家庭责任险B", "premium": "620", "coverageAmount": "1000000", "channel": "银行渠道", "status": "核保中", "riskScore": "低", "decisionNote": "等待第三方风控评分回传。", "policyNo": "", "createdAt": "2026-03-10", "updatedAt": "2026-03-11"},
    {"id": "10", "caseNo": "UW2026030610", "customerNo": "C20260006", "applicantName": "杨雨桐", "idNo": "420102199411082026", "productName": "车辆综合保险标准版", "premium": "3600", "coverageAmount": "2000000", "channel": "线下网点", "status": "待受理", "riskScore": "中", "decisionNote": "新单录入，待规则引擎初筛。", "policyNo": "", "createdAt": "2026-03-11", "updatedAt": "2026-03-11"},
]

_next_uw_id = 11


def allocate_case_no() -> str:
    d = date.today().strftime("%Y%m%d")
    prefix = f"UW{d}"
    n = sum(1 for c in UNDERWRITING_CASES if str(c.get("caseNo", "")).startswith(prefix))
    return f"{prefix}{n + 1:04d}"


def list_underwriting_cases() -> List[Dict[str, Any]]:
    return list(UNDERWRITING_CASES)


def get_underwriting_case(case_id: str) -> Optional[Dict[str, Any]]:
    for c in UNDERWRITING_CASES:
        if c.get("id") == case_id:
            return c
    return None


def create_underwriting_case(data: Dict[str, Any]) -> Dict[str, Any]:
    global _next_uw_id
    item = dict(data)
    item.setdefault("id", str(_next_uw_id))
    if not item.get("caseNo"):
        item["caseNo"] = allocate_case_no()
    item.setdefault("idNo", "")
    item.setdefault("premium", "0")
    item.setdefault("coverageAmount", "0")
    item.setdefault("channel", "")
    item.setdefault("status", "待受理")
    item.setdefault("riskScore", "")
    item.setdefault("decisionNote", "")
    item.setdefault("policyNo", "")
    today = date.today().isoformat()
    item.setdefault("createdAt", today)
    item.setdefault("updatedAt", today)
    _next_uw_id += 1
    UNDERWRITING_CASES.append(item)
    return item


def update_underwriting_case(case_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    for idx, c in enumerate(UNDERWRITING_CASES):
        if c.get("id") == case_id:
            updated = dict(c)
            updated.update(data)
            updated["id"] = case_id
            updated["updatedAt"] = date.today().isoformat()
            UNDERWRITING_CASES[idx] = updated
            return updated
    return None


def delete_underwriting_case(case_id: str) -> bool:
    for idx, c in enumerate(UNDERWRITING_CASES):
        if c.get("id") == case_id:
            UNDERWRITING_CASES.pop(idx)
            return True
    return False
