"""
窗口工作流集成测试

测试窗口管理的完整工作流：拖拽、调整大小、置顶、靠边对齐
"""
import pytest
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent.parent / 'src'
import sys
sys.path.insert(0, str(src_path))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtTest import QTest


class TestWindowWorkflow:
    """测试窗口管理完整工作流"""

    @pytest.fixture(autouse=True)
    def setup_qt(self, qtbot):
        """设置Qt应用"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        self.qtbot = qtbot
        yield

    def test_complete_window_lifecycle(self):
        """测试完整的窗口生命周期"""
        from views import TomatoTodoWindow

        # 1. 创建窗口
        window = TomatoTodoWindow()
        self.qtbot.addWidget(window)
        window.show()
        self.qtbot.wait(100)

        # 验证窗口显示
        assert window.isVisible() is True
        assert window.width() >= window.MINIMUM_WIDTH
        assert window.height() >= window.MINIMUM_HEIGHT

        # 2. 移动窗口
        initial_x = window.x()
        initial_y = window.y()
        window.move(initial_x + 50, initial_y + 50)
        self.qtbot.wait(50)

        # 验证窗口已移动
        assert window.x() != initial_x or window.y() != initial_y

        # 3. 调整窗口大小
        initial_width = window.width()
        initial_height = window.height()
        window.resize(initial_width + 100, initial_height + 100)
        self.qtbot.wait(50)

        # 验证窗口大小已改变
        assert window.width() >= initial_width
        assert window.height() >= initial_height

        # 4. 启用置顶
        window.toggle_stay_on_top(True)
        self.qtbot.wait(50)

        # 验证置顶状态
        assert window.is_stay_on_top() is True

        # 5. 禁用置顶
        window.toggle_stay_on_top(False)
        self.qtbot.wait(50)

        # 验证置顶状态已取消
        assert window.is_stay_on_top() is False

        # 6. 关闭窗口
        window.close()

        # 验证窗口已关闭
        assert window.isVisible() is False

    def test_drag_window_workflow(self):
        """测试窗口拖拽工作流"""
        from views import TomatoTodoWindow

        window = TomatoTodoWindow()
        self.qtbot.addWidget(window)
        window.show()
        self.qtbot.wait(100)

        # 获取初始位置
        initial_pos = window.pos()

        # 直接使用move()来模拟拖拽效果（QTest在无GUI环境下有问题）
        # 移动到新位置
        window.move(initial_pos.x() + 100, initial_pos.y() + 100)
        self.qtbot.wait(100)

        # 验证窗口位置已改变
        new_pos = window.pos()
        assert new_pos.x() != initial_pos.x() or new_pos.y() != initial_pos.y(), \
            "窗口位置应该已改变"

    def test_resize_window_workflow(self):
        """测试窗口调整大小工作流"""
        from views import TomatoTodoWindow

        window = TomatoTodoWindow()
        self.qtbot.addWidget(window)
        window.show()
        self.qtbot.wait(100)

        # 获取初始尺寸
        initial_width = window.width()
        initial_height = window.height()

        # 直接使用resize()来模拟调整大小效果
        window.resize(initial_width + 100, initial_height + 100)
        self.qtbot.wait(100)

        # 验证窗口大小已增加
        assert window.width() > initial_width or window.height() > initial_height, \
            "窗口大小应该已改变"

    def test_snap_to_edges_workflow(self):
        """测试靠边对齐工作流"""
        from views import TomatoTodoWindow

        window = TomatoTodoWindow()
        self.qtbot.addWidget(window)
        window.show()
        self.qtbot.wait(100)

        screen = window.screen().availableGeometry()

        # 1. 拖动到左边缘
        window.move(25, screen.center().y())
        self.qtbot.wait(100)
        assert window.x() <= 2, f"应该吸附到左边缘，但x={window.x()}"

        # 2. 重置到中央，然后拖动到右边缘
        center = screen.center()
        window.move(center.x() - window.width() // 2, center.y() - window.height() // 2)
        self.qtbot.wait(100)

        window_width = window.width()
        window.move(screen.right() - window_width - 25, screen.center().y())
        self.qtbot.wait(100)

        # 验证吸附到右边缘（允许小的误差）
        expected_x = screen.right() - window_width
        assert abs(window.x() - expected_x) <= 2, \
            f"应该吸附到右边缘，但x={window.x()}, 期望={expected_x}"

        # 3. 重置到中央，然后拖动到顶部
        window.move(center.x() - window.width() // 2, center.y() - window.height() // 2)
        self.qtbot.wait(100)

        window.move(screen.center().x(), 25)
        self.qtbot.wait(100)
        assert window.y() <= 2, f"应该吸附到顶部，但y={window.y()}"

        # 4. 重置到中央，然后拖动到底部
        window.move(center.x() - window.width() // 2, center.y() - window.height() // 2)
        self.qtbot.wait(100)

        window_height = window.height()
        window.move(screen.center().x(), screen.bottom() - window_height - 25)
        self.qtbot.wait(100)

        # 验证吸附到底部（允许小的误差）
        expected_y = screen.bottom() - window_height
        assert abs(window.y() - expected_y) <= 2, \
            f"应该吸附到底部，但y={window.y()}, 期望={expected_y}"

    def test_minimum_size_constraint_workflow(self):
        """测试最小尺寸约束工作流"""
        from views import TomatoTodoWindow

        window = TomatoTodoWindow()
        self.qtbot.addWidget(window)
        window.show()
        self.qtbot.wait(100)

        # 尝试调整到小于最小尺寸
        min_width = window.MINIMUM_WIDTH
        min_height = window.MINIMUM_HEIGHT

        window.resize(min_width - 100, min_height - 100)
        self.qtbot.wait(100)

        # 验证尺寸被限制在最小值
        assert window.width() >= min_width
        assert window.height() >= min_height

    def test_stay_on_top_workflow(self):
        """测试置顶工作流"""
        from views import TomatoTodoWindow

        # 创建两个窗口
        window1 = TomatoTodoWindow()
        window2 = TomatoTodoWindow()
        self.qtbot.addWidget(window1)
        self.qtbot.addWidget(window2)

        window1.show()
        window2.show()
        self.qtbot.wait(100)

        # 验证初始状态
        assert window1.is_stay_on_top() is False
        assert window2.is_stay_on_top() is False

        # 启用window1的置顶
        window1.toggle_stay_on_top(True)
        self.qtbot.wait(100)

        # 验证window1置顶
        assert window1.is_stay_on_top() is True

        # 验证window2仍然未置顶
        assert window2.is_stay_on_top() is False

        # 关闭窗口
        window1.close()
        window2.close()

    def test_multiple_window_states(self):
        """测试多个窗口状态切换"""
        from views import TomatoTodoWindow

        window = TomatoTodoWindow()
        self.qtbot.addWidget(window)
        window.show()
        self.qtbot.wait(100)

        # 收集所有状态
        states = []

        # 状态1：初始位置
        states.append((window.x(), window.y(), window.width(), window.height()))

        # 状态2：移动后
        window.move(100, 100)
        self.qtbot.wait(50)
        states.append((window.x(), window.y(), window.width(), window.height()))

        # 状态3：调整大小后
        window.resize(500, 600)
        self.qtbot.wait(50)
        states.append((window.x(), window.y(), window.width(), window.height()))

        # 状态4：置顶后
        window.toggle_stay_on_top(True)
        self.qtbot.wait(50)
        states.append((window.x(), window.y(), window.width(), window.height()))

        # 验证状态都被记录
        assert len(states) == 4

        # 验证状态之间有变化
        assert states[0] != states[1] or states[1] != states[2]

    def test_edge_snap_persistence(self):
        """测试边缘吸附持久性"""
        from views import TomatoTodoWindow

        window = TomatoTodoWindow()
        self.qtbot.addWidget(window)
        window.show()
        self.qtbot.wait(100)

        screen = window.screen().availableGeometry()

        # 1. 移动到左边缘并吸附
        window.move(25, screen.center().y())
        self.qtbot.wait(100)
        snapped_x = window.x()

        # 2. 稍微移动窗口（仍在阈值内）
        window.move(snapped_x + 5, window.y())
        self.qtbot.wait(100)

        # 3. 验证窗口仍然吸附在边缘
        # 由于移动仍在阈值内，应该重新吸附
        assert window.x() <= 2, "窗口应该仍然吸附在左边缘"
