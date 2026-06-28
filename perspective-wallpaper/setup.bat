@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   透视壁纸 - 一键配置脚本
echo ========================================
echo.

cd /d "%~dp0"
set "APP_DIR=%cd%"
set "APP_EXE=%APP_DIR%\PerspectiveWallpaper.exe"
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "DESKTOP_DIR=%USERPROFILE%\Desktop"
set "SHORTCUT_NAME=透视壁纸.lnk"

if not exist "%APP_EXE%" (
    set "USE_SOURCE=1"
    set "APP_EXE=%APP_DIR%\main.py"
) else (
    set "USE_SOURCE=0"
)

echo 当前目录: %APP_DIR%
echo.

echo [1/4] 检查运行环境...
if "%USE_SOURCE%"=="1" (
    where python >nul 2>nul
    if %errorlevel% neq 0 (
        echo 错误: 未找到 Python，请先安装 Python 3.8 或更高版本。
        echo 下载地址: https://www.python.org/downloads/
        pause
        exit /b 1
    )
    echo  ✓ Python 已安装
) else (
    echo  ✓ 检测到打包好的 exe 文件
)
echo.

echo [2/4] 安装依赖...
if "%USE_SOURCE%"=="1" (
    python -m pip install --upgrade pip
    python -m pip install pywebview
    if %errorlevel% neq 0 (
        echo 警告: 依赖安装失败，程序可能无法正常运行。
    ) else (
        echo  ✓ 依赖安装完成
    )
) else (
    echo  ✓ 无需安装依赖
)
echo.

echo [3/4] 创建桌面快捷方式...
set "SCRIPT=%TEMP%\create_shortcut.vbs"
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%SCRIPT%"
echo sLinkFile = "%DESKTOP_DIR%\%SHORTCUT_NAME%" >> "%SCRIPT%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%SCRIPT%"
if "%USE_SOURCE%"=="1" (
    echo oLink.TargetPath = "pythonw.exe" >> "%SCRIPT%"
    echo oLink.Arguments = """%APP_EXE%""" >> "%SCRIPT%"
) else (
    echo oLink.TargetPath = "%APP_EXE%" >> "%SCRIPT%"
    echo oLink.Arguments = "" >> "%SCRIPT%"
)
echo oLink.WorkingDirectory = "%APP_DIR%" >> "%SCRIPT%"
echo oLink.Description = "透视壁纸 - 鼠标透视效果桌面壁纸" >> "%SCRIPT%"
echo oLink.WindowStyle = 7 >> "%SCRIPT%"
echo oLink.Save >> "%SCRIPT%"
cscript //nologo "%SCRIPT%"
del "%SCRIPT%"
echo  ✓ 桌面快捷方式已创建
echo.

echo [4/4] 配置开机自启动...
set "STARTUP_LNK=%STARTUP_DIR%\%SHORTCUT_NAME%"
set "SCRIPT2=%TEMP%\create_startup.vbs"
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%SCRIPT2%"
echo sLinkFile = "%STARTUP_LNK%" >> "%SCRIPT2%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%SCRIPT2%"
if "%USE_SOURCE%"=="1" (
    echo oLink.TargetPath = "pythonw.exe" >> "%SCRIPT2%"
    echo oLink.Arguments = """%APP_EXE%""" >> "%SCRIPT2%"
) else (
    echo oLink.TargetPath = "%APP_EXE%" >> "%SCRIPT2%"
    echo oLink.Arguments = "" >> "%SCRIPT2%"
)
echo oLink.WorkingDirectory = "%APP_DIR%" >> "%SCRIPT2%"
echo oLink.Description = "透视壁纸 - 开机自启动" >> "%SCRIPT2%"
echo oLink.WindowStyle = 7 >> "%SCRIPT2%"
echo oLink.Save >> "%SCRIPT2%"
cscript //nologo "%SCRIPT2%"
del "%SCRIPT2%"
echo  ✓ 开机自启动已配置
echo.

echo ========================================
echo   配置完成！
echo ========================================
echo.
echo 使用说明:
echo   - 桌面快捷方式: 双击 "透视壁纸" 启动
echo   - 开机自启动: 已配置，重启后自动运行
echo   - 按 H 键显示/隐藏调节面板
echo   - 替换图片: 修改 assets\base.png 和 assets\xray.png
echo   - 退出程序: 在任务管理器中结束进程
echo.
echo 是否立即启动程序？
set /p "choice=输入 Y 启动，其他键退出: "
if /i "%choice%"=="Y" (
    echo 正在启动...
    if "%USE_SOURCE%"=="1" (
        start "" pythonw.exe "%APP_EXE%"
    ) else (
        start "" "%APP_EXE%"
    )
)

endlocal
