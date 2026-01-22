"""
番茄时钟数据仓库

处理番茄时钟相关的数据库操作
"""
from datetime import datetime, date
from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import Session
from models import PomodoroTimer, PomodoroStats


class PomodoroRepository:
    """番茄时钟数据仓库"""

    def __init__(self, session: Session):
        """
        初始化仓库

        Args:
            session: SQLAlchemy会话
        """
        self.session = session

    def get_timer(self) -> Optional[PomodoroTimer]:
        """
        获取当前番茄时钟状态

        Returns:
            PomodoroTimer或None
        """
        return self.session.query(PomodoroTimer).first()

    def save_timer(self, timer: PomodoroTimer) -> PomodoroTimer:
        """
        保存番茄时钟状态

        Args:
            timer: 番茄时钟对象

        Returns:
            保存后的番茄时钟对象
        """
        # 使用merge，因为pomodoro_timer表只有一条记录
        timer.last_update = datetime.now()
        self.session.merge(timer)
        return timer

    def create_stats(self, mode: str, duration_seconds: int) -> PomodoroStats:
        """
        创建统计记录

        Args:
            mode: 模式 ('work' 或 'break')
            duration_seconds: 完成的时长（秒）

        Returns:
            创建的统计对象
        """
        now = datetime.now()
        stats = PomodoroStats(
            mode=mode,
            duration_seconds=duration_seconds,
            completed_at=now,
            date=now.strftime('%Y-%m-%d')
        )
        self.session.add(stats)
        return stats

    def get_stats_today(self, mode: str = 'work') -> int:
        """
        获取今日完成的番茄数

        Args:
            mode: 模式 ('work' 或 'break')

        Returns:
            完成的番茄数
        """
        today = date.today().strftime('%Y-%m-%d')
        count = self.session.query(PomodoroStats).filter(
            PomodoroStats.mode == mode,
            PomodoroStats.date == today
        ).count()
        return count

    def get_stats_week(self, mode: str = 'work') -> int:
        """
        获取本周完成的番茄数

        Args:
            mode: 模式 ('work' 或 'break')

        Returns:
            完成的番茄数
        """
        from datetime import timedelta
        week_ago = (date.today() - timedelta(days=7)).strftime('%Y-%m-%d')
        count = self.session.query(PomodoroStats).filter(
            PomodoroStats.mode == mode,
            PomodoroStats.date >= week_ago
        ).count()
        return count

    def get_stats_total(self, mode: str = 'work') -> int:
        """
        获取总共完成的番茄数

        Args:
            mode: 模式 ('work' 或 'break')

        Returns:
            完成的番茄数
        """
        count = self.session.query(PomodoroStats).filter(
            PomodoroStats.mode == mode
        ).count()
        return count
