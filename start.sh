#!/bin/bash
# TEMU 智能出图系统 - 快速启动脚本
# 核心作者: 企鹅

set -e

echo "========================================"
echo "  TEMU 智能出图系统 V6.5"
echo "  核心作者: 企鹅"
echo "========================================"
echo ""

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "⚠️  未找到 .env 文件"
    echo "📝 正在创建 .env 文件..."
    cp .env.example .env
    echo "✅ 已创建 .env 文件"
    echo ""
    echo "⚠️  请编辑 .env 文件，填入你的配置："
    echo "   1. GEMINI_API_KEY=your_api_key_here"
    echo "   2. 其他配置项（可选）"
    echo ""
    echo "编辑完成后，重新运行此脚本"
    exit 1
fi

# 检查 GEMINI_API_KEY
source .env
if [ -z "$GEMINI_API_KEY" ] || [ "$GEMINI_API_KEY" = "your_gemini_api_key_here" ]; then
    echo "❌ 请在 .env 文件中设置 GEMINI_API_KEY"
    echo ""
    echo "获取 API Key 的步骤："
    echo "1. 访问 https://aistudio.google.com/apikey"
    echo "2. 登录 Google 账号"
    echo "3. 创建或复制 API Key"
    echo "4. 填入 .env 文件的 GEMINI_API_KEY 字段"
    exit 1
fi

echo "✅ 配置检查通过"
echo ""

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ 未安装 Docker"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ 未安装 Docker Compose"
    echo "请先安装 Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker 环境检查通过"
echo ""

# 创建数据目录
if [ ! -d "data" ]; then
    echo "📁 创建数据目录..."
    mkdir -p data
    echo "✅ 数据目录创建完成"
    echo ""
fi

# 询问操作
echo "请选择操作："
echo "  1) 启动服务"
echo "  2) 停止服务"
echo "  3) 重启服务"
echo "  4) 查看日志"
echo "  5) 查看状态"
echo "  6) 清理数据"
echo ""
read -p "请输入选项 (1-6): " choice

case $choice in
    1)
        echo ""
        echo "🚀 正在启动服务..."
        docker-compose up -d
        echo ""
        echo "✅ 服务已启动！"
        echo ""
        echo "📍 访问地址: http://localhost:8501"
        echo "🔐 默认密码: ${ACCESS_PASSWORD:-temu2024}"
        echo "👨‍💼 管理员密码: ${ADMIN_PASSWORD:-admin888}"
        echo ""
        echo "查看日志: docker-compose logs -f"
        ;;
    2)
        echo ""
        echo "🛑 正在停止服务..."
        docker-compose down
        echo "✅ 服务已停止"
        ;;
    3)
        echo ""
        echo "🔄 正在重启服务..."
        docker-compose restart
        echo "✅ 服务已重启"
        ;;
    4)
        echo ""
        echo "📋 查看日志（Ctrl+C 退出）..."
        docker-compose logs -f
        ;;
    5)
        echo ""
        echo "📊 服务状态："
        docker-compose ps
        ;;
    6)
        echo ""
        read -p "⚠️  确定要清理所有数据吗？(y/N): " confirm
        if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
            echo "🗑️  正在清理数据..."
            rm -rf data/*
            echo "✅ 数据已清理"
        else
            echo "❌ 取消清理"
        fi
        ;;
    *)
        echo "❌ 无效的选项"
        exit 1
        ;;
esac

echo ""
echo "========================================"
echo "  完成！"
echo "========================================"
