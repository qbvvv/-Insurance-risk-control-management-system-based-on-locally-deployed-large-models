"""
毕业设计主演示脚本：
- 演示从自然语言风控规则 → 结构化规则 JSON → 规则执行的完整流程
"""

import json
from pathlib import Path

from nlp_parser.parser_llm import QwenRuleLLMParser
from nlp_parser.postprocess import normalize_rule_json
from rules_engine.schema import RiskRuleIR, RuleCondition, RuleAction
from rules_engine.rule_executor import RuleExecutor


def build_ir_from_llm_json(j: dict) -> RiskRuleIR:
    """
    将大模型解析后的 JSON 映射为规则引擎的中间表示 IR。
    这里做一个非常简化的映射示例，真实项目中可根据字段更精细设计。
    """
    # 简单假设：如果 condition_logic/threshold 中包含“理赔次数”，则映射到 claim.count_3m
    conditions = []
    text = (j.get("condition_logic") or "") + " " + (j.get("threshold") or "")
    if "理赔" in text and "次" in text:
        conditions.append(
            RuleCondition(
                entity="claim",
                field="count_3m",
                op=">",
                value=3,
                time_window="3m",
            )
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
        action = RuleAction.CUSTOM
        action_params = {}

    return RiskRuleIR(
        rule_id=j["rule_id"],
        description_cn=j["description_cn"],
        conditions=conditions,
        action=action,
        action_params=action_params,
        enabled=True,
        priority=10,
    )


def main() -> None:
    # 1. 自然语言规则
    nl_rule = "同一用户3个月内理赔超过3次则标记为高风险"

    # 2. 调用大模型解析（未设置 QWEN_MODEL_PATH 时默认用项目下的 qwen1.8）
    default_model = (Path(__file__).parent / "qwen1_8").resolve().as_posix()
    parser = QwenRuleLLMParser(model_path=default_model, prompt_variant="json_only")
    raw_json = parser.parse_single_rule_to_dict(nl_rule)
    norm_json = normalize_rule_json(raw_json)

    print("=== LLM 解析结果（规范化后） ===")
    print(json.dumps(norm_json, ensure_ascii=False, indent=2))

    # 3. 映射到规则引擎 IR
    ir_rule = build_ir_from_llm_json(norm_json)

    # 4. 构造规则执行器并对样例数据执行
    executor = RuleExecutor([ir_rule])
    record = {"user_id": "u1", "claim_count_3m": 4}
    hit, details = executor.evaluate_record(record)

    print("\n=== 规则执行结果 ===")
    print("是否命中规则:", hit)
    print("命中详情:", json.dumps(details, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

