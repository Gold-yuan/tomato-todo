"""
时间设置对话框

用于自定义番茄时长和休息时长
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSpinBox, QButtonGroup,
    QRadioButton, QFrame
)
from PyQt6.QtCore import Qt
from utils.constants import DEFAULT_WORK_DURATION, DEFAULT_BREAK_DURATION


class TimeSetDialog(QDialog):
    """时间设置对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置时间")
        self.setMinimumWidth(350)

        self._work_duration = DEFAULT_WORK_DURATION
        self._break_duration = DEFAULT_BREAK_DURATION

        self._init_ui()

    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # 工作时长设置
        work_group = self._create_time_group(
            "工作时长",
            DEFAULT_WORK_DURATION,
            60,  # 最小1分钟
            7200,  # 最大2小时
            "work"
        )
        layout.addWidget(work_group)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        # 休息时长设置
        break_group = self._create_time_group(
            "休息时长",
            DEFAULT_BREAK_DURATION,
            60,
            3600,  # 最大1小时
            "break"
        )
        layout.addWidget(break_group)

        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # 确认按钮
        self.ok_button = QPushButton("确定")
        self.ok_button.setMinimumHeight(35)
        self.ok_button.setMinimumWidth(100)
        self.ok_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)

        # 取消按钮
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setMinimumHeight(35)
        self.cancel_button.setMinimumWidth(100)
        self.cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def _create_time_group(self, title: str, default_value: int,
                          min_value: int, max_value: int, mode: str):
        """创建时间设置组"""
        group = QFrame()
        group_layout = QVBoxLayout()
        group_layout.setSpacing(10)

        # 标题
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2C3E50;
            }
        """)
        group_layout.addWidget(title_label)

        # 数字输入框
        spin_box = QSpinBox()
        spin_box.setRange(min_value, max_value)
        spin_box.setValue(default_value)
        spin_box.setSuffix(" 秒")
        spin_box.setMinimumHeight(35)
        spin_box.setStyleSheet("""
            QSpinBox {
                font-size: 14px;
                padding: 5px;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
            }
            QSpinBox:focus {
                border: 1px solid #E74C3C;
            }
        """)

        # 保存到实例变量
        if mode == "work":
            self._work_spinbox = spin_box
        else:
            self._break_spinbox = spin_box

        group_layout.addWidget(spin_box)

        # 快捷预设
        presets_layout = QHBoxLayout()
        presets_layout.setSpacing(5)

        if mode == "work":
            presets = [
                ("25分钟", 1500),
                ("30分钟", 1800),
                ("45分钟", 2700),
            ]
        else:  # break
            presets = [
                ("5分钟", 300),
                ("10分钟", 600),
                ("15分钟", 900),
            ]

        for preset_text, preset_value in presets:
            preset_button = QPushButton(preset_text)
            preset_button.setCheckable(False)
            preset_button.setMinimumHeight(30)
            preset_button.setCursor(Qt.CursorShape.PointingHandCursor)
            preset_button.clicked.connect(
                lambda checked, value=preset_value, sb=spin_box: sb.setValue(value)
            )
            presets_layout.addWidget(preset_button)

        group_layout.addLayout(presets_layout)
        group.setLayout(group_layout)

        return group

    def get_durations(self) -> tuple:
        """
        获取设置的工作和休息时长

        Returns:
            (work_duration, break_duration) 以秒为单位
        """
        return (
            self._work_spinbox.value(),
            self._break_spinbox.value()
        )

    @staticmethod
    def get_time_settings(parent=None) -> tuple:
        """
        静态方法：显示对话框并获取时间设置

        Args:
            parent: 父窗口

        Returns:
            (work_duration, break_duration) 或 None（如果取消）
        """
        dialog = TimeSetDialog(parent)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            return dialog.get_durations()
        else:
            return None
