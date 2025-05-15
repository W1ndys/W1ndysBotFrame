#!/bin/bash
dos2unix "$0"

# 进入当前目录的app目录
cd "$(dirname "$0")/app"

# 检查PID文件是否存在
if [ -f app.pid ]; then
    # 读取PID
    PID=$(cat app.pid)

    # 检查进程是否存在
    if ps -p $PID >/dev/null; then
        echo "杀死进程 $PID"
        kill $PID
    else
        echo "进程 $PID 不存在，直接启动新进程"
    fi

    # 删除PID文件
    rm app.pid
else
    echo "PID文件不存在，直接启动新进程"
fi

# 检查虚拟环境是否存在
if [ -d "../venv/bin" ]; then
    echo "虚拟环境存在，激活虚拟环境..."
    # 激活虚拟环境
    . "../venv/bin/activate"
else
    echo "虚拟环境不存在，使用系统Python环境..."
fi

# 启动Python程序并捕获错误
nohup python main.py >app.log 2> >(tee -a app.log) &

# 保存新的PID到文件
echo $! >app.pid

echo "Python程序已启动，新的PID保存在app/app.pid中"

find /home/bot/app/scripts \( -name ".git" -o -name ".gitignore" -o -name ".gitmodules" -o -name ".gitattributes" \) -exec rm -rf {} +

echo "已删除git相关文件"
