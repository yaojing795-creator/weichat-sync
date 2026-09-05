#!/bin/bash
# ===== 云端微信跟圈 SaaS 一键部署脚本 =====
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
PORT=${PORT:-8765}
DB_PATH=${DB_PATH:-"$PROJECT_DIR/data/weichat_sync.db"}

echo "=========================================="
echo "  云端微信跟圈 SaaS 部署脚本"
echo "=========================================="
echo ""

# 创建数据目录
mkdir -p "$PROJECT_DIR/data"
export DB_PATH

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3，请先安装 Python 3.8+"
    exit 1
fi
echo "✅ Python 版本: $(python3 --version)"

# 检查依赖
echo ""
echo "📦 检查依赖..."
MISSING=()
for pkg in fastapi uvicorn sqlalchemy aiosqlite bcrypt python-multipart; do
    if ! python3 -c "import $pkg" 2>/dev/null; then
        MISSING+=("$pkg")
    fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
    echo "⚠️  缺少依赖: ${MISSING[*]}"
    echo "   正在安装..."
    pip3 install fastapi uvicorn sqlalchemy aiosqlite bcrypt python-multipart --break-system-packages 2>/dev/null || \
    pip3 install fastapi uvicorn sqlalchemy aiosqlite bcrypt python-multipart
    echo "✅ 依赖安装完成"
fi

# 启动服务
echo ""
echo "🚀 启动服务..."
echo "   访问地址: http://localhost:$PORT"
echo "   管理员账号: admin / admin123"
echo ""

cd "$BACKEND_DIR"
exec python3 main.py
