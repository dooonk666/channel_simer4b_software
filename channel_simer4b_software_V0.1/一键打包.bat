@echo off
chcp 65001 >nul
echo ========================================
echo   PyInstaller 自动打包脚本
echo ========================================
echo.

cd /d "%~dp0"

echo [1/5] 清理旧的构建文件...
if exist build rmdir /s /q build
if exist dist\ChannelSimulator rmdir /s /q dist\ChannelSimulator
echo 完成！
echo.

echo [2/5] 开始打��...
pyinstaller ChannelSimulator.spec --clean
if %errorlevel% neq 0 (
    echo.
    echo ❌ 打包失败！请检查错误信息。
    pause
    exit /b 1
)
echo 完成！
echo.

echo [3/5] 复制文档文件...
copy /Y FRAME_STRUCTURE.md dist\ChannelSimulator\ >nul
copy /Y DEBUG_GUIDE.md dist\ChannelSimulator\ >nul
copy /Y CONFIG_IMPORT_README.md dist\ChannelSimulator\ >nul
echo 完成！
echo.

echo [4/5] 创建启动脚本...
echo @echo off > dist\ChannelSimulator\启动程序.bat
echo chcp 65001 ^>nul >> dist\ChannelSimulator\启动程序.bat
echo echo ======================================== >> dist\ChannelSimulator\启动程序.bat
echo echo   信道模拟器控制软件 V0.1 >> dist\ChannelSimulator\启动程序.bat
echo echo ======================================== >> dist\ChannelSimulator\���动程序.bat
echo echo. >> dist\ChannelSimulator\启动程序.bat
echo echo 正在启动程序... >> dist\ChannelSimulator\启动程序.bat
echo echo. >> dist\ChannelSimulator\启动程序.bat
echo cd /d "%%~dp0" >> dist\ChannelSimulator\启动程序.bat
echo start "" "ChannelSimulator.exe" >> dist\ChannelSimulator\启动程序.bat
echo echo. >> dist\ChannelSimulator\启动程序.bat
echo echo 程序已启动！ >> dist\ChannelSimulator\启动程序.bat
echo echo. >> dist\ChannelSimulator\启动程序.bat
echo timeout /t 2 ^>nul >> dist\ChannelSimulator\启动程序.bat
echo 完成！
echo.

echo [5/5] 获取文件信息...
cd dist\ChannelSimulator
for /f %%A in ('powershell -command "(Get-ChildItem -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB"') do set size=%%A
cd ..\..
echo 打包文件夹大小: %size% MB
echo.

echo ========================================
echo ✅ 打包完成！
echo ========================================
echo.
echo 输出目录: dist\ChannelSimulator\
echo 主程序: ChannelSimulator.exe
echo.
echo 可以将 ChannelSimulator 文件夹直接分发到其他电脑使用。
echo.
pause

