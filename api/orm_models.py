"""SQLAlchemy ORM 表定义（与 sql/init_insurance_db.sql 对齐）。"""

from typing import Optional

from sqlalchemy import BigInteger, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    customer_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    id_type: Mapped[str] = mapped_column(String(32), nullable=False, default="身份证")
    id_no: Mapped[str] = mapped_column(String(64), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), nullable=False)
    occupation: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    level: Mapped[str] = mapped_column(String(32), nullable=False, default="普通")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="在保")
    photo: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    gender: Mapped[str] = mapped_column(String(16), nullable=False, default="未知")
    address: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    remark: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    created_at: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)


class Policy(Base):
    __tablename__ = "policies"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    policy_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    customer_no: Mapped[str] = mapped_column(String(64), nullable=False)
    product_name: Mapped[str] = mapped_column(String(128), nullable=False)
    premium: Mapped[str] = mapped_column(String(32), nullable=False, default="0")
    coverage_amount: Mapped[str] = mapped_column(String(32), nullable=False, default="0")
    start_date: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    end_date: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="生效中")


class Product(Base):
    """保险产品主数据（对应 /products API）。"""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    product_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    product_name: Mapped[str] = mapped_column(String(128), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    description: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    premium_guide: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    coverage_cap: Mapped[str] = mapped_column(String(64), nullable=False, default="0")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="在售")
    created_at: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)


class UnderwritingCase(Base):
    """承保案件（投保单 / 核保流程记录，对应 /underwriting_cases API）。"""

    __tablename__ = "underwriting_cases"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    case_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    customer_no: Mapped[str] = mapped_column(String(64), nullable=False)
    applicant_name: Mapped[str] = mapped_column(String(64), nullable=False)
    id_no: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    product_name: Mapped[str] = mapped_column(String(128), nullable=False)
    premium: Mapped[str] = mapped_column(String(32), nullable=False, default="0")
    coverage_amount: Mapped[str] = mapped_column(String(32), nullable=False, default="0")
    channel: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="待受理")
    risk_score: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    decision_note: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    policy_no: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    updated_at: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)


class Claim(Base):
    """理赔案件（对应 /claims API）。"""

    __tablename__ = "claims"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    claim_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    policy_no: Mapped[str] = mapped_column(String(64), nullable=False)
    customer_no: Mapped[str] = mapped_column(String(64), nullable=False)
    claimant_name: Mapped[str] = mapped_column(String(64), nullable=False)
    product_name: Mapped[str] = mapped_column(String(128), nullable=False)
    claim_type: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    incident_reason: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    incident_date: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    report_date: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    claim_amount: Mapped[str] = mapped_column(String(32), nullable=False, default="0")
    approved_amount: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="待受理")
    decision_note: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    created_at: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    updated_at: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)


class ServiceTicket(Base):
    """售后与投诉工单（对应 /service_tickets API）。"""

    __tablename__ = "service_tickets"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    ticket_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    ticket_type: Mapped[str] = mapped_column(String(32), nullable=False, default="投诉")
    customer_no: Mapped[str] = mapped_column(String(64), nullable=False)
    contact_name: Mapped[str] = mapped_column(String(64), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    policy_no: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    category: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    subject: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="待受理")
    handler: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    resolution_note: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    start_date: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    end_date: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    created_at: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    updated_at: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)


class SalesChannel(Base):
    """销售渠道主数据（对应 /channels API）。"""

    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    channel_code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    channel_name: Mapped[str] = mapped_column(String(128), nullable=False)
    channel_type: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    manager: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    commission_rule: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    contact_phone: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="合作中")
    remark: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    created_at: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    updated_at: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)


class BlacklistEntry(Base):
    __tablename__ = "blacklist"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    id_no: Mapped[str] = mapped_column(String(64), nullable=False)
    reason: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="启用")


class RiskAlertRow(Base):
    __tablename__ = "risk_alerts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    alert_type: Mapped[str] = mapped_column(String(64), nullable=False)
    alert_desc: Mapped[str] = mapped_column(String(512), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(32), nullable=False, default="高")


class RiskRuleRow(Base):
    """可执行风控规则（预设 + 自然语言解析入库）。"""

    __tablename__ = "risk_rules"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    rule_id: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    description_cn: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    action: Mapped[str] = mapped_column(String(64), nullable=False, default="manual_review")
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="preset")
    ir_json: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    enabled: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class PremiumFlow(Base):
    """保费收付流水（对应 /premium_flows API）。"""

    __tablename__ = "premium_flows"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    flow_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    flow_type: Mapped[str] = mapped_column(String(32), nullable=False)
    policy_no: Mapped[str] = mapped_column(String(64), nullable=False)
    amount: Mapped[str] = mapped_column(String(32), nullable=False, default="0")
    pay_method: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    remark: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    created_at: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    updated_at: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)


class CommissionSettlement(Base):
    """佣金结算与对账（对应 /commission_settlements API）。"""

    __tablename__ = "commission_settlements"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    settlement_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    channel_name: Mapped[str] = mapped_column(String(128), nullable=False)
    channel_code: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    period: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    commission_amount: Mapped[str] = mapped_column(String(32), nullable=False, default="0")
    reconcile_status: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    remark: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    created_at: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    updated_at: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)


class ReinsuranceContract(Base):
    """再保合同（对应 /reinsurance_contracts API）。"""

    __tablename__ = "reinsurance_contracts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    contract_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    contract_type: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    cedent: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    reinsurer: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="生效")
    remark: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    created_at: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    updated_at: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)


class ReinsuranceBill(Base):
    """分出/分入与再保账单（对应 /reinsurance_bills API）。"""

    __tablename__ = "reinsurance_bills"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    bill_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    biz_kind: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    period: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    premium_wan: Mapped[str] = mapped_column(String(32), nullable=False, default="0")
    claim_recover_wan: Mapped[str] = mapped_column(String(32), nullable=False, default="0")
    remark: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    created_at: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    updated_at: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)


class AgentTeam(Base):
    """代理人/团队组织架构（对应 /agent_teams API）。"""

    __tablename__ = "agent_teams"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    team_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    parent_team_no: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    created_at: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    updated_at: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)


class Agent(Base):
    """代理人主数据（对应 /agents API）。"""

    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    agent_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    id_no: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    phone: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    team_no: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    title: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="在职")
    created_at: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    updated_at: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)


class AgentPerformance(Base):
    """代理人/团队业绩（对应 /agent_performance_summary）。"""

    __tablename__ = "agent_performances"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    perf_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    owner_type: Mapped[str] = mapped_column(String(16), nullable=False, default="team")
    owner_no: Mapped[str] = mapped_column(String(64), nullable=False)
    period: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    premium_wan: Mapped[str] = mapped_column(String(32), nullable=False, default="0")
    kpi_rate: Mapped[str] = mapped_column(String(32), nullable=False, default="0%")
    created_at: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    updated_at: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)


class SystemUser(Base):
    """系统管理：用户表。"""

    __tablename__ = "system_users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    role: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="启用")
    created_at: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    updated_at: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)


class SystemParam(Base):
    """系统管理：参数表。"""

    __tablename__ = "system_params"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    param_key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    param_value: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    description: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    created_at: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    updated_at: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)


class SystemLog(Base):
    """系统管理：日志表。"""

    __tablename__ = "system_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    log_type: Mapped[str] = mapped_column(String(32), nullable=False, default="info")
    actor: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    action: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    created_at: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
