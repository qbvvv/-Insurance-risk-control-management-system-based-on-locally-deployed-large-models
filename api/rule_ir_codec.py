"""RiskRuleIR ↔ JSON 字符串，供 MySQL risk_rules.ir_json 列存储。"""

from __future__ import annotations

import json
from typing import Any, Dict, List

from rules_engine.schema import RiskRuleIR, RuleAction, RuleCondition


def ir_to_json_str(ir: RiskRuleIR) -> str:
    d = ir_to_dict(ir)
    return json.dumps(d, ensure_ascii=False)


def ir_to_dict(ir: RiskRuleIR) -> Dict[str, Any]:
    action_val = ir.action.value if isinstance(ir.action, RuleAction) else str(ir.action)
    return {
        "rule_id": ir.rule_id,
        "description_cn": ir.description_cn,
        "conditions": [_cond_to_dict(c) for c in ir.conditions],
        "action": action_val,
        "action_params": dict(ir.action_params),
        "enabled": ir.enabled,
        "priority": ir.priority,
    }


def _cond_to_dict(c: RuleCondition) -> Dict[str, Any]:
    return {
        "entity": c.entity,
        "field": c.field,
        "op": c.op,
        "value": c.value,
        "time_window": c.time_window,
    }


def ir_from_json_str(s: str) -> RiskRuleIR:
    return ir_from_dict(json.loads(s))


def ir_from_dict(d: Dict[str, Any]) -> RiskRuleIR:
    conds: List[RuleCondition] = []
    for c in d.get("conditions") or []:
        conds.append(
            RuleCondition(
                entity=c["entity"],
                field=c["field"],
                op=c["op"],
                value=c["value"],
                time_window=c.get("time_window"),
            )
        )
    action_raw = d.get("action", "manual_review")
    try:
        action = RuleAction(action_raw)
    except ValueError:
        action = RuleAction.MANUAL_REVIEW
    return RiskRuleIR(
        rule_id=d["rule_id"],
        description_cn=d.get("description_cn") or "",
        conditions=conds,
        action=action,
        action_params=dict(d.get("action_params") or {}),
        enabled=bool(d.get("enabled", True)),
        priority=int(d.get("priority", 100)),
    )
