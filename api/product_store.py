"""
保险产品管理 — 内存存储（无 DATABASE_URL 时使用）。
"""

from datetime import date
from typing import Any, Dict, List, Optional

PRODUCTS: List[Dict[str, Any]] = [
    {"id": "1", "productNo": "PRD20260001", "productName": "家庭财产综合险A", "category": "财产险", "description": "家庭财产综合保障，含火灾、盗抢与水渍损失。", "premiumGuide": "1680 元/年起", "coverageCap": "500000", "status": "在售", "createdAt": "2026-03-06"},
    {"id": "2", "productNo": "PRD20260002", "productName": "城市家庭责任险B", "category": "责任险", "description": "覆盖第三者人身与财产损失责任。", "premiumGuide": "520 元/年起", "coverageCap": "1000000", "status": "在售", "createdAt": "2026-03-06"},
    {"id": "3", "productNo": "PRD20260003", "productName": "健康无忧百万医疗险", "category": "健康险", "description": "住院医疗与特药保障，含重疾住院扩展。", "premiumGuide": "365 元/年起", "coverageCap": "6000000", "status": "在售", "createdAt": "2026-03-06"},
    {"id": "4", "productNo": "PRD20260004", "productName": "安行无忧综合意外险", "category": "意外险", "description": "交通意外、意外医疗与住院津贴。", "premiumGuide": "299 元/年起", "coverageCap": "1000000", "status": "在售", "createdAt": "2026-03-06"},
    {"id": "5", "productNo": "PRD20260005", "productName": "安心一生终身寿险", "category": "寿险", "description": "终身身故保障与保单现金价值。", "premiumGuide": "12000 元/年起", "coverageCap": "1000000", "status": "在售", "createdAt": "2026-03-06"},
    {"id": "6", "productNo": "PRD20260006", "productName": "金盈年金养老计划", "category": "养老险", "description": "年金给付与养老金领取安排。", "premiumGuide": "8000 元/年起", "coverageCap": "3000000", "status": "在售", "createdAt": "2026-03-06"},
    {"id": "7", "productNo": "PRD20260007", "productName": "悦享高端门急诊医疗险", "category": "健康险", "description": "门急诊与体检增值服务。", "premiumGuide": "2500 元/年起", "coverageCap": "2000000", "status": "在售", "createdAt": "2026-03-06"},
    {"id": "8", "productNo": "PRD20260008", "productName": "车辆综合保险标准版", "category": "车险", "description": "车损、第三者与驾乘人员责任。", "premiumGuide": "3600 元/年起", "coverageCap": "2000000", "status": "在售", "createdAt": "2026-03-06"},
    {"id": "9", "productNo": "PRD20260009", "productName": "商户营业中断保障险", "category": "财产险", "description": "保障商户营业中断及固定成本损失。", "premiumGuide": "4200 元/年起", "coverageCap": "1500000", "status": "在售", "createdAt": "2026-03-06"},
    {"id": "10", "productNo": "PRD20260010", "productName": "雇主责任保障计划", "category": "责任险", "description": "覆盖雇员工伤与雇主责任赔偿。", "premiumGuide": "6800 元/年起", "coverageCap": "3000000", "status": "在售", "createdAt": "2026-03-06"},
    {"id": "11", "productNo": "PRD20260011", "productName": "跨境差旅意外保障", "category": "意外险", "description": "差旅意外、行李延误与医疗救援。", "premiumGuide": "199 元/次起", "coverageCap": "800000", "status": "在售", "createdAt": "2026-03-06"},
    {"id": "12", "productNo": "PRD20260012", "productName": "电商退货运费保障险", "category": "财产险", "description": "覆盖电商订单退货运费损失。", "premiumGuide": "99 元/年起", "coverageCap": "50000", "status": "在售", "createdAt": "2026-03-06"}
]

_next_product_id = 13


def allocate_product_no() -> str:
    d = date.today().strftime("%Y%m%d")
    prefix = f"PRD{d}"
    n = sum(1 for p in PRODUCTS if str(p.get("productNo", "")).startswith(prefix))
    return f"{prefix}{n + 1:04d}"


def list_products() -> List[Dict[str, Any]]:
    return list(PRODUCTS)


def get_product(product_id: str) -> Optional[Dict[str, Any]]:
    for p in PRODUCTS:
        if p.get("id") == product_id:
            return p
    return None


def get_conflicting_product_for_catalog_key(
    product_name: str, category: str, exclude_product_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    pn = (product_name or "").strip()
    cat = (category or "").strip()
    if not pn:
        return None
    for p in PRODUCTS:
        if (p.get("productName") or "").strip() != pn:
            continue
        if (p.get("category") or "").strip() != cat:
            continue
        if exclude_product_id is not None and str(p.get("id")) == str(exclude_product_id):
            continue
        return dict(p)
    return None


def create_product(data: Dict[str, Any]) -> Dict[str, Any]:
    global _next_product_id
    item = dict(data)
    item.setdefault("id", str(_next_product_id))
    item.setdefault("category", "")
    item.setdefault("description", "")
    item.setdefault("premiumGuide", "")
    item.setdefault("coverageCap", "0")
    item.setdefault("status", "在售")
    item.setdefault("createdAt", date.today().isoformat())
    _next_product_id += 1
    PRODUCTS.append(item)
    return item


def update_product(product_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    for idx, p in enumerate(PRODUCTS):
        if p.get("id") == product_id:
            updated = dict(p)
            updated.update(data)
            updated["id"] = product_id
            PRODUCTS[idx] = updated
            return updated
    return None


def delete_product(product_id: str) -> bool:
    for idx, p in enumerate(PRODUCTS):
        if p.get("id") == product_id:
            PRODUCTS.pop(idx)
            return True
    return False
