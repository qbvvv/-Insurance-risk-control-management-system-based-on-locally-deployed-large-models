-- ============================================================
-- 保险风控项目 — MySQL 初始化脚本
-- 使用方法（任选其一）：
--   1) 无 mysql 命令行（Windows 常见）：在后端目录执行
--      .venv\Scripts\python.exe tools\run_init_sql.py
--   2) 已配置 PATH：mysql -u 你的用户名 -p < sql/init_insurance_db.sql
--   3) Navicat / MySQL Workbench：打开本文件后整段执行
-- ============================================================

-- 创建数据库（若已存在会报错，可先删掉或改用 IF NOT EXISTS）
CREATE DATABASE IF NOT EXISTS insurance_db
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE insurance_db;

-- -----------------------------
-- 客户表（对应 /customers API）
-- -----------------------------
DROP TABLE IF EXISTS customers;
CREATE TABLE customers (
  id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '内部主键',
  customer_no   VARCHAR(64)  NOT NULL COMMENT '客户编号',
  name          VARCHAR(64)  NOT NULL COMMENT '姓名',
  id_type       VARCHAR(32)  NOT NULL DEFAULT '身份证' COMMENT '证件类型',
  id_no         VARCHAR(64)  NOT NULL COMMENT '证件号',
  phone         VARCHAR(32)  NOT NULL COMMENT '手机号',
  occupation    VARCHAR(128) NOT NULL DEFAULT '' COMMENT '职业',
  level         VARCHAR(32)  NOT NULL DEFAULT '普通' COMMENT '客户等级',
  status        VARCHAR(32)  NOT NULL DEFAULT '在保' COMMENT '状态',
  photo         VARCHAR(512) NOT NULL DEFAULT '' COMMENT '头像/照片URL',
  gender        VARCHAR(16)  NOT NULL DEFAULT '未知' COMMENT '性别',
  address       VARCHAR(255) NOT NULL DEFAULT '' COMMENT '联系地址',
  remark        VARCHAR(512) NOT NULL DEFAULT '' COMMENT '备注',
  created_at    VARCHAR(32)  NULL COMMENT '创建日期(字符串，与现接口一致)',
  PRIMARY KEY (id),
  UNIQUE KEY uk_customer_no (customer_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='客户';

-- -----------------------------
-- 保单表（对应 /policies API）
-- -----------------------------
DROP TABLE IF EXISTS policies;
CREATE TABLE policies (
  id               BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '内部主键',
  policy_no        VARCHAR(64)  NOT NULL COMMENT '保单号',
  customer_no      VARCHAR(64)  NOT NULL COMMENT '客户编号',
  product_name     VARCHAR(128) NOT NULL COMMENT '产品名称',
  premium          VARCHAR(32)  NOT NULL DEFAULT '0' COMMENT '保费',
  coverage_amount  VARCHAR(32)  NOT NULL DEFAULT '0' COMMENT '保额',
  start_date       VARCHAR(32)  NULL COMMENT '起保日期',
  end_date         VARCHAR(32)  NULL COMMENT '止保日期',
  status           VARCHAR(32)  NOT NULL DEFAULT '生效中' COMMENT '保单状态',
  PRIMARY KEY (id),
  UNIQUE KEY uk_policy_no (policy_no),
  KEY idx_customer_no (customer_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='保单';

-- -----------------------------
-- 保险产品（对应 /products API，与保单 product_name 可对应）
-- -----------------------------
DROP TABLE IF EXISTS products;
CREATE TABLE products (
  id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '内部主键',
  product_no      VARCHAR(64)  NOT NULL COMMENT '产品编号',
  product_name    VARCHAR(128) NOT NULL COMMENT '产品名称',
  category        VARCHAR(64)  NOT NULL DEFAULT '' COMMENT '险种类别',
  description     VARCHAR(512) NOT NULL DEFAULT '' COMMENT '产品说明',
  premium_guide   VARCHAR(64)  NOT NULL DEFAULT '' COMMENT '参考保费/起价说明',
  coverage_cap    VARCHAR(64)  NOT NULL DEFAULT '0' COMMENT '保额上限说明',
  status          VARCHAR(32)  NOT NULL DEFAULT '在售' COMMENT '在售/停售',
  created_at      VARCHAR(32)  NULL COMMENT '创建日期',
  PRIMARY KEY (id),
  UNIQUE KEY uk_product_no (product_no),
  KEY idx_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='保险产品';

-- -----------------------------
-- 承保案件（对应 /underwriting_cases API）
-- -----------------------------
DROP TABLE IF EXISTS underwriting_cases;
CREATE TABLE underwriting_cases (
  id               BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '内部主键',
  case_no          VARCHAR(64)  NOT NULL COMMENT '投保单号/案件号 UW…',
  customer_no      VARCHAR(64)  NOT NULL COMMENT '客户编号',
  applicant_name   VARCHAR(64)  NOT NULL COMMENT '投保人姓名',
  id_no            VARCHAR(64)  NOT NULL DEFAULT '' COMMENT '证件号',
  product_name     VARCHAR(128) NOT NULL COMMENT '投保产品名称',
  premium          VARCHAR(32)  NOT NULL DEFAULT '0' COMMENT '申请保费',
  coverage_amount  VARCHAR(32)  NOT NULL DEFAULT '0' COMMENT '申请保额',
  channel          VARCHAR(64)  NOT NULL DEFAULT '' COMMENT '渠道',
  status           VARCHAR(32)  NOT NULL DEFAULT '待受理' COMMENT '案件状态',
  risk_score       VARCHAR(32)  NOT NULL DEFAULT '' COMMENT '风险分/等级',
  decision_note    VARCHAR(512) NOT NULL DEFAULT '' COMMENT '核保结论备注',
  policy_no        VARCHAR(64)  NULL COMMENT '通过后关联保单号',
  created_at       VARCHAR(32)  NULL,
  updated_at       VARCHAR(32)  NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_case_no (case_no),
  KEY idx_uw_customer (customer_no),
  KEY idx_uw_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='承保案件';

-- -----------------------------
-- 理赔案件（对应 /claims API）
-- -----------------------------
DROP TABLE IF EXISTS claims;
CREATE TABLE claims (
  id               BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '内部主键',
  claim_no         VARCHAR(64)  NOT NULL COMMENT '理赔案件号 CLM…',
  policy_no        VARCHAR(64)  NOT NULL COMMENT '关联保单号',
  customer_no      VARCHAR(64)  NOT NULL COMMENT '客户编号',
  claimant_name    VARCHAR(64)  NOT NULL COMMENT '申请人/索赔人',
  product_name     VARCHAR(128) NOT NULL COMMENT '险种/产品名称',
  claim_type       VARCHAR(64)  NOT NULL DEFAULT '' COMMENT '理赔类型',
  incident_reason  VARCHAR(256) NOT NULL DEFAULT '' COMMENT '出险原因',
  incident_date    VARCHAR(32)  NOT NULL DEFAULT '' COMMENT '出险日期',
  report_date      VARCHAR(32)  NOT NULL DEFAULT '' COMMENT '报案日期',
  claim_amount     VARCHAR(32)  NOT NULL DEFAULT '0' COMMENT '申请赔付金额',
  approved_amount  VARCHAR(32)  NOT NULL DEFAULT '' COMMENT '核定赔付金额',
  status           VARCHAR(32)  NOT NULL DEFAULT '待受理' COMMENT '案件状态',
  decision_note    VARCHAR(512) NOT NULL DEFAULT '' COMMENT '核赔结论备注',
  created_at       VARCHAR(32)  NULL,
  updated_at       VARCHAR(32)  NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_claim_no (claim_no),
  KEY idx_claim_policy (policy_no),
  KEY idx_claim_customer (customer_no),
  KEY idx_claim_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='理赔案件';

-- -----------------------------
-- 售后与投诉工单（对应 /service_tickets API）
-- -----------------------------
DROP TABLE IF EXISTS service_tickets;
CREATE TABLE service_tickets (
  id               BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '内部主键',
  ticket_no        VARCHAR(64)  NOT NULL COMMENT '工单号 CS…',
  ticket_type      VARCHAR(32)  NOT NULL DEFAULT '投诉' COMMENT '售后 | 投诉',
  customer_no      VARCHAR(64)  NOT NULL COMMENT '客户编号',
  contact_name     VARCHAR(64)  NOT NULL COMMENT '联系人姓名',
  phone            VARCHAR(32)  NOT NULL DEFAULT '' COMMENT '联系电话',
  policy_no        VARCHAR(64)  NOT NULL DEFAULT '' COMMENT '关联保单号',
  category         VARCHAR(128) NOT NULL DEFAULT '' COMMENT '类型/分类',
  subject          VARCHAR(256) NOT NULL DEFAULT '' COMMENT '主题摘要',
  content          LONGTEXT     NOT NULL COMMENT '详细内容',
  status           VARCHAR(32)  NOT NULL DEFAULT '待受理' COMMENT '处理状态',
  handler          VARCHAR(64)  NOT NULL DEFAULT '' COMMENT '处理人',
  resolution_note  VARCHAR(512) NOT NULL DEFAULT '' COMMENT '处理结果说明',
  start_date       VARCHAR(32)  NOT NULL DEFAULT '' COMMENT '计划开始 yyyy-MM-dd',
  end_date         VARCHAR(32)  NOT NULL DEFAULT '' COMMENT '计划结束 yyyy-MM-dd',
  created_at       VARCHAR(32)  NULL,
  updated_at       VARCHAR(32)  NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_ticket_no (ticket_no),
  KEY idx_st_customer (customer_no),
  KEY idx_st_status (status),
  KEY idx_st_type (ticket_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='售后与投诉工单';

-- -----------------------------
-- 销售渠道（对应 /channels API）
-- -----------------------------
DROP TABLE IF EXISTS channels;
CREATE TABLE channels (
  id               BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '内部主键',
  channel_code     VARCHAR(64)  NOT NULL COMMENT '渠道编码',
  channel_name     VARCHAR(128) NOT NULL COMMENT '渠道名称',
  channel_type     VARCHAR(64)  NOT NULL DEFAULT '' COMMENT '代理人/银行/网销/经纪等',
  manager          VARCHAR(64)  NOT NULL DEFAULT '' COMMENT '负责人',
  commission_rule  VARCHAR(256) NOT NULL DEFAULT '' COMMENT '佣金或手续费说明',
  contact_phone    VARCHAR(32)  NOT NULL DEFAULT '' COMMENT '联系电话',
  status           VARCHAR(32)  NOT NULL DEFAULT '合作中' COMMENT '合作中/暂停/终止',
  remark           VARCHAR(512) NOT NULL DEFAULT '' COMMENT '备注',
  created_at       VARCHAR(32)  NULL,
  updated_at       VARCHAR(32)  NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_channel_code (channel_code),
  KEY idx_channel_type (channel_type),
  KEY idx_channel_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='销售渠道';

-- -----------------------------
-- 财务管理（对应 /premium_flows、/commission_settlements API）
-- -----------------------------
DROP TABLE IF EXISTS premium_flows;
CREATE TABLE premium_flows (
  id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '内部主键',
  flow_no     VARCHAR(64)  NOT NULL COMMENT '流水号 PF…',
  flow_type   VARCHAR(32)  NOT NULL COMMENT '首期/续期/理赔赔款等',
  policy_no   VARCHAR(64)  NOT NULL COMMENT '保单号',
  amount      VARCHAR(32)  NOT NULL DEFAULT '0' COMMENT '金额（元）',
  pay_method  VARCHAR(64)  NOT NULL DEFAULT '' COMMENT '支付方式',
  status      VARCHAR(32)  NOT NULL DEFAULT '' COMMENT '状态',
  remark      VARCHAR(512) NOT NULL DEFAULT '' COMMENT '备注',
  created_at  VARCHAR(32)  NULL,
  updated_at  VARCHAR(32)  NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_flow_no (flow_no),
  KEY idx_pf_policy (policy_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='保费收付流水';

DROP TABLE IF EXISTS commission_settlements;
CREATE TABLE commission_settlements (
  id                 BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '内部主键',
  settlement_no      VARCHAR(64)  NOT NULL COMMENT '结算单号 CM…',
  channel_name       VARCHAR(128) NOT NULL COMMENT '渠道/代理人',
  channel_code       VARCHAR(64)  NOT NULL DEFAULT '' COMMENT '渠道编码（可选）',
  period             VARCHAR(32)  NOT NULL DEFAULT '' COMMENT '结算周期如 2026-02',
  commission_amount  VARCHAR(32)  NOT NULL DEFAULT '0' COMMENT '佣金（元）',
  reconcile_status   VARCHAR(32)  NOT NULL DEFAULT '' COMMENT '对账状态',
  remark             VARCHAR(512) NOT NULL DEFAULT '' COMMENT '备注',
  created_at         VARCHAR(32)  NULL,
  updated_at         VARCHAR(32)  NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_settlement_no (settlement_no),
  KEY idx_cs_channel (channel_name),
  KEY idx_cs_period (period)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='佣金结算';

-- -----------------------------
-- 再保管理（对应 /reinsurance_contracts、/reinsurance_bills API）
-- -----------------------------
DROP TABLE IF EXISTS reinsurance_contracts;
CREATE TABLE reinsurance_contracts (
  id             BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '内部主键',
  contract_no    VARCHAR(64)  NOT NULL COMMENT '合同编号 RC…',
  contract_type  VARCHAR(64)  NOT NULL DEFAULT '' COMMENT '再保类型 比例/溢额等',
  cedent         VARCHAR(128) NOT NULL DEFAULT '' COMMENT '原保险人/分出方',
  reinsurer      VARCHAR(128) NOT NULL DEFAULT '' COMMENT '再保险人',
  status         VARCHAR(32)  NOT NULL DEFAULT '生效' COMMENT '合同状态',
  remark         VARCHAR(512) NOT NULL DEFAULT '' COMMENT '备注',
  created_at     VARCHAR(32)  NULL,
  updated_at     VARCHAR(32)  NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_contract_no (contract_no),
  KEY idx_rc_reinsurer (reinsurer)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='再保合同';

DROP TABLE IF EXISTS reinsurance_bills;
CREATE TABLE reinsurance_bills (
  id                 BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '内部主键',
  bill_no            VARCHAR(64)  NOT NULL COMMENT '账单号 RB…',
  biz_kind           VARCHAR(32)  NOT NULL DEFAULT '' COMMENT '分出/分入',
  period             VARCHAR(32)  NOT NULL DEFAULT '' COMMENT '账期 如 2026Q1',
  premium_wan        VARCHAR(32)  NOT NULL DEFAULT '0' COMMENT '保费（万元）',
  claim_recover_wan  VARCHAR(32)  NOT NULL DEFAULT '0' COMMENT '摊回赔款（万元）',
  remark             VARCHAR(512) NOT NULL DEFAULT '' COMMENT '备注',
  created_at         VARCHAR(32)  NULL,
  updated_at         VARCHAR(32)  NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_bill_no (bill_no),
  KEY idx_rb_period (period),
  KEY idx_rb_kind (biz_kind)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='再保账单';

-- -----------------------------
-- 代理人/团队管理（对应 /agent_teams、/agents、/agent_performance_summary API）
-- -----------------------------
DROP TABLE IF EXISTS agent_performances;
CREATE TABLE agent_performances (
  id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '内部主键',
  perf_no       VARCHAR(64)  NOT NULL COMMENT '业绩编号 AP…',
  owner_type    VARCHAR(16)  NOT NULL DEFAULT 'team' COMMENT 'owner 类型 team | agent',
  owner_no      VARCHAR(64)  NOT NULL COMMENT 'owner 编号（team_no / agent_no）',
  period        VARCHAR(32)  NOT NULL DEFAULT '' COMMENT '账期，如 2026Q1',
  premium_wan   VARCHAR(32)  NOT NULL DEFAULT '0' COMMENT '保费（万元）',
  kpi_rate      VARCHAR(32)  NOT NULL DEFAULT '0%' COMMENT 'KPI 达成率',
  created_at    VARCHAR(32)  NULL,
  updated_at    VARCHAR(32)  NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_perf_no (perf_no),
  KEY idx_perf_period (period),
  KEY idx_perf_owner (owner_type, owner_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='代理人/团队业绩';

DROP TABLE IF EXISTS agents;
CREATE TABLE agents (
  id         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '内部主键',
  agent_no   VARCHAR(64)  NOT NULL COMMENT '代理人编号 AG…',
  name       VARCHAR(64)  NOT NULL COMMENT '代理人姓名',
  id_no      VARCHAR(64)  NOT NULL DEFAULT '' COMMENT '证件号',
  phone      VARCHAR(32)  NOT NULL DEFAULT '' COMMENT '手机号',
  team_no    VARCHAR(64)  NOT NULL DEFAULT '' COMMENT '所属团队 team_no',
  title      VARCHAR(64)  NOT NULL DEFAULT '' COMMENT '职级/头衔',
  status     VARCHAR(32)  NOT NULL DEFAULT '在职' COMMENT '状态',
  created_at VARCHAR(32)  NULL,
  updated_at VARCHAR(32)  NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_agent_no (agent_no),
  KEY idx_agents_team (team_no),
  KEY idx_agents_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='代理人主数据';

DROP TABLE IF EXISTS agent_teams;
CREATE TABLE agent_teams (
  id             BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '内部主键',
  team_no        VARCHAR(64)  NOT NULL COMMENT '团队编号 TM…',
  name           VARCHAR(64)  NOT NULL COMMENT '团队名称',
  title          VARCHAR(64)  NOT NULL DEFAULT '' COMMENT '职级/职务',
  parent_team_no VARCHAR(64)  NOT NULL DEFAULT '' COMMENT '上级团队编号（可空）',
  created_at     VARCHAR(32)  NULL,
  updated_at     VARCHAR(32)  NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_team_no (team_no),
  KEY idx_team_parent (parent_team_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='代理人团队组织架构';

-- -----------------------------
-- 系统管理（对应 /system_users、/system_params、/system_logs API）
-- -----------------------------
DROP TABLE IF EXISTS system_logs;
CREATE TABLE system_logs (
  id         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '内部主键',
  log_type   VARCHAR(32)  NOT NULL DEFAULT 'info' COMMENT '日志类型',
  actor      VARCHAR(64)  NOT NULL DEFAULT '' COMMENT '操作者',
  action     VARCHAR(256) NOT NULL DEFAULT '' COMMENT '操作内容',
  created_at VARCHAR(32)  NULL,
  PRIMARY KEY (id),
  KEY idx_logs_type (log_type),
  KEY idx_logs_actor (actor)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统日志';

DROP TABLE IF EXISTS system_params;
CREATE TABLE system_params (
  id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '内部主键',
  param_key   VARCHAR(64)  NOT NULL COMMENT '参数键',
  param_value VARCHAR(512) NOT NULL DEFAULT '' COMMENT '参数值',
  description VARCHAR(512) NOT NULL DEFAULT '' COMMENT '描述',
  created_at  VARCHAR(32)  NULL,
  updated_at  VARCHAR(32)  NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_param_key (param_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统参数';

DROP TABLE IF EXISTS system_users;
CREATE TABLE system_users (
  id         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '内部主键',
  username   VARCHAR(64)  NOT NULL COMMENT '用户名',
  role       VARCHAR(64)  NOT NULL DEFAULT '' COMMENT '角色',
  status     VARCHAR(32)  NOT NULL DEFAULT '启用' COMMENT '启用/停用',
  created_at VARCHAR(32)  NULL,
  updated_at VARCHAR(32)  NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_username (username),
  KEY idx_users_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统用户';

-- -----------------------------
-- 黑名单（对应 /blacklist API）
-- -----------------------------
DROP TABLE IF EXISTS blacklist;
CREATE TABLE blacklist (
  id       BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  name     VARCHAR(64)  NOT NULL COMMENT '姓名',
  id_no    VARCHAR(64)  NOT NULL COMMENT '证件号',
  reason   VARCHAR(512) NOT NULL DEFAULT '' COMMENT '列入原因',
  status   VARCHAR(32)  NOT NULL DEFAULT '启用' COMMENT '启用/停用',
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='黑名单';

-- -----------------------------
-- 风险预警（对应 /risk_alerts API）
-- 说明：desc 为 MySQL 保留相关词，列名用 alert_desc，接口仍返回 desc
-- -----------------------------
DROP TABLE IF EXISTS risk_alerts;
CREATE TABLE risk_alerts (
  id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  code        VARCHAR(64)  NOT NULL COMMENT '预警编号',
  alert_type  VARCHAR(64)  NOT NULL COMMENT '预警类型，对应 JSON 字段 type',
  alert_desc  VARCHAR(512) NOT NULL COMMENT '预警说明，对应 JSON 字段 desc',
  risk_level  VARCHAR(32)  NOT NULL DEFAULT '高' COMMENT '风险等级，对应 JSON 字段 level',
  PRIMARY KEY (id),
  KEY idx_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='风险预警';

-- -----------------------------
-- 可执行风控规则（预设 + 自然语言解析入库，对应 GET /rules 与引擎加载）
-- 初次导入后若表为空，启动 FastAPI 时会自动写入 9 条预设（见 api.store_mysql.seed_preset_rules_if_empty）
-- -----------------------------
DROP TABLE IF EXISTS risk_rules;
CREATE TABLE risk_rules (
  id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  rule_id         VARCHAR(128) NOT NULL COMMENT '业务规则 ID，唯一',
  description_cn  VARCHAR(512) NOT NULL DEFAULT '' COMMENT '中文描述',
  action          VARCHAR(64)  NOT NULL DEFAULT 'manual_review' COMMENT '命中动作枚举值',
  source          VARCHAR(32)  NOT NULL DEFAULT 'preset' COMMENT 'preset | nl_parsed',
  ir_json         LONGTEXT     NOT NULL COMMENT 'RiskRuleIR JSON',
  priority        INT          NOT NULL DEFAULT 100 COMMENT '越小越优先',
  enabled         TINYINT      NOT NULL DEFAULT 1 COMMENT '1 启用 0 停用',
  PRIMARY KEY (id),
  UNIQUE KEY uk_rule_id (rule_id),
  KEY idx_priority (priority)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='风控规则库';

-- -----------------------------
-- 可选：示例数据（与内存版默认数据接近）
-- -----------------------------
INSERT INTO customers (customer_no, name, id_type, id_no, phone, occupation, level, status, photo, gender, address, remark, created_at)
VALUES
  ('C20260001', '张伟', '身份证', '110101199001012026', '13810012026', '专业技术人员', '普通', '在保', '', '男', '北京市朝阳区望京街道', '线上投保活跃客户', '2026-03-06'),
  ('C20260002', '王晓芳', '身份证', '310101199202142026', '13910022026', '专业技术人员', '普通', '在保', '', '女', '上海市浦东新区花木街道', '理赔响应速度较快', '2026-03-06'),
  ('C20260003', '李娜', '身份证', '440106198806222026', '13710032026', '专业技术人员', '普通', '在保', '', '女', '广东省广州市天河区', '家庭保障需求明确', '2026-03-06'),
  ('C20260004', '欧阳子涵', '身份证', '320102198511302026', '13610042026', '专业技术人员', '普通', '在保', '', '男', '江苏省南京市玄武区', '医疗险续保客户', '2026-03-06'),
  ('C20260005', '陈杰', '身份证', '330103199307172026', '13510052026', '办事人员', '普通', '在保', '', '男', '浙江省杭州市西湖区', '银行渠道转化', '2026-03-06'),
  ('C20260006', '杨雨桐', '身份证', '420102199411082026', '18810062026', '生产运输工人', '普通', '在保', '', '女', '湖北省武汉市江岸区', '车险投保客户', '2026-03-06'),
  ('C20260007', '赵磊', '身份证', '510104198912052026', '18710072026', '办事人员', '高风险', '在保', '', '男', '四川省成都市锦江区', '反欺诈规则命中观察', '2026-03-06'),
  ('C20260008', '上官婉儿', '身份证', '120105199605262026', '18610082026', '专业技术人员', '普通', '在保', '', '女', '天津市河北区', '家财险和意外险组合', '2026-03-06'),
  ('C20260009', '周强', '身份证', '350203198710192026', '18510092026', '专业技术人员', '普通', '在保', '', '男', '福建省厦门市思明区', '线上直销客户', '2026-03-06'),
  ('C20260010', '吴思涵', '身份证', '210102199808032026', '15610102026', '商业服务业人员', '普通', '在保', '', '女', '辽宁省沈阳市和平区', '活动期投保客户', '2026-03-06'),
  ('C20260011', '徐鹏', '身份证', '230103198403112026', '15810112026', '国家机关负责人', '普通', '在保', '', '男', '黑龙江省哈尔滨市南岗区', '长期寿险客户', '2026-03-06'),
  ('C20260012', '孙嘉怡', '身份证', '370102199512242026', '15910122026', '商业服务业人员', '普通', '在保', '', '女', '山东省济南市历下区', '商户经营相关保障', '2026-03-06'),
  ('C20260013', '司马明哲', '身份证', '430103198909092026', '15110132026', '生产运输工人', '普通', '在保', '', '男', '湖南省长沙市天心区', '工伤意外保障需求', '2026-03-06'),
  ('C20260014', '朱琳', '身份证', '610104199001152026', '15210142026', '商业服务业人员', '普通', '在保', '', '女', '陕西省西安市莲湖区', '代理人自保单', '2026-03-06'),
  ('C20260015', '高梓轩', '身份证', '500103198706282026', '15310152026', '专业技术人员', '普通', '在保', '', '男', '重庆市渝中区', '高端医疗产品需求', '2026-03-06'),
  ('C20260016', '林雪', '身份证', '460106199309212026', '15510162026', '专业技术人员', '普通', '在保', '', '女', '海南省海口市龙华区', '门诊医疗责任关注', '2026-03-06'),
  ('C20260017', '何军', '身份证', '341102198802072026', '15710172026', '办事人员', '普通', '在保', '', '男', '安徽省合肥市蜀山区', '条款阅读完整', '2026-03-06'),
  ('C20260018', '郭芷若', '身份证', '530103199404132026', '18210182026', '专业技术人员', '普通', '在保', '', '女', '云南省昆明市盘龙区', '偏好线上服务', '2026-03-06'),
  ('C20260019', '马超', '身份证', '640104198609162026', '18310192026', '商业服务业人员', '普通', '在保', '', '男', '宁夏银川市兴庆区', '渠道佣金核对样本', '2026-03-06'),
  ('C20260020', '罗丹', '身份证', '520103199701272026', '18410202026', '商业服务业人员', '普通', '在保', '', '女', '贵州省贵阳市云岩区', '跨地区出险场景', '2026-03-06'),
  ('C20260021', '梁晨曦', '身份证', '450103198312302026', '18910212026', '生产运输工人', '高风险', '在保', '', '男', '广西南宁市青秀区', '车险理赔高频观察', '2026-03-06'),
  ('C20260022', '宋佳', '身份证', '620102199111052026', '18110222026', '办事人员', '普通', '在保', '', '女', '甘肃省兰州市城关区', '社区团体投保样本', '2026-03-06'),
  ('C20260023', '诸葛云飞', '身份证', '360102198805142026', '18010232026', '专业技术人员', '普通', '在保', '', '男', '江西省南昌市东湖区', '教育行业客户', '2026-03-06'),
  ('C20260024', '谢雨薇', '身份证', '130102199210252026', '17710242026', '办事人员', '普通', '在保', '', '女', '河北省石家庄市长安区', '财务报销型客户', '2026-03-06'),
  ('C20260025', '韩天宇', '身份证', '140106198401082026', '17610252026', '办事人员', '普通', '在保', '', '男', '山西省太原市小店区', '团险配置咨询', '2026-03-06'),
  ('C20260026', '唐蕾', '身份证', '220104199507192026', '17510262026', '农林牧渔水利业', '普通', '在保', '', '女', '吉林省长春市朝阳区', '农业经营风险保障', '2026-03-06'),
  ('C20260027', '努尔夏提·阿不都热依木', '身份证', '650102199103062026', '16610272026', '生产运输工人', '普通', '在保', '', '男', '新疆乌鲁木齐市天山区', '新疆区域样本客户', '2026-03-06'),
  ('C20260028', '迪丽娜尔·买买提', '身份证', '650104199608112026', '19910282026', '生产运输工人', '普通', '在保', '', '女', '新疆乌鲁木齐市新市区', '渠道补录客户', '2026-03-06'),
  ('C20260029', '阿依古丽·吐尔逊', '身份证', '652901199303292026', '19810292026', '商业服务业人员', '普通', '在保', '', '女', '新疆阿克苏市', '旅游意外险客户', '2026-03-06'),
  ('C20260030', '麦尔丹·伊明', '身份证', '653101199012182026', '16710302026', '生产运输工人', '高风险', '在保', '', '男', '新疆喀什市', '高风险客户监控样本', '2026-03-06');

INSERT INTO policies (policy_no, customer_no, product_name, premium, coverage_amount, start_date, end_date, status)
VALUES
  ('P20260001', 'C20260001', '家庭财产综合险A', '1680', '500000', '2026-01-01', '2026-12-31', '生效中'),
  ('P20260002', 'C20260002', '城市家庭责任险B', '620', '1000000', '2026-01-15', '2027-01-14', '生效中'),
  ('P20260003', 'C20260003', '健康无忧百万医疗险', '365', '6000000', '2026-02-01', '2027-01-31', '生效中'),
  ('P20260004', 'C20260004', '安行无忧综合意外险', '299', '1000000', '2026-02-08', '2027-02-07', '生效中'),
  ('P20260005', 'C20260005', '安心一生终身寿险', '12000', '1000000', '2026-02-18', '2046-02-17', '生效中'),
  ('P20260006', 'C20260006', '金盈年金养老计划', '8000', '3000000', '2026-03-01', '2046-02-28', '生效中'),
  ('P20260007', 'C20260007', '悦享高端门急诊医疗险', '2500', '2000000', '2026-03-05', '2027-03-04', '生效中'),
  ('P20260008', 'C20260008', '车辆综合保险标准版', '3600', '2000000', '2026-03-12', '2027-03-11', '生效中'),
  ('P20260009', 'C20260009', '商户营业中断保障险', '4200', '1500000', '2026-03-18', '2027-03-17', '生效中'),
  ('P20260010', 'C20260010', '雇主责任保障计划', '6800', '3000000', '2026-03-21', '2027-03-20', '生效中'),
  ('P20260011', 'C20260011', '跨境差旅意外保障', '499', '800000', '2026-03-25', '2027-03-24', '生效中'),
  ('P20260012', 'C20260012', '电商退货运费保障险', '99', '50000', '2026-03-28', '2027-03-27', '生效中');

INSERT INTO products (product_no, product_name, category, description, premium_guide, coverage_cap, status, created_at)
VALUES
  ('PRD20260001', '家庭财产综合险A', '财产险', '家庭财产综合保障，含火灾、盗抢与水渍损失。', '1680 元/年起', '500000', '在售', '2026-03-06'),
  ('PRD20260002', '城市家庭责任险B', '责任险', '覆盖第三者人身与财产损失责任。', '520 元/年起', '1000000', '在售', '2026-03-06'),
  ('PRD20260003', '健康无忧百万医疗险', '健康险', '住院医疗与特药保障，含重疾住院扩展。', '365 元/年起', '6000000', '在售', '2026-03-06'),
  ('PRD20260004', '安行无忧综合意外险', '意外险', '交通意外、意外医疗与住院津贴。', '299 元/年起', '1000000', '在售', '2026-03-06'),
  ('PRD20260005', '安心一生终身寿险', '寿险', '终身身故保障与保单现金价值。', '12000 元/年起', '1000000', '在售', '2026-03-06'),
  ('PRD20260006', '金盈年金养老计划', '养老险', '年金给付与养老金领取安排。', '8000 元/年起', '3000000', '在售', '2026-03-06'),
  ('PRD20260007', '悦享高端门急诊医疗险', '健康险', '门急诊与体检增值服务。', '2500 元/年起', '2000000', '在售', '2026-03-06'),
  ('PRD20260008', '车辆综合保险标准版', '车险', '车损、第三者与驾乘人员责任。', '3600 元/年起', '2000000', '在售', '2026-03-06'),
  ('PRD20260009', '商户营业中断保障险', '财产险', '保障商户营业中断及固定成本损失。', '4200 元/年起', '1500000', '在售', '2026-03-06'),
  ('PRD20260010', '雇主责任保障计划', '责任险', '覆盖雇员工伤与雇主责任赔偿。', '6800 元/年起', '3000000', '在售', '2026-03-06'),
  ('PRD20260011', '跨境差旅意外保障', '意外险', '差旅意外、行李延误与医疗救援。', '199 元/次起', '800000', '在售', '2026-03-06'),
  ('PRD20260012', '电商退货运费保障险', '财产险', '覆盖电商订单退货运费损失。', '99 元/年起', '50000', '在售', '2026-03-06');

INSERT INTO underwriting_cases (
  case_no, customer_no, applicant_name, id_no, product_name, premium, coverage_amount,
  channel, status, risk_score, decision_note, policy_no, created_at, updated_at
) VALUES
(
  'UW2026030601',
  'C20260001',
  '张伟',
  '110101199001012026',
  '健康无忧百万医疗险',
  '365',
  '6000000',
  '线上直销',
  '自动通过',
  '低',
  '规则引擎未命中高风险，自动核保通过。',
  NULL,
  '2026-03-06',
  '2026-03-06'
),
(
  'UW2026030602',
  'C20260005',
  '陈杰',
  '330103199307172026',
  '安心一生终身寿险',
  '12000',
  '1000000',
  '银行渠道',
  '待人工核保',
  '中',
  '高额寿险需人工复核与体检材料。',
  NULL,
  '2026-03-06',
  '2026-03-06'
),
(
  'UW2026030603',
  'C20260007',
  '赵磊',
  '510104198912052026',
  '悦享高端门急诊医疗险',
  '2500',
  '2000000',
  '个人代理',
  '人工通过',
  '中',
  '补充既往病史说明后人工通过。',
  'P20260007',
  '2026-03-07',
  '2026-03-08'
),
(
  'UW2026030604',
  'C20260008',
  '上官婉儿',
  '120105199605262026',
  '车辆综合保险标准版',
  '3600',
  '2000000',
  '网销平台',
  '自动通过',
  '低',
  '车险标准核保规则通过。',
  'P20260008',
  '2026-03-07',
  '2026-03-07'
),
(
  'UW2026030605',
  'C20260015',
  '高梓轩',
  '500103198706282026',
  '健康无忧百万医疗险',
  '420',
  '6000000',
  '线下网点',
  '待补件',
  '中',
  '需补充门急诊病历与体检报告。',
  NULL,
  '2026-03-08',
  '2026-03-08'
),
(
  'UW2026030606',
  'C20260021',
  '梁晨曦',
  '450103198312302026',
  '商户营业中断保障险',
  '4500',
  '1500000',
  '个人代理',
  '拒保',
  '高',
  '近12个月出险频率偏高，暂不承保。',
  NULL,
  '2026-03-08',
  '2026-03-09'
),
(
  'UW2026030607',
  'C20260009',
  '周强',
  '350203198710192026',
  '安行无忧综合意外险',
  '299',
  '1000000',
  '线上直销',
  '自动通过',
  '低',
  '职业类别与告知一致，自动通过。',
  'P20260004',
  '2026-03-09',
  '2026-03-09'
),
(
  'UW2026030608',
  'C20260011',
  '徐鹏',
  '230103198403112026',
  '金盈年金养老计划',
  '8000',
  '3000000',
  '银保渠道',
  '人工通过',
  '中',
  '财务审查与反洗钱筛查通过。',
  'P20260006',
  '2026-03-10',
  '2026-03-10'
),
(
  'UW2026030609',
  'C20260003',
  '李娜',
  '440106198806222026',
  '城市家庭责任险B',
  '620',
  '1000000',
  '银行渠道',
  '核保中',
  '低',
  '等待第三方风控评分回传。',
  NULL,
  '2026-03-10',
  '2026-03-11'
),
(
  'UW2026030610',
  'C20260006',
  '杨雨桐',
  '420102199411082026',
  '车辆综合保险标准版',
  '3600',
  '2000000',
  '线下网点',
  '待受理',
  '中',
  '新单录入，待规则引擎初筛。',
  NULL,
  '2026-03-11',
  '2026-03-11'
);

INSERT INTO claims (
  claim_no, policy_no, customer_no, claimant_name, product_name, claim_type, incident_reason,
  incident_date, report_date, claim_amount, approved_amount, status, decision_note, created_at, updated_at
) VALUES
(
  'CLM20260306001',
  'P20260001',
  'C20260001',
  '张某某',
  '家庭财产综合险A',
  '财产',
  '室内水管爆裂致地板受损',
  '2026-02-10',
  '2026-03-01',
  '50000',
  '45000',
  '已结案',
  '定损后同意赔付 45000 元，免赔额已扣除。',
  '2026-03-06',
  '2026-03-06'
),
(
  'CLM20260306002',
  'P20260008',
  'C20260008',
  '上官婉儿',
  '车辆综合保险标准版',
  '车损',
  '倒车碰撞导致后保险杠受损',
  '2026-03-05',
  '2026-03-05',
  '12000',
  '9800',
  '已结案',
  '按车损险责任赔付。',
  '2026-03-07',
  '2026-03-08'
),
(
  'CLM20260306003',
  'P20260007',
  'C20260007',
  '赵磊',
  '悦享高端门急诊医疗险',
  '医疗',
  '急性阑尾炎住院治疗',
  '2026-03-09',
  '2026-03-10',
  '18000',
  '16500',
  '处理中',
  '票据审核中。',
  '2026-03-10',
  '2026-03-11'
),
(
  'CLM20260306004',
  'P20260009',
  'C20260009',
  '周强',
  '商户营业中断保障险',
  '营业中断',
  '仓库电路故障停业 3 天',
  '2026-03-02',
  '2026-03-04',
  '76000',
  '',
  '待调查',
  '待第三方公估报告。',
  '2026-03-09',
  '2026-03-10'
),
(
  'CLM20260306005',
  'P20260003',
  'C20260003',
  '李娜',
  '健康无忧百万医疗险',
  '医疗',
  '住院手术医疗费用报销',
  '2026-03-01',
  '2026-03-03',
  '26000',
  '24000',
  '已结案',
  '符合医保外责任，核赔通过。',
  '2026-03-07',
  '2026-03-09'
),
(
  'CLM20260306006',
  'P20260002',
  'C20260002',
  '王晓芳',
  '城市家庭责任险B',
  '责任',
  '第三者人身轻微伤害协商赔偿',
  '2026-03-08',
  '2026-03-09',
  '15000',
  '',
  '待受理',
  '资料已收件，待分案。',
  '2026-03-11',
  '2026-03-11'
),
(
  'CLM20260306007',
  'P20260005',
  'C20260005',
  '陈杰',
  '安心一生终身寿险',
  '身故',
  '受益人申请身故保险金',
  '2026-02-28',
  '2026-03-12',
  '1000000',
  '',
  '处理中',
  '受益关系与材料核验中。',
  '2026-03-12',
  '2026-03-13'
),
(
  'CLM20260306008',
  'P20260011',
  'C20260011',
  '徐鹏',
  '跨境差旅意外保障',
  '意外',
  '境外旅行期间意外骨折',
  '2026-03-14',
  '2026-03-15',
  '88000',
  '72000',
  '已结案',
  '按条款境外医疗与意外责任赔付。',
  '2026-03-15',
  '2026-03-16'
);

INSERT INTO service_tickets (
  ticket_no, ticket_type, customer_no, contact_name, phone, policy_no, category, subject, content,
  status, handler, resolution_note, start_date, end_date, created_at, updated_at
) VALUES
(
  'CS2026030601',
  '投诉',
  'C20260001',
  '张伟',
  '13810012026',
  'P20260001',
  '理赔时效',
  '理赔审核周期偏长',
  '客户反馈提交材料后超过承诺时效仍未结案，要求跟进。',
  '处理中',
  '客服-王某',
  '',
  '2026-03-06',
  '2026-03-10',
  '2026-03-06',
  '2026-03-06'
),
(
  'CS2026030602',
  '投诉',
  'C20260002',
  '王晓芳',
  '13910022026',
  'P20260002',
  '销售误导',
  '产品责任与宣传不符',
  '称投保时业务员口头承诺与条款不一致。',
  '已结案',
  '合规-李某',
  '已与客户沟通并出具说明函，客户无异议。',
  '2026-03-04',
  '2026-03-06',
  '2026-03-05',
  '2026-03-06'
),
(
  'CS2026030603',
  '售后',
  'C20260008',
  '上官婉儿',
  '18610082026',
  'P20260008',
  '保单变更',
  '车辆信息变更申请',
  '客户更换车辆使用性质，申请批改。',
  '处理中',
  '客服-赵宁',
  '',
  '2026-03-07',
  '2026-03-14',
  '2026-03-07',
  '2026-03-07'
),
(
  'CS2026030604',
  '售后',
  'C20260015',
  '高梓轩',
  '15310152026',
  'P20260005',
  '续保咨询',
  '高端医疗续保条件咨询',
  '咨询是否可免等待期续保。',
  '已结案',
  '客服-孙悦',
  '已说明续保规则并发送书面指引。',
  '2026-03-08',
  '2026-03-09',
  '2026-03-08',
  '2026-03-08'
),
(
  'CS2026030605',
  '投诉',
  'C20260010',
  '吴思涵',
  '15610102026',
  'P20260010',
  '核保时效',
  '加急核保未在承诺时间内反馈',
  '团体雇主责任险加急案件，客户催促出具核保结论。',
  '待受理',
  '',
  '',
  '2026-03-09',
  '2026-03-12',
  '2026-03-09',
  '2026-03-09'
),
(
  'CS2026030606',
  '售后',
  'C20260012',
  '孙嘉怡',
  '15910122026',
  'P20260012',
  '退保咨询',
  '电商退货运费险退保',
  '店铺关闭申请退保与未使用保费退还。',
  '处理中',
  '客服-周倩',
  '',
  '2026-03-09',
  '2026-03-16',
  '2026-03-09',
  '2026-03-10'
),
(
  'CS2026030607',
  '投诉',
  'C20260004',
  '欧阳子涵',
  '13610042026',
  'P20260004',
  '增值服务',
  '体检预约失败',
  '高端医疗附赠体检多次预约失败，要求协调。',
  '已结案',
  '运营-郑某',
  '已协调合作机构完成预约并致歉。',
  '2026-03-08',
  '2026-03-09',
  '2026-03-08',
  '2026-03-09'
),
(
  'CS2026030608',
  '售后',
  'C20260007',
  '赵磊',
  '18710072026',
  'P20260007',
  '发票与凭证',
  '电子发票抬头错误',
  '企业投保人申请重开增值税发票。',
  '处理中',
  '财务-刘某',
  '',
  '2026-03-11',
  '2026-03-18',
  '2026-03-11',
  '2026-03-11'
);

INSERT INTO channels (
  channel_code, channel_name, channel_type, manager, commission_rule, contact_phone, status, remark, created_at, updated_at
) VALUES
(
  'AG001',
  '个人代理渠道',
  '代理人',
  '张主管',
  '首年 25%，续期 5%',
  '021-68551001',
  '合作中',
  '',
  '2026-03-01',
  '2026-03-06'
),
(
  'BN001',
  'XX 银行保险部',
  '银行',
  '李经理',
  '首年 15%，续期 3%',
  '010-65232002',
  '合作中',
  '',
  '2026-03-01',
  '2026-03-06'
),
(
  'BR001',
  'XX 保险经纪公司',
  '经纪',
  '刘总监',
  '首年 12%，续期 2.5%',
  '021-58881200',
  '合作中',
  '经代协议 2026 版',
  '2026-02-15',
  '2026-03-06'
),
(
  'WS001',
  '网销直营旗舰店',
  '网销',
  '陈运营',
  '按 CPA 结算，单笔 80–200 元',
  '400-800-9001',
  '合作中',
  '信息流投放渠道',
  '2026-01-10',
  '2026-03-06'
),
(
  'TM001',
  '电话销售中心',
  '电销',
  '马经理',
  '坐席绩效制，首单阶梯奖励',
  '0755-26600001',
  '合作中',
  '',
  '2025-12-01',
  '2026-03-07'
),
(
  'YL001',
  '异业合作-XX出行',
  '异业',
  '何商务',
  '联合会员权益兑换，按激活量结算',
  '010-90001122',
  '暂停',
  '季度复盘后恢复',
  '2025-11-20',
  '2026-03-08'
);

INSERT INTO premium_flows (
  flow_no, flow_type, policy_no, amount, pay_method, status, remark, created_at, updated_at
) VALUES
(
  'PF20260306001',
  '首期',
  'P20260006',
  '8000',
  '银行代扣',
  '成功',
  '年金险首期',
  '2026-03-06',
  '2026-03-06'
),
(
  'PF20260306002',
  '理赔赔款',
  'P20260001',
  '45000',
  '转账',
  '已支付',
  '财产险结案赔款',
  '2026-03-06',
  '2026-03-06'
),
(
  'PF20260306003',
  '首期',
  'P20260001',
  '1680',
  '银行代扣',
  '成功',
  '家财险首期',
  '2026-03-07',
  '2026-03-07'
),
(
  'PF20260306004',
  '续期',
  'P20260006',
  '8000',
  '银行代扣',
  '成功',
  '年金险续期',
  '2026-03-07',
  '2026-03-07'
),
(
  'PF20260306005',
  '理赔赔款',
  'P20260008',
  '9800',
  '转账',
  '已支付',
  '车险理赔',
  '2026-03-09',
  '2026-03-09'
),
(
  'PF20260306006',
  '首期',
  'P20260003',
  '365',
  '线上支付',
  '成功',
  '百万医疗首期',
  '2026-03-08',
  '2026-03-08'
),
(
  'PF20260306007',
  '首期',
  'P20260005',
  '12000',
  '转账',
  '成功',
  '终身寿险首期',
  '2026-03-09',
  '2026-03-09'
),
(
  'PF20260306008',
  '退费',
  'P20260012',
  '99',
  '原路退回',
  '成功',
  '退货运费险退保',
  '2026-03-10',
  '2026-03-10'
),
(
  'PF20260306009',
  '理赔赔款',
  'P20260003',
  '24000',
  '转账',
  '处理中',
  '医疗险批量打款队列中',
  '2026-03-11',
  '2026-03-11'
),
(
  'PF20260306010',
  '首期',
  'P20260010',
  '6800',
  '对公转账',
  '成功',
  '雇主责任险首期',
  '2026-03-12',
  '2026-03-12'
);

INSERT INTO commission_settlements (
  settlement_no, channel_name, channel_code, period, commission_amount, reconcile_status, remark, created_at, updated_at
) VALUES
(
  'CM20260306001',
  '个人代理渠道',
  'AG001',
  '2026-02',
  '12000',
  '已对账',
  '',
  '2026-03-06',
  '2026-03-06'
),
(
  'CM20260306002',
  'XX 银行保险部',
  'BN001',
  '2026-02',
  '38000',
  '对账中',
  '',
  '2026-03-06',
  '2026-03-06'
),
(
  'CM20260306003',
  '网销直营旗舰店',
  'WS001',
  '2026-03',
  '8600',
  '待对账',
  '线上引流成本结算',
  '2026-03-10',
  '2026-03-10'
),
(
  'CM20260306004',
  'XX 保险经纪公司',
  'BR001',
  '2026-02',
  '22400',
  '已对账',
  '经代渠道月度结算',
  '2026-03-08',
  '2026-03-08'
),
(
  'CM20260306005',
  '电话销售中心',
  'TM001',
  '2026-03',
  '5600',
  '对账中',
  '电销坐席绩效提成',
  '2026-03-11',
  '2026-03-11'
),
(
  'CM20260306006',
  '个人代理渠道',
  'AG001',
  '2026-03',
  '15800',
  '待对账',
  '跨月补录单并入',
  '2026-03-12',
  '2026-03-12'
);

INSERT INTO reinsurance_contracts (
  contract_no, contract_type, cedent, reinsurer, status, remark, created_at, updated_at
) VALUES
(
  'RC20260306001',
  '比例再保',
  '本公司',
  'XX 再保险公司',
  '生效',
  '',
  '2026-03-06',
  '2026-03-06'
),
(
  'RC20260306002',
  '溢额再保',
  '本公司',
  'YY 再保险公司',
  '生效',
  '',
  '2026-03-06',
  '2026-03-06'
);

INSERT INTO reinsurance_bills (
  bill_no, biz_kind, period, premium_wan, claim_recover_wan, remark, created_at, updated_at
) VALUES
(
  'RB20260306001',
  '分出',
  '2026Q1',
  '260',
  '30',
  '',
  '2026-03-06',
  '2026-03-06'
),
(
  'RB20260306002',
  '分入',
  '2026Q1',
  '120',
  '8',
  '',
  '2026-03-06',
  '2026-03-06'
);

INSERT INTO agent_teams (team_no, name, title, parent_team_no, created_at, updated_at)
VALUES
  ('TM20260306001', '王总监团队', '营销总监', '', '2026-03-06', '2026-03-06'),
  ('TM20260306002', '李经理团队', '营业部经理', 'TM20260306001', '2026-03-06', '2026-03-06'),
  ('TM20260306003', '张主管', '营业部主管', 'TM20260306002', '2026-03-06', '2026-03-06');

INSERT INTO agents (agent_no, name, id_no, phone, team_no, title, status, created_at, updated_at)
VALUES
  ('AG20260306001', '王总监', '110101198401012026', '13800012026', 'TM20260306001', '营销总监', '在职', '2026-03-06', '2026-03-06'),
  ('AG20260306002', '李经理', '310101198503022026', '13900022026', 'TM20260306002', '营业部经理', '在职', '2026-03-06', '2026-03-06'),
  ('AG20260306003', '张主管', '440106198612032026', '13700032026', 'TM20260306003', '营业部主管', '在职', '2026-03-06', '2026-03-06');

INSERT INTO agent_performances (perf_no, owner_type, owner_no, period, premium_wan, kpi_rate, created_at, updated_at)
VALUES
  ('AP20260306001', 'team', 'TM20260306001', '2026Q1', '580', '112%', '2026-03-06', '2026-03-06'),
  ('AP20260306002', 'team', 'TM20260306002', '2026Q1', '320', '96%', '2026-03-06', '2026-03-06'),
  ('AP20260306003', 'agent', 'AG20260306003', '2026Q1', '120', '88%', '2026-03-06', '2026-03-06');

INSERT INTO system_users (username, role, status, created_at, updated_at)
VALUES
  ('admin', '系统管理员', '启用', '2026-03-06', '2026-03-06'),
  ('uw_user', '承保岗', '启用', '2026-03-06', '2026-03-06');

INSERT INTO system_params (param_key, param_value, description, created_at, updated_at)
VALUES
  ('nl_prompt_variant', 'json_only', '自然语言解析 prompt 版本默认值', '2026-03-06', '2026-03-06'),
  ('risk_default_level', '高', '风险等级默认值', '2026-03-06', '2026-03-06');

INSERT INTO system_logs (log_type, actor, action, created_at)
VALUES
  ('login', 'admin', '登录系统', '2026-03-06');

INSERT INTO blacklist (name, id_no, reason, status) VALUES
  ('梁晨曦', '450103198312302026', '近12个月疑似异常高频理赔（车险观察）', '启用'),
  ('麦尔丹·伊明', '653101199012182026', '同设备多账号短期密集投保', '启用'),
  ('赵磊', '510104198912052026', '客户等级为高风险，反欺诈规则命中复核', '启用'),
  ('王晓芳', '310101199202142026', '同址高额保单聚集，疑似集中投保', '启用'),
  ('迪丽娜尔·买买提', '650104199608112026', '同手机号关联多证件，需来源复核', '启用');

INSERT INTO risk_alerts (code, alert_type, alert_desc, risk_level) VALUES
  ('AL2026030601', '集中投保', '短期内同一地址多笔高保额投保', '高'),
  ('AL2026030602', '异常理赔', '同一客户近30天理赔金额显著高于历史均值', '高'),
  ('AL2026030603', '证件异常', '批量证件末位规律一致，需复核来源真实性', '中'),
  ('AL2026030604', '夜间理赔', '凌晨时段多笔高额理赔集中发生', '高'),
  ('AL2026030605', '渠道异动', '单渠道7日内新单量环比异常攀升', '中'),
  ('AL2026030606', '收款风险', '同一收款账户短期承接多客户赔款入账', '高'),
  ('AL2026030607', '代理人风险', '单代理人名下短期出险率显著高于渠道均值', '中'),
  ('AL2026030608', '退保重投', '续保窗口外同一客户频繁退保重投', '中'),
  ('AL2026030609', '设备伪冒', '同一设备指纹24小时内关联多证件投保', '高'),
  ('AL2026030610', '关系网络', '与欺诈名单客户在地址或收款卡上多项重合', '高'),
  ('AL2026030611', '保单早赔', '起保72小时内高额理赔案件集中出现', '高'),
  ('AL2026030612', '团单异常', '团单被保人数与工商登记雇员数偏离过大', '低');
