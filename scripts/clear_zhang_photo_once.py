"""One-off: clear photo URL for customer C20260001 (张某某). Reads DATABASE_URL from .env."""
from pathlib import Path
from urllib.parse import unquote, urlparse

import pymysql

env = Path(__file__).resolve().parent.parent / ".env"
url = ""
for line in env.read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line.startswith("DATABASE_URL=") and not line.startswith("#"):
        url = line.split("=", 1)[1].strip().strip('"')
        break
if not url:
    raise SystemExit("DATABASE_URL missing in .env")

u = urlparse(url.replace("mysql+pymysql", "mysql"))
db = (u.path or "/")[1:].split("?")[0]
conn = pymysql.connect(
    host=u.hostname or "127.0.0.1",
    port=u.port or 3306,
    user=unquote(u.username or ""),
    password=unquote(u.password or ""),
    database=db,
    charset="utf8mb4",
)
try:
    with conn.cursor() as cur:
        cur.execute("UPDATE customers SET photo = %s WHERE customer_no = %s", ("", "C20260001"))
        conn.commit()
        cur.execute(
            "SELECT customer_no, name, photo FROM customers WHERE customer_no = %s",
            ("C20260001",),
        )
        print(cur.fetchone())
finally:
    conn.close()
