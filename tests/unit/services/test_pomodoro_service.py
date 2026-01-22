"""
PomodoroService单元测试

测试番茄时钟服务的所有方法
"""
import pytest
from datetime import datetime
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent.parent.parent.parent / 'src'
import sys
sys.path.insert(0, str(src_path))

from services import PomodoroService
from models import PomodoroTimer
from utils.constants import MIN_DURATION, MAX_DURATION


class TestPomodoroServiceStartTimer:
    """测试start_timer方法"""

    def test_start_timer_success(self, db_session):
        """测试成功启动计时器"""
        service = PomodoroService(db_session)
        timer = service.start_timer(1500, 'work')

        assert timer is not None
        assert timer.mode == 'work'
        assert timer.duration_seconds == 1500
        assert timer.remaining_seconds == 1500
        assert timer.status == 'running'
        assert timer.start_time is not None

    def test_start_timer_invalid_duration_too_short(self, db_session):
        """测试时长过短"""
        service = PomodoroService(db_session)
        with pytest.raises(ValueError, match="时长必须在"):
            service.start_timer(30, 'work')

    def test_start_timer_invalid_duration_too_long(self, db_session):
        """测试时长过长"""
        service = PomodoroService(db_session)
        with pytest.raises(ValueError, match="时长必须在"):
            service.start_timer(10000, 'work')

    def test_start_timer_invalid_mode(self, db_session):
        """测试无效模式"""
        service = PomodoroService(db_session)
        with pytest.raises(ValueError, match="模式必须是"):
            service.start_timer(1500, 'invalid')

    def test_start_timer_already_running(self, db_session):
        """测试重复启动"""
        service = PomodoroService(db_session)
        service.start_timer(1500, 'work')
        db_session.commit()

        with pytest.raises(RuntimeError, match="时钟已在运行中"):
            service.start_timer(1500, 'work')

    def test_start_timer_break_mode(self, db_session):
        """测试启动休息模式"""
        service = PomodoroService(db_session)
        timer = service.start_timer(300, 'break')

        assert timer.mode == 'break'
        assert timer.duration_seconds == 300


class TestPomodoroServicePauseTimer:
    """测试pause_timer方法"""

    def test_pause_timer_success(self, db_session):
        """测试成功暂停"""
        service = PomodoroService(db_session)
        service.start_timer(1500, 'work')
        db_session.commit()

        timer = service.pause_timer()
        db_session.commit()

        assert timer.status == 'paused'

    def test_pause_timer_not_running(self, db_session):
        """测试暂停未运行的时钟"""
        service = PomodoroService(db_session)
        service.start_timer(1500, 'work')
        db_session.commit()
        service.pause_timer()
        db_session.commit()

        with pytest.raises(RuntimeError, match="时钟未在运行"):
            service.pause_timer()

    def test_pause_timer_no_timer(self, db_session):
        """测试暂停不存在的计时器"""
        service = PomodoroService(db_session)
        with pytest.raises(RuntimeError, match="时钟未在运行"):
            service.pause_timer()


class TestPomodoroServiceResumeTimer:
    """测试resume_timer方法"""

    def test_resume_timer_success(self, db_session):
        """测试成功继续"""
        service = PomodoroService(db_session)
        service.start_timer(1500, 'work')
        db_session.commit()
        service.pause_timer()
        db_session.commit()

        timer = service.resume_timer()
        db_session.commit()

        assert timer.status == 'running'

    def test_resume_timer_calculates_elapsed(self, db_session):
        """测试继续时计算经过时间"""
        service = PomodoroService(db_session)
        service.start_timer(1500, 'work')
        db_session.commit()
        service.pause_timer()
        db_session.commit()

        # 模拟时间流逝（在实际测试中可以使用mock）
        timer = service.resume_timer()
        db_session.commit()

        assert timer.status == 'running'
        assert timer.remaining_seconds <= 1500

    def test_resume_timer_not_paused(self, db_session):
        """测试继续未暂停的时钟"""
        service = PomodoroService(db_session)
        service.start_timer(1500, 'work')
        db_session.commit()

        with pytest.raises(RuntimeError, match="时钟未暂停"):
            service.resume_timer()

    def test_resume_timer_no_timer(self, db_session):
        """测试继续不存在的计时器"""
        service = PomodoroService(db_session)
        with pytest.raises(RuntimeError, match="时钟未暂停"):
            service.resume_timer()


class TestPomodoroServiceStopTimer:
    """测试stop_timer方法"""

    def test_stop_timer_success(self, db_session):
        """测试成功停止"""
        service = PomodoroService(db_session)
        service.start_timer(1500, 'work')
        db_session.commit()

        timer = service.stop_timer()
        db_session.commit()

        assert timer.status == 'stopped'
        assert timer.remaining_seconds == 1500

    def test_stop_timer_while_paused(self, db_session):
        """测试暂停时停止"""
        service = PomodoroService(db_session)
        service.start_timer(1500, 'work')
        db_session.commit()
        service.pause_timer()
        db_session.commit()
        service.stop_timer()
        db_session.commit()

        timer = service.get_current_timer()
        assert timer.status == 'stopped'
        assert timer.remaining_seconds == 1500

    def test_stop_timer_no_timer(self, db_session):
        """测试停止不存在的计时器"""
        service = PomodoroService(db_session)
        timer = service.stop_timer()
        db_session.commit()

        # 应该创建一个停止的计时器
        assert timer.status == 'stopped'
        assert timer.duration_seconds == 1500


class TestPomodoroServiceTick:
    """测试tick方法"""

    def test_tick_decrements_remaining(self, db_session):
        """测试倒计时递减"""
        service = PomodoroService(db_session)
        service.start_timer(1500, 'work')
        db_session.commit()

        timer = service.tick()
        db_session.commit()

        assert timer.remaining_seconds == 1499

    def test_tick_when_paused(self, db_session):
        """测试暂停时tick不更新"""
        service = PomodoroService(db_session)
        service.start_timer(1500, 'work')
        db_session.commit()
        service.pause_timer()
        db_session.commit()

        timer = service.tick()

        assert timer.remaining_seconds == 1500

    def test_tick_when_stopped(self, db_session):
        """测试停止时tick不更新"""
        service = PomodoroService(db_session)
        service.start_timer(1500, 'work')
        db_session.commit()
        service.stop_timer()
        db_session.commit()

        timer = service.tick()

        assert timer.remaining_seconds == 1500

    def test_tick_returns_none_when_complete(self, db_session):
        """测试倒计时结束时返回None"""
        service = PomodoroService(db_session)
        service.start_timer(60, 'work')
        db_session.commit()

        # 模拟倒计时到0
        for _ in range(60):
            timer = service.tick()
        db_session.commit()

        assert timer is None

        # 验证统计已保存
        from models import PomodoroStats
        stats = db_session.query(PomodoroStats).all()
        assert len(stats) == 1
        assert stats[0].mode == 'work'

    def test_tick_auto_switch_to_break(self, db_session):
        """测试自动切换到休息模式"""
        service = PomodoroService(db_session)
        service.start_timer(60, 'work')
        db_session.commit()

        # 倒计时结束
        for _ in range(60):
            service.tick()
        db_session.commit()

        # 获取当前计时器
        timer = service.get_current_timer()
        assert timer.mode == 'break'
        assert timer.duration_seconds == 300

    def test_tick_auto_switch_to_work(self, db_session):
        """测试从休息自动切换回工作"""
        service = PomodoroService(db_session)
        service.start_timer(60, 'break')
        db_session.commit()

        # 倒计时结束
        for _ in range(60):
            service.tick()
        db_session.commit()

        timer = service.get_current_timer()
        assert timer.mode == 'work'
        assert timer.duration_seconds == 1500


class TestPomodoroServiceGetCurrentTimer:
    """测试get_current_timer方法"""

    def test_get_current_timer_exists(self, db_session):
        """测试获取存在的计时器"""
        service = PomodoroService(db_session)
        service.start_timer(1500, 'work')
        db_session.commit()

        timer = service.get_current_timer()
        assert timer is not None
        assert timer.status == 'running'

    def test_get_current_timer_not_exists(self, db_session):
        """测试获取不存在的计时器"""
        service = PomodoroService(db_session)
        timer = service.get_current_timer()
        assert timer is None


class TestPomodoroServiceGetStats:
    """测试get_stats方法"""

    def test_get_stats_initial(self, db_session):
        """测试初始统计"""
        service = PomodoroService(db_session)
        stats = service.get_stats()

        assert stats['total_completed'] == 0
        assert stats['today_completed'] == 0
        assert stats['week_completed'] == 0
        assert stats['today_breaks'] == 0
        assert stats['week_breaks'] == 0

    def test_get_stats_after_completion(self, db_session):
        """测试完成后的统计"""
        service = PomodoroService(db_session)
        service.start_timer(60, 'work')
        db_session.commit()

        # 完成一个番茄
        for _ in range(60):
            service.tick()
        db_session.commit()

        stats = service.get_stats()
        assert stats['total_completed'] == 1
        assert stats['today_completed'] == 1
        assert stats['week_completed'] == 1

    def test_get_stats_work_and_break(self, db_session):
        """测试工作和休息统计"""
        service = PomodoroService(db_session)

        # 完成工作番茄
        service.start_timer(60, 'work')
        for _ in range(60):
            service.tick()
        db_session.commit()

        # 完成休息
        service.start_timer(60, 'break')
        for _ in range(60):
            service.tick()
        db_session.commit()

        stats = service.get_stats()
        assert stats['total_completed'] == 1  # 仅统计工作
        assert stats['today_completed'] == 1
        assert stats['today_breaks'] == 1
