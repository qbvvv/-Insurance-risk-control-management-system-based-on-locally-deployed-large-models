"""
对大模型输出的 JSON 结果进行校验和简单修正。

这部分可以在论文中作为“规则生成结果质量提升”的一块内容：
- 字段完整性校验
- 合法值范围校验（如 confidence 必须在 0~1）
- 简单的规则归一化（去空格、统一大小写等）
"""

from typing import Any, Dict


def clamp_confidence(conf: Any) -> float:
    # confidence 通常应该是 0~1 的小数；
    # 如果模型输出成了非数字（或漏字段），就回退到默认 0.5。
    try:
        v = float(conf)
    except Exception:
        return 0.5
    return max(0.0, min(1.0, v))


def normalize_rule_json(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    输入：模型原始 JSON dict
    输出：经过简单清洗、补全后的 JSON dict

    你可以把它理解为：
    - 让字段齐全（缺了补默认值）
    - 让 confidence 落在合理范围
    - 去掉一些多余空格，减少后续字符串解析/展示的麻烦
    """
    data = dict(raw)  # 浅拷贝

    data.setdefault("rule_id", "auto_rule_id")
    data.setdefault("description_cn", "")
    data.setdefault("entities", [])
    data.setdefault("time_window", None)
    data.setdefault("condition_logic", "")
    data.setdefault("threshold", None)
    data.setdefault("action", "")
    data["confidence"] = clamp_confidence(data.get("confidence", 0.5))

    # 去掉 description、action 等字符串首尾空格
    for key in ["rule_id", "description_cn", "condition_logic", "action"]:
        if isinstance(data.get(key), str):
            data[key] = data[key].strip()

    return data

