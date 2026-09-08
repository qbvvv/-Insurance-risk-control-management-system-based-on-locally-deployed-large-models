"""
向 MySQL 写入可命中风控规则的演示数据。

覆盖的典型命中场景：
1) claim_freq_high_risk: 3个月内理赔次数 > 3
2) policy_year_claim_reject: 同一年度理赔次数 > 5
3) claim_premium_ratio_review: 理赔/保费比 > 10
4) new_user_early_claim_review: 投保后 7 天内理赔
5) night_claim_manual: 今日报案（在当前聚合逻辑下会映射为夜间提交）
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from api.database import db_enabled, init_db
from api.store_mysql import (
    allocate_claim_no,
    create_claim,
    create_customer,
    create_policy,
    list_claims,
    list_customers,
    list_policies,
)


def _find_customer_by_id_no(id_no: str) -> Optional[Dict[str, Any]]:
    for c in list_customers():
        if str(c.get("idNo", "")).strip() == id_no:
            return c
    return None


def _find_policy(policy_no: str) -> Optional[Dict[str, Any]]:
    for p in list_policies():
        if str(p.get("policyNo", "")).strip() == policy_no:
            return p
    return None


def _claim_exists(policy_no: str, report_date: str, amount: str) -> bool:
    for c in list_claims():
        if (
            str(c.get("policyNo", "")).strip() == policy_no
            and str(c.get("reportDate", "")).strip() == report_date
            and str(c.get("claimAmount", "")).strip() == str(amount)
        ):
            return True
    return False


def _ensure_customer(name: str, id_no: str, phone: str, address: str) -> Dict[str, Any]:
    exists = _find_customer_by_id_no(id_no)
    if exists:
        return exists
    return create_customer(
        {
            "name": name,
            "idType": "身份证",
            "idNo": id_no,
            "phone": phone,
            "occupation": "风控样例客户",
            "level": "普通",
            "status": "在保",
            "gender": "未知",
            "address": address,
            "remark": "规则命中测试数据",
        }
    )


def _ensure_policy(customer_no: str, product_name: str, premium: str, start_date: str) -> Dict[str, Any]:
    # 同一个 customer + product + start_date 认为是一张测试保单，避免重复插入
    for p in list_policies():
        if (
            str(p.get("customerNo", "")).strip() == customer_no
            and str(p.get("productName", "")).strip() == product_name
            and str(p.get("startDate", "")).strip() == start_date
        ):
            return p
    policy_no = _allocate_policy_no()
    return create_policy(
        {
            "policyNo": policy_no,
            "customerNo": customer_no,
            "productName": product_name,
            "premium": premium,
            "coverageAmount": "500000",
            "startDate": start_date,
            "endDate": (date.fromisoformat(start_date) + timedelta(days=365)).isoformat(),
            "status": "生效中",
        }
    )


def _allocate_policy_no() -> str:
    y = date.today().year
    prefix = f"P{y}"
    max_seq = 0
    for p in list_policies():
        no = str(p.get("policyNo", "")).strip()
        if not no.startswith(prefix):
            continue
        tail = no[len(prefix) :]
        if tail.isdigit():
            max_seq = max(max_seq, int(tail))
    return f"{prefix}{max_seq + 1:04d}"


def _ensure_claim(
    customer_no: str,
    claimant_name: str,
    product_name: str,
    policy_no: str,
    report_date: str,
    claim_amount: str,
    approved_amount: str,
    incident_delta_days: int = 2,
) -> None:
    if _claim_exists(policy_no, report_date, claim_amount):
        return
    rpt = date.fromisoformat(report_date)
    incident_date = (rpt - timedelta(days=incident_delta_days)).isoformat()
    create_claim(
        {
            "claimNo": allocate_claim_no(),
            "policyNo": policy_no,
            "customerNo": customer_no,
            "claimantName": claimant_name,
            "productName": product_name,
            "claimType": "财产",
            "incidentReason": "规则命中样例事件",
            "incidentDate": incident_date,
            "reportDate": report_date,
            "claimAmount": claim_amount,
            "approvedAmount": approved_amount,
            "status": "待受理",
            "decisionNote": "演示数据",
        }
    )


def seed() -> Dict[str, int]:
    if not db_enabled():
        raise RuntimeError("未启用 DATABASE_URL，当前不是 MySQL 模式，无法写入数据库。")
    init_db()
    today = date.today()
    y = today.year

    inserted_customers = 0
    inserted_policies = 0
    inserted_claims = 0

    scenarios: List[Dict[str, Any]] = [
        {
            "name": "高频理赔客户A",
            "id_no": "TST-RULE-0001",
            "phone": "13800000001",
            "address": "广州市天河区样例路1号",
            "product_name": "家庭财产综合险A",
            "premium": "2000",
            "start_date": (today - timedelta(days=180)).isoformat(),
            "claims": [
                (today - timedelta(days=10)).isoformat(),
                (today - timedelta(days=30)).isoformat(),
                (today - timedelta(days=50)).isoformat(),
                (today - timedelta(days=70)).isoformat(),
            ],
            "claim_amount": "12000",
            "approved_amount": "10000",
        },
        {
            "name": "年度高频理赔客户B",
            "id_no": "TST-RULE-0002",
            "phone": "13800000002",
            "address": "深圳市南山区样例路2号",
            "product_name": "家庭财产综合险A",
            "premium": "3000",
            "start_date": f"{y}-01-01",
            "claims": [
                f"{y}-01-20",
                f"{y}-02-10",
                f"{y}-03-05",
                f"{y}-04-08",
                f"{y}-05-12",
                f"{y}-06-18",
            ],
            "claim_amount": "8000",
            "approved_amount": "7000",
        },
        {
            "name": "高赔付比客户C",
            "id_no": "TST-RULE-0003",
            "phone": "13800000003",
            "address": "杭州市滨江区样例路3号",
            "product_name": "家庭财产综合险A",
            "premium": "1000",
            "start_date": (today - timedelta(days=60)).isoformat(),
            "claims": [(today - timedelta(days=5)).isoformat()],
            "claim_amount": "20000",
            "approved_amount": "18000",
        },
        {
            "name": "新用户早赔客户D",
            "id_no": "TST-RULE-0004",
            "phone": "13800000004",
            "address": "成都市高新区样例路4号",
            "product_name": "家庭财产综合险A",
            "premium": "2500",
            "start_date": (today - timedelta(days=3)).isoformat(),
            "claims": [today.isoformat()],
            "claim_amount": "3000",
            "approved_amount": "2500",
        },
    ]

    for s in scenarios:
        existing_customer = _find_customer_by_id_no(s["id_no"])
        c = _ensure_customer(s["name"], s["id_no"], s["phone"], s["address"])
        if not existing_customer:
            inserted_customers += 1

        customer_no = str(c["customerNo"])
        existing_policy = None
        for p in list_policies():
            if (
                str(p.get("customerNo", "")).strip() == customer_no
                and str(p.get("productName", "")).strip() == s["product_name"]
                and str(p.get("startDate", "")).strip() == s["start_date"]
            ):
                existing_policy = p
                break
        pol = _ensure_policy(customer_no, s["product_name"], s["premium"], s["start_date"])
        if not existing_policy:
            inserted_policies += 1

        policy_no = str(pol["policyNo"])
        for rd in s["claims"]:
            existed = _claim_exists(policy_no, rd, s["claim_amount"])
            _ensure_claim(
                customer_no=customer_no,
                claimant_name=s["name"],
                product_name=s["product_name"],
                policy_no=policy_no,
                report_date=rd,
                claim_amount=s["claim_amount"],
                approved_amount=s["approved_amount"],
            )
            if not existed:
                inserted_claims += 1

    return {
        "inserted_customers": inserted_customers,
        "inserted_policies": inserted_policies,
        "inserted_claims": inserted_claims,
    }


if __name__ == "__main__":
    result = seed()
    print("seed finished:", result)
