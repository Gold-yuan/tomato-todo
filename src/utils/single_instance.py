"""
单实例管理

使用QLockFile确保同一时间只运行一个应用实例
"""
import sys
from PyQt6.QtCore import QLockFile, qDebug
from PyQt6.QtWidgets import QMessageBox
from utils.constants import LOCK_FILE_PATH


class SingleInstanceManager:
    """单实例管理器"""

    def __init__(self, lock_path: str = LOCK_FILE_PATH):
        """
        初始化单实例管理器

        Args:
            lock_path: 锁文件路径
        """
        self.lock_path = lock_path
        self.lock_file = QLockFile(lock_path)
        self.lock_file.setStaleLockTime(0)  # 不自动清理旧锁

    def try_lock(self) -> bool:
        """
        尝试获取锁，启动单实例

        Returns:
            bool: 成功获取锁返回True，否则返回False
        """
        if self.lock_file.tryLock(10):  # 等待10毫秒
            return True
        else:
            return False

    def unlock(self):
        """释放锁"""
        if self.lock_file.isLocked():
            self.lock_file.unlock()

    def show_already_running_message(self):
        """显示已有实例运行的提示"""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle("番茄时钟")
        msg_box.setText("应用已在运行")
        msg_box.setInformativeText("请在任务栏中找到已运行的窗口")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def __enter__(self):
        """上下文管理器入口"""
        self.try_lock()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.unlock()
        return False
