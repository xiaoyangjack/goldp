#!/bin/bash

# 安装 GoldQuant 调度器到 launchd

echo "=== GoldQuant 调度器安装脚本 ==="

# 获取当前目录的绝对路径
PROJECT_PATH=$(pwd)

# 获取 Python 路径
PYTHON_PATH=$(which python3)

echo "项目路径: $PROJECT_PATH"
echo "Python 路径: $PYTHON_PATH"

# 检查 main.py 是否存在
if [ ! -f "$PROJECT_PATH/main.py" ]; then
    echo "错误: main.py 不存在。请创建主入口文件。"
    exit 1
fi

# 创建日志目录
mkdir -p "$PROJECT_PATH/data/logs"

# 复制并替换占位符
PLIST_TEMPLATE="$PROJECT_PATH/deploy/com.goldquant.scheduler.plist"
PLIST_DEST="$PROJECT_PATH/deploy/com.goldquant.scheduler.plist"

# 替换占位符
sed -i '' "s|PYTHON_PATH_PLACEHOLDER|$PYTHON_PATH|g" "$PLIST_DEST"
sed -i '' "s|PROJECT_PATH_PLACEHOLDER|$PROJECT_PATH|g" "$PLIST_DEST"

echo "已更新 plist 文件中的路径"

# 复制到 launchd 目录
LAUNCHD_DIR="$HOME/Library/LaunchAgents"
mkdir -p "$LAUNCHD_DIR"
cp "$PLIST_DEST" "$LAUNCHD_DIR/"

echo "已复制 plist 文件到 $LAUNCHD_DIR"

# 加载服务
launchctl load "$LAUNCHD_DIR/com.goldquant.scheduler.plist"

echo "已加载 launchd 服务"

echo "=== 安装完成 ==="
echo "使用以下命令查看服务状态:"
echo "  launchctl list | grep com.goldquant.scheduler"
echo "使用以下命令卸载服务:"
echo "  launchctl unload $LAUNCHD_DIR/com.goldquant.scheduler.plist"
echo "  rm $LAUNCHD_DIR/com.goldquant.scheduler.plist"
