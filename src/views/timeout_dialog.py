"""
全屏倒计时结束提示对话框

倒计时结束时显示全屏提示，支持渐隐动画和点击/按键关闭
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QKeyEvent, QMouseEvent
from PyQt6.QtWidgets import QGraphicsOpacityEffect


class TimeoutDialog(QDialog):
    """全屏倒计时结束提示对话框"""

    def __init__(self, mode: str, parent=None):
        """
        初始化对话框

        Args:
            mode: 'work' 或 'break'
            parent: 父窗口
        """
        super().__init__(parent)

        self._mode = mode
        self._auto_close_timer = None
        self._fade_animation = None

        # 设置窗口属性
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        # 初始化UI
        self._init_ui()

        # 设置2秒后自动关闭
        self._setup_auto_close()

        # 设置渐隐动画
        self._setup_fade_animation()

    def _init_ui(self):
        """初始化UI"""
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(30)

        # 标题
        if self._mode == 'work':
            title_text = "工作时间结束！"
            color = "#E74C3C"  # 番茄红
        else:  # break
            title_text = "休息时间结束！"
            color = "#27AE60"  # 绿色

        title_label = QLabel(title_text)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 48px;
                font-weight: bold;
                color: {color};
                padding: 20px;
            }}
        """)
        main_layout.addWidget(title_label)

        # 提示文字
        if self._mode == 'work':
            subtitle = "休息一下，准备下一个番茄钟吧！"
        else:
            subtitle = "休息结束，开始新的工作吧！"

        subtitle_label = QLabel(subtitle)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: #2C3E50;
                padding: 10px;
            }
        """)
        main_layout.addWidget(subtitle_label)

        # 点击关闭提示
        hint_label = QLabel("点击任意位置或按任意键关闭")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #7F8C8D;
                padding: 10px;
            }
        """)
        main_layout.addWidget(hint_label)

        self.setLayout(main_layout)

        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background-color: rgba(245, 246, 250, 0.95);
                border-radius: 15px;
            }
        """)

    def _setup_auto_close(self):
        """设置2秒后自动关闭"""
        self._auto_close_timer = QTimer(self)
        self._auto_close_timer.setSingleShot(True)
        self._auto_close_timer.timeout.connect(self._start_fade_out)
        self._auto_close_timer.start(2000)  # 2秒后开始渐隐

    def _setup_fade_animation(self):
        """设置渐隐动画"""
        # 创建透明度效果
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)

        # 创建渐隐动画
        self._fade_animation = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._fade_animation.setDuration(500)  # 500ms渐隐
        self._fade_animation.setStartValue(1.0)  # 从完全不透明
        self._fade_animation.setEndValue(0.0)  # 到完全透明
        self._fade_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._fade_animation.finished.connect(self.close)

    def _start_fade_out(self):
        """开始渐隐"""
        if self._fade_animation:
            self._fade_animation.start()

    def keyPressEvent(self, event: QKeyEvent):
        """按键事件：任意键关闭"""
        # 停止自动关闭定时器
        if self._auto_close_timer and self._auto_close_timer.isActive():
            self._auto_close_timer.stop()

        # 直接关闭（不渐隐）
        self.close()

    def mousePressEvent(self, event: QMouseEvent):
        """鼠标点击事件：点击任意位置关闭"""
        # 停止自动关闭定时器
        if self._auto_close_timer and self._auto_close_timer.isActive():
            self._auto_close_timer.stop()

        # 直接关闭（不渐隐）
        self.close()

    def closeEvent(self, event):
        """关闭事件：清理资源"""
        if self._auto_close_timer:
            self._auto_close_timer.stop()
        if self._fade_animation:
            self._fade_animation.stop()

        super().closeEvent(event)

    @staticmethod
    def show_timeout(mode: str, parent=None):
        """
        静态方法：显示超时提示

        Args:
            mode: 'work' 或 'break'
            parent: 父窗口
        """
        dialog = TimeoutDialog(mode, parent)
        dialog.show()
