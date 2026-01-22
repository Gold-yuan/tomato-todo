"""
Pytest配置和共享fixtures

提供测试所需的数据库会话和测试客户端
"""
import pytest
import tempfile
import os
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / 'src'
import sys
sys.path.insert(0, str(src_path))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from database.connection import SessionLocal


@pytest.fixture(scope="function")
def db_session():
    """
    创建内存数据库测试会话

    每个测试函数使用独立的数据库，测试结束后自动清理
    """
    # 创建内存数据库
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )

    # 创建所有表
    Base.metadata.create_all(bind=engine)

    # 创建会话
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    session = TestingSessionLocal()

    yield session

    # 清理：关闭会话
    session.close()


@pytest.fixture(scope="function")
def test_client(db_session):
    """
    创建测试客户端

    提供预配置的数据库会话给测试使用
    """
    # 可以在这里创建测试客户端实例
    # 暂时直接返回session
    return db_session


# pytest-qt 配置

def pytest_configure(config):
    """
    Pytest配置钩子

    配置pytest-qt相关设置
    """
    config.addinivalue_line(
        "markers",
        "qt: mark test as requiring Qt"
    )


@pytest.fixture
def qtbot_strong(qtbot):
    """
    强类型的qtbot fixture

    确保Qt widget在测试结束后被正确清理
    """
    widgets = []

    def add_widget(widget):
        widgets.append(widget)
        qtbot.addWidget(widget)

    yield add_widget

    # 清理所有widgets
    for widget in widgets:
        widget.close()
