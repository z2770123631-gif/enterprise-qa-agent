@echo off
echo ========================================
echo    企业知识库智能问答Agent 启动脚本
echo ========================================
echo.
echo [1/2] 安装依赖...
pip install -r requirements.txt
echo [2/2] 启动服务...
python main.py
pause
