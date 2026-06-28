@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   透视壁纸 - 一键打包脚本
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] 检查 Python 环境...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误: 未找到 Python，请先安装 Python 3.8 或更高版本。
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo  ✓ Python 已安装
python --version
echo.

echo [2/4] 安装打包依赖...
python -m pip install --upgrade pip
python -m pip install pyinstaller pywebview
if %errorlevel% neq 0 (
    echo 错误: 依赖安装失败，请检查网络连接。
    pause
    exit /b 1
)
echo  ✓ 依赖安装完成
echo.

echo [3/4] 开始打包...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

pyinstaller ^
    --onefile ^
    --windowed ^
    --name "PerspectiveWallpaper" ^
    --add-data "index.html;." ^
    --add-data "assets;assets" ^
    --add-data "config.json;." ^
    main.py

if %errorlevel% neq 0 (
    echo 错误: 打包失败。
    pause
    exit /b 1
)
echo  ✓ 打包完成
echo.

echo [4/4] 复制配置文件到输出目录...
copy /y "config.json" "dist\config.json" >nul
if not exist "dist\assets" mkdir "dist\assets"
xcopy /y /e /i "assets\*" "dist\assets\" >nul
echo  ✓ 文件复制完成
echo.

echo ========================================
echo   打包成功！
echo ========================================
echo.
echo 输出目录: %cd%\dist
echo 主程序: PerspectiveWallpaper.exe
echo.
echo 分发说明:
echo   1. 将 dist 文件夹压缩为 ZIP
echo   2. 复制到目标电脑解压
echo   3. 双击 PerspectiveWallpaper.exe 运行
echo   4. 如需修改图片，替换 assets 文件夹中的 base.png 和 xray.png
echo.
pause
