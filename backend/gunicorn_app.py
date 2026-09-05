# -*- coding: utf-8 -*-
"""Gunicorn 启动配置（生产环境用）"""
import sys
import os

# 确保backend目录在Python路径中
sys.path.insert(0, os.path.dirname(__file__))

# 导入FastAPI应用
from main import app

# Gunicorn 会自动导入这个 app 对象
application = app

# 添加健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "ok"}
