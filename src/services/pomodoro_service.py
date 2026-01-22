"""
番茄时钟服务

封装番茄时钟的业务逻辑
"""
from typing import Optional, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from database.repositories import PomodoroRepository
from models import PomodoroTimer
from utils.constants import MIN_DURATION, MAX_DURATION


class PomodoroService:
    """番茄时钟服务"""

    def __init__(self, session: Session):
        """
        初始化服务

        Args:
            session: SQLAlchemy会话
        """
        self.session = session
        self.repository = PomodoroRepository(session)

    def start_timer(self, duration: int, mode: str = 'work') -> PomodoroTimer:
        """
        启动番茄时钟

        Args:
            duration: 倒计时时长（秒）
            mode: 模式 ('work' 或 'break')

        Returns:
            PomodoroTimer对象

        Raises:
            ValueError: 如果参数无效
            RuntimeError: 如果时钟已在运行
        """
        # 验证参数
        if duration < MIN_DURATION or duration > MAX_DURATION:
            raise ValueError(f"时长必须在{MIN_DURATION}-{MAX_DURATION}秒之间")

        if mode not in ['work', 'break']:
            raise ValueError("模式必须是'work'或'break'")

        # 检查是否已有运行中的时钟
        current = self.repository.get_timer()
        if current and current.status == 'running':
            raise RuntimeError("时钟已在运行中")

        # 如果有已停止的计时器，复用它
        if current and current.status == 'stopped':
            current.mode = mode
            current.duration_seconds = duration
            current.remaining_seconds = duration
            current.status = 'running'
            current.start_time = datetime.now()
            current.last_update = datetime.now()
            saved_timer = self.repository.save_timer(current)
            self.session.flush()
            return saved_timer

        # 创建新计时器
        timer = PomodoroTimer(
            mode=mode,
            duration_seconds=duration,
            remaining_seconds=duration,
            status='running',
            start_time=datetime.now(),
            last_update=datetime.now()
        )

        saved_timer = self.repository.save_timer(timer)
        self.session.flush()
        return saved_timer

    def pause_timer(self) -> PomodoroTimer:
        """
        暂停番茄时钟

        Returns:
            PomodoroTimer对象

        Raises:
            RuntimeError: 如果时钟未运行
        """
        timer = self.repository.get_timer()
        if not timer or timer.status != 'running':
            raise RuntimeError("时钟未在运行")

        timer.status = 'paused'
        timer.last_update = datetime.now()
        saved_timer = self.repository.save_timer(timer)
        self.session.flush()  # 确保状态立即更新
        return saved_timer

    def resume_timer(self) -> PomodoroTimer:
        """
        继续番茄时钟

        Returns:
            PomodoroTimer对象

        Raises:
            RuntimeError: 如果时钟未暂停
        """
        timer = self.repository.get_timer()
        if not timer or timer.status != 'paused':
            raise RuntimeError("时钟未暂停")

        # 计算从暂停到现在经过的时间
        elapsed = int((datetime.now() - timer.last_update).total_seconds())
        timer.remaining_seconds = max(0, timer.remaining_seconds - elapsed)
        timer.status = 'running'
        timer.last_update = datetime.now()

        saved_timer = self.repository.save_timer(timer)
        self.session.flush()
        return saved_timer

    def stop_timer(self) -> PomodoroTimer:
        """
        停止番茄时钟

        Returns:
            PomodoroTimer对象
        """
        timer = self.repository.get_timer()
        if timer:
            timer.status = 'stopped'
            timer.remaining_seconds = timer.duration_seconds
            timer.last_update = datetime.now()
            saved_timer = self.repository.save_timer(timer)
            self.session.flush()
            return saved_timer
        else:
            # 如果没有计时器，创建一个停止的
            timer = PomodoroTimer(
                mode='work',
                duration_seconds=1500,
                remaining_seconds=1500,
                status='stopped',
                last_update=datetime.now()
            )
            saved_timer = self.repository.save_timer(timer)
            self.session.flush()
            return saved_timer

    def tick(self) -> Optional[PomodoroTimer]:
        """
        更新倒计时（每秒调用）

        Returns:
            更新后的PomodoroTimer对象，如果倒计时结束返回None
        """
        timer = self.repository.get_timer()
        if not timer or timer.status != 'running':
            return timer

        # 减少剩余时间
        timer.remaining_seconds -= 1
        timer.last_update = datetime.now()

        # 检查是否结束
        if timer.remaining_seconds <= 0:
            # 保存统计数据
            self.repository.create_stats(
                mode=timer.mode,
                duration_seconds=timer.duration_seconds
            )

            # 自动切换到下一个模式
            next_mode = 'break' if timer.mode == 'work' else 'work'
            next_duration = 300 if next_mode == 'break' else 1500

            timer.mode = next_mode
            timer.duration_seconds = next_duration
            timer.remaining_seconds = next_duration
            timer.status = 'stopped'
            timer.start_time = None

            self.repository.save_timer(timer)
            self.session.flush()
            return None  # 倒计时结束

        saved_timer = self.repository.save_timer(timer)
        self.session.flush()
        return saved_timer

    def get_current_timer(self) -> Optional[PomodoroTimer]:
        """
        获取当前番茄时钟状态

        Returns:
            PomodoroTimer对象或None
        """
        return self.repository.get_timer()

    def get_stats(self) -> Dict[str, int]:
        """
        获取统计数据

        Returns:
            统计字典
        """
        return {
            'total_completed': self.repository.get_stats_total('work'),
            'today_completed': self.repository.get_stats_today('work'),
            'week_completed': self.repository.get_stats_week('work'),
            'today_breaks': self.repository.get_stats_today('break'),
            'week_breaks': self.repository.get_stats_week('break'),
        }
