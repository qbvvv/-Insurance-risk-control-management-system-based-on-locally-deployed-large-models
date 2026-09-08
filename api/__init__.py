"""
对外提供 HTTP 接口的模块。

计划：
- server.py 使用 FastAPI 提供简单的 REST API：
  - POST /parse_rule: 输入自然语言风控规则，返回结构化 JSON
  - POST /execute_rule: 输入规则 + 业务数据，返回命中结果（可选）

说明：
- 这个目录通常会按“路由接口（server.py）/ 数据存储（*_store.py）/ 规则辅助（rule_helpers.py）/ 预设规则（preset_rules.py）”来组织
- 你后续如果要扩展“更多业务模块”，一般就是在这里继续增加新的 *store 或 router 逻辑
"""

