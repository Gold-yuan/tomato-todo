"""
番茄时钟和TodoList桌面小组件 - 主应用入口

包含主窗口、单实例检测和状态恢复
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from database.connection import get_session
from services import PomodoroService
from views import PomodoroWidget
from controllers import PomodoroController
from utils.single_instance import SingleInstanceManager
from utils.constants import DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT


class TomatoTodoApp(QMainWindow):
    """番茄时钟应用主窗口"""

    def __init__(self):
        super().__init__()

        # 初始化数据库会话
        self.session = get_session()

        # 初始化服务
        self.pomodoro_service = PomodoroService(self.session)

        # 初始化UI
        self._init_ui()

        # 初始化控制器
        self._init_controllers()

        # 加载应用状态
        self._load_application_state()

    def _init_ui(self):
        """初始化UI"""
        # 设置窗口属性
        self.setWindowTitle("番茄时钟")
        self.setMinimumSize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)

        # 创建中央widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 创建番茄时钟组件
        self.pomodoro_widget = PomodoroWidget()
        main_layout.addWidget(self.pomodoro_widget)

        # TODO: 后续添加TodoList组件
        # todo_widget = TodoWidget()
        # main_layout.addWidget(todo_widget)

        central_widget.setLayout(main_layout)

        # 加载样式
        self._load_stylesheet()

    def _load_stylesheet(self):
        """加载QSS样式表"""
        style_path = Path(__file__).parent.parent / "assets" / "styles" / "main.qss"
        try:
            with open(style_path, "r", encoding="utf-8") as f:
                stylesheet = f.read()
                self.setStyleSheet(stylesheet)
        except Exception as e:
            print(f"加载样式表失败: {e}")

    def _init_controllers(self):
        """初始化控制器"""
        self.pomodoro_controller = PomodoroController(
            self.pomodoro_widget,
            self.pomodoro_service,
            self.session
        )

        # 连接完成信号
        self.pomodoro_controller.timer_completed.connect(self._on_timer_completed)

    def _load_application_state(self):
        """加载应用状态"""
        # TODO: 从用户偏好设置加载窗口位置和大小
        # TODO: 从单实例检测中获取冲突处理

        # 恢复番茄时钟状态
        timer = self.pomodoro_service.get_current_timer()
        if timer and timer.status == 'running':
            # 如果之前是运行状态，自动恢复（但不自动开始）
            # 用户需要手动点击开始
            pass

    def _on_timer_completed(self, mode: str):
        """处理计时器完成"""
        # TODO: 后续可以添加通知、声音等
        print(f"计时器完成: {mode}")

    def closeEvent(self, event):
        """关闭事件：清理资源"""
        # 清理控制器
        if hasattr(self, 'pomodoro_controller'):
            self.pomodoro_controller.cleanup()

        # 关闭数据库会话
        if self.session:
            self.session.close()

        super().closeEvent(event)


def main():
    """主函数"""
    # 单实例检测
    lock_manager = SingleInstanceManager()

    if not lock_manager.try_lock():
        # 已有实例在运行
        lock_manager.show_already_running_message()
        sys.exit(1)

    try:
        # 创建应用
        app = QApplication(sys.argv)
        app.setApplicationName("番茄时钟")
        app.setOrganizationName("TomatoTodo")

        # 创建主窗口
        window = TomatoTodoApp()
        window.show()

        # 运行应用
        sys.exit(app.exec())

    except Exception as e:
        print(f"应用启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        # 释放锁
        lock_manager.unlock()


if __name__ == '__main__':
    main()
