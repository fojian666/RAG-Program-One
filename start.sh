#!/usr/bin/env bash

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
VENV_PYTHON="$PROJECT_ROOT/.venv/bin/python"

echo "🚀 Image RAG 启动脚本"
echo "======================"

# 检查虚拟环境
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ 未找到 Python 虚拟环境: $VENV_PYTHON"
    echo "请先创建虚拟环境并安装依赖"
    exit 1
fi

# 检查前端依赖
if [ ! -d "$PROJECT_ROOT/frontend/node_modules" ]; then
    echo "📦 安装前端依赖..."
    (cd "$PROJECT_ROOT/frontend" && npm install)
fi

# 启动后端（日志重定向到文件）
echo "🔧 启动后端服务 (http://localhost:8000)..."
(cd "$PROJECT_ROOT/backend" && "$VENV_PYTHON" main.py > "$PROJECT_ROOT/backend.log" 2>&1) &
BACKEND_PID=$!

# 等待后端就绪
echo "⏳ 等待后端启动..."
for i in $(seq 1 30); do
    if curl -s http://localhost:8000/api/v1/images > /dev/null 2>&1; then
        echo "✅ 后端已就绪"
        break
    fi
    sleep 1
    if [ "$i" -eq 30 ]; then
        echo "⚠️ 后端启动超时，查看 backend.log 排查问题"
        cat "$PROJECT_ROOT/backend.log" | tail -20
    fi
done

# 启动前端
echo "🎨 启动前端服务 (http://localhost:5173)..."
(cd "$PROJECT_ROOT/frontend" && npm run dev > "$PROJECT_ROOT/frontend.log" 2>&1) &
FRONTEND_PID=$!

echo ""
echo "======================"
echo "✅ 所有服务已启动"
echo "   前端: http://localhost:5173"
echo "   后端: http://localhost:8000"
echo "======================"
echo "按 Ctrl+C 停止所有服务"
echo ""

# 捕获退出信号
trap 'echo ""; echo "🛑 正在停止服务..."; kill $FRONTEND_PID $BACKEND_PID 2>/dev/null; wait; echo "👋 已退出"; exit 0' INT TERM

wait
