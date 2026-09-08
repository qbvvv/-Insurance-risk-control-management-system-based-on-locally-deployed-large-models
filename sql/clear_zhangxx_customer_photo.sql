-- 清空示例客户「张某某」的客户编号 C20260001 在库中的照片 URL（字段 photo）。
-- 适用：曾在「客户列表」编辑并上传过照片、需要恢复为无照片记录时执行。
-- 用法（按你的连接信息替换）：mysql -u... -p 库名 < clear_zhangxx_customer_photo.sql

UPDATE customers
SET photo = ''
WHERE customer_no = 'C20260001';
