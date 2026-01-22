"""
用户偏好模型

存储用户的个人设置和偏好
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Index
from database import Base


class UserPreferences(Base):
    """用户偏好表"""
    __tablename__ = 'user_preferences'

    id = Column(Integer, primary_key=True)
    key = Column(String(50), nullable=False, unique=True)  # 配置键
    value = Column(String(500), nullable=False)  # 配置值（JSON格式）
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # 索引：快速查找配置
    __table_args__ = (
        Index('idx_key', 'key'),
    )

    def __repr__(self):
        return f"<UserPreferences(key='{self.key}', value='{self.value[:30]}...')>"

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
