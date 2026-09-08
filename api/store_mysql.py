"""MySQL 版存储实现（与 customer_store / risk_store 函数签名一致）。"""

from datetime import date
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from api.database import get_session_factory
from api.orm_models import (
    BlacklistEntry,
    Customer,
    Policy,
    Product,
    RiskAlertRow,
    RiskRuleRow,
    UnderwritingCase,
    Claim,
    ServiceTicket,
    SalesChannel,
)
from api.preset_rules import PRESET_RULES
from api.rule_ir_codec import ir_from_json_str, ir_to_json_str
from rules_engine.schema import RiskRuleIR, RuleAction


def _session() -> Session:
    return get_session_factory()()


def _customer_to_dict(c: Customer) -> Dict[str, Any]:
    return {
        "id": str(c.id),
        "customerNo": c.customer_no,
        "name": c.name,
        "idType": c.id_type,
        "idNo": c.id_no,
        "phone": c.phone,
        "occupation": c.occupation,
        "level": c.level,
        "status": c.status,
        "photo": c.photo or "",
        "gender": c.gender or "未知",
        "address": c.address or "",
        "remark": c.remark or "",
        "createdAt": c.created_at or "",
    }


def list_customers() -> List[Dict[str, Any]]:
    db = _session()
    try:
        rows = db.scalars(select(Customer).order_by(Customer.id)).all()
        return [_customer_to_dict(c) for c in rows]
    finally:
        db.close()


def get_customer(customer_id: str) -> Optional[Dict[str, Any]]:
    db = _session()
    try:
        c = db.get(Customer, int(customer_id))
        return _customer_to_dict(c) if c else None
    except ValueError:
        return None
    finally:
        db.close()


def allocate_customer_no() -> str:
    """生成新的客户编号：C + 年份 + 四位序号（与内存版规则一致）。"""
    db = _session()
    try:
        y = date.today().year
        prefix = f"C{y}"
        rows = db.scalars(select(Customer.customer_no).where(Customer.customer_no.like(f"{prefix}%"))).all()
        max_seq = 0
        for no in rows:
            if not no or not str(no).startswith(prefix):
                continue
            tail = str(no)[len(prefix) :]
            if tail.isdigit() and len(tail) == 4:
                max_seq = max(max_seq, int(tail))
        return f"{prefix}{max_seq + 1:04d}"
    finally:
        db.close()


def create_customer(data: Dict[str, Any]) -> Dict[str, Any]:
    db = _session()
    try:
        item = dict(data)
        item.pop("customerNo", None)
        item["customerNo"] = allocate_customer_no()
        row = Customer(
            customer_no=item["customerNo"],
            name=item["name"],
            id_type=item.get("idType", "身份证"),
            id_no=item["idNo"],
            phone=item["phone"],
            occupation=item.get("occupation") or "",
            level=item.get("level", "普通"),
            status=item.get("status", "在保"),
            photo=(item.get("photo") or "").strip()[:512],
            gender=(item.get("gender") or "未知").strip()[:16] or "未知",
            address=(item.get("address") or "").strip()[:255],
            remark=(item.get("remark") or "").strip()[:512],
            created_at=item.get("createdAt") or date.today().isoformat(),
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return _customer_to_dict(row)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def update_customer(customer_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    db = _session()
    try:
        c = db.get(Customer, int(customer_id))
        if not c:
            return None
        key_map = {
            "customerNo": "customer_no",
            "name": "name",
            "idType": "id_type",
            "idNo": "id_no",
            "phone": "phone",
            "occupation": "occupation",
            "level": "level",
            "status": "status",
            "photo": "photo",
            "gender": "gender",
            "address": "address",
            "remark": "remark",
            "createdAt": "created_at",
        }
        for k, v in data.items():
            if v is None:
                continue
            if k == "customerNo":
                continue
            col = key_map.get(k)
            if col is not None:
                setattr(c, col, v)
        db.commit()
        db.refresh(c)
        return _customer_to_dict(c)
    except ValueError:
        return None
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def delete_customer(customer_id: str) -> bool:
    db = _session()
    try:
        c = db.get(Customer, int(customer_id))
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


def _policy_to_dict(p: Policy) -> Dict[str, Any]:
    return {
        "id": str(p.id),
        "policyNo": p.policy_no,
        "customerNo": p.customer_no,
        "productName": p.product_name,
        "premium": p.premium,
        "coverageAmount": p.coverage_amount,
        "startDate": p.start_date or "",
        "endDate": p.end_date or "",
        "status": p.status,
    }


def list_policies() -> List[Dict[str, Any]]:
    db = _session()
    try:
        rows = db.scalars(select(Policy).order_by(Policy.id)).all()
        return [_policy_to_dict(p) for p in rows]
    finally:
        db.close()


def get_policy(policy_id: str) -> Optional[Dict[str, Any]]:
    db = _session()
    try:
        p = db.get(Policy, int(policy_id))
        return _policy_to_dict(p) if p else None
    except ValueError:
        return None
    finally:
        db.close()


def create_policy(data: Dict[str, Any]) -> Dict[str, Any]:
    db = _session()
    try:
        item = dict(data)
        row = Policy(
            policy_no=item["policyNo"],
            customer_no=item["customerNo"],
            product_name=item["productName"],
            premium=str(item.get("premium", "0")),
            coverage_amount=str(item.get("coverageAmount", "0")),
            start_date=item.get("startDate"),
            end_date=item.get("endDate"),
            status=item.get("status", "生效中"),
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return _policy_to_dict(row)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def update_policy(policy_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    db = _session()
    try:
        p = db.get(Policy, int(policy_id))
        if not p:
            return None
        key_map = {
            "policyNo": "policy_no",
            "customerNo": "customer_no",
            "productName": "product_name",
            "premium": "premium",
            "coverageAmount": "coverage_amount",
            "startDate": "start_date",
            "endDate": "end_date",
            "status": "status",
        }
        for k, v in data.items():
            if v is None:
                continue
            col = key_map.get(k)
            if col is not None:
                setattr(p, col, str(v) if k in ("premium", "coverageAmount") else v)
        db.commit()
        db.refresh(p)
        return _policy_to_dict(p)
    except ValueError:
        return None
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def delete_policy(policy_id: str) -> bool:
    db = _session()
    try:
        p = db.get(Policy, int(policy_id))
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


def allocate_product_no() -> str:
    """按自然日生成 PRDyyyyMMdd + 当日序号（四位）。"""
    db = _session()
    try:
        d = date.today().strftime("%Y%m%d")
        prefix = f"PRD{d}"
        cnt = int(
            db.scalar(
                select(func.count()).select_from(Product).where(Product.product_no.like(f"{prefix}%"))
            )
            or 0
        )
        return f"{prefix}{cnt + 1:04d}"
    finally:
        db.close()


def _product_to_dict(p: Product) -> Dict[str, Any]:
    return {
        "id": str(p.id),
        "productNo": p.product_no,
        "productName": p.product_name,
        "category": p.category,
        "description": p.description,
        "premiumGuide": p.premium_guide,
        "coverageCap": p.coverage_cap,
        "status": p.status,
        "createdAt": p.created_at or "",
    }


def list_products() -> List[Dict[str, Any]]:
    db = _session()
    try:
        rows = db.scalars(select(Product).order_by(Product.id)).all()
        return [_product_to_dict(p) for p in rows]
    finally:
        db.close()


def get_conflicting_product_for_catalog_key(
    product_name: str, category: str, exclude_product_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    若已存在相同「险种 + 产品名称」的另一条主数据（非 exclude_product_id），返回该条，否则 None。
    用于防止标准目录项重复建档。
    """
    pn = (product_name or "").strip()
    cat = (category or "").strip()
    if not pn:
        return None
    db = _session()
    try:
        rows = db.scalars(
            select(Product).where(Product.product_name == pn, Product.category == cat)
        ).all()
        for p in rows:
            if exclude_product_id is not None and str(p.id) == str(exclude_product_id):
                continue
            return _product_to_dict(p)
        return None
    finally:
        db.close()


def get_product(product_id: str) -> Optional[Dict[str, Any]]:
    db = _session()
    try:
        p = db.get(Product, int(product_id))
        return _product_to_dict(p) if p else None
    except ValueError:
        return None
    finally:
        db.close()


def create_product(data: Dict[str, Any]) -> Dict[str, Any]:
    db = _session()
    try:
        item = dict(data)
        row = Product(
            product_no=item["productNo"],
            product_name=item["productName"],
            category=item.get("category") or "",
            description=item.get("description") or "",
            premium_guide=item.get("premiumGuide") or "",
            coverage_cap=str(item.get("coverageCap", "0")),
            status=item.get("status", "在售"),
            created_at=item.get("createdAt") or date.today().isoformat(),
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return _product_to_dict(row)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def update_product(product_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    db = _session()
    try:
        p = db.get(Product, int(product_id))
        if not p:
            return None
        key_map = {
            "productNo": "product_no",
            "productName": "product_name",
            "category": "category",
            "description": "description",
            "premiumGuide": "premium_guide",
            "coverageCap": "coverage_cap",
            "status": "status",
            "createdAt": "created_at",
        }
        for k, v in data.items():
            if v is None:
                continue
            col = key_map.get(k)
            if col is not None:
                setattr(p, col, str(v) if k == "coverageCap" else v)
        db.commit()
        db.refresh(p)
        return _product_to_dict(p)
    except ValueError:
        return None
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def delete_product(product_id: str) -> bool:
    db = _session()
    try:
        p = db.get(Product, int(product_id))
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


def allocate_underwriting_case_no() -> str:
    """投保单号：UW + yyyyMMdd + 当日四位序号。"""
    db = _session()
    try:
        d = date.today().strftime("%Y%m%d")
        prefix = f"UW{d}"
        cnt = int(
            db.scalar(
                select(func.count())
                .select_from(UnderwritingCase)
                .where(UnderwritingCase.case_no.like(f"{prefix}%"))
            )
            or 0
        )
        return f"{prefix}{cnt + 1:04d}"
    finally:
        db.close()


def _underwriting_to_dict(u: UnderwritingCase) -> Dict[str, Any]:
    return {
        "id": str(u.id),
        "caseNo": u.case_no,
        "customerNo": u.customer_no,
        "applicantName": u.applicant_name,
        "idNo": u.id_no,
        "productName": u.product_name,
        "premium": u.premium,
        "coverageAmount": u.coverage_amount,
        "channel": u.channel,
        "status": u.status,
        "riskScore": u.risk_score,
        "decisionNote": u.decision_note,
        "policyNo": u.policy_no or "",
        "createdAt": u.created_at or "",
        "updatedAt": u.updated_at or "",
    }


def list_underwriting_cases() -> List[Dict[str, Any]]:
    db = _session()
    try:
        rows = db.scalars(select(UnderwritingCase).order_by(UnderwritingCase.id.desc())).all()
        return [_underwriting_to_dict(u) for u in rows]
    finally:
        db.close()


def get_underwriting_case(case_id: str) -> Optional[Dict[str, Any]]:
    db = _session()
    try:
        u = db.get(UnderwritingCase, int(case_id))
        return _underwriting_to_dict(u) if u else None
    except ValueError:
        return None
    finally:
        db.close()


def create_underwriting_case(data: Dict[str, Any]) -> Dict[str, Any]:
    db = _session()
    try:
        item = dict(data)
        today = date.today().isoformat()
        row = UnderwritingCase(
            case_no=item.get("caseNo") or allocate_underwriting_case_no(),
            customer_no=item["customerNo"],
            applicant_name=item["applicantName"],
            id_no=item.get("idNo") or "",
            product_name=item["productName"],
            premium=str(item.get("premium", "0")),
            coverage_amount=str(item.get("coverageAmount", "0")),
            channel=item.get("channel") or "",
            status=item.get("status", "待受理"),
            risk_score=item.get("riskScore") or "",
            decision_note=item.get("decisionNote") or "",
            policy_no=item.get("policyNo") or None,
            created_at=item.get("createdAt") or today,
            updated_at=item.get("updatedAt") or today,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return _underwriting_to_dict(row)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def update_underwriting_case(case_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    db = _session()
    try:
        u = db.get(UnderwritingCase, int(case_id))
        if not u:
            return None
        key_map = {
            "caseNo": "case_no",
            "customerNo": "customer_no",
            "applicantName": "applicant_name",
            "idNo": "id_no",
            "productName": "product_name",
            "premium": "premium",
            "coverageAmount": "coverage_amount",
            "channel": "channel",
            "status": "status",
            "riskScore": "risk_score",
            "decisionNote": "decision_note",
            "policyNo": "policy_no",
            "createdAt": "created_at",
            "updatedAt": "updated_at",
        }
        for k, v in data.items():
            if v is None:
                continue
            col = key_map.get(k)
            if col is not None:
                if col == "policy_no" and v == "":
                    setattr(u, col, None)
                elif k in ("premium", "coverageAmount"):
                    setattr(u, col, str(v))
                else:
                    setattr(u, col, v)
        u.updated_at = date.today().isoformat()
        db.commit()
        db.refresh(u)
        return _underwriting_to_dict(u)
    except ValueError:
        return None
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def delete_underwriting_case(case_id: str) -> bool:
    db = _session()
    try:
        u = db.get(UnderwritingCase, int(case_id))
        if not u:
            return False
        db.delete(u)
        db.commit()
        return True
    except ValueError:
        return False
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def allocate_claim_no() -> str:
    """理赔案件号：CLM + yyyyMMdd + 当日四位序号。"""
    db = _session()
    try:
        d = date.today().strftime("%Y%m%d")
        prefix = f"CLM{d}"
        cnt = int(
            db.scalar(
                select(func.count()).select_from(Claim).where(Claim.claim_no.like(f"{prefix}%"))
            )
            or 0
        )
        return f"{prefix}{cnt + 1:04d}"
    finally:
        db.close()


def _claim_to_dict(c: Claim) -> Dict[str, Any]:
    return {
        "id": str(c.id),
        "claimNo": c.claim_no,
        "policyNo": c.policy_no,
        "customerNo": c.customer_no,
        "claimantName": c.claimant_name,
        "productName": c.product_name,
        "claimType": c.claim_type,
        "incidentReason": c.incident_reason,
        "incidentDate": c.incident_date,
        "reportDate": c.report_date,
        "claimAmount": c.claim_amount,
        "approvedAmount": c.approved_amount,
        "status": c.status,
        "decisionNote": c.decision_note,
        "createdAt": c.created_at or "",
        "updatedAt": c.updated_at or "",
    }


def list_claims() -> List[Dict[str, Any]]:
    db = _session()
    try:
        rows = db.scalars(select(Claim).order_by(Claim.id.desc())).all()
        return [_claim_to_dict(c) for c in rows]
    finally:
        db.close()


def get_claim(claim_id: str) -> Optional[Dict[str, Any]]:
    db = _session()
    try:
        c = db.get(Claim, int(claim_id))
        return _claim_to_dict(c) if c else None
    except ValueError:
        return None
    finally:
        db.close()


def create_claim(data: Dict[str, Any]) -> Dict[str, Any]:
    db = _session()
    try:
        item = dict(data)
        today = date.today().isoformat()
        row = Claim(
            claim_no=item.get("claimNo") or allocate_claim_no(),
            policy_no=item["policyNo"],
            customer_no=item["customerNo"],
            claimant_name=item["claimantName"],
            product_name=item["productName"],
            claim_type=item.get("claimType") or "",
            incident_reason=item.get("incidentReason") or "",
            incident_date=item.get("incidentDate") or "",
            report_date=item.get("reportDate") or "",
            claim_amount=str(item.get("claimAmount", "0")),
            approved_amount=str(item.get("approvedAmount", "") or ""),
            status=item.get("status", "待受理"),
            decision_note=item.get("decisionNote") or "",
            created_at=item.get("createdAt") or today,
            updated_at=item.get("updatedAt") or today,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return _claim_to_dict(row)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def update_claim(claim_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    db = _session()
    try:
        c = db.get(Claim, int(claim_id))
        if not c:
            return None
        key_map = {
            "claimNo": "claim_no",
            "policyNo": "policy_no",
            "customerNo": "customer_no",
            "claimantName": "claimant_name",
            "productName": "product_name",
            "claimType": "claim_type",
            "incidentReason": "incident_reason",
            "incidentDate": "incident_date",
            "reportDate": "report_date",
            "claimAmount": "claim_amount",
            "approvedAmount": "approved_amount",
            "status": "status",
            "decisionNote": "decision_note",
            "createdAt": "created_at",
            "updatedAt": "updated_at",
        }
        for k, v in data.items():
            if v is None:
                continue
            col = key_map.get(k)
            if col is not None:
                if k in ("claimAmount", "approvedAmount"):
                    setattr(c, col, str(v))
                else:
                    setattr(c, col, v)
        c.updated_at = date.today().isoformat()
        db.commit()
        db.refresh(c)
        return _claim_to_dict(c)
    except ValueError:
        return None
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def delete_claim(claim_id: str) -> bool:
    db = _session()
    try:
        c = db.get(Claim, int(claim_id))
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


def allocate_service_ticket_no() -> str:
    """工单编号：CS + yyyyMMdd + 当日四位序号。"""
    db = _session()
    try:
        d = date.today().strftime("%Y%m%d")
        prefix = f"CS{d}"
        cnt = int(
            db.scalar(
                select(func.count())
                .select_from(ServiceTicket)
                .where(ServiceTicket.ticket_no.like(f"{prefix}%"))
            )
            or 0
        )
        return f"{prefix}{cnt + 1:04d}"
    finally:
        db.close()


def _service_ticket_to_dict(t: ServiceTicket) -> Dict[str, Any]:
    return {
        "id": str(t.id),
        "ticketNo": t.ticket_no,
        "ticketType": t.ticket_type,
        "customerNo": t.customer_no,
        "contactName": t.contact_name,
        "phone": t.phone,
        "policyNo": t.policy_no,
        "category": t.category,
        "subject": t.subject,
        "content": t.content,
        "status": t.status,
        "handler": t.handler,
        "resolutionNote": t.resolution_note,
        "startDate": t.start_date or "",
        "endDate": t.end_date or "",
        "createdAt": t.created_at or "",
        "updatedAt": t.updated_at or "",
    }


def list_service_tickets() -> List[Dict[str, Any]]:
    db = _session()
    try:
        rows = db.scalars(select(ServiceTicket).order_by(ServiceTicket.id.desc())).all()
        return [_service_ticket_to_dict(x) for x in rows]
    finally:
        db.close()


def get_service_ticket(ticket_id: str) -> Optional[Dict[str, Any]]:
    db = _session()
    try:
        t = db.get(ServiceTicket, int(ticket_id))
        return _service_ticket_to_dict(t) if t else None
    except ValueError:
        return None
    finally:
        db.close()


def create_service_ticket(data: Dict[str, Any]) -> Dict[str, Any]:
    db = _session()
    try:
        item = dict(data)
        today = date.today().isoformat()
        row = ServiceTicket(
            ticket_no=item.get("ticketNo") or allocate_service_ticket_no(),
            ticket_type=item.get("ticketType", "投诉"),
            customer_no=item["customerNo"],
            contact_name=item["contactName"],
            phone=item.get("phone") or "",
            policy_no=item.get("policyNo") or "",
            category=item.get("category") or "",
            subject=item.get("subject") or "",
            content=item.get("content") or "",
            status=item.get("status", "待受理"),
            handler=item.get("handler") or "",
            resolution_note=item.get("resolutionNote") or "",
            start_date=item.get("startDate") or "",
            end_date=item.get("endDate") or "",
            created_at=item.get("createdAt") or today,
            updated_at=item.get("updatedAt") or today,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return _service_ticket_to_dict(row)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def update_service_ticket(ticket_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    db = _session()
    try:
        t = db.get(ServiceTicket, int(ticket_id))
        if not t:
            return None
        key_map = {
            "ticketNo": "ticket_no",
            "ticketType": "ticket_type",
            "customerNo": "customer_no",
            "contactName": "contact_name",
            "phone": "phone",
            "policyNo": "policy_no",
            "category": "category",
            "subject": "subject",
            "content": "content",
            "status": "status",
            "handler": "handler",
            "resolutionNote": "resolution_note",
            "startDate": "start_date",
            "endDate": "end_date",
            "createdAt": "created_at",
            "updatedAt": "updated_at",
        }
        for k, v in data.items():
            if v is None:
                continue
            col = key_map.get(k)
            if col is not None:
                setattr(t, col, v)
        t.updated_at = date.today().isoformat()
        db.commit()
        db.refresh(t)
        return _service_ticket_to_dict(t)
    except ValueError:
        return None
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def delete_service_ticket(ticket_id: str) -> bool:
    db = _session()
    try:
        t = db.get(ServiceTicket, int(ticket_id))
        if not t:
            return False
        db.delete(t)
        db.commit()
        return True
    except ValueError:
        return False
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def allocate_channel_code() -> str:
    """渠道编码：CH + yyyyMMdd + 当日四位序号（亦可由前端手工指定唯一编码）。"""
    db = _session()
    try:
        d = date.today().strftime("%Y%m%d")
        prefix = f"CH{d}"
        cnt = int(
            db.scalar(
                select(func.count())
                .select_from(SalesChannel)
                .where(SalesChannel.channel_code.like(f"{prefix}%"))
            )
            or 0
        )
        return f"{prefix}{cnt + 1:04d}"
    finally:
        db.close()


def _channel_to_dict(c: SalesChannel) -> Dict[str, Any]:
    return {
        "id": str(c.id),
        "channelCode": c.channel_code,
        "channelName": c.channel_name,
        "channelType": c.channel_type,
        "manager": c.manager,
        "commissionRule": c.commission_rule,
        "contactPhone": c.contact_phone,
        "status": c.status,
        "remark": c.remark,
        "createdAt": c.created_at or "",
        "updatedAt": c.updated_at or "",
    }


def list_channels() -> List[Dict[str, Any]]:
    db = _session()
    try:
        rows = db.scalars(select(SalesChannel).order_by(SalesChannel.id)).all()
        return [_channel_to_dict(c) for c in rows]
    finally:
        db.close()


def get_channel(channel_id: str) -> Optional[Dict[str, Any]]:
    db = _session()
    try:
        c = db.get(SalesChannel, int(channel_id))
        return _channel_to_dict(c) if c else None
    except ValueError:
        return None
    finally:
        db.close()


def create_channel(data: Dict[str, Any]) -> Dict[str, Any]:
    db = _session()
    try:
        item = dict(data)
        today = date.today().isoformat()
        cc = (item.get("channelCode") or "").strip()
        if not cc:
            cc = allocate_channel_code()
        row = SalesChannel(
            channel_code=cc,
            channel_name=item["channelName"],
            channel_type=item.get("channelType") or "",
            manager=item.get("manager") or "",
            commission_rule=item.get("commissionRule") or "",
            contact_phone=item.get("contactPhone") or "",
            status=item.get("status", "合作中"),
            remark=item.get("remark") or "",
            created_at=item.get("createdAt") or today,
            updated_at=item.get("updatedAt") or today,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return _channel_to_dict(row)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def update_channel(channel_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    db = _session()
    try:
        c = db.get(SalesChannel, int(channel_id))
        if not c:
            return None
        key_map = {
            "channelCode": "channel_code",
            "channelName": "channel_name",
            "channelType": "channel_type",
            "manager": "manager",
            "commissionRule": "commission_rule",
            "contactPhone": "contact_phone",
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
                setattr(c, col, v)
        c.updated_at = date.today().isoformat()
        db.commit()
        db.refresh(c)
        return _channel_to_dict(c)
    except ValueError:
        return None
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def delete_channel(channel_id: str) -> bool:
    db = _session()
    try:
        c = db.get(SalesChannel, int(channel_id))
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


def _bl_to_dict(b: BlacklistEntry) -> Dict[str, Any]:
    return {"id": str(b.id), "name": b.name, "idNo": b.id_no, "reason": b.reason, "status": b.status}


def list_blacklist() -> List[Dict[str, Any]]:
    db = _session()
    try:
        rows = db.scalars(select(BlacklistEntry).order_by(BlacklistEntry.id)).all()
        return [_bl_to_dict(x) for x in rows]
    finally:
        db.close()


def add_blacklist(item: Dict[str, Any]) -> Dict[str, Any]:
    d = dict(item)
    db = _session()
    try:
        row = BlacklistEntry(
            name=d["name"],
            id_no=d["idNo"],
            reason=d.get("reason", ""),
            status=d.get("status", "启用"),
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return _bl_to_dict(row)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def update_blacklist(item_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    db = _session()
    try:
        row = db.get(BlacklistEntry, int(item_id))
        if not row:
            return None
        patch = dict(data)
        if patch.get("name") is not None:
            row.name = patch["name"]
        if patch.get("idNo") is not None:
            row.id_no = patch["idNo"]
        if patch.get("reason") is not None:
            row.reason = patch["reason"]
        if patch.get("status") is not None:
            row.status = patch["status"]
        db.commit()
        db.refresh(row)
        return _bl_to_dict(row)
    except ValueError:
        return None
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def delete_blacklist(item_id: str) -> bool:
    db = _session()
    try:
        row = db.get(BlacklistEntry, int(item_id))
        if not row:
            return False
        db.delete(row)
        db.commit()
        return True
    except ValueError:
        return False
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _al_to_dict(a: RiskAlertRow) -> Dict[str, Any]:
    return {
        "id": str(a.id),
        "code": a.code,
        "type": a.alert_type,
        "desc": a.alert_desc,
        "level": a.risk_level,
    }


def list_alerts() -> List[Dict[str, Any]]:
    db = _session()
    try:
        rows = db.scalars(select(RiskAlertRow).order_by(RiskAlertRow.id)).all()
        return [_al_to_dict(x) for x in rows]
    finally:
        db.close()


def count_risk_alerts() -> int:
    db = _session()
    try:
        return int(db.scalar(select(func.count()).select_from(RiskAlertRow)) or 0)
    finally:
        db.close()


def ensure_risk_alerts_seeded() -> None:
    """按预警编号补全 risk_alerts：init 脚本若只插了 1 条，启动后仍会与内存版 12 条对齐。"""
    from api.risk_store import RISK_ALERT_SEED

    db = _session()
    try:
        codes = set(db.scalars(select(RiskAlertRow.code)).all())
        added = False
        for row in RISK_ALERT_SEED:
            if row["code"] in codes:
                continue
            db.add(
                RiskAlertRow(
                    code=row["code"],
                    alert_type=row["type"],
                    alert_desc=row["desc"],
                    risk_level=row["level"],
                )
            )
            codes.add(row["code"])
            added = True
        if added:
            db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def seed_risk_alerts_if_empty() -> None:
    """兼容旧名：改为按 code 补全缺失行。"""
    ensure_risk_alerts_seeded()


def ensure_blacklist_seeded() -> None:
    """按证件号补全 blacklist，与 api.risk_store.BLACKLIST_SEED 一致（不覆盖已有行）。"""
    from api.risk_store import BLACKLIST_SEED

    db = _session()
    try:
        id_nos = set(db.scalars(select(BlacklistEntry.id_no)).all())
        added = False
        for row in BLACKLIST_SEED:
            if row["idNo"] in id_nos:
                continue
            db.add(
                BlacklistEntry(
                    name=row["name"],
                    id_no=row["idNo"],
                    reason=row.get("reason", ""),
                    status=row.get("status", "启用"),
                )
            )
            id_nos.add(row["idNo"])
            added = True
        if added:
            db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def count_risk_rules() -> int:
    db = _session()
    try:
        return int(db.scalar(select(func.count()).select_from(RiskRuleRow)) or 0)
    finally:
        db.close()


def list_risk_rule_irs() -> List[RiskRuleIR]:
    db = _session()
    try:
        rows = (
            db.scalars(
                select(RiskRuleRow)
                .where(RiskRuleRow.enabled == 1)
                .order_by(RiskRuleRow.priority, RiskRuleRow.id)
            )
            .all()
        )
        return [ir_from_json_str(r.ir_json) for r in rows]
    finally:
        db.close()


def list_all_risk_rule_ids() -> List[str]:
    """返回 risk_rules 表中已存在的全部 rule_id（含 enabled=0），用于列表合并时区分「未入库」与「已停用」。"""
    db = _session()
    try:
        rows = db.scalars(select(RiskRuleRow.rule_id)).all()
        return [str(x) for x in rows]
    finally:
        db.close()


def list_risk_rules_api_rows() -> List[Dict[str, Any]]:
    db = _session()
    try:
        rows = (
            db.scalars(
                select(RiskRuleRow)
                .where(RiskRuleRow.enabled == 1)
                .order_by(RiskRuleRow.priority, RiskRuleRow.id)
            )
            .all()
        )
        return [
            {
                "rule_id": r.rule_id,
                "description_cn": r.description_cn,
                "action": r.action,
                "source": r.source,
            }
            for r in rows
        ]
    finally:
        db.close()


def seed_preset_rules_if_empty() -> None:
    if count_risk_rules() > 0:
        return
    db = _session()
    try:
        for ir in PRESET_RULES:
            action_val = ir.action.value if isinstance(ir.action, RuleAction) else str(ir.action)
            db.add(
                RiskRuleRow(
                    rule_id=ir.rule_id,
                    description_cn=ir.description_cn,
                    action=action_val,
                    source="preset",
                    ir_json=ir_to_json_str(ir),
                    priority=ir.priority,
                    enabled=1 if ir.enabled else 0,
                )
            )
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def sync_preset_rules_from_code() -> None:
    """
    将 api.preset_rules.PRESET_RULES 与 risk_rules 对齐：
    - 缺失的预设行：插入；
    - 已存在且 source=preset 的行：更新文案、动作、IR、优先级（保留 enabled，便于通过「停用」关闭预设）。
    - source=nl_parsed 的行：不覆盖。
    """
    db = _session()
    try:
        for ir in PRESET_RULES:
            action_val = ir.action.value if isinstance(ir.action, RuleAction) else str(ir.action)
            j = ir_to_json_str(ir)
            existing = db.scalar(select(RiskRuleRow).where(RiskRuleRow.rule_id == ir.rule_id))
            if existing is None:
                db.add(
                    RiskRuleRow(
                        rule_id=ir.rule_id,
                        description_cn=ir.description_cn,
                        action=action_val,
                        source="preset",
                        ir_json=j,
                        priority=ir.priority,
                        enabled=1 if ir.enabled else 0,
                    )
                )
            elif str(existing.source or "") == "preset":
                existing.description_cn = ir.description_cn
                existing.action = action_val
                existing.ir_json = j
                existing.priority = ir.priority
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def upsert_nl_risk_rule(ir: RiskRuleIR) -> None:
    """自然语言解析入库：新增或更新 nl_parsed；不修改 src=preset 的行。"""
    db = _session()
    try:
        existing = db.scalar(select(RiskRuleRow).where(RiskRuleRow.rule_id == ir.rule_id))
        action_val = ir.action.value if isinstance(ir.action, RuleAction) else str(ir.action)
        if existing is None:
            db.add(
                RiskRuleRow(
                    rule_id=ir.rule_id,
                    description_cn=ir.description_cn,
                    action=action_val,
                    source="nl_parsed",
                    ir_json=ir_to_json_str(ir),
                    priority=ir.priority,
                    enabled=1 if ir.enabled else 0,
                )
            )
        elif existing.source == "preset":
            pass
        else:
            existing.description_cn = ir.description_cn
            existing.action = action_val
            existing.ir_json = ir_to_json_str(ir)
            existing.priority = ir.priority
            existing.enabled = 1 if ir.enabled else 0
            existing.source = "nl_parsed"
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_risk_rule_row(rule_id: str) -> Optional[Dict[str, Any]]:
    """按 rule_id 读取一条规则（包含 enabled/priority/ir_json）。"""
    rid = (rule_id or "").strip()
    if not rid:
        return None
    db = _session()
    try:
        r = db.scalar(select(RiskRuleRow).where(RiskRuleRow.rule_id == rid))
        if r is None:
            return None
        return {
            "rule_id": r.rule_id,
            "description_cn": r.description_cn,
            "action": r.action,
            "source": r.source,
            "priority": int(r.priority or 0),
            "enabled": 1 if int(r.enabled or 0) == 1 else 0,
            "ir_json": r.ir_json,
        }
    finally:
        db.close()


def update_risk_rule_row(rule_id: str, patch: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    更新规则字段：
    - 允许更新 description_cn/action/priority/enabled
    - 不允许修改 rule_id/source/ir_json（避免破坏可执行 IR 一致性）
    """
    rid = (rule_id or "").strip()
    if not rid:
        return None
    db = _session()
    try:
        r = db.scalar(select(RiskRuleRow).where(RiskRuleRow.rule_id == rid))
        if r is None:
            return None
        if r.source == "preset":
            # 预设规则不允许直接修改（建议用 enabled 关闭）
            pass
        if patch.get("description_cn") is not None:
            r.description_cn = str(patch.get("description_cn") or "").strip()[:512]
        if patch.get("action") is not None:
            r.action = str(patch.get("action") or "").strip()[:64] or r.action
        if patch.get("priority") is not None:
            try:
                r.priority = int(patch.get("priority"))
            except Exception:
                pass
        if patch.get("enabled") is not None:
            v = patch.get("enabled")
            r.enabled = 1 if (v is True or str(v) == "1" or str(v).lower() == "true") else 0
        db.commit()
        db.refresh(r)
        return {
            "rule_id": r.rule_id,
            "description_cn": r.description_cn,
            "action": r.action,
            "source": r.source,
            "priority": int(r.priority or 0),
            "enabled": 1 if int(r.enabled or 0) == 1 else 0,
        }
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def delete_risk_rule_row(rule_id: str) -> bool:
    """删除一条规则（仅允许删除 nl_parsed；preset 建议通过 enabled 关闭）。"""
    rid = (rule_id or "").strip()
    if not rid:
        return False
    db = _session()
    try:
        r = db.scalar(select(RiskRuleRow).where(RiskRuleRow.rule_id == rid))
        if r is None:
            return False
        if str(r.source or "") == "preset":
            return False
        db.delete(r)
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def add_alert(item: Dict[str, Any]) -> Dict[str, Any]:
    d = dict(item)
    db = _session()
    try:
        code_in = d.get("code")
        row = RiskAlertRow(
            code=code_in or "PENDING",
            alert_type=d["type"],
            alert_desc=d["desc"],
            risk_level=d.get("level", "高"),
        )
        db.add(row)
        db.flush()
        if not code_in:
            row.code = f"AL{row.id:08d}"
        db.commit()
        db.refresh(row)
        return _al_to_dict(row)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
