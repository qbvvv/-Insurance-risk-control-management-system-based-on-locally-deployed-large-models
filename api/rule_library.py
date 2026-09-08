"""规则库统一入口：MySQL risk_rules 与无库时的内存 NL 规则。"""

from __future__ import annotations

import uuid
from dataclasses import replace
from typing import Any, Dict, List

from api.database import db_enabled
from api.preset_rules import get_preset_by_rule_id, get_preset_rules
from rules_engine.schema import RiskRuleIR

_memory_nl: List[RiskRuleIR] = []


def get_executable_rules() -> List[RiskRuleIR]:
    if db_enabled():
        from api.store_mysql import list_all_risk_rule_ids, list_risk_rule_irs

        db_irs = list_risk_rule_irs()
        known_ids = set(list_all_risk_rule_ids())
        extra = [ir for ir in get_preset_rules() if ir.rule_id not in known_ids]
        merged = sorted(
            db_irs + extra,
            key=lambda x: (x.priority, x.rule_id),
        )
        if merged:
            return merged
        # 表为空：与旧逻辑一致，退化为纯代码预设
        if not known_ids:
            return list(get_preset_rules())
        return []
    base = list(get_preset_rules())
    seen = {r.rule_id for r in base}
    for r in _memory_nl:
        if r.enabled and r.rule_id not in seen:
            base.append(r)
            seen.add(r.rule_id)
    return base


def list_rules_for_api() -> List[Dict[str, Any]]:
    if db_enabled():
        from api.store_mysql import list_all_risk_rule_ids, list_risk_rules_api_rows

        db_rows = list_risk_rules_api_rows()
        db_map = {r["rule_id"]: r for r in db_rows}
        existing_any = set(list_all_risk_rule_ids())
        preset_sorted = sorted(get_preset_rules(), key=lambda x: (x.priority, x.rule_id))
        merged: List[Dict[str, Any]] = []
        for ir in preset_sorted:
            rid = ir.rule_id
            if rid in db_map:
                merged.append(db_map[rid])
            elif rid not in existing_any:
                # 代码里新增的预设尚未写入 MySQL：直接展示（重启后会由 sync_preset_rules_from_code 落库）
                merged.append(
                    {
                        "rule_id": ir.rule_id,
                        "description_cn": ir.description_cn,
                        "action": ir.action.value,
                        "source": "preset",
                    }
                )
            # rid 已在库但 enabled=0：列表不展示（与仅返回启用行的语义一致）
        seen = {r["rule_id"] for r in merged}
        for r in db_rows:
            if r["rule_id"] not in seen:
                merged.append(r)
                seen.add(r["rule_id"])
        if merged:
            return merged
        if not existing_any:
            return [
                {
                    "rule_id": r.rule_id,
                    "description_cn": r.description_cn,
                    "action": r.action.value,
                    "source": "preset",
                }
                for r in get_preset_rules()
            ]
        return []
    rows: List[Dict[str, Any]] = [
        {
            "rule_id": r.rule_id,
            "description_cn": r.description_cn,
            "action": r.action.value,
            "source": "preset",
        }
        for r in get_preset_rules()
    ]
    seen = {r["rule_id"] for r in rows}
    for r in _memory_nl:
        if r.enabled:
            item = {
                "rule_id": r.rule_id,
                "description_cn": r.description_cn,
                "action": r.action.value,
                "source": "nl_parsed",
            }
            if r.rule_id in seen:
                for i, x in enumerate(rows):
                    if x["rule_id"] == r.rule_id:
                        rows[i] = item
                        break
            else:
                rows.append(item)
                seen.add(r.rule_id)
    return rows


def try_save_parsed_rule(ir: RiskRuleIR, norm: Dict[str, Any]) -> bool:
    """
    将解析得到的 IR 写入规则库。
    - 与预设库为同一对象引用时不重复写入。
    - auto_rule_id / demo_rule / 空 id 会生成 nl_ 前缀新 id 并回写 norm["rule_id"]。
    """
    preset = get_preset_by_rule_id(ir.rule_id)
    if preset is not None and ir is preset:
        return False

    if not ir.rule_id or ir.rule_id in ("auto_rule_id", "demo_rule"):
        new_id = f"nl_{uuid.uuid4().hex[:12]}"
        ir = replace(ir, rule_id=new_id)
        norm["rule_id"] = new_id

    if db_enabled():
        from api.store_mysql import upsert_nl_risk_rule

        upsert_nl_risk_rule(ir)
    else:
        _append_memory_nl(ir)
    return True


def get_rule_detail(rule_id: str) -> Optional[Dict[str, Any]]:
    """读取规则详情（用于编辑/删除前展示）。"""
    rid = (rule_id or "").strip()
    if not rid:
        return None
    # 优先查 DB（若启用）
    if db_enabled():
        from api.store_mysql import get_risk_rule_row

        return get_risk_rule_row(rid)
    # 无 DB：预设规则来自代码；nl_parsed 来自内存
    preset = get_preset_by_rule_id(rid)
    if preset is not None:
        return {
            "rule_id": preset.rule_id,
            "description_cn": preset.description_cn,
            "action": preset.action.value,
            "source": "preset",
            "priority": int(getattr(preset, "priority", 100) or 100),
            "enabled": 1 if getattr(preset, "enabled", True) else 0,
            "ir_json": "",
        }
    for r in _memory_nl:
        if r.rule_id == rid:
            return {
                "rule_id": r.rule_id,
                "description_cn": r.description_cn,
                "action": r.action.value,
                "source": "nl_parsed",
                "priority": int(getattr(r, "priority", 100) or 100),
                "enabled": 1 if getattr(r, "enabled", True) else 0,
                "ir_json": "",
            }
    return None


def update_rule(rule_id: str, patch: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """更新规则（DB：更新 risk_rules；内存：仅更新 nl 规则）。"""
    rid = (rule_id or "").strip()
    if not rid:
        return None
    if db_enabled():
        from api.store_mysql import update_risk_rule_row

        return update_risk_rule_row(rid, patch)
    # 预设规则不允许修改
    if get_preset_by_rule_id(rid) is not None:
        return None
    for i, r in enumerate(_memory_nl):
        if r.rule_id != rid:
            continue
        desc = patch.get("description_cn")
        action = patch.get("action")
        enabled = patch.get("enabled")
        priority = patch.get("priority")
        nr = r
        if desc is not None:
            nr = replace(nr, description_cn=str(desc))
        if action is not None:
            # 内存版仅支持保持原 action（避免解析枚举失败），允许传入同值
            pass
        if enabled is not None:
            nr = replace(nr, enabled=bool(int(enabled)) if str(enabled).isdigit() else bool(enabled))
        if priority is not None:
            try:
                nr = replace(nr, priority=int(priority))
            except Exception:
                pass
        _memory_nl[i] = nr
        return {
            "rule_id": nr.rule_id,
            "description_cn": nr.description_cn,
            "action": nr.action.value,
            "source": "nl_parsed",
            "priority": int(getattr(nr, "priority", 100) or 100),
            "enabled": 1 if getattr(nr, "enabled", True) else 0,
        }
    return None


def delete_rule(rule_id: str) -> bool:
    """删除规则（DB：仅删除 nl_parsed；内存：仅删除内存 nl 规则）。"""
    rid = (rule_id or "").strip()
    if not rid:
        return False
    if db_enabled():
        from api.store_mysql import delete_risk_rule_row

        return delete_risk_rule_row(rid)
    if get_preset_by_rule_id(rid) is not None:
        return False
    global _memory_nl
    before = len(_memory_nl)
    _memory_nl = [x for x in _memory_nl if x.rule_id != rid]
    return len(_memory_nl) != before


def _append_memory_nl(ir: RiskRuleIR) -> None:
    global _memory_nl
    for i, x in enumerate(_memory_nl):
        if x.rule_id == ir.rule_id:
            _memory_nl[i] = ir
            return
    _memory_nl.append(ir)
