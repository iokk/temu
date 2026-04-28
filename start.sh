#!/bin/bash
# TEMU 智能出图系统 V8.0

echo "========================================"
echo "  🍌 TEMU 智能出图系统 V8.0"
echo "  Powered by Nano Banana Pro"
echo "========================================"

if [ ! -f .env ]; then
    cp .env.example .env
    echo "❗ 请编辑 .env 设置 GEMINI_API_KEY"
    exit 1
fi

source .env
if [ -z "$GEMINI_API_KEY" ] || [ "$GEMINI_API_KEY" = "your_api_key_here" ]; then
    echo "❌ 请设置 GEMINI_API_KEY"
    exit 1
fi

mkdir -p data

echo "1) 🚀 启动  2) 🛑 停止  3) 🔄 重启  4) 📋 日志  5) 🔨 重建"
read -p "选择: " c

case $c in
    1) docker-compose up -d && echo "✅ http://localhost:${PORT:-8501}" ;;
    2) docker-compose down ;;
    3) docker-compose restart ;;
    4) docker-compose logs -f ;;
    5) docker-compose build --no-cache && docker-compose up -d ;;
esac
