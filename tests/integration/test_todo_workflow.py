"""
TodoList工作流集成测试

测试Todo任务的完整生命周期和业务流程
"""
import pytest
import time
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent.parent / 'src'
import sys
sys.path.insert(0, str(src_path))

from services import TodoService, NotFoundError


class TestTodoWorkflow:
    """测试Todo任务完整工作流"""

    @pytest.fixture(autouse=True)
    def setup_service(self, db_session):
        """使用pytest fixture创建独立的数据库会话"""
        self.session = db_session
        self.service = TodoService(db_session)
        yield
        # 测试结束后自动清理（由fixture处理）

    def test_complete_lifecycle(self):
        """测试完整生命周期：创建→完成→取消完成→删除"""
        # 1. 创建任务
        task = self.service.create_task("完成项目文档")
        self.session.commit()

        assert task.id is not None
        assert task.content == "完成项目文档"
        assert task.is_completed is False
        assert task.completed_at is None

        # 2. 完成任务
        updated_task = self.service.toggle_completed(task.id)
        self.session.commit()

        assert updated_task.is_completed is True
        assert updated_task.completed_at is not None

        # 3. 取消完成
        uncompleted_task = self.service.toggle_completed(task.id)
        self.session.commit()

        assert uncompleted_task.is_completed is False
        assert uncompleted_task.completed_at is None

        # 4. 修改内容
        edited_task = self.service.update_task(task.id, "更新后的项目文档")
        self.session.commit()

        assert edited_task.content == "更新后的项目文档"

        # 5. 删除任务
        result = self.service.delete_task(task.id)
        self.session.commit()

        assert result is True

        # 验证任务已删除（尝试更新会失败）
        with pytest.raises(NotFoundError):
            self.service.update_task(task.id, "任何内容")

    def test_batch_operations(self):
        """测试批量操作：创建多个任务→部分完成→分页获取"""
        # 创建25个任务
        task_ids = []
        for i in range(25):
            task = self.service.create_task(f"任务{i+1}")
            task_ids.append(task.id)
        self.session.commit()

        # 完成前10个任务
        for task_id in task_ids[:10]:
            self.service.toggle_completed(task_id)
        self.session.commit()

        # 获取第一页（20个）
        result = self.service.get_tasks(page=1, per_page=20)

        assert result['total'] == 25
        assert result['page'] == 1
        assert result['per_page'] == 20
        assert result['total_pages'] == 2
        assert len(result['tasks']) == 20

        # 验证排序：未完成在前，已完成在后
        tasks = result['tasks']
        uncompleted_count = sum(1 for t in tasks if not t.is_completed)
        completed_count = sum(1 for t in tasks if t.is_completed)

        # 第一页应该有所有15个未完成任务 + 5个已完成任务
        assert uncompleted_count == 15
        assert completed_count == 5

        # 获取第二页（5个）
        result2 = self.service.get_tasks(page=2, per_page=20)
        assert len(result2['tasks']) == 5
        # 第二页应该全是已完成任务
        assert all(t.is_completed for t in result2['tasks'])

    def test_search_and_edit_workflow(self):
        """测试搜索→编辑→再次搜索的工作流"""
        # 创建多个任务
        self.service.create_task("学习Python")
        self.service.create_task("学习JavaScript")
        self.service.create_task("完成Python项目")
        self.service.create_task("完成JavaScript项目")
        self.session.commit()

        # 搜索包含"Python"的任务
        results = self.service.search_tasks("Python")
        assert len(results) == 2

        # 修改第一个搜索结果
        task_to_edit = results[0]
        edited_task = self.service.update_task(
            task_to_edit.id,
            "深入学习Python"
        )
        self.session.commit()

        assert edited_task.content == "深入学习Python"

        # 再次搜索，验证修改生效
        new_results = self.service.search_tasks("Python")
        assert any("深入学习" in t.content for t in new_results)

    def test_task_priority_by_update_time(self):
        """测试任务按更新时间排序的工作流"""
        # 创建3个任务
        task1 = self.service.create_task("任务1")
        task2 = self.service.create_task("任务2")
        task3 = self.service.create_task("任务3")
        self.session.commit()

        # 完成任务1（让它有最新的updated_at）
        time.sleep(0.01)  # 确保时间戳不同
        self.service.toggle_completed(task1.id)
        self.session.commit()

        # 获取已完成任务
        result = self.service.get_tasks(completed_only=True)
        completed_tasks = result['tasks']

        # 任务1应该排在已完成任务的第一位
        assert len(completed_tasks) == 1
        assert completed_tasks[0].id == task1.id

    def test_concurrent_modifications(self):
        """测试连续修改同一任务"""
        # 创建任务
        task = self.service.create_task("原始任务")
        self.session.commit()

        # 第一次修改
        task = self.service.update_task(task.id, "修改1")
        self.session.commit()
        assert task.content == "修改1"

        # 第二次修改
        task = self.service.update_task(task.id, "修改2")
        self.session.commit()
        assert task.content == "修改2"

        # 第三次修改
        task = self.service.update_task(task.id, "修改3")
        self.session.commit()
        assert task.content == "修改3"

    def test_completed_only_pagination(self):
        """测试已完成任务的分页"""
        # 创建10个任务并完成其中8个
        for i in range(10):
            self.service.create_task(f"任务{i+1}")
        self.session.commit()

        # 完成前8个
        all_tasks = self.service.get_tasks(per_page=20)['tasks']
        for i in range(8):
            self.service.toggle_completed(all_tasks[i].id)
        self.session.commit()

        # 获取已完成任务，分页为5
        page1 = self.service.get_tasks(page=1, per_page=5, completed_only=True)
        assert len(page1['tasks']) == 5
        assert page1['total'] == 8
        assert page1['total_pages'] == 2
        assert all(t.is_completed for t in page1['tasks'])

        page2 = self.service.get_tasks(page=2, per_page=5, completed_only=True)
        assert len(page2['tasks']) == 3
        assert all(t.is_completed for t in page2['tasks'])

    def test_empty_state_workflow(self):
        """测试空状态下的各种操作"""
        # 空列表
        result = self.service.get_tasks()
        assert result['total'] == 0
        assert len(result['tasks']) == 0

        # 搜索无结果
        search_results = self.service.search_tasks("不存在的任务")
        assert len(search_results) == 0

        # 尝试删除不存在的任务
        with pytest.raises(NotFoundError):
            self.service.delete_task(999)

        # 尝试修改不存在的任务
        with pytest.raises(NotFoundError):
            self.service.update_task(999, "新内容")

        # 尝试完成不存在的任务
        with pytest.raises(NotFoundError):
            self.service.toggle_completed(999)

    def test_task_validation_workflow(self):
        """测试任务验证流程"""
        # 1. 空内容验证
        with pytest.raises(ValueError, match="任务内容不能为空"):
            self.service.create_task("")

        with pytest.raises(ValueError, match="任务内容不能为空"):
            self.service.create_task("   ")

        # 2. 超长内容验证
        from utils.constants import MAX_TASK_CONTENT_LENGTH
        long_content = "A" * (MAX_TASK_CONTENT_LENGTH + 1)
        with pytest.raises(ValueError, match="任务内容不能超过"):
            self.service.create_task(long_content)

        # 3. 创建有效任务
        valid_task = self.service.create_task("  有效任务  ")
        self.session.commit()
        assert valid_task.content == "有效任务"  # 去除首尾空格

        # 4. 更新时的验证
        with pytest.raises(ValueError, match="任务内容不能为空"):
            self.service.update_task(valid_task.id, "")
