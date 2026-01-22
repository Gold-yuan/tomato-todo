"""
用户偏好服务

封装用户偏好的业务逻辑
"""
from typing import Any, Dict
from sqlalchemy.orm import Session
from database.repositories import PreferencesRepository


class PreferencesService:
    """用户偏好服务"""

    def __init__(self, session: Session):
        """
        初始化服务

        Args:
            session: SQLAlchemy会话
        """
        self.session = session
        self.repository = PreferencesRepository(session)

    def get_preference(self, key: str, default: Any = None) -> Any:
        """
        获取偏好配置

        Args:
            key: 配置键
            default: 默认值（如果不存在）

        Returns:
            配置值（已解析JSON）
        """
        value_str = self.repository.get(key)
        if value_str is None:
            return default

        try:
            import json
            return json.loads(value_str)
        except Exception:
            # 如果JSON解析失败，返回原始字符串
            return value_str

    def set_preference(self, key: str, value: Any) -> None:
        """
        设置偏好配置

        Args:
            key: 配置键
            value: 配置值（自动序列化为JSON）

        Raises:
            ValueError: 如果值无法序列化为JSON
        """
        try:
            self.repository.set(key, value)
        except Exception as e:
            raise ValueError(f"无法序列化配置值: {e}")

    def set_preferences(self, preferences: Dict[str, Any]) -> None:
        """
        批量设置偏好配置

        Args:
            preferences: 配置字典

        Raises:
            ValueError: 如果任何值无法序列化为JSON
        """
        for key, value in preferences.items():
            self.set_preference(key, value)

    def get_all_preferences(self) -> Dict[str, Any]:
        """
        获取所有偏好配置

        Returns:
            配置字典
        """
        return self.repository.get_all()
