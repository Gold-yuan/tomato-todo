"""
Todo任务数据仓库

处理Todo任务相关的数据库操作
"""
from typing import List, Dict
from sqlalchemy.orm import Session
from models import TodoTask


class TodoRepository:
    """Todo任务数据仓库"""

    def __init__(self, session: Session):
        """
        初始化仓库

        Args:
            session: SQLAlchemy会话
        """
        self.session = session

    def create(self, content: str) -> TodoTask:
        """
        创建新任务

        Args:
            content: 任务内容

        Returns:
            创建的任务对象
        """
        task = TodoTask(content=content)
        self.session.add(task)
        return task

    def get_by_id(self, task_id: int) -> TodoTask:
        """
        根据ID获取任务

        Args:
            task_id: 任务ID

        Returns:
            任务对象

        Raises:
            NoResultFound: 任务不存在
        """
        return self.session.query(TodoTask).filter(
            TodoTask.id == task_id
        ).one()

    def update(self, task_id: int, content: str) -> TodoTask:
        """
        更新任务内容

        Args:
            task_id: 任务ID
            content: 新的任务内容

        Returns:
            更新后的任务对象

        Raises:
            NoResultFound: 任务不存在
        """
        task = self.get_by_id(task_id)
        task.content = content
        # updated_at会自动更新
        return task

    def delete(self, task_id: int) -> bool:
        """
        删除任务

        Args:
            task_id: 任务ID

        Returns:
            成功返回True

        Raises:
            NoResultFound: 任务不存在
        """
        task = self.get_by_id(task_id)
        self.session.delete(task)
        return True

    def toggle_completed(self, task_id: int) -> TodoTask:
        """
        切换任务完成状态

        Args:
            task_id: 任务ID

        Returns:
            更新后的任务对象

        Raises:
            NoResultFound: 任务不存在
        """
        task = self.get_by_id(task_id)
        from datetime import datetime

        if task.is_completed:
            # 已完成 -> 未完成
            task.is_completed = False
            task.completed_at = None
        else:
            # 未完成 -> 已完成
            task.is_completed = True
            task.completed_at = datetime.now()

        # updated_at会自动更新，任务自动移动
        return task

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
        # 构建查询
        query = self.session.query(TodoTask)

        if completed_only:
            query = query.filter(TodoTask.is_completed == True)

        # 获取总数
        total = query.count()

        # 排序：未完成在前，已完成在后；同类别内按updated_at DESC排序
        query = query.order_by(
            TodoTask.is_completed.desc(),
            TodoTask.updated_at.desc()
        )

        # 分页
        offset = (page - 1) * per_page
        tasks = query.limit(per_page).offset(offset).all()

        # 计算总页数
        total_pages = (total + per_page - 1) // per_page

        return {
            'tasks': tasks,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
        }

    def search_tasks(self, keyword: str) -> List[TodoTask]:
        """
        搜索任务

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的任务列表
        """
        return self.session.query(TodoTask).filter(
            TodoTask.content.contains(keyword)
        ).order_by(
            TodoTask.is_completed.desc(),
            TodoTask.updated_at.desc()
        ).all()
