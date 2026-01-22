"""
数据库模块

导出SQLAlchemy基类和引擎实例
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """所有ORM模型的基类"""
    pass


__all__ = ['Base']
