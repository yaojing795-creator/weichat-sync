# -*- coding: utf-8 -*-
"""数据库模型定义"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), nullable=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # 关联账号
    accounts = relationship("WeChatAccount", back_populates="owner", cascade="all, delete-orphan")
    # 关联任务
    tasks = relationship("FollowTask", back_populates="owner", cascade="all, delete-orphan")


class WeChatAccount(Base):
    """微信账号表"""
    __tablename__ = "wechat_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    wxid = Column(String(100), unique=True, nullable=False, index=True)
    nickname = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    session_id = Column(String(200), nullable=True)
    status = Column(String(20), default="offline")
    last_online = Column(DateTime, nullable=True)
    last_offline = Column(DateTime, nullable=True)
    error_msg = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="accounts")
    tasks = relationship("FollowTask", back_populates="account", cascade="all, delete-orphan")
    forward_logs = relationship("ForwardLog", back_populates="account", cascade="all, delete-orphan")


class FollowTask(Base):
    """跟圈任务表"""
    __tablename__ = "follow_tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("wechat_accounts.id"), nullable=False)
    source_wxid = Column(String(100), nullable=False)
    source_nickname = Column(String(100), nullable=True)
    delay_seconds = Column(Integer, default=60, nullable=False)
    is_enabled = Column(Boolean, default=True)
    is_running = Column(Boolean, default=False)
    last_sync_time = Column(DateTime, nullable=True)
    total_forwarded = Column(Integer, default=0)
    total_failed = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="tasks")
    account = relationship("WeChatAccount", back_populates="tasks")
    logs = relationship("ForwardLog", back_populates="task", cascade="all, delete-orphan")


class ForwardLog(Base):
    """转发记录表"""
    __tablename__ = "forward_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("wechat_accounts.id"), nullable=True)
    task_id = Column(Integer, ForeignKey("follow_tasks.id"), nullable=True)
    source_wxid = Column(String(100), nullable=False)
    content_type = Column(String(20), nullable=False)
    content_summary = Column(Text, nullable=True)
    media_urls = Column(JSON, nullable=True)
    status = Column(String(20), default="pending")
    delay_applied = Column(Integer, nullable=True)
    error_msg = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)

    account = relationship("WeChatAccount", back_populates="forward_logs")
    task = relationship("FollowTask", back_populates="logs")


class SystemLog(Base):
    """系统日志表"""
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    level = Column(String(20), nullable=False)
    module = Column(String(50), nullable=True)
    message = Column(Text, nullable=False)
    extra_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class WeChatPost(Base):
    """朋友圈动态缓存表"""
    __tablename__ = "wechat_posts"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(String(100), unique=True, nullable=False)
    wxid = Column(String(100), nullable=False)
    content = Column(Text, nullable=True)
    media_urls = Column(JSON, nullable=True)
    media_types = Column(JSON, nullable=True)
    publish_time = Column(DateTime, nullable=True)
    receive_time = Column(DateTime, default=datetime.utcnow)
    is_forwarded = Column(Boolean, default=False)
    forward_task_id = Column(Integer, ForeignKey("follow_tasks.id"), nullable=True)
