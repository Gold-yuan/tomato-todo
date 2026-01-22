"""
窗口行为单元测试

测试窗口最小尺寸限制和靠边对齐功能
"""
import pytest
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent.parent / 'src'
import sys
sys.path.insert(0, str(src_path))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QScreen
import sys


class TestWindowMinimumSize:
    """测试窗口最小尺寸限制"""

    @pytest.fixture(autouse=True)
    def setup_qt(self):
        """设置Qt应用"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        yield
        # 清理由pytest-qt处理

    def test_minimum_width_constraint(self, qtbot):
        """测试最小宽度约束"""
        from views import TomatoTodoWindow

        window = TomatoTodoWindow()
        qtbot.addWidget(window)

        # 获取最小宽度
        min_width = window.minimumWidth()
        min_height = window.minimumHeight()

        # 验证最小尺寸存在且大于0
        assert min_width > 0, "窗口应该有最小宽度限制"
        assert min_height > 0, "窗口应该有最小高度限制"

        # 验证合理的最小尺寸（至少能容纳时钟和部分TodoList）
        assert min_width >= 350, "最小宽度应该至少350px以容纳内容"
        assert min_height >= 400, "最小高度应该至少400px以容纳时钟和部分任务列表"

    def test_cannot_resize_below_minimum(self, qtbot):
        """测试无法调整到最小尺寸以下"""
        from views import TomatoTodoWindow

        window = TomatoTodoWindow()
        qtbot.addWidget(window)
        window.show()

        # 获取最小尺寸
        min_width = window.minimumWidth()
        min_height = window.minimumHeight()

        # 尝试设置更小的尺寸
        window.resize(min_width - 50, min_height - 50)

        # 验证尺寸没有被设置到最小值以下
        assert window.width() >= min_width, "窗口宽度不应该小于最小宽度"
        assert window.height() >= min_height, "窗口高度不应该小于最小高度"

    def test_resize_event_enforces_minimum(self, qtbot):
        """测试resize事件强制执行最小尺寸"""
        from views import TomatoTodoWindow

        window = TomatoTodoWindow()
        qtbot.addWidget(window)
        window.show()

        min_width = window.minimumWidth()
        min_height = window.minimumHeight()

        # 触发resize事件
        from PyQt6.QtCore import QSize
        window.resize(QSize(min_width - 100, min_height - 100))

        # 验证尺寸被限制在最小值
        assert window.width() >= min_width
        assert window.height() >= min_height


class TestWindowSnapping:
    """测试窗口靠边对齐功能"""

    @pytest.fixture(autouse=True)
    def setup_qt(self):
        """设置Qt应用"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()

        # 获取屏幕尺寸
        self.screen = QApplication.primaryScreen()
        self.screen_geometry = self.screen.availableGeometry()
        yield

    def test_snap_to_left_edge(self, qtbot):
        """测试吸附到屏幕左边缘"""
        from views import TomatoTodoWindow

        window = TomatoTodoWindow()
        qtbot.addWidget(window)
        window.show()

        # 获取吸附阈值
        snap_threshold = window.snap_threshold if hasattr(window, 'snap_threshold') else 30

        # 将窗口移动到接近左边缘的位置
        target_x = snap_threshold - 5  # 在阈值内
        target_y = self.screen_geometry.center().y()
        window.move(target_x, target_y)

        # 验证窗口吸附到边缘（x坐标应该为0）
        assert window.x() == 0, "窗口应该吸附到屏幕左边缘"

    def test_snap_to_right_edge(self, qtbot):
        """测试吸附到屏幕右边缘"""
        from views import TomatoTodoWindow

        window = TomatoTodoWindow()
        qtbot.addWidget(window)
        window.show()

        # 等待窗口显示
        qtbot.wait(100)

        snap_threshold = window.snap_threshold if hasattr(window, 'snap_threshold') else 30

        # 将窗口移动到接近右边缘的位置
        window_width = window.width()
        target_x = self.screen_geometry.right() - window_width - snap_threshold + 5
        target_y = self.screen_geometry.center().y()
        window.move(target_x, target_y)

        # 等待moveEvent处理完成
        qtbot.wait(100)

        # 验证窗口吸附到右边缘（允许小的误差）
        expected_x = self.screen_geometry.right() - window_width
        # 窗口管理器可能有小的调整，允许2像素误差
        assert abs(window.x() - expected_x) <= 2, \
            f"窗口应该吸附到屏幕右边缘，但x={window.x()}, 期望={expected_x}"

    def test_snap_to_top_edge(self, qtbot):
        """测试吸附到屏幕顶部"""
        from views import TomatoTodoWindow

        window = TomatoTodoWindow()
        qtbot.addWidget(window)
        window.show()
        qtbot.wait(100)

        snap_threshold = window.snap_threshold if hasattr(window, 'snap_threshold') else 30

        # 将窗口移动到接近顶部的位置
        target_x = self.screen_geometry.center().x() - window.width() // 2
        target_y = snap_threshold - 5
        window.move(target_x, target_y)
        qtbot.wait(100)

        # 验证窗口吸附到顶部（允许小的误差）
        assert window.y() <= 2, f"窗口应该吸附到屏幕顶部，但y={window.y()}"

    def test_snap_to_bottom_edge(self, qtbot):
        """测试吸附到屏幕底部"""
        from views import TomatoTodoWindow

        window = TomatoTodoWindow()
        qtbot.addWidget(window)
        window.show()
        qtbot.wait(100)

        snap_threshold = window.snap_threshold if hasattr(window, 'snap_threshold') else 30

        # 将窗口移动到接近底部的位置
        window_height = window.height()
        target_x = self.screen_geometry.center().x() - window.width() // 2
        target_y = self.screen_geometry.bottom() - window_height - snap_threshold + 5
        window.move(target_x, target_y)
        qtbot.wait(100)

        # 验证窗口吸附到底部（允许小的误差）
        expected_y = self.screen_geometry.bottom() - window_height
        assert abs(window.y() - expected_y) <= 2, \
            f"窗口应该吸附到屏幕底部，但y={window.y()}, 期望={expected_y}"

    def test_no_snap_when_far_from_edge(self, qtbot):
        """测试远离边缘时不吸附"""
        from views import TomatoTodoWindow

        window = TomatoTodoWindow()
        qtbot.addWidget(window)
        window.show()
        qtbot.wait(100)

        snap_threshold = window.snap_threshold if hasattr(window, 'snap_threshold') else 30

        # 将窗口移动到屏幕中央（远离边缘）
        center = self.screen_geometry.center()
        target_x = center.x() - window.width() // 2
        target_y = center.y() - window.height() // 2
        window.move(target_x, target_y)
        qtbot.wait(100)

        # 验证窗口位置保持不变（不吸附，允许小的误差）
        assert abs(window.x() - target_x) < 10, \
            f"远离边缘时窗口应该保持原位置，但x={window.x()}, 期望={target_x}"
        assert abs(window.y() - target_y) < 10, \
            f"远离边缘时窗口应该保持原位置，但y={window.y()}, 期望={target_y}"

    def test_snap_threshold_is_reasonable(self, qtbot):
        """测试吸附阈值是否合理"""
        from views import TomatoTodoWindow

        window = TomatoTodoWindow()
        qtbot.addWidget(window)
        window.show()

        # 验证吸附阈值存在且合理
        if hasattr(window, 'snap_threshold'):
            threshold = window.snap_threshold
            assert 10 <= threshold <= 50, "吸附阈值应该在10-50像素之间"
        else:
            # 如果没有明确的阈值属性，测试默认行为
            pytest.skip("窗口没有明确的snap_threshold属性")


class TestWindowDragAndResize:
    """测试窗口拖拽和调整大小"""

    @pytest.fixture(autouse=True)
    def setup_qt(self):
        """设置Qt应用"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        yield

    def test_window_is_resizable(self, qtbot):
        """测试窗口可以调整大小"""
        from views import TomatoTodoWindow

        window = TomatoTodoWindow()
        qtbot.addWidget(window)
        window.show()

        initial_width = window.width()
        initial_height = window.height()

        # 增加窗口大小
        new_width = initial_width + 100
        new_height = initial_height + 100
        window.resize(new_width, new_height)

        # 验证大小已改变
        assert window.width() == new_width, "窗口宽度应该可以调整"
        assert window.height() == new_height, "窗口高度应该可以调整"

    def test_window_is_movable(self, qtbot):
        """测试窗口可以移动"""
        from views import TomatoTodoWindow

        window = TomatoTodoWindow()
        qtbot.addWidget(window)
        window.show()

        initial_x = window.x()
        initial_y = window.y()

        # 移动窗口
        new_x = initial_x + 50
        new_y = initial_y + 50
        window.move(new_x, new_y)

        # 验证位置已改变
        assert window.x() == new_x, "窗口应该可以水平移动"
        assert window.y() == new_y, "窗口应该可以垂直移动"


class TestWindowStayOnTop:
    """测试窗口置顶功能"""

    @pytest.fixture(autouse=True)
    def setup_qt(self):
        """设置Qt应用"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        yield

    def test_toggle_stay_on_top(self, qtbot):
        """测试切换置顶状态"""
        from views import TomatoTodoWindow

        window = TomatoTodoWindow()
        qtbot.addWidget(window)
        window.show()

        # 检查是否有切换置顶的方法
        if hasattr(window, 'toggle_stay_on_top'):
            initial_flags = window.windowFlags()

            # 切换到置顶
            window.toggle_stay_on_top(True)
            assert window.windowFlags() & Qt.WindowType.WindowStaysOnTopHint, \
                "启用置顶后应该有WindowStaysOnTopHint标志"

            # 取消置顶
            window.toggle_stay_on_top(False)
            assert not (window.windowFlags() & Qt.WindowType.WindowStaysOnTopHint), \
                "禁用置顶后不应该有WindowStaysOnTopHint标志"
        else:
            pytest.skip("窗口没有toggle_stay_on_top方法")

    def test_stay_on_top_persists(self, qtbot):
        """测试置顶状态持久化"""
        from views import TomatoTodoWindow

        window = TomatoTodoWindow()
        qtbot.addWidget(window)
        window.show()

        if hasattr(window, 'toggle_stay_on_top') and hasattr(window, 'is_stay_on_top'):
            # 启用置顶
            window.toggle_stay_on_top(True)

            # 验证状态被保存
            assert window.is_stay_on_top() is True, "置顶状态应该被保存"

            # 禁用置顶
            window.toggle_stay_on_top(False)

            # 验证状态被更新
            assert window.is_stay_on_top() is False, "置顶状态应该被更新"
        else:
            pytest.skip("窗口缺少必要的方法")
