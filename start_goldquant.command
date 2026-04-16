#!/bin/bash
# 黄金量化一键启动脚本

# 获取当前目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 激活虚拟环境并启动服务
cd "$PROJECT_DIR/GoldQuant"

# 激活虚拟环境
if [ -f "../gold_quant_env/bin/activate" ]; then
    source ../gold_quant_env/bin/activate
elif [ -f "gold_quant_env/bin/activate" ]; then
    source gold_quant_env/bin/activate
fi

# 启动Flask服务
python web_app.py
