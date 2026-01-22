# 实施计划: 番茄时钟和TodoList桌面小组件

**分支**: `001-tomato-todo-widget` | **日期**: 2026-01-21 | **规范**: [spec.md](./spec.md)
**输入**: 来自 `/specs/001-tomato-todo-widget/spec.md` 的功能规范

**注意**: 此模板由 `/speckit.plan` 命令填充. 执行工作流程请参见 `.specify/templates/commands/plan.md`.

## 摘要

本功能实现一个Windows桌面小组件,包含番茄工作法计时器和TodoList任务管理。核心功能包括:

**主要需求**:
- **番茄时钟(P1)**: 支持25分钟工作/5分钟休息自动轮询,开始/暂停/停止控制,全屏视觉提示
- **TodoList(P2)**: 任务增删改查,完成状态切换,倒序显示,分页支持(20条/页)
- **窗口管理(P3)**: 置顶、靠边、调整大小,最小尺寸限制(时钟+2行TodoList)

**技术方法**:
- **架构**: MVC + 服务层,模块化设计,职责分离
- **技术栈**: Python 3.11 + PyQt6 + SQLAlchemy + SQLite
- **打包**: PyInstaller单文件exe,无需安装Python环境

## 技术背景

**语言/版本**: Python 3.11+
**主要依赖**: PyQt6 6.6.0+, SQLAlchemy 2.0+, pytest 7.4+
**存储**: SQLite 3.40+ (本地文件数据库)
**测试**: pytest + pytest-qt (单元测试、集成测试、UI测试)
**目标平台**: Windows 10+
**项目类型**: 单一桌面应用
**性能目标**:
- UI响应: <100ms (60fps流畅度)
- 数据库操作: <50ms
- 应用启动: <1秒
- 内存占用: <100MB (空载)
**约束条件**:
- 单实例运行(使用文件锁)
- 离线可用(无网络依赖)
- 无声音提示(纯视觉)
- TodoList单条最多100个中文字符
**规模/范围**:
- 4个数据表,约2000行代码
- 3个主要模块(时钟、TodoList、窗口管理)
- 预计支持100+条Todo任务

## 章程检查

*门控: 必须在阶段 0 研究前通过. 阶段 1 设计后重新检查. *

### 初始章程检查 (阶段 0 前)

✅ **I. 用户体验优先**
- PyQt6提供流畅的UI体验和动画效果
- 扁平化设计,去锐利化,符合现代UI标准
- 响应迅速,启动时间<3秒

✅ **II. 简单性**
- 使用Python开发,快速迭代
- SQLite轻量级,无需额外服务
- 避免过度设计,只实现必需功能

✅ **III. 模块化架构**
- 采用MVC + 服务层架构
- 时钟、TodoList、窗口管理三个模块独立
- 清晰的接口定义,低耦合

✅ **IV. 代码质量**
- 使用pytest进行单元测试和集成测试
- 目标测试覆盖率>80%
- 中文注释,Google风格docstring

✅ **V. 可维护性**
- 清晰的分层架构
- SQLAlchemy ORM简化数据库操作
- Alembic管理数据库迁移

### 设计后重新检查 (阶段 1 后)

✅ **架构复杂性合理性**
- MVC + 服务层: 符合桌面应用标准模式,不过度设计
- SQLAlchemy ORM: 比直接SQL更易维护,值得抽象层
- 服务层封装: 业务逻辑与UI分离,便于测试

✅ **无违反章程原则**
- 无不必要的复杂性
- 所有技术选择都有明确理由
- 符合"简单性"和"模块化"原则

## 项目结构

### 文档(此功能)

```
specs/001-tomato-todo-widget/
├── plan.md              # 此文件 (/speckit.plan 命令输出)
├── research.md          # 阶段 0 输出 - 技术栈研究
├── data-model.md        # 阶段 1 输出 - 数据模型设计
├── quickstart.md        # 阶段 1 输出 - 快速开始指南
├── contracts/           # 阶段 1 输出 - API契约
│   └── service-apis.md  # 服务层API定义
├── spec.md              # 功能规范
└── checklists/          # 质量检查清单
    └── requirements.md  # 规范质量检查
```

### 源代码(仓库根目录)

```
src/
├── main.py                      # 应用入口点
├── models/                      # 数据模型层(SQLAlchemy)
│   ├── __init__.py
│   ├── pomodoro_timer.py        # 番茄时钟模型
│   ├── todo_task.py             # Todo任务模型
│   └── user_preferences.py      # 用户偏好模型
├── views/                       # UI组件层(PyQt6)
│   ├── __init__.py
│   ├── main_window.py           # 主窗口
│   ├── pomodoro_widget.py       # 番茄时钟组件
│   ├── todo_widget.py           # TodoList组件
│   ├── timeout_dialog.py        # 全屏倒计时结束提示
│   └── dialogs/                 # 对话框
│       ├── settings_dialog.py   # 设置对话框
│       └── time_set_dialog.py   # 时间设置对话框
├── controllers/                 # 控制器层(连接View和Service)
│   ├── __init__.py
│   ├── pomodoro_controller.py   # 番茄时钟控制器
│   └── todo_controller.py       # Todo控制器
├── services/                    # 业务逻辑层
│   ├── __init__.py
│   ├── pomodoro_service.py      # 番茄时钟业务逻辑
│   ├── todo_service.py          # Todo业务逻辑
│   └── preferences_service.py   # 偏好设置业务逻辑
├── database/                    # 数据库访问层
│   ├── __init__.py
│   ├── connection.py            # 数据库连接管理
│   └── repositories/            # 数据仓库模式
│       ├── __init__.py
│       ├── pomodoro_repository.py
│       └── todo_repository.py
└── utils/                       # 工具函数
    ├── __init__.py
    ├── single_instance.py       # 单实例管理
    ├── validators.py            # 数据验证器
    └── constants.py             # 常量定义

tests/
├── conftest.py                  # pytest配置和fixture
├── unit/                        # 单元测试
│   ├── services/                # 服务层测试
│   │   ├── test_pomodoro_service.py
│   │   └── test_todo_service.py
│   └── utils/                   # 工具函数测试
│       └── test_validators.py
└── integration/                 # 集成测试
    ├── test_database.py         # 数据库集成测试
    └── test_workflows.py        # 端到端工作流测试

assets/                          # 资源文件
├── icon.ico                     # 应用图标
├── styles/
│   └── main.qss                 # 主样式表(扁平化设计)
└── fonts/                       # 自定义字体(如需要)

# 数据目录(运行时在Windows临时目录自动创建)
# %TEMP%\TomatoTodo\
# ├── tomato_todo.db             # SQLite数据库
# └── backup/                    # 数据库备份

scripts/                         # 脚本工具
├── init_db.py                   # 数据库初始化
└── build.py                     # 打包脚本

docs/                            # 文档
├── architecture.md              # 架构说明
└── user_guide.md                # 用户指南

pyproject.toml                   # Poetry配置
README.md                        # 项目说明
LICENSE                          # MIT许可证

# 打包输出
dist/
└── TomatoTodo.exe               # 便携式可执行文件(无需安装)
```

**结构决策**: 选择单一项目结构,因为:
1. 桌面应用不需要前后端分离
2. 所有代码在同一仓库,便于开发和打包
3. 清晰的分层架构(model/view/controller/service)实现模块化

## 复杂度跟踪

*仅在章程检查有必须证明的违规时填写*

| 违规 | 为什么需要 | 拒绝更简单替代方案的原因 |
|-----------|------------|-------------------------------------|
| 服务层(Service Layer) | 封装业务逻辑,使控制器和数据访问分离 | 直接在Controller中操作数据库会导致代码重复,难以测试和复用业务逻辑 |
| 数据仓库模式(Repository) | 抽象数据库访问,便于单元测试 | 直接使用SQLAlchemy Session会导致测试时依赖真实数据库,难以mock |
| SQLAlchemy ORM | 简化数据库操作,提供类型安全 | 原生SQL需要手动处理类型转换和SQL注入风险,代码冗长 |

## 实施路线图

### 阶段 0: 技术研究 ✅ (已完成)
- [x] 选择技术栈: Python + PyQt6 + SQLAlchemy + SQLite
- [x] 架构设计: MVC + 服务层
- [x] 依赖管理: Poetry
- [x] 测试框架: pytest + pytest-qt
- [x] 打包工具: PyInstaller

**输出**: [research.md](./research.md)

### 阶段 1: 设计与合同 ✅ (已完成)
- [x] 数据模型设计: 4个核心表(pomodoro_timer, pomodoro_stats, todo_tasks, user_preferences)
- [x] API契约定义: 服务层接口规范
- [x] 项目结构规划: 分层架构
- [x] 快速开始指南: 开发环境设置

**输出**:
- [data-model.md](./data-model.md)
- [contracts/service-apis.md](./contracts/service-apis.md)
- [quickstart.md](./quickstart.md)

### 阶段 2: 任务分解 (待执行)
运行 `/speckit.tasks` 生成详细的任务列表(tasks.md)

### 阶段 3: 实施 (待执行)
1. **基础设施**
   - 初始化项目结构
   - 配置Poetry和依赖
   - 创建数据库模型
   - 配置pytest

2. **数据库层**
   - 实现数据库连接
   - 实现数据仓库(Repository)
   - 编写数据迁移脚本
   - 添加数据库测试

3. **服务层**
   - 实现PomodoroService
   - 实现TodoService
   - 实现PreferencesService
   - 编写单元测试

4. **UI层**
   - 实现主窗口和布局
   - 实现番茄时钟组件
   - 实现TodoList组件
   - 实现对话框
   - 应用QSS样式

5. **控制器层**
   - 实现PomodoroController
   - 实现TodoController
   - 连接信号和槽

6. **集成与测试**
   - 端到端测试
   - UI自动化测试
   - 性能测试
   - Bug修复

7. **打包与发布**
   - PyInstaller打包配置
   - 创建安装程序
   - 编写用户文档
   - 发布v1.0.0

## 关键里程碑

1. **M1 - 数据库就绪** (预计1周)
   - 数据模型创建
   - 数据库初始化脚本
   - Repository层实现并通过测试

2. **M2 - 核心功能** (预计2周)
   - 番茄时钟完整流程可运行
   - TodoList基本CRUD可用
   - 单元测试覆盖率>80%

3. **M3 - UI完整** (预计3周)
   - 所有UI组件实现
   - 扁平化设计应用
   - 用户交互流畅

4. **M4 - 发布准备** (预计4周)
   - 打包为exe可执行文件
   - 完成文档和测试
   - 性能达标
   - 发布v1.0.0

## 风险与缓解

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| PyQt6学习曲线 | 中 | 低 | 使用官方文档和示例,渐进式开发 |
| 系统休眠时间计算 | 高 | 中 | 使用时间戳校验,记录last_update时间 |
| SQLite并发 | 中 | 低 | 单实例设计,使用文件锁,连接池管理 |
| PyInstaller打包问题 | 中 | 中 | 提前验证打包流程,使用最新稳定版 |
| 性能不达标 | 高 | 低 | 使用连接池,分页加载,UI虚拟化 |

## 下一步

1. 运行 `/speckit.tasks` 生成详细任务列表
2. 开始实施阶段1: 基础设施搭建
3. 创建数据库初始化脚本

---

**计划版本**: 1.0.0
**最后更新**: 2026-01-21
**状态**: 阶段1已完成,等待阶段2任务分解
