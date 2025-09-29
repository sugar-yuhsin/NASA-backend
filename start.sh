#!/bin/bash

# NASA Hackathon FastAPI 專案啟動腳本

set -e

echo "🚀 NASA Hackathon API 啟動腳本"
echo "================================"

# 檢查 Python 版本
python_version=$(python3 --version 2>&1)
echo "Python 版本: $python_version"

# 檢查虛擬環境
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ 虛擬環境已啟用: $VIRTUAL_ENV"
else
    echo "⚠️ 建議使用虛擬環境"
fi

# 安裝依賴
echo "📦 安裝依賴..."
pip install -r requirements.txt

# 檢查環境變數檔案
if [ ! -f .env ]; then
    echo "📝 複製環境變數範例檔案..."
    cp .env.example .env
    echo "⚠️ 請編輯 .env 檔案設定你的配置"
fi

# 創建上傳目錄
mkdir -p uploads

# 啟動應用程式
echo "🚀 啟動 FastAPI 應用程式..."
echo "API 文檔: http://localhost:8000/docs"
echo "ReDoc: http://localhost:8000/redoc"
echo "健康檢查: http://localhost:8000/health"
echo ""
echo "按 Ctrl+C 停止服務"

python3 main.py 