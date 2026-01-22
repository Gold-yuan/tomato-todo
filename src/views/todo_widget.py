"""
TodoList UI组件

显示任务列表、输入框、分页控件
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QLineEdit,
    QPushButton, QLabel, QMenu, QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction


class TaskWidgetItem(QWidget):
    """自定义任务项组件"""

    def __init__(self, task_id: int, content: str, is_completed: bool, parent=None):
        super().__init__(parent)

        self.task_id = task_id
        self.content = content
        self.is_completed = is_completed

        # 创建布局
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # 完成状态图标
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(20, 20)
        self._update_icon()
        layout.addWidget(self.icon_label)

        # 任务文本
        self.text_label = QLabel(content)
        self.text_label.setWordWrap(True)
        self.text_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.text_label.setToolTip(content)  # 完整内容tooltip
        self._update_text_style()
        layout.addWidget(self.text_label, 1)  # stretch=1占据剩余空间

        self.setLayout(layout)

        # 设置固定高度
        self.setFixedHeight(40)

    def _update_icon(self):
        """更新完成状态图标"""
        if self.is_completed:
            # 已完成：绿色圆形勾选
            self.icon_label.setText("✓")
            self.icon_label.setStyleSheet("""
                QLabel {
                    background-color: #27AE60;
                    color: white;
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: bold;
                }
            """)
        else:
            # 未完成：灰色圆形
            self.icon_label.setText("○")
            self.icon_label.setStyleSheet("""
                QLabel {
                    background-color: #BDC3C7;
                    color: white;
                    border-radius: 10px;
                    font-size: 14px;
                }
            """)

    def _update_text_style(self):
        """更新文本样式"""
        if self.is_completed:
            self.text_label.setStyleSheet("""
                QLabel {
                    color: #95A5A6;
                    text-decoration: line-through;
                }
            """)
        else:
            self.text_label.setStyleSheet("""
                QLabel {
                    color: #2C3E50;
                }
            """)

    def set_completed(self, is_completed: bool):
        """设置完成状态"""
        self.is_completed = is_completed
        self._update_icon()
        self._update_text_style()

    def set_content(self, content: str):
        """设置任务内容"""
        self.content = content
        self.text_label.setText(content)
        self.text_label.setToolTip(content)


class TodoWidget(QWidget):
    """TodoList任务列表组件"""

    # 定义信号
    task_create_requested = pyqtSignal(str)  # 请求创建任务，参数：任务内容
    task_toggle_requested = pyqtSignal(int)  # 请求切换完成状态，参数：任务ID
    task_delete_requested = pyqtSignal(int)  # 请求删除任务，参数：任务ID
    task_edit_requested = pyqtSignal(int, str)  # 请求编辑任务，参数：任务ID、新内容
    page_changed = pyqtSignal(int)  # 页码变化，参数：新页码

    def __init__(self, parent=None):
        super().__init__(parent)

        # 分页状态
        self._current_page = 1
        self._total_pages = 1
        self._per_page = 20
        self._total = 0

        # 初始化UI
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 标题
        title_label = QLabel("待办任务")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2C3E50;
                padding: 5px;
            }
        """)
        main_layout.addWidget(title_label)

        # 任务输入框
        input_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("输入新任务，按回车添加...")
        self.task_input.setObjectName("taskInput")
        self.task_input.returnPressed.connect(self._on_add_task)
        input_layout.addWidget(self.task_input)

        main_layout.addLayout(input_layout)

        # 任务列表
        self.task_list = QListWidget()
        self.task_list.setObjectName("taskList")
        self.task_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.task_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.task_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.task_list.customContextMenuRequested.connect(self._show_context_menu)
        main_layout.addWidget(self.task_list)

        # 分页控件
        pagination_widget = QWidget()
        pagination_widget.setObjectName("paginationWidget")
        pagination_layout = QHBoxLayout()
        pagination_layout.setContentsMargins(5, 5, 5, 5)
        pagination_layout.setSpacing(10)

        # 上一页按钮
        self.prev_button = QPushButton("上一页")
        self.prev_button.setObjectName("pageButton")
        self.prev_button.setEnabled(False)
        self.prev_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_button.clicked.connect(self._on_prev_page)
        pagination_layout.addWidget(self.prev_button)

        # 页码标签
        self.page_label = QLabel("第 1 / 1 页")
        self.page_label.setObjectName("pageLabel")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pagination_layout.addWidget(self.page_label, 1)  # stretch=1

        # 下一页按钮
        self.next_button = QPushButton("下一页")
        self.next_button.setObjectName("pageButton")
        self.next_button.setEnabled(False)
        self.next_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_button.clicked.connect(self._on_next_page)
        pagination_layout.addWidget(self.next_button)

        pagination_widget.setLayout(pagination_layout)
        main_layout.addWidget(pagination_widget)

        # 设置布局
        self.setLayout(main_layout)

    def _on_add_task(self):
        """添加任务按钮点击"""
        content = self.task_input.text().strip()
        if content:
            self.task_create_requested.emit(content)
            self.task_input.clear()

    def _on_prev_page(self):
        """上一页按钮点击"""
        if self._current_page > 1:
            new_page = self._current_page - 1
            self.page_changed.emit(new_page)

    def _on_next_page(self):
        """下一页按钮点击"""
        if self._current_page < self._total_pages:
            new_page = self._current_page + 1
            self.page_changed.emit(new_page)

    def _on_item_double_clicked(self, item: QListWidgetItem):
        """任务项双击 - 编辑"""
        widget = self.task_list.itemWidget(item)
        if widget and isinstance(widget, TaskWidgetItem):
            self._start_inline_edit(widget, item)

    def _start_inline_edit(self, widget: TaskWidgetItem, item: QListWidgetItem):
        """开始行内编辑"""
        # 使用QInputDialog进行编辑
        new_content, ok = QInputDialog.getText(
            self,
            "编辑任务",
            "修改任务内容:",
            text=widget.content
        )

        if ok and new_content.strip():
            self.task_edit_requested.emit(widget.task_id, new_content.strip())

    def _show_context_menu(self, pos):
        """显示右键菜单"""
        item = self.task_list.itemAt(pos)
        if not item:
            return

        widget = self.task_list.itemWidget(item)
        if not widget or not isinstance(widget, TaskWidgetItem):
            return

        menu = QMenu(self)

        # 切换完成状态
        toggle_action = QAction(
            "标记为未完成" if widget.is_completed else "标记为已完成",
            menu
        )
        toggle_action.triggered.connect(
            lambda: self.task_toggle_requested.emit(widget.task_id)
        )
        menu.addAction(toggle_action)

        # 编辑
        edit_action = QAction("编辑", menu)
        edit_action.triggered.connect(
            lambda: self._start_inline_edit(widget, item)
        )
        menu.addAction(edit_action)

        menu.addSeparator()

        # 删除
        delete_action = QAction("删除", menu)
        delete_action.triggered.connect(
            lambda: self.task_delete_requested.emit(widget.task_id)
        )
        menu.addAction(delete_action)

        # 显示菜单
        menu.exec(self.task_list.mapToGlobal(pos))

    def set_tasks(self, tasks_data: list, current_page: int = 1,
                  total_pages: int = 1, total: int = 0):
        """
        设置任务列表数据

        Args:
            tasks_data: 任务数据列表，每项为 (task_id, content, is_completed) 元组
            current_page: 当前页码
            total_pages: 总页数
            total: 总任务数
        """
        self._current_page = current_page
        self._total_pages = total_pages
        self._total = total

        # 清空列表
        self.task_list.clear()

        # 添加任务
        for task_id, content, is_completed in tasks_data:
            item = QListWidgetItem()
            item.setSizeHint(item.sizeHint())  # 使用默认大小

            # 创建自定义widget
            widget = TaskWidgetItem(task_id, content, is_completed)

            # 设置到列表项
            self.task_list.addItem(item)
            self.task_list.setItemWidget(item, widget)

        # 更新分页控件
        self._update_pagination()

    def _update_pagination(self):
        """更新分页控件状态"""
        # 更新页码标签
        if self._total_pages > 0:
            self.page_label.setText(f"第 {self._current_page} / {self._total_pages} 页")
        else:
            self.page_label.setText("第 0 / 0 页")

        # 更新按钮状态
        self.prev_button.setEnabled(self._current_page > 1)
        self.next_button.setEnabled(self._current_page < self._total_pages)

    def get_current_page(self) -> int:
        """获取当前页码"""
        return self._current_page

    def set_current_page(self, page: int):
        """设置当前页码"""
        self._current_page = page
        self._update_pagination()
