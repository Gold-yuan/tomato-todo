"""
数据库初始化脚本

用于创建数据库表和预置数据
"""
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.connection import init_database, get_db_path, get_app_dir


def main():
    """主函数"""
    print("=" * 50)
    print("番茄时钟 - 数据库初始化")
    print("=" * 50)
    print()

    # 显示路径信息
    print(f"应用目录: {get_app_dir()}")
    print(f"数据库路径: {get_db_path()}")
    print()

    # 初始化数据库
    print("正在初始化数据库...")
    try:
        init_database()
        print("✅ 数据库初始化成功！")
        print()
        print("已创建的表:")
        print("  - pomodoro_timer   (番茄时钟状态表)")
        print("  - pomodoro_stats   (番茄时钟统计表)")
        print("  - todo_tasks       (Todo任务表)")
        print("  - user_preferences (用户偏好表)")
        print()
        print("已预置默认配置:")
        print("  - work_duration: 1500秒 (25分钟)")
        print("  - break_duration: 300秒 (5分钟)")
        print("  - always_on_top: False")
        print("  - auto_start_break: True")
        print("  - theme: light")
        print()
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print("=" * 50)


if __name__ == '__main__':
    main()
