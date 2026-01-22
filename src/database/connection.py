"""
数据库连接管理

管理SQLite数据库连接、Session工厂和数据库初始化
"""
import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from utils.constants import APP_DIR, DB_PATH


# 确保应用目录存在
os.makedirs(APP_DIR, exist_ok=True)


def get_engine():
    """
    创建并返回数据库引擎

    Returns:
        Engine: SQLAlchemy引擎实例

    配置说明:
        - 使用StaticPool: SQLite单线程设计
        - check_same_thread=False: 允许多线程访问（Qt UI需要）
        - 外键约束启用: 确保数据完整性
    """
    engine = create_engine(
        f'sqlite:///{DB_PATH}',
        connect_args={
            'check_same_thread': False,  # 允许多线程访问
        },
        poolclass=StaticPool,  # SQLite使用静态连接池
        echo=False  # 生产环境关闭SQL日志
    )

    # 启用外键约束（SQLite需要）
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


# 创建全局引擎实例
engine = get_engine()

# 创建Session工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_session() -> Session:
    """
    获取一个新的数据库会话

    Returns:
        Session: SQLAlchemy会话实例

    使用示例:
        >>> session = get_session()
        >>> try:
        ...     # 执行数据库操作
        ...     session.commit()
        ... finally:
        ...     session.close()
    """
    session = SessionLocal()
    return session


def init_database():
    """
    初始化数据库，创建所有表

    应在应用启动时调用
    """
    from database import Base

    # 创建所有表
    Base.metadata.create_all(bind=engine)

    # 预置默认配置
    _seed_default_preferences()


def _seed_default_preferences():
    """
    预置默认用户偏好配置

    如果配置不存在则创建，存在则跳过
    """
    from models import UserPreferences
    from services import PreferencesService
    import json

    session = get_session()
    try:
        prefs_service = PreferencesService(session)

        # 检查是否已有配置
        existing = prefs_service.get_all_preferences()
        if not existing:
            # 预置默认配置
            default_prefs = {
                'work_duration': 1500,  # 25分钟
                'break_duration': 300,  # 5分钟
                'always_on_top': False,
                'auto_start_break': True,
                'theme': 'light'
            }
            prefs_service.set_preferences(default_prefs)
            session.commit()

    finally:
        session.close()


def get_db_path() -> str:
    """
    获取数据库文件路径

    Returns:
        str: 数据库文件的绝对路径
    """
    return DB_PATH


def get_app_dir() -> str:
    """
    获取应用数据目录

    Returns:
        str: 应用数据目录的绝对路径
    """
    return APP_DIR
