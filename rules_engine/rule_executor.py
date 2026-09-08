from dataclasses import asdict
from typing import Any, Dict, List, Tuple

from .schema import RiskRuleIR, RuleAction


class RuleExecutor:
    """
    极简版规则执行引擎。

    目标：
    - 方便在毕设里演示“规则从自然语言 → 结构化 → 可执行”
    - 支持对单条交易/理赔记录进行规则命中判断
    - 输出命中结果和动作，便于后续接入风控系统
    """

    def __init__(self, rules: List[RiskRuleIR]) -> None:
        self.rules = [r for r in rules if r.enabled]

    def evaluate_record(self, record: Dict[str, Any]) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        对单条记录执行所有规则。

        :param record: 业务记录，简单用 dict 表示，例如：
                       {"user_id": "u1", "claim_amount": 60000, "claim_count_3m": 4}
        :return: (是否命中任一规则, 命中详情列表)
        """
        hits: List[Dict[str, Any]] = []

        for rule in sorted(self.rules, key=lambda r: r.priority):
            if self._match_rule(rule, record):
                hits.append(
                    {
                        "rule_id": rule.rule_id,
                        "description_cn": rule.description_cn,
                        "action": rule.action.value,
                        "action_params": rule.action_params,
                    }
                )

        return (len(hits) > 0, hits)

    def _match_rule(self, rule: RiskRuleIR, record: Dict[str, Any]) -> bool:
        """
        简化版的“条件全部 AND”匹配逻辑。
        """
        for cond in rule.conditions:
            # 这里假设 record 中的 key 为 "{entity}_{field}" 或直接是 field
            key_candidates = [f"{cond.entity}_{cond.field}", cond.field]
            value = None
            for k in key_candidates:
                if k in record:
                    value = record[k]
                    break

            if value is None:
                return False

            if not self._compare(value, cond.op, cond.value):
                return False

        return True

    @staticmethod
    def _compare(left: Any, op: str, right: Any) -> bool:
        """
        极简比较逻辑，支持常见运算符及 in（右值为可迭代集合）。
        """
        if op == ">":
            return left > right
        if op == ">=":
            return left >= right
        if op == "<":
            return left < right
        if op == "<=":
            return left <= right
        if op == "==":
            return left == right
        if op == "!=":
            return left != right
        if op == "in":
            try:
                return left in right
            except TypeError:
                return False
        # 兜底：未知运算符，直接返回 False
        return False


if __name__ == "__main__":
    """
    简单命令行测试：演示如何从 IR 执行规则。
    """
    from .schema import RiskRuleIR, RuleCondition

    rule = RiskRuleIR(
        rule_id="claim_freq_high_risk",
        description_cn="同一用户3个月内理赔超过3次则标记为高风险",
        conditions=[
            RuleCondition(
                entity="claim",
                field="count_3m",
                op=">",
                value=3,
            )
        ],
        action=RuleAction.TAG_HIGH_RISK,
        action_params={"risk_level": "high"},
        priority=10,
    )

    executor = RuleExecutor([rule])
    record = {"user_id": "u1", "claim_count_3m": 4}
    hit, details = executor.evaluate_record(record)
    print("hit:", hit)
    print("details:", details)

