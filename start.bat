@echo off

:: Gold Quant Research System 启动脚本

echo === Gold Quant Research System 启动脚本 ===

:: 检查Python环境
echo 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未找到Python。请安装Python 3.9或更高版本。
    pause
    exit /b 1
)

python --version

:: 检查依赖
echo 检查依赖包...
if not exist "gold_quant_system\requirements.txt" (
    echo 错误：未找到requirements.txt文件。
    pause
    exit /b 1
)

:: 安装依赖
echo 安装依赖包...
pip install -r gold_quant_system\requirements.txt

if %errorlevel% neq 0 (
    echo 警告：依赖安装可能失败，请手动安装依赖后再运行。
) else (
    echo 依赖安装成功！
)

:: 启动GUI
echo 启动Gold Quant Research System GUI...
python gold_quant_system\main.py

if %errorlevel% neq 0 (
    echo 警告：GUI启动失败，请尝试手动启动。
    echo 手动启动命令：python gold_quant_system\main.py
)

echo === 启动脚本执行完成 ===
pause
