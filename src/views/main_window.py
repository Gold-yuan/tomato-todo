"""
主窗口组件

实现无边框窗口、拖拽、调整大小、置顶、靠边对齐等功能
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QSizeGrip
)
from PyQt6.QtCore import Qt, QPoint, QRect
from PyQt6.QtGui import QCursor


class TomatoTodoWindow(QMainWindow):
    """番茄时钟主窗口"""

    # 定义常量
    SNAP_THRESHOLD = 30  # 吸附阈值（像素）
    MINIMUM_WIDTH = 350  # 最小宽度
    MINIMUM_HEIGHT = 400  # 最小高度
    RESIZE_HANDLE_SIZE = 10  # 调整大小手柄尺寸

    def __init__(self, parent=None):
        super().__init__(parent)

        # 窗口状态
        self._is_stay_on_top = False
        self._is_dragging = False
        self._is_resizing = False
        self._drag_start_position = QPoint()
        self._resize_edge = None  # 'top', 'bottom', 'left', 'right', 'topleft', etc.

        # 初始化UI
        self._init_ui()

        # 设置窗口属性
        self._setup_window_flags()

    def _init_ui(self):
        """初始化UI"""
        # 设置窗口标题
        self.setWindowTitle("番茄时钟 & 待办清单")

        # 设置最小尺寸
        self.setMinimumSize(self.MINIMUM_WIDTH, self.MINIMUM_HEIGHT)

        # 创建中央widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # 主布局（稍后会被外部填充）
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.central_widget.setLayout(self.main_layout)

        # 添加调整大小手柄（右下角）
        self.size_grip = QSizeGrip(self)
        self.size_grip.setVisible(False)  # 初始隐藏，无边框时显示

    def _setup_window_flags(self):
        """设置窗口标志"""
        # 默认无边框
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowSystemMenuHint
        )

    def add_widget(self, widget, stretch=0):
        """
        添加widget到主布局

        Args:
            widget: 要添加的widget
            stretch: 拉伸因子
        """
        self.main_layout.addWidget(widget, stretch)

    def resizeEvent(self, event):
        """重写resize事件 - 强制执行最小尺寸"""
        super().resizeEvent(event)

        # 确保不会小于最小尺寸
        new_width = max(event.size().width(), self.MINIMUM_WIDTH)
        new_height = max(event.size().height(), self.MINIMUM_HEIGHT)

        if new_width != event.size().width() or new_height != event.size().height():
            self.resize(new_width, new_height)

        # 更新大小调整手柄位置
        self._update_size_grip_position()

    def _update_size_grip_position(self):
        """更新大小调整手柄位置"""
        if self.size_grip.isVisible():
            grip_size = self.size_grip.size()
            self.size_grip.move(
                self.width() - grip_size.width(),
                self.height() - grip_size.height()
            )

    def mousePressEvent(self, event):
        """鼠标按下事件 - 开始拖拽或调整大小"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 检查是否在边缘（调整大小）
            edge = self._get_resize_edge(event.position().toPoint())
            if edge:
                self._is_resizing = True
                self._resize_edge = edge
                self._drag_start_position = event.position().toPoint()
            else:
                # 检查是否在标题栏区域（拖拽）
                # 简化：假设窗口上半部分可以拖拽
                if event.position().y() < 50:  # 标题栏高度
                    self._is_dragging = True
                    self._drag_start_position = event.position().toPoint()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 执行拖拽或调整大小"""
        if event.buttons() & Qt.MouseButton.LeftButton:
            if self._is_dragging:
                # 拖拽窗口
                delta = event.position().toPoint() - self._drag_start_position
                new_pos = self.pos() + delta
                self.move(new_pos)

            elif self._is_resizing:
                # 调整窗口大小
                self._handle_resize(event.position().toPoint())

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """鼠标释放事件 - 结束拖拽或调整大小"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = False
            self._is_resizing = False
            self._resize_edge = None

        super().mouseReleaseEvent(event)

    def moveEvent(self, event):
        """窗口移动事件 - 处理靠边对齐"""
        super().moveEvent(event)

        # 检查是否靠近屏幕边缘
        self._snap_to_edges()

    def _get_resize_edge(self, pos: QPoint) -> str:
        """
        获取鼠标位置的边缘

        Args:
            pos: 鼠标位置

        Returns:
            边缘名称或None
        """
        x = pos.x()
        y = pos.y()
        w = self.width()
        h = self.height()
        margin = self.RESIZE_HANDLE_SIZE

        # 检查各个边缘和角落
        if x <= margin and y <= margin:
            return 'topleft'
        elif x >= w - margin and y <= margin:
            return 'topright'
        elif x <= margin and y >= h - margin:
            return 'bottomleft'
        elif x >= w - margin and y >= h - margin:
            return 'bottomright'
        elif x <= margin:
            return 'left'
        elif x >= w - margin:
            return 'right'
        elif y <= margin:
            return 'top'
        elif y >= h - margin:
            return 'bottom'

        return None

    def _handle_resize(self, pos: QPoint):
        """
        处理窗口大小调整

        Args:
            pos: 当前鼠标位置
        """
        if not self._resize_edge:
            return

        delta = pos - self._drag_start_position
        new_geometry = self.geometry()
        min_width = self.MINIMUM_WIDTH
        min_height = self.MINIMUM_HEIGHT

        if 'left' in self._resize_edge:
            new_x = self.x() + delta.x()
            new_width = self.width() - delta.x()
            if new_width >= min_width:
                new_geometry.setX(new_x)
                new_geometry.setWidth(new_width)

        if 'right' in self._resize_edge:
            new_width = self.width() + delta.x()
            if new_width >= min_width:
                new_geometry.setWidth(new_width)

        if 'top' in self._resize_edge:
            new_y = self.y() + delta.y()
            new_height = self.height() - delta.y()
            if new_height >= min_height:
                new_geometry.setY(new_y)
                new_geometry.setHeight(new_height)

        if 'bottom' in self._resize_edge:
            new_height = self.height() + delta.y()
            if new_height >= min_height:
                new_geometry.setHeight(new_height)

        self.setGeometry(new_geometry)
        self._drag_start_position = pos

    def _snap_to_edges(self):
        """吸附到屏幕边缘"""
        # 获取屏幕信息
        screen = self.screen().availableGeometry()
        window_geom = self.geometry()

        # 检查左边缘（独立检查，不使用elif）
        if abs(window_geom.left() - screen.left()) < self.SNAP_THRESHOLD:
            window_geom.moveLeft(screen.left())

        # 检查右边缘
        if abs(window_geom.right() - screen.right()) < self.SNAP_THRESHOLD:
            window_geom.moveRight(screen.right())

        # 检查顶部
        if abs(window_geom.top() - screen.top()) < self.SNAP_THRESHOLD:
            window_geom.moveTop(screen.top())

        # 检查底部
        if abs(window_geom.bottom() - screen.bottom()) < self.SNAP_THRESHOLD:
            window_geom.moveBottom(screen.bottom())

        # 应用吸附后的位置
        self.setGeometry(window_geom)

    def toggle_stay_on_top(self, enabled: bool = None):
        """
        切换置顶状态

        Args:
            enabled: True启用置顶，False禁用，None切换
        """
        if enabled is None:
            enabled = not self._is_stay_on_top

        self._is_stay_on_top = enabled

        # 更新窗口标志
        if enabled:
            self.setWindowFlags(
                self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint
            )
        else:
            self.setWindowFlags(
                self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint
            )

        # 重新显示窗口（窗口标志改变后需要）
        self.show()

    def is_stay_on_top(self) -> bool:
        """
        获取置顶状态

        Returns:
            是否置顶
        """
        return self._is_stay_on_top

    @property
    def snap_threshold(self) -> int:
        """获取吸附阈值"""
        return self.SNAP_THRESHOLD
