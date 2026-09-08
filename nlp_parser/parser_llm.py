"""
使用 transformers 加载 Qwen-1.8B-Chat 的自然语言风控规则解析器。
支持本地目录或 ModelScope/HuggingFace 模型 ID。
"""

import json
import os
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from .prompt_templates import get_prompt_variants


@dataclass
class RiskRuleLLMOutput:
    """
    大模型直接输出的规则结构（尚未映射到规则引擎 IR）。
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
    # 有些大模型会把 JSON 输出包在 ```json ... ``` 代码块里；
    # 这函数会把它“裁剪”出来，保证后续 json.loads 能正常解析。
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        candidates = [p for p in parts if "{" in p or "[" in p]
        if candidates:
            return candidates[0].strip()
    return text


class QwenRuleLLMParser:
    """
    使用 transformers 加载 Qwen-1.8B-Chat 的自然语言风控规则解析器。
    模型路径支持：本地目录（如 ./qwen1.8）或模型 ID（如 Qwen/Qwen-1_8B-Chat）。
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        device: Optional[str] = None,
        prompt_variant: str = "json_only",
    ) -> None:
        """
        :param model_path: 模型路径。默认从环境变量 QWEN_MODEL_PATH 读取。
                          可以是本地目录（如 F:/桌面/保险项目/毕业设计/qwen1.8）
                          或 ModelScope/HuggingFace 模型 ID（如 Qwen/Qwen-1_8B-Chat）。
        :param device: 推理设备，如 "cuda"、"cpu"、"cuda:0"。默认自动选择（有 GPU 用 cuda）。
        :param prompt_variant: 提示词版本，json_only / cot_then_json / batch_rules。
        """
        # model_path：本地模型目录路径（或模型ID）
        # 这里优先使用调用方传入的 model_path；如果没传，就从环境变量 QWEN_MODEL_PATH 读取。
        model_path = model_path or os.getenv("QWEN_MODEL_PATH", "").strip()
        if not model_path:
            raise ValueError(
                "未设置 Qwen 模型路径，请在初始化时传入 model_path，"
                "或设置环境变量 QWEN_MODEL_PATH，例如：\n"
                "  QWEN_MODEL_PATH=F:/桌面/保险项目/毕业设计/qwen1.8\n"
                "或 QWEN_MODEL_PATH=Qwen/Qwen-1_8B-Chat"
            )

        # Windows 下如果模型目录名包含 '.'（例如 qwen1.8），transformers 的动态模块缓存
        # 可能会把它当作 Python 包路径的一部分，导致导入失败。
        # 这里做一个“自动复制到不含 '.' 的目录”的小修复，让你更少踩坑。
        p = Path(model_path)
        if p.exists() and p.is_dir() and "." in p.name:
            safe_dir = p.with_name(p.name.replace(".", "_"))
            try:
                if not safe_dir.exists():
                    shutil.copytree(p, safe_dir)
                model_path = str(safe_dir)
            except Exception:
                # 如果复制失败（如权限/磁盘问题），继续用原路径，让报错信息暴露给用户排查
                pass

        # 推理设备：
        # - 有 GPU：默认用 cuda
        # - 没 GPU：默认用 cpu
        self._device = device
        if self._device is None:
            self._device = "cuda" if torch.cuda.is_available() else "cpu"

        self._tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            trust_remote_code=True,
        )
        self._model = AutoModelForCausalLM.from_pretrained(
            model_path,
            trust_remote_code=True,
            torch_dtype="auto",
        )
        self._model = self._model.to(self._device)

        self._prompt_variants = get_prompt_variants()
        if prompt_variant not in self._prompt_variants:
            raise ValueError(f"未知提示词版本: {prompt_variant}")
        self.prompt_variant = prompt_variant

    def _build_messages(self, rule_text: str) -> List[Dict[str, str]]:
        # 把“规则文本”放进提示词模板，组装成给大模型的 system/user messages
        tpl = self._prompt_variants[self.prompt_variant]
        system_content = tpl.system
        user_content = tpl.user_instruction.format(rule_text=rule_text)
        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ]

    def parse_single_rule(
        self,
        rule_text: str,
        temperature: float = 0.2,
        max_tokens: int = 512,
    ) -> RiskRuleLLMOutput:
        """
        解析单条规则，返回大模型输出的结构。
        """
        messages = self._build_messages(rule_text)

        # prompt：
        # - system_prompt：约束大模型“必须输出 JSON”
        # - user_query：具体的自然语言规则文本
        # Qwen 仓库的 remote code 通常提供 model.chat(tokenizer, query, history, system=...)
        # 这种方式不依赖 tokenizer.chat_template，更稳定。
        system_prompt = messages[0]["content"]
        user_query = messages[1]["content"]

        if hasattr(self._model, "chat"):
            # Qwen 的 chat 接口返回 (response, history)
            kwargs: Dict[str, Any] = {
                "tokenizer": self._tokenizer,
                "query": user_query,
                "history": None,
                "system": system_prompt,
            }
            # 不同版本实现对参数名支持略有差异，这里尽量兼容
            try:
                # max_new_tokens：生成的“新内容”最大长度
                # temperature：越大越随机；风控规则解析一般用较小值更稳定
                content, _history = self._model.chat(
                    **kwargs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                )
            except TypeError:
                content, _history = self._model.chat(**kwargs)
        else:
            # 兜底：使用 transformers 的 chat template（若缺失，会有 warning，但仍可能可用）
            # 如果 model 没有 chat 方法，就用 generate 方式生成文本。
            text = self._tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
            inputs = self._tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=4096,
            ).to(self._model.device)

            with torch.no_grad():
                outputs = self._model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    do_sample=temperature > 0,
                    pad_token_id=self._tokenizer.eos_token_id,
                )

            response_ids = outputs[0][inputs["input_ids"].shape[1] :]
            content = self._tokenizer.decode(response_ids, skip_special_tokens=True)
        raw_json = _strip_code_fences(content)

        try:
            # 模型最终要输出 JSON，这里把字符串解析成 dict
            data = json.loads(raw_json)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"模型返回的 JSON 解析失败: {e}\n原始内容: {content}"
            ) from e

        return RiskRuleLLMOutput(
            rule_id=str(data.get("rule_id") or "auto_rule_id"),
            description_cn=str(data.get("description_cn") or rule_text),
            entities=list(data.get("entities") or []),
            time_window=data.get("time_window"),
            condition_logic=str(data.get("condition_logic") or ""),
            threshold=data.get("threshold"),
            action=str(data.get("action") or ""),
            confidence=float(data.get("confidence") or 0.5),
        )

    def parse_single_rule_to_dict(self, rule_text: str) -> Dict[str, Any]:
        # 把 dataclass 输出转换成普通 dict，便于后续 postprocess 和 API 返回
        return asdict(self.parse_single_rule(rule_text))
