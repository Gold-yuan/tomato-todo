"""
番茄时钟统计模型

存储番茄时钟的使用统计和历史记录
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from database import Base


class PomodoroStats(Base):
    """番茄时钟统计表"""
    __tablename__ = 'pomodoro_stats'

    id = Column(Integer, primary_key=True)
    mode = Column(String(10), nullable=False)  # 'work' or 'break'
    duration_seconds = Column(Integer, nullable=False)  # 实际完成的时长
    completed_at = Column(DateTime, nullable=False)  # 完成时间
    date = Column(String(10), nullable=False)  # 日期 YYYY-MM-DD

    def __repr__(self):
        return (
            f"<PomodoroStats(id={self.id}, mode={self.mode}, "
            f"duration={self.duration_seconds}s, date={self.date})>"
        )

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'mode': self.mode,
            'duration_seconds': self.duration_seconds,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'date': self.date,
        }
