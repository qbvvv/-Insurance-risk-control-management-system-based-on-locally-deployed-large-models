"""
理赔案件 — 内存存储（无 DATABASE_URL 时使用）。
"""

from datetime import date
from typing import Any, Dict, List, Optional

CLAIMS: List[Dict[str, Any]] = [
    {"id": "1", "claimNo": "CLM20260306001", "policyNo": "P20260001", "customerNo": "C20260001", "claimantName": "张某某", "productName": "家庭财产综合险A", "claimType": "财产", "incidentReason": "室内水管爆裂致地板受损", "incidentDate": "2026-02-10", "reportDate": "2026-03-01", "claimAmount": "50000", "approvedAmount": "45000", "status": "已结案", "decisionNote": "定损后同意赔付 45000 元，免赔额已扣除。", "createdAt": "2026-03-06", "updatedAt": "2026-03-06"},
    {"id": "2", "claimNo": "CLM20260306002", "policyNo": "P20260008", "customerNo": "C20260008", "claimantName": "上官婉儿", "productName": "车辆综合保险标准版", "claimType": "车损", "incidentReason": "倒车碰撞导致后保险杠受损", "incidentDate": "2026-03-05", "reportDate": "2026-03-05", "claimAmount": "12000", "approvedAmount": "9800", "status": "已结案", "decisionNote": "按车损险责任赔付。", "createdAt": "2026-03-07", "updatedAt": "2026-03-08"},
    {"id": "3", "claimNo": "CLM20260306003", "policyNo": "P20260007", "customerNo": "C20260007", "claimantName": "赵磊", "productName": "悦享高端门急诊医疗险", "claimType": "医疗", "incidentReason": "急性阑尾炎住院治疗", "incidentDate": "2026-03-09", "reportDate": "2026-03-10", "claimAmount": "18000", "approvedAmount": "16500", "status": "处理中", "decisionNote": "票据审核中。", "createdAt": "2026-03-10", "updatedAt": "2026-03-11"},
    {"id": "4", "claimNo": "CLM20260306004", "policyNo": "P20260009", "customerNo": "C20260009", "claimantName": "周强", "productName": "商户营业中断保障险", "claimType": "营业中断", "incidentReason": "仓库电路故障停业 3 天", "incidentDate": "2026-03-02", "reportDate": "2026-03-04", "claimAmount": "76000", "approvedAmount": "", "status": "待调查", "decisionNote": "待第三方公估报告。", "createdAt": "2026-03-09", "updatedAt": "2026-03-10"},
    {"id": "5", "claimNo": "CLM20260306005", "policyNo": "P20260003", "customerNo": "C20260003", "claimantName": "李娜", "productName": "健康无忧百万医疗险", "claimType": "医疗", "incidentReason": "住院手术医疗费用报销", "incidentDate": "2026-03-01", "reportDate": "2026-03-03", "claimAmount": "26000", "approvedAmount": "24000", "status": "已结案", "decisionNote": "符合医保外责任，核赔通过。", "createdAt": "2026-03-07", "updatedAt": "2026-03-09"},
    {"id": "6", "claimNo": "CLM20260306006", "policyNo": "P20260002", "customerNo": "C20260002", "claimantName": "王晓芳", "productName": "城市家庭责任险B", "claimType": "责任", "incidentReason": "第三者人身轻微伤害协商赔偿", "incidentDate": "2026-03-08", "reportDate": "2026-03-09", "claimAmount": "15000", "approvedAmount": "", "status": "待受理", "decisionNote": "资料已收件，待分案。", "createdAt": "2026-03-11", "updatedAt": "2026-03-11"},
    {"id": "17", "claimNo": "CLM20260306007", "policyNo": "P20260005", "customerNo": "C20260005", "claimantName": "陈杰", "productName": "安心一生终身寿险", "claimType": "身故", "incidentReason": "受益人申请身故保险金", "incidentDate": "2026-02-28", "reportDate": "2026-03-12", "claimAmount": "1000000", "approvedAmount": "", "status": "处理中", "decisionNote": "受益关系与材料核验中。", "createdAt": "2026-03-12", "updatedAt": "2026-03-13"},
    {"id": "18", "claimNo": "CLM20260306008", "policyNo": "P20260011", "customerNo": "C20260011", "claimantName": "徐鹏", "productName": "跨境差旅意外保障", "claimType": "意外", "incidentReason": "境外旅行期间意外骨折", "incidentDate": "2026-03-14", "reportDate": "2026-03-15", "claimAmount": "88000", "approvedAmount": "72000", "status": "已结案", "decisionNote": "按条款境外医疗与意外责任赔付。", "createdAt": "2026-03-15", "updatedAt": "2026-03-16"},
    # ---------- 预设规则命中样本 ----------
    # claim_freq_high_risk：同一客户 3 个月内理赔 > 3 次（C20260007 共 4 次）
    {"id": "7", "claimNo": "CLM20260420007", "policyNo": "P20260007", "customerNo": "C20260007", "claimantName": "赵磊", "productName": "悦享高端门急诊医疗险", "claimType": "医疗", "incidentReason": "门诊检查费用报销", "incidentDate": "2026-03-18", "reportDate": "2026-03-20", "submitHour": 10, "claimAmount": "1200", "approvedAmount": "980", "status": "已结案", "decisionNote": "票据齐全，按比例赔付。", "createdAt": "2026-03-20", "updatedAt": "2026-03-20"},
    {"id": "8", "claimNo": "CLM20260420008", "policyNo": "P20260007", "customerNo": "C20260007", "claimantName": "赵磊", "productName": "悦享高端门急诊医疗险", "claimType": "医疗", "incidentReason": "急诊输液费用报销", "incidentDate": "2026-04-04", "reportDate": "2026-04-05", "submitHour": 23, "claimAmount": "2600", "approvedAmount": "2100", "status": "处理中", "decisionNote": "夜间提交，进入人工复核。", "createdAt": "2026-04-05", "updatedAt": "2026-04-05"},
    {"id": "9", "claimNo": "CLM20260420009", "policyNo": "P20260007", "customerNo": "C20260007", "claimantName": "赵磊", "productName": "悦享高端门急诊医疗险", "claimType": "医疗", "incidentReason": "复诊开药费用报销", "incidentDate": "2026-04-18", "reportDate": "2026-04-20", "submitHour": 9, "claimAmount": "800", "approvedAmount": "620", "status": "待受理", "decisionNote": "资料待补齐。", "createdAt": "2026-04-20", "updatedAt": "2026-04-20"},

    # policy_year_claim_reject：同一保单年度内理赔次数 > 5（C20260021 共 6 次）
    {"id": "10", "claimNo": "CLM20260401010", "policyNo": "P20260021", "customerNo": "C20260021", "claimantName": "梁晨曦", "productName": "商户营业中断保障险", "claimType": "营业中断", "incidentReason": "短停电导致停业半天", "incidentDate": "2026-03-12", "reportDate": "2026-03-12", "submitHour": 14, "claimAmount": "5000", "approvedAmount": "4200", "status": "已结案", "decisionNote": "按条款核赔。", "createdAt": "2026-03-12", "updatedAt": "2026-03-12"},
    {"id": "11", "claimNo": "CLM20260401011", "policyNo": "P20260021", "customerNo": "C20260021", "claimantName": "梁晨曦", "productName": "商户营业中断保障险", "claimType": "营业中断", "incidentReason": "设备故障停业1天", "incidentDate": "2026-03-20", "reportDate": "2026-03-21", "submitHour": 11, "claimAmount": "12000", "approvedAmount": "9800", "status": "已结案", "decisionNote": "核赔通过。", "createdAt": "2026-03-21", "updatedAt": "2026-03-21"},
    {"id": "12", "claimNo": "CLM20260401012", "policyNo": "P20260021", "customerNo": "C20260021", "claimantName": "梁晨曦", "productName": "商户营业中断保障险", "claimType": "营业中断", "incidentReason": "物业检修停业半天", "incidentDate": "2026-04-02", "reportDate": "2026-04-02", "submitHour": 16, "claimAmount": "4000", "approvedAmount": "3500", "status": "已结案", "decisionNote": "核赔通过。", "createdAt": "2026-04-02", "updatedAt": "2026-04-02"},
    {"id": "13", "claimNo": "CLM20260401013", "policyNo": "P20260021", "customerNo": "C20260021", "claimantName": "梁晨曦", "productName": "商户营业中断保障险", "claimType": "营业中断", "incidentReason": "小型火灾排烟停业1天", "incidentDate": "2026-04-10", "reportDate": "2026-04-11", "submitHour": 20, "claimAmount": "18000", "approvedAmount": "", "status": "待调查", "decisionNote": "待公估报告。", "createdAt": "2026-04-11", "updatedAt": "2026-04-11"},
    {"id": "14", "claimNo": "CLM20260401014", "policyNo": "P20260021", "customerNo": "C20260021", "claimantName": "梁晨曦", "productName": "商户营业中断保障险", "claimType": "营业中断", "incidentReason": "临时搬迁停业2天", "incidentDate": "2026-04-18", "reportDate": "2026-04-19", "submitHour": 9, "claimAmount": "30000", "approvedAmount": "", "status": "处理中", "decisionNote": "资料审核中。", "createdAt": "2026-04-19", "updatedAt": "2026-04-19"},

    # claim_premium_ratio_review：理赔金额/保费比例 > 10（P20260012 保费 99）
    {"id": "15", "claimNo": "CLM20260402015", "policyNo": "P20260012", "customerNo": "C20260012", "claimantName": "孙嘉怡", "productName": "电商退货运费保障险", "claimType": "财产", "incidentReason": "多次退货运费集中报销", "incidentDate": "2026-04-01", "reportDate": "2026-04-02", "submitHour": 22, "claimAmount": "2500", "approvedAmount": "2000", "status": "待人工核赔", "decisionNote": "赔付金额与保费比例异常，触发复核。", "createdAt": "2026-04-02", "updatedAt": "2026-04-02"},

    # new_user_early_claim_review：起保后 7 天内理赔（P20260010 起保 2026-03-21）
    {"id": "16", "claimNo": "CLM20260325016", "policyNo": "P20260010", "customerNo": "C20260010", "claimantName": "吴思涵", "productName": "雇主责任保障计划", "claimType": "责任", "incidentReason": "员工轻微工伤就医", "incidentDate": "2026-03-24", "reportDate": "2026-03-25", "submitHour": 15, "claimAmount": "6000", "approvedAmount": "", "status": "处理中", "decisionNote": "起保后短期内报案，进入人工审核。", "createdAt": "2026-03-25", "updatedAt": "2026-03-25"}
]

_next_id = 19


def allocate_claim_no() -> str:
    d = date.today().strftime("%Y%m%d")
    prefix = f"CLM{d}"
    n = sum(1 for c in CLAIMS if str(c.get("claimNo", "")).startswith(prefix))
    return f"{prefix}{n + 1:04d}"


def list_claims() -> List[Dict[str, Any]]:
    return list(CLAIMS)


def get_claim(claim_id: str) -> Optional[Dict[str, Any]]:
    for c in CLAIMS:
        if c.get("id") == claim_id:
            return c
    return None


def create_claim(data: Dict[str, Any]) -> Dict[str, Any]:
    global _next_id
    item = dict(data)
    item.setdefault("id", str(_next_id))
    if not item.get("claimNo"):
        item["claimNo"] = allocate_claim_no()
    item.setdefault("claimType", "")
    item.setdefault("incidentReason", "")
    item.setdefault("incidentDate", "")
    item.setdefault("reportDate", "")
    item.setdefault("claimAmount", "0")
    item.setdefault("approvedAmount", "")
    item.setdefault("status", "待受理")
    item.setdefault("decisionNote", "")
    today = date.today().isoformat()
    item.setdefault("createdAt", today)
    item.setdefault("updatedAt", today)
    _next_id += 1
    CLAIMS.append(item)
    return item


def update_claim(claim_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    for idx, c in enumerate(CLAIMS):
        if c.get("id") == claim_id:
            updated = dict(c)
            updated.update(data)
            updated["id"] = claim_id
            updated["updatedAt"] = date.today().isoformat()
            CLAIMS[idx] = updated
            return updated
    return None


def delete_claim(claim_id: str) -> bool:
    for idx, c in enumerate(CLAIMS):
        if c.get("id") == claim_id:
            CLAIMS.pop(idx)
            return True
    return False
