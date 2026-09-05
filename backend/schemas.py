# -*- coding: utf-8 -*-
"""Pydantic 数据模式定义"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# ===== 认证相关 =====
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    email: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


# ===== 用户相关 =====
class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    is_admin: bool = False


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


# ===== 微信账号相关 =====
class WeChatAccountCreate(BaseModel):
    wxid: str = Field(..., min_length=1, max_length=100)
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None


class WeChatAccountOut(BaseModel):
    id: int
    wxid: str
    nickname: Optional[str]
    avatar_url: Optional[str]
    status: str
    last_online: Optional[datetime]
    last_offline: Optional[datetime]
    error_msg: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class WeChatAccountUpdate(BaseModel):
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None


# ===== 跟圈任务相关 =====
class FollowTaskCreate(BaseModel):
    account_id: int
    source_wxid: str = Field(..., min_length=1, max_length=100)
    source_nickname: Optional[str] = None
    delay_seconds: int = Field(default=60, ge=0, le=300)


class FollowTaskOut(BaseModel):
    id: int
    account_id: int
    source_wxid: str
    source_nickname: Optional[str]
    delay_seconds: int
    is_enabled: bool
    is_running: bool
    last_sync_time: Optional[datetime]
    total_forwarded: int
    total_failed: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FollowTaskUpdate(BaseModel):
    is_enabled: Optional[bool] = None
    delay_seconds: Optional[int] = Field(None, ge=0, le=300)
    source_nickname: Optional[str] = None


# ===== 转发记录相关 =====
class ForwardLogOut(BaseModel):
    id: int
    source_wxid: str
    content_type: str
    content_summary: Optional[str]
    status: str
    delay_applied: Optional[int]
    error_msg: Optional[str]
    created_at: datetime
    finished_at: Optional[datetime]

    class Config:
        from_attributes = True


# ===== 统计相关 =====
class AccountStats(BaseModel):
    total_accounts: int
    online_accounts: int
    offline_accounts: int
    total_tasks: int
    running_tasks: int
    today_forwards: int
    today_success: int
    today_failed: int


class DashboardStats(BaseModel):
    user_stats: AccountStats
    recent_logs: List[dict]


# ===== 系统日志相关 =====
class SystemLogOut(BaseModel):
    id: int
    level: str
    module: Optional[str]
    message: str
    created_at: datetime

    class Config:
        from_attributes = True


# ===== 朋友圈动态相关 =====
class WeChatPostOut(BaseModel):
    id: int
    post_id: str
    wxid: str
    content: Optional[str]
    media_urls: Optional[list]
    media_types: Optional[list]
    publish_time: Optional[datetime]
    receive_time: datetime
    is_forwarded: bool

    class Config:
        from_attributes = True
