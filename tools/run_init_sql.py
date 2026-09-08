"""
无需安装「mysql 命令行」在 PATH 里：用当前项目的 Python + PyMySQL 执行建库脚本。

在后端目录执行：
  .\\.venv\\Scripts\\python.exe tools\\run_init_sql.py

需要：后端\\.env 中已配置 DATABASE_URL；MySQL 服务已启动；
账号需有权限执行 CREATE DATABASE / DROP TABLE / INSERT（通常 root 或已授权用户）。
"""

from __future__ import annotations

import sys
from pathlib import Path

# 后端根目录（含 api/、sql/、.env）
BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

import pymysql
from dotenv import load_dotenv
from pymysql.constants import CLIENT
from sqlalchemy.engine import make_url

load_dotenv(BACKEND_ROOT / ".env")

SQL_FILE = BACKEND_ROOT / "sql" / "init_insurance_db.sql"


def main() -> None:
    from os import getenv

    raw = (getenv("DATABASE_URL") or "").strip()
    if not raw:
        print("错误：后端目录 .env 中未设置 DATABASE_URL。")
        sys.exit(1)

    u = make_url(raw)
    host = u.host or "127.0.0.1"
    port = int(u.port) if u.port else 3306
    user = u.username
    password = u.password or ""

    if not user:
        print("错误：连接串中缺少用户名。")
        sys.exit(1)

    text = SQL_FILE.read_text(encoding="utf-8")

    print(f"连接 {host}:{port} 用户 {user} …")
    print(f"执行 {SQL_FILE.name} …")

    conn = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        charset="utf8mb4",
        client_flag=CLIENT.MULTI_STATEMENTS,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(text)
        conn.commit()
        print("完成：库表与示例数据已执行（若权限不足请看下方报错）。")
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        main()
    except pymysql.err.OperationalError as e:
        print("数据库连接/权限失败：", e)
        print("若提示 Access denied，请检查 .env 里账号密码；若不能用 CREATE DATABASE，请用 root 执行 sql/init_insurance_db.sql，或为该用户授权。")
        sys.exit(1)
    except Exception as e:
        print("执行失败：", e)
        sys.exit(1)
