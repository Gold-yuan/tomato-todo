"""
Todo任务模型

存储所有Todo任务
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Index
from database import Base


class TodoTask(Base):
    """Todo任务表"""
    __tablename__ = 'todo_tasks'

    id = Column(Integer, primary_key=True)
    content = Column(String(100), nullable=False)  # 最多100个中文字符
    is_completed = Column(Boolean, nullable=False, default=False)
    completed_at = Column(DateTime)  # 完成时间
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # 索引：优化排序查询
    __table_args__ = (
        Index('idx_completed_updated', 'is_completed', 'updated_at'),
        Index('idx_is_completed', 'is_completed'),
    )

    def __repr__(self):
        status = "✓" if self.is_completed else " "
        return f"<TodoTask(id={self.id}, content='{self.content[:20]}...', [{status}])>"

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'content': self.content,
            'is_completed': self.is_completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
