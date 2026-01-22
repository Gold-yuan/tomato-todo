"""
TodoList控制器

连接TodoWidget UI和TodoService，处理用户交互
"""
from PyQt6.QtCore import QObject, pyqtSignal


class TodoController(QObject):
    """TodoList控制器"""

    # 定义信号（用于通知主窗口或其他组件）
    task_created = pyqtSignal(int)  # 任务已创建，参数：任务ID
    task_updated = pyqtSignal(int)  # 任务已更新，参数：任务ID
    task_deleted = pyqtSignal(int)  # 任务已删除，参数：任务ID
    task_toggled = pyqtSignal(int, bool)  # 任务状态已切换，参数：任务ID、新状态
    error_occurred = pyqtSignal(str)  # 发生错误，参数：错误消息

    def __init__(self, widget, service, parent=None):
        """
        初始化控制器

        Args:
            widget: TodoWidget实例
            service: TodoService实例
            parent: 父对象
        """
        super().__init__(parent)

        self.widget = widget
        self.service = service

        # 连接UI信号到控制器槽
        self._connect_signals()

        # 加载初始数据
        self._load_tasks()

    def _connect_signals(self):
        """连接UI信号到控制器槽"""
        # 任务创建
        self.widget.task_create_requested.connect(self._on_create_task)

        # 任务完成状态切换
        self.widget.task_toggle_requested.connect(self._on_toggle_task)

        # 任务删除
        self.widget.task_delete_requested.connect(self._on_delete_task)

        # 任务编辑
        self.widget.task_edit_requested.connect(self._on_edit_task)

        # 分页变化
        self.widget.page_changed.connect(self._on_page_changed)

    def _load_tasks(self, page: int = 1):
        """
        加载任务列表

        Args:
            page: 页码
        """
        try:
            # 调用service获取任务
            result = self.service.get_tasks(
                page=page,
                per_page=20,
                completed_only=False
            )

            # 转换数据格式
            tasks_data = [
                (task.id, task.content, task.is_completed)
                for task in result['tasks']
            ]

            # 更新UI
            self.widget.set_tasks(
                tasks_data=tasks_data,
                current_page=result['page'],
                total_pages=result['total_pages'],
                total=result['total']
            )

        except Exception as e:
            self.error_occurred.emit(f"加载任务失败: {str(e)}")

    def _on_create_task(self, content: str):
        """
        处理创建任务请求

        Args:
            content: 任务内容
        """
        try:
            task = self.service.create_task(content)
            self.service.session.commit()

            # 发射信号
            self.task_created.emit(task.id)

            # 重新加载第一页
            self._load_tasks(page=1)

        except ValueError as e:
            # 验证错误
            self.error_occurred.emit(str(e))
        except Exception as e:
            self.error_occurred.emit(f"创建任务失败: {str(e)}")

    def _on_toggle_task(self, task_id: int):
        """
        处理切换任务完成状态请求

        Args:
            task_id: 任务ID
        """
        try:
            task = self.service.toggle_completed(task_id)
            self.service.session.commit()

            # 发射信号
            self.task_toggled.emit(task_id, task.is_completed)

            # 重新加载当前页
            current_page = self.widget.get_current_page()
            self._load_tasks(page=current_page)

        except Exception as e:
            self.error_occurred.emit(f"切换任务状态失败: {str(e)}")

    def _on_delete_task(self, task_id: int):
        """
        处理删除任务请求

        Args:
            task_id: 任务ID
        """
        try:
            self.service.delete_task(task_id)
            self.service.session.commit()

            # 发射信号
            self.task_deleted.emit(task_id)

            # 重新加载当前页
            current_page = self.widget.get_current_page()
            self._load_tasks(page=current_page)

        except Exception as e:
            self.error_occurred.emit(f"删除任务失败: {str(e)}")

    def _on_edit_task(self, task_id: int, new_content: str):
        """
        处理编辑任务请求

        Args:
            task_id: 任务ID
            new_content: 新的任务内容
        """
        try:
            task = self.service.update_task(task_id, new_content)
            self.service.session.commit()

            # 发射信号
            self.task_updated.emit(task_id)

            # 重新加载当前页
            current_page = self.widget.get_current_page()
            self._load_tasks(page=current_page)

        except ValueError as e:
            # 验证错误
            self.error_occurred.emit(str(e))
        except Exception as e:
            self.error_occurred.emit(f"编辑任务失败: {str(e)}")

    def _on_page_changed(self, new_page: int):
        """
        处理分页变化

        Args:
            new_page: 新页码
        """
        self._load_tasks(page=new_page)

    def refresh(self):
        """刷新任务列表"""
        current_page = self.widget.get_current_page()
        self._load_tasks(page=current_page)
