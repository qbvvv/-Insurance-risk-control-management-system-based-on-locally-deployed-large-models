-- 已有库升级：为客户表增加头像、性别、地址、备注（若列已存在会报错，可逐条执行并忽略错误）
USE insurance_db;

ALTER TABLE customers ADD COLUMN photo   VARCHAR(512) NOT NULL DEFAULT '' COMMENT '头像/照片URL' AFTER status;
ALTER TABLE customers ADD COLUMN gender  VARCHAR(16)  NOT NULL DEFAULT '未知' COMMENT '性别' AFTER photo;
ALTER TABLE customers ADD COLUMN address VARCHAR(255) NOT NULL DEFAULT '' COMMENT '联系地址' AFTER gender;
ALTER TABLE customers ADD COLUMN remark  VARCHAR(512) NOT NULL DEFAULT '' COMMENT '备注' AFTER address;
