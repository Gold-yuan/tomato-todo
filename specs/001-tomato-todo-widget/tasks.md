# 任务: 番茄时钟和TodoList桌面小组件

**输入**: 来自 `/specs/001-tomato-todo-widget/` 的设计文档
**前置条件**: plan.md(必需)、spec.md(用户故事必需)、research.md、data-model.md、contracts/

**测试**: 根据项目章程要求,本任务清单包含单元测试和集成测试任务(目标覆盖率>80%)

**组织结构**: 任务按用户故事分组, 以便每个故事能够独立实施和测试

## 格式: `[ID] [P?] [Story] 描述`
- **[P]**: 可以并行运行(不同文件, 无依赖关系)
- **[Story]**: 此任务属于哪个用户故事(例如: US1、US2、US3)
- 在描述中包含确切的文件路径

## 路径约定
- **单一项目**: 仓库根目录下的 `src/`、`tests/`

---

## 阶段 1: 设置(共享基础设施)

**目的**: 项目初始化和基本结构

- [ ] T001 创建项目目录结构(src/models、src/views、src/controllers、src/services、src/database、src/utils、tests/unit、tests/integration、assets/styles)
- [ ] T002 使用Poetry初始化Python 3.11项目并配置依赖项(pyproject.toml: PyQt6、SQLAlchemy、pytest、pytest-qt、pyinstaller)
- [ ] T003 [P] 配置代码检查工具(pyproject.toml: pylint、black、flake8)
- [ ] T004 [P] 创建资源文件目录结构(assets/icon.ico、assets/styles/main.qss)
- [ ] T005 [P] 初始化Git仓库(.gitignore忽略__pycache__、*.pyc、.venv、dist、build、*.db)

---

## 阶段 2: 基础(阻塞前置条件)

**目的**: 在任何用户故事可以实施之前必须完成的核心基础设施

**⚠️ 关键**: 在此阶段完成之前, 无法开始任何用户故事工作

### 数据库层基础

- [ ] T006 [P] 在 src/database/connection.py 中实现数据库连接管理(SQLAlchemy引擎、Session工厂、临时目录路径管理)
- [ ] T007 [P] 在 src/database/__init__.py 中创建Base基类和引擎实例导出
- [ ] T008 [P] 在 src/utils/constants.py 中定义应用常量(应用目录、数据库路径、锁文件路径、默认时长配置)
- [ ] T009 [P] 在 src/utils/single_instance.py 中实现单实例管理(QLockFile文件锁、冲突检测)
- [ ] T010 [P] 在 scripts/init_db.py 中创建数据库初始化脚本(创建表、预置配置)

### 数据模型基础

- [ ] T011 [P] 在 src/models/pomodoro_timer.py 中创建PomodoroTimer模型(id、mode、duration_seconds、remaining_seconds、status、start_time、last_update、created_at、updated_at)
- [ ] T012 [P] 在 src/models/pomodoro_stats.py 中创建PomodoroStats模型(id、mode、duration_seconds、completed_at、date)
- [ ] T013 [P] 在 src/models/todo_task.py 中创建TodoTask模型(id、content、is_completed、completed_at、created_at、updated_at)
- [ ] T014 [P] 在 src/models/user_preferences.py 中创建UserPreferences模型(id、key、value、created_at、updated_at)
- [ ] T015 [P] 在 src/models/__init__.py 中导出所有模型类

### 数据仓库层

- [ ] T016 [P] 在 src/database/repositories/pomodoro_repository.py 中实现PomodoroRepository(获取/保存/更新计时器状态、统计查询)
- [ ] T017 [P] 在 src/database/repositories/todo_repository.py 中实现TodoRepository(CRUD操作、分页查询、搜索)
- [ ] T018 [P] 在 src/database/repositories/preferences_repository.py 中实现PreferencesRepository(获取/设置配置)
- [ ] T019 [P] 在 src/database/repositories/__init__.py 中导出所有仓库类

### 服务层基础

- [ ] T020 [P] 在 src/services/pomodoro_service.py 中实现PomodoroService框架(初始化、依赖注入)
- [ ] T021 [P] 在 src/services/todo_service.py 中实现TodoService框架(初始化、依赖注入)
- [ ] T022 [P] 在 src/services/preferences_service.py 中实现PreferencesService框架(初始化、依赖注入)
- [ ] T023 [P] 在 src/services/__init__.py 中导出所有服务类

### 测试基础

- [ ] T024 [P] 在 tests/conftest.py 中配置pytest(fixture:内存数据库、测试Session、测试客户端)
- [ ] T025 [P] 在 tests/conftest.py 中配置pytest-qt(qtbot、qtbot_strong、pytest_configure)
- [ ] T026 [P] 在 tests/unit/test_database.py 中编写数据库连接和单实例管理的单元测试

**检查点**: 基础就绪 - 现在可以开始并行实施用户故事

---

## 阶段 3: 用户故事 1 - 番茄时钟计时器 (优先级: P1)🎯 MVP

**目标**: 实现完整的番茄时钟功能,包括25分钟工作/5分钟休息自动轮询、开始/暂停/停止控制、全屏视觉提示

**独立测试**:
- 启动应用,设置25分钟倒计时,点击开始验证倒计时运行
- 点击暂停验证倒计时暂停,继续验证恢复
- 倒计时归零验证全屏提示显示,2秒后自动渐隐或点击/按键后渐隐
- 验证自动切换到5分钟休息模式,完成后再切换回25分钟工作模式
- 应用重启后验证时钟状态正确恢复

### 用户故事 1 的测试⚠️

**注意: 先编写这些测试, 确保在实施前它们失败**

- [ ] T027 [P] [US1] 在 tests/unit/services/test_pomodoro_service.py 中编写PomodoroService.start_timer的单元测试
- [ ] T028 [P] [US1] 在 tests/unit/services/test_pomodoro_service.py 中编写PomodoroService.pause_timer的单元测试
- [ ] T029 [P] [US1] 在 tests/unit/services/test_pomodoro_service.py 中编写PomodoroService.resume_timer的单元测试
- [ ] T030 [P] [US1] 在 tests/unit/services/test_pomodoro_service.py 中编写PomodoroService.stop_timer的单元测试
- [ ] T031 [P] [US1] 在 tests/unit/services/test_pomodoro_service.py 中编写PomodoroService.tick的单元测试(倒计时更新和归零处理)
- [ ] T032 [P] [US1] 在 tests/integration/test_pomodoro_workflow.py 中编写完整番茄时钟工作流的集成测试(设置→开始→暂停→继续→完成→自动切换)

### 用户故事 1 的实施

#### UI组件

- [ ] T033 [P] [US1] 在 src/views/pomodoro_widget.py 中创建番茄时钟UI组件(QLCD数字显示、开始/暂停图标、停止图标、布局)
- [ ] T034 [P] [US1] 在 src/views/dialogs/time_set_dialog.py 中创建时间设置对话框(数字键盘输入、确认/取消按钮)
- [ ] T035 [P] [US1] 在 src/views/timeout_dialog.py 中创建全屏倒计时结束提示对话框(渐隐动画、2秒定时器、点击/按键事件)
- [ ] T036 [US1] 在 assets/styles/main.qss 中添加番茄时钟组件样式(扁平化、圆角、柔和阴影、番茄红#E74C3C主题色)

#### 控制器层

- [ ] T037 [US1] 在 src/controllers/pomodoro_controller.py 中实现PomodoroController(连接UI和Service,处理按钮点击、更新UI状态)

#### 服务层实现

- [ ] T038 [US1] 在 src/services/pomodoro_service.py 中实现start_timer方法(创建计时器、验证时长、保存到数据库、返回PomodoroTimer)
- [ ] T039 [US1] 在 src/services/pomodoro_service.py 中实现pause_timer方法(更新状态为paused、保存last_update时间、返回PomodoroTimer)
- [ ] T040 [US1] 在 src/services/pomodoro_service.py 中实现resume_timer方法(从暂停处继续、计算经过时间、返回PomodoroTimer)
- [ ] T041 [US1] 在 src/services/pomodoro_service.py 中实现stop_timer方法(重置为初始状态、保存到数据库、返回PomodoroTimer)
- [ ] T042 [US1] 在 src/services/pomodoro_service.py 中实现tick方法(每秒调用、减少remaining_seconds、处理归零、保存统计数据、自动切换模式)
- [ ] T043 [US1] 在 src/services/pomodoro_service.py 中实现get_current_timer方法(从数据库获取当前计时器状态)
- [ ] T044 [US1] 在 src/services/pomodoro_service.py 中实现get_stats方法(查询pomodoro_stats表、计算今日/本周/总数、返回统计字典)

#### 应用入口

- [ ] T045 [US1] 在 src/main.py 中创建应用主窗口(QMainWindow、设置无边框窗口属性、集成番茄时钟组件)
- [ ] T046 [US1] 在 src/main.py 中实现单实例检测(调用single_instance.py、锁文件冲突时提示并退出)
- [ ] T047 [US1] 在 src/main.py 中实现应用启动时的状态恢复(从数据库加载计时器状态、恢复UI显示)

**检查点**: 此时, 用户故事 1 应该完全功能化且可独立测试

---

## 阶段 4: 用户故事 2 - TodoList任务管理 (优先级: P2)

**目标**: 实现TodoList任务管理功能,包括添加、完成、删除、修改,倒序显示,分页支持(20条/页)

**独立测试**:
- 在输入框输入任务文本,按回车验证任务添加到列表顶部
- 点击圆形完成图标验证任务添加删除线并移动到底部
- 再次点击完成图标验证任务恢复到未完成状态并回到顶部
- 右键点击任务验证弹出菜单(删除、修改、标记完成)
- 验证任务超过20条时显示分页控件
- 应用重启后验证任务列表正确恢复

### 用户故事 2 的测试⚠️

**注意: 先编写这些测试, 确保在实施前它们失败**

- [ ] T048 [P] [US2] 在 tests/unit/services/test_todo_service.py 中编写TodoService.create_task的单元测试
- [ ] T049 [P] [US2] 在 tests/unit/services/test_todo_service.py 中编写TodoService.update_task的单元测试
- [ ] T050 [P] [US2] 在 tests/unit/services/test_todo_service.py 中编写TodoService.delete_task的单元测试
- [ ] T051 [P] [US2] 在 tests/unit/services/test_todo_service.py 中编写TodoService.toggle_completed的单元测试
- [ ] T052 [P] [US2] 在 tests/unit/services/test_todo_service.py 中编写TodoService.get_tasks的单元测试(分页逻辑、排序逻辑)
- [ ] T053 [P] [US2] 在 tests/integration/test_todo_workflow.py 中编写TodoList完整工作流的集成测试(创建→完成→取消完成→删除→修改→分页)

### 用户故事 2 的实施

#### UI组件

- [ ] T054 [P] [US2] 在 src/views/todo_widget.py 中创建TodoList UI组件(QListWidget、输入框、滚动区域、分页控件)
- [ ] T055 [P] [US2] 在 src/views/todo_widget.py 中实现自定义任务项QWidget(圆形完成图标、任务文本标签、截断显示、tooltip、高亮效果)
- [ ] T056 [P] [US2] 在 src/views/todo_widget.py 中实现右键菜单(QMenu、删除/修改/标记完成选项)
- [ ] T057 [P] [US2] 在 src/views/todo_widget.py 中实现分页控件(上一页/下一页按钮、页码显示)
- [ ] T058 [US2] 在 src/views/todo_widget.py 中实现任务编辑功能(双击或右键菜单触发、行内编辑、回车保存、ESC取消)
- [ ] T059 [US2] 在 assets/styles/main.qss 中添加TodoList组件样式(扁平化、圆角、悬停高亮、完成状态删除线)

#### 控制器层

- [ ] T060 [US2] 在 src/controllers/todo_controller.py 中实现TodoController(连接UI和Service,处理回车、点击、右键、分页事件,更新UI)

#### 服务层实现

- [ ] T061 [US2] 在 src/services/todo_service.py 中实现create_task方法(验证内容长度<=100字符、创建TodoTask、保存到数据库、返回TodoTask)
- [ ] T062 [US2] 在 src/services/todo_service.py 中实现update_task方法(更新content、验证长度、updated_at自动更新、返回TodoTask)
- [ ] T063 [US2] 在 src/services/todo_service.py 中实现delete_task方法(删除任务、返回True、处理NotFoundError)
- [ ] T064 [US2] 在 src/services/todo_service.py 中实现toggle_completed方法(切换is_completed、设置/清除completed_at、updated_at自动更新、返回TodoTask)
- [ ] T065 [US2] 在 src/services/todo_service.py 中实现get_tasks方法(分页查询、排序ORDER BY is_completed DESC, updated_at DESC、返回TaskList字典)
- [ ] T066 [US2] 在 src/services/todo_service.py 中实现search_tasks方法(关键词搜索content字段、返回任务列表)

#### 主窗口集成

- [ ] T067 [US2] 在 src/main.py中集成TodoList组件到主窗口(垂直布局:上方番茄时钟、下方TodoList)
- [ ] T068 [US2] 在 src/main.py中实现窗口布局自适应(番茄时钟和TodoList按比例分配空间、窗口缩放时调整)

**检查点**: 此时, 用户故事 1 和 2 都应该独立运行

---

## 阶段 5: 用户故事 3 - 窗口布局和交互 (优先级: P3)

**目标**: 实现窗口管理功能,包括置顶、靠边、调整大小,最小尺寸限制

**独立测试**:
- 拖动窗口到屏幕边缘验证自动对齐
- 拖动窗口边缘或角落验证窗口可以调整大小
- 尝试缩小窗口到最小尺寸验证停止缩小(时钟+2行TodoList)
- 点击置顶按钮验证窗口保持在其他窗口之上
- 验证窗口大小改变时TodoList区域自适应

### 用户故事 3 的测试⚠️

**注意: 先编写这些测试, 确保在实施前它们失败**

- [ ] T069 [P] [US3] 在 tests/unit/test_window_behavior.py 中编写窗口最小尺寸限制的单元测试
- [ ] T070 [P] [US3] 在 tests/unit/test_window_behavior.py 中编写窗口靠边对齐的单元测试
- [ ] T071 [P] [US3] 在 tests/integration/test_window_workflow.py 中编写窗口管理完整工作流的集成测试(拖拽、调整、置顶、靠边)

### 用户故事 3 的实施

#### UI组件

- [ ] T072 [P] [US3] 在 src/views/main_window.py 中实现无边框窗口(QMainWindow、Qt.FramelessWindowHint、Qt.WindowSystemMenuHint)
- [ ] T073 [P] [US3] 在 src/views/main_window.py 中实现窗口拖拽功能(mousePressEvent、mouseMoveEvent、计算窗口位置)
- [ ] T074 [P] [US3] 在 src/views/main_window.py 中实现窗口大小调整功能(QSizeGrip、拖拽边缘和角落、重写resizeEvent)
- [ ] T075 [P] [US3] 在 src/views/main_window.py 中实现窗口最小尺寸限制(resizeEvent中检查width/height、阻止缩小到最小值以下)
- [ ] T076 [P] [US3] 在 src/views/main_window.py 中实现置顶功能(Qt.WindowStaysOnTopHint、切换置顶状态、菜单选项或工具栏按钮)
- [ ] T077 [P] [US3] 在 src/views/main_window.py 中实现靠边对齐(moveEvent中检测屏幕边缘、自动吸附对齐)
- [ ] T078 [US3] 在 src/main.py中创建QApplication、设置窗口图标(assets/icon.ico)、显示主窗口

#### 控制器层

- [ ] T079 [US3] 在 src/controllers/window_controller.py 中实现WindowController(处理窗口事件、管理窗口状态、保存窗口位置到偏好设置)

#### 服务层实现

- [ ] T080 [US3] 在 src/services/preferences_service.py 中实现get_preference方法(从数据库获取配置、支持默认值、解析JSON)
- [ ] T081 [US3] 在 src/services/preferences_service.py 中实现set_preference方法(保存配置到数据库、序列化为JSON、更新updated_at)
- [ ] T082 [US3] 在 src/services/preferences_service.py 中实现set_preferences方法(批量保存配置字典)
- [ ] T083 [US3] 在 src/services/preferences_service.py 中实现get_all_preferences方法(获取所有用户配置、返回字典)

#### 样式完善

- [ ] T084 [US3] 在 assets/styles/main.qss中添加扁平化全局样式(去锐利化、圆角8px、柔和阴影box-shadow: 0 2px 8px rgba(0,0,0,0.1)、主色#E74C3C、背景色#F5F6FA)
- [ ] T085 [US3] 在 assets/styles/main.qss中添加窗口样式(无边框、圆角窗口、自定义标题栏)

**检查点**: 所有用户故事现在应该独立功能化

---

## 阶段 6: 完善与横切关注点

**目的**: 影响多个用户故事的改进

### 测试完善

- [ ] T086 [P] 在 tests/unit/test_validators.py 中编写数据验证器的单元测试(任务内容长度、时间范围验证)
- [ ] T087 [P] 在 tests/unit/test_validators.py 中编写系统休眠时间计算的单元测试(系统锁定后时间戳校验)
- [ ] T088 [P] 在 tests/integration/test_database.py 中编写数据库操作的集成测试(连接、事务、迁移)
- [ ] T089 [P] 在 tests/integration/test_workflows.py 中编写端到端工作流测试(番茄时钟+TodoList+窗口管理)

### 性能优化

- [ ] T090 在 src/database/connection.py 中优化数据库连接池配置(StaticPool、连接复用)
- [ ] T091 在 src/views/todo_widget.py 中实现TodoList虚拟化模式(处理大量任务时的性能)
- [ ] T092 在 src/services/pomodoro_service.py 中优化统计查询性能(添加数据库索引、缓存统计结果)

### 文档和发布

- [ ] T093 更新 README.md(项目介绍、功能特性、安装说明、使用指南)
- [ ] T094 更新 docs/user_guide.md(用户手册、功能说明、常见问题)
- [ ] T095 [P] 在 scripts/build.py 中创建PyInstaller打包配置(--onefile、--windowed、--icon、添加资产文件)
- [ ] T096 [P] 使用PyInstaller打包生成 dist/TomatoTodo.exe便携式可执行文件

---

## 依赖关系与执行顺序

### 阶段依赖关系

- **设置(阶段 1)**: 无依赖关系 - 可立即开始
- **基础(阶段 2)**: 依赖于设置完成 - 阻塞所有用户故事
- **用户故事(阶段 3+)**: 都依赖于基础阶段完成
  - 然后用户故事可以并行进行(如果有人员)
  - 或按优先级顺序进行(P1 → P2 → P3)
- **完善(最终阶段)**: 依赖于所有期望的用户故事完成

### 用户故事依赖关系

- **用户故事 1(P1)**: 可在基础(阶段 2)后开始 - 无其他故事依赖
- **用户故事 2(P2)**: 可在基础(阶段 2)后开始 - 可与 US1 集成但应独立可测试
- **用户故事 3(P3)**: 可在基础(阶段 2)后开始 - 可与 US1/US2 集成但应独立可测试

### 每个用户故事内部

- 测试(如包含)必须在实施前编写并失败
- 模型在服务之前
- 服务在端点之前
- 核心实施在集成之前
- 故事完成后才移至下一个优先级

### 并行机会

#### 设置阶段并行任务

```bash
# 可以并行执行:
T001 创建项目目录结构
T002 使用Poetry初始化项目
T003 配置代码检查工具
T004 创建资源文件目录结构
T005 初始化Git仓库
```

#### 基础阶段并行任务

```bash
# 可以并行执行:
T006 数据库连接管理
T007 Base基类和引擎导出
T008 应用常量定义
T009 单实例管理
T010 数据库初始化脚本
T011-T014 数据模型
T016-T019 数据仓库
T020-T023 服务框架
T024-T025 测试配置
```

#### 用户故事 1 并行任务

```bash
# 测试(并行):
T027-T032 编写所有单元测试和集成测试

# UI组件(并行):
T033 番茄时钟UI组件
T034 时间设置对话框
T035 全屏提示对话框

# 服务层(依赖模型):
T038-T044 实现所有服务方法
```

#### 用户故事 2 并行任务

```bash
# 测试(并行):
T048-T053 编写所有单元测试和集成测试

# UI组件(并行):
T054 TodoList UI组件
T055 自定义任务项
T056 右键菜单
T057 分页控件
T058 任务编辑
```

#### 用户故事 3 并行任务

```bash
# 测试(并行):
T069-T071 编写所有测试

# UI组件(并行):
T072 无边框窗口
T073 窗口拖拽
T074 大小调整
T075 最小尺寸
T076 置顶功能
T077 靠边对齐
```

---

## 实施策略

### 仅 MVP(仅用户故事 1)

**目标**: 交付可用的番茄时钟

1. 完成阶段 1: 设置 (T001-T005)
2. 完成阶段 2: 基础 (T006-T026)
3. 完成阶段 3: 用户故事 1 (T027-T047)
4. **停止并验证**: 独立测试番茄时钟功能
5. 打包为exe: T095、T096
6. 如准备好则部署/演示

**交付物**: TomatoTodo.exe (仅番茄时钟功能)

### 增量交付

**目标**: 逐步增加功能,每个阶段都可独立使用

1. 完成设置 + 基础 → 基础就绪
2. 添加用户故事 1 → 独立测试 → 部署/演示 (MVP! - 番茄时钟)
3. 添加用户故事 2 → 独立测试 → 部署/演示 (番茄时钟 + TodoList)
4. 添加用户故事 3 → 独立测试 → 部署/演示 (完整功能)
5. 每个故事在不破坏先前故事的情况下增加价值

**交付物**:
- MVP: TomatoTodo.exe (番茄时钟)
- v2.0: TomatoTodo.exe (番茄时钟 + TodoList)
- v3.0: TomatoTodo.exe (完整功能)

### 并行团队策略

**适用场景**: 有多个开发人员同时工作

1. 团队一起完成设置 + 基础 (T001-T026)
2. 基础完成后并行开始:
   - 开发人员 A: 用户故事 1 (T027-T047)
   - 开发人员 B: 用户故事 2 (T048-T068)
   - 开发人员 C: 用户故事 3 (T069-T085)
3. 故事独立完成和集成到主窗口
4. 联合测试、文档和打包 (T086-T096)

---

## 注意事项

- [P] 任务 = 不同文件, 无依赖关系
- [Story] 标签将任务映射到特定用户故事以实现可追溯性
- 每个用户故事应该独立可完成和可测试
- 在实施前验证测试失败(测试驱动开发)
- 在每个任务或逻辑组后提交代码
- 在任何检查点停止以独立验证故事
- 避免: 模糊任务、相同文件冲突、破坏独立性的跨故事依赖

---

**任务版本**: 1.0.0
**总任务数**: 96项
**用户故事**: 3个 (P1番茄时钟、P2 TodoList、P3 窗口管理)
**测试覆盖率目标**: >80%
**预计工期**: 4周 (MVP: 1周, 完整功能: 4周)
