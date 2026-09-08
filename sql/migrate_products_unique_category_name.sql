-- 可选：在库中已无「同险种 + 同产品名称」重复行后，增加唯一约束，从数据库层防止重复建档。
-- 执行前请先删除或合并重复产品，例如：
--   SELECT product_name, category, COUNT(*) c FROM products GROUP BY product_name, category HAVING c > 1;
--   手工保留一条后删除多余行，再执行下方语句。

-- ALTER TABLE products
--   ADD UNIQUE KEY uk_products_category_name (category, product_name);
