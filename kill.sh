#!/bin/bash

# 查找并终止所有运行中的 main.py 进程
echo "Killing all main.py processes..."
pkill -f "python main.py"

# 检查是否成功终止
if [ $? -eq 0 ]; then
    echo "All main.py processes have been killed successfully."
else
    echo "No main.py processes found or unable to kill processes."
fi
