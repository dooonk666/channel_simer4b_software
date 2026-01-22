@echo off
chcp 65001 >nul
echo ================================
echo 信道模拟器软件 V0.1
echo 支持24条多径
echo ================================
echo.

REM 首先尝试运行Python版本
echo [1/2] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python未安装，将使用EXE版本
    goto run_exe
)

echo [2/2] 测试PyQt5...
python -c "from PyQt5.QtWidgets import QApplication" >nul 2>&1
if errorlevel 1 (
    echo.
    echo PyQt5无法加载（缺少Visual C++ Redistributable）
    echo.
    echo 选项：
    echo   1. 运行 fix_pyqt5.bat 修复PyQt5问题后使用Python版本
    echo   2. 直接使用EXE版本（推荐）
    echo.
    choice /C 12 /N /M "请选择 [1]修复 [2]使用EXE: "
    if errorlevel 2 goto run_exe
    if errorlevel 1 (
        call fix_pyqt5.bat
        exit /b
    )
)

REM Python版本可用
echo.
echo [成功] Python环境正常，启动程序...
echo.
python main.py
exit /b

:run_exe
echo.
echo [信息] 使用编译版本...
if exist "channel_simer4b_software_V0.1\main.exe" (
    echo 启动: channel_simer4b_software_V0.1\main.exe
    start "" "channel_simer4b_software_V0.1\main.exe"
) else if exist "build\main\main.exe" (
    echo 启动: build\main\main.exe
    start "" "build\main\main.exe"
) else (
    echo.
    echo [错误] 未找到EXE文件
    echo 请确保以下任一文件存在：
    echo   - channel_simer4b_software_V0.1\main.exe
    echo   - build\main\main.exe
    echo.
    pause
    exit /b 1
)

echo.
echo 程序已在后台启动
echo.
timeout /t 3

