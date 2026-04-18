#!/bin/bash

# Gold Quant Research System 启动脚本

echo "=== Gold Quant Research System 启动脚本 ==="

# 检查Python环境
echo "检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "错误：未找到Python 3。请安装Python 3.9或更高版本。"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "找到Python版本: $PYTHON_VERSION"

# 检查依赖
echo "检查依赖包..."
if [ ! -f "gold_quant_system/requirements.txt" ]; then
    echo "错误：未找到requirements.txt文件。"
    exit 1
fi

# 安装依赖
echo "安装依赖包..."
python3 -m pip install -r gold_quant_system/requirements.txt

if [ $? -ne 0 ]; then
    echo "警告：依赖安装可能失败，请手动安装依赖后再运行。"
else
    echo "依赖安装成功！"
fi

# 启动GUI
echo "启动Gold Quant Research System GUI..."
python3 gold_quant_system/main.py

if [ $? -ne 0 ]; then
    echo "警告：GUI启动失败，请尝试手动启动。"
    echo "手动启动命令：python3 gold_quant_system/main.py"
fi

echo "=== 启动脚本执行完成 ==="
