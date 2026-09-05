# -*- coding: utf-8 -*-
"""Gunicorn 启动配置（生产环境用）"""
from main import app

# Gunicorn 会自动导入这个 app 对象
application = app
