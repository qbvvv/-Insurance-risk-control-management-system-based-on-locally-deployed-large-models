"""
风控与规则管理 + 自然语言规则解析 API。
提供：黑名单/预警列表、自然语言转规则、规则执行测试。
"""

import json
import re
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, Header, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator, model_validator
from sqlalchemy.exc import IntegrityError

from api.store_proxy import (
    add_alert,
    add_blacklist,
    delete_blacklist,
    allocate_channel_code,
    allocate_claim_no,
    allocate_commission_settlement_no,
    allocate_premium_flow_no,
    allocate_reinsurance_bill_no,
    allocate_reinsurance_contract_no,
    allocate_agent_no,
    allocate_agent_team_no,
    allocate_product_no,
    allocate_service_ticket_no,
    allocate_underwriting_case_no,
    create_policy,
    create_customer,
    create_product,
    create_underwriting_case,
    create_claim,
    create_service_ticket,
    create_channel,
    create_premium_flow,
    create_commission_settlement,
    create_reinsurance_contract,
    create_reinsurance_bill,
    create_agent_team,
    create_agent,
    create_system_user,
    create_system_param,
    create_system_log,
    delete_policy,
    delete_customer,
    delete_product,
    delete_underwriting_case,
    delete_claim,
    delete_service_ticket,
    delete_channel,
    delete_premium_flow,
    delete_commission_settlement,
    delete_reinsurance_contract,
    delete_reinsurance_bill,
    delete_agent_team,
    delete_agent,
    delete_system_user,
    delete_system_param,
    get_policy,
    get_customer,
    get_product,
    get_conflicting_product_for_catalog_key,
    get_underwriting_case,
    get_claim,
    get_service_ticket,
    get_channel,
    get_premium_flow,
    get_commission_settlement,
    get_reinsurance_contract,
    get_reinsurance_bill,
    get_agent_team,
    get_agent,
    get_agent_performance_summary,
    get_system_user,
    get_system_param,
    list_alerts,
    list_blacklist,
    list_policies,
    list_customers,
    list_products,
    list_underwriting_cases,
    list_claims,
    list_service_tickets,
    list_channels,
    list_premium_flows,
    list_commission_settlements,
    list_reinsurance_contracts,
    list_reinsurance_bills,
    list_agent_teams,
    list_agents,
    list_system_users,
    list_system_params,
    list_system_logs,
    seed_agent_demo_data_if_empty,
    seed_system_demo_data_if_empty,
    update_policy,
    update_customer,
    update_product,
    update_underwriting_case,
    update_claim,
    update_service_ticket,
    update_channel,
    update_blacklist,
    update_premium_flow,
    update_commission_settlement,
    update_reinsurance_contract,
    update_reinsurance_bill,
    update_agent_team,
    update_agent,
    update_system_user,
    update_system_param,
)
from api.rule_helpers import build_ir_from_llm_json

app = FastAPI(title="风控与规则管理 API")

# 简化版会话：内存 token 存储（重启服务后失效，满足当前毕设/演示登录管理需求）
_AUTH_SESSIONS: Dict[str, Dict[str, Any]] = {}

# 客户本地上传照片存储目录（通过 POST /customers/upload_photo 写入，/static/customer_photos 访问）
CUSTOMER_PHOTO_DIR = Path(__file__).resolve().parent / "static" / "customer_photos"


def _ensure_customer_photo_dir() -> None:
    CUSTOMER_PHOTO_DIR.mkdir(parents=True, exist_ok=True)


def _allocate_policy_no() -> str:
    """根据已有保单号生成新的 P+数字 保单号（仅用于 POST 未传 policyNo 时）。"""
    mx = 0
    for p in list_policies():
        s = str(p.get("policyNo") or "").strip().upper()
        if s.startswith("P") and s[1:].isdigit():
            mx = max(mx, int(s[1:]))
    return f"P{mx + 1}"


# 运行方式示例：
#   uvicorn api.server:app --reload --port 8000
# Swagger 接口文档：
#   http://localhost:8000/docs

# 允许前端跨域（前端 dev 通常在 5173）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup_init_db() -> None:
    """配置 DATABASE_URL 时自动建表（表已存在不会删数据）。"""
    from api.database import db_enabled, init_db

    if db_enabled():
        init_db()
        from api.store_mysql import seed_preset_rules_if_empty

        seed_preset_rules_if_empty()
        from api.store_mysql import sync_preset_rules_from_code

        sync_preset_rules_from_code()
        seed_agent_demo_data_if_empty()
        seed_system_demo_data_if_empty()
        from api.store_mysql import ensure_blacklist_seeded, ensure_risk_alerts_seeded

        ensure_risk_alerts_seeded()
        ensure_blacklist_seeded()


# ---------- 请求/响应模型 ----------
# 这些类是 FastAPI 的“类型约束 + 文档来源”：
# - 前端请求体会被解析成对应的 Pydantic 模型
# - FastAPI 会自动生成 /docs 里的请求示例与字段说明


class ParseRuleRequest(BaseModel):
    """
    /parse_rule 入参（JSON body）

    输入字段：
    - rule_text: 业务人员的自然语言风控规则
      例如："同一用户3个月内理赔超过3次则标记为高风险"
    - prompt_variant: 提示词版本（影响大模型输出形式）
      默认："json_only"
    """
    rule_text: str
    # 不同 prompt 版本会让模型输出格式稍有不同（论文/消融用）
    prompt_variant: str = "json_only"


class ParseRuleResponse(BaseModel):
    """
    /parse_rule 出参

    输出字段：
    - parsed_rule: 结构化规则（dict）
      典型字段：
      - rule_id: 规则唯一标识
      - description_cn: 中文规则描述
      - entities: 规则涉及的业务实体列表
      - time_window: 时间窗口（如"3个月内"；没有则为 null）
      - condition_logic: 条件逻辑（自然语言）
      - threshold: 阈值描述
      - action: 命中动作（如"标记为高风险"、"拒赔"、"人工审核"）
      - confidence: 置信度（0~1）
    - saved_to_library: 是否已写入规则库（与预设完全相同时不会重复写入）
    """
    parsed_rule: Dict[str, Any]
    saved_to_library: bool = False


class EvaluateRuleRequest(BaseModel):
    """
    /evaluate_rule 入参（JSON body）

    输入字段：
    - record: 业务记录 dict（供规则引擎做条件匹配）
      规则引擎会尝试读取：
      - "{entity}_{field}"（例如 claim_count_3m）
      - 或直接读取 cond.field（例如 count_3m）
    - rule_text: 可选
      - 不填：对预设规则库全部规则进行评估
      - 填了：先解析 rule_text，再只对解析出的这一条规则评估
    """
    # 业务数据：规则引擎只关心 record 里是否存在某些字段
    record: Dict[str, Any]
    # 可选：如果提供 rule_text，则只对该条解析出来的规则做评估
    rule_text: Optional[str] = None


class EvaluateRuleResponse(BaseModel):
    """
    /evaluate_rule 出参

    输出字段：
    - hit: 是否命中（当前 record 是否满足任意一条规则）
    - details: 命中的规则列表
      每条包含：
      - rule_id
      - description_cn
      - action
      - action_params
    """
    hit: bool
    details: List[Dict[str, Any]]


class ParseTestRecordRequest(BaseModel):
    """将自然语言业务描述解析为规则执行用记录。"""

    text: str


class ParseTestRecordResponse(BaseModel):
    record: Dict[str, Any]


class SaveParsedRuleRequest(BaseModel):
    """将前端已解析的结构化规则写入规则库。"""

    parsed_rule: Dict[str, Any]


class SaveParsedRuleResponse(BaseModel):
    rule_id: str
    saved_to_library: bool
    message: str


class QueryRuleMatchedCustomersRequest(BaseModel):
    """按一条规则检索命中的客户列表。"""

    rule_text: Optional[str] = None
    parsed_rule: Optional[Dict[str, Any]] = None


class RuleMatchedCustomerItem(BaseModel):
    customer_id: str
    customer_no: str
    customer_name: str
    hit_details: List[Dict[str, Any]]


class QueryRuleMatchedCustomersResponse(BaseModel):
    hit_count: int
    items: List[RuleMatchedCustomerItem]


class ApplyRuleActionsRequest(BaseModel):
    rule_text: Optional[str] = None
    parsed_rule: Optional[Dict[str, Any]] = None
    customer_ids: Optional[List[str]] = None


class ApplyRuleActionsResponse(BaseModel):
    affected_count: int
    items: List[Dict[str, Any]]


class RuleListItem(BaseModel):
    """
    /rules 单条规则信息（返回给前端展示）
    """
    rule_id: str
    description_cn: str
    action: str
    source: str = "preset"


class RuleDetailResponse(BaseModel):
    rule_id: str
    description_cn: str
    action: str
    source: str = "preset"
    priority: int = 100
    enabled: int = 1


class UpdateRuleRequest(BaseModel):
    description_cn: Optional[str] = None
    action: Optional[str] = None
    priority: Optional[int] = None
    enabled: Optional[int] = None


class CustomerBase(BaseModel):
    """
    customers 相关的“客户基础字段”（创建/更新的主要字段来源）。
    说明：后端内部主键 id 会由 server 在创建时生成，入参通常不需要 id。
    """
    customerNo: str
    name: str
    idType: str = "身份证"
    idNo: str
    phone: str
    occupation: Optional[str] = ""
    level: Optional[str] = "普通"
    status: Optional[str] = "在保"
    photo: str = ""
    gender: str = "未知"
    address: str = ""
    remark: str = ""
    createdAt: Optional[str] = None


class CustomerCreate(BaseModel):
    """POST /customers：客户编号 customerNo 无需传，由后端统一生成。"""

    customerNo: Optional[str] = None
    name: str
    idType: str = "身份证"
    idNo: str
    phone: str
    occupation: Optional[str] = ""
    level: Optional[str] = "普通"
    status: Optional[str] = "在保"
    photo: str = ""
    gender: str = "未知"
    address: str = ""
    remark: str = ""
    createdAt: Optional[str] = None


class CustomerUpdate(BaseModel):
    """
    PUT /customers/{customer_id} 入参（字段可选，只更新非 None 的内容）
    """
    customerNo: Optional[str] = None
    name: Optional[str] = None
    idType: Optional[str] = None
    idNo: Optional[str] = None
    phone: Optional[str] = None
    occupation: Optional[str] = None
    level: Optional[str] = None
    status: Optional[str] = None
    photo: Optional[str] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    remark: Optional[str] = None


class CustomerOut(CustomerBase):
    """
    GET/POST/PUT /customers 的返回结构（包含后端生成的 id）
    """
    id: str


class PolicyBase(BaseModel):
    """
    policies 相关“保单基础字段”。
    """

    policyNo: str
    customerNo: str
    productName: str
    premium: str = "0"
    coverageAmount: str = "0"
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    status: Optional[str] = "生效中"


class PolicyCreate(BaseModel):
    """POST /policies：policyNo 可省略，由后端自动生成。"""

    policyNo: Optional[str] = None
    customerNo: str
    productName: str
    premium: str = "0"
    coverageAmount: str = "0"
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    status: Optional[str] = "生效中"

    @field_validator("premium", "coverageAmount")
    @classmethod
    def validate_amount_fields(cls, v: str) -> str:
        s = (v or "").strip()
        if s == "":
            return "0"
        try:
            x = float(s.replace(",", ""))
        except ValueError:
            raise ValueError("保费、保额须为有效数字")
        if x < 0:
            raise ValueError("保费、保额不能为负数")
        if x > 1e13:
            raise ValueError("金额超出合理范围")
        return s


class PolicyUpdate(BaseModel):
    """
    PUT /policies/{policy_id} 入参（字段可选，只更新非 None 的内容）
    """

    policyNo: Optional[str] = None
    customerNo: Optional[str] = None
    productName: Optional[str] = None
    premium: Optional[str] = None
    coverageAmount: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    status: Optional[str] = None


class PolicyOut(PolicyBase):
    """
    GET/POST/PUT /policies 的返回结构（包含后端生成的 id）
    """

    id: str


class ProductBase(BaseModel):
    """保险产品主数据字段（与 policies.productName 可对应）。"""

    productNo: str
    productName: str
    category: str = ""
    description: str = ""
    premiumGuide: str = ""
    coverageCap: str = "0"
    status: str = "在售"
    createdAt: Optional[str] = None


class ProductCatalogItem(BaseModel):
    """标准产品目录条目（下拉选用，参考保费/保额由目录决定）。"""

    productName: str
    category: str
    premiumGuide: str
    coverageCap: str
    description: str


class ProductCreateRequest(BaseModel):
    """POST /products：选目录中的产品名称；编号由后端生成；可覆盖或补充产品说明。"""

    productName: str
    status: str = "在售"
    description: Optional[str] = None


class ProductUpdateBody(BaseModel):
    """PUT /products：可改状态、更换目录产品，或单独维护产品说明（编号不变）。"""

    productName: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None


class ProductOut(ProductBase):
    id: str


class UnderwritingCaseBase(BaseModel):
    """承保案件（投保单 / 核保记录）。"""

    caseNo: str
    customerNo: str
    applicantName: str
    idNo: str = ""
    productName: str
    premium: str = "0"
    coverageAmount: str = "0"
    channel: str = ""
    status: str = "待受理"
    riskScore: str = ""
    decisionNote: str = ""
    policyNo: Optional[str] = ""
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None


class UnderwritingCaseCreate(BaseModel):
    """
    受理端新建投保单：客户须已建档；投保人姓名与证件号一律以客户主数据为准；
    状态固定为「待受理」；不受理关联保单号与风险分（由后续核保环节维护）。
    """

    customerNo: str
    productName: str
    premium: str = "0"
    coverageAmount: str = "0"
    channel: str = ""
    decisionNote: str = ""


# 允许填写关联保单号的结案类状态（与前端一致）
_UW_POLICY_ALLOWED_STATUSES = frozenset({"已通过", "自动通过"})


class UnderwritingCaseUpdate(BaseModel):
    """PUT /underwriting_cases：仅允许更新流程与核保相关字段，不可篡改申请主体与标的。"""

    channel: Optional[str] = None
    status: Optional[str] = None
    riskScore: Optional[str] = None
    decisionNote: Optional[str] = None
    policyNo: Optional[str] = None


class UnderwritingCaseOut(UnderwritingCaseBase):
    id: str


class ClaimBase(BaseModel):
    """理赔案件。"""

    claimNo: str
    policyNo: str
    customerNo: str
    claimantName: str
    productName: str
    claimType: str = ""
    incidentReason: str = ""
    incidentDate: str = ""
    reportDate: str = ""
    claimAmount: str = "0"
    approvedAmount: str = ""
    status: str = "待受理"
    decisionNote: str = ""
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None


class ClaimCreate(BaseModel):
    """POST /claims：理赔案件号 claimNo 由后端生成（CLMyyyyMMdd + 四位序号）。"""

    policyNo: str
    customerNo: str
    claimantName: str
    productName: str
    claimType: str = ""
    incidentReason: str = ""
    incidentDate: str = ""
    reportDate: str = ""
    claimAmount: str = "0"
    approvedAmount: str = ""
    status: str = "待受理"
    decisionNote: str = ""


class ClaimUpdate(BaseModel):
    policyNo: Optional[str] = None
    customerNo: Optional[str] = None
    claimantName: Optional[str] = None
    productName: Optional[str] = None
    claimType: Optional[str] = None
    incidentReason: Optional[str] = None
    incidentDate: Optional[str] = None
    reportDate: Optional[str] = None
    claimAmount: Optional[str] = None
    approvedAmount: Optional[str] = None
    status: Optional[str] = None
    decisionNote: Optional[str] = None


class ClaimOut(ClaimBase):
    id: str


class ServiceTicketBase(BaseModel):
    """售后与投诉工单。"""

    ticketNo: str
    ticketType: str = "投诉"
    customerNo: str
    contactName: str
    phone: str = ""
    policyNo: str = ""
    category: str = ""
    subject: str = ""
    content: str = ""
    status: str = "待受理"
    handler: str = ""
    resolutionNote: str = ""
    startDate: str = ""
    endDate: str = ""
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None


class ServiceTicketCreate(BaseModel):
    """POST /service_tickets：工单号 ticketNo 由后端生成（CSyyyyMMdd + 四位序号）。"""

    ticketType: str = "投诉"
    customerNo: str
    contactName: str
    phone: str = ""
    policyNo: str = ""
    category: str = ""
    subject: str = ""
    content: str = ""
    status: str = "待受理"
    handler: str = ""
    resolutionNote: str = ""
    startDate: str = ""
    endDate: str = ""

    @model_validator(mode="after")
    def validate_plan_dates(self) -> "ServiceTicketCreate":
        s = (self.startDate or "").strip()
        e = (self.endDate or "").strip()
        if (s and not e) or (e and not s):
            raise ValueError("计划开始日期与结束日期须同时填写或同时留空")
        if s and e and e < s:
            raise ValueError("计划结束日期不能早于开始日期")
        return self


class ServiceTicketUpdate(BaseModel):
    """
    工单建档后仅允许更新处理环节字段，防止篡改客户、保单与原始诉求等主数据。
    """

    status: Optional[str] = None
    handler: Optional[str] = None
    resolutionNote: Optional[str] = None


class ServiceTicketOut(ServiceTicketBase):
    id: str


class ChannelBase(BaseModel):
    """销售渠道主数据。"""

    channelCode: str
    channelName: str
    channelType: str = ""
    manager: str = ""
    commissionRule: str = ""
    contactPhone: str = ""
    status: str = "合作中"
    remark: str = ""
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None


class ChannelCreate(BaseModel):
    """POST /channels：channelCode 留空则自动生成（CHyyyyMMdd + 四位序号）。"""

    channelCode: Optional[str] = None
    channelName: str
    channelType: str = ""
    manager: str = ""
    commissionRule: str = ""
    contactPhone: str = ""
    status: str = "合作中"
    remark: str = ""


class ChannelUpdate(BaseModel):
    """PUT /channels：不可修改 channelCode。"""

    channelName: Optional[str] = None
    channelType: Optional[str] = None
    manager: Optional[str] = None
    commissionRule: Optional[str] = None
    contactPhone: Optional[str] = None
    status: Optional[str] = None
    remark: Optional[str] = None


class ChannelOut(ChannelBase):
    id: str


class PremiumFlowBase(BaseModel):
    """保费收付流水。"""

    flowNo: str
    flowType: str
    policyNo: str
    amount: str = "0"
    payMethod: str = ""
    status: str = ""
    remark: str = ""
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None


class PremiumFlowCreate(BaseModel):
    """POST /premium_flows：flowNo 可空，空则 PF + 日期 + 序号。"""

    flowNo: Optional[str] = None
    flowType: str
    policyNo: str
    amount: str = "0"
    payMethod: str = ""
    status: str = ""
    remark: str = ""


class PremiumFlowUpdate(BaseModel):
    flowType: Optional[str] = None
    policyNo: Optional[str] = None
    amount: Optional[str] = None
    payMethod: Optional[str] = None
    status: Optional[str] = None
    remark: Optional[str] = None


class PremiumFlowOut(PremiumFlowBase):
    id: str


class CommissionSettlementBase(BaseModel):
    """佣金结算与对账。"""

    settlementNo: str
    channelName: str
    channelCode: str = ""
    period: str = ""
    commissionAmount: str = "0"
    reconcileStatus: str = ""
    remark: str = ""
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None


class CommissionSettlementCreate(BaseModel):
    """POST /commission_settlements：settlementNo 可空，空则 CM + 日期 + 序号。"""

    settlementNo: Optional[str] = None
    channelName: str
    channelCode: str = ""
    period: str = ""
    commissionAmount: str = "0"
    reconcileStatus: str = ""
    remark: str = ""


class CommissionSettlementUpdate(BaseModel):
    channelName: Optional[str] = None
    channelCode: Optional[str] = None
    period: Optional[str] = None
    commissionAmount: Optional[str] = None
    reconcileStatus: Optional[str] = None
    remark: Optional[str] = None


class CommissionSettlementOut(CommissionSettlementBase):
    id: str


class ReinsuranceContractBase(BaseModel):
    """再保合同。"""

    contractNo: str
    contractType: str = ""
    cedent: str = ""
    reinsurer: str = ""
    status: str = "生效"
    remark: str = ""
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None


class ReinsuranceContractCreate(BaseModel):
    """POST /reinsurance_contracts：contractNo 可空，空则 RC + 日期 + 序号。"""

    contractNo: Optional[str] = None
    contractType: str = ""
    cedent: str = ""
    reinsurer: str = ""
    status: str = "生效"
    remark: str = ""


class ReinsuranceContractUpdate(BaseModel):
    contractType: Optional[str] = None
    cedent: Optional[str] = None
    reinsurer: Optional[str] = None
    status: Optional[str] = None
    remark: Optional[str] = None


class ReinsuranceContractOut(ReinsuranceContractBase):
    id: str


class ReinsuranceBillBase(BaseModel):
    """分出/分入与再保账单（金额单位为万元）。"""

    billNo: str
    kind: str
    period: str = ""
    premium: str = "0"
    claimRecover: str = "0"
    remark: str = ""
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None


class ReinsuranceBillCreate(BaseModel):
    """POST /reinsurance_bills：billNo 可空，空则 RB + 日期 + 序号。"""

    billNo: Optional[str] = None
    kind: str
    period: str = ""
    premium: str = "0"
    claimRecover: str = "0"
    remark: str = ""


class ReinsuranceBillUpdate(BaseModel):
    kind: Optional[str] = None
    period: Optional[str] = None
    premium: Optional[str] = None
    claimRecover: Optional[str] = None
    remark: Optional[str] = None


class ReinsuranceBillOut(ReinsuranceBillBase):
    id: str


class AgentTeamBase(BaseModel):
    """代理人/团队组织架构。"""

    teamNo: str
    name: str
    title: str = ""
    parentTeamNo: str = ""
    parent: str = "-"
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None


class AgentTeamCreate(BaseModel):
    """POST /agent_teams：teamNo 可空，空则后端生成。"""

    teamNo: Optional[str] = None
    name: str
    title: str = ""
    parentTeamNo: str = ""


class AgentTeamUpdate(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    parentTeamNo: Optional[str] = None


class AgentTeamOut(AgentTeamBase):
    id: str


class AgentBase(BaseModel):
    """代理人主数据。"""

    agentNo: str
    name: str
    idNo: str = ""
    phone: str = ""
    teamNo: str = ""
    title: str = ""
    status: str = "在职"
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None


class AgentCreate(BaseModel):
    """POST /agents：agentNo 可空，空则后端生成。"""

    agentNo: Optional[str] = None
    name: str
    idNo: str = ""
    phone: str = ""
    teamNo: str = ""
    title: str = ""
    status: str = "在职"


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    idNo: Optional[str] = None
    phone: Optional[str] = None
    teamNo: Optional[str] = None
    title: Optional[str] = None
    status: Optional[str] = None


class AgentOut(AgentBase):
    id: str


class AgentPerformanceSummaryOut(BaseModel):
    name: str
    premium: str = "0"
    rate: str = "0%"
    period: Optional[str] = None


class AnalyticsSummaryOut(BaseModel):
    premiumTotalWan: str = "0"
    claimTotalWan: str = "0"
    claimRatioPercent: str = "0"
    customerCount: int = 0
    policyCount: int = 0
    claimCount: int = 0
    riskAlertCount: int = 0
    blacklistCount: int = 0


class SystemUserBase(BaseModel):
    username: str
    fullName: str = ""
    employeeNo: str = ""
    orgCode: str = ""
    department: str = ""
    post: str = ""
    role: str = ""
    dataScope: str = "本人"
    status: str = "启用"
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None


class SystemUserCreate(BaseModel):
    username: str
    fullName: str = ""
    employeeNo: str = ""
    orgCode: str = ""
    department: str = ""
    post: str = ""
    role: str = ""
    dataScope: str = "本人"
    status: str = "启用"


class SystemUserUpdate(BaseModel):
    fullName: Optional[str] = None
    employeeNo: Optional[str] = None
    orgCode: Optional[str] = None
    department: Optional[str] = None
    post: Optional[str] = None
    role: Optional[str] = None
    dataScope: Optional[str] = None
    status: Optional[str] = None


class SystemUserOut(SystemUserBase):
    id: str


class SystemParamBase(BaseModel):
    paramKey: str
    paramValue: str = ""
    description: str = ""
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None


class SystemParamCreate(BaseModel):
    paramKey: str
    paramValue: str = ""
    description: str = ""


class SystemParamUpdate(BaseModel):
    paramValue: Optional[str] = None
    description: Optional[str] = None


class SystemParamOut(SystemParamBase):
    id: str


class SystemLogOut(BaseModel):
    id: str
    logType: str
    actor: str
    action: str
    module: str = ""
    result: str = ""
    ip: str = ""
    createdAt: str = ""


class AuditPolicyOut(BaseModel):
    id: str
    action: str
    riskLevel: str
    requireReview: bool = False
    retentionDays: int = 180


class RoadmapItemOut(BaseModel):
    phase: str
    target: str
    deliverables: List[str] = []
    acceptance: str = ""


class AuthLoginRequest(BaseModel):
    username: str
    password: str


class AuthRegisterRequest(BaseModel):
    username: str
    password: str


class AuthUserOut(BaseModel):
    username: str
    role: str = ""
    status: str = "启用"
    dataScope: str = "本人"
    orgCode: str = ""


class AuthLoginResponse(BaseModel):
    token: str
    user: AuthUserOut
    permissions: List[str] = []
    menus: List[str] = []


class AuthResetPasswordRequest(BaseModel):
    username: str
    newPassword: str


class AuthForceLogoutRequest(BaseModel):
    username: str


@app.post("/auth/login", response_model=AuthLoginResponse)
def auth_login(req: AuthLoginRequest, request: Request) -> AuthLoginResponse:
    user = _validate_login(req.username, req.password)
    if not user:
        _write_audit_log("login", (req.username or "").strip() or "unknown", "登录失败", module="auth", result="failed", ip=request.client.host if request.client else "")
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = uuid.uuid4().hex
    role = str(user.get("role", "")).strip() or "普通用户"
    permissions = _permissions_for_role(role)
    menus = _menus_for_role(role)
    _AUTH_SESSIONS[token] = {
        "user": user,
        "permissions": permissions,
        "menus": menus,
        "created_at": datetime.utcnow().isoformat(),
    }
    _write_audit_log("login", str(user.get("username", "")).strip(), "登录成功", module="auth", result="success", ip=request.client.host if request.client else "")
    return AuthLoginResponse(token=token, user=AuthUserOut(**user), permissions=permissions, menus=menus)


@app.post("/auth/register", response_model=AuthLoginResponse)
def auth_register(req: AuthRegisterRequest) -> AuthLoginResponse:
    username = (req.username or "").strip()
    password = req.password or ""
    if len(username) < 3:
        raise HTTPException(status_code=400, detail="用户名至少 3 位")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="密码至少 6 位")
    if username == "admin":
        raise HTTPException(status_code=409, detail="该用户名不可用")

    try:
        created = create_system_user(
            {
                "username": username,
                "role": "普通用户",
                "status": "启用",
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except IntegrityError:
        raise HTTPException(status_code=409, detail="用户名已存在")

    _upsert_user_password(username, password)
    _upsert_user_meta(
        username,
        {
            "fullName": username,
            "employeeNo": "",
            "orgCode": "",
            "department": "",
            "post": "",
            "dataScope": "本人",
        },
    )
    user = _build_auth_user(
        str(created.get("username", "")).strip(),
        str(created.get("role", "")).strip() or "普通用户",
        str(created.get("status", "")).strip() or "启用",
        "本人",
        "",
    )
    token = uuid.uuid4().hex
    permissions = _permissions_for_role(str(user.get("role", "")).strip())
    menus = _menus_for_role(str(user.get("role", "")).strip())
    _AUTH_SESSIONS[token] = {
        "user": user,
        "permissions": permissions,
        "menus": menus,
        "created_at": datetime.utcnow().isoformat(),
    }
    _write_audit_log("register", username, "注册普通用户并自动登录", module="auth", result="success")
    return AuthLoginResponse(token=token, user=AuthUserOut(**user), permissions=permissions, menus=menus)


@app.get("/auth/me", response_model=AuthUserOut)
def auth_me(authorization: Optional[str] = Header(default=None)) -> AuthUserOut:
    user = _resolve_auth_user(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="登录状态已失效，请重新登录")
    return AuthUserOut(**user)


@app.post("/auth/logout")
def auth_logout(authorization: Optional[str] = Header(default=None)) -> Dict[str, bool]:
    header = (authorization or "").strip()
    if header.lower().startswith("bearer "):
        token = header[7:].strip()
        if token:
            session = _AUTH_SESSIONS.pop(token, None)
            if session:
                user = session.get("user") or {}
                _write_audit_log("logout", str(user.get("username", "")).strip() or "unknown", "退出登录", module="auth", result="success")
    return {"success": True}


@app.post("/auth/reset_password")
def auth_reset_password(req: AuthResetPasswordRequest, authorization: Optional[str] = Header(default=None)) -> Dict[str, bool]:
    username = (req.username or "").strip()
    new_password = req.newPassword or ""
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="新密码至少 6 位")
    if username == "admin":
        raise HTTPException(status_code=403, detail="管理员密码请通过受控方式修改")

    users = list_system_users()
    if not any(str(x.get("username", "")).strip() == username for x in users):
        raise HTTPException(status_code=404, detail="用户不存在")
    _upsert_user_password(username, new_password)
    actor = "system"
    current = _resolve_auth_user(authorization)
    if current:
        actor = str(current.get("username", "")).strip() or actor
    _write_audit_log("security", actor, f"重置用户密码：{username}", module="system", result="success")
    return {"success": True}


@app.post("/auth/force_logout")
def auth_force_logout(req: AuthForceLogoutRequest, authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    username = (req.username or "").strip()
    if not username:
        raise HTTPException(status_code=400, detail="用户名不能为空")
    removed = 0
    for token, session in list(_AUTH_SESSIONS.items()):
        user = session.get("user") or {}
        if str(user.get("username", "")).strip() == username:
            _AUTH_SESSIONS.pop(token, None)
            removed += 1
    actor = "system"
    current = _resolve_auth_user(authorization)
    if current:
        actor = str(current.get("username", "")).strip() or actor
    _write_audit_log("security", actor, f"强制下线用户：{username}", module="system", result="success")
    return {"success": True, "count": removed}


@app.get("/auth/sessions")
def auth_sessions() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for token, session in _AUTH_SESSIONS.items():
        user = session.get("user") or {}
        rows.append(
            {
                "token": token,
                "username": str(user.get("username", "")).strip(),
                "role": str(user.get("role", "")).strip(),
                "createdAt": str(session.get("created_at", "") or ""),
            }
        )
    return rows


class BlacklistItem(BaseModel):
    """
    POST /blacklist 入参

    输入字段：
    - name: 姓名
    - idNo: 证件号
    - reason: 列入原因
    - status: 启用/停用（默认启用）
    """
    name: str
    idNo: str
    reason: str
    status: str = "启用"


class BlacklistUpdateItem(BaseModel):
    name: Optional[str] = None
    idNo: Optional[str] = None
    reason: Optional[str] = None
    status: Optional[str] = None


class AlertItem(BaseModel):
    """
    POST /risk_alerts 入参

    输入字段：
    - type: 预警类型
    - desc: 预警说明
    - level: 风险等级（默认 高）
    """
    type: str
    desc: str
    level: str = "高"


# ---------- 自然语言转规则（NL -> JSON / IR） ----------
# 数据流概览：
# 1) 前端提交 rule_text（自然语言）
# 2) try：使用本地大模型（QwenRuleLLMParser）解析为 JSON
# 3) normalize_rule_json 做字段补全/校验
# 4) 最后：
#    - /parse_rule 直接把 JSON 返回给前端
#    - /evaluate_rule 再把 JSON 映射为规则引擎 IR（build_ir_from_llm_json）

# 与 rules_dataset.jsonl 一致的 rule_id 回退映射（关键词 -> rule_id）
# 元组结构：（必须包含的关键词...，最后一个元素是 rule_id）
# 注意：这是“降级方案”，当本地大模型未配置/解析失败时仍能跑通系统。
_NL_FALLBACK_RULE_IDS = [
    ("证件号", "7天", "投保", "id_no_apply_5_7d"),
    ("手机号", "证件号", "3", "phone_idno_link_verify_3"),
    ("设备指纹", "24", "申请", "device_apply_reject_24h_10"),
    ("被保险人", "75", "100万", "insured_age75_cov1m_manual"),
    ("同一地址", "30天", "高额", "address_high_new_30d_4"),
    ("保单生效", "7天", "理赔", "policy_effective_claim_7d_review"),
    ("夜间", "阈值", "理赔", "night_claim_amount_manual"),
    ("NLP", "相似", "客户", "claim_nlp_similar_cluster"),
    ("收款账户", "投保人", "首次", "payout_unrelated_first_high_review"),
    ("银行卡", "30天", "客户", "card_multi_customer_payout_30d"),
    ("黑名单", "关联网络", "赔付", "payout_blacklist_network_block"),
    ("收款账户", "24小时", "更换", "payout_account_change_reject_24h_2"),
    ("代理人", "早期出险", "渠道", "agent_early_loss_channel_alert_30d"),
    ("渠道", "高保额", "低保费", "channel_gbmi_anomaly_review"),
    ("代理人", "模板", "地址", "agent_template_input_qc"),
    ("证件号", "手机号", "黑名单", "blacklist_multi_dim_hit_reject"),
    ("确证欺诈", "共享", "关系点", "fraud_graph_shared_points_2"),
    ("新客户", "关系图谱", "首次", "new_customer_graph_strong_limit"),
    ("同一用户", "理赔", "3", "claim_freq_high_risk"),
    ("保单年度", "理赔", "5", "policy_year_claim_reject"),
    ("投保人", "年龄", "70", "elderly_manual_underwrite"),
    ("同一IP", "10", "ip_freq_abnormal"),
    ("理赔金额", "年度保费", "10", "claim_premium_ratio_review"),
    ("新用户", "7天", "理赔", "new_user_early_claim_review"),
    ("银行卡", "3", "保单", "card_multi_policy_alert"),
    ("夜间", "22", "6", "night_claim_manual"),
    ("收货地址", "5", "高额保单", "address_multi_high_policy_verify"),
]


ROLE_PERMISSION_TEMPLATE: Dict[str, List[str]] = {
    "系统管理员": ["*:*"],
    "承保岗": ["underwriting:view", "underwriting:edit", "policy:view"],
    "理赔岗": ["claim:view", "claim:edit", "policy:view"],
    "反欺诈岗": ["risk:view", "risk:edit", "blacklist:view", "blacklist:edit"],
    "财务岗": ["finance:view", "finance:edit"],
    "再保岗": ["reinsurance:view", "reinsurance:edit"],
    "审计岗": ["audit:view", "system_logs:view"],
    "普通用户": ["dashboard:view"],
}

ROLE_MENU_TEMPLATE: Dict[str, List[str]] = {
    "系统管理员": ["*"],
    "承保岗": ["/dashboard", "/underwriting", "/policy", "/customer", "/product"],
    "理赔岗": ["/dashboard", "/claim", "/policy", "/customer", "/service"],
    "反欺诈岗": ["/dashboard", "/risk-fraud", "/risk", "/customer"],
    "财务岗": ["/dashboard", "/finance", "/report", "/analytics"],
    "再保岗": ["/dashboard", "/reinsurance", "/policy", "/report"],
    "审计岗": ["/dashboard", "/report", "/analytics", "/system"],
    "普通用户": ["/dashboard"],
}

ALLOWED_SYSTEM_ROLES = frozenset(ROLE_PERMISSION_TEMPLATE.keys())
_ALLOWED_DATA_SCOPES = frozenset({"全部数据", "本机构数据", "本人"})
_USERNAME_LOGIN_PATTERN = re.compile(r"^[a-zA-Z0-9_]{3,32}$")


def _validate_system_user_fields(
    *,
    username: str,
    role: str,
    data_scope: str,
    status: str,
    full_name: str = "",
    employee_no: str = "",
    org_code: str = "",
    department: str = "",
    post: str = "",
    creating: bool,
) -> None:
    """与前端一致的系统用户字段校验及内置管理员治理约束。"""
    u = (username or "").strip()
    if not _USERNAME_LOGIN_PATTERN.match(u):
        raise HTTPException(status_code=400, detail="用户名须为 3-32 位字母、数字或下划线")
    role = (role or "").strip()
    if role not in ALLOWED_SYSTEM_ROLES:
        raise HTTPException(status_code=400, detail="角色不在系统允许范围内")
    ds = (data_scope or "").strip() or "本人"
    if ds not in _ALLOWED_DATA_SCOPES:
        raise HTTPException(status_code=400, detail="数据权限取值无效")
    st = (status or "").strip() or "启用"
    if st not in ("启用", "停用"):
        raise HTTPException(status_code=400, detail="状态取值无效")
    if creating and role == "系统管理员":
        raise HTTPException(status_code=400, detail="不允许新建系统管理员账号")
    if not creating and u != "admin" and role == "系统管理员":
        raise HTTPException(status_code=400, detail="不允许将用户提升为系统管理员")
    if u == "admin":
        if role != "系统管理员":
            raise HTTPException(status_code=400, detail="内置管理员角色不可修改")
        if ds != "全部数据":
            raise HTTPException(status_code=400, detail="内置管理员须使用「全部数据」数据权限")
        if st != "启用":
            raise HTTPException(status_code=400, detail="内置管理员账号不可停用")
    elif ds == "全部数据":
        raise HTTPException(status_code=400, detail="仅系统管理员可使用「全部数据」")
    if len((full_name or "").strip()) > 32:
        raise HTTPException(status_code=400, detail="姓名长度不可超过 32 个字符")
    en = (employee_no or "").strip()
    if len(en) > 32:
        raise HTTPException(status_code=400, detail="工号长度不可超过 32 位")
    if en and not re.match(r"^[A-Za-z0-9_-]+$", en):
        raise HTTPException(status_code=400, detail="工号仅允许字母、数字、下划线与短横线")
    oc = (org_code or "").strip().upper()
    if len(oc) > 32:
        raise HTTPException(status_code=400, detail="机构编码长度不可超过 32 位")
    if oc and not re.match(r"^[A-Z0-9/_-]+$", oc):
        raise HTTPException(status_code=400, detail="机构编码仅允许字母、数字、斜杠与短横线")
    if len((department or "").strip()) > 64:
        raise HTTPException(status_code=400, detail="部门名称过长")
    if len((post or "").strip()) > 64:
        raise HTTPException(status_code=400, detail="岗位名称过长")


def _build_auth_user(
    username: str,
    role: str = "系统管理员",
    status: str = "启用",
    data_scope: str = "本人",
    org_code: str = "",
) -> Dict[str, str]:
    return {
        "username": username,
        "role": role or "系统管理员",
        "status": status or "启用",
        "dataScope": data_scope or "本人",
        "orgCode": org_code or "",
    }


def _user_password_param_key(username: str) -> str:
    return f"auth_password_{username}"


def _user_meta_param_key(username: str) -> str:
    return f"auth_user_meta_{username}"


def _find_param_by_key(param_key: str) -> Optional[Dict[str, Any]]:
    key = (param_key or "").strip()
    if not key:
        return None
    for param in list_system_params():
        if str(param.get("paramKey", "")).strip() == key:
            return param
    return None


def _delete_param_by_key(param_key: str) -> None:
    p = _find_param_by_key(param_key)
    if p and p.get("id") is not None:
        delete_system_param(str(p.get("id")))


def _get_user_password(username: str) -> str:
    key = _user_password_param_key(username)
    param = _find_param_by_key(key)
    if param:
        return str(param.get("paramValue", "") or "")
    return ""


def _upsert_param_by_key(param_key: str, value: str, description: str) -> None:
    p = _find_param_by_key(param_key)
    if p and p.get("id") is not None:
        update_system_param(str(p.get("id")), {"paramValue": value, "description": description})
        return
    create_system_param({"paramKey": param_key, "paramValue": value, "description": description})


def _get_user_meta(username: str) -> Dict[str, Any]:
    key = _user_meta_param_key(username)
    p = _find_param_by_key(key)
    if not p:
        return {}
    raw = str(p.get("paramValue", "") or "").strip()
    if not raw:
        return {}
    try:
        obj = json.loads(raw)
        if isinstance(obj, dict):
            return obj
    except Exception:
        return {}
    return {}


def _upsert_user_password(username: str, password: str) -> None:
    key = _user_password_param_key(username)
    _upsert_param_by_key(key, password, f"登录密码（{username}）")


def _upsert_user_meta(username: str, meta: Dict[str, Any]) -> None:
    org_raw = str(meta.get("orgCode", "") or "").strip()
    safe_meta = {
        "fullName": str(meta.get("fullName", "") or "").strip(),
        "employeeNo": str(meta.get("employeeNo", "") or "").strip(),
        "orgCode": org_raw.upper() if org_raw else "",
        "department": str(meta.get("department", "") or "").strip(),
        "post": str(meta.get("post", "") or "").strip(),
        "dataScope": str(meta.get("dataScope", "") or "").strip() or "本人",
    }
    key = _user_meta_param_key(username)
    _upsert_param_by_key(key, json.dumps(safe_meta, ensure_ascii=False), f"用户扩展信息（{username}）")


def _build_user_with_meta(row: Dict[str, Any]) -> Dict[str, Any]:
    username = str(row.get("username", "") or "").strip()
    merged = dict(row)
    meta = _get_user_meta(username)
    merged["fullName"] = str(meta.get("fullName", merged.get("fullName", "") or ""))
    merged["employeeNo"] = str(meta.get("employeeNo", merged.get("employeeNo", "") or ""))
    merged["orgCode"] = str(meta.get("orgCode", merged.get("orgCode", "") or ""))
    merged["department"] = str(meta.get("department", merged.get("department", "") or ""))
    merged["post"] = str(meta.get("post", merged.get("post", "") or ""))
    ds = str(meta.get("dataScope", merged.get("dataScope", "") or "本人")).strip() or "本人"
    if username == "admin":
        merged["dataScope"] = "全部数据"
        if not (merged.get("orgCode") or "").strip():
            merged["orgCode"] = "HQ"
    else:
        merged["dataScope"] = ds
    return merged


def _permissions_for_role(role: str) -> List[str]:
    return list(ROLE_PERMISSION_TEMPLATE.get(role, ROLE_PERMISSION_TEMPLATE.get("普通用户", [])))


def _menus_for_role(role: str) -> List[str]:
    return list(ROLE_MENU_TEMPLATE.get(role, ROLE_MENU_TEMPLATE.get("普通用户", [])))


def _write_audit_log(log_type: str, actor: str, action: str, module: str = "", result: str = "", ip: str = "") -> None:
    suffix = ""
    if module or result or ip:
        suffix = f" | module={module or '-'} result={result or '-'} ip={ip or '-'}"
    try:
        create_system_log(
            {
                "logType": log_type or "info",
                "actor": actor or "system",
                "action": f"{action}{suffix}",
                "createdAt": datetime.utcnow().isoformat(),
            }
        )
    except Exception:
        # 审计日志失败不影响主业务流
        return


def _validate_login(username: str, password: str) -> Optional[Dict[str, str]]:
    u = (username or "").strip()
    p = password or ""
    if not u or not p:
        return None

    # 默认管理员账户（与登录页文案保持一致）
    if u == "admin" and p == "admin123":
        return _build_auth_user("admin", "系统管理员", "启用", "全部数据", "HQ")

    # 系统用户：优先使用注册时保存的密码；没有记录时兼容历史默认密码 123456
    users = list_system_users()
    for row in users:
        row = _build_user_with_meta(row)
        row_name = str(row.get("username", "")).strip()
        row_status = str(row.get("status", "启用")).strip()
        expected_password = _get_user_password(row_name) or "123456"
        if row_name == u and row_status != "停用" and p == expected_password:
            return _build_auth_user(
                row_name,
                str(row.get("role", "")).strip() or "普通用户",
                row_status,
                str(row.get("dataScope", "")).strip() or "本人",
                str(row.get("orgCode", "")).strip(),
            )
    return None


def _resolve_auth_session(authorization: Optional[str]) -> Optional[Dict[str, Any]]:
    header = (authorization or "").strip()
    if not header.lower().startswith("bearer "):
        return None
    token = header[7:].strip()
    if not token:
        return None
    session = _AUTH_SESSIONS.get(token)
    if not session:
        return None
    return session


def _resolve_auth_user(authorization: Optional[str]) -> Optional[Dict[str, Any]]:
    session = _resolve_auth_session(authorization)
    if not session:
        return None
    user = session.get("user") or {}
    return _build_auth_user(
        str(user.get("username", "")).strip(),
        str(user.get("role", "")).strip(),
        str(user.get("status", "")).strip() or "启用",
        str(user.get("dataScope", "")).strip() or "本人",
        str(user.get("orgCode", "")).strip(),
    )


def _parse_rule_with_fallback(rule_text: str, prompt_variant: str) -> Dict[str, Any]:
    try:
        # 尝试调用本地大模型解析器，把自然语言规则解析成 dict(JSON)
        from nlp_parser.parser_llm import QwenRuleLLMParser
        # 对模型 JSON 输出进行简单校验/补全，使字段尽量齐全
        from nlp_parser.postprocess import normalize_rule_json
        parser = QwenRuleLLMParser(prompt_variant=prompt_variant)
        raw = parser.parse_single_rule_to_dict(rule_text)
        norm = normalize_rule_json(raw)
        return _enrich_rule_json_from_text(rule_text, norm)
    except Exception:
        # 未配置模型或解析失败时：
        # 1) 用关键词直接映射到预设规则的 rule_id
        # 2) 让 build_ir_from_llm_json 能直接复用 preset IR，保证 evaluate_rule 可运行
        t = rule_text.strip()
        for parts in _NL_FALLBACK_RULE_IDS:
            if all(p in t for p in parts[:-1]):
                rule_id = parts[-1]
                from api.preset_rules import RULE_ID_TO_IR
                ir = RULE_ID_TO_IR.get(rule_id)
                if ir:
                    norm = {
                        "rule_id": rule_id,
                        "description_cn": ir.description_cn,
                        "entities": [],
                        "time_window": None,
                        "condition_logic": "",
                        "threshold": None,
                        "action": ir.action.value,
                        # confidence 只是一个“示意值”，说明是降级生成的
                        "confidence": 0.9,
                    }
                    return _enrich_rule_json_from_text(rule_text, norm)
        norm = {
            "rule_id": "demo_rule",
            "description_cn": t or "未识别规则",
            "entities": [],
            "time_window": None,
            "condition_logic": "",
            "threshold": None,
            "action": "manual_review",
            "confidence": 0.7,
        }
        # 兜底分支也做模板补全：让大多数常见规则句式至少能补齐阈值/时间窗/条件逻辑
        return _enrich_rule_json_from_text(rule_text, norm)


def _enrich_rule_json_from_text(rule_text: str, norm: Dict[str, Any]) -> Dict[str, Any]:
    """
    在大模型输出字段不全时，用规则模板补齐关键字段：
    - entities / time_window / condition_logic / threshold / action
    目标：让“多数常见规则模板”解析结果更像可执行规则（即便未接入完整业务数据源）。
    """
    import re

    t = (rule_text or "").strip()
    out = dict(norm or {})
    desc = str(out.get("description_cn") or t or "").strip()
    if not desc:
        return out

    # ---- action 关键词归一 ----
    action_text = (desc + " " + str(out.get("action") or "")).strip()
    if any(k in action_text for k in ("拒绝自动核保", "拒保", "禁止自动赔付", "禁止自动赔款")):
        out["action"] = "reject"
    elif any(k in action_text for k in ("预警",)):
        out["action"] = "alert"
    elif any(k in action_text for k in ("人工审核", "复核", "核验", "核查", "强制人工核保")):
        out["action"] = "manual_review"
    elif any(k in action_text for k in ("标记高风险", "高风险")):
        out["action"] = "tag_high_risk"

    # ---- 时间窗口识别 ----
    if not out.get("time_window"):
        if "24小时" in desc or "24 小时" in desc:
            out["time_window"] = "24h"
        elif "7天" in desc or "7 天" in desc:
            out["time_window"] = "7d"
        elif "30天" in desc or "30 天" in desc:
            out["time_window"] = "30d"
        elif "3个月" in desc or "三个月" in desc:
            out["time_window"] = "3m"

    # ---- 阈值提取（>= / >）----
    def _first_int(pattern: str) -> int | None:
        m = re.search(pattern, desc)
        if not m:
            return None
        try:
            return int(m.group(1))
        except Exception:
            return None

    # 100万 / 100 万
    def _money_to_yuan(s: str) -> int | None:
        s = (s or "").strip()
        m = re.search(r"(\\d+(?:\\.\\d+)?)\\s*万", s)
        if m:
            return int(float(m.group(1)) * 10000)
        m2 = re.search(r"(\\d+(?:\\.\\d+)?)\\s*元", s)
        if m2:
            return int(float(m2.group(1)))
        return None

    # ---- 模板补全（覆盖你截图里的大多数句式）----
    entities = list(out.get("entities") or [])
    cond = str(out.get("condition_logic") or "").strip()

    def _set_entities(*xs: str):
        nonlocal entities
        for x in xs:
            if x and x not in entities:
                entities.append(x)

    # 1) 同一证件号 7天 内 提交投保申请 >= N 次
    if ("证件号" in desc and "提交" in desc and "投保" in desc and ("7天" in desc or "7 天" in desc)):
        n = _first_int(r">=\\s*(\\d+)\\s*次") or _first_int(r">\\s*(\\d+)\\s*次")
        n = n or 5
        _set_entities("id_no", "policy")
        out["time_window"] = out.get("time_window") or "7d"
        out["threshold"] = out.get("threshold") or n
        out["condition_logic"] = cond or f"id_no.policy_apply_count_{out['time_window']} >= {n}"

    # 2) 同一手机号 关联 不同证件号 >= N 个（身份核验）
    if ("手机号" in desc or "手机" in desc) and ("证件号" in desc or "证件" in desc) and ("不同" in desc or "关联" in desc):
        n = _first_int(r">=\\s*(\\d+)\\s*个") or 3
        _set_entities("phone", "id_no")
        out["threshold"] = out.get("threshold") or n
        out["condition_logic"] = cond or f"phone.distinct_idno_count >= {n}"

    # 3) 同一设备指纹 24小时 内 提交申请 >= N 次（拒绝自动核保）
    if ("设备" in desc and ("24小时" in desc or "24 小时" in desc) and "提交" in desc and ("申请" in desc or "投保" in desc)):
        n = _first_int(r">=\\s*(\\d+)\\s*次") or 10
        _set_entities("device", "policy")
        out["time_window"] = out.get("time_window") or "24h"
        out["threshold"] = out.get("threshold") or n
        out["condition_logic"] = cond or f"device.apply_count_{out['time_window']} >= {n}"

    # 4) 年龄 > A 且 保额 > B万（强制人工核保/审核）
    if ("年龄" in desc and ("保额" in desc or "保费" in desc) and (">" in desc or ">=" in desc)):
        age = _first_int(r"年龄\\s*[>＝=]+\\s*(\\d+)") or _first_int(r"年龄\\s*>\\s*(\\d+)") or 75
        money = _money_to_yuan(desc) or 1000000
        _set_entities("applicant", "policy")
        out["threshold"] = out.get("threshold") or {"age_gt": age, "coverage_gt": money}
        out["condition_logic"] = cond or f"applicant.age > {age} AND policy.coverage_amount > {money}"

    # 5) 30天 同一地址 新增 高额保单 >= N 份
    if (("30天" in desc or "30 天" in desc) and ("同一地址" in desc or "同址" in desc) and "高额" in desc and ("保单" in desc)):
        n = _first_int(r">=\\s*(\\d+)\\s*份") or 4
        _set_entities("address", "policy")
        out["time_window"] = out.get("time_window") or "30d"
        out["threshold"] = out.get("threshold") or n
        out["condition_logic"] = cond or f"address.high_policy_new_count_{out['time_window']} >= {n}"

    # 6) 保单生效 <= 7天 即发生理赔（重点复核/人工）
    if ("保单" in desc and ("生效" in desc or "起保" in desc) and ("7天" in desc or "7 天" in desc) and "理赔" in desc):
        _set_entities("policy", "claim")
        out["time_window"] = out.get("time_window") or "7d"
        out["threshold"] = out.get("threshold") or 7
        out["condition_logic"] = cond or "user.claim_days_after_policy <= 7"

    # 7) 保单年度内 理赔次数 > N（拒赔/拒保）
    if (("年度" in desc or "年内" in desc) and "理赔" in desc and ("次数" in desc or "次" in desc)):
        n = _first_int(r">\\s*(\\d+)\\s*次") or 5
        _set_entities("policy", "claim")
        out["threshold"] = out.get("threshold") or n
        out["condition_logic"] = cond or f"policy.year_claim_count > {n}"

    # 8) 单次理赔金额 / 年保费比例 > N（复核）
    if ("理赔" in desc and ("年保费" in desc or "保费" in desc) and ("比例" in desc or "/" in desc) and (">" in desc or ">=" in desc)):
        n = _first_int(r">\\s*(\\d+)") or 10
        _set_entities("claim", "policy")
        out["threshold"] = out.get("threshold") or n
        out["condition_logic"] = cond or f"claim.premium_ratio > {n}"

    # 9) 夜间 22:00-06:00 提交理赔（+金额阈值可选）
    if ("夜间" in desc or "22:00" in desc or "06:00" in desc) and "理赔" in desc:
        _set_entities("claim")
        out["threshold"] = out.get("threshold") or "night_hours"
        out["condition_logic"] = cond or "claim.submit_hour in [22,23,0,1,2,3,4,5,6]"

    # 10) 24小时 内 更换收款账户 >= N 次（禁止自动赔付）
    if (("收款账户" in desc or "收款账号" in desc) and ("更换" in desc or "变更" in desc) and ("24小时" in desc or "24 小时" in desc)):
        n = _first_int(r">=\\s*(\\d+)\\s*次") or 2
        _set_entities("payout")
        out["time_window"] = out.get("time_window") or "24h"
        out["threshold"] = out.get("threshold") or n
        out["condition_logic"] = cond or f"payout.payee_account_change_count_{out['time_window']} >= {n}"

    # 11) 收款账户与投保人无关系 + 首次使用 + 金额较高（复核/核验）
    if ("收款账户" in desc or "收款账号" in desc) and ("无关系" in desc or "无关" in desc) and ("首次" in desc or "首笔" in desc) and ("金额" in desc or "较高" in desc):
        _set_entities("payout", "applicant")
        amt = _money_to_yuan(desc) or 50000
        out["threshold"] = out.get("threshold") or {"amount_ge": amt, "first_use": True, "related": False}
        out["condition_logic"] = cond or f"payout.payee_account_first_use == true AND payout.payee_account_related_to_applicant == false AND payout.amount >= {amt}"

    # 12) 同一银行卡 30天 内 被 >= N 个客户用于赔付收款（预警）
    if ("银行卡" in desc and ("30天" in desc or "30 天" in desc) and ("赔付" in desc or "赔款" in desc) and ("客户" in desc or "多人" in desc)):
        n = _first_int(r">=\\s*(\\d+)\\s*个") or 3
        _set_entities("card", "payout")
        out["time_window"] = out.get("time_window") or "30d"
        out["threshold"] = out.get("threshold") or n
        out["condition_logic"] = cond or f"card.payout_receiver_distinct_customer_count_{out['time_window']} >= {n}"

    # 13) 赔付账户历史命中黑名单关联网络（拦截/人工核验）
    if ("赔付" in desc and ("黑名单" in desc or "关联网络" in desc or "命中" in desc)):
        _set_entities("payout", "blacklist")
        out["threshold"] = out.get("threshold") or True
        out["condition_logic"] = cond or "payout.payee_account_blacklist_linked == true"

    # 14) 同一事故描述文本在多客户间高度相似（NLP 相似度高） -> 团伙嫌疑
    if ("事故" in desc and ("相似" in desc or "NLP" in desc or "相似度" in desc) and ("多客户" in desc or "多人" in desc or "团伙" in desc)):
        _set_entities("claim", "nlp")
        out["threshold"] = out.get("threshold") or {"similarity_ge": 0.9, "distinct_customers_ge": 3}
        out["condition_logic"] = cond or "claim.incident_text_similarity_max >= 0.9 AND claim.incident_text_similarity_distinct_customers >= 3"

    # 15) 代理人名下保单早期出险率（30天）显著高于渠道均值 x%
    if ("代理人" in desc and ("早期出险率" in desc or "出险率" in desc) and ("30天" in desc or "30 天" in desc) and ("渠道均值" in desc or "均值" in desc) and ("%" in desc or "百分" in desc)):
        _set_entities("agent", "channel")
        out["time_window"] = out.get("time_window") or "30d"
        m = re.search(r"(\\d+)\\s*%|百分之(\\d+)", desc)
        x = int((m.group(1) or m.group(2) or "20")) if m else 20
        out["threshold"] = out.get("threshold") or {"delta_percent": x, "window": out["time_window"]}
        out["condition_logic"] = cond or f"agent.early_claim_rate_{out['time_window']} >= channel.avg_early_claim_rate_{out['time_window']} * (1 + {x}/100)"

    # 16) 渠道短期内高保额低保费组合异常集中（渠道风控审查）
    if ("渠道" in desc and ("高保额" in desc and "低保费" in desc) and ("集中" in desc or "异常" in desc) and ("短期" in desc or "30天" in desc or "30 天" in desc)):
        _set_entities("channel", "policy")
        out["time_window"] = out.get("time_window") or ("30d" if ("30天" in desc or "30 天" in desc) else "short_term")
        out["threshold"] = out.get("threshold") or {"concentration_ge": 0.6, "window": out["time_window"]}
        out["condition_logic"] = cond or f"channel.high_coverage_low_premium_combo_concentration_{out['time_window']} >= 0.6"

    # 17) 代理人录入字段重复模板化明显（地址/职业异常一致） -> 质检
    if ("代理人" in desc and ("重复" in desc or "模板化" in desc) and ("地址" in desc or "职业" in desc) and ("质检" in desc or "检查" in desc)):
        _set_entities("agent", "customer")
        out["threshold"] = out.get("threshold") or {"field_consistency_ge": 0.9}
        out["condition_logic"] = cond or "agent.input_field_template_similarity >= 0.9"
        out["action"] = out.get("action") or "alert"

    # 18) 客户证件号/手机号/设备/IP 任一命中黑名单 -> 直接转人工或拒绝
    if ("命中黑名单" in desc and ("证件号" in desc or "手机号" in desc or "设备" in desc or "IP" in desc)):
        _set_entities("blacklist", "user")
        out["threshold"] = out.get("threshold") or True
        out["condition_logic"] = cond or "blacklist.hit_any_of[id_no,phone,device,ip] == true"
        # 默认转人工（若描述含“拒绝/拒保”则上面的 action 归一会变成 reject）
        out["action"] = out.get("action") or "manual_review"

    # 19) 与已确证欺诈客户共享关键关系点 >= 2（设备/地址/收款卡） -> 标记高风险
    if ("确证欺诈" in desc or "已确证欺诈" in desc) and ("共享" in desc or "关系点" in desc) and (">=" in desc or "≥" in desc):
        _set_entities("graph", "user")
        n = _first_int(r">=\\s*(\\d+)\\s*个") or _first_int(r"≥\\s*(\\d+)\\s*个") or 2
        out["threshold"] = out.get("threshold") or n
        out["condition_logic"] = cond or f"graph.shared_risk_relation_points >= {n}"
        out["action"] = out.get("action") or "tag_high_risk"

    # 20) 新客户首次投保即与高风险关系图谱强关联 -> 限制自动通过
    if ("新客户" in desc and "首次投保" in desc and ("关系图谱" in desc or "图谱" in desc) and ("强关联" in desc or "关联" in desc)):
        _set_entities("graph", "policy", "user")
        out["threshold"] = out.get("threshold") or {"is_first_policy": True, "risk_graph_strong_link": True}
        out["condition_logic"] = cond or "policy.is_first_for_user == true AND graph.strong_link_to_high_risk == true"
        out["action"] = out.get("action") or "manual_review"

    # entities 写回
    out["entities"] = entities

    # 最后兜底：仍为空则给一个可读的边界描述，避免前端展示“空”
    if not str(out.get("condition_logic") or "").strip():
        out["condition_logic"] = f"（待完善）{desc}"
    return out


def _parse_test_record_text(text: str) -> Dict[str, Any]:
    """自然语言业务描述 -> 规则执行记录（用于前端规则执行测试）。"""
    t = (text or "").strip()
    if not t:
        return {}
    rec: Dict[str, Any] = {}
    if "3个月" in t and "理赔" in t:
        rec["claim_count_3m"] = 4
    if ("年度" in t or "年内" in t) and "理赔" in t:
        rec["policy_year_claim_count"] = 6
    if "年龄" in t and ("70" in t or "老人" in t or "高龄" in t):
        rec["applicant_age"] = 75
    if "IP" in t and ("10" in t or "频繁" in t):
        rec["ip_daily_submit_count"] = 12
    if ("理赔" in t and "保费" in t) or "比例" in t:
        rec["claim_premium_ratio"] = 15
    if ("新用户" in t or "新客" in t) and ("7天" in t or "一周" in t):
        rec["user_claim_days_after_policy"] = 5
    if "银行卡" in t and ("多单" in t or "3" in t):
        rec["card_policy_count"] = 4
    if "夜间" in t or "凌晨" in t:
        rec["submit_hour"] = 23
    if ("地址" in t or "同址" in t) and ("高额" in t or "5" in t):
        rec["address_high_policy_count"] = 6
    # -------- 新增：覆盖更多“截图模板规则”的测试记录字段 --------
    # 同一手机号关联不同证件号 >= 3
    if ("手机号" in t or "手机" in t) and ("证件号" in t or "证件" in t) and ("不同" in t or "关联" in t):
        rec["phone_distinct_idno_count"] = 3
    # 同一设备指纹 24 小时内提交申请 >= 10
    if "设备" in t and ("24小时" in t or "24 小时" in t) and ("提交" in t and ("申请" in t or "投保" in t)):
        rec["device_apply_count_24h"] = 10
    # 同一证件号 7天内提交投保申请 >= 5
    if ("证件号" in t and ("7天" in t or "7 天" in t) and "投保" in t and "提交" in t):
        rec["idno_policy_apply_count_7d"] = 5
    # 30天 同一地址新增高额保单 >= 4
    if ("30天" in t or "30 天" in t) and ("同一地址" in t or "同址" in t) and "高额" in t and "保单" in t:
        rec["address_high_policy_new_count_30d"] = 4
    # 收款账户 24 小时内更换 >= 2 次
    if ("收款账户" in t or "收款账号" in t) and ("更换" in t or "变更" in t) and ("24小时" in t or "24 小时" in t):
        rec["payout_payee_account_change_count_24h"] = 2
    # 赔付账户命中黑名单关联网络
    if ("赔付" in t and ("黑名单" in t or "关联网络" in t or "命中" in t)):
        rec["payout_payee_account_blacklist_linked"] = True
    # NLP 相似度团伙嫌疑
    if ("事故" in t and ("相似" in t or "NLP" in t or "相似度" in t) and ("多客户" in t or "多人" in t or "团伙" in t)):
        rec["claim_incident_text_similarity_max"] = 0.92
        rec["claim_incident_text_similarity_distinct_customers"] = 3
    # 代理人早期出险率异常
    if ("代理人" in t and ("早期出险率" in t or "出险率" in t) and ("30天" in t or "30 天" in t) and ("渠道均值" in t or "均值" in t)):
        rec["agent_early_claim_rate_30d"] = 0.18
        rec["channel_avg_early_claim_rate_30d"] = 0.10
    # 渠道高保额低保费组合集中
    if ("渠道" in t and "高保额" in t and "低保费" in t and ("集中" in t or "异常" in t)):
        rec["channel_high_coverage_low_premium_combo_concentration_30d"] = 0.75
    # 代理人录入字段重复模板化明显（地址/职业异常一致）
    if ("代理人" in t and ("重复" in t or "模板化" in t) and ("地址" in t or "职业" in t)):
        rec["agent_input_field_template_similarity"] = 0.92
    # 客户证件号/手机号/设备/IP 任一命中黑名单
    if ("命中黑名单" in t and ("证件号" in t or "手机号" in t or "设备" in t or "IP" in t)):
        rec["blacklist_hit_any"] = True
    # 共享关键关系点 >= 2
    if ("共享" in t and ("关系点" in t or "设备" in t or "地址" in t or "收款卡" in t) and (">=" in t or "≥" in t)):
        rec["graph_shared_risk_relation_points"] = 2
    # 新客户首次投保 + 高风险关系图谱强关联
    if ("新客户" in t and "首次投保" in t and ("关系图谱" in t or "图谱" in t) and ("强关联" in t or "关联" in t)):
        rec["policy_is_first_for_user"] = True
        rec["graph_strong_link_to_high_risk"] = True
    if "用户" in t:
        rec.setdefault("user_id", "u1")
    if not rec:
        # 兜底：至少返回一个可读字段，提示用户再细化描述
        rec = {"user_id": "u1"}
    return rec


@app.post("/parse_rule", response_model=ParseRuleResponse)
def parse_rule(req: ParseRuleRequest) -> ParseRuleResponse:
    """
    POST /parse_rule

    输入字段（ParseRuleRequest）：
    - rule_text: 自然语言风控规则文本
    - prompt_variant: 提示词版本（默认 "json_only"）

    输出字段（ParseRuleResponse）：
    - parsed_rule: 解析后的结构化规则 dict（见 ParseRuleResponse 注释）
    """
    # 解析自然语言规则 -> 结构化 JSON（尽量使用本地大模型）
    norm = _parse_rule_with_fallback(req.rule_text, req.prompt_variant)
    return ParseRuleResponse(parsed_rule=norm, saved_to_library=False)


@app.post("/parse_test_record", response_model=ParseTestRecordResponse)
def parse_test_record(req: ParseTestRecordRequest) -> ParseTestRecordResponse:
    rec = _parse_test_record_text(req.text)
    return ParseTestRecordResponse(record=rec)


@app.post("/rules/add_parsed", response_model=SaveParsedRuleResponse)
def add_parsed_rule(req: SaveParsedRuleRequest) -> SaveParsedRuleResponse:
    """将解析后的结构化规则写入规则库（预设重复规则不会重复入库）。"""
    from api.rule_library import try_save_parsed_rule

    norm = dict(req.parsed_rule or {})
    if not norm:
        raise HTTPException(status_code=400, detail="parsed_rule 不能为空")
    ok, reason = _validate_parsed_rule_for_library(norm)
    if not ok:
        raise HTTPException(status_code=400, detail=reason)
    ir = build_ir_from_llm_json(norm)
    saved = try_save_parsed_rule(ir, norm)
    rid = str(norm.get("rule_id") or ir.rule_id or "")
    msg = "规则已加入规则库" if saved else "规则已存在于规则库，未重复写入"
    return SaveParsedRuleResponse(rule_id=rid, saved_to_library=saved, message=msg)


# ---------- 规则执行测试 ----------


@app.post("/evaluate_rule", response_model=EvaluateRuleResponse)
def evaluate_rule(req: EvaluateRuleRequest) -> EvaluateRuleResponse:
    """
    POST /evaluate_rule

    输入字段（EvaluateRuleRequest）：
    - record: 一条业务记录 dict
    - rule_text: 可选（不填则评估 preset_rules 全部规则；填了则只评估该条解析出的规则）

    输出字段（EvaluateRuleResponse）：
    - hit: 是否命中任意一条规则
    - details: 命中的规则列表
    """
    # 规则执行测试：
    # - 没有传 rule_text：对 preset_rules 全部规则跑一遍
    # - 传了 rule_text：先解析该条规则，再对 record 执行这一条规则
    from api.rule_library import get_executable_rules
    from rules_engine.rule_executor import RuleExecutor
    if req.rule_text:
        norm = _parse_rule_with_fallback(req.rule_text, "json_only")
        # 把 LLM JSON 映射为可执行 IR（可能直接返回 preset IR）
        ir = build_ir_from_llm_json(norm)
        rules = [ir]
    else:
        rules = get_executable_rules()
    executor = RuleExecutor(rules)
    hit, details = executor.evaluate_record(req.record)
    # hit：当前这条 record 是否命中“任意一条规则”
    # details：命中的规则列表（包含 rule_id、description_cn、action 等）
    return EvaluateRuleResponse(hit=hit, details=details)


def _parse_date_safe(s: str) -> Optional[date]:
    text = (s or "").strip()
    if not text:
        return None
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except Exception:
        return None


def _to_float(x: Any, default: float = 0.0) -> float:
    try:
        if x is None:
            return default
        return float(str(x).strip() or default)
    except Exception:
        return default


def _customer_rule_record(
    customer_no: str,
    claims: List[Dict[str, Any]],
    policies: List[Dict[str, Any]],
    customers: List[Dict[str, Any]],
) -> Dict[str, Any]:
    claim_rows = [c for c in claims if str(c.get("customerNo", "")).strip() == customer_no]
    policy_rows = [p for p in policies if str(p.get("customerNo", "")).strip() == customer_no]
    customer = next((x for x in customers if str(x.get("customerNo", "")).strip() == customer_no), {})
    today = date.today()
    three_months_ago = today - timedelta(days=90)
    claim_count_3m = 0
    policy_year_claim_count = 0
    latest_submit_hour = -1
    max_ratio = 0.0
    min_claim_days_after_policy: Optional[int] = None
    card_policy_count = len(policy_rows)

    policy_by_no = {str(p.get("policyNo", "")).strip(): p for p in policy_rows}
    for c in claim_rows:
        report_dt = _parse_date_safe(str(c.get("reportDate", "")))
        incident_dt = _parse_date_safe(str(c.get("incidentDate", "")))
        if report_dt and report_dt >= three_months_ago:
            claim_count_3m += 1
        if report_dt and report_dt.year == today.year:
            policy_year_claim_count += 1
        if report_dt:
            raw_h = c.get("submitHour") if c.get("submitHour") is not None else c.get("submit_hour")
            h = int(_to_float(raw_h, default=-1)) if raw_h is not None and str(raw_h).strip() != "" else -1
            if h >= 0:
                latest_submit_hour = max(latest_submit_hour, h)
            else:
                latest_submit_hour = max(latest_submit_hour, 23 if report_dt == today else 12)
        amt = _to_float(c.get("approvedAmount") or c.get("claimAmount") or 0.0)
        policy_no = str(c.get("policyNo", "")).strip()
        premium = _to_float(policy_by_no.get(policy_no, {}).get("premium"), 0.0)
        if premium > 0:
            max_ratio = max(max_ratio, amt / premium)
        start_dt = _parse_date_safe(str(policy_by_no.get(policy_no, {}).get("startDate", "")))
        if start_dt and report_dt:
            days = (report_dt - start_dt).days
            if min_claim_days_after_policy is None or days < min_claim_days_after_policy:
                min_claim_days_after_policy = days

    # 同址高额保单数：统计“与当前客户同地址”的客户下，保额 >= 300000 的保单数量
    cur_addr = str(customer.get("address", "")).strip()
    same_addr_customer_nos = {
        str(c.get("customerNo", "")).strip()
        for c in customers
        if str(c.get("address", "")).strip() and str(c.get("address", "")).strip() == cur_addr
    }
    address_high_policy_count = 0
    if cur_addr and same_addr_customer_nos:
        for p in policies:
            p_cno = str(p.get("customerNo", "")).strip()
            if p_cno not in same_addr_customer_nos:
                continue
            cov = _to_float(p.get("coverageAmount"), 0.0)
            if cov >= 300000:
                address_high_policy_count += 1

    # 同一手机号关联不同证件号数量（身份核验类规则）
    cur_phone = str(customer.get("phone", "")).strip()
    phone_to_idnos: Dict[str, set] = {}
    for cu in customers:
        ph = str(cu.get("phone") or "").strip()
        if not ph:
            continue
        phone_to_idnos.setdefault(ph, set()).add(str(cu.get("idNo") or "").strip())
    phone_distinct_idno_count = len(phone_to_idnos.get(cur_phone, set())) if cur_phone else 1

    return {
        "user_id": customer_no,
        "claim_count_3m": claim_count_3m,
        "policy_year_claim_count": policy_year_claim_count,
        "claim_premium_ratio": round(max_ratio, 2),
        "user_claim_days_after_policy": min_claim_days_after_policy if min_claim_days_after_policy is not None else 9999,
        "submit_hour": latest_submit_hour if latest_submit_hour >= 0 else 12,
        "card_policy_count": card_policy_count,
        "address_high_policy_count": address_high_policy_count,
        "phone_distinct_idno_count": phone_distinct_idno_count,
    }


def _validate_parsed_rule_for_library(norm: Dict[str, Any]) -> tuple[bool, str]:
    """规则库入库质量校验，避免随意输入文本直接入库。"""
    desc = str(norm.get("description_cn") or "").strip()
    rid = str(norm.get("rule_id") or "").strip()
    cond_logic = str(norm.get("condition_logic") or "").strip()
    threshold = str(norm.get("threshold") or "").strip()
    confidence_raw = norm.get("confidence")
    confidence = _to_float(confidence_raw, default=0.0)

    if len(desc) < 4:
        return False, "规则描述过短，无法确认业务语义，请补充具体条件"
    domain_keywords = (
        "理赔",
        "投保",
        "保单",
        "风险",
        "欺诈",
        "审核",
        "拒保",
        "预警",
        "黑名单",
        "高风险",
        "手机号",
        "证件",
        "证件号",
        "身份",
        "核验",
        "校验",
        "注册",
        "登录",
        "设备",
        "IP",
    )
    # 先构建 IR：若能构建出“非占位条件”，则不强制要求命中关键词白名单
    ir = build_ir_from_llm_json(norm)
    is_placeholder = (
        len(ir.conditions) == 1
        and ir.conditions[0].entity == "user"
        and ir.conditions[0].field == "risk_score"
        and ir.conditions[0].op == ">"
        and str(ir.conditions[0].value) in ("0", "0.0")
    )
    if not any(k in desc for k in domain_keywords) and is_placeholder:
        return False, "规则描述缺少风控业务语义，请输入可执行的风控规则"
    # rule_id 为 demo_rule/auto_rule_id 时允许入库，后续会自动生成 nl_ 前缀的新 rule_id
    # （由 api.rule_library.try_save_parsed_rule 负责生成并回写）
    if rid == "":
        return False, "该规则未形成有效 rule_id，请先解析出可用的规则标识后重试"
    # 若已明确命中预设规则（例如 policy_year_claim_reject），即使阈值字段为空也允许入库。
    from api.preset_rules import get_preset_by_rule_id

    preset = get_preset_by_rule_id(rid) if rid else None
    if not cond_logic and not threshold and preset is None and is_placeholder:
        return False, "规则缺少条件逻辑或阈值，无法判定执行边界"
    if is_placeholder:
        return False, "当前规则被解析为占位条件，请使用更明确的业务描述"

    # 若解析出了可执行条件，则允许较低置信度（身份核验类规则常见 0.7 左右）
    if confidence_raw is not None and confidence < 0.5:
        return False, "规则置信度偏低，请优化自然语言描述后重试"
    return True, ""


@app.post("/rules/query_matched_customers", response_model=QueryRuleMatchedCustomersResponse)
def query_rule_matched_customers(req: QueryRuleMatchedCustomersRequest) -> QueryRuleMatchedCustomersResponse:
    """按规则检索命中的客户（用于风控工作台快速定位风险客户）。"""
    from rules_engine.rule_executor import RuleExecutor

    if req.parsed_rule:
        norm = dict(req.parsed_rule)
    else:
        text = (req.rule_text or "").strip()
        if not text:
            raise HTTPException(status_code=400, detail="rule_text 与 parsed_rule 至少提供一个")
        norm = _parse_rule_with_fallback(text, "json_only")
    ir = build_ir_from_llm_json(norm)
    executor = RuleExecutor([ir])

    customers = list_customers()
    claims = list_claims()
    policies = list_policies()
    items: List[RuleMatchedCustomerItem] = []
    for c in customers:
        customer_no = str(c.get("customerNo", "")).strip()
        if not customer_no:
            continue
        record = _customer_rule_record(customer_no, claims, policies, customers)
        hit, details = executor.evaluate_record(record)
        if hit:
            items.append(
                RuleMatchedCustomerItem(
                    customer_id=str(c.get("id", "")),
                    customer_no=customer_no,
                    customer_name=str(c.get("name", "")),
                    hit_details=details,
                )
            )
    return QueryRuleMatchedCustomersResponse(hit_count=len(items), items=items)


@app.post("/rules/apply_actions", response_model=ApplyRuleActionsResponse)
def apply_rule_actions(req: ApplyRuleActionsRequest) -> ApplyRuleActionsResponse:
    """对命中客户执行规则动作：高风险标记/人工审核/拒保/预警。"""
    q = QueryRuleMatchedCustomersRequest(rule_text=req.rule_text, parsed_rule=req.parsed_rule)
    matched = query_rule_matched_customers(q)
    target_ids = set(str(x) for x in (req.customer_ids or []))
    rows = matched.items
    if target_ids:
        rows = [x for x in rows if x.customer_id in target_ids]

    customer_by_id = {str(c.get("id", "")): c for c in list_customers()}
    result_items: List[Dict[str, Any]] = []
    for row in rows:
        cid = row.customer_id
        c = customer_by_id.get(cid)
        if not c:
            continue
        patch: Dict[str, Any] = {}
        action_logs: List[str] = []
        for d in row.hit_details:
            action = str(d.get("action", "")).strip()
            desc = str(d.get("description_cn", "")).strip()
            if action == "tag_high_risk":
                patch["level"] = "高风险"
                action_logs.append("已标记高风险")
            elif action == "manual_review":
                patch["status"] = "人工审核"
                action_logs.append("已转人工审核")
            elif action == "reject":
                patch["status"] = "拒保"
                action_logs.append("已标记拒保")
                add_blacklist(
                    {
                        "name": c.get("name", ""),
                        "idNo": c.get("idNo", ""),
                        "reason": f"规则拒保：{desc or d.get('rule_id', '')}",
                        "status": "启用",
                    }
                )
            elif action == "alert":
                action_logs.append("已生成预警")
            else:
                action_logs.append("已记录风控动作")
            add_alert(
                {
                    "type": "规则命中",
                    "desc": f"客户{c.get('customerNo', '')}命中规则：{desc or d.get('rule_id', '')}",
                    "level": "高",
                }
            )
        if patch:
            update_customer(cid, patch)
        result_items.append(
            {
                "customer_id": cid,
                "customer_no": c.get("customerNo", ""),
                "customer_name": c.get("name", ""),
                "actions": action_logs,
            }
        )
    return ApplyRuleActionsResponse(affected_count=len(result_items), items=result_items)


# ---------- 预设规则列表（供前端展示/选择） ----------


@app.get("/rules", response_model=List[RuleListItem])
def list_rules():
    """
    GET /rules

    输入字段：无
    输出字段：
    - List[RuleListItem]，每条包含：
      { rule_id, description_cn, action, source }
    """
    from api.rule_library import list_rules_for_api

    rows = list_rules_for_api()
    return [
        RuleListItem(
            rule_id=r["rule_id"],
            description_cn=r["description_cn"],
            action=r["action"],
            source=r.get("source", "preset"),
        )
        for r in rows
    ]


@app.get("/rules/{rule_id}", response_model=RuleDetailResponse)
def get_rule_detail_api(rule_id: str):
    """读取规则详情（用于编辑/启停/优先级管理）。"""
    from api.rule_library import get_rule_detail

    row = get_rule_detail(rule_id)
    if not row:
        raise HTTPException(status_code=404, detail="规则不存在")
    return RuleDetailResponse(
        rule_id=str(row.get("rule_id") or ""),
        description_cn=str(row.get("description_cn") or ""),
        action=str(row.get("action") or ""),
        source=str(row.get("source") or "preset"),
        priority=int(row.get("priority") or 100),
        enabled=int(row.get("enabled") or 0),
    )


@app.put("/rules/{rule_id}", response_model=RuleDetailResponse)
def update_rule_api(rule_id: str, req: UpdateRuleRequest):
    """更新规则（描述/动作/优先级/启停）。"""
    from api.rule_library import update_rule

    patch: Dict[str, Any] = {}
    if req.description_cn is not None:
        patch["description_cn"] = req.description_cn
    if req.action is not None:
        patch["action"] = req.action
    if req.priority is not None:
        patch["priority"] = req.priority
    if req.enabled is not None:
        patch["enabled"] = req.enabled
    row = update_rule(rule_id, patch)
    if not row:
        raise HTTPException(status_code=400, detail="规则不可修改或不存在（预设规则建议仅启停）")
    return RuleDetailResponse(
        rule_id=str(row.get("rule_id") or ""),
        description_cn=str(row.get("description_cn") or ""),
        action=str(row.get("action") or ""),
        source=str(row.get("source") or "preset"),
        priority=int(row.get("priority") or 100),
        enabled=int(row.get("enabled") or 0),
    )


@app.delete("/rules/{rule_id}")
def delete_rule_api(rule_id: str):
    """删除规则（仅允许删除自然语言入库的 nl_parsed；preset 不允许删除）。"""
    from api.rule_library import delete_rule

    ok = delete_rule(rule_id)
    if not ok:
        raise HTTPException(status_code=400, detail="删除失败：预设规则不允许删除，或规则不存在")
    return {"deleted": True, "rule_id": rule_id}


# ---------- 黑名单 ----------


@app.get("/blacklist")
def get_blacklist() -> List[Dict[str, Any]]:
    """
    GET /blacklist

    输入字段：无
    输出字段（每条 dict）：
    - id: 后端内部ID
    - name: 姓名
    - idNo: 证件号
    - reason: 列入原因
    - status: 启用/停用
    """
    return list_blacklist()


@app.post("/blacklist")
def post_blacklist(item: BlacklistItem) -> Dict[str, Any]:
    """
    POST /blacklist

    输入字段（BlacklistItem）：
    - name / idNo / reason / status

    输出字段：
    - 新增后的整条记录 dict（包含后端自动生成的 id）
    """
    return add_blacklist(item.dict())


@app.put("/blacklist/{item_id}")
def put_blacklist(item_id: str, item: BlacklistUpdateItem) -> Dict[str, Any]:
    patch = {k: v for k, v in item.dict().items() if v is not None}
    if not patch:
        raise HTTPException(status_code=400, detail="无更新字段")
    row = update_blacklist(item_id, patch)
    if not row:
        raise HTTPException(status_code=404, detail="Blacklist item not found")
    return row


@app.delete("/blacklist/{item_id}")
def remove_blacklist(item_id: str) -> Dict[str, Any]:
    ok = delete_blacklist(item_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Blacklist item not found")
    return {"success": True}


# ---------- 风险预警 ----------


@app.get("/risk_alerts")
def get_risk_alerts() -> List[Dict[str, Any]]:
    """
    GET /risk_alerts

    输入字段：无
    输出字段（每条 dict）：
    - id: 后端内部ID
    - code: 预警编号（如 AL2026030601）
    - type: 预警类型
    - desc: 预警说明
    - level: 风险等级
    """
    return list_alerts()


@app.post("/risk_alerts")
def post_risk_alert(item: AlertItem) -> Dict[str, Any]:
    """
    POST /risk_alerts

    输入字段（AlertItem）：
    - type / desc / level

    输出字段：
    - 新增后的整条记录 dict（包含后端自动生成的 id/code）
    """
    return add_alert(item.dict())


# ---------- 保险客户管理 ----------


@app.get("/customers", response_model=List[CustomerOut])
def get_customers() -> List[CustomerOut]:
    """
    GET /customers

    输入字段：无
    输出字段：
    - List[CustomerOut]，包含客户完整信息：
      { id, customerNo, name, idType, idNo, phone, occupation, level, status, createdAt }
    """
    return [CustomerOut(**c) for c in list_customers()]


@app.post("/customers/upload_photo")
async def upload_customer_photo(request: Request, file: UploadFile = File(...)) -> Dict[str, str]:
    """
    上传客户照片（multipart，字段名 file）。返回可写入客户 photo 字段的完整 URL。
    须放在 /customers/{id} 相关路由旁，避免路径被误解析为 id。
    """
    _ensure_customer_photo_dir()
    ct = (file.content_type or "").lower()
    if not ct.startswith("image/"):
        raise HTTPException(status_code=400, detail="请上传图片文件（如 jpg、png）")
    raw = await file.read()
    if len(raw) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="图片大小请不超过 5MB")
    ext = Path(file.filename or "").suffix.lower()
    if ext not in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
        if "png" in ct:
            ext = ".png"
        elif "gif" in ct:
            ext = ".gif"
        elif "webp" in ct:
            ext = ".webp"
        else:
            ext = ".jpg"
    name = f"{uuid.uuid4().hex}{ext}"
    dest = CUSTOMER_PHOTO_DIR / name
    dest.write_bytes(raw)
    base = str(request.base_url).rstrip("/")
    photo_url = f"{base}/static/customer_photos/{name}"
    if len(photo_url) > 500:
        raise HTTPException(status_code=500, detail="生成的照片地址过长，请检查服务根路径配置")
    return {"photoUrl": photo_url}


@app.get("/customers/{customer_id}", response_model=CustomerOut)
def get_customer_api(customer_id: str) -> CustomerOut:
    """GET /customers/{customer_id}：按内部主键 id 查询单个客户。"""
    row = get_customer(customer_id)
    if not row:
        raise HTTPException(status_code=404, detail="Customer not found")
    return CustomerOut(**row)


@app.post("/customers", response_model=CustomerOut)
def post_customer(item: CustomerCreate) -> CustomerOut:
    """
    POST /customers

    输入字段（CustomerCreate）：
    - name / idType / idNo / phone（必填）
    - occupation / level / status / createdAt（可选）
    - customerNo 无需填写，由后端按「C+年份+四位序号」自动生成

    输出字段：
    - CustomerOut：包含后端生成的 id、customerNo 及全部客户字段
    """
    payload = item.dict()
    payload.pop("customerNo", None)
    created = create_customer(payload)
    return CustomerOut(**created)


@app.put("/customers/{customer_id}", response_model=CustomerOut)
def put_customer(customer_id: str, item: CustomerUpdate) -> CustomerOut:
    """
    PUT /customers/{customer_id}

    路径参数：
    - customer_id: 后端内部主键（字符串）

    输入字段：
    - CustomerUpdate：所有字段都可选，只更新你传入且不为 None 的字段

    输出字段：
    - 更新后的 CustomerOut

    失败情况：
    - 404: 找不到该 customer_id
    """
    exists = get_customer(customer_id)
    if not exists:
        raise HTTPException(status_code=404, detail="Customer not found")
    data = {k: v for k, v in item.dict().items() if v is not None}
    data.pop("customerNo", None)
    updated = update_customer(customer_id, data)
    if not updated:
        raise HTTPException(status_code=500, detail="Update failed")
    return CustomerOut(**updated)


@app.delete("/customers/{customer_id}")
def remove_customer(customer_id: str) -> Dict[str, Any]:
    """
    DELETE /customers/{customer_id}

    路径参数：
    - customer_id: 后端内部主键（字符串）

    输出字段：
    - {"success": true}（删除成功）

    失败情况：
    - 404: 找不到该 customer_id
    """
    ok = delete_customer(customer_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"success": True}


# ---------- 保单管理 ----------


@app.get("/policies", response_model=List[PolicyOut])
def get_policies() -> List[PolicyOut]:
    """
    GET /policies

    输入字段：无
    输出字段：
    - List[PolicyOut]，包含保单完整信息：
      { id, policyNo, customerNo, productName, premium, coverageAmount, startDate, endDate, status }
    """

    return [PolicyOut(**p) for p in list_policies()]


@app.post("/policies", response_model=PolicyOut)
def post_policy(item: PolicyCreate) -> PolicyOut:
    """
    POST /policies

    输入字段（PolicyCreate）：
    - policyNo：可选；省略或空串时由后端按已有保单号递增生成
    - customerNo / productName / premium / coverageAmount
    - startDate / endDate / status（可选）

    输出字段：
    - PolicyOut：包含后端生成的 id + 全部保单字段
    """

    d = item.model_dump()
    pn = (d.get("policyNo") or "").strip()
    d["policyNo"] = _allocate_policy_no() if not pn else pn
    created = create_policy(d)
    return PolicyOut(**created)


@app.put("/policies/{policy_id}", response_model=PolicyOut)
def put_policy(policy_id: str, item: PolicyUpdate) -> PolicyOut:
    """
    PUT /policies/{policy_id}

    路径参数：
    - policy_id: 后端内部主键（字符串）

    输入字段：
    - PolicyUpdate：所有字段都可选，只更新你传入且不为 None 的字段

    失败情况：
    - 404: 找不到该 policy_id
    """

    exists = get_policy(policy_id)
    if not exists:
        raise HTTPException(status_code=404, detail="Policy not found")
    data = {k: v for k, v in item.dict().items() if v is not None}
    updated = update_policy(policy_id, data)
    if not updated:
        raise HTTPException(status_code=500, detail="Update failed")
    return PolicyOut(**updated)


@app.delete("/policies/{policy_id}")
def remove_policy(policy_id: str) -> Dict[str, Any]:
    """
    DELETE /policies/{policy_id}

    路径参数：
    - policy_id: 后端内部主键（字符串）

    输出字段：
    - {"success": true}（删除成功）

    失败情况：
    - 404: 找不到该 policy_id
    """

    ok = delete_policy(policy_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Policy not found")
    return {"success": True}


# ---------- 产品管理 ----------


@app.get("/products/catalog", response_model=List[ProductCatalogItem])
def get_product_catalog() -> List[ProductCatalogItem]:
    """标准产品目录（名称 / 险种 / 参考保费 / 保额上限 / 说明），供前端下拉。"""
    from api.product_catalog import list_catalog

    return [ProductCatalogItem(**x) for x in list_catalog()]


@app.get("/products/categories")
def get_product_categories() -> List[str]:
    """险种类别列表（去重顺序与目录一致）。"""
    from api.product_catalog import list_categories

    return list_categories()


@app.get("/products", response_model=List[ProductOut])
def get_products() -> List[ProductOut]:
    """
    GET /products

    输出：产品列表 { id, productNo, productName, category, description, premiumGuide, coverageCap, status, createdAt }
    """
    return [ProductOut(**p) for p in list_products()]


@app.get("/products/{product_id}", response_model=ProductOut)
def read_product(product_id: str) -> ProductOut:
    """GET /products/{product_id} — 单条产品主数据（含产品说明）。"""
    row = get_product(product_id)
    if not row:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductOut(**row)


@app.post("/products", response_model=ProductOut)
def post_product(item: ProductCreateRequest) -> ProductOut:
    """POST /products — 新增产品（productNo 自动生成；保费/保额等来自标准目录）。"""
    from api.product_catalog import merge_catalog_for_create

    try:
        body = merge_catalog_for_create(item.productName, item.status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if item.description is not None:
        desc = (item.description or "").strip()
        if desc:
            body["description"] = desc[:512]
    dup = get_conflicting_product_for_catalog_key(body["productName"], body["category"])
    if dup:
        raise HTTPException(
            status_code=409,
            detail="该标准目录产品已在主数据中建档（产品编号 "
            f"{dup.get('productNo', '')}），请勿重复添加；如需调整状态请使用「编辑」。",
        )
    body["productNo"] = allocate_product_no()
    created = create_product(body)
    return ProductOut(**created)


@app.put("/products/{product_id}", response_model=ProductOut)
def put_product(product_id: str, item: ProductUpdateBody) -> ProductOut:
    """PUT /products/{product_id} — 更新状态或更换为目录中另一产品（不可改编号）。"""
    from api.product_catalog import get_catalog_entry, merge_catalog_for_create

    exists = get_product(product_id)
    if not exists:
        raise HTTPException(status_code=404, detail="Product not found")
    if item.productName is None and item.status is None and item.description is None:
        raise HTTPException(status_code=400, detail="请至少提供 productName、status 或 description 之一")

    target_status = item.status if item.status is not None else exists["status"]
    patch: Dict[str, Any] = {}
    if item.productName is not None:
        if item.productName == exists.get("productName"):
            if get_catalog_entry(item.productName):
                try:
                    patch = merge_catalog_for_create(item.productName, target_status)
                except ValueError as e:
                    raise HTTPException(status_code=400, detail=str(e))
            else:
                patch = {"status": target_status}
        else:
            try:
                patch = merge_catalog_for_create(item.productName, target_status)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        if item.status is not None:
            patch["status"] = item.status
    elif item.status is not None:
        patch["status"] = item.status

    if item.description is not None:
        patch["description"] = (item.description or "").strip()[:512]

    if not patch:
        raise HTTPException(status_code=400, detail="请至少提供 productName、status 或 description 之一")

    name_changed = patch.get("productName") is not None and patch.get("productName") != exists.get(
        "productName"
    )
    cat_changed = patch.get("category") is not None and patch.get("category") != exists.get("category")
    if name_changed or cat_changed:
        final_name = patch.get("productName", exists.get("productName"))
        final_cat = patch.get("category", exists.get("category"))
        dup = get_conflicting_product_for_catalog_key(
            final_name, final_cat, exclude_product_id=product_id
        )
        if dup:
            raise HTTPException(
                status_code=409,
                detail="目标目录产品已由另一条记录使用（产品编号 "
                f"{dup.get('productNo', '')}），无法重复建档。",
            )

    updated = update_product(product_id, patch)
    if not updated:
        raise HTTPException(status_code=500, detail="Update failed")
    return ProductOut(**updated)


@app.delete("/products/{product_id}")
def remove_product(product_id: str) -> Dict[str, Any]:
    """DELETE /products/{product_id}"""
    ok = delete_product(product_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"success": True}


# ---------- 承保管理（承保案件） ----------


def _customer_row_by_customer_no(customer_no: str) -> Optional[Dict[str, Any]]:
    key = (customer_no or "").strip()
    if not key:
        return None
    for row in list_customers():
        if (row.get("customerNo") or "").strip() == key:
            return row
    return None


@app.get("/underwriting_cases", response_model=List[UnderwritingCaseOut])
def get_underwriting_cases() -> List[UnderwritingCaseOut]:
    """GET /underwriting_cases — 承保案件列表。"""
    return [UnderwritingCaseOut(**c) for c in list_underwriting_cases()]


@app.post("/underwriting_cases", response_model=UnderwritingCaseOut)
def post_underwriting_case(item: UnderwritingCaseCreate) -> UnderwritingCaseOut:
    """POST /underwriting_cases — 新增案件（caseNo 自动生成）；姓名/证件号取自客户主数据。"""
    cust = _customer_row_by_customer_no(item.customerNo)
    if not cust:
        raise HTTPException(status_code=400, detail="客户编号不存在，请先在客户管理中建档")
    prod = (item.productName or "").strip()
    if not prod:
        raise HTTPException(status_code=400, detail="投保产品不能为空")
    body = {
        "customerNo": cust["customerNo"],
        "applicantName": cust.get("name") or "",
        "idNo": cust.get("idNo") or "",
        "productName": prod,
        "premium": str(item.premium or "0"),
        "coverageAmount": str(item.coverageAmount or "0"),
        "channel": item.channel or "",
        "status": "待受理",
        "riskScore": "",
        "decisionNote": item.decisionNote or "",
        "policyNo": "",
    }
    body["caseNo"] = allocate_underwriting_case_no()
    created = create_underwriting_case(body)
    return UnderwritingCaseOut(**created)


@app.put("/underwriting_cases/{case_id}", response_model=UnderwritingCaseOut)
def put_underwriting_case(case_id: str, item: UnderwritingCaseUpdate) -> UnderwritingCaseOut:
    """PUT /underwriting_cases/{case_id} — 仅更新渠道、状态、风险分、备注与关联保单号。"""
    exists = get_underwriting_case(case_id)
    if not exists:
        raise HTTPException(status_code=404, detail="Underwriting case not found")
    data = {k: v for k, v in item.dict().items() if v is not None}
    if not data:
        raise HTTPException(status_code=400, detail="无更新字段")
    merged = dict(exists)
    merged.update(data)
    policy_no = (merged.get("policyNo") or "").strip()
    st = (merged.get("status") or "").strip()
    if policy_no and st not in _UW_POLICY_ALLOWED_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="仅在案件状态为「已通过」或「自动通过」时可维护关联保单号；请先调整状态或留空保单号",
        )
    updated = update_underwriting_case(case_id, data)
    if not updated:
        raise HTTPException(status_code=500, detail="Update failed")
    return UnderwritingCaseOut(**updated)


@app.delete("/underwriting_cases/{case_id}")
def remove_underwriting_case(case_id: str) -> Dict[str, Any]:
    """DELETE /underwriting_cases/{case_id}"""
    ok = delete_underwriting_case(case_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Underwriting case not found")
    return {"success": True}


# ---------- 理赔管理 ----------


@app.get("/claims", response_model=List[ClaimOut])
def get_claims() -> List[ClaimOut]:
    """GET /claims — 理赔案件列表。"""
    return [ClaimOut(**c) for c in list_claims()]


@app.post("/claims", response_model=ClaimOut)
def post_claim(item: ClaimCreate) -> ClaimOut:
    """POST /claims — 新增理赔案件。"""
    body = item.dict()
    body["claimNo"] = allocate_claim_no()
    created = create_claim(body)
    return ClaimOut(**created)


@app.put("/claims/{claim_id}", response_model=ClaimOut)
def put_claim(claim_id: str, item: ClaimUpdate) -> ClaimOut:
    """PUT /claims/{claim_id} — 更新理赔案件（不可改 claimNo）。"""
    exists = get_claim(claim_id)
    if not exists:
        raise HTTPException(status_code=404, detail="Claim not found")
    data = {k: v for k, v in item.dict().items() if v is not None}
    if not data:
        raise HTTPException(status_code=400, detail="无更新字段")
    updated = update_claim(claim_id, data)
    if not updated:
        raise HTTPException(status_code=500, detail="Update failed")
    return ClaimOut(**updated)


@app.delete("/claims/{claim_id}")
def remove_claim(claim_id: str) -> Dict[str, Any]:
    """DELETE /claims/{claim_id}"""
    ok = delete_claim(claim_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Claim not found")
    return {"success": True}


# ---------- 售后与投诉管理 ----------


@app.get("/service_tickets", response_model=List[ServiceTicketOut])
def get_service_tickets() -> List[ServiceTicketOut]:
    """GET /service_tickets — 售后/投诉工单列表。"""
    return [ServiceTicketOut(**t) for t in list_service_tickets()]


@app.post("/service_tickets", response_model=ServiceTicketOut)
def post_service_ticket(item: ServiceTicketCreate) -> ServiceTicketOut:
    """POST /service_tickets — 新增工单。"""
    body = item.dict()
    body["ticketNo"] = allocate_service_ticket_no()
    created = create_service_ticket(body)
    return ServiceTicketOut(**created)


@app.put("/service_tickets/{ticket_id}", response_model=ServiceTicketOut)
def put_service_ticket(ticket_id: str, item: ServiceTicketUpdate) -> ServiceTicketOut:
    """PUT /service_tickets/{ticket_id} — 仅可更新状态、处理人、处理说明（不可改工单号及建档信息）。"""
    exists = get_service_ticket(ticket_id)
    if not exists:
        raise HTTPException(status_code=404, detail="Service ticket not found")
    data = {k: v for k, v in item.dict().items() if v is not None}
    if not data:
        raise HTTPException(status_code=400, detail="请至少提供状态、处理人或处理说明之一")
    updated = update_service_ticket(ticket_id, data)
    if not updated:
        raise HTTPException(status_code=500, detail="Update failed")
    return ServiceTicketOut(**updated)


@app.delete("/service_tickets/{ticket_id}")
def remove_service_ticket(ticket_id: str) -> Dict[str, Any]:
    """DELETE /service_tickets/{ticket_id}"""
    ok = delete_service_ticket(ticket_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Service ticket not found")
    return {"success": True}


# ---------- 渠道管理 ----------


@app.get("/channels", response_model=List[ChannelOut])
def get_channels() -> List[ChannelOut]:
    """GET /channels — 销售渠道列表。"""
    return [ChannelOut(**c) for c in list_channels()]


@app.post("/channels", response_model=ChannelOut)
def post_channel(item: ChannelCreate) -> ChannelOut:
    """POST /channels — 新增渠道。"""
    body = item.dict()
    cc = (body.get("channelCode") or "").strip()
    body["channelCode"] = cc if cc else allocate_channel_code()
    created = create_channel(body)
    return ChannelOut(**created)


@app.put("/channels/{channel_id}", response_model=ChannelOut)
def put_channel(channel_id: str, item: ChannelUpdate) -> ChannelOut:
    """PUT /channels/{channel_id} — 更新渠道。"""
    exists = get_channel(channel_id)
    if not exists:
        raise HTTPException(status_code=404, detail="Channel not found")
    data = {k: v for k, v in item.dict().items() if v is not None}
    if not data:
        raise HTTPException(status_code=400, detail="无更新字段")
    updated = update_channel(channel_id, data)
    if not updated:
        raise HTTPException(status_code=500, detail="Update failed")
    return ChannelOut(**updated)


@app.delete("/channels/{channel_id}")
def remove_channel(channel_id: str) -> Dict[str, Any]:
    """DELETE /channels/{channel_id}"""
    ok = delete_channel(channel_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Channel not found")
    return {"success": True}


# ---------- 财务管理 ----------


@app.get("/premium_flows", response_model=List[PremiumFlowOut])
def get_premium_flows_api() -> List[PremiumFlowOut]:
    """GET /premium_flows — 保费收付流水。"""
    return [PremiumFlowOut(**x) for x in list_premium_flows()]


@app.post("/premium_flows", response_model=PremiumFlowOut)
def post_premium_flow(item: PremiumFlowCreate) -> PremiumFlowOut:
    body = item.dict()
    if not (body.get("flowNo") or "").strip():
        body["flowNo"] = allocate_premium_flow_no()
    created = create_premium_flow(body)
    return PremiumFlowOut(**created)


@app.put("/premium_flows/{flow_id}", response_model=PremiumFlowOut)
def put_premium_flow(flow_id: str, item: PremiumFlowUpdate) -> PremiumFlowOut:
    exists = get_premium_flow(flow_id)
    if not exists:
        raise HTTPException(status_code=404, detail="Premium flow not found")
    data = {k: v for k, v in item.dict().items() if v is not None}
    if not data:
        raise HTTPException(status_code=400, detail="无更新字段")
    updated = update_premium_flow(flow_id, data)
    if not updated:
        raise HTTPException(status_code=500, detail="Update failed")
    return PremiumFlowOut(**updated)


@app.delete("/premium_flows/{flow_id}")
def remove_premium_flow(flow_id: str) -> Dict[str, Any]:
    ok = delete_premium_flow(flow_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Premium flow not found")
    return {"success": True}


@app.get("/commission_settlements", response_model=List[CommissionSettlementOut])
def get_commission_settlements_api() -> List[CommissionSettlementOut]:
    """GET /commission_settlements — 佣金结算与对账。"""
    return [CommissionSettlementOut(**x) for x in list_commission_settlements()]


@app.post("/commission_settlements", response_model=CommissionSettlementOut)
def post_commission_settlement(item: CommissionSettlementCreate) -> CommissionSettlementOut:
    body = item.dict()
    if not (body.get("settlementNo") or "").strip():
        body["settlementNo"] = allocate_commission_settlement_no()
    created = create_commission_settlement(body)
    return CommissionSettlementOut(**created)


@app.put("/commission_settlements/{settlement_id}", response_model=CommissionSettlementOut)
def put_commission_settlement(settlement_id: str, item: CommissionSettlementUpdate) -> CommissionSettlementOut:
    exists = get_commission_settlement(settlement_id)
    if not exists:
        raise HTTPException(status_code=404, detail="Commission settlement not found")
    data = {k: v for k, v in item.dict().items() if v is not None}
    if not data:
        raise HTTPException(status_code=400, detail="无更新字段")
    updated = update_commission_settlement(settlement_id, data)
    if not updated:
        raise HTTPException(status_code=500, detail="Update failed")
    return CommissionSettlementOut(**updated)


@app.delete("/commission_settlements/{settlement_id}")
def remove_commission_settlement(settlement_id: str) -> Dict[str, Any]:
    ok = delete_commission_settlement(settlement_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Commission settlement not found")
    return {"success": True}


# ---------- 再保管理 ----------


@app.get("/reinsurance_contracts", response_model=List[ReinsuranceContractOut])
def get_reinsurance_contracts_api() -> List[ReinsuranceContractOut]:
    return [ReinsuranceContractOut(**x) for x in list_reinsurance_contracts()]


@app.post("/reinsurance_contracts", response_model=ReinsuranceContractOut)
def post_reinsurance_contract(item: ReinsuranceContractCreate) -> ReinsuranceContractOut:
    body = item.dict()
    if not (body.get("contractNo") or "").strip():
        body["contractNo"] = allocate_reinsurance_contract_no()
    created = create_reinsurance_contract(body)
    return ReinsuranceContractOut(**created)


@app.put("/reinsurance_contracts/{contract_id}", response_model=ReinsuranceContractOut)
def put_reinsurance_contract(contract_id: str, item: ReinsuranceContractUpdate) -> ReinsuranceContractOut:
    exists = get_reinsurance_contract(contract_id)
    if not exists:
        raise HTTPException(status_code=404, detail="Reinsurance contract not found")
    data = {k: v for k, v in item.dict().items() if v is not None}
    if not data:
        raise HTTPException(status_code=400, detail="无更新字段")
    updated = update_reinsurance_contract(contract_id, data)
    if not updated:
        raise HTTPException(status_code=500, detail="Update failed")
    return ReinsuranceContractOut(**updated)


@app.delete("/reinsurance_contracts/{contract_id}")
def remove_reinsurance_contract(contract_id: str) -> Dict[str, Any]:
    ok = delete_reinsurance_contract(contract_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Reinsurance contract not found")
    return {"success": True}


@app.get("/reinsurance_bills", response_model=List[ReinsuranceBillOut])
def get_reinsurance_bills_api() -> List[ReinsuranceBillOut]:
    return [ReinsuranceBillOut(**x) for x in list_reinsurance_bills()]


@app.post("/reinsurance_bills", response_model=ReinsuranceBillOut)
def post_reinsurance_bill(item: ReinsuranceBillCreate) -> ReinsuranceBillOut:
    body = item.dict()
    if not (body.get("billNo") or "").strip():
        body["billNo"] = allocate_reinsurance_bill_no()
    created = create_reinsurance_bill(body)
    return ReinsuranceBillOut(**created)


@app.put("/reinsurance_bills/{bill_id}", response_model=ReinsuranceBillOut)
def put_reinsurance_bill(bill_id: str, item: ReinsuranceBillUpdate) -> ReinsuranceBillOut:
    exists = get_reinsurance_bill(bill_id)
    if not exists:
        raise HTTPException(status_code=404, detail="Reinsurance bill not found")
    data = {k: v for k, v in item.dict().items() if v is not None}
    if not data:
        raise HTTPException(status_code=400, detail="无更新字段")
    updated = update_reinsurance_bill(bill_id, data)
    if not updated:
        raise HTTPException(status_code=500, detail="Update failed")
    return ReinsuranceBillOut(**updated)


@app.delete("/reinsurance_bills/{bill_id}")
def remove_reinsurance_bill(bill_id: str) -> Dict[str, Any]:
    ok = delete_reinsurance_bill(bill_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Reinsurance bill not found")
    return {"success": True}


# ---------- 代理人/团队管理 ----------


@app.get("/agent_teams", response_model=List[AgentTeamOut])
def get_agent_teams_api() -> List[AgentTeamOut]:
    return [AgentTeamOut(**x) for x in list_agent_teams()]


@app.post("/agent_teams", response_model=AgentTeamOut)
def post_agent_team(item: AgentTeamCreate) -> AgentTeamOut:
    created = create_agent_team(item.dict())
    return AgentTeamOut(**created)


@app.put("/agent_teams/{team_id}", response_model=AgentTeamOut)
def put_agent_team(team_id: str, item: AgentTeamUpdate) -> AgentTeamOut:
    exists = get_agent_team(team_id)
    if not exists:
        raise HTTPException(status_code=404, detail="Agent team not found")
    data = {k: v for k, v in item.dict().items() if v is not None}
    if not data:
        raise HTTPException(status_code=400, detail="无更新字段")
    updated = update_agent_team(team_id, data)
    if not updated:
        raise HTTPException(status_code=500, detail="Update failed")
    return AgentTeamOut(**updated)


@app.delete("/agent_teams/{team_id}")
def remove_agent_team(team_id: str) -> Dict[str, Any]:
    ok = delete_agent_team(team_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Agent team not found")
    return {"success": True}


@app.get("/agents", response_model=List[AgentOut])
def get_agents_api() -> List[AgentOut]:
    return [AgentOut(**x) for x in list_agents()]


@app.post("/agents", response_model=AgentOut)
def post_agent(item: AgentCreate) -> AgentOut:
    body = item.dict()
    if not (body.get("agentNo") or "").strip():
        body["agentNo"] = allocate_agent_no()
    created = create_agent(body)
    return AgentOut(**created)


@app.put("/agents/{agent_id}", response_model=AgentOut)
def put_agent(agent_id: str, item: AgentUpdate) -> AgentOut:
    exists = get_agent(agent_id)
    if not exists:
        raise HTTPException(status_code=404, detail="Agent not found")
    data = {k: v for k, v in item.dict().items() if v is not None}
    if not data:
        raise HTTPException(status_code=400, detail="无更新字段")
    updated = update_agent(agent_id, data)
    if not updated:
        raise HTTPException(status_code=500, detail="Update failed")
    return AgentOut(**updated)


@app.delete("/agents/{agent_id}")
def remove_agent(agent_id: str) -> Dict[str, Any]:
    ok = delete_agent(agent_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"success": True}


@app.get("/agent_performance_summary", response_model=List[AgentPerformanceSummaryOut])
def get_agent_performance_summary_api(period: str = "") -> List[AgentPerformanceSummaryOut]:
    rows = get_agent_performance_summary(period)
    return [
        AgentPerformanceSummaryOut(
            name=r.get("name", ""),
            premium=str(r.get("premium", "0")),
            rate=r.get("rate", "0%"),
            period=r.get("period"),
        )
        for r in (rows or [])
    ]


# ---------- 报表与分析 ----------


def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        if x is None:
            return default
        s = str(x).strip()
        if not s:
            return default
        return float(s)
    except Exception:
        return default


@app.get("/analytics/summary", response_model=AnalyticsSummaryOut)
def get_analytics_summary_api() -> AnalyticsSummaryOut:
    premium_flows = list_premium_flows()
    claims = list_claims()
    customers = list_customers()
    policies = list_policies()
    risk_alerts = list_alerts()
    blacklist = list_blacklist()

    premium_yuan = sum(
        _safe_float(x.get("amount", "0"))
        for x in premium_flows
        if (x.get("flowType") or "") != "理赔赔款"
    )
    claim_yuan = sum(_safe_float(c.get("approvedAmount") or c.get("claimAmount") or "0") for c in claims)

    ratio = 0.0
    if premium_yuan > 0:
        ratio = claim_yuan / premium_yuan * 100.0

    return AnalyticsSummaryOut(
        premiumTotalWan=str(round(premium_yuan / 10000.0, 2)),
        claimTotalWan=str(round(claim_yuan / 10000.0, 2)),
        claimRatioPercent=str(round(ratio, 2)),
        customerCount=len(customers),
        policyCount=len(policies),
        claimCount=len(claims),
        riskAlertCount=len(risk_alerts),
        blacklistCount=len(blacklist),
    )


# ---------- 系统管理 ----------


@app.get("/system_users", response_model=List[SystemUserOut])
def get_system_users_api() -> List[SystemUserOut]:
    return [SystemUserOut(**_build_user_with_meta(u)) for u in list_system_users()]


@app.post("/system_users", response_model=SystemUserOut)
def post_system_user(item: SystemUserCreate) -> SystemUserOut:
    uname = (item.username or "").strip()
    if uname == "admin":
        raise HTTPException(status_code=409, detail="管理员账号已存在")
    _validate_system_user_fields(
        username=uname,
        role=item.role,
        data_scope=item.dataScope,
        status=item.status,
        full_name=item.fullName,
        employee_no=item.employeeNo,
        org_code=item.orgCode,
        department=item.department,
        post=item.post,
        creating=True,
    )
    try:
        created = create_system_user(
            {
                "username": uname,
                "role": item.role,
                "status": item.status,
            }
        )
        _upsert_user_meta(
            uname,
            {
                "fullName": item.fullName,
                "employeeNo": item.employeeNo,
                "orgCode": item.orgCode,
                "department": item.department,
                "post": item.post,
                "dataScope": item.dataScope,
            },
        )
        _write_audit_log("system", "admin", f"新增系统用户：{uname}", module="system", result="success")
        return SystemUserOut(**_build_user_with_meta(created))
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except IntegrityError:
        raise HTTPException(status_code=409, detail="用户名已存在")


@app.put("/system_users/{user_id}", response_model=SystemUserOut)
def put_system_user(user_id: str, item: SystemUserUpdate) -> SystemUserOut:
    exists = get_system_user(user_id)
    if not exists:
        raise HTTPException(status_code=404, detail="System user not found")
    merged = _build_user_with_meta(dict(exists))
    username = str(merged.get("username", "")).strip()
    new_role = (item.role if item.role is not None else merged.get("role", "")) or ""
    new_status = (item.status if item.status is not None else merged.get("status", "")) or ""
    new_scope = (item.dataScope if item.dataScope is not None else merged.get("dataScope", "")) or ""
    new_fn = item.fullName if item.fullName is not None else merged.get("fullName", "")
    new_eno = item.employeeNo if item.employeeNo is not None else merged.get("employeeNo", "")
    new_org = item.orgCode if item.orgCode is not None else merged.get("orgCode", "")
    new_dept = item.department if item.department is not None else merged.get("department", "")
    new_post = item.post if item.post is not None else merged.get("post", "")
    _validate_system_user_fields(
        username=username,
        role=str(new_role).strip(),
        data_scope=str(new_scope).strip(),
        status=str(new_status).strip(),
        full_name=str(new_fn),
        employee_no=str(new_eno),
        org_code=str(new_org),
        department=str(new_dept),
        post=str(new_post),
        creating=False,
    )
    data = {}
    if item.role is not None:
        data["role"] = item.role
    if item.status is not None:
        data["status"] = item.status
    updated = update_system_user(user_id, data)
    if not updated:
        raise HTTPException(status_code=500, detail="Update failed")
    username = str(updated.get("username", "")).strip()
    current_meta = _get_user_meta(username)
    if item.fullName is not None:
        current_meta["fullName"] = item.fullName
    if item.employeeNo is not None:
        current_meta["employeeNo"] = item.employeeNo
    if item.orgCode is not None:
        current_meta["orgCode"] = item.orgCode
    if item.department is not None:
        current_meta["department"] = item.department
    if item.post is not None:
        current_meta["post"] = item.post
    if item.dataScope is not None:
        current_meta["dataScope"] = item.dataScope
    _upsert_user_meta(username, current_meta)
    _write_audit_log("system", "admin", f"更新系统用户：{username}", module="system", result="success")
    return SystemUserOut(**_build_user_with_meta(updated))


@app.delete("/system_users/{user_id}")
def remove_system_user(user_id: str) -> Dict[str, Any]:
    row = get_system_user(user_id)
    if row and str(row.get("username", "")).strip() == "admin":
        raise HTTPException(status_code=403, detail="管理员账号不可删除")
    ok = delete_system_user(user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="System user not found")
    if row:
        username = str(row.get("username", "")).strip()
        _delete_param_by_key(_user_password_param_key(username))
        _delete_param_by_key(_user_meta_param_key(username))
        for token, session in list(_AUTH_SESSIONS.items()):
            u = session.get("user") or {}
            if str(u.get("username", "")).strip() == username:
                _AUTH_SESSIONS.pop(token, None)
        _write_audit_log("system", "admin", f"删除系统用户：{username}", module="system", result="success")
    return {"success": True}


@app.get("/system_params", response_model=List[SystemParamOut])
def get_system_params_api() -> List[SystemParamOut]:
    return [SystemParamOut(**p) for p in list_system_params()]


@app.post("/system_params", response_model=SystemParamOut)
def post_system_param(item: SystemParamCreate) -> SystemParamOut:
    if (item.paramKey or "").strip().startswith("auth_password_"):
        raise HTTPException(status_code=403, detail="登录密码参数不可在此直接维护")
    try:
        created = create_system_param(item.dict())
        _write_audit_log("system", "admin", f"新增系统参数：{item.paramKey}", module="system", result="success")
        return SystemParamOut(**created)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except IntegrityError:
        raise HTTPException(status_code=409, detail="参数键已存在")


@app.put("/system_params/{param_id}", response_model=SystemParamOut)
def put_system_param(param_id: str, item: SystemParamUpdate) -> SystemParamOut:
    exists = get_system_param(param_id)
    if not exists:
        raise HTTPException(status_code=404, detail="System param not found")
    if str(exists.get("paramKey", "")).strip().startswith("auth_password_"):
        raise HTTPException(status_code=403, detail="登录密码参数不可在此直接维护")
    data = {k: v for k, v in item.dict().items() if v is not None}
    updated = update_system_param(param_id, data)
    if not updated:
        raise HTTPException(status_code=500, detail="Update failed")
    _write_audit_log("system", "admin", f"更新系统参数：{exists.get('paramKey', '')}", module="system", result="success")
    return SystemParamOut(**updated)


@app.delete("/system_params/{param_id}")
def remove_system_param(param_id: str) -> Dict[str, Any]:
    row = get_system_param(param_id)
    if row and str(row.get("paramKey", "")).strip().startswith("auth_password_"):
        raise HTTPException(status_code=403, detail="登录密码参数不可删除")
    ok = delete_system_param(param_id)
    if not ok:
        raise HTTPException(status_code=404, detail="System param not found")
    if row:
        _write_audit_log("system", "admin", f"删除系统参数：{row.get('paramKey', '')}", module="system", result="success")
    return {"success": True}


@app.get("/system_logs", response_model=List[SystemLogOut])
def get_system_logs_api(limit: int = 100, module: str = "", actor: str = "", keyword: str = "") -> List[SystemLogOut]:
    rows = list_system_logs(limit * 3 if limit > 0 else 100)
    module_kw = (module or "").strip()
    actor_kw = (actor or "").strip()
    keyword_kw = (keyword or "").strip()
    filtered: List[Dict[str, Any]] = []
    for row in rows:
        action = str(row.get("action", "") or "")
        if module_kw and f"module={module_kw}" not in action:
            continue
        if actor_kw and str(row.get("actor", "")).strip() != actor_kw:
            continue
        if keyword_kw and keyword_kw not in action:
            continue
        enriched = dict(row)
        enriched.setdefault("module", "")
        enriched.setdefault("result", "")
        enriched.setdefault("ip", "")
        if "| module=" in action:
            parts = action.split("|")
            enriched["action"] = parts[0].strip()
            for seg in parts[1:]:
                seg = seg.strip()
                if seg.startswith("module="):
                    enriched["module"] = seg.replace("module=", "", 1)
                elif seg.startswith("result="):
                    enriched["result"] = seg.replace("result=", "", 1)
                elif seg.startswith("ip="):
                    enriched["ip"] = seg.replace("ip=", "", 1)
        filtered.append(enriched)
        if len(filtered) >= max(0, int(limit)):
            break
    return [SystemLogOut(**x) for x in filtered]


@app.get("/system/audit_policies", response_model=List[AuditPolicyOut])
def get_audit_policies_api() -> List[AuditPolicyOut]:
    return [
        AuditPolicyOut(id="1", action="登录失败连续告警", riskLevel="高", requireReview=False, retentionDays=365),
        AuditPolicyOut(id="2", action="重置密码", riskLevel="高", requireReview=True, retentionDays=365),
        AuditPolicyOut(id="3", action="强制下线", riskLevel="中", requireReview=False, retentionDays=180),
        AuditPolicyOut(id="4", action="系统用户删除", riskLevel="高", requireReview=True, retentionDays=365),
        AuditPolicyOut(id="5", action="系统参数删除", riskLevel="中", requireReview=False, retentionDays=180),
        AuditPolicyOut(id="6", action="关键业务数据删除", riskLevel="高", requireReview=True, retentionDays=365),
    ]


@app.get("/system/roadmap", response_model=List[RoadmapItemOut])
def get_system_roadmap_api() -> List[RoadmapItemOut]:
    return [
        RoadmapItemOut(
            phase="一期",
            target="账号-权限-审计闭环",
            deliverables=[
                "登录返回权限快照",
                "系统用户扩展信息管理",
                "重置密码与强制下线",
                "日志筛选与高风险操作覆盖",
            ],
            acceptance="管理员可按角色控制菜单访问，关键操作均可追溯",
        ),
        RoadmapItemOut(
            phase="二期",
            target="组织与数据权限精细化",
            deliverables=[
                "组织架构（总/分/支）",
                "数据权限（本机构/本团队/本人）",
                "会话列表与异地登录提醒",
            ],
            acceptance="跨机构数据隔离可验证，账号安全策略可配置",
        ),
    ]


_ensure_customer_photo_dir()
app.mount(
    "/static/customer_photos",
    StaticFiles(directory=str(CUSTOMER_PHOTO_DIR)),
    name="customer_photos_files",
)
