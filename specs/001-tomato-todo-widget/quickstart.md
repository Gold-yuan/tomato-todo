# 快速开始指南: 番茄时钟和TodoList桌面小组件

**功能**: 001-tomato-todo-widget
**创建时间**: 2026-01-21
**目标用户**: 开发者

---

## 环境要求

### 必需软件

- **Python**: 3.11 或更高版本
- **操作系统**: Windows 10 或更高版本
- **Git**: 用于克隆代码仓库

### 推荐工具

- **Poetry**: 依赖管理和虚拟环境
- **VS Code**: 代码编辑器(推荐插件: Python, PyQt)
- **SQLite Browser**: 数据库可视化工具

---

## 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/your-org/tomato-todo.git
cd tomato-todo
git checkout 001-tomato-todo-widget
```

### 2. 安装Poetry(如果未安装)

```bash
# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# 验证安装
poetry --version
```

### 3. 安装依赖

```bash
# 创建虚拟环境并安装依赖
poetry install

# 激活虚拟环境
poetry shell
```

### 4. 初始化数据库

```bash
# 运行数据库迁移脚本
python scripts/init_db.py
```

数据库文件将创建在 `%TEMP%\TomatoTodo\tomato_todo.db` (Windows临时目录)

---

## 运行应用

### 开发模式

```bash
# 运行应用
poetry run python src/main.py
```

### 打包为可执行文件

```bash
# 使用PyInstaller打包
poetry run pyinstaller --onefile --windowed --icon=assets/icon.ico --name="TomatoTodo" src/main.py

# 可执行文件位于 dist/TomatoTodo.exe
```

**使用说明**:
- `TomatoTodo.exe` 是便携式应用,无需安装
- 双击直接运行
- 数据自动存储在Windows临时目录 (`%TEMP%\TomatoTodo\`)
- 卸载时直接删除exe文件即可(数据需手动清理)

---

## 项目结构

```
tomato-todo/
├── src/                       # 源代码
│   ├── main.py                # 应用入口
│   ├── models/                # 数据模型
│   │   ├── __init__.py
│   │   ├── pomodoro_timer.py  # 番茄时钟模型
│   │   ├── todo_task.py       # Todo任务模型
│   │   └── user_preferences.py # 用户偏好模型
│   ├── views/                 # UI组件
│   │   ├── __init__.py
│   │   ├── main_window.py     # 主窗口
│   │   ├── pomodoro_widget.py # 番茄时钟组件
│   │   ├── todo_widget.py     # TodoList组件
│   │   └── dialogs/           # 对话框
│   │       ├── settings_dialog.py
│   │       └── time_set_dialog.py
│   ├── controllers/           # 控制器
│   │   ├── __init__.py
│   │   ├── pomodoro_controller.py
│   │   └── todo_controller.py
│   ├── services/              # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── pomodoro_service.py
│   │   ├── todo_service.py
│   │   └── preferences_service.py
│   ├── database/              # 数据库访问层
│   │   ├── __init__.py
│   │   ├── connection.py      # 数据库连接
│   │   └── repositories/      # 数据仓库
│   │       ├── pomodoro_repository.py
│   │       └── todo_repository.py
│   └── utils/                 # 工具函数
│       ├── __init__.py
│       ├── single_instance.py # 单实例管理
│       └── validators.py      # 数据验证
├── tests/                     # 测试
│   ├── unit/                  # 单元测试
│   ├── integration/           # 集成测试
│   └── conftest.py            # pytest配置
├── assets/                    # 资源文件
│   ├── icon.ico               # 应用图标
│   └── styles/                # QSS样式文件
│       └── main.qss           # 主样式
├── scripts/                   # 脚本
│   ├── init_db.py             # 数据库初始化
│   └── build.py               # 打包脚本
├── docs/                      # 文档
│   └── architecture.md        # 架构说明
├── pyproject.toml             # Poetry配置
└── README.md                  # 项目说明
```

---

## 开发指南

### 添加新功能

1. **定义数据模型** (`src/models/`)
   - 创建SQLAlchemy模型类
   - 添加验证规则

2. **创建数据仓库** (`src/database/repositories/`)
   - 实现数据库访问方法
   - 编写单元测试

3. **实现业务逻辑** (`src/services/`)
   - 封装业务规则
   - 编写集成测试

4. **创建UI组件** (`src/views/`)
   - 设计PyQt6组件
   - 连接信号和槽

5. **编写控制器** (`src/controllers/`)
   - 连接View和Service
   - 处理用户交互

### 代码规范

- **命名**: 使用snake_case(变量、函数)和PascalCase(类)
- **注释**: 中文注释,说明业务逻辑
- **类型注解**: 使用Python类型提示
- **文档字符串**: Google风格docstring

示例:

```python
class PomodoroService:
    """番茄时钟业务逻辑服务"""

    def start_timer(self, duration: int) -> PomodoroTimer:
        """
        启动番茄时钟

        Args:
            duration: 倒计时时长(秒)

        Returns:
            PomodoroTimer: 创建的番茄时钟实例

        Raises:
            ValueError: 如果duration不在有效范围内
        """
        if not 60 <= duration <= 7200:
            raise ValueError("时长必须在60秒到7200秒之间")

        # 业务逻辑...
```

### 测试

```bash
# 运行所有测试
poetry run pytest

# 运行单元测试
poetry run pytest tests/unit

# 运行集成测试
poetry run pytest tests/integration

# 生成覆盖率报告
poetry run pytest --cov=src --cov-report=html
```

---

## 常见问题

### Q1: 数据库文件在哪里?

**A**: 数据库文件位于Windows临时目录:
- `C:\Users\<用户名>\AppData\Local\Temp\TomatoTodo\tomato_todo.db`
- 或通过环境变量: `%TEMP%\TomatoTodo\tomato_todo.db`
- 首次运行应用时会自动创建目录和数据库

### Q2: 如何重置应用数据?

**A**:
```bash
# 删除整个应用数据目录
rmdir /s %TEMP%\TomatoTodo

# 或只删除数据库文件
del %TEMP%\TomatoTodo\tomato_todo.db

# 重新启动应用,会自动创建新的数据库
```

### Q3: 应用无法启动,提示"应用已在运行"?

**A**: 检查任务管理器,关闭已运行的TomatoTodo.exe进程。或者删除临时锁文件:
```bash
del %TEMP%\TomatoTodo.lock
```

### Q4: 如何自定义主题?

**A**: 编辑 `assets/styles/main.qss` 文件,修改颜色和样式定义。

### Q5: 如何查看数据库内容?

**A**: 使用DB Browser for SQLite(https://sqlitebrowser.org/)打开数据库文件:
- `%TEMP%\TomatoTodo\tomato_todo.db`
- 或在应用中添加"数据备份"功能,备份到桌面后查看

---

## 调试技巧

### 启用调试日志

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)
```

### PyQt调试模式

```bash
# 启用Qt调试输出
set QT_LOGGING_RULES=*.debug=true
poetry run python src/main.py
```

### SQL查询日志

```python
# 在database/connection.py中启用SQL日志
import tempfile
app_dir = os.path.join(tempfile.gettempdir(), 'TomatoTodo')
db_path = os.path.join(app_dir, 'tomato_todo.db')

engine = create_engine(
    f'sqlite:///{db_path}',
    echo=True  # 打印所有SQL查询
)
```

---

## 性能优化建议

1. **使用连接池**: SQLAlchemy已配置连接池
2. **懒加载**: TodoList使用分页加载
3. **避免过度查询**: 使用select_related预加载关联数据
4. **UI虚拟化**: QListWidget使用虚拟模式处理大量数据

---

## 部署

### 打包发布

```bash
# 1. 更新版本号(pyproject.toml)
# 2. 运行打包脚本
python scripts/build.py

# 3. 测试可执行文件
dist/TomatoTodo.exe

# 4. 创建安装包(使用NSIS或Inno Setup)
```

### 分发方式

- **直接下载**: 提供exe文件下载
- **便携版**: 解压即用,无需安装
- **安装版**: 使用NSIS制作安装程序

---

## 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

### 代码审查清单

- [ ] 遵循代码规范
- [ ] 添加单元测试(覆盖率>80%)
- [ ] 更新文档
- [ ] 通过所有测试
- [ ] 无性能回退

---

## 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件

---

## 联系方式

- 项目主页: https://github.com/your-org/tomato-todo
- 问题反馈: https://github.com/your-org/tomato-todo/issues
- 邮箱: your-email@example.com

---

**祝您开发愉快!** 🍅
