"""
数据库连接：仅当环境变量 DATABASE_URL 非空时创建引擎。

连接串示例：
  mysql+pymysql://root:密码@127.0.0.1:3306/insurance_db?charset=utf8mb4
"""

import os
from typing import Generator, Optional

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()

DATABASE_URL: str = (os.getenv("DATABASE_URL") or "").strip()

_engine: Optional[Engine] = None
_session_factory: Optional[sessionmaker] = None


def get_engine() -> Optional[Engine]:
    global _engine, _session_factory
    if not DATABASE_URL:
        return None
    if _engine is None:
        _engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        _session_factory = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    return _engine


def db_enabled() -> bool:
    return bool(DATABASE_URL)


def get_session_factory() -> sessionmaker:
    get_engine()
    assert _session_factory is not None
    return _session_factory


def init_db() -> None:
    """启动时根据 ORM 建表（表已存在则不会删掉数据）。"""
    if not db_enabled():
        return
    from api.orm_models import Base

    eng = get_engine()
    assert eng is not None
    Base.metadata.create_all(bind=eng)


def get_db_session() -> Generator[Session, None, None]:
    """FastAPI Depends 用：yield 会话后提交/回滚并关闭。"""
    db = get_session_factory()()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
