import json
import os
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

from llama_cpp import Llama


@dataclass
class RiskRule:
    """
    规则结构化表示，可根据你的数据库/规则引擎继续扩展字段。
    """
    rule_id: str
    description_cn: str
    entities: List[str]
    time_window: Optional[str]
    condition_logic: str
    threshold: Optional[str]
    action: str
    confidence: float


def _strip_code_fences(text: str) -> str:
    """
    去掉模型可能生成的 ```json ... ``` 包裹。
    """
    text = text.strip()
    if text.startswith("```"):
        # ```json\n...\n```
        parts = text.split("```")
        # 期望中间那段是 JSON
        candidates = [p for p in parts if "{" in p or "[" in p]
        if candidates:
            return candidates[0].strip()
    return text


class QwenRiskRuleParser:
    """
    使用本地 Qwen-7B-Chat-Q5_K_M.gguf 的风控规则解析器。
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        n_ctx: int = 4096,
        n_threads: Optional[int] = None,
    ) -> None:
        """
        :param model_path: GGUF 模型路径，默认从环境变量 QWEN_GGUF_PATH 读取。
        :param n_ctx: 上下文长度。
        :param n_threads: 线程数，默认使用 os.cpu_count()。
        """
        model_path = model_path or os.getenv("QWEN_GGUF_PATH", "").strip()
        if not model_path:
            raise ValueError(
                "未设置 Qwen GGUF 模型路径，请在初始化时传入 model_path，"
                "或设置环境变量 QWEN_GGUF_PATH，例如："
                "QWEN_GGUF_PATH=f:/models/Qwen-7B-Chat-Q5_K_M.gguf"
            )

        self._llm = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_threads=n_threads or os.cpu_count() or 4,
            # llama-cpp 内置的 Qwen 聊天模板
            chat_format="qwen",
        )

        # 系统提示词模板（可根据需要在外部暴露）
        self.system_prompt_basic = (
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

        # few-shot 示例提示词（给模型看作参考）
        self.few_shot_examples = [
            {
                "user": "同一用户3个月内理赔超过3次则标记为高风险",
                "assistant": {
                    "rule_id": "claim_freq_high_risk",
                    "description_cn": "同一用户3个月内理赔超过3次则标记为高风险",
                    "entities": ["用户", "理赔记录"],
                    "time_window": "3个月内",
                    "condition_logic": "同一用户的理赔次数 > 3",
                    "threshold": "理赔次数 > 3",
                    "action": "标记为高风险",
                    "confidence": 0.95,
                },
            },
            {
                "user": "单笔理赔金额超过5万元需要人工审核",
                "assistant": {
                    "rule_id": "large_claim_manual_review",
                    "description_cn": "单笔理赔金额超过5万元需要人工审核",
                    "entities": ["理赔记录"],
                    "time_window": None,
                    "condition_logic": "单笔理赔金额 > 50000 元",
                    "threshold": "金额 > 50000 元",
                    "action": "人工审核",
                    "confidence": 0.96,
                },
            },
        ]

    def _build_few_shot_text(self) -> str:
        """
        把 few-shot 示例拼成一个文本放在 system 里，减少调用复杂度。
        """
        lines: List[str] = ["下面是若干示例："]
        for ex in self.few_shot_examples:
            lines.append(f"【示例用户输入】{ex['user']}")
            lines.append("【示例解析结果(JSON)】")
            lines.append(json.dumps(ex["assistant"], ensure_ascii=False))
        return "\n".join(lines)

    def build_prompt_for_rule(self, rule_text: str) -> List[Dict[str, Any]]:
        """
        构造聊天消息列表，供 llama-cpp 的 create_chat_completion 使用。
        """
        system_content = self.system_prompt_basic + "\n" + self._build_few_shot_text()

        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": system_content},
            {
                "role": "user",
                "content": (
                    "请将下面的风控规则解析为一个 JSON 对象，"
                    "只输出 JSON，不要解释，不要额外文字：\n"
                    f"{rule_text}"
                ),
            },
        ]
        return messages

    def parse_rule(
        self,
        rule_text: str,
        temperature: float = 0.2,
        max_tokens: int = 512,
    ) -> RiskRule:
        """
        解析单条规则，返回结构化 RiskRule。
        """
        messages = self.build_prompt_for_rule(rule_text)

        result = self._llm.create_chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        content: str = result["choices"][0]["message"]["content"]
        raw_json = _strip_code_fences(content)

        try:
            data = json.loads(raw_json)
        except json.JSONDecodeError as e:
            # 如果解析失败，可以在这里记录日志或抛出自定义异常
            raise ValueError(f"模型返回的 JSON 解析失败: {e}\n原始内容: {content}") from e

        # 容错处理：缺失字段时给默认值
        rule = RiskRule(
            rule_id=str(data.get("rule_id") or "auto_rule_id"),
            description_cn=str(data.get("description_cn") or rule_text),
            entities=list(data.get("entities") or []),
            time_window=data.get("time_window"),
            condition_logic=str(data.get("condition_logic") or ""),
            threshold=data.get("threshold"),
            action=str(data.get("action") or ""),
            confidence=float(data.get("confidence") or 0.5),
        )
        return rule

    def parse_rule_to_dict(self, rule_text: str) -> Dict[str, Any]:
        """
        解析规则并直接返回 dict，方便和其他模块对接或直接存数据库。
        """
        return asdict(self.parse_rule(rule_text))


if __name__ == "__main__":
    """
    简单命令行测试：
    1. 先安装依赖：pip install -r requirements.txt
    2. 设置环境变量 QWEN_GGUF_PATH 指向你的 GGUF 文件。
    3. 运行：python module2_qwen_llm.py
    """
    example_rule = "同一用户3个月内理赔超过3次则标记为高风险"
    parser = QwenRiskRuleParser()
    parsed = parser.parse_rule_to_dict(example_rule)
    print(json.dumps(parsed, ensure_ascii=False, indent=2))

