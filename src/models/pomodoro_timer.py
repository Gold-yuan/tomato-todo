"""
番茄时钟状态模型

存储当前番茄时钟的运行状态
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from database import Base


class PomodoroTimer(Base):
    """番茄时钟状态表（单例，仅一条记录）"""
    __tablename__ = 'pomodoro_timer'

    id = Column(Integer, primary_key=True)
    mode = Column(String(10), nullable=False)  # 'work' or 'break'
    duration_seconds = Column(Integer, nullable=False)
    remaining_seconds = Column(Integer, nullable=False)
    status = Column(String(10), nullable=False)  # 'running', 'paused', 'stopped'
    start_time = Column(DateTime)  # 开始时间
    last_update = Column(DateTime, nullable=False)  # 最后更新时间
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return (
            f"<PomodoroTimer(id={self.id}, mode={self.mode}, "
            f"status={self.status}, remaining={self.remaining_seconds}s)>"
        )

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'mode': self.mode,
            'duration_seconds': self.duration_seconds,
            'remaining_seconds': self.remaining_seconds,
            'status': self.status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
