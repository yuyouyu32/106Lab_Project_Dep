#!/bin/bash

# 获取脚本所在目录，并设置环境变量 LABDEVDIR
export LABDEVDIR=$(pwd)
echo "LABDEVDIR is set to $LABDEVDIR"

# 遍历当前目录下的所有文件夹
for dir in */ ; do
    # 检查 main.py 是否存在于该文件夹中
    if [ -f "$dir/main.py" ]; then
        echo "Starting main.py in directory $dir"
        
        # 后台运行 main.py 并将日志重定向到 main.log
        (cd "$dir" && nohup python main.py > main.log 2>&1 &)
        
        echo "main.py in $dir is running in the background. Logs are being saved to $dir/main.log"
    else
        echo "No main.py in $dir, skipping..."
    fi
done
