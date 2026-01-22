"""
用户偏好数据仓库

处理用户偏好相关的数据库操作
"""
import json
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from models import UserPreferences


class PreferencesRepository:
    """用户偏好数据仓库"""

    def __init__(self, session: Session):
        """
        初始化仓库

        Args:
            session: SQLAlchemy会话
        """
        self.session = session

    def get(self, key: str) -> Optional[str]:
        """
        获取偏好配置值（JSON字符串）

        Args:
            key: 配置键

        Returns:
            配置值（JSON字符串）或None
        """
        pref = self.session.query(UserPreferences).filter(
            UserPreferences.key == key
        ).first()
        return pref.value if pref else None

    def set(self, key: str, value: Any) -> UserPreferences:
        """
        设置偏好配置

        Args:
            key: 配置键
            value: 配置值（会自动序列化为JSON字符串）

        Returns:
            保存后的偏好对象
        """
        # 序列化为JSON
        json_value = json.dumps(value, ensure_ascii=False)

        # 查找是否已存在
        pref = self.session.query(UserPreferences).filter(
            UserPreferences.key == key
        ).first()

        if pref:
            # 更新
            pref.value = json_value
        else:
            # 新建
            pref = UserPreferences(key=key, value=json_value)
            self.session.add(pref)

        return pref

    def get_all(self) -> Dict[str, Any]:
        """
        获取所有偏好配置

        Returns:
            配置字典（值已解析为实际类型）
        """
        prefs = self.session.query(UserPreferences).all()
        result = {}
        for pref in prefs:
            try:
                result[pref.key] = json.loads(pref.value)
            except json.JSONDecodeError:
                # 如果JSON解析失败，返回原始字符串
                result[pref.key] = pref.value
        return result

    def delete(self, key: str) -> bool:
        """
        删除偏好配置

        Args:
            key: 配置键

        Returns:
            成功返回True
        """
        pref = self.session.query(UserPreferences).filter(
            UserPreferences.key == key
        ).first()
        if pref:
            self.session.delete(pref)
            return True
        return False
