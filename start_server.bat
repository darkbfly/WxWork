@echo off
chcp 65001 >nul
echo ========================================
echo 企业微信回调验证接口启动脚本
echo ========================================
echo.

REM 配置企业微信参数（请根据实际情况修改）
set WXWORK_TOKEN=R9IWIpiQRVu69BYc2f
set WXWORK_ENCODING_AES_KEY=tEbtRwiBp1UAIXZXrAIhvTBVS5IUku4ICc22dL1roLx
set WXWORK_CORP_ID=wwd7a3b0c978473076

REM 检查参数是否已配置
if "%WXWORK_TOKEN%"=="your_token_here" (
    echo [警告] 请修改此脚本中的 WXWORK_TOKEN 配置
)
if "%WXWORK_ENCODING_AES_KEY%"=="your_encoding_aes_key_here" (
    echo [警告] 请修改此脚本中的 WXWORK_ENCODING_AES_KEY 配置
)
if "%WXWORK_CORP_ID%"=="your_corp_id_here" (
    echo [警告] 请修改此脚本中的 WXWORK_CORP_ID 配置
)
echo.

REM 显示配置信息
echo 当前配置:
echo   Token: %WXWORK_TOKEN%
echo   EncodingAESKey: %WXWORK_ENCODING_AES_KEY:~0,20%...
echo   CorpID: %WXWORK_CORP_ID%
echo   端口: 7777
echo.

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python
    pause
    exit /b 1
)

echo.
echo ========================================
echo 启动服务中...
echo 服务地址: http://localhost:6666
echo 验证接口: http://localhost:6666/
echo 健康检查: http://localhost:6666/health
echo ========================================
echo 按 Ctrl+C 停止服务
echo.

REM 启动 FastAPI 服务，端口 6666
python -m uvicorn fastapi_callback:app --host 0.0.0.0 --port 6666

pause
