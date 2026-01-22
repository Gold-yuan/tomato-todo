"""
番茄时钟UI组件

显示倒计时、控制按钮（开始/暂停/停止）
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLCDNumber
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont


class PomodoroWidget(QWidget):
    """番茄时钟显示组件"""

    # 定义信号
    start_requested = pyqtSignal(int)  # 请求开始，参数：时长（秒）
    pause_requested = pyqtSignal()  # 请求暂停
    stop_requested = pyqtSignal()  # 请求停止
    time_set_requested = pyqtSignal()  # 请求设置时间

    def __init__(self, parent=None):
        super().__init__(parent)

        # 状态
        self._current_mode = 'work'  # work 或 break
        self._is_running = False
        self._is_paused = False

        # 初始化UI
        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 模式标签
        self.mode_label = QLabel("工作模式")
        self.mode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mode_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #E74C3C;
                padding: 5px;
            }
        """)
        main_layout.addWidget(self.mode_label)

        # 数字时钟显示
        self.lcd_display = QLCDNumber()
        self.lcd_display.setDigitCount(8)  # HH:MM:SS 格式
        self.lcd_display.display("25:00:00")
        self.lcd_display.setMinimumHeight(80)
        self.lcd_display.setStyleSheet("""
            QLCDNumber {
                background-color: #F5F6FA;
                color: #2C3E50;
                border: 2px solid #E74C3C;
                border-radius: 8px;
            }
        """)
        main_layout.addWidget(self.lcd_display)

        # 控制按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # 开始/暂停按钮
        self.start_pause_button = QPushButton("开始")
        self.start_pause_button.setMinimumHeight(40)
        self.start_pause_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_pause_button.clicked.connect(self._on_start_pause_clicked)
        button_layout.addWidget(self.start_pause_button)

        # 停止按钮
        self.stop_button = QPushButton("停止")
        self.stop_button.setMinimumHeight(40)
        self.stop_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stop_button.setEnabled(False)  # 初始禁用
        self.stop_button.clicked.connect(self._on_stop_clicked)
        button_layout.addWidget(self.stop_button)

        # 设置时间按钮
        self.set_time_button = QPushButton("设置")
        self.set_time_button.setMinimumHeight(40)
        self.set_time_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.set_time_button.clicked.connect(self.time_set_requested.emit)
        button_layout.addWidget(self.set_time_button)

        main_layout.addLayout(button_layout)

        # 设置布局
        self.setLayout(main_layout)

    def _on_start_pause_clicked(self):
        """开始/暂停按钮点击"""
        if self._is_running:
            # 暂停
            self.pause_requested.emit()
        else:
            # 开始（使用默认时长）
            duration = 1500 if self._current_mode == 'work' else 300
            self.start_requested.emit(duration)

    def _on_stop_clicked(self):
        """停止按钮点击"""
        self.stop_requested.emit()

    def update_display(self, remaining_seconds: int):
        """
        更新倒计时显示

        Args:
            remaining_seconds: 剩余秒数
        """
        hours = remaining_seconds // 3600
        minutes = (remaining_seconds % 3600) // 60
        seconds = remaining_seconds % 60

        # 格式化为 HH:MM:SS
        time_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.lcd_display.display(time_text)

    def set_mode(self, mode: str):
        """
        设置模式

        Args:
            mode: 'work' 或 'break'
        """
        self._current_mode = mode
        if mode == 'work':
            self.mode_label.setText("工作模式")
            self.mode_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #E74C3C;
                    padding: 5px;
                }
            """)
        else:  # break
            self.mode_label.setText("休息模式")
            self.mode_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #27AE60;
                    padding: 5px;
                }
            """)

    def set_running_state(self, is_running: bool, is_paused: bool = False):
        """
        设置运行状态

        Args:
            is_running: 是否运行中
            is_paused: 是否暂停
        """
        self._is_running = is_running
        self._is_paused = is_paused

        # 更新按钮状态
        if is_running and not is_paused:
            self.start_pause_button.setText("暂停")
            self.stop_button.setEnabled(True)
            self.set_time_button.setEnabled(False)
        elif is_paused:
            self.start_pause_button.setText("继续")
            self.stop_button.setEnabled(True)
            self.set_time_button.setEnabled(False)
        else:  # stopped
            self.start_pause_button.setText("开始")
            self.stop_button.setEnabled(False)
            self.set_time_button.setEnabled(True)

    def get_mode(self) -> str:
        """获取当前模式"""
        return self._current_mode
