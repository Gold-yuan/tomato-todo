"""
Todo任务服务

封装Todo任务的业务逻辑
"""
from typing import Dict, List
from sqlalchemy.orm import Session
from database.repositories import TodoRepository
from models import TodoTask
from utils.constants import MAX_TASK_CONTENT_LENGTH


class TodoService:
    """Todo任务服务"""

    def __init__(self, session: Session):
        """
        初始化服务

        Args:
            session: SQLAlchemy会话
        """
        self.session = session
        self.repository = TodoRepository(session)

    def create_task(self, content: str) -> TodoTask:
        """
        创建新任务

        Args:
            content: 任务内容

        Returns:
            TodoTask对象

        Raises:
            ValueError: 如果内容无效
        """
        # 验证内容
        if not content or not content.strip():
            raise ValueError("任务内容不能为空")

        if len(content) > MAX_TASK_CONTENT_LENGTH:
            raise ValueError(f"任务内容不能超过{MAX_TASK_CONTENT_LENGTH}个字符")

        return self.repository.create(content.strip())

    def update_task(self, task_id: int, content: str) -> TodoTask:
        """
        更新任务内容

        Args:
            task_id: 任务ID
            content: 新的任务内容

        Returns:
            TodoTask对象

        Raises:
            ValueError: 如果内容无效
            NotFoundError: 如果任务不存在
        """
        # 验证内容
        if not content or not content.strip():
            raise ValueError("任务内容不能为空")

        if len(content) > MAX_TASK_CONTENT_LENGTH:
            raise ValueError(f"任务内容不能超过{MAX_TASK_CONTENT_LENGTH}个字符")

        try:
            return self.repository.update(task_id, content.strip())
        except Exception:
            # 将SQLAlchemy的NoResultFound转换为业务异常
            raise NotFoundError(f"任务 {task_id} 不存在")

    def delete_task(self, task_id: int) -> bool:
        """
        删除任务

        Args:
            task_id: 任务ID

        Returns:
            成功返回True

        Raises:
            NotFoundError: 如果任务不存在
        """
        try:
            return self.repository.delete(task_id)
        except Exception:
            raise NotFoundError(f"任务 {task_id} 不存在")

    def toggle_completed(self, task_id: int) -> TodoTask:
        """
        切换任务完成状态

        Args:
            task_id: 任务ID

        Returns:
            TodoTask对象

        Raises:
            NotFoundError: 如果任务不存在
        """
        try:
            return self.repository.toggle_completed(task_id)
        except Exception:
            raise NotFoundError(f"任务 {task_id} 不存在")

    def get_tasks(
        self,
        page: int = 1,
        per_page: int = 20,
        completed_only: bool = False
    ) -> Dict:
        """
        分页获取任务列表

        Args:
            page: 页码（从1开始）
            per_page: 每页数量
            completed_only: 是否只获取已完成任务

        Returns:
            包含任务列表和分页信息的字典
        """
        return self.repository.get_tasks(page, per_page, completed_only)

    def search_tasks(self, keyword: str) -> List[TodoTask]:
        """
        搜索任务

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的任务列表
        """
        return self.repository.search_tasks(keyword)


class NotFoundError(Exception):
    """资源未找到异常"""
    pass
