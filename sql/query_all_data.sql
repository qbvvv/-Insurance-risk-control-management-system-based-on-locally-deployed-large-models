-- ============================================================
-- 查询 insurance_db 中各表全部数据（在 MySQL Workbench / 命令行中执行）
-- 使用前请先：USE insurance_db; 或在本连接中选中该库
-- ============================================================

USE insurance_db;

-- ---------- 客户 ----------
SELECT '=== customers 客户表 ===' AS section;
SELECT * FROM customers;

-- ---------- 保单 ----------
SELECT '=== policies 保单表 ===' AS section;
SELECT * FROM policies;

-- ---------- 保险产品 ----------
SELECT '=== products 产品表 ===' AS section;
SELECT * FROM products;

-- ---------- 承保案件 ----------
SELECT '=== underwriting_cases 承保案件 ===' AS section;
SELECT * FROM underwriting_cases;

-- ---------- 理赔案件 ----------
SELECT '=== claims 理赔案件 ===' AS section;
SELECT * FROM claims;

-- ---------- 售后与投诉工单 ----------
SELECT '=== service_tickets 售后与投诉 ===' AS section;
SELECT * FROM service_tickets;

-- ---------- 销售渠道 ----------
SELECT '=== channels 渠道 ===' AS section;
SELECT * FROM channels;

-- ---------- 保费收付流水 ----------
SELECT '=== premium_flows 保费收付 ===' AS section;
SELECT * FROM premium_flows;

-- ---------- 佣金结算 ----------
SELECT '=== commission_settlements 佣金结算 ===' AS section;
SELECT * FROM commission_settlements;

-- ---------- 再保合同 ----------
SELECT '=== reinsurance_contracts 再保合同 ===' AS section;
SELECT * FROM reinsurance_contracts;

-- ---------- 再保账单 ----------
SELECT '=== reinsurance_bills 再保账单 ===' AS section;
SELECT * FROM reinsurance_bills;

-- ---------- 代理人团队 ----------
SELECT '=== agent_teams 代理人团队 ===' AS section;
SELECT * FROM agent_teams;

-- ---------- 代理人 ----------
SELECT '=== agents 代理人 ===' AS section;
SELECT * FROM agents;

-- ---------- 代理人/团队业绩 ----------
SELECT '=== agent_performances 业绩汇总 ===' AS section;
SELECT * FROM agent_performances;

-- ---------- 系统管理 ----------
SELECT '=== system_users 系统用户 ===' AS section;
SELECT * FROM system_users;

SELECT '=== system_params 系统参数 ===' AS section;
SELECT * FROM system_params;

SELECT '=== system_logs 系统日志 ===' AS section;
SELECT * FROM system_logs;

-- ---------- 黑名单 ----------
SELECT '=== blacklist 黑名单 ===' AS section;
SELECT * FROM blacklist;

-- ---------- 风控规则库（预设 + NL 入库）----------
SELECT '=== risk_rules 规则库 ===' AS section;
SELECT id, rule_id, description_cn, action, source, priority, enabled, LEFT(ir_json, 120) AS ir_json_preview FROM risk_rules;

-- ---------- 风险预警 ----------
SELECT '=== risk_alerts 风险预警 ===' AS section;
SELECT
  id,
  code,
  alert_type,
  alert_desc,
  risk_level
FROM risk_alerts;

-- （若希望列名与接口 JSON 一致，可用下面别名版）
-- SELECT id, code, alert_type AS type, alert_desc AS `desc`, risk_level AS level FROM risk_alerts;
