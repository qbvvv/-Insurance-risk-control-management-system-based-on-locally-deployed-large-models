"""
售后与投诉工单 — 内存存储（无 DATABASE_URL 时使用）。
"""

from datetime import date
from typing import Any, Dict, List, Optional

SERVICE_TICKETS: List[Dict[str, Any]] = [
    {"id": "1", "ticketNo": "CS2026030601", "ticketType": "投诉", "customerNo": "C20260001", "contactName": "张伟", "phone": "13810012026", "policyNo": "P20260001", "category": "理赔时效", "subject": "理赔审核周期偏长", "content": "客户反馈提交材料后超过承诺时效仍未结案，要求跟进。", "status": "处理中", "handler": "客服-王某", "resolutionNote": "", "startDate": "2026-03-06", "endDate": "2026-03-10", "createdAt": "2026-03-06", "updatedAt": "2026-03-06"},
    {"id": "2", "ticketNo": "CS2026030602", "ticketType": "投诉", "customerNo": "C20260002", "contactName": "王晓芳", "phone": "13910022026", "policyNo": "P20260002", "category": "销售误导", "subject": "产品责任与宣传不符", "content": "称投保时业务员口头承诺与条款不一致。", "status": "已结案", "handler": "合规-李某", "resolutionNote": "已与客户沟通并出具说明函，客户无异议。", "startDate": "2026-03-04", "endDate": "2026-03-06", "createdAt": "2026-03-05", "updatedAt": "2026-03-06"},
    {"id": "3", "ticketNo": "CS2026030603", "ticketType": "售后", "customerNo": "C20260008", "contactName": "上官婉儿", "phone": "18610082026", "policyNo": "P20260008", "category": "保单变更", "subject": "车辆信息变更申请", "content": "客户更换车辆使用性质，申请批改。", "status": "处理中", "handler": "客服-赵宁", "resolutionNote": "", "startDate": "2026-03-07", "endDate": "2026-03-14", "createdAt": "2026-03-07", "updatedAt": "2026-03-07"},
    {"id": "4", "ticketNo": "CS2026030604", "ticketType": "售后", "customerNo": "C20260015", "contactName": "高梓轩", "phone": "15310152026", "policyNo": "P20260005", "category": "续保咨询", "subject": "高端医疗续保条件咨询", "content": "咨询是否可免等待期续保。", "status": "已结案", "handler": "客服-孙悦", "resolutionNote": "已说明续保规则并发送书面指引。", "startDate": "2026-03-08", "endDate": "2026-03-09", "createdAt": "2026-03-08", "updatedAt": "2026-03-08"},
    {"id": "5", "ticketNo": "CS2026030605", "ticketType": "投诉", "customerNo": "C20260010", "contactName": "吴思涵", "phone": "15610102026", "policyNo": "P20260010", "category": "核保时效", "subject": "加急核保未在承诺时间内反馈", "content": "团体雇主责任险加急案件，客户催促出具核保结论。", "status": "待受理", "handler": "", "resolutionNote": "", "startDate": "2026-03-09", "endDate": "2026-03-12", "createdAt": "2026-03-09", "updatedAt": "2026-03-09"},
    {"id": "6", "ticketNo": "CS2026030606", "ticketType": "售后", "customerNo": "C20260012", "contactName": "孙嘉怡", "phone": "15910122026", "policyNo": "P20260012", "category": "退保咨询", "subject": "电商退货运费险退保", "content": "店铺关闭申请退保与未使用保费退还。", "status": "处理中", "handler": "客服-周倩", "resolutionNote": "", "startDate": "2026-03-09", "endDate": "2026-03-16", "createdAt": "2026-03-09", "updatedAt": "2026-03-10"},
    {"id": "7", "ticketNo": "CS2026030607", "ticketType": "投诉", "customerNo": "C20260004", "contactName": "欧阳子涵", "phone": "13610042026", "policyNo": "P20260004", "category": "增值服务", "subject": "体检预约失败", "content": "高端医疗附赠体检多次预约失败，要求协调。", "status": "已结案", "handler": "运营-郑某", "resolutionNote": "已协调合作机构完成预约并致歉。", "startDate": "2026-03-08", "endDate": "2026-03-09", "createdAt": "2026-03-08", "updatedAt": "2026-03-09"},
    {"id": "8", "ticketNo": "CS2026030608", "ticketType": "售后", "customerNo": "C20260007", "contactName": "赵磊", "phone": "18710072026", "policyNo": "P20260007", "category": "发票与凭证", "subject": "电子发票抬头错误", "content": "企业投保人申请重开增值税发票。", "status": "处理中", "handler": "财务-刘某", "resolutionNote": "", "startDate": "2026-03-11", "endDate": "2026-03-18", "createdAt": "2026-03-11", "updatedAt": "2026-03-11"},
]

_next_id = 9


def allocate_ticket_no() -> str:
    d = date.today().strftime("%Y%m%d")
    prefix = f"CS{d}"
    n = sum(1 for t in SERVICE_TICKETS if str(t.get("ticketNo", "")).startswith(prefix))
    return f"{prefix}{n + 1:04d}"


def list_service_tickets() -> List[Dict[str, Any]]:
    return list(SERVICE_TICKETS)


def get_service_ticket(ticket_id: str) -> Optional[Dict[str, Any]]:
    for t in SERVICE_TICKETS:
        if t.get("id") == ticket_id:
            return t
    return None


def create_service_ticket(data: Dict[str, Any]) -> Dict[str, Any]:
    global _next_id
    item = dict(data)
    item.setdefault("id", str(_next_id))
    if not item.get("ticketNo"):
        item["ticketNo"] = allocate_ticket_no()
    item.setdefault("phone", "")
    item.setdefault("policyNo", "")
    item.setdefault("category", "")
    item.setdefault("subject", "")
    item.setdefault("content", "")
    item.setdefault("status", "待受理")
    item.setdefault("handler", "")
    item.setdefault("resolutionNote", "")
    item.setdefault("startDate", "")
    item.setdefault("endDate", "")
    today = date.today().isoformat()
    item.setdefault("createdAt", today)
    item.setdefault("updatedAt", today)
    _next_id += 1
    SERVICE_TICKETS.append(item)
    return item


def update_service_ticket(ticket_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    for idx, t in enumerate(SERVICE_TICKETS):
        if t.get("id") == ticket_id:
            updated = dict(t)
            updated.update(data)
            updated["id"] = ticket_id
            updated["updatedAt"] = date.today().isoformat()
            SERVICE_TICKETS[idx] = updated
            return updated
    return None


def delete_service_ticket(ticket_id: str) -> bool:
    for idx, t in enumerate(SERVICE_TICKETS):
        if t.get("id") == ticket_id:
            SERVICE_TICKETS.pop(idx)
            return True
    return False
