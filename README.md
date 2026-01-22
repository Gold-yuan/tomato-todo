# 番茄时钟和TodoList桌面小组件

一个简洁的Windows桌面小组件，结合番茄工作法和任务管理功能。

## 功能特性

- 番茄时钟：25分钟工作/5分钟休息循环
- TodoList管理：创建、编辑、删除、完成任务
- 窗口管理：悬浮置顶、靠边对齐、可调整大小
- 扁平化设计：圆角、柔和阴影、现代化UI

## 技术栈

- Python 3.11+
- PyQt6
- SQLAlchemy
- SQLite

## 安装

```bash
# 安装依赖
poetry install

# 运行应用
poetry run python src/main.py
```

## 开发

```bash
# 运行测试
poetry run pytest

# 代码格式化
poetry run black .

# 代码检查
poetry run flake8 src/
poetry run pylint src/
```

## 许可证

MIT License
