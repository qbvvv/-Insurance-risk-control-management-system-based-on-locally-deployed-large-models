from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class RuleAction(str, Enum):
    """规则命中后的动作类型。"""

    TAG_HIGH_RISK = "tag_high_risk"
    MANUAL_REVIEW = "manual_review"
    REJECT = "reject"
    ALERT = "alert"
    CUSTOM = "custom"


@dataclass
class RuleCondition:
    """
    条件表达式的简化中间表示。

    示例：
    - entity: "claim"
      field: "count"
      op: ">"
      value: 3
      time_window: "3m"  # 3 个月
    """

    entity: str
    field: str
    op: str
    value: Any
    time_window: Optional[str] = None


@dataclass
class RiskRuleIR:
    """
    风控规则的中间表示（Intermediate Representation）。

    这是连接“大模型解析结果 JSON” 与 “规则执行引擎”的桥梁。
    """

    rule_id: str
    description_cn: str
    conditions: List[RuleCondition]
    action: RuleAction
    action_params: Dict[str, Any]
    enabled: bool = True
    priority: int = 100  # 数字越小优先级越高

