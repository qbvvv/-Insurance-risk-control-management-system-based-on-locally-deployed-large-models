"""
将大模型解析的 JSON 转为规则引擎 IR，供 API 调用。
若解析结果含 rule_id 且存在于预设库，优先返回预设 IR；
否则按全文匹配备注稿中的业务话术映射到对应预设规则（与 preset_rules 一致）。
"""

from dataclasses import replace
from typing import Any, Dict, List, Optional

from rules_engine.schema import RiskRuleIR, RuleCondition, RuleAction

from api.preset_rules import get_preset_by_rule_id


def _preset_from_fulltext(text: str) -> Optional[RiskRuleIR]:
    """将自然语言全文匹配到备注稿对应的预设 IR（按特异性优先）。"""
    t = text
    g = get_preset_by_rule_id

    if "同一用户" in t and ("3个月" in t or "三个月" in t) and "理赔" in t and "3" in t:
        return g("claim_freq_high_risk")
    if "保单年度" in t and "理赔" in t and "5" in t:
        return g("policy_year_claim_reject")
    if ("理赔" in t and "保费" in t and ("比例" in t or "/" in t) and "10" in t) or (
        "理赔金额" in t and "年保费" in t and "10" in t
    ):
        return g("claim_premium_ratio_review")
    if "新用户" in t and ("7天" in t or "7 天" in t) and "理赔" in t:
        return g("new_user_early_claim_review")
    if "证件号" in t and ("7天" in t or "7 天" in t) and "投保" in t:
        return g("id_no_apply_5_7d")
    if ("手机号" in t or "手机" in t) and ("证件号" in t or "证件" in t) and ("关联" in t or "不同" in t):
        return g("phone_idno_link_verify_3")
    if ("设备指纹" in t or "设备" in t) and ("24小时" in t or "24 小时" in t) and ("申请" in t or "提交" in t):
        return g("device_apply_reject_24h_10")
    if "被保险人" in t and "75" in t and "100万" in t:
        return g("insured_age75_cov1m_manual")
    if ("30天" in t or "30 天" in t) and ("同一地址" in t or "同址" in t) and "高额" in t and "保单" in t:
        return g("address_high_new_30d_4")
    if "保单生效" in t and ("7天" in t or "7 天" in t) and "理赔" in t:
        return g("policy_effective_claim_7d_review")
    if ("夜间" in t or "22:00" in t or "06:00" in t or "22" in t) and "理赔" in t and ("金额" in t or "阈值" in t):
        return g("night_claim_amount_manual")
    if ("夜间" in t or "22" in t) and "理赔" in t and "金额" not in t and "阈值" not in t:
        return g("night_claim_manual")
    if "NLP" in t or ("相似" in t and "多客户" in t):
        return g("claim_nlp_similar_cluster")
    if "收款" in t and "投保人" in t and ("无关系" in t or "无亲属" in t) and ("首次" in t or "首次使用" in t):
        return g("payout_unrelated_first_high_review")
    if "银行卡" in t and ("30天" in t or "30 天" in t) and "客户" in t and ("赔付" in t or "收款" in t):
        return g("card_multi_customer_payout_30d")
    if "赔付" in t and "黑名单" in t and ("关联网络" in t or "网络" in t):
        return g("payout_blacklist_network_block")
    if ("收款账户" in t or "收款账号" in t) and ("24小时" in t or "24 小时" in t) and ("更换" in t or "变更" in t):
        return g("payout_account_change_reject_24h_2")
    if "代理人" in t and ("早期出险" in t or "出险率" in t) and ("30天" in t or "30 天" in t or "渠道" in t):
        return g("agent_early_loss_channel_alert_30d")
    if "渠道" in t and "高保额" in t and "低保费" in t:
        return g("channel_gbmi_anomaly_review")
    if "代理人" in t and ("模板" in t or "重复" in t) and ("地址" in t or "职业" in t):
        return g("agent_template_input_qc")
    if ("黑名单" in t or "命中黑名单" in t) and (
        "证件" in t or "手机" in t or "设备" in t or "IP" in t or "ip" in t
    ):
        return g("blacklist_multi_dim_hit_reject")
    if ("确证欺诈" in t or "欺诈客户" in t) and ("共享" in t or "关系点" in t):
        return g("fraud_graph_shared_points_2")
    if "新客户" in t and ("关系图谱" in t or "图谱" in t):
        return g("new_customer_graph_strong_limit")
    if "收货地址" in t and "高额保单" in t and "5" in t:
        return g("address_multi_high_policy_verify")
    if "投保人" in t and "70" in t and "年龄" in t:
        return g("elderly_manual_underwrite")
    if "同一IP" in t and "10" in t:
        return g("ip_freq_abnormal")
    if "银行卡" in t and "3" in t and "保单" in t and "客户" not in t:
        return g("card_multi_policy_alert")
    if "命中黑名单" in t:
        return g("blacklist_multi_dim_hit_reject")
    if "共享" in t and ("关系点" in t or "关系图谱" in t) and (">=" in t or "≥" in t):
        return g("fraud_graph_shared_points_2")
    return None


def build_ir_from_llm_json(j: Dict[str, Any]) -> RiskRuleIR:
    """
    把“大模型输出 JSON”变成“规则引擎可执行 IR（RiskRuleIR）”。

    1) rule_id 命中预设库则直接复用预设 IR。
    2) 否则按 description_cn + condition_logic + threshold 全文匹配备注稿预设。
    3) 否则用关键词拼装条件（可能与多条同时命中，用于兼容旧逻辑）。
    """
    rid = j.get("rule_id")
    if rid:
        preset = get_preset_by_rule_id(rid)
        if preset is not None:
            return preset

    text = (
        (j.get("description_cn") or "")
        + " "
        + (j.get("condition_logic") or "")
        + " "
        + str(j.get("threshold") or "")
    )

    matched = _preset_from_fulltext(text)
    if matched is not None:
        desc = str(j.get("description_cn") or "").strip() or matched.description_cn
        new_id = str(j.get("rule_id") or "").strip() or matched.rule_id
        return replace(matched, rule_id=new_id, description_cn=desc)

    conditions: List[RuleCondition] = []
    if "理赔" in text and "次" in text and "保单年度" not in text:
        conditions.append(
            RuleCondition(
                entity="claim",
                field="count_3m",
                op=">",
                value=3,
                time_window="3m",
            )
        )
    if "投保" in text and ("笔" in text or "次" in text):
        conditions.append(
            RuleCondition(
                entity="policy",
                field="count_short_term",
                op=">",
                value=2,
                time_window="1m",
            )
        )
    if ("手机号" in text or "手机" in text) and ("证件号" in text or "证件" in text) and ("不同" in text or "关联" in text):
        conditions.append(
            RuleCondition(
                entity="phone",
                field="distinct_idno_count",
                op=">=",
                value=3,
                time_window="",
            )
        )
    if "证件号" in text and ("7天" in text or "7 天" in text) and "投保" in text and ("提交" in text or "申请" in text):
        conditions.append(
            RuleCondition(
                entity="id_no",
                field="policy_apply_count_7d",
                op=">=",
                value=5,
                time_window="7d",
            )
        )
    if ("设备" in text and ("24小时" in text or "24 小时" in text) and ("提交" in text or "申请" in text)):
        conditions.append(
            RuleCondition(
                entity="device",
                field="apply_count_24h",
                op=">=",
                value=10,
                time_window="24h",
            )
        )
    if (("30天" in text or "30 天" in text) and ("同一地址" in text or "同址" in text) and "高额" in text and "保单" in text):
        conditions.append(
            RuleCondition(
                entity="address",
                field="high_policy_new_count_30d",
                op=">=",
                value=4,
                time_window="30d",
            )
        )
    if (("收款账户" in text or "收款账号" in text) and ("更换" in text or "变更" in text) and ("24小时" in text or "24 小时" in text)):
        conditions.append(
            RuleCondition(
                entity="payout",
                field="payee_account_change_count_24h",
                op=">=",
                value=2,
                time_window="24h",
            )
        )
    if "命中黑名单" in text:
        conditions.append(
            RuleCondition(
                entity="blacklist",
                field="hit_any",
                op="==",
                value=True,
                time_window="",
            )
        )
    if ("共享" in text and ("关系点" in text or "关系图谱" in text) and (">=" in text or "≥" in text)):
        conditions.append(
            RuleCondition(
                entity="graph",
                field="shared_risk_relation_points",
                op=">=",
                value=2,
                time_window="",
            )
        )
    if not conditions:
        conditions.append(
            RuleCondition(entity="user", field="risk_score", op=">", value=0)
        )

    action_str = j.get("action", "")
    if "高风险" in action_str:
        action = RuleAction.TAG_HIGH_RISK
        action_params = {"risk_level": "high"}
    elif "人工审核" in action_str:
        action = RuleAction.MANUAL_REVIEW
        action_params = {}
    elif "黑名单" in action_str:
        action = RuleAction.CUSTOM
        action_params = {"list": "blacklist"}
    else:
        action = RuleAction.TAG_HIGH_RISK
        action_params = {"risk_level": "high"}

    return RiskRuleIR(
        rule_id=j.get("rule_id") or "auto_rule_id",
        description_cn=j.get("description_cn") or "",
        conditions=conditions,
        action=action,
        action_params=action_params,
        enabled=True,
        priority=10,
    )
