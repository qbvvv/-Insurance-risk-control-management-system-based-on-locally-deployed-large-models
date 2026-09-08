-- 工单表增加「计划处理起止日期」（与前端日期选择器对应）
ALTER TABLE service_tickets
  ADD COLUMN start_date VARCHAR(32) NOT NULL DEFAULT '' COMMENT '计划开始 yyyy-MM-dd' AFTER resolution_note,
  ADD COLUMN end_date   VARCHAR(32) NOT NULL DEFAULT '' COMMENT '计划结束 yyyy-MM-dd' AFTER start_date;
