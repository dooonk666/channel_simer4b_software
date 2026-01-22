@echo off
chcp 65001 >nul
echo ================================
echo PyQt5 DLL问题修复工具
echo ================================
echo.
echo 此工具将帮助您解决PyQt5的DLL加载错误
echo.
echo 正在检查Python和PyQt5安装...
python --version
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.7-3.11
    pause
    exit /b 1
)
echo.

echo 正在测试PyQt5...
python test_pyqt5.py
if errorlevel 1 (
    echo.
    echo [警告] PyQt5无法正常加载
    echo.
    echo 可能的原因：缺少Visual C++ Redistributable运行库
    echo.
    echo 解决方案：
    echo 1. 下载并安装 Visual C++ 2015-2022 Redistributable (x64)
    echo    下载地址: https://aka.ms/vs/17/release/vc_redist.x64.exe
    echo.
    echo 2. 下载并安装 Visual C++ 2013 Redistributable (x64)
    echo    下载地址: https://aka.ms/highdpimfc2013x64enu
    echo.
    echo 是否现在打开下载页面？
    choice /C YN /M "输入Y���开浏览器，N跳过"
    if errorlevel 2 goto skip_download
    if errorlevel 1 (
        start https://aka.ms/vs/17/release/vc_redist.x64.exe
        echo.
        echo 请安装完成后重新运行此脚本
    )
    :skip_download
) else (
    echo.
    echo [成功] PyQt5工作正常！
    echo.
    echo 您可以运行主程序了：
    echo python main.py
)

echo.
pause

