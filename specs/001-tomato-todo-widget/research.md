# 技术研究: 番茄时钟和TodoList桌面小组件

**功能**: 001-tomato-todo-widget
**创建时间**: 2026-01-21
**研究目标**: 确定Windows桌面应用开发的最佳技术栈和架构

---

## 1. 编程语言和框架选择

### 决策: **Python + PyQt6 (PySide6)**

**理由**:
- **跨平台能力**: Python + PyQt6 虽然当前针对 Windows 10+,但未来可轻松扩展到 macOS 和 Linux
- **成熟稳定**: PyQt6 是成熟的桌面应用框架,拥有丰富的组件和良好的文档
- **自定义窗口**: PyQt6 支持无边框窗口、自定义窗口样式、透明度和动画效果,满足扁平化设计需求
- **快速开发**: Python 开发效率高,适合快速迭代和原型验证
- **社区支持**: 庞大的社区,丰富的第三方库,易于解决问题
- **SQLite集成**: Python 内置 sqlite3 模块,集成简单高效

**备选方案考虑**:
- **Electron + JavaScript/TypeScript**: 跨平台但资源占用大(>100MB内存),不符合章程的性能要求
- **C# + WPF**: Windows原生,性能好,但跨平台支持差,.NET MAUI还不够成熟
- **Flutter Desktop**: 跨平台,但 Windows 桌面支持还在beta阶段,不稳定
- **Tauri + Rust**: 轻量级,但生态不成熟,学习曲线陡峭

### 技术栈版本
- **Python**: 3.11 (LTS,性能和稳定性平衡)
- **PyQt6**: 6.6.0+ (最新稳定版)
- **SQLite**: 3.40+ (Python内置)

---

## 2. UI框架和设计系统

### 决策: **PyQt6原生组件 + QSS样式表**

**理由**:
- **扁平化设计**: 使用QSS(Qt Style Sheets)实现扁平化、圆角、柔和阴影效果
- **自定义窗口**: 使用 `Qt.FramelessWindowHint` 实现无边框窗口
- **动画效果**: 使用 `QPropertyAnimation` 实现渐隐渐显、缩放等动画
- **组件丰富**: QLabel、QPushButton、QListWidget、QLineEdit 等组件满足所有UI需求
- **样式隔离**: QSS类似CSS,易于维护和统一设计风格

**设计规范**:
- **圆角**: 8px (按钮、卡片)
- **阴影**: `box-shadow: 0 2px 8px rgba(0,0,0,0.1)`
- **字体**: Microsoft YaHei UI (微软雅黑), 14px 基础字号
- **颜色**:
  - 主色: #E74C3C (番茄红)
  - 背景色: #F5F6FA (浅灰)
  - 文本色: #2C3E50 (深灰)
  - 边框色: #BDC3C7 (中灰)
  - 成功色: #27AE60 (绿色)

---

## 3. 数据持久化方案

### 决策: **SQLite + SQLAlchemy**

**理由**:
- **轻量级**: SQLite 是嵌入式数据库,无需额外服务,符合章程的简单性原则
- **性能**: 对于TodoList和用户偏好,SQLite性能完全满足需求(<10ms查询)
- **事务支持**: ACID特性保证数据一致性
- **ORM**: SQLAlchemy提供ORM,简化数据库操作,代码更易维护
- **备份简单**: 单文件数据库,易于备份和迁移

**数据库设计**:
```
database/tomato_todo.db
├── pomodoro_timer (番茄时钟状态和历史)
├── todo_tasks (Todo任务)
├── user_preferences (用户偏好)
└── pomodoro_stats (统计数据)
```

---

## 4. 架构模式

### 决策: **MVC + 服务层架构**

**理由**:
- **模块化**: 符合章程原则III - 模块化架构
- **职责分离**: Model(数据)、View(UI)、Controller(逻辑)、Service(业务)
- **可测试性**: 各层独立,易于单元测试和集成测试
- **可维护性**: 清晰的分层结构,易于理解和修改

**架构层次**:
```
src/
├── models/          # 数据模型(SQLAlchemy)
├── views/           # UI组件(PyQt6)
├── controllers/     # 控制器(连接View和Service)
├── services/        # 业务逻辑层
├── database/        # 数据库访问层
└── utils/           # 工具函数
```

---

## 5. 单实例实现方案

### 决策: **Qt单例模式 + 文件锁**

**理由**:
- **跨平台**: 使用QFile锁机制,Windows/Linux/macOS通用
- **简单可靠**: 启动时尝试创建锁文件,失败则提示已有实例运行
- **资源保护**: 防止多实例同时修改SQLite数据库

**实现方式**:
```python
import os
from PyQt6.QtCore import QLockFile

LOCK_FILE = os.path.join(tempfile.gettempdir(), 'tomato_todo.lock')
lock = QLockFile(LOCK_FILE)
if not.lock.tryLock(100):
    sys.exit("应用已在运行")
```

---

## 6. 系统休眠/锁定处理

### 决策: **Windows API + 时间戳校验**

**理由**:
- **精度**: 记录开始时间戳,恢复时计算实际经过时间
- **容错**: 使用`ctypes`调用Windows API检测休眠事件
- **简单**: 不需要复杂的后台线程,仅需定时器触发时校验

**实现方式**:
```python
import time
start_time = time.time()
# 休眠后恢复
elapsed = time.time() - start_time
remaining = target_duration - elapsed
```

---

## 7. 测试框架

### 决策: **pytest + pytest-qt**

**理由**:
- **Python标准**: pytest是Python最流行的测试框架
- **Qt支持**: pytest-qt提供Qt特定的测试工具和fixture
- **覆盖率**: pytest-cov生成代码覆盖率报告
- **简单**: 装饰器和断言语法简洁易读

**测试策略**:
- **单元测试**: 测试Service层业务逻辑(目标覆盖率>80%)
- **集成测试**: 测试数据库访问和数据模型
- **UI测试**: 使用pytest-qt模拟用户交互(关键流程)

---

## 8. 打包和分发

### 决策: **PyInstaller**

**理由**:
- **单文件**: 可打包为单个exe文件,用户无需安装Python
- **图标支持**: 支持自定义应用图标
- **启动速度快**: 相比其他打包工具,PyInstaller启动速度较快
- **社区广泛**: 成熟稳定,文档丰富

**打包命令**:
```bash
pyinstaller --onefile --windowed --icon=assets/icon.ico --name="TomatoTodo" src/main.py
```

---

## 9. 性能优化策略

### 关键决策:

1. **数据库连接池**: 使用SQLAlchemy连接池,避免频繁打开关闭连接
2. **懒加载**: TodoList分页加载,仅加载当前页数据
3. **定时器优化**: 使用QTimer而不是线程,减少资源占用
4. **UI渲染**: 启用Qt的垂直同步,避免过度绘制

---

## 10. 依赖管理

### 决策: **poetry**

**理由**:
- **锁文件**: poetry.lock确保依赖版本一致性
- **虚拟环境**: 自动管理虚拟环境
- **发布简单**: 一键构建和发布到PyPI

**核心依赖**:
```
[tool.poetry.dependencies]
python = "^3.11"
PyQt6 = "^6.6.0"
SQLAlchemy = "^2.0.0"
pytest = "^7.4.0"
pytest-qt = "^4.2.0"
pyinstaller = "^6.0.0"
```

---

## 总结

### 最终技术栈

| 层次 | 技术 | 版本 |
|------|------|------|
| 语言 | Python | 3.11+ |
| UI框架 | PyQt6 | 6.6.0+ |
| ORM | SQLAlchemy | 2.0+ |
| 数据库 | SQLite | 3.40+ |
| 测试 | pytest + pytest-qt | 7.4.0+ |
| 打包 | PyInstaller | 6.0+ |
| 依赖管理 | poetry | latest |

### 架构决策

- **模式**: MVC + 服务层
- **数据库**: SQLite + SQLAlchemy ORM
- **UI**: PyQt6原生组件 + QSS样式
- **测试**: pytest单元测试 + 集成测试
- **打包**: PyInstaller单文件exe

### 符合章程验证

✅ **用户体验优先**: PyQt6提供流畅的UI体验
✅ **简单性**: Python开发效率高,SQLite轻量级
✅ **模块化架构**: MVC模式清晰分层
✅ **代码质量**: pytest测试保证质量
✅ **可维护性**: 清晰的架构和中文注释
