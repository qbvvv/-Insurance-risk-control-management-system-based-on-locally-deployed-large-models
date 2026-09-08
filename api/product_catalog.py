"""
保险产品标准目录：名称 + 险种 + 参考保费/保额/说明（与前端下拉一致）。
新增产品时须选用目录中的产品名称，服务端据此补全字段。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

# 每条对应一种可售产品模板（参考保费随险种/产品固定，不由用户手填）
PRODUCT_CATALOG: List[Dict[str, str]] = [
    {
        "productName": "家庭财产综合险A",
        "category": "财产险",
        "premiumGuide": "1680 元/年起",
        "coverageCap": "500000",
        "description": "家庭财产综合保障，含火灾、盗抢等常见责任。",
    },
    {
        "productName": "企业财产基本险",
        "category": "财产险",
        "premiumGuide": "按标的估值 0.8‰ 起",
        "coverageCap": "10000000",
        "description": "企业固定资产与存货火灾、爆炸等基本风险。",
    },
    {
        "productName": "健康无忧百万医疗险",
        "category": "健康险",
        "premiumGuide": "365 元/年起",
        "coverageCap": "6000000",
        "description": "住院医疗、特需及指定门诊，年度保额百万级。",
    },
    {
        "productName": "安心一生终身寿险",
        "category": "人寿险",
        "premiumGuide": "按保额与年龄计价",
        "coverageCap": "5000000",
        "description": "终身身故/全残保障，可搭配可选责任。",
    },
    {
        "productName": "畅行天下意外险",
        "category": "意外险",
        "premiumGuide": "199 元/年起",
        "coverageCap": "1000000",
        "description": "综合意外身故伤残及意外医疗。",
    },
    {
        "productName": "交强险（示范）",
        "category": "车险",
        "premiumGuide": "按车型基准保费",
        "coverageCap": "200000",
        "description": "机动车交通事故责任强制保险（演示用固定说明）。",
    },
    {
        "productName": "商业第三者责任险（示范）",
        "category": "车险",
        "premiumGuide": "按保额分档计价",
        "coverageCap": "2000000",
        "description": "商业三者险，保额可选（演示）。",
    },
]


def list_catalog() -> List[Dict[str, str]]:
    return [dict(x) for x in PRODUCT_CATALOG]


def list_categories() -> List[str]:
    seen: List[str] = []
    for x in PRODUCT_CATALOG:
        c = x["category"]
        if c not in seen:
            seen.append(c)
    return seen


def get_catalog_entry(product_name: str) -> Optional[Dict[str, str]]:
    for x in PRODUCT_CATALOG:
        if x["productName"] == product_name:
            return dict(x)
    return None


def merge_catalog_for_create(product_name: str, status: str) -> Dict[str, Any]:
    row = get_catalog_entry(product_name)
    if not row:
        raise ValueError(f"产品名称不在标准目录中：{product_name}")
    return {
        "productName": row["productName"],
        "category": row["category"],
        "description": row["description"],
        "premiumGuide": row["premiumGuide"],
        "coverageCap": row["coverageCap"],
        "status": status or "在售",
    }


