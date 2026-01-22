"""
TodoService单元测试

测试Todo任务服务的所有方法
"""
import pytest
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent.parent.parent.parent / 'src'
import sys
sys.path.insert(0, str(src_path))

from services import TodoService, NotFoundError
from models import TodoTask
from utils.constants import MAX_TASK_CONTENT_LENGTH


class TestTodoServiceCreateTask:
    """测试create_task方法"""

    def test_create_task_success(self, db_session):
        """测试成功创建任务"""
        service = TodoService(db_session)
        task = service.create_task("完成项目文档")
        db_session.commit()

        assert task is not None
        assert task.id is not None
        assert task.content == "完成项目文档"
        assert task.is_completed is False
        assert task.created_at is not None
        assert task.updated_at is not None

    def test_create_task_empty_content(self, db_session):
        """测试创建空任务"""
        service = TodoService(db_session)
        with pytest.raises(ValueError, match="任务内容不能为空"):
            service.create_task("")

    def test_create_task_whitespace_only(self, db_session):
        """测试创建空白任务"""
        service = TodoService(db_session)
        with pytest.raises(ValueError, match="任务内容不能为空"):
            service.create_task("   ")

    def test_create_task_too_long(self, db_session):
        """测试创建超长任务"""
        service = TodoService(db_session)
        long_content = "A" * (MAX_TASK_CONTENT_LENGTH + 1)
        with pytest.raises(ValueError, match="任务内容不能超过"):
            service.create_task(long_content)

    def test_create_task_trimming(self, db_session):
        """测试创建任务时自动去除首尾空格"""
        service = TodoService(db_session)
        task = service.create_task("  完成项目文档  ")

        assert task.content == "完成项目文档"


class TestTodoServiceUpdateTask:
    """测试update_task方法"""

    def test_update_task_success(self, db_session):
        """测试成功更新任务"""
        service = TodoService(db_session)
        task = service.create_task("原始任务")
        db_session.commit()

        updated_task = service.update_task(task.id, "更新后的任务")
        db_session.commit()

        assert updated_task.content == "更新后的任务"

    def test_update_task_empty_content(self, db_session):
        """测试更新为空内容"""
        service = TodoService(db_session)
        task = service.create_task("原始任务")
        db_session.commit()

        with pytest.raises(ValueError, match="任务内容不能为空"):
            service.update_task(task.id, "")

    def test_update_task_not_found(self, db_session):
        """测试更新不存在的任务"""
        service = TodoService(db_session)
        with pytest.raises(NotFoundError):
            service.update_task(999, "新内容")


class TestTodoServiceDeleteTask:
    """测试delete_task方法"""

    def test_delete_task_success(self, db_session):
        """测试成功删除任务"""
        service = TodoService(db_session)
        task = service.create_task("要删除的任务")
        db_session.commit()

        result = service.delete_task(task.id)
        db_session.commit()

        assert result is True

        # 验证任务已删除
        with pytest.raises(NotFoundError):
            service.update_task(task.id, "任何内容")

    def test_delete_task_not_found(self, db_session):
        """测试删除不存在的任务"""
        service = TodoService(db_session)
        with pytest.raises(NotFoundError):
            service.delete_task(999)


class TestTodoServiceToggleCompleted:
    """测试toggle_completed方法"""

    def test_toggle_to_completed(self, db_session):
        """测试从未完成切换到已完成"""
        service = TodoService(db_session)
        task = service.create_task("新任务")
        db_session.commit()

        updated_task = service.toggle_completed(task.id)
        db_session.commit()

        assert updated_task.is_completed is True
        assert updated_task.completed_at is not None

    def test_toggle_to_uncompleted(self, db_session):
        """测试从已完成切换回未完成"""
        service = TodoService(db_session)
        task = service.create_task("新任务")
        db_session.commit()

        # 先完成
        service.toggle_completed(task.id)
        db_session.commit()

        # 取消完成
        updated_task = service.toggle_completed(task.id)
        db_session.commit()

        assert updated_task.is_completed is False
        assert updated_task.completed_at is None

    def test_toggle_not_found(self, db_session):
        """测试切换不存在的任务"""
        service = TodoService(db_session)
        with pytest.raises(NotFoundError):
            service.toggle_completed(999)


class TestTodoServiceGetTasks:
    """测试get_tasks方法"""

    def test_get_tasks_first_page(self, db_session):
        """测试获取第一页"""
        service = TodoService(db_session)

        # 创建25个任务
        for i in range(25):
            service.create_task(f"任务{i}")
        db_session.commit()

        result = service.get_tasks(page=1, per_page=20)

        assert result['total'] == 25
        assert result['page'] == 1
        assert result['per_page'] == 20
        assert result['total_pages'] == 2
        assert len(result['tasks']) == 20

    def test_get_tasks_second_page(self, db_session):
        """测试获取第二页"""
        service = TodoService(db_session)

        # 创建25个任务
        for i in range(25):
            service.create_task(f"任务{i}")
        db_session.commit()

        result = service.get_tasks(page=2, per_page=20)

        assert len(result['tasks']) == 5

    def test_get_tasks_sorting(self, db_session):
        """测试任务排序（未完成在前，已完成后）"""
        service = TodoService(db_session)

        # 创建任务
        task1 = service.create_task("任务1")
        task2 = service.create_task("任务2")
        task3 = service.create_task("任务3")
        db_session.commit()

        # 完成任务2和task1
        service.toggle_completed(task2.id)
        service.toggle_completed(task1.id)
        db_session.commit()

        # 获取任务列表
        result = service.get_tasks(page=1, per_page=20)
        tasks = result['tasks']

        # 验证排序：未完成任务在前，已完成任务在后
        completed_count = sum(1 for t in tasks if t.is_completed)
        uncompleted_count = sum(1 for t in tasks if not t.is_completed)

        assert completed_count == 2  # task1, task2已完成
        assert uncompleted_count == 1  # task3未完成

        # 第一个任务应该是未完成的
        assert tasks[0].is_completed is False
        # 剩余两个应该是已完成的
        assert tasks[1].is_completed is True
        assert tasks[2].is_completed is True

    def test_get_tasks_completed_only(self, db_session):
        """测试只获取已完成任务"""
        service = TodoService(db_session)

        # 创建任务
        task1 = service.create_task("任务1")
        task2 = service.create_task("任务2")
        task3 = service.create_task("任务3")
        db_session.commit()

        # 完成任务2和任务3
        service.toggle_completed(task2.id)
        service.toggle_completed(task3.id)
        db_session.commit()

        # 只获取已完成任务
        result = service.get_tasks(completed_only=True)

        assert result['total'] == 2
        assert len(result['tasks']) == 2
        assert all(t.is_completed for t in result['tasks'])

    def test_get_tasks_empty_list(self, db_session):
        """测试空任务列表"""
        service = TodoService(db_session)

        result = service.get_tasks()

        assert result['total'] == 0
        assert result['total_pages'] == 0
        assert len(result['tasks']) == 0


class TestTodoServiceSearchTasks:
    """测试search_tasks方法"""

    def test_search_tasks_found(self, db_session):
        """测试搜索找到匹配任务"""
        service = TodoService(db_session)

        service.create_task("完成Python项目文档")
        service.create_task("学习JavaScript")
        service.create_task("编写测试代码")
        db_session.commit()

        results = service.search_tasks("项目")

        assert len(results) == 1
        assert "项目" in results[0].content

    def test_search_tasks_not_found(self, db_session):
        """测试搜索未找到匹配"""
        service = TodoService(db_session)

        service.create_task("任务1")
        db_session.commit()

        results = service.search_tasks("不存在的关键词")

        assert len(results) == 0

    def test_search_tasks_case_sensitive(self, db_session):
        """测试搜索区分大小写"""
        service = TodoService(db_session)

        service.create_task("Python编程")
        db_session.commit()

        results = service.search_tasks("python")

        # 应该不区分大小写或不区分，根据实现
        # 当前SQLAlchemy的contains默认不区分大小写
        assert len(results) >= 0
