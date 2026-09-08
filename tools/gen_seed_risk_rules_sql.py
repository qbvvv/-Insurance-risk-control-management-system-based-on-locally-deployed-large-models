"""生成 sql/seed_preset_risk_rules.sql（与 api.preset_rules 一致）。"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api.preset_rules import PRESET_RULES
from api.rule_ir_codec import ir_to_json_str
from rules_engine.schema import RuleAction

OUT = ROOT / "sql" / "seed_preset_risk_rules.sql"

lines = [
    "-- ============================================================ ",
    "-- 预设风控规则写入 risk_rules（与 api/preset_rules.py 完全一致，由本脚本生成） ",
    "-- 执行：.venv\\Scripts\\python.exe tools\\gen_seed_risk_rules_sql.py ",
    "-- ============================================================ ",
    "USE insurance_db;",
    "",
    "-- 若重复执行报主键冲突，可先：DELETE FROM risk_rules WHERE source = 'preset'; ",
    "",
]


def esc_sql(s: str) -> str:
    return s.replace("\\", "\\\\").replace("'", "''")


for ir in PRESET_RULES:
    j = ir_to_json_str(ir)
    action_val = ir.action.value if isinstance(ir.action, RuleAction) else str(ir.action)
    lines.append(
        "INSERT INTO risk_rules (rule_id, description_cn, action, source, ir_json, priority, enabled) VALUES ("
        f"'{esc_sql(ir.rule_id)}', '{esc_sql(ir.description_cn)}', '{esc_sql(action_val)}', 'preset', "
        f"'{esc_sql(j)}', {ir.priority}, {1 if ir.enabled else 0});"
    )

OUT.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote {OUT}")
