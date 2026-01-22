# 数据模型: 番茄时钟和TodoList桌面小组件

**功能**: 001-tomato-todo-widget
**创建时间**: 2026-01-21
**数据库**: SQLite 3.40+
**ORM**: SQLAlchemy 2.0+

---

## 数据库架构

### 数据库文件
- **路径**: `%TEMP%\TomatoTodo\tomato_todo.db` (Windows用户临时目录)
  - 例如: `C:\Users\<用户名>\AppData\Local\Temp\TomatoTodo\tomato_todo.db`
- **编码**: UTF-8
- **外键约束**: 启用

**路径说明**:
- 使用Windows临时目录存储用户数据
- 便携式设计: exe无需安装,数据跟随系统
- 应用首次运行时自动创建目录结构
- 卸载时直接删除exe即可,数据保留在临时目录(可手动清理)

---

## 数据表定义

### 1. pomodoro_timer (番茄时钟状态表)

存储当前番茄时钟的运行状态,用于应用重启后恢复状态。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY | 主键 |
| mode | VARCHAR(10) | NOT NULL | 当前模式: 'work'(工作) / 'break'(休息) |
| duration_seconds | INTEGER | NOT NULL | 设置的时长(秒) |
| remaining_seconds | INTEGER | NOT NULL | 剩余时间(秒) |
| status | VARCHAR(10) | NOT NULL | 运行状态: 'running'(运行中) / 'paused'(暂停) / 'stopped'(停止) |
| start_time | DATETIME | | 开始时间 |
| last_update | DATETIME | NOT NULL | 最后更新时间 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

**索引**:
- `idx_status`: 索引(status) - 快速查询当前状态

**验证规则**:
- `duration_seconds` > 0 且 <= 7200 (最大2小时)
- `remaining_seconds` >= 0 且 <= `duration_seconds`
- `mode` 必须是 'work' 或 'break'
- `status` 必须是 'running'、'paused' 或 'stopped'

**状态转换**:
```
stopped → running (开始)
running → paused (暂停)
paused → running (继续)
running/paused → stopped (停止)
```

---

### 2. pomodoro_stats (番茄时钟统计表)

存储番茄时钟的使用统计和历史记录。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY | 主键 |
| mode | VARCHAR(10) | NOT NULL | 模式: 'work' / 'break' |
| duration_seconds | INTEGER | NOT NULL | 实际完成的时长(秒) |
| completed_at | DATETIME | NOT NULL | 完成时间 |
| date | DATE | NOT NULL | 日期(用于统计) |

**索引**:
- `idx_date`: 索引(date) - 按日期查询统计
- `idx_completed_at`: 索引(completed_at) - 按时间排序

**统计查询**:
- 今日完成工作番茄数: `SELECT COUNT(*) FROM pomodoro_stats WHERE mode='work' AND date=CURRENT_DATE`
- 本周完成工作番茄数: `SELECT COUNT(*) FROM pomodoro_stats WHERE mode='work' AND date>=date('now', '-7 days')`
- 总完成番茄数: `SELECT COUNT(*) FROM pomodoro_stats`

---

### 3. todo_tasks (Todo任务表)

存储所有Todo任务。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY | 主键 |
| content | TEXT | NOT NULL | 任务内容(最多100个中文字符) |
| is_completed | BOOLEAN | NOT NULL DEFAULT 0 | 是否完成 |
| completed_at | DATETIME | | 完成时间 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

**索引**:
- `idx_completed_updated`: 复合索引(is_completed DESC, updated_at DESC) - 优化排序查询
- `idx_is_completed`: 索引(is_completed) - 筛选未完成/已完成

**验证规则**:
- `content` 长度 <= 100 个中文字符

**排序逻辑**:
- 未完成任务在前,已完成任务在后
- 同类别内按updated_at倒序排列(最新更新的在前)
- SQL: `SELECT * FROM todo_tasks ORDER BY is_completed DESC, updated_at DESC`

**分页逻辑**:
- 每页20条任务
- 按上述排序规则分页

---

### 4. user_preferences (用户偏好表)

存储用户的个人设置和偏好。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PRIMARY KEY | 主键 |
| key | VARCHAR(50) | NOT NULL UNIQUE | 配置键 |
| value | TEXT | NOT NULL | 配置值(JSON格式) |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

**预置配置键**:

| key | value类型 | 说明 |
|-----|-----------|------|
| work_duration | INTEGER | 工作时长(秒), 默认: 1500 (25分钟) |
| break_duration | INTEGER | 休息时长(秒), 默认: 300 (5分钟) |
| window_x | INTEGER | 窗口X坐标 |
| window_y | INTEGER | 窗口Y坐标 |
| window_width | INTEGER | 窗口宽度 |
| window_height | INTEGER | 窗口高度 |
| always_on_top | BOOLEAN | 置顶状态, 默认: false |
| auto_start_break | BOOLEAN | 自动开始休息, 默认: true |
| theme | STRING | 主题: 'light' / 'dark', 默认: 'light' |

**索引**:
- `idx_key`: UNIQUE索引(key) - 快速查找配置

---

## 关系图

```
pomodoro_timer (单例,仅一条记录)
    ↓ (统计记录)
pomodoro_stats
    ├── mode='work' (工作番茄)
    └── mode='break' (休息记录)

todo_tasks (多条记录)
    ├── is_completed=0 (未完成任务, 按updated_at DESC排序)
    └── is_completed=1 (已完成任务, 按updated_at DESC排序)

user_preferences (键值对配置)
    ├── work_duration=1500
    ├── break_duration=300
    └── ...
```

---

## SQLAlchemy模型定义

### PomodoroTimer

```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class PomodoroTimer(Base):
    __tablename__ = 'pomodoro_timer'

    id = Column(Integer, primary_key=True)
    mode = Column(String(10), nullable=False)  # 'work' or 'break'
    duration_seconds = Column(Integer, nullable=False)
    remaining_seconds = Column(Integer, nullable=False)
    status = Column(String(10), nullable=False)  # 'running', 'paused', 'stopped'
    start_time = Column(DateTime)
    last_update = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
```

### PomodoroStats

```python
class PomodoroStats(Base):
    __tablename__ = 'pomodoro_stats'

    id = Column(Integer, primary_key=True)
    mode = Column(String(10), nullable=False)  # 'work' or 'break'
    duration_seconds = Column(Integer, nullable=False)
    completed_at = Column(DateTime, nullable=False)
    date = Column(String(10), nullable=False)  # YYYY-MM-DD
```

### TodoTask

```python
class TodoTask(Base):
    __tablename__ = 'todo_tasks'

    id = Column(Integer, primary_key=True)
    content = Column(String(100), nullable=False)  # 最多100个中文字符
    is_completed = Column(Boolean, nullable=False, default=False)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
```

### UserPreferences

```python
class UserPreferences(Base):
    __tablename__ = 'user_preferences'

    id = Column(Integer, primary_key=True)
    key = Column(String(50), nullable=False, unique=True)
    value = Column(String(500), nullable=False)  # JSON格式
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
```

---

## 数据库操作示例

### 初始化数据库

```python
import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 获取Windows临时目录
app_dir = os.path.join(tempfile.gettempdir(), 'TomatoTodo')
os.makedirs(app_dir, exist_ok=True)

db_path = os.path.join(app_dir, 'tomato_todo.db')
engine = create_engine(f'sqlite:///{db_path}')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
```

### 保存和恢复番茄时钟状态

```python
# 保存状态
timer = PomodoroTimer(
    mode='work',
    duration_seconds=1500,
    remaining_seconds=1200,
    status='running',
    start_time=datetime.now(),
    last_update=datetime.now()
)
session.merge(timer)  # 使用merge,因为只有一条记录
session.commit()

# 恢复状态
timer = session.query(PomodoroTimer).first()
if timer and timer.status == 'running':
    # 计算实际经过时间
    elapsed = (datetime.now() - timer.last_update).total_seconds()
    timer.remaining_seconds = max(0, timer.remaining_seconds - int(elapsed))
```

### 添加Todo任务

```python
# 创建新任务(updated_at自动设置为当前时间)
task = TodoTask(
    content='完成项目文档'
)
session.add(task)
session.commit()
```

### 完成Todo任务

```python
task = session.query(TodoTask).filter_by(id=task_id).first()
if task:
    task.is_completed = True
    task.completed_at = datetime.now()
    # updated_at会自动更新,任务自动移动到列表底部
    session.commit()
```

### 取消完成Todo任务

```python
task = session.query(TodoTask).filter_by(id=task_id).first()
if task and task.is_completed:
    task.is_completed = False
    task.completed_at = None
    # updated_at会自动更新,任务自动移动到未完成列表顶部
    session.commit()
```

### 分页查询Todo任务

```python
page = 1
per_page = 20
offset = (page - 1) * per_page

# 未完成任务在前,已完成任务在后,同类别内按updated_at DESC排序
tasks = session.query(TodoTask)\
    .order_by(TodoTask.is_completed.desc(), TodoTask.updated_at.desc())\
    .limit(per_page)\
    .offset(offset)\
    .all()
```

---

## 数据迁移策略

### 版本管理

使用Alembic进行数据库版本管理和迁移:

```bash
# 初始化Alembic
alembic init alembic

# 创建迁移脚本
alembic revision --autogenerate -m "Initial schema"

# 应用迁移
alembic upgrade head
```

### 备份和恢复

```python
import os
import tempfile
import shutil
from datetime import datetime

# 获取应用目录
app_dir = os.path.join(tempfile.gettempdir(), 'TomatoTodo')
backup_dir = os.path.join(app_dir, 'backup')
os.makedirs(backup_dir, exist_ok=True)

# 备份
db_path = os.path.join(app_dir, 'tomato_todo.db')
backup_path = os.path.join(backup_dir, f"tomato_todo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
shutil.copy2(db_path, backup_path)

# 恢复
shutil.copy2(backup_path, db_path)
```

---

## 性能优化

### 连接池配置

```python
engine = create_engine(
    'sqlite:///data/tomato_todo.db',
    poolclass=StaticPool,  # SQLite单线程,使用静态池
    connect_args={'check_same_thread': False},  # 允许多线程访问
    echo=False  # 生产环境关闭SQL日志
)
```

### 批量操作

```python
# 批量插入任务
tasks = [
    TodoTask(content=f'任务{i}')
    for i in range(100)
]
session.bulk_save_objects(tasks)
session.commit()
```

---

## 数据完整性

### 触发器

**自动更新updated_at**:

```sql
CREATE TRIGGER update_pomodoro_timer_timestamp
AFTER UPDATE ON pomodoro_timer
FOR EACH ROW
BEGIN
    UPDATE pomodoro_timer SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
```

### 级联删除

目前不需要级联删除,所有表独立存储。

---

## 总结

- **4个核心表**: pomodoro_timer、pomodoro_stats、todo_tasks、user_preferences
- **关系**: 一对一(timer)、一对多(stats/tasks)、键值对(preferences)
- **索引优化**: 关键字段建立索引,加速查询
- **数据完整性**: 外键约束、触发器、验证规则
- **性能**: 连接池、批量操作、分页查询
- **可维护性**: Alembic迁移、备份恢复策略
