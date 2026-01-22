#!/bin/bash

# 阶段4 TodoList任务 (T048-T068)
for i in 048 049 050 051 052 053 054 055 056 057 058 059 060 061 062 063 064 065 066 067 068; do
    sed -i "s/^- \[ \] T$i \([P ]\]/- [X] T$i \1/" tasks.md
done

# 阶段5 窗口管理任务 (T069-T077)
for i in 069 070 071 072 073 074 075 076 077; do
    sed -i "s/^- \[ \] T$i \([P ]\)/- [X] T$i \1/" tasks.md
done

echo "已标记完成的任务"
