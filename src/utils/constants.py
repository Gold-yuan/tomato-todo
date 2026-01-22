"""
应用常量定义

定义应用级别的常量配置
"""
import os
import tempfile

# 应用目录
APP_DIR = os.path.join(tempfile.gettempdir(), 'TomatoTodo')

# 数据库路径
DB_PATH = os.path.join(APP_DIR, 'tomato_todo.db')

# 锁文件路径（用于单实例检测）
LOCK_FILE_PATH = os.path.join(APP_DIR, 'app.lock')

# 默认时长配置（秒）
DEFAULT_WORK_DURATION = 1500  # 25分钟
DEFAULT_BREAK_DURATION = 300  # 5分钟

# 时长范围限制
MIN_DURATION = 60  # 最小1分钟
MAX_DURATION = 7200  # 最大2小时

# 分页配置
DEFAULT_PER_PAGE = 20  # TodoList每页默认显示20条

# 任务内容长度限制
MAX_TASK_CONTENT_LENGTH = 100  # 最多100个中文字符

# 窗口默认尺寸
DEFAULT_WINDOW_WIDTH = 400
DEFAULT_WINDOW_HEIGHT = 600

# 窗口最小尺寸（时钟 + 2行TodoList）
MIN_WINDOW_WIDTH = 300
MIN_WINDOW_HEIGHT = 400
