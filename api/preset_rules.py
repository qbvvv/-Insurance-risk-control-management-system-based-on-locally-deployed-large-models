"""
与 rules_dataset.jsonl 及业务备注稿对应的可执行预设规则。
规则 ID 供 evaluate_rule、解析回退与 rule_helpers 全文匹配使用。
"""

from typing import List, Optional

from api.preset_rules_ext_100 import EXT_REMARK_100_RULES
from rules_engine.schema import RiskRuleIR, RuleCondition, RuleAction

# 夜间 22:00–次日 06:00 的小时集合（用于 submit_hour in [...]）
NIGHT_HOURS = [22, 23, 0, 1, 2, 3, 4, 5, 6]

PRESET_RULES: List[RiskRuleIR] = [
    # ---------- 原有基线规则（与数据集 / 回退子串对齐）----------
    RiskRuleIR(
        rule_id="claim_freq_high_risk",
        description_cn="同一用户3个月内理赔超过3次则标记为高风险",
        conditions=[
            RuleCondition(entity="claim", field="count_3m", op=">", value=3, time_window="3m"),
        ],
        action=RuleAction.TAG_HIGH_RISK,
        action_params={"risk_level": "high"},
        enabled=True,
        priority=10,
    ),
    RiskRuleIR(
        rule_id="policy_year_claim_reject",
        description_cn="同一保单年度内理赔次数 > 5次，暂停自动赔付。",
        conditions=[
            RuleCondition(
                entity="policy",
                field="year_claim_count",
                op=">",
                value=5,
                time_window="policy_year",
            ),
        ],
        action=RuleAction.REJECT,
        action_params={"reason": "policy_year_claim_reject"},
        enabled=True,
        priority=20,
    ),
    RiskRuleIR(
        rule_id="elderly_manual_underwrite",
        description_cn="投保人年龄超过70岁需人工核保",
        conditions=[
            RuleCondition(entity="applicant", field="age", op=">", value=70),
        ],
        action=RuleAction.MANUAL_REVIEW,
        action_params={"reason": "elderly_manual_underwrite"},
        enabled=True,
        priority=30,
    ),
    RiskRuleIR(
        rule_id="ip_freq_abnormal",
        description_cn="单日同一IP提交超过10次申请则标记异常",
        conditions=[
            RuleCondition(
                entity="ip",
                field="daily_submit_count",
                op=">",
                value=10,
                time_window="1d",
            ),
        ],
        action=RuleAction.ALERT,
        action_params={"reason": "ip_freq_abnormal"},
        enabled=True,
        priority=40,
    ),
    RiskRuleIR(
        rule_id="claim_premium_ratio_review",
        description_cn="单次理赔金额 / 年保费比例 > 10，触发专项复核。",
        conditions=[
            RuleCondition(
                entity="claim",
                field="premium_ratio",
                op=">",
                value=10,
            ),
        ],
        action=RuleAction.MANUAL_REVIEW,
        action_params={"reason": "claim_premium_ratio_review"},
        enabled=True,
        priority=50,
    ),
    RiskRuleIR(
        rule_id="new_user_early_claim_review",
        description_cn="新用户投保后7天内申请理赔则进入人工审核",
        conditions=[
            RuleCondition(
                entity="user",
                field="claim_days_after_policy",
                op="<=",
                value=7,
                time_window="after_policy",
            ),
        ],
        action=RuleAction.MANUAL_REVIEW,
        action_params={"reason": "new_user_early_claim_review"},
        enabled=True,
        priority=60,
    ),
    RiskRuleIR(
        rule_id="card_multi_policy_alert",
        description_cn="同一银行卡被超过3个不同保单使用则预警",
        conditions=[
            RuleCondition(
                entity="card",
                field="policy_count",
                op=">",
                value=3,
            ),
        ],
        action=RuleAction.ALERT,
        action_params={"reason": "card_multi_policy_alert"},
        enabled=True,
        priority=70,
    ),
    RiskRuleIR(
        rule_id="night_claim_manual",
        description_cn="夜间22点至次日6点提交的理赔自动转人工",
        conditions=[
            RuleCondition(
                entity="claim",
                field="submit_hour",
                op="in",
                value=NIGHT_HOURS,
            ),
        ],
        action=RuleAction.MANUAL_REVIEW,
        action_params={"reason": "night_claim_manual"},
        enabled=True,
        priority=80,
    ),
    RiskRuleIR(
        rule_id="address_multi_high_policy_verify",
        description_cn="同一收货地址对应超过5份高额保单则核验",
        conditions=[
            RuleCondition(
                entity="address",
                field="high_policy_count",
                op=">",
                value=5,
            ),
        ],
        action=RuleAction.MANUAL_REVIEW,
        action_params={"reason": "address_multi_high_policy_verify"},
        enabled=True,
        priority=90,
    ),
    # ---------- 备注稿 20 条：与业务话术一一对应的预设 ----------
    RiskRuleIR(
        rule_id="id_no_apply_5_7d",
        description_cn="同一证件号在 7天 内提交投保申请 >= 5次，标记高风险并人工审核。",
        conditions=[
            RuleCondition(
                entity="id_no",
                field="policy_apply_count_7d",
                op=">=",
                value=5,
                time_window="7d",
            ),
        ],
        action=RuleAction.TAG_HIGH_RISK,
        action_params={"risk_level": "high", "followup": "manual_review"},
        enabled=True,
        priority=11,
    ),
    RiskRuleIR(
        rule_id="phone_idno_link_verify_3",
        description_cn="同一手机号关联不同证件号 >= 3个，触发身份核验。",
        conditions=[
            RuleCondition(
                entity="phone",
                field="distinct_idno_count",
                op=">=",
                value=3,
                time_window="",
            ),
        ],
        action=RuleAction.MANUAL_REVIEW,
        action_params={"reason": "phone_idno_link_verify"},
        enabled=True,
        priority=12,
    ),
    RiskRuleIR(
        rule_id="device_apply_reject_24h_10",
        description_cn="同一设备指纹在 24小时 内提交申请 >= 10次，拒绝自动核保。",
        conditions=[
            RuleCondition(
                entity="device",
                field="apply_count_24h",
                op=">=",
                value=10,
                time_window="24h",
            ),
        ],
        action=RuleAction.REJECT,
        action_params={"reason": "device_apply_reject_24h_10"},
        enabled=True,
        priority=13,
    ),
    RiskRuleIR(
        rule_id="insured_age75_cov1m_manual",
        description_cn="被保险人年龄 > 75 且保额 > 100万，强制人工核保。",
        conditions=[
            RuleCondition(entity="insured", field="age", op=">", value=75),
            RuleCondition(entity="policy", field="coverage_amount", op=">", value=1_000_000),
        ],
        action=RuleAction.MANUAL_REVIEW,
        action_params={"reason": "insured_age75_cov1m_manual"},
        enabled=True,
        priority=14,
    ),
    RiskRuleIR(
        rule_id="address_high_new_30d_4",
        description_cn="短期内（30天）同一地址新增高额保单 >= 4份，触发反欺诈核查。",
        conditions=[
            RuleCondition(
                entity="address",
                field="high_policy_new_count_30d",
                op=">=",
                value=4,
                time_window="30d",
            ),
        ],
        action=RuleAction.MANUAL_REVIEW,
        action_params={"reason": "address_high_new_30d_4"},
        enabled=True,
        priority=15,
    ),
    RiskRuleIR(
        rule_id="policy_effective_claim_7d_review",
        description_cn="保单生效 <= 7天 即发生理赔，进入重点复核。",
        conditions=[
            RuleCondition(
                entity="policy",
                field="days_from_effective_to_claim",
                op="<=",
                value=7,
                time_window="after_effective",
            ),
        ],
        action=RuleAction.MANUAL_REVIEW,
        action_params={"reason": "policy_effective_claim_7d_review"},
        enabled=True,
        priority=16,
    ),
    RiskRuleIR(
        rule_id="night_claim_amount_manual",
        description_cn="夜间 22:00-06:00 提交理赔且金额 > 阈值，转人工审核。",
        conditions=[
            RuleCondition(entity="claim", field="submit_hour", op="in", value=NIGHT_HOURS),
            RuleCondition(entity="claim", field="claim_amount", op=">", value=50_000),
        ],
        action=RuleAction.MANUAL_REVIEW,
        action_params={"reason": "night_claim_amount_manual", "amount_threshold_yuan": 50000},
        enabled=True,
        priority=17,
    ),
    RiskRuleIR(
        rule_id="claim_nlp_similar_cluster",
        description_cn="同一事故描述文本在多客户间高相似（NLP相似度高），标记团伙嫌疑。",
        conditions=[
            RuleCondition(
                entity="claim",
                field="nlp_cross_customer_similarity",
                op=">=",
                value=0.85,
            ),
        ],
        action=RuleAction.TAG_HIGH_RISK,
        action_params={"risk_level": "high", "tag": "nlp_cluster"},
        enabled=True,
        priority=18,
    ),
    RiskRuleIR(
        rule_id="payout_unrelated_first_high_review",
        description_cn="收款账户与投保人无关系且首次使用，且金额较高，触发复核。",
        conditions=[
            RuleCondition(entity="payout", field="unrelated_to_policyholder", op="==", value=True),
            RuleCondition(entity="payout", field="first_use_account", op="==", value=True),
            RuleCondition(entity="claim", field="claim_amount", op=">", value=100_000),
        ],
        action=RuleAction.MANUAL_REVIEW,
        action_params={"reason": "payout_unrelated_first_high_review"},
        enabled=True,
        priority=19,
    ),
    RiskRuleIR(
        rule_id="card_multi_customer_payout_30d",
        description_cn="同一银行卡在 30天 内被 >= 3 个客户用于赔付收款，触发预警。",
        conditions=[
            RuleCondition(
                entity="card",
                field="distinct_customer_count_30d",
                op=">=",
                value=3,
                time_window="30d",
            ),
        ],
        action=RuleAction.ALERT,
        action_params={"reason": "card_multi_customer_payout_30d"},
        enabled=True,
        priority=21,
    ),
    RiskRuleIR(
        rule_id="payout_blacklist_network_block",
        description_cn="赔付账户历史命中黑名单关联网络，拦截并人工核验。",
        conditions=[
            RuleCondition(entity="payout", field="blacklist_network_hit", op="==", value=True),
        ],
        action=RuleAction.MANUAL_REVIEW,
        action_params={"reason": "payout_blacklist_network_block"},
        enabled=True,
        priority=22,
    ),
    RiskRuleIR(
        rule_id="payout_account_change_reject_24h_2",
        description_cn="赔付前短时间内频繁更换收款账户（24小时 内 >= 2次），禁止自动赔付。",
        conditions=[
            RuleCondition(
                entity="payout",
                field="payee_account_change_count_24h",
                op=">=",
                value=2,
                time_window="24h",
            ),
        ],
        action=RuleAction.REJECT,
        action_params={"reason": "payout_account_change_reject_24h_2"},
        enabled=True,
        priority=23,
    ),
    RiskRuleIR(
        rule_id="agent_early_loss_channel_alert_30d",
        description_cn="同一代理人名下保单早期出险率（30天）显著高于渠道均值 x%，预警。",
        conditions=[
            RuleCondition(
                entity="agent",
                field="early_claim_rate_vs_channel_30d",
                op=">",
                value=1.2,
                time_window="30d",
            ),
        ],
        action=RuleAction.ALERT,
        action_params={"reason": "agent_early_loss_channel_alert_30d"},
        enabled=True,
        priority=24,
    ),
    RiskRuleIR(
        rule_id="channel_gbmi_anomaly_review",
        description_cn="某渠道短期内高保额低保费组合异常集中，触发渠道风控审查。",
        conditions=[
            RuleCondition(
                entity="channel",
                field="gbmi_anomaly_index",
                op=">",
                value=0.6,
            ),
        ],
        action=RuleAction.MANUAL_REVIEW,
        action_params={"reason": "channel_gbmi_anomaly_review"},
        enabled=True,
        priority=25,
    ),
    RiskRuleIR(
        rule_id="agent_template_input_qc",
        description_cn="代理人录入字段重复模板化明显（地址/职业异常一致），触发质检。",
        conditions=[
            RuleCondition(
                entity="agent",
                field="template_field_similarity",
                op=">",
                value=0.8,
            ),
        ],
        action=RuleAction.MANUAL_REVIEW,
        action_params={"reason": "agent_template_input_qc"},
        enabled=True,
        priority=26,
    ),
    RiskRuleIR(
        rule_id="blacklist_multi_dim_hit_reject",
        description_cn="客户证件号/手机号/设备/IP 任一命中黑名单，直接转人工或拒绝。",
        conditions=[
            RuleCondition(entity="blacklist", field="hit_any", op="==", value=True),
        ],
        action=RuleAction.REJECT,
        action_params={"reason": "blacklist_multi_dim_hit_reject"},
        enabled=True,
        priority=27,
    ),
    RiskRuleIR(
        rule_id="fraud_graph_shared_points_2",
        description_cn="与已确证欺诈客户共享关键关系点（设备、地址、收款卡）>= 2 个，标记高风险。",
        conditions=[
            RuleCondition(
                entity="graph",
                field="shared_risk_relation_points",
                op=">=",
                value=2,
                time_window="",
            ),
        ],
        action=RuleAction.TAG_HIGH_RISK,
        action_params={"risk_level": "high", "tag": "fraud_graph"},
        enabled=True,
        priority=28,
    ),
    RiskRuleIR(
        rule_id="new_customer_graph_strong_limit",
        description_cn="新客户首次投保即与高风险关系图谱强关联，限制自动通过。",
        conditions=[
            RuleCondition(
                entity="user",
                field="high_risk_graph_association_score",
                op=">",
                value=0.75,
            ),
        ],
        action=RuleAction.REJECT,
        action_params={"reason": "new_customer_graph_strong_limit"},
        enabled=True,
        priority=29,
    ),
]

# 备注稿扩展 100 条（材料/备注.md 第 77–176 行），IR 定义见 preset_rules_ext_100.py
PRESET_RULES = PRESET_RULES + EXT_REMARK_100_RULES

RULE_ID_TO_IR = {r.rule_id: r for r in PRESET_RULES}


def get_preset_rules():
    """返回当前启用的预设规则列表（副本），供遍历或 evaluate_rule 使用。"""
    return [r for r in PRESET_RULES if r.enabled]


def get_preset_by_rule_id(rule_id: str) -> Optional[RiskRuleIR]:
    """按 rule_id 返回预设规则（用于解析结果回退）。"""
    return RULE_ID_TO_IR.get(rule_id)
