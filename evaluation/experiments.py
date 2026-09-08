"""
用于跑不同 prompt / 参数配置下的批量实验。
"""

import json
from pathlib import Path
from typing import List, Dict

from nlp_parser.parser_llm import QwenRuleLLMParser
from nlp_parser.postprocess import normalize_rule_json
from .metrics import field_level_accuracy, overall_rule_match_rate


def load_dataset(path: Path) -> List[Dict]:
    """
    假定数据集是一个 JSON lines 文件，每行一条：
    {"nl_rule": "...自然语言规则...", "gold": {...结构化规则...}}
    """
    samples: List[Dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            samples.append(json.loads(line))
    return samples


def run_experiment(
    dataset_path: str,
    prompt_variant: str = "json_only",
) -> None:
    """
    在给定数据集上，使用指定提示词版本跑一次实验并打印指标。
    """
    data_path = Path(dataset_path)
    samples = load_dataset(data_path)

    parser = QwenRuleLLMParser(prompt_variant=prompt_variant)

    gold_list: List[Dict] = []
    pred_list: List[Dict] = []

    for sample in samples:
        nl_rule = sample["nl_rule"]
        gold = sample["gold"]
        llm_out = parser.parse_single_rule_to_dict(nl_rule)
        norm_pred = normalize_rule_json(llm_out)

        gold_list.append(gold)
        pred_list.append(norm_pred)

    fields = ["rule_id", "description_cn", "entities", "time_window", "condition_logic", "threshold", "action"]
    field_acc = field_level_accuracy(gold_list, pred_list, fields)
    overall = overall_rule_match_rate(gold_list, pred_list)

    print(f"Prompt variant: {prompt_variant}")
    print("Field-level accuracy:", json.dumps(field_acc, ensure_ascii=False, indent=2))
    print(f"Overall match rate: {overall:.4f}")


if __name__ == "__main__":
    # 示例：python -m evaluation.experiments data/rules_dataset.jsonl json_only
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", help="数据集路径，如 data/rules_dataset.jsonl")
    parser.add_argument(
        "--prompt_variant",
        default="json_only",
        choices=["json_only", "cot_then_json", "batch_rules"],
    )
    args = parser.parse_args()

    run_experiment(args.dataset, prompt_variant=args.prompt_variant)

