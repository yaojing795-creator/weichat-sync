# -*- coding: utf-8 -*-
"""云端微信跟圈 SaaS 后端主入口"""
import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from datetime import datetime

from database import engine, Base
import models
from routers import auth, accounts, tasks, admin
from services.wechat_service import init_default_admin
from services.sync_service import sync_manager, start_all_running_tasks


async def _init_db():
    """初始化数据库表结构（如果不存在）"""
    # 使用checkfirst=True参数，避免重复创建表
    Base.metadata.create_all(bind=engine, checkfirst=True)
    print("[数据库] 表结构检查完成")


async def _seed_admin():
    """初始化默认管理员"""
    from database import SessionLocal
    db = SessionLocal()
    try:
        init_default_admin(db)
    finally:
        db.close()
    print("[系统] 管理员初始化完成")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 50)
    print("  云端微信跟圈 SaaS 服务启动中...")
    print("=" * 50)
    await _init_db()
    await _seed_admin()
    await start_all_running_tasks()
    # 不创建后台任务，避免阻塞启动
    print("[系统] 服务启动完成")
    yield
    print("\n[系统] 服务正在关闭...")
    await sync_manager.shutdown_all(None)
    print("[系统] 服务已关闭")


app = FastAPI(
    title="云端微信跟圈 SaaS",
    description="微信朋友圈自动同步管理系统原型",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(tasks.router)
app.include_router(admin.router)


@app.get("/api/health")
def health_check():
    """健康检查接口"""
    return {
        "status": "ok",
        "service": "weichat-sync",
        "version": "1.0.0",
        "running_tasks": sync_manager.get_running_count(),
    }


@app.get("/")
def root():
    """根路径"""
    return {"message": "云端微信跟圈 SaaS 服务运行中"}


# 前端静态文件托管
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8765"))
    print(f"🚀 启动服务: http://{host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")
