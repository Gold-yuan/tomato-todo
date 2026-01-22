"""
PomodoroService集成测试

测试完整的番茄时钟工作流
"""
import pytest
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent.parent / 'src'
import sys
sys.path.insert(0, str(src_path))

from services import PomodoroService
from models import PomodoroTimer, PomodoroStats


class TestPomodoroWorkflow:
    """测试完整番茄时钟工作流"""

    def test_complete_workflow(self, db_session):
        """测试完整工作流：设置→开始→暂停→继续→完成→自动切换"""
        service = PomodoroService(db_session)

        # 1. 开始25分钟工作番茄
        timer = service.start_timer(1500, 'work')
        db_session.commit()
        assert timer.status == 'running'
        assert timer.remaining_seconds == 1500

        # 2. 暂停
        timer = service.pause_timer()
        db_session.commit()
        assert timer.status == 'paused'

        # 3. 继续
        timer = service.resume_timer()
        db_session.commit()
        assert timer.status == 'running'

        # 4. 停止并快速完成（模拟60秒）
        service.stop_timer()
        db_session.commit()
        service.start_timer(60, 'work')
        db_session.commit()
        for _ in range(60):
            service.tick()
        db_session.commit()

        # 5. 验证统计已保存
        stats = db_session.query(PomodoroStats).filter_by(mode='work').all()
        assert len(stats) == 1

        # 6. 验证自动切换到休息模式
        timer = service.get_current_timer()
        assert timer is not None
        assert timer.mode == 'break'
        assert timer.duration_seconds == 300
        assert timer.status == 'stopped'

    def test_multiple_pomodoros(self, db_session):
        """测试多个连续番茄"""
        service = PomodoroService(db_session)

        # 完成第一个工作番茄
        service.start_timer(60, 'work')
        for _ in range(60):
            service.tick()

        # 完成休息
        service.start_timer(60, 'break')
        for _ in range(60):
            service.tick()

        # 完成第二个工作番茄
        service.start_timer(60, 'work')
        for _ in range(60):
            service.tick()

        db_session.commit()

        # 验证统计
        work_stats = db_session.query(PomodoroStats).filter_by(mode='work').all()
        break_stats = db_session.query(PomodoroStats).filter_by(mode='break').all()

        assert len(work_stats) == 2
        assert len(break_stats) == 1

        # 验证统计数据
        stats = service.get_stats()
        assert stats['total_completed'] == 2
        assert stats['today_completed'] == 2
        assert stats['today_breaks'] == 1

    def test_stop_and_restart(self, db_session):
        """测试停止并重新启动"""
        service = PomodoroService(db_session)

        # 启动并停止
        service.start_timer(1500, 'work')
        timer = service.stop_timer()
        db_session.commit()
        assert timer.status == 'stopped'

        # 重新启动
        timer = service.start_timer(1800, 'work')
        db_session.commit()
        assert timer.status == 'running'
        assert timer.duration_seconds == 1800

    def test_pause_resume_multiple_times(self, db_session):
        """测试多次暂停和继续"""
        service = PomodoroService(db_session)

        service.start_timer(1500, 'work')
        db_session.commit()

        # 多次暂停和继续
        for _ in range(3):
            service.pause_timer()
            db_session.commit()
            assert service.get_current_timer().status == 'paused'

            service.resume_timer()
            db_session.commit()
            assert service.get_current_timer().status == 'running'

    def test_recovery_after_crash(self, db_session):
        """测试崩溃后恢复"""
        service = PomodoroService(db_session)

        # 启动计时器
        service.start_timer(1500, 'work')
        db_session.commit()

        # 模拟崩溃：创建新服务实例
        service2 = PomodoroService(db_session)
        timer = service2.get_current_timer()

        assert timer is not None
        assert timer.status == 'running'

    def test_stats_aggregation(self, db_session):
        """测试统计数据聚合"""
        service = PomodoroService(db_session)

        # 完成3个工作番茄和3个休息
        for _ in range(3):
            service.start_timer(60, 'work')
            for _ in range(60):
                service.tick()

            service.start_timer(60, 'break')
            for _ in range(60):
                service.tick()

        db_session.commit()

        stats = service.get_stats()
        assert stats['total_completed'] == 3
        assert stats['today_completed'] == 3
        assert stats['week_completed'] == 3
        assert stats['today_breaks'] == 3
        assert stats['week_breaks'] == 3

    def test_auto_rotation_cycle(self, db_session):
        """测试工作-休息自动轮询"""
        service = PomodoroService(db_session)

        # 工作 -> 休息 -> 工作 -> 休息
        for i in range(2):
            # 工作
            service.start_timer(60, 'work')
            assert service.get_current_timer().mode == 'work'
            for _ in range(60):
                service.tick()

            # 验证切换到休息
            timer = service.get_current_timer()
            assert timer.mode == 'break'
            assert timer.duration_seconds == 300

            # 休息
            service.start_timer(60, 'break')
            for _ in range(60):
                service.tick()

            # 验证切换到工作
            timer = service.get_current_timer()
            assert timer.mode == 'work'
            assert timer.duration_seconds == 1500

        db_session.commit()

        # 验证统计
        work_stats = db_session.query(PomodoroStats).filter_by(mode='work').count()
        break_stats = db_session.query(PomodoroStats).filter_by(mode='break').count()

        assert work_stats == 2
        assert break_stats == 2

    def test_tick_only_updates_running_timer(self, db_session):
        """测试tick只更新运行中的计时器"""
        service = PomodoroService(db_session)

        service.start_timer(1500, 'work')
        db_session.commit()

        # 暂停后tick不更新
        service.pause_timer()
        initial_remaining = service.get_current_timer().remaining_seconds
        service.tick()
        assert service.get_current_timer().remaining_seconds == initial_remaining

        # 停止后tick不更新
        service.stop_timer()
        service.tick()
        assert service.get_current_timer().remaining_seconds == 1500
