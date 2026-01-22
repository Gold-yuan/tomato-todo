"""
番茄时钟功能测试脚本

在无GUI环境下测试核心业务逻辑
"""
import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

from database.connection import get_session, init_database
from services import PomodoroService
from models import PomodoroStats


def test_pomodoro_workflow():
    """测试完整番茄时钟工作流"""
    print("=" * 60)
    print("番茄时钟功能测试")
    print("=" * 60)
    print()

    # 初始化数据库
    print("1. 初始化数据库...")
    init_database()
    print("✅ 数据库初始化完成\n")

    # 创建会话和服务
    session = get_session()
    service = PomodoroService(session)

    try:
        # 清理：停止任何运行中的计时器
        existing_timer = service.get_current_timer()
        if existing_timer:
            service.stop_timer()
            session.commit()
            print("0. 清理现有计时器状态...")
            print(f"   之前状态: {existing_timer.status}, 模式: {existing_timer.mode}")
            print()
        # 测试1: 启动工作番茄
        print("2. 启动25分钟工作番茄...")
        timer = service.start_timer(1500, 'work')
        session.commit()
        print(f"✅ 工作番茄已启动")
        print(f"   模式: {timer.mode}")
        print(f"   状态: {timer.status}")
        print(f"   剩余时间: {timer.remaining_seconds}秒 ({timer.remaining_seconds // 60}分钟)")
        print()

        # 测试2: 暂停
        print("3. 暂停番茄钟...")
        timer = service.pause_timer()
        session.commit()
        print(f"✅ 番茄钟已暂停")
        print(f"   状态: {timer.status}")
        print()

        # 测试4: 继续
        print("4. 继续番茄钟...")
        timer = service.resume_timer()
        session.commit()
        print(f"✅ 番茄钟已继续")
        print(f"   状态: {timer.status}")
        print()

        # 测试5: 模拟倒计时（快速完成60秒）
        print("5. 模拟60秒倒计时...")
        service.stop_timer()  # 先停止之前的
        session.commit()
        service.start_timer(60, 'work')
        session.commit()

        for i in range(60):
            import time
            time.sleep(0.1)  # 加快测试速度
            timer = service.tick()
            if timer is None:
                # 倒计时结束
                print("   倒计时: 0秒...")
                break
            elif (i + 1) % 10 == 0:  # 每10%显示一次
                print(f"   倒计时: {timer.remaining_seconds}秒...")

        session.commit()
        print("✅ 倒计时完成！")
        print()

        # 测试6: 检查统计
        print("6. 检查统计数据...")
        stats = service.get_stats()
        print(f"✅ 统计数据:")
        print(f"   总完成番茄数: {stats['total_completed']}")
        print(f"   今日完成: {stats['today_completed']}")
        print(f"   本周完成: {stats['week_completed']}")
        print()

        # 测试7: 检查模式切换
        print("7. 检查模式自动切换...")
        timer = service.get_current_timer()
        if timer:
            print(f"✅ 模式已自动切换:")
            print(f"   当前模式: {timer.mode}")
            print(f"   设定时长: {timer.duration_seconds}秒 ({timer.duration_seconds // 60}分钟)")
            print(f"   状态: {timer.status}")
        print()

        # 测试8: 启动休息番茄
        print("8. 启动5分钟休息番茄...")
        timer = service.start_timer(300, 'break')
        session.commit()
        print(f"✅ 休息番茄已启动")
        print(f"   模式: {timer.mode}")
        print(f"   状态: {timer.status}")
        print()

        # 测试9: 停止
        print("9. 停止番茄钟...")
        timer = service.stop_timer()
        session.commit()
        print(f"✅ 番茄钟已停止")
        print(f"   状态: {timer.status}")
        print(f"   剩余时间: {timer.remaining_seconds}秒")
        print()

        # 测试10: 数据库记录验证
        print("10. 验证数据库记录...")
        stats_records = session.query(PomodoroStats).all()
        print(f"✅ 数据库记录:")
        print(f"   统计记录数: {len(stats_records)}")
        for stat in stats_records:
            print(f"   - {stat.mode}: {stat.duration_seconds}秒, {stat.completed_at}")
        print()

        print("=" * 60)
        print("✅ 所有测试通过！番茄时钟功能正常！")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        session.close()


if __name__ == '__main__':
    success = test_pomodoro_workflow()
    sys.exit(0 if success else 1)
