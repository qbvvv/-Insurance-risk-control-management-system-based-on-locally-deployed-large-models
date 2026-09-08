"""
全局配置（示例），方便在代码中集中管理路径和默认参数。
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_DATASET = DATA_DIR / "rules_dataset.jsonl"

