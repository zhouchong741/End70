#!/bin/bash

# End70 爬虫定时任务
# 每小时执行一次

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 自动激活虚拟环境（如果存在）
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✓ 已激活虚拟环境"
fi

echo "========================================"
echo "  End70 爬虫定时任务"
echo "  每小时执行一次"
echo "  按 Ctrl+C 停止"
echo "========================================"
echo ""

while true; do
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始执行爬虫..."
    
    # 执行爬虫脚本
    python3 scrape_endclothing.py
    
    if [ $? -ne 0 ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 爬虫执行失败，跳过上传"
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 爬虫执行完成，准备上传..."
        
        # 上传到 GitHub
        git add endclothing_70off.json data.js
        
        if ! git diff --staged --quiet; then
            git commit -m "Update product data - $(date '+%Y-%m-%d %H:%M')"
            git push origin main
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] 数据已上传，等待 GitHub Pages 自动部署..."
        else
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] 数据无变化，跳过上传"
        fi
    fi
    
    echo ""
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 下次执行时间: 1小时后"
    echo "----------------------------------------"
    
    # 等待1小时 (3600秒)
    sleep 3600
done
