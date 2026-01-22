# 服务层API契约

**功能**: 001-tomato-todo-widget
**创建时间**: 2026-01-21
**架构**: MVC + 服务层

---

## 概述

本文档定义了应用内部服务层的API契约。服务层封装业务逻辑,为控制器提供清晰的接口。

---

## 1. PomodoroService (番茄时钟服务)

### 1.1 启动番茄时钟

**方法**: `start_timer(duration: int, mode: str) -> PomodoroTimer`

**描述**: 启动一个新的番茄时钟倒计时

**参数**:
- `duration` (int): 倒计时时长(秒), 范围: 60-7200
- `mode` (str): 时钟模式, 'work'(工作) 或 'break'(休息)

**返回**: `PomodoroTimer` 对象

**异常**:
- `ValueError`: 如果duration不在有效范围内
- `ValueError`: 如果mode不是'work'或'break'
- `RuntimeError`: 如果时钟已在运行中

**示例**:
```python
# 启动25分钟工作番茄
timer = pomodoro_service.start_timer(1500, 'work')
# timer.id = 1
# timer.remaining_seconds = 1500
# timer.status = 'running'
```

---

### 1.2 暂停番茄时钟

**方法**: `pause_timer() -> PomodoroTimer`

**描述**: 暂停当前运行的番茄时钟

**返回**: 更新后的 `PomodoroTimer` 对象

**异常**:
- `RuntimeError`: 如果时钟未在运行

**示例**:
```python
timer = pomodoro_service.pause_timer()
# timer.status = 'paused'
```

---

### 1.3 继续番茄时钟

**方法**: `resume_timer() -> PomodoroTimer`

**描述**: 继续暂停的番茄时钟

**返回**: 更新后的 `PomodoroTimer` 对象

**异常**:
- `RuntimeError`: 如果时钟未暂停

**示例**:
```python
timer = pomodoro_service.resume_timer()
# timer.status = 'running'
```

---

### 1.4 停止番茄时钟

**方法**: `stop_timer() -> PomodoroTimer`

**描述**: 停止当前番茄时钟,重置状态

**返回**: 更新后的 `PomodoroTimer` 对象

**异常**: 无

**示例**:
```python
timer = pomodoro_service.stop_timer()
# timer.status = 'stopped'
# timer.remaining_seconds = timer.duration_seconds
```

---

### 1.5 获取当前状态

**方法**: `get_current_timer() -> PomodoroTimer | None`

**描述**: 获取当前番茄时钟状态

**返回**: `PomodoroTimer` 对象或 None

**示例**:
```python
timer = pomodoro_service.get_current_timer()
if timer and timer.status == 'running':
    print(f"剩余时间: {timer.remaining_seconds}秒")
```

---

### 1.6 更新倒计时

**方法**: `tick() -> PomodoroTimer | None`

**描述**: 每秒调用,更新倒计时,自动处理倒计时结束

**返回**: 更新后的 `PomodoroTimer` 对象,如果倒计时结束返回 None

**业务逻辑**:
1. 减少remaining_seconds
2. 如果remaining_seconds <= 0:
   - 保存统计数据
   - 自动切换到下一个模式(工作→休息→工作)
   - 返回 None

**示例**:
```python
# 定时器每秒调用
timer = pomodoro_service.tick()
if timer is None:
    # 倒计时结束,显示全屏提示
    show_timeout_dialog()
    # 自动切换模式
    new_timer = pomodoro_service.get_current_timer()
```

---

### 1.7 获取统计数据

**方法**: `get_stats() -> PomodoroStats`

**描述**: 获取番茄时钟统计数据

**返回**: `PomodoroStats` 对象
```python
{
    "total_completed": 150,      # 总完成番茄数
    "today_completed": 8,        # 今日完成工作番茄数
    "week_completed": 45,        # 本周完成工作番茄数
    "today_breaks": 7,           # 今日休息次数
    "week_breaks": 42            # 本周休息次数
}
```

**示例**:
```python
stats = pomodoro_service.get_stats()
print(f"今日完成: {stats['today_completed']}个番茄")
```

---

## 2. TodoService (Todo任务服务)

### 2.1 创建任务

**方法**: `create_task(content: str) -> TodoTask`

**描述**: 创建一个新的Todo任务

**参数**:
- `content` (str): 任务内容, 最多100个中文字符

**返回**: 创建的 `TodoTask` 对象

**异常**:
- `ValueError`: 如果content为空
- `ValueError`: 如果content超过100个字符

**业务逻辑**:
- 创建任务时updated_at自动设置为当前时间
- 任务自动出现在列表顶部(未完成任务中最新更新的在前)
- 保存到数据库

**示例**:
```python
task = todo_service.create_task("完成项目文档")
# task.id = 1
# task.content = "完成项目文档"
# task.is_completed = False
# task.updated_at = datetime.now()  # 自动设置
```

---

### 2.2 更新任务

**方法**: `update_task(task_id: int, content: str) -> TodoTask`

**描述**: 更新任务内容

**参数**:
- `task_id` (int): 任务ID
- `content` (str): 新的任务内容

**返回**: 更新后的 `TodoTask` 对象

**异常**:
- `NotFoundError`: 如果任务不存在
- `ValueError`: 如果content为空或超过100个字符

**示例**:
```python
task = todo_service.update_task(1, "完成项目文档和用户手册")
```

---

### 2.3 删除任务

**方法**: `delete_task(task_id: int) -> bool`

**描述**: 删除指定任务

**参数**:
- `task_id` (int): 任务ID

**返回**: 成功返回 True

**异常**:
- `NotFoundError`: 如果任务不存在

**业务逻辑**:
- 直接删除任务,无需重新计算position

**示例**:
```python
success = todo_service.delete_task(1)
```

---

### 2.4 切换完成状态

**方法**: `toggle_completed(task_id: int) -> TodoTask`

**描述**: 切换任务的完成状态

**参数**:
- `task_id` (int): 任务ID

**返回**: 更新后的 `TodoTask` 对象

**异常**:
- `NotFoundError`: 如果任务不存在

**业务逻辑**:
- 未完成→已完成: 设置is_completed=True,设置completed_at,updated_at自动更新,任务自动移动到列表底部(已完成任务中)
- 已完成→未完成: 设置is_completed=False,清空completed_at,updated_at自动更新,任务自动移动到列表顶部(未完成任务中)

**示例**:
```python
task = todo_service.toggle_completed(1)
# task.is_completed = True
# task.completed_at = datetime.now()
# task.updated_at = datetime.now()  # 自动更新,任务自动移到底部
```

---

### 2.5 获取任务列表

**方法**: `get_tasks(page: int = 1, per_page: int = 20, completed_only: bool = False) -> TaskList`

**描述**: 分页获取任务列表

**参数**:
- `page` (int): 页码, 从1开始
- `per_page` (int): 每页数量, 默认20
- `completed_only` (bool): 是否只获取已完成任务

**返回**: `TaskList` 对象
```python
{
    "tasks": [TodoTask, ...],  # 任务列表
    "total": 100,              # 总任务数
    "page": 1,                 # 当前页
    "per_page": 20,            # 每页数量
    "total_pages": 5           # 总页数
}
```

**排序规则**:
- 未完成任务在前,已完成任务在后
- 同类别内按updated_at DESC排序(最新更新的在前)
- SQL: `ORDER BY is_completed DESC, updated_at DESC`

**示例**:
```python
# 获取第1页,每页20条
result = todo_service.get_tasks(page=1, per_page=20)
for task in result['tasks']:
    print(f"{task.content} - {'已完成' if task.is_completed else '未完成'}")
```

---

### 2.6 搜索任务

**方法**: `search_tasks(keyword: str) -> List[TodoTask]`

**描述**: 按关键词搜索任务

**参数**:
- `keyword` (str): 搜索关键词

**返回**: 匹配的任务列表

**搜索范围**: 任务内容(content)

**示例**:
```python
tasks = todo_service.search_tasks("文档")
# 返回所有包含"文档"的任务
```

---

## 3. PreferencesService (用户偏好服务)

### 3.1 获取偏好设置

**方法**: `get_preference(key: str, default: Any = None) -> Any`

**描述**: 获取指定偏好设置

**参数**:
- `key` (str): 配置键
- `default` (Any): 默认值(如果不存在)

**返回**: 配置值(解析JSON后的实际类型)

**预置键**:
- `work_duration`: int - 工作时长(秒), 默认1500
- `break_duration`: int - 休息时长(秒), 默认300
- `always_on_top`: bool - 置顶状态, 默认False
- `theme`: str - 主题, 默认'light'

**示例**:
```python
work_duration = preferences_service.get_preference('work_duration', 1500)
# 返回: 1500
```

---

### 3.2 设置偏好

**方法**: `set_preference(key: str, value: Any) -> None`

**描述**: 设置偏好配置

**参数**:
- `key` (str): 配置键
- `value` (Any): 配置值(自动序列化为JSON)

**返回**: None

**异常**:
- `ValueError`: 如果value无法序列化为JSON

**示例**:
```python
preferences_service.set_preference('work_duration', 1800)  # 30分钟
```

---

### 3.3 批量设置

**方法**: `set_preferences(preferences: Dict[str, Any]) -> None`

**描述**: 批量设置偏好配置

**参数**:
- `preferences` (Dict): 配置字典

**示例**:
```python
preferences_service.set_preferences({
    'work_duration': 1800,
    'break_duration': 600,
    'always_on_top': True
})
```

---

### 3.4 获取所有配置

**方法**: `get_all_preferences() -> Dict[str, Any]`

**描述**: 获取所有用户偏好配置

**返回**: 配置字典

**示例**:
```python
prefs = preferences_service.get_all_preferences()
# 返回: {'work_duration': 1500, 'break_duration': 300, ...}
```

---

## 4. 数据模型定义

### PomodoroTimer

```python
@dataclass
class PomodoroTimer:
    id: int
    mode: str                    # 'work' | 'break'
    duration_seconds: int
    remaining_seconds: int
    status: str                  # 'running' | 'paused' | 'stopped'
    start_time: datetime | None
    last_update: datetime
```

### TodoTask

```python
@dataclass
class TodoTask:
    id: int
    content: str                 # 最多100个字符
    is_completed: bool
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime
```

### PomodoroStats

```python
@dataclass
class PomodoroStats:
    total_completed: int
    today_completed: int
    week_completed: int
    today_breaks: int
    week_breaks: int
```

---

## 5. 异常定义

### 自定义异常

```python
class NotFoundError(Exception):
    """资源未找到异常"""
    pass

class ValidationError(Exception):
    """数据验证异常"""
    pass

class BusinessLogicError(Exception):
    """业务逻辑异常"""
    pass
```

### 异常处理示例

```python
try:
    task = todo_service.create_task("")
except ValidationError as e:
    print(f"验证失败: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

---

## 6. 事务处理

### 自动事务

所有服务方法自动包裹在数据库事务中:
- 成功: 自动commit
- 失败: 自动rollback

### 手动事务

```python
from database.connection import session

with session.begin():
    # 批量操作
    todo_service.create_task("任务1")
    todo_service.create_task("任务2")
    # 任何错误都会回滚整个事务
```

---

## 7. 性能指标

### 响应时间目标

- 创建任务: < 50ms
- 更新任务: < 50ms
- 查询任务列表(20条): < 100ms
- 启动番茄时钟: < 50ms
- 获取统计数据: < 100ms

### 并发处理

- 单实例设计,无需处理多线程并发
- 数据库操作使用连接池
- UI操作在主线程,业务逻辑可在后台线程

---

## 8. 测试契约

### 单元测试示例

```python
def test_create_task():
    service = TodoService(session)
    task = service.create_task("测试任务")
    assert task.id is not None
    assert task.content == "测试任务"
    assert task.is_completed is False
```

### 集成测试示例

```python
def test_start_and_complete_pomodoro():
    service = PomodoroService(session)
    timer = service.start_timer(60, 'work')
    assert timer.status == 'running'
    assert timer.remaining_seconds == 60
```

---

## 9. 版本控制

### API版本

当前版本: **v1.0**

### 向后兼容性

- 修改现有方法签名视为破坏性变更
- 添加新方法不破坏兼容性
- 废弃方法保留一个主版本周期

---

## 10. 文档更新日志

- **2026-01-21**: 初始版本,定义所有服务API契约
