"""
集中管理提示词模板，便于在 experiments 中切换和对比。
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class PromptTemplate:
    name: str
    system: str
    user_instruction: str


def basic_system_prompt() -> str:
    # system prompt 的作用：约束模型“只输出 JSON、不编造规则逻辑”
    # 这样你后面才能稳定使用 json.loads() 解析模型输出。
    return (
        "你是保险风控规则工程师，负责把中文自然语言规则精确转换成结构化 JSON。"
        "只根据用户给出的规则文本进行解析，不要自己发明业务逻辑。"
        "必须严格输出 JSON，字段含义如下：\n"
        "- rule_id: 规则唯一标识，若用户未给出，则根据含义生成一个简短的英文蛇形命名，例如 claim_freq_high_risk。\n"
        "- description_cn: 中文规则描述，尽量保持和用户原文一致。\n"
        "- entities: 规则涉及的业务实体列表，如 ['用户','保单','设备']。\n"
        "- time_window: 时间窗口，如 '3个月内','7天内'，没有则为 null。\n"
        "- condition_logic: 条件逻辑的自然语言描述（可带简单运算符）。\n"
        "- threshold: 阈值描述，如 '理赔次数>3'、'金额>=10000 元'，没有则为 null。\n"
        "- action: 命中规则后的动作，如 '标记为高风险','拒赔','人工审核'。\n"
        "- confidence: 模型对解析结果的置信度，0~1 的小数。\n"
    )


def get_prompt_variants() -> Dict[str, PromptTemplate]:
    """
    不同提示词版本，用于论文中的消融实验 / 对比实验。
    """

    # 版本 A：只输出 JSON
    variant_a = PromptTemplate(
        name="json_only",
        system=basic_system_prompt(),
        user_instruction="请将下面的风控规则解析为一个 JSON 对象，只输出 JSON，不要解释，不要额外文字：\n{rule_text}",
    )

    # 版本 B：先思考再输出 JSON（链式思考，但最终仍要求输出最后一行 JSON）
    variant_b = PromptTemplate(
        name="cot_then_json",
        system=basic_system_prompt()
        + "\n在内部可以先逐步思考规则涉及的主体、时间窗口和条件，但最终输出时只保留最后一行 JSON。",
        user_instruction=(
            "请先用 1-2 句话分析该规则的主体、时间范围和触发条件，"
            "最后一行单独输出一个 JSON 对象。JSON 字段与系统提示要求一致。\n"
            "{rule_text}"
        ),
    )

    # 版本 C：多规则批量解析（当输入是多行换行分隔的规则时）
    variant_c = PromptTemplate(
        name="batch_rules",
        system=basic_system_prompt()
        + "\n当输入包含多条换行分隔的规则时，输出一个 JSON 数组 rules。",
        user_instruction=(
            "下面给出多条风控规则（每行一条）。请将它们解析为一个 JSON 对象："
            '{"rules": [...]}，其中每个元素对应一条规则的解析结果。\n'
            "{rule_text}"
        ),
    )

    return {
        variant_a.name: variant_a,
        variant_b.name: variant_b,
        variant_c.name: variant_c,
    }

