"""
数据库和单实例管理的单元测试

测试数据库连接、会话管理和单实例锁
"""
import pytest
import os
import tempfile
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent.parent / 'src'
import sys
sys.path.insert(0, str(src_path))

from database.connection import get_session, get_engine, get_app_dir, get_db_path, init_database
from utils.single_instance import SingleInstanceManager
from utils.constants import LOCK_FILE_PATH


class TestDatabaseConnection:
    """数据库连接测试"""

    def test_get_engine(self):
        """测试引擎创建"""
        engine = get_engine()
        assert engine is not None
        assert engine.url.drivername == "sqlite"

    def test_get_session(self):
        """测试会话创建"""
        session = get_session()
        assert session is not None
        session.close()

    def test_get_app_dir(self):
        """测试应用目录路径"""
        app_dir = get_app_dir()
        assert app_dir is not None
        assert 'TomatoTodo' in app_dir
        assert os.path.isabs(app_dir)

    def test_get_db_path(self):
        """测试数据库文件路径"""
        db_path = get_db_path()
        assert db_path is not None
        assert db_path.endswith('tomato_todo.db')
        assert os.path.isabs(db_path)

    def test_init_database(self, db_session):
        """测试数据库初始化"""
        # 使用测试fixture提供的内存数据库
        # 验证表是否创建
        from database import Base
        from models import PomodoroTimer, TodoTask, UserPreferences, PomodoroStats

        # 创建表
        Base.metadata.create_all(bind=db_session.get_bind())

        # 检查表是否存在（通过查询记录数，应该为0但不报错）
        assert db_session.query(PomodoroTimer).count() == 0
        assert db_session.query(TodoTask).count() == 0
        assert db_session.query(UserPreferences).count() == 0
        assert db_session.query(PomodoroStats).count() == 0


class TestSingleInstance:
    """单实例管理测试"""

    def test_single_instance_manager_creation(self):
        """测试单实例管理器创建"""
        # 使用临时文件作为锁文件
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = os.path.join(tmpdir, 'test.lock')
            manager = SingleInstanceManager(lock_path)
            assert manager is not None
            assert manager.lock_path == lock_path

    def test_try_lock_success(self):
        """测试成功获取锁"""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = os.path.join(tmpdir, 'test.lock')
            manager = SingleInstanceManager(lock_path)
            assert manager.try_lock() is True
            manager.unlock()

    def test_try_lock_failure(self):
        """测试锁冲突"""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = os.path.join(tmpdir, 'test.lock')

            # 第一个管理器获取锁
            manager1 = SingleInstanceManager(lock_path)
            assert manager1.try_lock() is True

            # 第二个管理器尝试获取锁应该失败
            manager2 = SingleInstanceManager(lock_path)
            assert manager2.try_lock() is False

            # 清理
            manager1.unlock()

    def test_context_manager(self):
        """测试上下文管理器"""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = os.path.join(tmpdir, 'test.lock')
            with SingleInstanceManager(lock_path) as manager:
                assert manager is not None
                # 在上下文中锁应该被持有
                assert manager.lock_file.isLocked()
            # 退出上下文后锁应该被释放
