from typing import Dict, List, Tuple


def field_level_accuracy(
    gold: List[Dict], pred: List[Dict], fields: List[str]
) -> Dict[str, float]:
    """
    计算指定字段上的准确率，用于评估“自然语言 → 结构化规则”的质量。

    :param gold: 标注好的标准答案列表
    :param pred: 模型输出的预测结果列表
    :param fields: 需要评估的字段名列表，如 ["rule_id", "entities", "action"]
    """
    assert len(gold) == len(pred), "gold 和 pred 数量必须一致"

    result: Dict[str, float] = {}
    n = len(gold)
    for field in fields:
        correct = 0
        for g, p in zip(gold, pred):
            if g.get(field) == p.get(field):
                correct += 1
        result[field] = correct / n if n > 0 else 0.0
    return result


def overall_rule_match_rate(gold: List[Dict], pred: List[Dict]) -> float:
    """
    规则整体匹配率：所有字段都相同才算命中。
    """
    assert len(gold) == len(pred), "gold 和 pred 数量必须一致"
    n = len(gold)
    correct = 0
    for g, p in zip(gold, pred):
        if g == p:
            correct += 1
    return correct / n if n > 0 else 0.0

