@echo off
chcp 65001 >nul
title End70 爬虫定时任务

echo ========================================
echo   End70 爬虫定时任务
echo   每小时执行一次
echo   按 Ctrl+C 停止
echo ========================================
echo.

:loop
echo [%date% %time%] 开始执行爬虫...
cd /d "c:\project\watcher\End70"

:: 执行爬虫脚本
python scrape_endclothing.py

if %errorlevel% neq 0 (
    echo [%date% %time%] 爬虫执行失败，跳过上传
    goto wait
)

echo [%date% %time%] 爬虫执行完成，准备上传...

:: 上传到 GitHub
git add endclothing_70off.json data.js
git diff --staged --quiet
if %errorlevel% neq 0 (
    git commit -m "Update product data - %date% %time%"
    git push origin main
    echo [%date% %time%] 数据已上传，等待 GitHub Pages 自动部署...
) else (
    echo [%date% %time%] 数据无变化，跳过上传
)

:wait
echo.
echo [%date% %time%] 下次执行时间: 1小时后
echo ----------------------------------------

:: 等待1小时 (3600秒)
timeout /t 3600 /nobreak

goto loop
