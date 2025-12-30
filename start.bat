@echo off
echo 🚀 启动Smart Custom AST-TTS项目
echo.

cd /d d:\pycharmWorkspace\smart_custom

echo 📋 检查项目文件...
if exist requirements.txt (
    echo ✅ requirements.txt 存在
) else (
    echo ❌ requirements.txt 不存在
    pause
    exit /b 1
)

if exist .env (
    echo ✅ .env 文件存在
) else (
    echo ⚠️  .env 文件不存在
)

echo.
echo 🔧 安装依赖...
pip install -r requirements.txt

echo.
echo 🚀 启动服务...
python main.py

pause