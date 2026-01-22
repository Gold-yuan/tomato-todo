"""
番茄时钟控制器

连接UI组件和Service层，处理按钮点击和UI状态更新
"""
from PyQt6.QtCore import QObject, pyqtSignal
from sqlalchemy.orm import Session
from services import PomodoroService
from views import PomodoroWidget
from views.dialogs import TimeSetDialog, TimeoutDialog
from utils.constants import DEFAULT_WORK_DURATION, DEFAULT_BREAK_DURATION


class PomodoroController(QObject):
    """番茄时钟控制器"""

    # 定义信号
    timer_completed = pyqtSignal(str)  # 倒计时结束，参数：mode

    def __init__(self, widget: PomodoroWidget, service: PomodoroService, session: Session):
        """
        初始化控制器

        Args:
            widget: PomodoroWidget UI组件
            service: PomodoroService 服务
            session: 数据库会话
        """
        super().__init__()

        self.widget = widget
        self.service = service
        self.session = session

        # 定时器（每秒更新）
        self._tick_timer = None

        # 连接信号
        self._connect_signals()

        # 加载初始状态
        self._load_initial_state()

    def _connect_signals(self):
        """连接UI信号到控制器槽"""
        self.widget.start_requested.connect(self._on_start_requested)
        self.widget.pause_requested.connect(self._on_pause_requested)
        self.widget.stop_requested.connect(self._on_stop_requested)
        self.widget.time_set_requested.connect(self._on_time_set_requested)

    def _load_initial_state(self):
        """加载初始状态"""
        # 获取当前计时器状态
        timer = self.service.get_current_timer()

        if timer:
            # 更新显示
            self.widget.update_display(timer.remaining_seconds)
            self.widget.set_mode(timer.mode)

            # 设置运行状态
            if timer.status == 'running':
                self.widget.set_running_state(is_running=True)
                self._start_tick_timer()
            elif timer.status == 'paused':
                self.widget.set_running_state(is_running=True, is_paused=True)
            else:  # stopped
                self.widget.set_running_state(is_running=False)
        else:
            # 没有计时器，显示默认时间
            self.widget.update_display(DEFAULT_WORK_DURATION)
            self.widget.set_mode('work')
            self.widget.set_running_state(is_running=False)

    def _on_start_requested(self, duration: int):
        """处理开始请求"""
        try:
            # 确定模式
            mode = self.widget.get_mode()

            # 启动计时器
            timer = self.service.start_timer(duration, mode)
            self.session.commit()

            # 更新UI
            self.widget.update_display(timer.remaining_seconds)
            self.widget.set_mode(timer.mode)
            self.widget.set_running_state(is_running=True)

            # 启动定时器
            self._start_tick_timer()

        except Exception as e:
            print(f"启动计时器失败: {e}")

    def _on_pause_requested(self):
        """处理暂停请求"""
        try:
            timer = self.service.pause_timer()
            self.session.commit()

            # 更新UI
            self.widget.set_running_state(is_running=True, is_paused=True)

            # 停止定时器
            self._stop_tick_timer()

        except Exception as e:
            print(f"暂停计时器失败: {e}")

    def _on_stop_requested(self):
        """处理停止请求"""
        try:
            timer = self.service.stop_timer()
            self.session.commit()

            # 更新UI
            self.widget.update_display(timer.remaining_seconds)
            self.widget.set_running_state(is_running=False)

            # 停止定时器
            self._stop_tick_timer()

        except Exception as e:
            print(f"停止计时器失败: {e}")

    def _on_time_set_requested(self):
        """处理时间设置请求"""
        # 显示时间设置对话框
        durations = TimeSetDialog.get_time_settings(parent=self.widget)

        if durations:
            work_duration, break_duration = durations
            # TODO: 保存到用户偏好设置
            print(f"设置时长 - 工作: {work_duration}秒, 休息: {break_duration}秒")

    def _start_tick_timer(self):
        """启动定时器"""
        if self._tick_timer is None:
            self._tick_timer = self._tick_timer = self._create_tick_timer()
            self._tick_timer.start()

    def _stop_tick_timer(self):
        """停止定时器"""
        if self._tick_timer:
            self._tick_timer.stop()
            self._tick_timer = None

    def _create_tick_timer(self):
        """创建定时器"""
        from PyQt6.QtCore import QTimer

        timer = QTimer(self)
        timer.setInterval(1000)  # 1秒
        timer.timeout.connect(self._on_tick)
        return timer

    def _on_tick(self):
        """处理定时器tick"""
        try:
            timer = self.service.tick()

            if timer is None:
                # 倒计时结束
                self._stop_tick_timer()

                # 获取当前计时器状态（已切换到下一个模式）
                current_timer = self.service.get_current_timer()
                if current_timer:
                    # 保存统计
                    self.session.commit()

                    # 显示全屏提示
                    self._show_timeout_dialog(current_timer.mode)

                    # 更新UI
                    self.widget.update_display(current_timer.remaining_seconds)
                    self.widget.set_mode(current_timer.mode)
                    self.widget.set_running_state(is_running=False)

                    # 发送完成信号
                    self.timer_completed.emit(current_timer.mode)
                else:
                    # 理论上不应该到这里
                    print("错误：倒计时结束后没有当前计时器")

            else:
                # 更新显示
                self.widget.update_display(timer.remaining_seconds)

        except Exception as e:
            print(f"Tick处理失败: {e}")
            self._stop_tick_timer()

    def _show_timeout_dialog(self, mode: str):
        """显示超时提示对话框"""
        try:
            TimeoutDialog.show_timeout(mode, parent=self.widget)
        except Exception as e:
            print(f"显示超时对话框失败: {e}")

    def cleanup(self):
        """清理资源"""
        self._stop_tick_timer()
