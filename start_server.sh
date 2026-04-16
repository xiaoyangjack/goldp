#!/bin/bash
# 黄金量化 Web应用 一键启动脚本
# Phase 3 - 优化版

set -e

cd "$(dirname "$0")"

echo "================================================"
echo "🎯 黄金量化交易系统启动脚本"
echo "================================================"

# 检查Python版本
echo "🔍 检查Python环境..."
python3 --version || {
    echo "❌ 错误: Python 3 未安装"
    exit 1
}

# 检查并创建虚拟环境
if [ ! -d "gold_quant_env" ]; then
    echo "📦 未找到虚拟环境，正在创建..."
    python3 -m venv gold_quant_env
    echo "✅ 虚拟环境创建成功"
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source gold_quant_env/bin/activate

# 升级pip
echo "📡 升级pip..."
pip install --upgrade pip > /dev/null 2>&1

# 检查并安装依赖
echo "📦 检查依赖..."
if [ -f "requirements.txt" ]; then
    echo "🔄 安装依赖包..."
    # 先确保 NumPy / Numba 版本兼容 vectorbt（避免 NumPy 2.x 导致 numba/vectorbt 失效）
    pip install -U "numpy<2" "numba<0.60"
    pip install -r requirements.txt
    echo "✅ 依赖安装完成"
else
    echo "⚠️  未找到 requirements.txt，安装基本依赖..."
    pip install flask pandas numpy requests plotly apscheduler loguru python-dotenv
    echo "✅ 基本依赖安装完成"
fi

# 检查必要的目录
echo "📁 检查目录结构..."
mkdir -p data logs

# 检查端口占用
echo "🔌 检查端口 5555..."
if lsof -i :5555 > /dev/null 2>&1; then
    echo "⚠️  端口 5555 已被占用，正在尝试停止占用进程..."
    pkill -f "python.*web_app.py" 2>/dev/null
    sleep 2
    if lsof -i :5555 > /dev/null 2>&1; then
        echo "❌ 错误: 端口 5555 仍被占用"
        exit 1
    fi
    echo "✅ 端口已释放"
fi

# 启动服务器
echo ""
echo "🚀 启动黄金量化Web服务..."
echo "================================================"
echo "📍 访问地址: http://127.0.0.1:5555"
echo "📊 健康检查: http://127.0.0.1:5555/health"
echo "📖 按 Ctrl+C 停止服务"
echo "================================================"
echo ""

# trap捕获Ctrl+C信号，自动关闭Python进程
trap 'echo ""; echo "🛑 正在关闭服务..."; pkill -f "python.*web_app.py" 2>/dev/null; exit 0' INT TERM

# 启动应用
python web_app.py

# 等待进程结束
wait
